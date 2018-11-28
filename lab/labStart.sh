#!/bin/bash

if ipmitool -H 192.168.1.119 -U Administrator -P q1w2e3 -I lan power status | grep -q off; then
    ipmitool -H 192.168.1.119 -U Administrator -P q1w2e3 -I lan power on
fi
if ipmitool -H 192.168.1.127 -U root -P calvin -I lanplus power status | grep -q off; then
    ipmitool -H 192.168.1.127 -U root -P calvin -I lanplus power on
fi   
