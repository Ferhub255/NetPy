#!/usr/bin/env python3
"""
Automatizacion de Troubleshooting de red
Autor: Carlos Fernando Tapia Vaca <fernando.tapiavaca@yandex.com>

	Tshoot_ISE.py
	Este script esta diseñado para automatizar tareas de Troubleshooting con Servidor Cisco ISE,
	Tiene la habilidad de abrir/cerrar puertos, Eliminar/agrega/reiniciar servicio 802.1x,
	consultar estado de la autenticacion entre otros.
	Esta orientado para uso de personal de mesa de ayuda de ###############.

	Requerimientos:
		-python 3
		-netmiko
		-openpyxl

Ultima revision 12-03-2020 17:40 Santa Cruz de la Sierra - Bolivia
"""

#Librerias
from netmiko import ConnectHandler
import netmiko
import datetime
import sys
from openpyxl import load_workbook
from getpass import getpass

#Variables
device = {
	'device_type':'cisco_ios',
	'ip':'',
	'username':"",
	'password':"",
	}
Switch = {
	'Nombre':'Null',
	'Ip':'0.0.0.0',
	'Puerto':'Null',
	}
Estado="DESCONECTADO"
State=False
path="DataBase.xlsx"
sheet="SWITCH"
Dicccionario={}
Lista=[]

print("\n--->Tshoot_ISE ha iniciado: \n")



def Imprimir_Menu():
	print("\n")
	print("=========================================")
	print("		Menu T-SHOOT				")
	print("=========================================")
	print("Operaciones:")
	print("\n")
	print("ESTADO: " + Estado)
	print(" 0) Conectar a Switch y Puerto")
	print(" 1) Mostrar Informacion de Conexion")
	print("-------> PUERTO <--------")
	print(" 2) Modo Abierto")
	print(" 3) Modo Cerrado")
	print(" 4) Apagar")
	print(" 5) Encender")
	print(" 6) Mostrar Configuracion del Puerto")
	print("-------> AUTENTICACION <-------")
	print(" 7) Mostrar Estado de Autenticacion")
	print(" 8) Deshabilitar Autenticacion")
	print(" 9) Habilitar Autenticacion")
	print("\n")
	print("10) Guardar Configuracion")
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

def Salir():
	if State==True:
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

#carga los parametros de nombre,ip e interface
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
	device['username']=input("User: ")
	device['password']=getpass()
	Mostrar_Parametros()
	print("Verifique Los Datos, si no es correcto vuelva a ingresar")
	device['ip']=str(Switch['Ip'])

#Lee las entradas del excel y las pasa al Dicccionario, la llave es el nombre del dispositivo y su valor a ip
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

#Retorna la ip de la lista donde esta alojada la base de datos, y elimina el /32 del final.
def Buscar_IP(nombre):
	try:
		ip=Dicccionario[nombre]
		return(ip[:-3])
	except Exception as err:
		print(err.args)
		return("0.0.0.0")


################################################################################
#Aqui inicia el script
try:
	Cargar_Base_de_Datos()
except Exception as err:
	print(err.args)
	print("Error al Cargar la Base de Datos, Verificar parametros.")


Imprimir_Menu()
while True:
	#Imprimir_Menu()
	Opcion=Seleccion_Opcion()
	if Opcion==0: #CONECTAR SWITCH PUERTO
		Insertar_Parametros()
		Imprimir_Menu()
		try:
			if State==True:
				net_connect.send_command("write")
			net_connect = ConnectHandler(**device)
			net_connect.enable()
			print("\n")
			print("Conexion Exitosa!"+"\n" +str(datetime.datetime.now()))
			Estado="CONECTADO A "+Switch['Nombre']
			print(Estado)
			net_connect.send_command("terminal length 0")
			State=True
		except Exception as err:
			print("\n")
			print("*****************************************************")
			print(" Conexion Fallida! ")
			print(err.args)
			Mostrar_Parametros()
			Estado="DESCONECTADO"
			State=False
			print("*****************************************************")

	elif Opcion==2: #ABIERTO
		Imprimir_Menu()
		try:
			config_commands=['interface '+ Switch['Puerto'],'auth open']
			net_connect.send_config_set(config_commands)
			print("Exito, MODO ABIERTO"+"\n" +str(datetime.datetime.now()))
		except Exception as err:
			print(err.args)
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==3: #CERRADO
		Imprimir_Menu()
		try:
			config_commands=['interface '+ Switch['Puerto'],'no auth open']
			net_connect.send_config_set(config_commands)
			print("Exito, MODO CERRADO"+"\n" +str(datetime.datetime.now()))
		except Exception as err:
			print(err.args)
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==4: #APAGAR
		Imprimir_Menu()
		try:
			config_commands=['interface '+ Switch['Puerto'],'shut']
			net_connect.send_config_set(config_commands)
			print("Exito, PUERTO APAGADO"+"\n" +str(datetime.datetime.now()))
		except Exception as err:
			print(err.args)
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==5: #ENCENDER
		Imprimir_Menu()
		try:
			config_commands=['interface '+ Switch['Puerto'],'no shut']
			net_connect.send_config_set(config_commands)
			print("Exito, PUERTO ENCENDIDO"+"\n" +str(datetime.datetime.now()))
		except Exception as err:
			print(err.args)
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==7: #MOSTRAR ESTADO
		Imprimir_Menu()
		try:
			String="--More--"
			output="\n----------------------------OUTPUT---------------------------\n"
			output+=net_connect.send_command_timing("show auth session int "+Switch['Puerto'])
			output+="\n"+net_connect.send_command_timing("show auth session int "+Switch['Puerto']+" detail")
			print(output+"\n" +str(datetime.datetime.now()))
		except Exception as err:
			print(err.args)
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==8: #ELIMINAR RADIUS
		Imprimir_Menu()
		try:
			config_commands=['interface '+ Switch['Puerto'],'no auth port auto']
			net_connect.send_config_set(config_commands)
			print("Exito, PUERTO SIN AUTENTICACION"+"\n" +str(datetime.datetime.now()))
		except Exception as err:
			print(err.args)
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==9: #AGREGAR RADIUS
		Imprimir_Menu()
		try:
			config_commands=['interface '+ Switch['Puerto'],'auth port auto']
			net_connect.send_config_set(config_commands)
			print("Exito, EXITO PUERTO CON AUTENTICACION"+"\n" +str(datetime.datetime.now()))
		except Exception as err:
			print(err.args)
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==1: #MOSTRAR
		Imprimir_Menu()
		Mostrar_Parametros()

	elif Opcion==6: #MOSTRAR INFORMACION DE PUERTO
		Imprimir_Menu()
		try:
			output="\n----------------------------OUTPUT---------------------------\n"
			output+=net_connect.send_command("show runn int "+Switch['Puerto'])
			print(output+"\n" +str(datetime.datetime.now()))
		except Exception as err:
			print(err.args)
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==10:#GUARDAR LA CONFIGURACION
		try:
			if State==True:
				net_connect.send_command("write")
				print("Se guardo correctamente "+"\n" +str(datetime.datetime.now()))
		except Exception as err:
			print(err.args)
			print("Ocurrio un error, verifique los parametros y la conexion.")

	elif Opcion==11:#SALIR DEL SCRIPT
		Salir()
