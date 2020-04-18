#!/usr/bin/env python3
"""
Automatizacion de configuraciones de la red
Autor: Carlos Fernando Tapia Vaca <fernando.tapiavaca@yandex.com>

	AdicionarReglasWLC.py
	Este script de proposito especifico para adicionar reglas a los perfiles ya creados
    	en el WLC cisco_wlc.
	
Ultima revision 05-09-2019 11:40 Santa Cruz de la Sierra - Bolivia
"""
##########################################################
# Librerias
from netmiko import ConnectHandler
import sys

##########################################################
# Variables
device = {
    "device_type": "cisco_wlc",
    "ip": "172.16.10.3",
    "username": "user",
    "password": "password",
}
permit = " permit"
deny = " deny"
direccionu = " 172.30.250.0 255.255.255.0"
direcciond = " 192.168.0.0 255.255.0.0"
direcciont = " 172.16.0.0 255.240.0.0"
direccionc = " 10.0.0.0 255.0.0.0"
print("\n---->NetAuto ha iniciado: \n")


def main():
    #####################################################
    ######extraer lineas del archivo de Accesso##########
    try:
        with open("perfiles") as f:
            archivo = f.read().splitlines()
    except:
        print("Fallo al abrir el Archivo")
        sys.exit()

        #####################################################
        ############Intentamos la conexion###################
    try:
        net_connect = ConnectHandler(**device)
    except:
        print("Fallo la Conexion")
        sys.exit()
    print("conexion Exitosa")
    #####################################################
    #######Recorremos los nombres de las listas##########
    ###############Y adicionamos las reglas##############
    for nombre in archivo:
        NumRegla = 2
        net_connect.send_command("config acl rule add " + nombre + " " + str(NumRegla))
        net_connect.send_command(
            "config acl rule action " + nombre + " " + str(NumRegla) + permit
        )
        net_connect.send_command(
            "config acl rule destination address "
            + nombre
            + " "
            + str(NumRegla)
            + direccionu
        )
        print("Regla Agregada: " + str(NumRegla))
        NumRegla += 1
        net_connect.send_command("config acl rule add " + nombre + " " + str(NumRegla))
        net_connect.send_command(
            "config acl rule action " + nombre + " " + str(NumRegla) + deny
        )
        net_connect.send_command(
            "config acl rule destination address "
            + nombre
            + " "
            + str(NumRegla)
            + direcciond
        )
        print("Regla Agregada: " + str(NumRegla))
        NumRegla += 1
        net_connect.send_command("config acl rule add " + nombre + " " + str(NumRegla))
        net_connect.send_command(
            "config acl rule action " + nombre + " " + str(NumRegla) + deny
        )
        net_connect.send_command(
            "config acl rule destination address "
            + nombre
            + " "
            + str(NumRegla)
            + direcciont
        )
        print("Regla Agregada: " + str(NumRegla))
        NumRegla += 1
        net_connect.send_command("config acl rule add " + nombre + " " + str(NumRegla))
        net_connect.send_command(
            "config acl rule action " + nombre + " " + str(NumRegla) + deny
        )
        net_connect.send_command(
            "config acl rule destination address "
            + nombre
            + " "
            + str(NumRegla)
            + direccionc
        )
        print("Regla Agregada: " + str(NumRegla))
        print("Terminado perfil: " + nombre)
    net_connect.close()


main()
