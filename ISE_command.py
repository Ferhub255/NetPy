#!/usr/bin/env python3
"""
Automatizacion de Configuraciones
Autor: Carlos Fernando Tapia Vaca <fernando.tapiavaca@yandex.com>

	ISE_command.py
	Este script esta diseñado para automatizar la configuraciones de comandos en los todos
	los switches de acceso del ############. Identifica que interfaces tienen Dot1x, luego
	identifica las vlanes asignadas a cada puerto e identifica si es de acceso o de voz
	luego genera el template para todas las interfaces del switch con jinja2.

	Requerimientos:
		-python 3
		-netmiko
		-jinja2
		-re (regex)
		-ntc-templates
		-git (https://gitforwindows.org/)(https://www.develves.net/blogs/asd/articles/using-git-with-powershell-on-windows-10/)
		-python -m pip install [package]

Ultima revision 31-03-2020 15:00 Santa Cruz de la Sierra - Bolivia
"""

#Librerias
from netmiko import ConnectHandler
from pprint import pprint
import re
import jinja2

#Variables
device = {
	'device_type':'cisco_ios',
	'ip':'',
	'username':"user",
	'password':"password",
	}
fallidos=""#direcciones ip de los SW fallidos

print("Script Iniciado...")
with open("direcciones","rt") as f:
    direcciones = f.readlines()
for dir in direcciones:
	interfaces=[]#se usa para agrupas el nombre de las interfaces con Dot1x
	var= {}#se usa para agrupar los datos e introducirlo en Variables
	Variables=[]#contiene las interfaces con sus vlans de un SW
	ios=""#version del switch
	i=0#contador
	#conexion
	try:
		device['ip']=dir
		net_connect = ConnectHandler(**device)
		dot1x=net_connect.send_command('show dot1x all', use_textfsm=True)
		vlans=net_connect.send_command('show interfaces switchport', use_textfsm=True)
		version=net_connect.send_command('show version', use_textfsm=True)
		print("Conexion Exitosa: " + dir)
	except Exception as err:
		print(err.args)
		print("Conexion Fallida")
		fallidos+=dir+" Conexion Fallida"
		continue

	#interfaces que tienen dot1x
	try:
		for interface in dot1x:
			interfaces.append(re.search(r"(..).+t(.*$)", interface['interface']).group(1)+re.search(r"(..).+t(.*$)", interface['interface']).group(2))
	except Exception as err:
		print(err.args)
		print("Fallo de interface dot1x")
		fallidos+=dir+" Fallo Interface Dot1x"
		continue

	#vlan asignadas a las interface
	for int in interfaces:
		while i<len(vlans):
			if vlans[i]['interface']==int:
				var['vlan']=vlans[i]['access_vlan']
				var['name']=int
				i+=1
				break
			i+=1
		Variables.append(var)
		var={}

	#asignamos la version
	ios=re.search(r"(^..)", version[0]['version']).group(1)
	#pprint(Variables)

	#se lee el template generico y se carga en una variable a jinja2
	template_file = 'template.j2'
	with open(template_file) as f:
	    template = f.read()
	t = jinja2.Template(template)

	#se crea en template para cada interface y se la envia al Switch
	command=""
	for int in Variables:
		command+=t.render(int)

	if ios=="12":
		command+="\n"+"tacacs-server timeout 5"+"\n"
	elif ios=="15":
		command+="\n"+"tacacs server ISE01BG"+"\n"+"timeout 5"+"\n"+"tacacs server ISE02BG"+"\n"+"timeout 5"+"\n"
	elif ios=="16":
		command+="\n"+"tacacs server ISE01BG"+"\n"+"timeout 5"+"\n"+"tacacs server ISE02BG"+"\n"+"timeout 5"+"\n"
	else:#si todo falla le metemos los 2
		command+="\n"+"tacacs-server timeout 5"+"\n"
		command+="\n"+"tacacs server ISE01BG"+"\n"+"timeout 5"+"\n"+"tacacs server ISE02BG"+"\n"+"timeout 5"+"\n"

	#print(command)
	#, cmd_verify=False
	#print(Variables)
	#print(ios)
	#print(command)
	command=command.splitlines()
	try:
		net_connect.send_config_set(command)
		net_connect.send_command("write")
		print("Comandos Ingresados")
		net_connect.disconnect()
		print("Desconectado Exitosamente")
	except Exception as err:
		print(err.args)
		print(" Conexion Fallida, Comandos")
		fallidos+=dir+" Conexion Fallida, Comandos"

file=open("Fallidos",'at')
file.write(fallidos)
file.close()
print("Script Finalizado.")
