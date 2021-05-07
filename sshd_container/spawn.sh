podman rm -f $(podman ps -a -f name=rootless_ssh -q)
echo "[ansible_containers]" > ansible_inventory
for i in {10..30};do
    container_name="rootless_ssh$i"
    container_port="330${i}"
    echo "$container_name ansible_user=admin ansible_connection=ssh ansible_port=$container_port ansible_host=127.0.0.1" >> ansible_inventory
    podman run -d --name=$container_name -p 330${i}:2022 --cgroup-manager=cgroupfs localhost/testsshd
    #-v ssh${i}logs:/var/log/journal:Z 
done
