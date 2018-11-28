#!/bin/bash
#
# Just a little grep that filters out garbage off syslog
# This should probably be an alias
#
grep -vP "/etc/cron.hourly|session-[0-9]+\.scope (pam_unix|Received disconnect)|systemd-logind.service (Removed session|New session)|/usr/lib64/sa/sa1|(Starting|Started|Stopped|Stopping) Session|(Starting|Stopping) User Slice|(Starting|Stopping) user-[0-9]+.slice|(Created|Removed) slice|os-collect-config(\.service)*[:]*.*(local-data not found. Skipping|No local metadata found)|snmpd(\.service)*(\[[0-9]+\]:)* Connection from UDP:" $*
