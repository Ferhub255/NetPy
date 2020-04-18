#!/usr/bin/env python3
"""
Automatizacion de la red
Autor: Carlos Fernando Tapia Vaca <fernando.tapiavaca@yandex.com>

	ScriptbgSSH.py
	Este script esta diseñado para relevamiento de datos de Swiches con cisco_ios
	pertenecientes al Cliente ############.
Ultima revision 04-09-2019 11:30 Santa Cruz de la Sierra - Bolivia
"""

# Librerias
from netmiko import ConnectHandler
import datetime
import sys

# Variables
device = {
    "device_type": "cisco_ios",
    "ip": "",
    "username": "user",
    "password": "password",
}


print("\n---->NetAuto ha iniciado: \n")


def main():
    corrupto = ""
    # extraer lineas del archivo de Accesso
    try:
        with open(
            input("Ingrese Nombre de Archivo con formato [ip username password]: ")
        ) as f:
            archivo = f.read().splitlines()
    except:
        print("Fallo al abrir el Archivo")
        sys.exit()
    for direccion in archivo:

        # Asignar Direcciones y Credenciales
        linea = direccion.split()
        device["ip"] = linea[0]
        # device['username']=linea[1]
        # device['password']=linea[2]

        # intentar Conexion
        try:
            net_connect = ConnectHandler(**device)
        except:
            print(" Conexion Fallida: " + linea[0] + "\n")
            corrupto += direccion + "\n"
            continue
        print("\nConexion Exitosa: " + linea[0])

        # Intentar Enable
        try:
            net_connect.enable()
        except:
            print(
                "\n Fallo Enable, privilegios de la cuenta insuficientes: "
                + linea[0]
                + "\n"
            )
            corrupto += direccion + " ->Fallo enable" + "\n"
            continue

        # Reunir Datos
        output = ""
        output += "\n----------------------------VERSION---------------------------\n"
        output += net_connect.send_command("show version")
        output += "\n------------------------CONFIGURATION-------------------------\n"
        output += net_connect.send_command("show run")
        nombre = net_connect.find_prompt() + linea[0]

        # Creamos el archivo
        file = open(nombre, "wt")
        file.write(output)
        file.write("\n Creado en: " + str(datetime.datetime.now()) + "\n")
        file.close()
        print(" Archivo Creado")
        net_connect.disconnect()
        print("Desconectado\n")

    file = open("corruptos", "at")
    file.write("+++++++++++++++++++++++++++++++++++++++++++++++++++")
    file.write(corrupto)
    file.write("\n Creado en: " + str(datetime.datetime.now()) + "\n")
    file.close()
    print(" Lista de Corruptos Actualizada")
    print("----------------------------------->Fin")


main()
