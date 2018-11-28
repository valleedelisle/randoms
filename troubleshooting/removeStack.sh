#!/bin/bash
#
# Script that removes the overcloud stack and brings back the undercloud to a clean state
# Don't use this on production system please :)
#

source /home/stack/stackrc
for i in $(openstack stack list -c ID -f value);do echo "Removing stack $i";openstack stack delete $i;done;
for i in $(openstack baremetal node list -c UUID -f value);do echo "Removing node $i";openstack baremetal node power off $i; openstack baremetal node delete $i;done;
source stackrc
rm /home/stack/undercloud-passwords.conf
systemctl list-unit-files | grep openstack | awk '{print $1}' | xargs -I {} sudo systemctl stop {}
systemctl list-unit-files | grep neutron | awk '{print $1}' | xargs -I {} sudo systemctl stop {}
sudo systemctl stop keepalived
sudo rm -rf /var/lib/mysql /var/lib/rabbitmq /etc/keystone /opt/stack/.undercloud-setup /root/stackrc /home/stack/stackrc  /var/opt/undercloud-stack /var/lib/ironic-discoverd/discoverd.sqlite /var/lib/ironic-inspector/inspector.sqlite  /home/stack/.instack /root/tripleo-undercloud-passwords
dirs="ceilometer heat glance horizon ironic ironic-discoverd keystone neutron nova swift haproxy"; for dir in $dirs; do sudo rm -rf /etc/$dir ; sudo rm -rf /var/log/$dir ;  sudo rm -rf /var/lib/$dir; done
sudo yum remove -y rabbitmq-server mariadb haproxy openvswitch keepalived $(rpm -qa | grep openstack)
sudo rm -rf /etc/sysconfig/network-scripts/ifcfg-br-ctlplane
sudo sed -i '/ovs/d ; /OVS/d'  /etc/sysconfig/network-scripts/ifcfg-eth1
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!! remove all interface configuration which is related to openvswitch from /etc/sysconfig/network-scripts, e.g. ifcfg-br_int, ifcfg-ovs_system, ifcfg-brctlplane, etc. roll back the configuration of the local interface!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
sudo rm -rf /srv/node/1/objects/*
sudo reboot
