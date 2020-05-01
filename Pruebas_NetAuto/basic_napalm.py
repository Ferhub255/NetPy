#!/usr/bin/env python

from napalm import get_network_driver
from jinja2 import Environment, FileSystemLoader
from yaml import safe_load


def main():
    # read yaml file into estructured data
    with open("hosts.yml", "r") as handle:
        host_root = safe_load(handle)

    for host in host_root["host_list"]:
        # Determine and create the network driver object based on platform
        print(f"Getting {host['platform']} driver")
        #breakpoint()
        driver = get_network_driver(host["platform"])
        conn = driver(hostname=host["ip"], username="admin", password="admin")
        print("openning connections")
        conn.open()
        #facts = conn.get_facts()
        #print(facts)
        #print(f"{facts['hostname']} model type: {facts['model']}")

        # read yaml file into structured data
        with open(f"vars/{host['name']}_vrf.yml") as handle:
            vrfs = safe_load(handle)

        # template the configuration
        j2_env = Environment(
            loader=FileSystemLoader("."), trim_blocks=True, autoescape=True
        )
        template = j2_env.get_template(f"templates/{host['platform']}_vpn.j2")
        new_vrf_config = template.render(data=vrfs)
        print(new_vrf_config)
        # NAPALM merging to compare and merge RT updates
        conn.load_merge_candidate(config=new_vrf_config)
        diff = conn.compare_config()

        if diff:
            print(diff)
            print("Committing configuration changes")
            conn.commit_config()
        else:
            print("no diff; config up to date")

        conn.close()
        print("\nOK!\n")


if __name__ == "__main__":
    main()
