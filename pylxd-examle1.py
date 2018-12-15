#!/usr/bin/env python3

import logging
from pylxd import Client
from time import sleep
import uuid

logging.basicConfig(
    filename=f'script.log',
    filemode='a',
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S.%f",
    level=logging.DEBUG)


def main():
    client = Client()
    geth_container = client.containers.create(
            get_container_config(), wait=True)
    print(geth_container.name)
    geth_container.start(wait=True)
    sleep(10)  # Wait for DHCP and internet access.
    filedata = open("./install-geth.sh").read()
    r = geth_container.files.put("/tmp/install.sh", filedata, mode="0750")
    r = geth_container.execute(["/bin/bash", "-c", "/tmp/install.sh"])
    print(r)
    if r.exit_code != 0:
        raise Exception(f"E: Issue with install script! {r}")
    r = geth_container.execute(
            ["/bin/bash", "-c", "systemctl start geth.service"])
    print(r)
    if r.exit_code != 0:
        raise Exception(f"E: Issue with service start! {r}")
    sleep(1)  # Wait for geth rpc to be fully available. Bug maybe?
    r = geth_container.execute(
            ["/bin/bash", "-c", "geth attach http://localhost:8545"])
    print(r)
    if r.exit_code != 0:
        raise Exception(f"E: Issue geth attach to rpc! {r}")
    geth_container.stop(wait=True)
    geth_container.delete(wait=True)


def get_container_config():
    DISTRO_CODENAME = "bionic"
    PROFILE_NAME = "default"
    APP_NAME = "geth"
    container_name = get_app_uuid(APP_NAME)
    if DISTRO_CODENAME == "bionic":
        server = "https://cloud-images.ubuntu.com/daily"
        alias = "bionic/amd64"
    elif DISTRO_CODENAME == "buster":
        server = "https://us.images.linuxcontainers.org/"
        alias = "debian/buster"
    else:
        server = "https://us.images.linuxcontainers.org/"
        alias = "debian/buster"
        print("E: Unsupported OS release codename!")
        raise Exception("E: Unsupported OS release codename!")

    pylxd_container_config = {
        "name": container_name,
        "source": {
            "type": "image",
            "mode": "pull",
            "server": server,
            "protocol": "simplestreams",
            "alias": alias},
        "profiles": [PROFILE_NAME]
    }

    return pylxd_container_config


def get_app_uuid(app_name):
    return app_name + uuid.uuid4().hex[:5]


if __name__ == "__main__":
    main()
