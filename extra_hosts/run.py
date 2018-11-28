import docker
from os import environ as env

extra_host_domain = env.get("EXTRA_HOSTS_POSTFIX", "AAA")

extra_hosts = {}
hosts = open('/etc/hosts','r')

for line in hosts:
    if extra_host_domain in line:
        host = line.split()[1]
        ip = line.split()[0]
        extra_hosts[host] = ip

client = docker.from_env()

c=client.containers.run("alpine", "ping -c 2 predator.osparc.io", detach=True, extra_hosts=extra_hosts)
for line in c.logs(stream=True):
    print(line.strip())
