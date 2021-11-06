import yaml  # pyyaml
from yaml import load, dump
from subprocess import Popen, PIPE
import time
from deepdiff import DeepDiff, grep
import re
import shutil

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

with open(r'config.yml') as f:
    config = yaml.safe_load(f)
with open(r'config.yml.past') as f:
    config_past = yaml.safe_load(f)
lxd_ipv4 = config['lxd']['ipv4']
lxd_bridge = config['lxd']['bridge']


def prep_rhel(name):
    process = Popen(['lxc', 'exec', name, '--', 'yum', 'install', '-y', 'openssh-server'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    process = Popen(['lxc', 'exec', name, '--', 'systemctl', 'start', 'sshd'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    process = Popen(['lxc', 'exec', name, '--', 'bash', '-c', 'if [ ! -d /root/.ssh ]; then mkdir -p /root/.ssh; fi'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    process = Popen(['lxc', 'exec', name, '--', 'bash', '-c', 'if [ ! -d /root/.ssh ]; then mkdir -p /root/.ssh; fi'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    process = Popen(['lxc', 'exec', name, '--', 'bash', '-c', 'if [ ! -f /root/.ssh/authorized_keys ]; then touch /root/.ssh/authorized_keys; fi'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

def create_container(c):
    lxd_ipv4 = config['lxd']['ipv4']
    lxd_bridge = config['lxd']['bridge']
    authorized_keys = c['authorized_keys']
    image = c['image']
    name = c['name']
    proxy = c['proxy']
    ipv4 = c['ipv4']
    process = Popen(['lxc', 'init', image, name], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    # if len(stdout.decode()) != 0:
    #     print(stdout.decode())

    process = Popen(['lxc', 'network', 'attach', lxd_bridge, name, 'eth0', 'eth0'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if len(stdout.decode()) != 0:
        print(stdout.decode())

    process = Popen(['lxc', 'config', 'device', 'set', name, 'eth0', 'ipv4.address', ipv4], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if len(stdout.decode()) != 0:
        print(stdout.decode())

    for p in proxy:
        proto = p.split(':')[0]
        src_port = p.split(':')[1]
        dst_port = p.split(':')[2]
        process = Popen(['lxc', 'config', 'device', 'add', name, f'proxy4_{proto}{dst_port}', 'proxy', 'nat=true', f'listen={proto}:{lxd_ipv4}:{src_port}', f'connect={proto}:0.0.0.0:{dst_port}'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if len(stdout.decode()) != 0:
            print(stdout.decode())

    process = Popen(['lxc', 'start', name], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if len(stdout.decode()) != 0:
        print(stdout.decode())
    process = Popen(['lxc', 'exec', name, '--', 'bash', '-c', 'while [ ! -d /root ]; do sleep 2; done'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if "centos" in image.lower() or "rhel" in image.lower():
        prep_rhel(name)

    process = Popen(['lxc', 'exec', name, '--', 'bash', '-c', 'while [ ! -f /root/.ssh/authorized_keys ]; do sleep 2; done'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    for authorized_key in authorized_keys:
        process = Popen(['lxc', 'exec', name, '--', 'bash', '-c', f'grep \"{authorized_key}\" /root/.ssh/authorized_keys || echo {authorized_key} >> /root/.ssh/authorized_keys'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        # print(stdout.decode(), stderr.decode())
    # print(f"Successfully created container {name}.")


def list_containers():
    process = Popen(['lxc', 'list'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode())


def main():
    for container_name in config['containers']:
        container = config['containers'][container_name]
        create_container(container)
    list_containers()


def proxy_add(name, v):
    proto = v.split(':')[0]
    src_port = v.split(':')[1]
    dst_port = v.split(':')[2]
    process = Popen(['lxc', 'config', 'device', 'add', name, f'proxy4_{proto}{dst_port}', 'proxy', 'nat=true', f'listen={proto}:{lxd_ipv4}:{src_port}', f'connect={proto}:0.0.0.0:{dst_port}'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode(), stderr.decode())


def proxy_remove(name, v):
    proto = v.split(':')[0]
    src_port = v.split(':')[1]
    dst_port = v.split(':')[2]
    process = Popen(['lxc', 'config', 'device', 'remove', name, f'proxy4_{proto}{dst_port}'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode(), stderr.decode())


def proxy_remove(name, v):
    proto = v.split(':')[0]
    src_port = v.split(':')[1]
    dst_port = v.split(':')[2]
    process = Popen(['lxc', 'config', 'device', 'remove', name, f'proxy4_{proto}{dst_port}'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode(), stderr.decode())


def container_remove(name):
    print(f"Removing container {name}.")
    process = Popen(['lxc', 'delete', '-f', name], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode(), stderr.decode())


def container_add(name):
    print(f"Adding container {name}.")
    authorized_keys = config['containers'][name]['authorized_keys']
    image = config['containers'][name]['image']
    ipv4 = config['containers'][name]['ipv4']
    process = Popen(['lxc', 'init', image, name], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode(), stderr.decode())
    process = Popen(['lxc', 'network', 'attach', lxd_bridge, name, 'eth0', 'eth0'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode(), stderr.decode())
    process = Popen(['lxc', 'config', 'device', 'set', name, 'eth0', 'ipv4.address', ipv4], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    process = Popen(['lxc', 'start', name], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stdout.decode(), stderr.decode())
    process = Popen(['lxc', 'exec', name, '--', 'bash', '-c', 'while [ ! -d /root ]; do sleep 2; done'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if "centos" in image.lower() or "rhel" in image.lower():
        prep_rhel(name)

    process = Popen(['lxc', 'exec', name, '--', 'bash', '-c', 'while [ ! -f /root/.ssh/authorized_keys ]; do sleep 2; done'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    for authorized_key in authorized_keys:
        process = Popen(['lxc', 'exec', name, '--', 'bash', '-c', f'grep \"{authorized_key}\" /root/.ssh/authorized_keys || echo {authorized_key} >> /root/.ssh/authorized_keys'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
       #  print(stdout.decode(), stderr.decode())


def proxy_changed(name, v):
    proxy_remove(name, v)
    proxy_add(name, v)


def a():
    # print(config)
    diff = DeepDiff(config_past, config, ignore_order=True)
    if len(diff) > 0:
        print(diff)
    if 'iterable_item_added' in diff:
        for k,v in diff['iterable_item_added'].items():
            k_list = re.findall("\['(.*?)'\]", k)
            name = k_list[1]
            if k | grep("proxy"):
                proxy_add(name, v)
    if 'iterable_item_removed' in diff:
        for k,v in diff['iterable_item_removed'].items():
            k_list = re.findall("\['(.*?)'\]", k)
            name = k_list[1]
            if k | grep("proxy"):
                proxy_remove(name, v)
    if 'values_changed' in diff:
        for k,v in diff['values_changed'].items():
            k_list = re.findall("\['(.*?)'\]", k)
            name = k_list[1]
            if k | grep("proxy"):
                # proxy_changed(name, v)
                msg = "E: Changes in proxy not supported."
                print(msg)
                msg = "Please remove and add new"
                print(msg)
    if 'dictionary_item_removed' in diff:
        # for k in diff['iterable_item_added'].items():
        for k in diff['dictionary_item_removed']:
            k_list = re.findall("\['(.*?)'\]", k)
            name = k_list[1]
            if k | grep("containers"):
                container_remove(name)
    if 'dictionary_item_added' in diff:
        # for k in diff['iterable_item_added'].items():
        for k in diff['dictionary_item_added']:
            k_list = re.findall("\['(.*?)'\]", k)
            name = k_list[1]
            if k | grep("containers"):
                container_add(name)


if __name__ == "__main__":
    # main()
    a()
    shutil.copy('config.yml', 'config.yml.past')
