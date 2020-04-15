#!/usr/bin/env python3
"""
Automatizacion de la red
Autor: Carlos Fernando Tapia Vaca <fernando.tapiavaca@yandex.com>

	ScriptWLC.py
	Este script de proposito especifico para cargar las ACL de Bg al WLC
    WLC cisco_wlc.
Ultima revision 02-09-2019 09:40 Santa Cruz de la Sierra - Bolivia
"""
##########################################################
#Librerias
from netmiko import ConnectHandler
import sys

##########################################################
#Variables
device = {
	'device_type':'cisco_wlc',
	'ip':'172.16.10.3',
	'username':'Dimatel',
	'password':'Bg2019',
}
dhcp=["68","67"]
udpport=["53","2701","2702","10123","3389"]
tcpport=["135","2701","2702","10123","3389"]
permit=" permit"
udp="17"
tcp="6"
icmp="1"
print("\n---->NetAuto ha iniciado: \n")


def main():
	NumRegla=1
	codigo=0
    #####################################################
    ######extraer lineas del archivo de Accesso##########
	try:
		with open("TemplateACL") as f:
			archivo= f.read().splitlines()
	except:
		print("Fallo al abrir el Archivo")
		sys.exit()

    #####################################################
    ############Intentamos la conexion###################
	try:
		net_connect=ConnectHandler(**device)
	except:
		print("Fallo la Conexion")
		#main()
		sys.exit()
	print("conexion Exitosa")

    #####################################################
    ##########Extraemos nombre de la ACL#################
	nombre=archivo[0].strip()
	del archivo[0]
	net_connect.send_command("config acl create " + nombre)

    #####################################################
    #############Recorrecmos el archivo##################
	for linea in archivo:
		linea=linea.strip()
		if linea == "host":
			codigo=1
			continue
		elif linea=="mask":
			codigo=2
			continue
		elif linea=="dhcp":
			net_connect.send_command("config acl rule add "+nombre+" "+ str(NumRegla))
			net_connect.send_command("config acl rule action "+nombre+" "+ str(NumRegla) +permit)
			net_connect.send_command("config acl rule protocol "+nombre+" "+str(NumRegla)+" "+udp)
			net_connect.send_command("config acl rule source port range "+nombre+" "+str(NumRegla)+" "+dhcp[0]+" "+dhcp[0])
			net_connect.send_command("config acl rule destination port range "+nombre+" "+str(NumRegla)+" "+dhcp[1]+" "+dhcp[1])
			print("Regla Agregada: "+str(NumRegla))
			NumRegla+=1
			codigo=0
			continue
		elif linea=="udp":
			for puerto in udpport:
				net_connect.send_command("config acl rule add "+nombre+" "+ str(NumRegla))
				net_connect.send_command("config acl rule action "+nombre+" "+ str(NumRegla) +permit)
				net_connect.send_command("config acl rule protocol "+nombre+" "+str(NumRegla)+" "+udp)
				net_connect.send_command("config acl rule destination port range "+nombre+" "+str(NumRegla)+" "+puerto+" "+puerto)
				print("Regla Agregada: "+str(NumRegla))
				NumRegla+=1
				codigo=0
			continue
		elif linea=="tcp":
			for puerto in tcpport:
				net_connect.send_command("config acl rule add "+nombre+" "+ str(NumRegla))
				net_connect.send_command("config acl rule action "+nombre+" "+str(NumRegla) +permit)
				net_connect.send_command("config acl rule protocol "+nombre+" "+str(NumRegla)+" "+tcp)
				net_connect.send_command("config acl rule destination port range "+nombre+" "+str(NumRegla)+" "+puerto+" "+puerto)
				print("Regla Agregada: "+str(NumRegla))
				NumRegla+=1
			codigo=0
			continue
		elif linea=="icmp":
			net_connect.send_command("config acl rule add "+nombre+" "+ str(NumRegla))
			net_connect.send_command("config acl rule action "+nombre+" "+ str(NumRegla) +permit)
			net_connect.send_command("config acl rule protocol "+nombre+" "+str(NumRegla)+" "+icmp)
			print("Regla Agregada: "+str(NumRegla))
			NumRegla+=1
			codigo=0
			continue
		elif linea=="ip":
			net_connect.send_command("config acl rule add "+nombre+" "+ str(NumRegla))
			net_connect.send_command("config acl rule action "+nombre+" "+ str(NumRegla) +permit)
			print("Regla Agregada: "+str(NumRegla))
			NumRegla+=1
			codigo=0
			continue
		else:
			if codigo==1:
				net_connect.send_command("config acl rule add "+nombre+" "+str(NumRegla))
				net_connect.send_command("config acl rule action "+nombre+" "+str(NumRegla) +permit)
				net_connect.send_command("config acl rule destination address "+nombre+" "+str(NumRegla)+" "+linea+" 255.255.255.255")
				print("Regla Agregada: "+str(NumRegla))
				NumRegla+=1
				continue
			elif codigo==2:
				linea=linea.split()
				ip=linea[0].strip()
				mask=linea[1].strip()
				net_connect.send_command("config acl rule add "+nombre+" "+str(NumRegla))
				net_connect.send_command("config acl rule action "+nombre+" "+str(NumRegla) +permit)
				net_connect.send_command("config acl rule destination address "+nombre+" "+str(NumRegla)+" "+ip+" "+mask)
				print("Regla Agregada: "+str(NumRegla))
				NumRegla+=1
				continue
			else:
				continue
	print("final: "+nombre)
	net_connect.close()
main()
