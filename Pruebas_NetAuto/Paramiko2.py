#!/usr/bin/python3
"""
Uso de Paramiko
"""
import time 
import paramiko
from yaml import safe_load
from jinja2 import Environment, FileSystemLoader

def send_cmd(conn, command):
    '''
    Dada una conexion, manda un comando
    '''

    conn.send(command + "\n")
    #Necesitamos esperar a que el esquipo responda
    time.sleep(4)

def get_output(conn):
    """
    Recibe datos del equipo, recibe en Bytestream, 
    tenemos que decodificar
    """
    return conn.recv(65535).decode("utf-8")

def main():
    '''
    Inventory: IOS v15
    '''
    
    # Reads hosts.yml files into structured data, may raise YAMLError
    with open("hosts.yml", "r") as host_file:
        host_list = safe_load(host_file)

    # recorremos la lista de dispositivos del diccionario
    for host in host_list["host_list"]:

        # Extraemos las configuraciones en diccionario
        with open(f"vars/{host['name']}_vrf.yml", 'r') as vrf_configfile:
            vrfs = safe_load(vrf_configfile)

        # Setup the jinja2 templating environment and render the template
        j2_env = Environment(  #inicializamos el Environment
            loader=FileSystemLoader("."), #identificamos el directorio
            trim_blocks=True, # Remueve los espacios en blanco de la izquierda
            autoescape=True
        )

        template = j2_env.get_template( #cargar el template
            f"paramiko/{host['platform']}_vpn.j2"
        )
        # Manera alternatica
        #new_vrf_config = ""
        #for vrf in vrfs['vrf']:
        #    new_vrf_config += template.render(vrf=vrf)

        # le pasamos el diccionario en una variable llamada data
        new_vrf_config = template.render(data = vrfs)

        # Create paramiko SSH client to connect to device
        conn_params = paramiko.SSHClient()
        conn_params.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn_params.connect(
            hostname = host['ip'],
            port = 22,
            username = "admin",
            password = "admin",
            look_for_keys = False,
            allow_agent = False,
        )
    
        conn = conn_params.invoke_shell()
        time.sleep(1.0)
        print(f"Entramos exitosamente a {get_output(conn)[-4:-1]}")

        # Enviamos la configuracion
        print(new_vrf_config)
        send_cmd(conn, new_vrf_config)
        print(f"Se configuro {host['name']} con VRF")
        conn.close()

if __name__ == "__main__":
    main()