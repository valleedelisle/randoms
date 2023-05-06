#! /bin/bash
# source https://stackoverflow.com/questions/62592461/updating-existing-ips-from-a-security-group-in-aws-using-aws-cli

# need my current ip
MY_IP=$(curl --silent https://checkip.amazonaws.com)
echo "Your IP is ${MY_IP}"
MY_CIDR="${MY_IP}/32"
# need security group id(s) and existing CIDR for the SG
sgs=$(aws ec2 describe-security-groups | jq -c '.SecurityGroups[]? | select( (.Tags[]? | select(.Key == "ssh-from-my-ip") | .Value | test("true|yes"; "i")))') # | if .IpPermissions | length == 0 then {sg: .GroupId, cidr: null } else {sg: .GroupId, cidr: .IpPermissions[].IpRanges[].CidrIp, desc: .IpPermissions[].IpRanges[].Description} end')
group_id=$(echo $sgs | jq -r '.GroupId')
echo $sgs | jq -c '.IpPermissions[]' | while read l; do
  port=$(echo $l | jq '.FromPort')
  if [[ $port != '22' ]]; then
    continue
  fi
  echo $l | jq -c '.IpRanges[]' | while read i; do
    desc=$(echo $i | jq -r '.Description')
    cidr=$(echo $i | jq -r '.CidrIp')
    if [[ $desc == 'ssh-from-my-ip' ]]; then
      echo "Revoking $cidr"
      aws ec2 revoke-security-group-ingress \
          --group-id "${group_id}" \
          --protocol tcp \
          --port 22 \
          --cidr "${cidr}"
    fi
  done
done
aws ec2 authorize-security-group-ingress --group-id "${group_id}" --ip-permissions '[{"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22, "IpRanges": [{"CidrIp": "'"${MY_CIDR}"'", "Description": "ssh-from-my-ip"}]}]'
