"""
Stateless Firewall
Autor: Carlos Fernando Tapia Vaca <fernando.tapiavaca@yandex.com>

	firewall.py
	Firewall Host-Based para un Servidor Linux distro Parrot.
	
Ultima revision 24-06-2017 11:30 Santa Cruz de la Sierra - Bolivia
"""

# importe de librerias y herramientas:
from netfilterqueue import NetfilterQueue
from scapy.all import *
import os

# BASE DE DATOS
policy = 0
dir = "INPUT"
ip = []
port = []
pro = []
contador = 0


def imprimir(kiki, accion):
    print (
        "Paquete Capturado----------------------------------------------------------------"
    )
    print ("IP Origen y Destino:")
    print kiki.src
    print kiki.dst
    print ("Puerto Origen y Destino: ")
    print kiki.sport
    print kiki.dport
    print ("Veredicto:")
    if accion == 0:
        print ("Packet Dropped")
    else:
        print ("Packet Shipped")


# FIREWALL
def firewall(pkt):
    q = 0  # control de flujo
    x = 0  # flag para saber si hiso match
    while q < contador and x == 0:
        sdip = IP(pkt.get_payload())
        if dir == "INPUT":  # me interesa sourceIP y Dport
            if sdip.src == ip[q] and sdip.dport == port[q]:
                # hiso MATCH
                x = 1
                if policy == 1:  # PERMIT
                    imprimir(sdip, 0)
                    pkt.drop()
                else:  # DENY
                    imprimir(sdip, 1)
                    pkt.accept()
        else:  # OUTPUT me interesa ip destino y por destino
            if sdip.dst == ip[q] and sdip.dport == port[q]:
                # match
                x = 1
                if policy == 1:  # PERMIT
                    imprimir(sdip, 0)
                    pkt.drop()
                else:  # DENY
                    imprimir(sdip, 1)
                    pkt.accept()
        q = q + 1
    if policy == 1 and x == 0:  # PERMIT implicito
        imprimir(sdip, 1)
        pkt.accept()
    if policy == 0 and x == 0:  # deny implicito
        imprimir(sdip, 0)
        pkt.drop()


# MAIN
# asocioamos nfilter a una variable y a la funcion firewall
nfqueue = NetfilterQueue()
nfqueue.bind(1, firewall)
# desplegamos MENU
x = 1
while x > 0:
    print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    print (":::::::::::::::::::::::F:I:R:E:W:A:L:L:::::::::::::::::::::")
    print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    print (":::::::::::::::::::::::::MENU:PRINCIPAL::::::::::::::::::::")
    print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    print ("1) Definir Politica........................................")
    print ("2) Agregar Regla (Debe vincular interface primero).........")
    print ("3) Mostrar Configuracion...................................")
    print ("4) Eliminar Regla..........................................")
    print ("5) Vincular Interface......................................")
    print ("6) Habilitar (Ctrl + C para deshabilitar)..................")
    print ("99) Salir y desvincular....................................")
    print (":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    x = input("Seleccione un numero: ")
    # OPCIONES
    if x == 1:  # POLITICA
        print ("Default Permit -> 1")
        print ("Default Deny			-> 0")
        y = input("Digite el numero: ")
        if y == 1 or y == 0:
            policy = y
        else:
            print ("digito incorrecto, seleccion 1 o 0")
    elif x == 2:  # AGREGAR REGLAS
        print ("ADICIONAR REGLA NUMERO: " + str(contador))
        ip.insert(contador, raw_input("Introducir IP (A.B.C.D): "))
        pro.insert(contador, raw_input("Introducir protocolo TCP o UDP: "))
        port.insert(contador, input("Introducir numero de puerto: "))
        contador = contador + 1
    elif x == 3:  # TABLA DE INFORMACION
        l = 0
        print ("*************TABLA DE INFORMACION*****************")
        print (dir)
        while l < contador:
            print (
                str(l)
                + ") IP: "
                + ip[l]
                + " Protocolo: "
                + pro[l]
                + " Puerto: "
                + str(port[l])
            )
            l = l + 1
        if policy == 1:
            print ("Politica: DEFAULT PERMIT")
        else:
            print ("Politica: DEFAULT DENY")
    elif x == 4:  # ELIMINAR REGLA
        numero = input("Digite el numero de relga: ")
        del ip[numero]
        del port[numero]
        del pro[numero]
        contador = contador - 1
    elif x == 5:  # VINCULAR INTERFACE se selecciona direccion e ipv4
        print ("Escriba la direccion del trafico INPUT o OUTPUT ")
        print ("En mayusculas y sin espacios")
        dir = raw_input("Escriba su opcion: ")
        if dir == "INPUT" or dir == "OUTPUT":
            os.system("ip addr show")
            print ("Formato: A.B.C.D/Mask")
            w = raw_input(
                "Introduzca la direccion IPv4 de la interface que le interesa: "
            )
            os.system("iptables -F")
            if dir == "INPUT":
                f = "iptables -I " + dir + " -d " + w + " -j NFQUEUE --queue-num 1"
            else:
                f = "iptables -I " + dir + " -s " + w + " -j NFQUEUE --queue-num 1"
            os.system(f)
        else:
            print ("InCoRrEcTo")
    elif x == 6:  # FIREWALL CORRIENDO
        try:
            nfqueue.run()
        except KeyboardInterrupt:
            print ("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            print ("%%%%%%%%%%%%%%%%%%%%%%INTERRUPCION%%%%%%%%%%%%%%%%%%%%%")
            print ("#######################################################")
    elif x == 99:  # DESVINCULAMOS
        nfqueue.unbind()
        os.system("iptables -F")
        os.system("iptables -F")
        exit()
    else:
        print ("Opcion InCoRrEcTa!!!")
