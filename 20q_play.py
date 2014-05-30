#!/usr/bin/python

import sys
import os 
import re
import random	#only if you want to guess randomly when out of questions

import urllib
import cgi 
import cgitb; cgitb.enable()

import mod20q as tq
import htmlgen as html
#global tq

from mod20q import newline
from mod20q import DB_FIELD_SEP

# variables

###############
# CGI HTML output functions
def output_head() :
	doctitle = 'I Know You'
	print "Content-Type: text/html"
	print                               # blank line, end of headers
	print "<TITLE>" + doctitle + "</TITLE>"
        print '''
	<head>
        '''
        print html.make_open_tag('link', {'rel':'icon', 'type':'image/png', 'href':'../images/riktov-icon.png' })
        print html.make_open_tag('link', {'rel':'stylesheet', 'type':'text/css', 'href':tq.config['css'] })
        print html.make_open_tag('link', {'rel':'stylesheet', 'type':'text/css', 'href':'css/effects.css' })
        
        print "<script src=\"js/jquery-1.3.1.js\"></script>"

        print "<script src=\"js/fadeout.js\"></script>"

        print '''
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	</head>
	<a href="../">Home</a> |
        '''
        print "<a href=\"%s\">Play</a> |" % cgi_url
        print '<a href="20q_edit.py">Editor</a>'
	print newline
	print "<hr>" + newline
	print "<h1>" + doctitle + "</h1>"

###############

def start_form(method, hidden_fields, clear_url_args=True) :
        action_attr = ''
        if clear_url_args:
                action_attr = ' action=' + cgi_url
	print "<form method=%s%s>" % (method, action_attr)

	for name, val in hidden_fields.iteritems() :
		print "<input type=hidden name='%s' value='%s'>"  % (name, val) 

def end_form() :
        print "</form>" ;

def form_submit_inputs(values, name) :
	for val in values:
		print "\t<input type=submit name='%s' value='%s'>"  % (name, val)
		

#############################
# input processing functions
# each invocation dispatches to one of the following functions based on query type. These function process 
# input and then display a new query page. Responding to the query page launches another invocation.

def process_eliminate(trail):
	#use the trail to restore state.
	things    = tq.db_load_things()

        #for visualization, save the state before the last question so we can fade out eliminated and switched things
        #remove the last response on the trail
        trail_tuples = tq.trail_to_tuple_list(trail)
        last_response_id, last_response_val = trail_tuples[-1]

        responses_except_last = tq.trail_to_responses(trail)
        responses_except_last.pop(last_response_id)

        things_before_last_resp = eliminate_things_against_responses(things, responses_except_last)

        eliminated_thing_names = [ tq.thing_name(th) for th in things_before_last_resp if conflicting_response(th, last_response_id, last_response_val) 
]
        #tq.dbgpr('<br>'.join(sorted(eliminated_thing_names)))
        #elimination_class_args = [ for th in things_before_last_resp ]

        #things    = eliminate_things_on_trail(things, trail)
        things = eliminate_things_against_responses(things_before_last_resp, { last_response_id:last_response_val })

	dbg_evenness = 0

	#decide what to keep asking or make a guess
	if len(things) == 1 :
		prompt_confirm_guess(things.pop(), filter_skipped_questions(trail), True) 
        else:
                questions = tq.db_load_questions()

                #separate out the identity questions, as they should be asked only after exhausting regular questions
                regular_questions  = [ q for q in questions if not (is_identity_question(q)) ]
                identity_questions = [ q for q in questions if (is_identity_question(q)) ]

                regular_questions = eliminate_questions_on_trail(regular_questions, things, trail)
                regular_questions = sorted(regular_questions, key = lambda x : evenness(tq.question_id(x), things), reverse=True)

                questions = regular_questions + identity_questions

                #questions with evenness of 0 cannot reveal any information, so remove them
                questions = [ q for q in questions if evenness(tq.question_id(q), things) != 0.00 ]

                #tq.dbgpr('<br>'.join(questions))

                #get the next legitimate question if available
                if questions:
                        next_q = questions.pop(0)
                else:
                        next_q = None

                if len(things) > 1 :	#can't make a guess yet
                        if next_q :	#keep asking
                                dbg_evenness = evenness(tq.question_id(next_q), things)
                                # ====> next state
                                prompt_next_answer(next_q, trail) 

                                #debug 
                                tq.dbgpr("%d Questions" % len(questions))
                                tq.dbgpr("%d Things" % len(things))
                                tq.dbgpr("Responses %d <span class=\"Yes\">%d</span> <span class=\"No\">%d</span>" % 
                                         tq.response_counts(tq.question_id(next_q), things))
                                tq.dbgpr("Evenness: %f" % dbg_evenness)
                                tq.dbgpr("Trail:%s" % trail)
                                
                                tq.print_debug_console()


                                print '<div class="ThingsBlockContainer">'
                                print_things_list(sorted(things_before_last_resp), tq.question_id(next_q), eliminated_thing_names)
                                print '<br style="clear:both" />'
                                print '</div>'

                                #debug_dump(things, questions, trail, next_q, dbg_evenness)

                        else :	#ran out of questions, but still more than one possibility

                                # Pick thing with longest trail, as others with shorter trails are likely to have
                                # responses that would have eliminated them had the question been asked.
                                sorted_things = sorted(things, key = lambda x : len(tq.thing_responses(x)))
                                pick = sorted_things.pop()
                                #pick = random.choice(things)

                                # ====> next state
                                prompt_confirm_guess(pick, filter_skipped_questions(trail))
	
                else :	#all possible things eliminated
                        #		if len(questions) > 0 :
                        if next_q :
                                print "<p>I still have questions to ask, but I've eliminated everyone I know!"
                        else :
                                print "<p>Hello, world! You are the first person to play this game."
                                form_prompt_get_identity('', trail, cgi_url)

def process_confirm_guess(trail, guess_name, is_it_you):
	if is_it_you == 'y' :
		print "I knew it! Thanks for playing, %s! " % guess_name

		if trail : #None if the first guess is correct
                        identity_responses = tq.thing_responses(tq.db_get_thing_by_name(guess_name))
                        your_responses = tq.trail_to_responses(trail)

                        merged_responses = dict(identity_responses.items() + your_responses.items())

                        updated_identity = (guess_name, merged_responses)
#			new_trail = tq.merge_trails(trail, tq.thing_trail(you_thing))
			tq.db_update_thing(updated_identity) 
                        
                        print_game_over(guess_name)
	else :
		form_prompt_get_identity(guess, trail, cgi_url)
		
def process_get_identity(trail, identity, guess):
	canonical_identity = get_canonical_name(identity)
	
	prompt_confirm_identity(canonical_identity, guess, trail)
			
def process_confirm_identity(trail, is_this_you, identity_name, guess_name):
	if is_this_you == 'y' :
                you_thing = tq.make_thing(identity_name, trail) 
		if guess_name == '' or guess_name == 'None' :	#"hello world" or, ran out of questions
			db_add_thing(you_thing) ;

			#Game over
			print "Thanks for playing, %s! " % identity
		else :
                        guess_thing = tq.db_get_thing_by_name(guess_name)
                        #update the database now.
                        tq.db_update_thing(you_thing) 

			questions = get_distinguishing_questions(you_thing, guess_thing)
			questions = [ q for q in questions if not tq.is_identity_question(q) ]

			prompt_get_question(trail, identity, guess, questions)
	else :	#loop
		form_prompt_get_identity(guess, trail, cgi_url)

def process_identity_question(trail, your_name, guess_name):
	"create a new identity question from your name"
        q_text = "{s!%s}" % your_name
        q_id = new_q_id(tq.db_load_questions())
        db_add_question(q_id + tq.DB_FIELD_SEP + q_text)
        
        db_update_distinguishing_question(your_name, guess_name, q_id, 'y')
        print_game_over(your_name)

def process_get_question(your_name, guess_name, selected_q, q_text, resp, q_filter=None):
        if selected_q:
                q_id = tq.question_id(selected_q)
        else :
                q_id = new_q_id(tq.db_load_questions())
                db_add_question(q_id + DB_FIELD_SEP + q_text)

        db_update_distinguishing_question(your_name, guess_name, q_id, resp)
        print_game_over(your_name)

################################
# 	
def db_update_distinguishing_question(your_name, other_name, q_id, your_resp):
        you_thing      = tq.db_get_thing_by_name(your_name)
        your_responses = tq.thing_responses(you_thing)
        your_responses[q_id] = your_resp
        tq.db_update_thing(you_thing) 
	
        other_thing     = tq.db_get_thing_by_name(other_name)
        other_responses = tq.thing_responses(other_thing)
        other_responses[q_id] = your_resp
        toggle_response(other_responses, q_id)
        tq.db_update_thing(other_thing)

#################################
# prompt functions. These are called after the input args are processed in the "process_" functions

def print_game_over(your_name):
        print "Thank you for playing, %s!" % your_name

def prompt_next_answer(question, trail) :
	if is_identity_question(question):
		q_text = 'Are you ' + identity_name(question) + '? (Not my final guess yes!)'
	else:
		q_text = tq.question_text(question)
        
        num_questions = len(tq.trail_to_responses(trail))
        print "<h3>%s [%s]: %s</h3>" % (num_questions, tq.question_id(question), q_text)

        params = {'prompt_type':'elimination' }

        old_trail = trail ;
        q_id = tq.question_id(question)

        for resp in ('Yes', 'No', 'Skip'):
                params['trail'] = old_trail + '-' + q_id + resp[0:1].lower()
                print "<a href=\"?%s\">%s</a>" % (urllib.urlencode(params), resp)

        #response is processed by process_eliminate

def prompt_confirm_guess(guess, trail, is_sure=False) :
        guess_name = tq.thing_name(guess)
        if is_sure:
                print "<p>I got it in %s questions! " % trail.count('-')
        else:
                print "<p>Still not certain, but I have no more questions to ask!"

	print "<p>I think you are %s. Am I right?" % wikiwrap(guess_name)
	print '<p>'

        params = {'prompt_type':'confirm_guess', 'guess':guess_name, 'trail':trail }
        
        for resp in ('Yes', 'No'):
                params['response'] = resp
                print "<a href=\"?%s\">%s</a>" % (urllib.urlencode(params), resp)

        #response is processed by confirm_guess

def prompt_confirm_identity(identity, guess, trail) :
	print "<p>Do you mean %s?" % wikiwrap(identity)

        params = {'prompt_type':'confirm_identity', 'identity':identity, 'guess':guess, 'trail':trail }

        for resp in ('Yes', 'No', 'Skip'):
                params['response'] = resp
                print "<a href=\"?%s\">%s</a>" % (urllib.urlencode(params), resp)

def form_prompt_get_identity(guess, trail, bail_url) :
	print "<p>Please tell me who you are."

        params = {'prompt_type':'get_identity', 'trail':trail, 'guess':guess }

        #we need to strip the args from the url since we were GETTING until now
	start_form('POST', params, True)
	print '<input type=text name="identity">' 
	end_form()

	print "<a href=%s>Forget it. I'm not telling.</a>" % bail_url

def prompt_get_question_select(questions, trail, identity, guess):
	print "Here are some possibilities that are already in the database: "
	
        params = {'prompt_type':'get_question', 'identity':identity, 'trail':trail, 'guess':guess }
	start_form('POST', params, True)
	
	print '<select name="existing_question" size=1>'

        responses = tq.trail_to_responses(trail)

	for q in questions :
		q_id = tq.question_id(q)

		css_class = ''	

		if q_id in responses :
			resp = responses[q_id]
			if resp == 'y':
				css_class = 'Yes'
			elif resp == 'n':
				css_class = 'No'
			else :
				css_class = ''	

		print "<option value=%s class=\"%s\"> %s" % (q_id, css_class, q)

	print '</select>'

	print '<input type="radio" name="answer" value="y" checked>Yes'
	print '<input type="radio" name="answer" value="n">No'

	print '<input type=submit value="Submit this question" name="response">'
        end_form()					
	
def prompt_get_question_new(questions, trail, identity, guess):
        params = {'prompt_type':'get_question', 'identity':identity, 'trail':trail, 'guess':guess }
        start_form('POST', params)
        
        print '''
	Write your own question :
	<p><input type=text size=75 name='new_question'>

	<p>And your answer to this question:

	<input type=radio name='answer' value='y' checked>Yes
	<input type=radio name='answer' value='n'>No
	
	<p><input type=submit value='Submit this question' name='response'>
        ''' 
        end_form()					

def prompt_make_identity_question(identity, guess):
        params = {'prompt_type':'identity_question', 'guess':guess, 'identity':identity}
        print "<p>Or, if you can\'t think of anything at all"
        print "that would distinguish you from %s, <a href=?%s>click here</a>." % (guess, urllib.urlencode(params))

def prompt_get_question(trail, identity, guess_name, questions) :
	print "<p>OK, %s, I've learned who you are. <br>\n" % wikiwrap(identity)
	print "Now please help me out by answering a question that will distinguish you "
        print "from my guess, %s.<br>" % guess_name

        print '<div class="QuestionSubmissions">'

        print '<div>'
        prompt_get_question_select(questions, trail, identity, guess)
	print '</div>'

	print '<div>'
        prompt_get_question_new(questions, trail, identity, guess)
        print '</div>'

	print '<div>'
        prompt_make_identity_question(identity, guess)
	print '</div>'

        print '</div>' #end QuestionSubmissions


#####################################
# some utility functions

def new_q_id(questions) :
	if questions == None :
		return 1
	return str(len(questions) + 1)
#	return str(lowest_missing([int(tq.split('DB_FIELD_SEPARATOR')[0]) for q in questions], 1))
	
def get_canonical_name(name) :
	#dummy return
	return name
#	return "Foobar X-45 " + name

def wikiwrap(s) :
	return s
#	return "<a href=\"http://en.wikipedia.org/wiki/%s\">%s</a>" % (s, s)

###################
# elimination algorithm
#

def conflicting_response(thing, q_id, resp):
        return not same_response_or_skipped(tq.thing_responses(thing), q_id, resp)

def same_response_or_skipped(responses, q_id, resp):
        """Assuming only binary responses, no skip"""
        if resp == 's' or not q_id in responses:
                return True
        return responses[q_id] == resp

def eliminate(things, q_id, q_r) :
        """Remove all things for which the response to resp is opposite"""
	if things :
		return [ th for th in things if same_response_or_skipped(tq.thing_responses(th), q_id, q_r) ]
#		return filter (lambda th: (th.find(step) < 0), things)
	return []

def eliminate_things_on_trail(things, trail) :	
	for q_id, q_r in tq.trail_to_tuple_list(trail) :
		things = eliminate(things, q_id, q_r)
	return things

def eliminate_things_against_responses(things, trail_responses):
        for q_id, q_r in trail_responses.items():
                things = eliminate(things, q_id, q_r)
        return things

def eliminate_questions_on_trail(questions, things, trail) :	
	"""



        """

        responses = tq.trail_to_responses(trail)
        question_dict = {}
        for q in questions:
                (q_id, q_text) = q.split(DB_FIELD_SEP)
                question_dict[q_id] = q_text

	for q_id in get_qids(responses) :
                # Filter out anything that's been asked, including skips
                if q_id in responses:
                        question_dict.pop(q_id, None)

                # Filter out any unrevealing questions. The set of things will never increase,
                # so once a question is determined to be unrevealing, it can be permanently removed.
                if is_unrevealing(q_id, things):
                        question_dict.pop(q_id, None)

                # If the question is an identity question, remove it if the identity thing's is not in the things
                


#		questions = filter(lambda ques: tq.question_id(ques) != q_id, questions)

#		questions = filter(lambda ques: not is_unrevealing(ques, things), questions)

		#questions = [q for q in questions if question_id(q) != q_id]
		#questions = [q for q in questions if False == is_unrevealing(question_id(q), things)]	

        questions = []
        for q_id in question_dict.keys():
                questions.append(q_id + DB_FIELD_SEP + question_dict[q_id])

	return questions

def filter_skipped_questions(trail) :
	return re.sub('\-\d+s', '', trail)
	
def inverse_step(step) :
	num  = step[:-1]#up to char
	resp = step[-1:]#last char
	if resp == 'y' :
		return num + 'n'
	elif resp == 'n' :
		return num + 'y'
	return step

def toggle_response(responses, q_id):
        if responses[q_id] == 'y':
                responses[q_id] = 'n'
        elif responses[q_id] == 'n':
                responses[q_id] = 'y'

# unrevealing questions have an evenness of 0 and will already sink
def is_unrevealing(q_id, things) :
	"""Return True if all of the things have the same response to the question"""
        #q_id = tq.question_id(q)
	rc = tq.response_counts(q_id, things)

	return (rc[0] * rc[1] * rc[2] == 0)


def identity_name(question) :
	found = re.match('\{s!(.+)\}', tq.question_text(question))
	if found:
		return found.group(1)
	else:
		return None
	
def is_identity_question(question):
	return identity_name(question) != None

###################
# extracting fields from records

def get_qids(responses):
        return responses.keys()
        #return [step[:-1] for step in responses]
	

########################
# operations on trails
#def merge_trails(tr1, tr2) :	#moved to module
	
#def sort_trail(trail) :	#moved to module

####################################
# extracting information from questions or things

def get_distinguishing_questions(thing1, thing2) :
	"""Questions that distinguish between thing1 and thing2: those that are in one but not the other
	plus those that are in neither. Or questions that do not conflict or match"""

	questions = tq.db_load_questions()

	q1 = set(get_qids(tq.thing_responses(thing1))) 
	q2 = set(get_qids(tq.thing_responses(thing2)))
	q_all = set([tq.question_id(ques) for ques in questions])
	
        #from the set of all questions, remove any question that both have answered
	selection = q_all - (q1 & q2)	#syntax for "set" data type, See tutorial 5.4
	
	select_trail = '-' + '-'.join(selection) + '-'

	return filter(lambda q: select_trail.find('-' + tq.question_id(q) + '-') > -1, questions)
	
#	return [q for q in questions if select_trail.find('-' + question_id(q) + '-') > -1]
	#return dummy_questions

#def get_questions(questions, ids) :
	
	
def evenness(q_id, things) :
	total, yesses, nos = tq.response_counts(q_id, things)
	if total == 0 :	#lazy hack
		return 0
	
	if yesses < nos:
		e = 1.0 * yesses / nos
	else:
		e = 1.0 * nos / yesses
	
	return e
#	return yesses 
#	yesses = int(yesses)
#	total = 1.0 * int(total)	#convert to fp
#	return abs(0.5 - (yesses / total))


#	print "DUMMY [add_thing(%s, %s)]" % (identity, trail)


#######################
# database file
# : most stuff is in module

def db_add_thing(thing) :
	tq.append_line(config.things_db_path, thing)

def db_add_question(question) :
	tq.append_line(tq.config['questionsdb'], question)


#####################################
#  HTML highlighting for debugging
#
def response_class(resp):
        if resp == 'y':
                name = 'Yes'
        elif resp == 'n':
                name = 'No'
        else:
                return {}

        return { 'class':name }

#def html_make_tag(contents, tag_name, args_dict=None):
#        open_tag = html_make_open_tag(tag_name, args_dict)
#        #open_tag[-1:3] = '>'
#        return open_tag + contents + "</%s>" % tag_name

#def html_make_open_tag(tag_name, args_dict=None):
#        param_str = ''
#        if args_dict:
#                param_tuples_list = args_dict.items()
#                param_str_list = [ "%s=%s" % (t[0], t[1]) for t in param_tuples_list ]
#                param_str = ' '.join(param_str_list)
#        return "<%s %s>" % (tag_name, param_str)

def tag_classes(thing, q_id, eliminated_things):
        class_list = []
        resp = tq.thing_response_to_q(thing, q_id)
        if resp == 'y':
                class_list.append('Yes')
        elif resp == 'n':
                class_list.append('No')

        if tq.thing_name(thing) in eliminated_things:
                class_list.append('Eliminated')

        if class_list:
                return { 'class':' '.join(class_list) }
        return None

def print_things_list(things, selected_q_id, eliminated_things):
        names = [ tq.thing_name(th) for th in things ]

        response_list = [ response_class(tq.thing_response_to_q(thing, selected_q_id)) for thing in things ]
        
        #lis  = [ html_make_tag(first_name(name), 'li', class_args) for (name, class_args) in zip(names, response_list) ]        
#        lis  = [ html.make_tag(first_name(tq.thing_name(th)), 'li', tag_classes(th, selected_q_id, eliminated_things)) for th in things ]
        lis  = [ html.make_tag('', 'li', tag_classes(th, selected_q_id, eliminated_things)) for th in things ]

        lis.append('<br style="clear:both" />')

        print '<ul class="Things">' + '\n'.join(lis) + '</ul>'

def first_name(name_str) :
	return re.sub(' .+', '', name_str)
	
def html_highlight(thing, q_id) :
	if 'display_name' in tq.config and tq.config['display_name'] == 'hidden':
		first_name = '+'
	else:
		first_name = re.sub(' .+', '', tq.thing_name(thing))
	
        resps = tq.thing_responses(thing)

	if q_id in resps and resps[q_id] == 'y' :
		return "<div class=\"Yes\">%s</div>" % first_name

	if q_id in resps and resps[q_id] == 'n' :
		return "<div class=\"No\">%s</div>" % first_name
	else :
		return "<div class=\"Unknown\">%s</div>" % first_name
#		return thing_name(thing)

def html_highlight_thinglist(things, q_id) :
	return [html_highlight(th, q_id) for th in things]

###################
# utility functions
#def splitkeep(s, delim) :

#look at zip, in Tutorial Sect 5
# use set differences ^ operator
def lowest_missing(numseq, base=0) :
	"""the smallest integer >= base in a sequence of integers"""
	s = sorted(numseq)
	
	#assume from 1
	for idx in range(0, len(numseq)) :
		if s[idx] > idx + base :
			return idx
	return len(numseq)
####os.path.basename(sys.argv[0])


def test() :
	contents = load_textfile(things_db_path)
	print contents 

#def adjoin(seq1, seq2, key=None, test=None)
	
def debug_dump(things, questions, trail, next_q, dbg_evenness) :
	questions.reverse()
	print '<div class="Debug">'
	print '<div class=\"Things">'
	print join(html_highlight_thinglist(things, tq.question_id(next_q)))
	print "</div>"
	print "<br>"
	print '<div class="Questions">'	
	print '<ul>'
	print "\t<li>" + "\n\t<li>".join(questions)
	print '</ul>'
	print '</div>'
	print '</div>'

	 
######################################################
## main

cgi_url = os.path.basename(sys.argv[0])

rcfilename = '.' + re.sub('_.+py', 'rc', cgi_url)
tq.configure(rcfilename)

#dummy values
dummy_guess = 'P-51 Mustang' 
#canonical_identity = 'P-51 Mustang'
dummy_questions = [
	'1. Do you have five engines?', 
	'2. Are you a bomber?', 
	'3. Are you Pakistani?',
	'4. Did you serve in Antarctica?'
	]

#based on what type of query we are responding to, send a new form
# This is essentially a state machine. Each block should end with another 
# form_prompt_* call to push it along to a new state


output_head()
#tq.dbgpr('Query type: ' + qtype)

form = cgi.FieldStorage()

prompt_type = form.getvalue('prompt_type') or 'elimination'
trail = form.getvalue('trail') or ''

if prompt_type == 'elimination' :
        process_eliminate(trail)

elif prompt_type == 'confirm_guess' :
	guess = form.getvalue('guess') 
	resp  = form.getvalue('response')[0:1].lower()
	
        process_confirm_guess(trail, guess, resp)
		
elif prompt_type == 'get_identity' :
	identity = form.getvalue('identity') or ''
	guess = form.getvalue('guess') 

        process_get_identity(trail, identity, guess)
		
elif prompt_type == 'confirm_identity' :
	resp  = form.getvalue('response')[0:1].lower()
	identity = form.getvalue('identity')
	guess = form.getvalue('guess') 
        
        process_confirm_identity(trail, resp, identity, guess)

elif prompt_type == 'get_question' :
	identity = form.getvalue('identity')
	guess    = form.getvalue('guess') 
        selected_question = form.getvalue('existing_question')
        new_question_text = form.getvalue('new_question')
	q_response   = form.getvalue('answer')

        process_get_question(identity, guess, selected_question, new_question_text, q_response)

elif prompt_type == 'identity_question' :
	trail    = form.getvalue('trail') or ''
	identity = form.getvalue('identity')
	guess    = form.getvalue('guess')

        process_identity_question(trail, identity, guess)
        
else :
	print "Unknown prompt type: %s" % prompt_type 
	

#######################
# end HTML output
tq.print_debug_console()
print '</body>\n</html>'
