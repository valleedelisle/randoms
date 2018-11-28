#!/bin/bash
screen -d -m -S osp
screen -S osp -p 0 -X stuff "ssh stack@undercloud-0^Msource ~/stackrc^Mnova list^Mheat stack-list^M"
SN=0
while read s;do
 SN=$(expr $SN + 1)
 NAME=$(echo $s | awk '{ print $1; }')
 IP=$(echo $s | grep -oP 'ctlplane=\K([0-9\.]+)');
 screen -S osp -X screen $SN
 screen -S osp -p $SN -X stuff "ssh stack@undercloud-0^Mssh heat-admin@$IP^Msudo -i^M"
 echo "$NAME $IP"
done < <(ssh stack@undercloud-0 "source stackrc;openstack server list -f value -c Name -c Networks | sort")

SN=$(expr $SN + 1)
screen -S osp -X screen $SN
screen -S osp -p $SN -X stuff "top^M"
