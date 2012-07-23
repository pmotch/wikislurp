#!/usr/bin/python

# Wikislurp is a program that calls to the Mediawiki API, only grabs the recent changes from the last call, denormalizes the output, and outputs it in a log like format
# Copyright (C) 2012  Dan Cundiff (dan.cundiff@gmail.com)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib2
import json
from time import gmtime, strftime, strptime, mktime, localtime
import datetime
import sys

## Variables to set
wikiurl = "http://en.wikipedia.org/w/api.php" #set this to whatever your mediawiki API URL is
variables_filename = "variables.txt" # set this to where you want the variables.txt to be saved

## Grabs timestamp from variables.txt and adds a second to the timestamp
try:
	variables_file = open(variables_filename, "r")
	end_timestamp = variables_file.read().strip()
	variables_file.close()
	end_timestamp = strptime(end_timestamp,'%Y-%m-%dT%H:%M:%SZ')
	end_timestamp = mktime(end_timestamp)
	end_timestamp += 1
	end_timestamp = localtime(end_timestamp)
	end_timestamp = strftime('%Y-%m-%dT%H:%M:%SZ', end_timestamp)
except IOError:
	## If error reading the file, bootstrap the timestamp
	end_timestamp = strftime('%Y-%m-%dT%H:%M:%SZ', gmtime())

## Define the start timestamp
start_timestamp = strftime('%Y-%m-%dT%H:%M:%SZ', gmtime())

## Call the API (response comes back as JSON into a python dictionary)
try:
	url = wikiurl + '?action=query&format=json&rcdir=newer&rcstart=' + end_timestamp + '&rclimit=500&list=recentchanges&rcprop=user|timestamp|comment|flags|title|ids|sizes|redirect|loginfo'
	response = urllib2.urlopen(url).read()
except Exception:
	print start_timestamp + "|status=URL error"
	sys.exit(1)
json_response = json.loads(response)

## Only handle query and recentchanges from the dictionary
changes = json_response["query"]["recentchanges"]

## Print out per line (like a flat log) each recent change
for change in changes:
	if ( change.has_key("minor") ):
		minor = 'yes'
	else:
		minor = 'no'
	if ( change.has_key("redirect") ):
		redirect = 'yes'
	else:
		redirect = 'no'
	if ( change.has_key("logid") ):
		logid = str(change["logid"])
	else:
		logid = 'na'
	if ( change.has_key("logtype") ):
		logtype = change["logtype"]
	else:
		logtype = 'na'
	if ( change.has_key("logaction") ):
		logaction = change["logaction"]
	else:
		logaction = 'na'

	print change["timestamp"] + "|type=" + change["type"] + "|ns=" + str(change['ns']) + "|title=" + change["title"] + "|user=" + change["user"] + "|rcid=" + str(change["rcid"]) + "|pageid=" + str(change["pageid"]) + "|revid=" + str(change["revid"]) + "|old_revid=" + str(change["old_revid"]) + "|oldlen=" + str(change["oldlen"]) + "|newlen=" + str(change["newlen"]) + "|minor=" + minor + "|redirect=" + redirect + "|logid=" + logid + "|logtype=" + logtype + "|logaction=" + logaction + "|comment=" + change["comment"]

## Grab the last timestamp and add it to the variables.txt file to be used again (next time as end_timestamp) once the program runs again - sloppy, i know 
changes = json_response["query"]["recentchanges"]
end_timestamp = changes[len(changes)-1]["timestamp"]
try:
	variables_file = open(variables_filename, "w")
	variables_file.write(end_timestamp)
	variables_file.close()
except:
	print start_timestamp + "|status=Could not write to varaibles.txt"
	pass