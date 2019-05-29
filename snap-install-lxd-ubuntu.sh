sudo apt-get update
sudo apt-get -y dist-upgrade
# sudo apt-get remove -y lxd
sudo apt remove --purge -y lxd lxd-client
sudo apt install -y zfsutils-linux
adduser myuser --gecos "" --disabled-password
adduser myuser lxd
adduser myuser sudo
sudo snap install lxd
sudo lxd init
sudo lxc list
# sudo snap start lxd

exit

Cleanup stuff 
# /var/snap/lxd/common/lxd/storage-pools
#
# use 'zfs destroy -r default' to destroy all datasets in the pool
# use 'zpool destroy default' to destroy the pool itself


basic config print below
"
config: {}
networks:
- config:
    ipv4.address: auto
    ipv6.address: auto
  description: ""
  managed: false
  name: lxdbr0
  type: ""
storage_pools:
- config:
    size: 300GB
  description: ""
  name: default
  driver: zfs
profiles:
- config: {}
  description: ""
  devices:
    eth0:
      name: eth0
      nictype: bridged
      parent: lxdbr0
      type: nic
    root:
      path: /
      pool: default
      type: disk
  name: default
cluster: null
"
