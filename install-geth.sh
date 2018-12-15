#!/usr/bin/env bash
## Quick & simple install using ethereum ppa.

set -exo pipefail

sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:ethereum/ethereum
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y ethereum


cat > /etc/systemd/system/geth.service <<EOF
[Unit]
Description=Ethereum Go Client
After=network.target

[Service]
User=geth
WorkingDirectory=/var/lib/geth
ExecStart=/usr/bin/geth --ws --rpc --rpcaddr 0.0.0.0 --rpcport 8545 
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

mkdir -p /var/lib/geth
useradd --home /var/lib/geth geth
chown geth:geth /var/lib/geth

systemctl enable geth.service
