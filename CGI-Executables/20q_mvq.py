#!/usr/bin/python
#20q_mvq.py
#Remove a question, and replace its slot with the highest-numbered question, updating all the answers accordingly
# replacing references to the highest-numbered questions with those to the replaced slot

import os
import sys
import re

import mod20q as tq

#########################
# main
rcfilename = '.' + re.sub('_.+py', 'rc', os.path.basename(sys.argv[0]))
tq.configure(rcfilename)

is_cgi = 'GATEWAY_INTERFACE' in os.environ
#[GATEWAY_INTERFACE]

if is_cgi:
    import cgi
    import cgitb
    cgitb.enable()

    form = cgi.FieldStorage()
    q_id = form.getvalue('q_id')

    cgi_url = os.path.basename(sys.argv[0])

    print "Content-Type: text/html"
    print
    print '<html><head></head>'
    print '<body>'

    tq.move_question(q_id)

    print "<br/><a href=\"%s\">Return</a>" % '20q_edit.py'
    print '</body>'
    print '<html>'

else:
    print "Running on command line"
    print
    q_id = sys.argv[1]

    tq.move_question(q_id)

#print "FOO"
#sys.exit()

