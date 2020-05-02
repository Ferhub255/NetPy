#!/usr/bin/env python

import logging
from nornir import InitNornir
from nornir.plugins.functions.text import print_result
from nornir.plugins.tasks.networking import (
    napalm_get,
    napalm_configure,
    netmiko_send_command,
    # napalm_cli,
)
from parse_model import get_rt_parser, rt_diff
from nornir.plugins.tasks.text import template_file
from nornir.plugins.tasks.files import write_file


def manage_rt(task):

    # Task 1: Gather facts using NAPALM to get model ID
    task1_result = task.run(task=napalm_get, getters=["get_facts"])
    model = task1_result[0].result["get_facts"]["model"]
    print(f"{task.host.name}: connected as model type {model}")

    # Task 2: Collect the VRF running configuration using netmiko
    task2_result = task.run(
        task=netmiko_send_command, command_string=task.host["vrf_cmd"]
    )
    cmd_output = task2_result[0].result
    # ALTERNATIVA usando NAPALM_CLI
    # task2_result = task.run(task = napalm_cli, commands = [task.host["vrf_cmd"]])
    # cmd_output = task2_result[0].result[task.host["vrf_cmd"]]

    # determine the parser, commparar configuraciones
    parse_rt = get_rt_parser(task.host.platform)
    vrf_data = parse_rt(cmd_output)
    rt_updates = rt_diff(task.host["vrfs"], vrf_data)

    # Task 3: Create the template of config to add
    task3_result = task.run(
        task=template_file,
        template=f"{task.host.platform}_vpn.j2",
        path="templates",
        data=rt_updates,
    )
    new_vrf_config = task3_result[0].result

    # Task 4: Configure the devices using NAPALM and print updates
    task4_result = task.run(task=napalm_configure, configuration=new_vrf_config)
    if task4_result[0].diff:
        print(f"{task.host.name}: diff below\n{task4_result[0].diff}")
    else:
        print(f"{task.host.name}: no diff; config up to date")


def main():
    # Inicializar
    nornir = InitNornir()
    print("Nornir initializaed with inventory hosts:")
    for host in nornir.inventory.hosts.keys():
        print(host)

    result = nornir.run(task=manage_rt)

    print_result(result, severity_level=logging.WARNING)


if __name__ == "__main__":
    main()
