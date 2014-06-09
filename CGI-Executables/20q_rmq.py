#!/usr/bin/python

import os
import sys
import re

import mod20q as tq

rcfilename = '.' + re.sub('_.+py', 'rc', os.path.basename(sys.argv[0]))
tq.configure(rcfilename)

#is_cgi = (thing_name != None)

is_cgi = 'GATEWAY_INTERFACE' in os.environ

#is_cgi = True

if is_cgi:
    import cgi
    import cgitb
    cgitb.enable()

    cgi_url = os.path.basename(sys.argv[0])

    form = cgi.FieldStorage()

    q_id = form.getvalue('question')
    names_to_remove = form.getlist('name')

    print "Content-Type: text/html"
    print

else:
    cmd = sys.argv.pop(0)
    q_id = sys.argv.pop(0)
    names_to_remove = sys.argv

    print "Running on command line"
    print 

#print "q_id: %s" % q_id + '<br>'
#print "names: %s" % names_to_remove + '<br>'


things = tq.db_load_things()

#this_thing = tq.find_thing_by_name(thing_name, things)

print "Remove responses by the following people to question %s" % q_id 
print '<ul>'

for name in names_to_remove:
    print "<li>%s</li>" % name
    
    thing = tq.get_thing_by_name(name, things)
    responses = thing.responses
    responses.pop(q_id, None)
    tq.db_update_thing(thing)

print '</ul>'
    
if is_cgi:
    print "<a href=\"20q_edit.py?q_id=%s\">Return</a>" % q_id
