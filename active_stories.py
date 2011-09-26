#!/usr/bin/env python

"""
Copyright (c) 2011 Socialize, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions: 

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.  

"""

import urllib2          
import sys

from pprint import pprint
from git.repo.base import Repo

from xml.dom.minidom import parse, parseString

def load_config():

    git_config = Repo().config_reader()
    pivotal_items = git_config.items('pivotal')

    token = None
    filter = None
    project_id = None

    for item_name, item_value in pivotal_items:
        if item_name == 'token':
            token = item_value

        if item_name == 'filter':
            filter = item_value

        if item_name == 'projectid':
            project_id = item_value

    return token, filter, project_id


def load_document(token, filter, project_id):
    req = urllib2.Request(
            'http://www.pivotaltracker.com/services/v3/projects/%s/stories/?filter=%s' % (
                project_id, urllib2.quote(filter)))
    req.add_header("X-TrackerToken", token) 
    result = urllib2.urlopen(req)

    return result

if __name__ == '__main__':

    files = sys.argv[0]
    msg_file = sys.argv[1]

    token, filter, project_id = load_config()
    pivotal_document = parse(load_document(token, filter, project_id))

    stories = pivotal_document.getElementsByTagName('story')


    stories_to_add = []
    potential_stories_to_add = []
    if stories:
        i=1
        print "Available Stories"
        for story in stories:
            id = story.getElementsByTagName('id')[0].firstChild.wholeText
            name = story.getElementsByTagName('name')[0].firstChild.wholeText

            print "%s: %s -- %s" % (i, id, name)
            potential_stories_to_add.append((id,name))

            i += 1
    else:
        print "Error: No started stories found!"
        sys.exit(1)


    # Git does not support interactive shells in hooks so I have to just assume the commit is for all of them
    # If this changes you can remove the following line and uncomment the rest:
    stories_to_add = potential_stories_to_add

    #if len(stories) > 1:
        #items_to_include = raw_input(
            #"Please Choose which stories you would like to include (comma separated list):"
            #).split(',')
        #items_to_include = [i.strip() for i in items_to_include if i]

        #for i in items_to_include:
            #stories_to_add.append(potential_stories_to_add[int(i)-1])
    #else:
        #stories_to_add.append(potential_stories_to_add[0])

    

    stringified_stories = ['#%s' % story[0] for story in stories_to_add]

    msg = open(msg_file, 'r').read()
    msg = '[%s] %s' % (' '.join(stringified_stories), msg)
    open(msg_file, 'w').write(msg)




        





