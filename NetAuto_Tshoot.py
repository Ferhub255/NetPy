#!/usr/bin/env python3
"""
Automatizacion de Troubleshooting red
Autor: Carlos Fernando Tapia Vaca <fernando.tapiavaca@yandex.com>

	Netauto_Tshoot.py
	Este script esta diseñado para automatizar tareas de Troubleshooting con Servidor Cisco ISE,
	Tiene la habilidad de abrir/cerrar puertos, Eliminar/agrega/reiniciar servicio 802.1x,
	consultar estado de la autenticacion entre otros.
	Esta orientado para uso de personal de mesa de ayuda del Banco Ganadero.

Ultima revision 02-03-2020 14:57 Santa Cruz de la Sierra - Bolivia
"""

#Librerias
from netmiko import ConnectHandler
import netmiko
import datetime
import sys
from openpyxl import load_workbook

#Variables
device = {
	'device_type':'cisco_ios',
	'ip':'',
	'username':"Dimatel",
	'password':"%13+@M&d-SW2960S-SC-2#",
	}
Switch = {
	'Nombre':'Null',
	'Ip':'0.0.0.0',
	'Puerto':'Null',
	}
Estado="DESCONECTADO"
path="DataBase.xlsx"
sheet="SWITCH"
Dicccionario={}
Lista=[]

print("\n---->Net_Tshoot ha iniciado: \n")



def Imprimir_Menu():
	print("\n")
	print("=========================================")
	print("		Menu T-SHOOT				")
	print("=========================================")
	print("Operaciones:")
	print("\n")
	print("ESTADO: " + Estado)
	print(" 0) Conectar")
	print("--------> PUERTO <--------")
	print(" 1) Modo Abierto")
	print(" 2) Modo Cerrado")
	print(" 3) Apagar")
	print(" 4) Encender")
	print("--------> RADIUS <--------")
	print(" 5) Mostrar Estado")
	print(" 6) Eliminar Radius")
	print(" 7) Agregar Radius")
	print(" 8) Reiniciar")
	print("------> PARAMETROS <------")
	print(" 9) Mostrar")
	print("10) Insertar")
	print("\n")
	print("11) Salir")
	print("\n")

def Seleccion_Opcion():
	print("-----------------------------------------------------")
	print("Ingrese el numero de la operacion que desea realizar.")
	print("-----------------------------------------------------")
	try:
		op=int(input("Operacion: "))
		if not((op>=0)and(op<=11)):
			raise ValueError
		return(op)
	except ValueError:
		print("Error: Wrong Input")
		return('E')

def Conectar():
	try:
		net_connect = ConnectHandler(**device)
		print(net_connect.find_prompt())
		print("\n")
		print("Conexion Exitosa!")
		Estado="CONECTADO A "+Switch['Nombre']
		print(Estado)
	except:
		print("\n")
		print("*****************************************************")
		print(" Conexion Fallida! ")
		Mostrar_Parametros()
		print(device)
		Estado="DESCONECTADO"
		print("*****************************************************")

def Salir():
	if Estado!="DESCONECTADO":
		net_connect.send_command("write")
		net_connect.disconnect()
		print("Desconectado")
	sys.exit()

def Mostrar_Parametros():
	print("\n")
	print("PARAMETROS")
	print("#####################################################")
	print("Nombre: "+Switch['Nombre'])
	print("    IP: "+Switch['Ip'])
	print("Puerto: "+Switch['Puerto'])
	print("#####################################################")

def Insertar_Parametros():
	print("\n")
	print("Los parametros deben ser exactos para realizar las acciones.")
	print("-----------------------------------------------------")
	Switch['Nombre']=input("Ingrese Nombre del Switch: ")
	ip=Buscar_IP(Switch['Nombre'])
	if ip != "0.0.0.0":
		Switch['Ip']=ip
	else:
		print("############################################################")
		print("NO SE ENCONTRO LA IP, VERIFIQUE NOMBRE O COLOQUE MANUALMENTE")
		print("############################################################")
		print("Ejemplo: 192.168.1.254")
		print("-----------------------------------------------------")
		Switch['Ip']=input("Ingresar IP: ")
	print("Ejemplo: Gigabitethernet0/2")
	print("-----------------------------------------------------")
	Switch['Puerto']= input("Ingresa Puerto: ")
	Mostrar_Parametros()
	print("Verifique Los Datos, si no es correcto vuelva a ingresar")
	device['ip']=str(Switch['Ip'])

def Cargar_Base_de_Datos():
	Workbook = load_workbook(path,read_only=True)
	Worksheet= Workbook[sheet]

	for row in Worksheet.rows:
		Lista=[]
		for cell in row:
			Lista.append(cell.value)
		Dicccionario[Lista[0]]=Lista[1]
	Lista=[]
	#print(Dicccionario)

def Desargar_Base_de_Datos():
	Dicccionario={}

def Buscar_IP(nombre):
	try:
		#eliminar /32
		ip=Dicccionario[nombre]
		return(ip[:-3])
	except:
		return("0.0.0.0")


################################################################################
try:
	Cargar_Base_de_Datos()
except:
	print("Error al Cargar la Base de Datos, Verificar parametros.")

while True:
	Imprimir_Menu()
	Opcion=Seleccion_Opcion()
	if Opcion==0: #CONECTAR
		try:
			net_connect = ConnectHandler(**device)
			#print(net_connect.find_prompt())
			net_connect.enable()
			print("\n")
			print("Conexion Exitosa!")
			Estado="CONECTADO A "+Switch['Nombre']
			print(Estado)
		except:
			print("\n")
			print("*****************************************************")
			print(" Conexion Fallida! ")
			Mostrar_Parametros()
			print(device)
			Estado="DESCONECTADO"
			print("*****************************************************")

	elif Opcion==1: #ABIERTO
		try:
			config_commands=['conf t','interface '+ Switch['Puerto'],'auth open','end']
			net_connect.send_config_set(config_commands)
			print("Exito")
		except:
			print("Ocurrio un error, verifique los parametros y la conexion.")
	elif Opcion==2: #CERRADO
		try:
			config_commands=['conf t','interface '+ Switch['Puerto'],'no auth open','end']
			net_connect.send_config_set(config_commands)
			print("Exito")
		except:
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==3: #APAGAR
		try:
			config_commands=['conf t','interface '+ Switch['Puerto'],'shut','end']
			net_connect.send_config_set(config_commands)
			print("Exito")
		except:
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==4: #ENCENDER
		try:
			config_commands=['conf t','interface '+ Switch['Puerto'],'no shut','end']
			net_connect.send_config_set(config_commands)
			print("Exito")
		except:
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==5: #MOSTRAR ESTADO
		try:
			output="\n----------------------------OUTPUT---------------------------\n"
			output+=net_connect.send_command("show auth session int "+Switch['Puerto'])
			output+="\n"+net_connect.send_command("show auth session int "+Switch['Puerto']+" detail")
			print(output)
			print("Exito")
		except:
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==6: #ELIMINAR RADIUS
		try:
			config_commands=['conf t','interface '+ Switch['Puerto'],'no auth port auto','end']
			net_connect.send_config_set(config_commands)
			print("Exito")
		except:
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==7: #AGREGAR RADIUS
		try:
			config_commands=['conf t','interface '+ Switch['Puerto'],'auth port auto','end']
			net_connect.send_config_set(config_commands)
			print("Exito")
		except:
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==8: #REINCIAR
		try:
			config_commands=['clear auth session int '+ Switch['Puerto']]
			net_connect.send_config_set(config_commands)
			print("Exito")
		except:
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==9: #MOSTRAR
		Mostrar_Parametros()
	elif Opcion==10: #INSERTAR
		Insertar_Parametros()
	elif Opcion==11: #SALIR
		Salir()
