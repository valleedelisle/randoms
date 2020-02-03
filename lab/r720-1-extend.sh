VERSION=10
BUILD=GA
#BUILD=Z5
HOST=192.168.88.244
HOST_USER=root
HOST_KEY=~/.ssh/id_ecdsa
ANSIBLE_LOG_PATH=deploy.log
PIP=.venv/bin/pip2.7

infrared workspace checkout $HOST
time infrared virsh -v --host-memory-overcommit True \
    --host-address $HOST \
    --host-key $HOST_KEY \
    --host-user $HOST_USER \
    --topology-nodes "compute:1" \
    --topology-extend yes \
    -e override.controller.cpu=2 \
    -e override.controller.memory=8192 \
    -e override.controller.disks.disk1.size=60G \
    -e override.compute.disks.disk1.size=60G \
    -e override.compute.memory=32768 \
    -e override.compute.cpu=8 \
    -e override.undercloud.memory=16384
