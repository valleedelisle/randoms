VERSION=15
BUILD=passed_phase2
#BUILD=Z5
HOST=192.168.88.251
HOST_USER=root
HOST_KEY=~/.ssh/id_ecdsa
ANSIBLE_LOG_PATH=deploy.log
PIP=.venv/bin/pip


virtualenv .venv && source .venv/bin/activate
$PIP install --upgrade pip 
$PIP install --upgrade setuptools
$PIP install --upgrade infrared
$PIP install .
infrared plugin add plugins/virsh
infrared plugin add plugins/tripleo-undercloud
infrared plugin add plugins/tripleo-overcloud
infrared workspace checkout $HOST
time infrared virsh --cleanup True --host-address $HOST --host-user $HOST_USER --host-key $HOST_KEY
time infrared virsh -v --host-memory-overcommit True \
    --host-address $HOST \
    --host-key $HOST_KEY \
    --host-user $HOST_USER \
    --image-url http://rhos-qe-mirror-tlv.usersys.redhat.com/brewroot/packages/rhel-guest-image/8.1/393/images/rhel-guest-image-8.1-393.x86_64.qcow2 \
    --topology-nodes "undercloud:1,controller:3,compute:1" \
    -e override.controller.cpu=4 \
    -e override.controller.memory=12288\
    -e override.controller.disks.disk1.size=60G \
    -e override.compute.disks.disk1.size=60G \
    -e override.compute.memory=32768 \
    -e override.compute.cpu=8 \
    -e override.undercloud.memory=16384 

time infrared tripleo-undercloud --version $VERSION --build $BUILD --images-task rpm --ssl true 
##--cdn cdn_creds.yml
time infrared tripleo-overcloud --deployment-files virt \
    --version $VERSION \
    --introspect yes \
    --tagging yes --postreboot yes --deploy yes \
    --network-backend flat --overcloud-ssl true \
    --overcloud-debug true \
    --config-heat ComputeExtraConfig.nova::allow_resize_to_same_host=true \
    --overcloud-templates infra_low_mem.yaml

infrared cloud-config -vv \
    -o cloud-config.yml \
    --deployment-files virt \
    --tasks create_external_network,forward_overcloud_dashboard,network_time,tempest_deployer_input


#  To beaker
# ir beaker --url=beaker.server.url --user=beaker.user --password=beaker.password --host-address=host.to.be.provisioned

