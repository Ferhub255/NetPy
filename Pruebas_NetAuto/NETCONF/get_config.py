#! /usr/bin/env python

from ncclient import manager
from lxml.etree import tostring


def main():
    # in line inventory
    xr_xmlns = "http://cisco.com/ns/yang/Cisco-IOS-XR-infra-rsi-cfg"
    # vrf specific platform
    host_dict = {
        "192.168.0.202": f'<vrfs xmlns="{xr_xmlns}"></vrfs>',
        "192.168.0.201": "<native><vrf></vrf></native>",
    }

    for hostname, vrf_filter in host_dict.items():
        connect_params = {
            "host": hostname,
            "username": "admin",
            "password": "admin",
            "hostkey_verify": False,
            "allow_agent": False,
            "look_for_keys": False,
        }

        with manager.connect(**connect_params) as conn:
            print(f"{hostname}: Connection open")
            # RPC call get, section running subtree vrf
            get_resp = conn.get_config(source="running", filter=("subtree", vrf_filter))
            if get_resp.ok:
                print(f"{hostname}: VRF configuration start")
                xml_config = tostring(get_resp.data_ele, pretty_print=True)
                print(xml_config.decode().strip())
                print(f"{hostname}: VRF configuration end")
            else:
                print(f"{hostname}: Errors: {','.join(get_resp.errors)}")


if __name__ == "__main__":
    main()
