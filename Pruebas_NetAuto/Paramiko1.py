#!/usr/bin/python3
"""
Uso de Paramiko
"""
import time 
import paramiko

def send_cmd(conn, command):
    '''
    Dada una conexion, manda un comando
    '''

    conn.send(command + "\n")
    #Necesitamos esperar a que el esquipo responda
    time.sleep(5)

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
    host_dict = {
        "192.168.0.201": "show running-config | section vrf_definition",
        "192.168.0.202": "show running-config vrf",
    }
    #Para cada equipo hacemos un conexion y enciamos el comando
    for ip, vrf_command in host_dict.items():
        # Se instancia un cliente SSH paramiko
        conn_params = paramiko.SSHClient()
        # Se ignora missing keys, lab environment
        conn_params.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn_params.connect(
            hostname = ip,
            port=22,
            username="admin",
            password="admin",
            look_for_keys=False, # no buscar las llaves crypto
            allow_agent=False, # no usar agentes locales SSH
        )

        conn = conn_params.invoke_shell()
        time.sleep(1.0)
        print(f"Entramos exitosamente a {get_output(conn).strip()}")

        commands = [
            "enable",
            "cisco",
            "terminal length 0",
            "show version | include Software",
            vrf_command,
        ]
        output = ""
        for command in commands:
            send_cmd(conn, command)
            output += get_output(conn)
        conn.close()

        print(f"Writing {ip} facts to file")
        with open(f"{ip}_facts.txt") as file:
            file.write(output)

if __name__ == "__main__":
    main()