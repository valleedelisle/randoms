VERSION=10
BUILD=GA
#BUILD=Z5
HOST=10.12.209.237
HOST_USER=root
HOST_KEY=~/.ssh/id_ecdsa
ANSIBLE_LOG_PATH=deploy.log
PIP=.venv/bin/pip2.7


virtualenv .venv && source .venv/bin/activate
$PIP install --upgrade pip 
$PIP install --upgrade setuptools
$PIP install --upgrade infrared
$PIP install .
infrared plugin add plugins/virsh
infrared plugin add plugins/tripleo-undercloud
infrared plugin add plugins/tripleo-overcloud
infrared workspace checkout $HOST
#time infrared virsh --cleanup True --host-address $HOST --host-user $HOST_USER --host-key $HOST_KEY
#time infrared virsh -v --host-memory-overcommit True \
#    --host-address $HOST \
#    --host-key $HOST_KEY \
#    --host-user $HOST_USER \
#    --topology-nodes "undercloud:1,controller:3,compute:1" \
#    -e override.controller.cpu=2 \
#    -e override.controller.memory=8192 \
#    -e override.controller.disks.disk1.size=60G \
#    -e override.compute.disks.disk1.size=60G \
#    -e override.compute.memory=32768 \
#    -e override.compute.cpu=8 \
#    -e override.undercloud.memory=16384

time infrared tripleo-undercloud --version $VERSION --build $BUILD --images-task rpm --ssl true 
##--cdn cdn_creds.yml
time infrared tripleo-overcloud --deployment-files virt \
    --version $VERSION \
    --introspect yes \
    --tagging yes --post yes --deploy yes \
    --network-backend vxlan --overcloud-ssl true \
    --overcloud-debug true \
    --config-heat ComputeExtraConfig.nova::allow_resize_to_same_host=true \
    --overcloud-templates infra_low_mem.yaml

infrared cloud-config -vv \
    -o cloud-config.yml \
    --deployment-files virt \
    --tasks create_external_network,forward_overcloud_dashboard,network_time,tempest_deployer_input


#  To beaker
# ir beaker --url=beaker.server.url --user=beaker.user --password=beaker.password --host-address=host.to.be.provisioned

