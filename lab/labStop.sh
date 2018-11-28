#!/bin/bash

for s in r610; do
 ssh $s "virsh list --all | grep -P '^[\s]*[0-9]+.*running' | sort -k2 | awk '{ print \$1; }' | xargs -I% -P 12 virsh shutdown % --mode agent" 
 while [ $(ssh $s "virsh list --all | grep -P '^[\s]*[0-9]+.*running' | wc -l") -gt "0" ]; do
     ssh $s "virsh list --all | grep -P '^[\s]*[0-9]+.*running' | sort -k2 | awk '{ print \$1; }' | xargs -I% -P 12 virsh shutdown %" 
     sleep 10
 done
 ssh $s "shutdown -h now"
done
