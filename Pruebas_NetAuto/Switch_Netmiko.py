#!/usr/bin/python3
"""
Uso de Netmiko
"""
import time
from netmiko import Netmiko
from yaml import safe_load
from jinja2 import Environment, FileSystemLoader


def main():
    """
    Inventory: IOS v15 cisco ios
    """
    # Reads hosts.yml files into structured data, may raise YAMLError
    with open("hosts.yml", "r") as host_file:
        host_list = safe_load(host_file)

    platform_map = {"ios": "cisco_ios", "iosxr": "cisco_xr"}

    # recorremos la lista de dispositivos del diccionario
    for host in host_list["host_list"]:

        platform = host["platform"]

        # Extraemos las configuraciones en diccionario
        with open(f"vars/{host['name']}_vrf.yml", "r") as vrf_configfile:
            vrfs = safe_load(vrf_configfile)

        # Setup the jinja2 templating environment and render the template
        j2_env = Environment(  # inicializamos el Environment
            loader=FileSystemLoader("."),  # identificamos el directorio
            trim_blocks=True,  # Remueve los espacios en blanco de la izquierda
            autoescape=True,
        )

        template = j2_env.get_template(  # cargar el template
            f"paramiko/{host['platform']}_vpn.j2"
        )
        # le pasamos el diccionario en una variable llamada data
        new_vrf_config = template.render(data=vrfs)

        # Create netmiko instance
        conn = Netmiko(
            ip=host["ip"],
            port=22,
            username="admin",
            password="admin",
            device_type=platform_map[platform],
            secret="cisco",
            global_delay_factor=2,
        )
        print(f"Entramos exitosamente a {conn.find_prompt()}")

        # Enviamos la configuracion, delay_facto 2=1seg
        conn.send_config_set(
            new_vrf_config.splitlines(), delay_factor=20, cmd_verify=False
        )
        conn.disconnect()
        # print(output)


if __name__ == "__main__":
    main()
