podman build -t testsshd -f Dockerfile --cgroup-manager=cgroupfs --build-arg ADMIN_PUBLIC_KEY="$(cat ~/.ssh/id_ecdsa.pub)"
