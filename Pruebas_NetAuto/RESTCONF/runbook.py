#!/usr/bin/env python

import requests
from nornir import InitNornir
from nornir.plugins.tasks.apis import http_method
from nornir.plugins.functions.text import print_result


def manage_rt(task, vrf_target, headers):
    # host-specific URL
    base_url = f"https://{task.host.hostname}/restconf"

    # Task 1: Use http_method to get the vrf config via HTTP GET
    task.run(
        task=http_method,
        name="Get VRF config via HTTP GET",
        method="get",
        url=base_url + vrf_target,
        auth=("admin", "admin"),
        headers=headers["get"],
        verify=False,
    )

    # Task 2: User http_method to update the VRF config via HTTP PUT
    task.run(
        task=http_method,
        name="Update VRF config via HTTP PUT",
        method="put",
        url=base_url + vrf_target,
        auth=("admin", "admin"),
        headers=headers["put_post"],
        verify=False,
        json=task.host["body"],
    )

    # Task 3: Save the config using HTTP POST
    task.run(
        task=http_method,
        name="Save VRF config via HTTP POST",
        method="post",
        url=base_url + "operations/cisco-ia:save-config",
        auth=("admin", "admin"),
        headers=headers["put_post"],
        verify=False,
    )


def main():

    # Disable SSl warnings, test environment
    requests.packages.urllib3.disable_warnings()

    # Define URL atrings and HTTP header
    vrf_target = "data/Cisco-IOS-XE-native:native/Cisco-IOS-XE-native:vrf"
    headers = {
        "get": {"Accept": "application/yang-data+json"},
        "put_post": {
            "Content-Type": "application/yang-data+json",
            "Accept": "application/yang-data+json, application/yang-data+json",
        },
    }
    nornir = InitNornir()
    result = nornir.run(
        task=manage_rt,
        name="Manage Devices via RESTCONF",
        vrf_target=vrf_target,
        headers=headers,
    )

    print_result(result)


if __name__ == "__main__":
    main()
