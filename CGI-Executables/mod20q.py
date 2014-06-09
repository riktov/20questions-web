#shared module for 20q
import re
import os

#globals
DB_FIELD_SEP = ':'
newline = "\n"
tab = "\t"

debug_console_contents = ''

config = {}

#things_db_path = ''
#questions_db_path = ''

#function definitions

#classes
class Thing:
        def __init__(self, name, trail=''):
                self.name = name
                self.responses = trail_to_responses(trail)
                self.first_name = re.sub(' .+', '', self.name) 

        def __repr__(self):
                return "<%s : %s>" % (self.name, self.responses)

        def response(self, q_id):
                if q_id in self.responses:
                        return self.responses[q_id]
                else:
                        return None

        def remove_response(self, q_id):
                self.responses.pop(q_id, None)

        pass


#############b################
# configure the rc and data files
def configure(rcfilename):
        global config
        if os.path.isfile(rcfilename) :	
                config = load_rc(rcfilename)
        else:
                dbgpr("No rcfile found, using defaults")


######################################
# manipulating response sets and trails

def as_list(trail) :
	return trail.lstrip('-').split('-')

def crack_step(step):
        """return a tuple consisting of the question id and answer"""
        return ( step[:-1], step[-1:])

def trail_to_tuple_list(trail) :
        return map(crack_step, as_list(trail))

def trail_to_responses(trail):
        responses = {}
        tuple_list = trail_to_tuple_list(trail)
        for step in tuple_list:
                responses[step[0]] = step[1]
        return responses

def responses_to_trail(responses):
        tr = ''
        for key in sorted(responses.keys(), key=int):
                tr += '-' + key + responses[key] 
        return tr

#def merge_trails(tr1, tr2) :
#	"""adjoin (keyed on dash-number) every element of tr1 to tr2"""
#	for step in splitkeep(tr1, '-') :
#		regexp = step[:-1] + '[yns]'
#		found = re.search(regexp, tr2)
#		if found == None :
#			tr2 += step
#	return sort_trail(tr2)

def sort_trail(trail) :
	if trail == '' : return ''
	steps = as_list(trail)
	ssteps = sorted(steps, key=lambda s : int(s[:-1]))
	return '-' + '-'.join(ssteps)


###############
# rcfile
def is_comment(str):
	found = (re.search('^\s*#', str) or re.search('^\s*$', str))
	return found
	
def cleanup(line):
	return line.strip(" \n\'")

#rcfile format: URL, regexp, url_prefix, download_dir
def load_rc(rcfile):
	rcval={}
	f = open(rcfile)
	for line in f:
		if (not (is_comment(line))):
			(key, val) = line.rstrip('\n').split('=')
			rcval[key] = val
	f.close()

        #import pdb; pdb.set_trace()
	return rcval


###################
# generic file access functions
def load_textfile(path, until=None) :
	"""Load a textfile into a list, with newlines trimmed. 
	Optional param string to terminate at"""
	#try :
	f = open(path, 'r')
	#except IOError :
	#	return [] 
	
	linelist = []
	
	if until :
		cre = re.compile(until)

	for line in f.readlines() :
		if until :
			found = cre.search(line)
			if found :
				linelist.append(line.rstrip('\n'))
				break
		linelist.append(line.rstrip('\n'))
	
	f.close() 
	
	return linelist

def update_record(path, record, fieldidx) :
	"""Replace all lines in a text file with specified record at fieldidx"""
	try :
		fin = open(path, 'r')
	except IOError :
		f = open(path, 'a')
		f.write(record)
		f.close()
		return
	
	tmpoutpath = path + '_tmp' + str(os.getpid())
	fout = open(tmpoutpath, 'w')
	
	replaced = 0
	new_fields = record.split(DB_FIELD_SEP)
	
	for line in fin :
		fin_fields = line.split(DB_FIELD_SEP)
		if fin_fields[fieldidx] == new_fields[fieldidx] :
			replaced += 1
			line = record + '\n'
		fout.write(line)
	
	if replaced == 0 :	#if no existing record match, append
		fout.write(record + '\n')

	fin.close()
	fout.close()
	
	#dbgpr ("update_record: %s, %s" % (tmpoutpath, path))
	os.rename(tmpoutpath, path)
        os.chmod(path, 0664)#so file can be manually edited by user in the apache group
	
def delete_record(path, target_field, fieldidx) :
	"""Delete all lines in a text file with specified record at fieldidx"""
	tmpoutpath = path + '_tmp' + str(os.getpid())
	
        #if the file doesn't exist, no need to delete
	try :
		fin = open(path, 'r')
	except IOError :
		return
	
	fout = open(tmpoutpath, 'w')
	
	for line in fin :
		fin_fields = line.split(DB_FIELD_SEP)
		if fin_fields[fieldidx] != target_field :
                        fout.write(line)
                
	fin.close()
	fout.close()
	
	#dbgpr ("update_record: %s, %s" % (tmpoutpath, path))
	os.rename(tmpoutpath, path)
        os.chmod(path, 0664)#so file can be manually edited by user in the apache group

def append_line(path, line) :
	f = open(path, 'a')
	f.write(line + '\n')
	f.close()

###################
# database file
def db_load_things() :
        global config
	return [ make_thing_from_line(line) for line in load_textfile(config['thingsdb']) if line]

def db_load_questions():
        global config
	return [ line for line in load_textfile(config['questionsdb']) if line ]

def db_update_thing(thing) :
#	raise MyError 
        th_name = thing.name
        th_trail = responses_to_trail(thing.responses) 
	update_record(config['thingsdb'], th_name + DB_FIELD_SEP + th_trail, 0)

def db_replace_question_text(q_id, text):
        update_record(config['questionsdb'], q_id + DB_FIELD_SEP + text, 0)

def db_get_thing_by_name(thing_name) :
        """A more efficient alternate to loading all things and getting, this stops loading after thing_name"""
	things = load_textfile(config['thingsdb'], thing_name)
	return make_thing_from_line(things.pop())

def db_delete_question(q_id):
        delete_record(config['questionsdb'], q_id, 0)
        
####################################
# creating things and accessing information from them
# a "thing" has a name and a set of responses to questions
# a reponse is a question ID with a corresponding answer
#def make_thing(name, trail):
        #return (name, trail_to_responses(trail))
#        return Thing(name, trail)

def make_thing_from_line(thing_line) :
        """Things are stored in the text database as thing lines"""
        fields = thing_line.split(DB_FIELD_SEP)
        return Thing(fields[0], fields[1])

#def thing_name(thing) :
#        return thing[0]

#def thing_responses(thing):
#        return thing[1]

#def thing_response_to_q(thing, q_id):
#        responses = thing_responses(thing)
#        if q_id in responses:
#                return responses[q_id]
#        else:
#                return None


#def thing_trail(thing) :
#	fields = thing.split(DB_FIELD_SEP)
#	return fields[1]

####################################
# creating questions and accessing information from them

def make_question(q_id, q_text):
        return q_id + DB_FIELD_SEP + q_text

def find_question(q_id, questions) :
        matches = filter(lambda q:question_id(q) == q_id, questions)
        return matches[0]

def find_question_by_text(text, questions):
        return [ q for q in questions if question_text(q) == text ]

def question_id(question) :
	#seems that the forms are clobbering the tab characters
	#So we'll assume that ids are the digits at the beginning
	if question == None : return None
	found = re.search('\d+', question)
	if found :
		return found.group()
#	fields = question.split(DB_FIELD_SEP)
#	return (fields[0])

def question_text(question) :
	fields = question.split(DB_FIELD_SEP)
        if fields[0] == '':
                return 'MISSING_QUESTION'
        else:
                return fields[1]

def is_identity_question(question):
        q_text = question_text(question)
        return q_text[:3] == '{s!'


#################################
# maintenance and editing

def move_question(q_id):
    if q_id == None or q_id == '':
        print "No question_id provided"
    else:
        things    = db_load_things()
        questions = db_load_questions()

        highest_id = str(max([ int(question_id(q)) for q in questions ]))

        q_text = question_text(find_question(highest_id, questions))

        print "Removing question \"%s\"" % question_text(find_question(q_id, questions)) 

        for th in things:
            responses = th.responses
            # print tr_dict
            
            #remove responses to the deleted question. I assume that any question I am deleted will have unanimous responses
            responses.pop(q_id, None)

            if highest_id in responses:
                #print tq.thing_name(th)

                responses[q_id] = responses[highest_id]
                responses.pop(highest_id, None)
            
                db_update_thing(th)
        
        db_replace_question_text(q_id, q_text)
        db_delete_question(highest_id)


###################################
# working with collections of questions, things, and responses


def get_thing_by_name(name, things) :
        found = [ th for th in things if th.name == name ]
        if found:
                return found[0]

def response_counts(q_id, things) :
	"""Return a tuple consisting of the total, y, and n responses to a question by all things"""
	tally = []

	for th in things :
		#resps = thing_responses(th)
		resps = th.responses
		if q_id in resps:
			tally += resps[q_id]	#just the [yn]
	
	return len(tally), tally.count('y'), tally.count('n')


def responders_to(q_id, things, resp=None):
        if resp:
                return [ th for th in responders_to(q_id, things) if th.response(q_id) == resp ]
        else:
                return [ th for th in things if q_id in th.responses ]
#                return filter(lambda th: q_id in thing_responses(th), things)


########################################
# analysis functions

def similarity(resps1, resps2):
        """Compare all responses of two things"""
        common_keys = set(resps1.keys()).intersection(set(resps2.keys()))
        if len(common_keys) == 0:
                return 0
        else:        
                vals1 = [ resps1[key] for key in common_keys ]
                vals2 = [ resps2[key] for key in common_keys ]
                
                matches = 0.0
                for (val1, val2) in zip(vals1, vals2):
                        if val1 == val2:
                                matches = matches + 1 
                                
                return matches / len(common_keys)
        #     return common_keys

def correlation(q_id_ind, q_id_dep, things):
       yes_1_responders = responders_to(q_id_ind, things, 'y')

       responders_both = responders_to(q_id_dep, yes_1_responders)
       
       responses_dep = [ th.response(q_id_dep) for th in responders_both ]

       #print responses_dep

       if len(responders_both) < 1:
               return 0.0

       positive_cor = (1.0 * responses_dep.count('y')) / len(responders_both)
       negative_cor = (1.0 * responses_dep.count('n')) / len(responders_both)
       
       if positive_cor == 0.0:
               return -1 * negative_cor
       else:
               return positive_cor
