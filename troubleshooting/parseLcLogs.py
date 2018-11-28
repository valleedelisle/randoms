#!/usr/bin/python
# Script to parse Dell's TSR logs and display on single lines
#
# David Vallee Delisle <david@valleedelisle.com>
#

import xml.etree.ElementTree as ET
import sys
from os import access, R_OK
from os.path import isfile

if len(sys.argv) < 2:
    print sys.argv[0] + " <XML File>\n"
    exit(1)

file = sys.argv[1]
if isfile(file) is False or access(file, R_OK) is False:
    print "File {} doesn't exist or isn't readable".format(file)
    exit(3)

tree = ET.parse(file)
root = tree.getroot()
for e in root:
    meta = {}
    for se in e:
        meta[se.tag] = se.text

    print str(e.get("Timestamp")) + " " + str(e.get("Severity")) + " [" + str(e.get("Category")) + " " + str(meta["MessageID"]) + " " + str(meta["FQDD"]) + "] " + str(meta["Message"])
