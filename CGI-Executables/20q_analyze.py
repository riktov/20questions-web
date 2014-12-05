
#!/usr/bin/python

import sys
import os 
import re
import urllib

import cgi 
import cgitb; cgitb.enable()

#import config
import mod20q as tq
import htmlgen as html
#global tq

# variables
def output_head(doctitle_suffix = '') :
#        doctitle = 'log(2)255 Editor' + ' - ' + doctitle_suffix
        doctitle = 'Analyzer'
        print "Content-Type: text/html"
	print                               # blank line, end of headers
        print '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
        print '<html xmlns="http://www.w3.org/1999/xhtml">'

        print '<head>'
	print "<title>" + doctitle + "</title>"
	
        print html.make_open_tag('link', { 'rel':'icon', 'type':'image/png', 'href':'../images/riktov-icon.png' })
        print html.make_open_tag('link', { 'rel':'stylesheet', 'type':'text/css', 'href':tq.config['css'] })

        print '<meta content="text/html; charset=utf-8" http-equiv="Content-Type">'
	print '</head>'

        print '<body>'

        print '<div class="TopMenu">'
#	print '<a href="../">Home</a> | '
        print '<a href="20q_play.py">Play</a> |'
	print '<a href="20q_edit.py">Editor</a> |'
	print '<a href="20q_analyze.py">Analyze</a>'
	print '<hr>'
        print '</div>'


        print '<div class="PageTitle">'
	print "<h1>%s</h1>" % doctitle
        print '</div>'


#question_id in mod
def responses(q_id, yn) :
	"""Get all the specified responses to a question"""
	resp = '-' + q_id + yn
	return filter(lambda th: re.search(resp, thing_trail(th)), things)

###########################
# screen output functions

def print_questions_list(questions, things=None, selected_q_id=None, selected_th_name=None):
        questions = [ q for q in questions if not tq.is_identity_question(q) ]

        #build some parallel lists for zipping
        q_ids = [ tq.question_id(q) for q in questions ]

        if things:
                corrs = [ tq.correlation(selected_q_id, q_id, things) for q_id in q_ids ] 

        #create a dictionary of lists of tag args, for each type of tag (identified by tag name)
        tag_args = {}
        tag_args['a']     = [ {'href':"?q_id=%s" % q_id} for q_id in q_ids ]

        #the anchors contain both href and CSS class for selected question, or response to selected thing
        anchors  = [ html.make_tag('a', q, ta) for (q, ta) in zip(questions, tag_args['a']) ]
        
        lines = anchors

        #final wrap with li, no tag args
        lines = [ html.make_tag('td', li) for li in lines ]
        
        if selected_q_id:
                lines = [ "<td>%s</td>" % str(cor)[0:4] + li for (cor, li) in zip(corrs, lines) ]
                
        lines = [ html.make_tag('tr', line) for line in lines ]

        lines = sorted(lines, reverse=True)


        print '<table class="Questions">'
        print '<tr>'
        if selected_q_id:
                print '<th>Cor</th>'
        print '<th>Question</th>'
        print '</tr>'

        print '\n'.join(lines) + '</table>'

def print_things_list(things, selected_th_name=None, selected_q_id=None):
        selected_thing = tq.get_thing_by_name(selected_th_name, things) 

        #parallel lists for zipping into tags
        names     = [ th.name for th in things ]
        href_list = [ {'href':'?' + urllib.urlencode({'name':"%s" % name})} for name in names ]

        if selected_th_name:
                sims      = [ selected_thing.similarity_to(th) for th in things ]

        lines  = [ html.make_tag('a', tq.first_name(name), ta) for (name, ta) in zip(names, href_list) ]
        lines  = [ html.make_tag('td', li) for li in lines ] 
        
        if selected_th_name:
                lines  = [ html.make_tag('td', str(sim)[0:4]) + li for (sim, li) in zip(sims, lines) ] 

        #final wrap with li, no tag args
        lines = [ html.make_tag('tr', anc) for anc in lines ]
        
        if selected_th_name:
                lines = sorted(lines, reverse=True)

        print '<table class="Things">'
        print '<tr>'
        if selected_th_name:
                print '<th>Sim</th>'
        print '<th>Name</th>'
        print '</tr>'
        print '\n'.join(lines)
        print '</table>'

###################
# utility functions

def strip_tags(html):
	return re.sub('<.+?>', '', html)

def q_checkname(question_html):
	question_text = re.sub('<.+?>', '', question_html)
	return 'q' + tq.question_id(question_text)
	
def th_checkname(thing_html):
	"""Assume thing_html is an anchor"""
	found = re.search('name=(.+)"', thing_html)
	if found :
		return 'th_' + found.group(1)
	return ''

#def adjoin(seq1, seq2, key=None, test=None)

#def missing_questions(questions):
 
def questions_num_range(questions):
        """Return a range of questions from the existing ids"""
        q_ids = [ int(tq.question_id(q)) for q in questions ]
        full_range = range(min(q_ids), max(q_ids))
        return full_range
	
def missing_questions(questions):
        q_num_range = questions_num_range(questions)
        q_nums = [ int(tq.question_id(q)) for q in questions ]
        return set(q_num_range).difference(q_nums)

def display_by_question(things, questions, q_id):
        question = tq.find_question(q_id, questions)

        #print '<h2>' + question + '</h2>'
        anchor = html.make_tag('a', question, {'href':"20q_edit.py?q_id=%s" % q_id })
        print html.make_tag('h2', anchor)
	
	print '<div id="left_column">'
        other_questions = [ q for q in questions if tq.question_id(q) != q_id ]
        print_questions_list(other_questions, things, q_id)
	print '</div>'

	print '<div id="right_column">'
        print_things_list(things)
        print '</div>'

def display_by_thing(things, questions, th_name):
	thing = tq.get_thing_by_name(th_name, things)

	print '<h2>' + thing.name + '</h2>'

	print '<div id="left_column">'
	print_questions_list(questions, things)
        print '</div>'

        print '<div id="right_column">'
        print_things_list(things, th_name)
        print '</div>'

def display_by_none(things, questions):
	print '<h2></h2>'

	print '<div id="left_column">'
	print_questions_list(questions)
        print '</div>'

        print '<div id="right_column">'
        print_things_list(things)
        print '</div>'


        

######################################################
## main

#form data should be retrieved first, because it exists even before the program runs!
form = cgi.FieldStorage()
g_q_id    = form.getvalue('q_id')
g_th_name = form.getvalue('name') 
#g_action    = form.getvalue('action')

cgi_url = os.path.basename(sys.argv[0])

head_suffix = g_th_name or g_q_id or ''

rcfilename = '.' + re.sub('_.+py', 'rc', cgi_url)
tq.configure(rcfilename)

output_head(head_suffix)

# no action, just display

if 'name' in form:
	query_by = 'thing'
elif 'q_id' in form:
	query_by = 'question'
else:
        query_by = 'none'

#load the databases
g_things    = tq.db_load_things()
g_questions = tq.db_load_questions()

g_things    = sorted(g_things, key = lambda x:x.name )
g_questions = sorted(g_questions, key = lambda x : int(tq.question_id(x)))

if query_by == 'question':
        display_by_question(g_things, g_questions, g_q_id)
elif query_by == 'thing' :	#by thing
        display_by_thing(g_things, g_questions, g_th_name)
else:
        display_by_none(g_things, g_questions)

#######################
# HTML output
#tq.print_debug_console()
print '</body></html>'
