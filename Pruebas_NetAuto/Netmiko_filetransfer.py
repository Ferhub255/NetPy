#!/usr/bin/python3
"""
Uso de Netmiko para transferir un archivo
"""
import time
import sys 
from netmiko import Netmiko, file_transfer
from yaml import safe_load


def main(argv):
    """
    Inventory: IOS v15 cisco ios
    """
    # Reads hosts.yml files into structured data, may raise YAMLError
    with open("hosts.yml", "r") as host_file:
        host_list = safe_load(host_file)

    platform_map = {"ios": "cisco_ios", "iosxr": "cisco_xr"}

    # recorremos la lista de dispositivos del diccionario
    for host in host_list["host_list"]:

        platform = platform_map[host["platform"]]

        # Create netmiko instance
        conn = Netmiko(
            ip=host["ip"],
            port=22,
            username="admin",
            password="admin",
            device_type=platform,
            secret="cisco",
            global_delay_factor=2,
        )
        print(f"Entramos exitosamente a {conn.find_prompt()}")
        print(f" Uploading {argv[1]}...")
        result = file_transfer(
            conn,
            source_file=argv[1],
            dest_file=argv[1],
            file_system=host.get("file_system"),
            # la funcion get va a tratar de buscar el key file_systme
            # si no lo logra devuleve None
            socket_timeout=10.0,
        )
        
        print(f" Details: {result}\n")
        conn.disconnect()
        


if __name__ == "__main__":
    # le pasamos el archivo como un argumento
    main(sys.argv)
