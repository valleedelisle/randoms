FROM fedora:34

ARG ADMIN_PUBLIC_KEY

RUN yum -y install openssh-server ed openssh-clients && yum clean all 
RUN sed -i 's/#Port.*$/Port 2022/' /etc/ssh/sshd_config && chmod 775 /var/run && rm -f /var/run/nologin
RUN adduser --system -s /bin/bash -u 1001 admin && \
           mkdir -p /home/admin/.ssh && \
           ssh-keygen -A
RUN touch /home/admin/.ssh/authorized_keys && \
           chmod 700 /home/admin/.ssh && \
           chmod 600 /home/admin/.ssh/authorized_keys && \
           sed -i 's/1001/0/g' /etc/passwd && \
           echo ${ADMIN_PUBLIC_KEY} >> /home/admin/.ssh/authorized_keys && \
           chown -R admin /home/admin
LABEL Description="This ssh server is running with rootless podman"
EXPOSE 2022

CMD ["/sbin/sshd", "-D"]
