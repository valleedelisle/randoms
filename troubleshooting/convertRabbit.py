#!/usr/bin/env python
#
# Script that flattens those ugly rabbit logs
# It takes each event and put it on one row instead of multiple lines
#
# Usage:
# convertRabbit.py <file1> <file2> <fileX>... > allrabbit.log
#
#
import sys, re
from datetime import datetime

loglist = []
dateRex = re.compile('=([a-zA-Z]+) REPORT==== ([0-9]{2}-[a-zA-Z]+-[0-9]{4}::[0-9]{2}:[0-9]{2}:[0-9]{2})')
files = sys.argv[1:]
for f in files:
    fm = re.search('.*rabbit\@([^-^.]+)', f)
    if fm:
        host = fm.group(1)
    else:
        hm = re.search('.*([^\/]+)$', f)
        if hm:
            host = hm.group(1)
    for line in open(f).read().splitlines():
        m = re.search(dateRex, line)
        if m:
            try:
                print("%s %s %s %s" % (time, host, severity, text))
                text = ""
                del time
                del severity
            except:
                pass
            time = datetime.strptime(m.group(2), "%d-%b-%Y::%H:%M:%S")
            severity = m.group(1)
        else:
            try:
                text
            except NameError:
                text = ""
            text += str(line.rstrip()) + "||"
