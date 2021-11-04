import yaml  # pyyaml
from yaml import load, dump
from subprocess import Popen, PIPE

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

with open(r'config.yml') as f:
    config = yaml.safe_load(f)
    # print(config['containers']['u3'])
    # create_container(config['containers']['u3'])
    # config = yaml.load(f, loader=Loader)
    # config = load(f, loader=Loader)

def create_container(c):
    lxd_ipv4 = config['lxd']['ipv4']
    lxd_bridge = config['lxd']['bridge']
    authorized_keys = c['authorized_keys']
    image = c['image']
    name = c['name']
    proxy = c['proxy']
    ipv4 = c['ipv4']
    # process = Popen(['lxc', 'init', image, name], stdout=PIPE, stderr=PIPE)
    # stdout, stderr = process.communicate()
    # print(stdout.decode())


    process = Popen(['lxc', 'network', 'attach', lxd_bridge, name, 'eth0', 'eth0'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if len(stdout.decode()) != 0:
        print(stdout.decode())

    process = Popen(['lxc', 'config', 'device', 'set', name, 'eth0', 'ipv4.address', ipv4], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if len(stdout.decode()) != 0:
        print(stdout.decode())



    for p in proxy:
        src_port = p.split(':')[0]
        dst_port = p.split(':')[1]
        process = Popen(['lxc', 'config', 'device', 'add', name, f'proxy4_tcp{dst_port}', 'proxy', 'nat=true', f'listen=tcp:{lxd_ipv4}:{src_port}', f'connect=tcp:0.0.0.0:{dst_port}'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if len(stdout.decode()) != 0:
            print(stdout.decode())

    process = Popen(['lxc', 'start', name], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if len(stdout.decode()) != 0:
        print(stdout.decode())


    for authorized_key in authorized_keys:
        process = Popen(['lxc', 'exec', name, '--', 'bash', '-c', f'grep \"{authorized_key}\" /root/.ssh/authorized_keys || echo {authorized_key} >> /root/.ssh/authorized_keys'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        # print(stdout.decode())

    print("done")
    return True

create_container(config['containers']['u3'])
