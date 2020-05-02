#! /usr/bin/env python

from jinja2 import Environment, FileSystemLoader
from yaml import safe_load
from ncclient import manager
from lxml.etree import fromstring


def save_config_ios(conn):
    save_rpc = '<save-config xmlns="http://cisco.com/yang/cisco-ia"/>'
    save_resp = conn.dispatch(fromstring(save_rpc))
    return save_resp


def main():
    # Read host file
    with open("hosts.yml", "r") as handle:
        host_root = safe_load(handle)

    for host in host_root["host_list"]:

        with open(f"vars/{host['name']}_vrfs.yml", "r") as handle:
            vrfs = safe_load(handle)

        j2_env = Environment(
            loader=FileSystemLoader("."), trim_blocks=True, autoescape=True
        )
        template = j2_env.get_template(f"templates/{host['platform']}_vpn.j2")
        new_vrf_config = template.render(data=vrfs["vrfs"])

        connect_params = {
            "host": host["ip"],
            "username": "admin",
            "password": "admin",
            "hostkey_verify": False,
            "allow_agent": False,
            "look_for_keys": False,
        }

        with manager.connect(**connect_params) as conn:
            # Apply the new config by replacing the VRF section.
            # This will delete unspecified VRF and subcomponents like RTs
            print(f"{host['name']}: Connection open")
            config_resp = conn.edit_config(
                target=host["edit_target"],
                config=new_vrf_config,
                default_operation=host.get("operation"),
            )

            print(f"{host['name']} Cheking edit-config response")
            if config_resp.ok:
                if host["platform"] == "iosxr":
                    save_resp = conn.commit()
                elif host["platform"] == "ios":
                    save_resp = save_config_ios(conn)

                if save_resp.ok:
                    print(f"{host['name']}: VRFs successfully updated")
            else:
                print(f"{host['name']}: Errors: {','.join(config_resp.errors)}")


if __name__ == "__main__":
    main()
