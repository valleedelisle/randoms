#!/usr/bin/env python
#
# sorts stdin by date
# I made this script before I knew oslo-log-merger existed.
#
# Usage:
# grep somestring /path/to/some/files* | sortByDate.py
#
#
import sys, re
from datetime import datetime

loglist = []
dateRex = re.compile('([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})')
for line in sys.stdin:
    m = re.search(dateRex, line)
    if m:
        time = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
        loglist.append({ "timestamp": time, "log": line})

loglist.sort(key=lambda r:r["timestamp"])
for l in loglist:
    print l["log"].rstrip()
