#!/usr/bin/python3
"""
Parsing text using Python re
"""
import re
from pprint import pprint

def parse_model_ios(text):
    """
    Extrae el model ID del show version,
    cisco CSR1000V (VXE) processor (revision VXE) with 31k/32k memory
    """
    model_regex = re.compile(r"cisco\s+(?P<model>\S+)\s+\(\S+\)\s+processor\s+")

    # Se busca un match en el output
    model_match = model_regex.search(text)
    if model_match:
        return model_match.group("model")
    return None


def parse_model_iosxr(text):
    """
    Extrae el ID de un ios XR comando show diag 0/0,
    PID             : R-IOSXRV9000-RP-C
    """
    model_regex = re.compile(r"\s+PID\s+:[ \t]+(?P<model>\S+)")

    # se busca el match
    model_match = model_regex.search(text)
    if model_match:
        return model_match.group("model")
    return None


def parse_model_ios1215(text):
    """
    Extrae datos del show version de ios v12 y v15
    """
    model_regex = re.compile(
        r"Cisco.+Software\s\((?P<software>\S+)\).+Version\s(?P<model>\S+),?(\W+.+){20}\W.+mail.+\W+(?P<email>.+).(\W+.+){2}\.\W.+ID\s(?P<Processor_id>\S+)\W*(\W+.+){10}?register\s\S+\s(?P<register>\S+)\W*"
    )

    # se busca el match
    model_match = model_regex.search(text)
    if model_match:
        ios_version = {}
        ios_version['software'] = model_match.group("software")
        ios_version['version'] = model_match.group("model")
        ios_version['email'] = model_match.group("email")
        ios_version['processor_id'] = model_match.group("Processor_id")
        return ios_version
    return None

def parse_rt_ios(text):
    '''
    Extrae las variables de la configuracion y retorna un diccionario
    '''
    # lista de vfs
    vrf_list = ["vrf"+ section for section in text.strip().split("vrf") if section]
    return_dict = {}
    
    # Recorremos cada bloque de configuracion
    for vrf in vrf_list:
        # Se crea un diccionario de cada politica vrf
        name_regex = re.compile(r"vrf\s+definition\s+(?P<name>\S+)\W?")
        name_match = name_regex.search(vrf)
        sub_dict = {}
        vrf_dict = {name_match.group("name"):sub_dict}

        rti_regex = re.compile(r"route-target\s+import\s+(?P<route_i>\d+:\d+)")
        rti_match = rti_regex.findall(vrf)
        sub_dict.update({"route_import": rti_match})

        rte_regex = re.compile(r"route-target\s+export\s+(?P<route_e>\d+:\d+)")
        rte_match = rte_regex.findall(vrf)
        sub_dict.update({"route_export":rte_match})

        return_dict.update(vrf_dict)
    return return_dict
        
def parse_rt_iosxr(text):
    vrf_list = ["vrf"+section for section in text.strip().split("vrf") if section]
    return_dict = {}

    for vrf in vrf_list:
        #name
        vrf_regex = re.compile(r"^vrf\s+(?P<name>\S+)")
        vrf_match = vrf_regex.search(vrf)
        sub_dict = {}
        vrf_dict = {vrf_match.group("name"):sub_dict}

        #import routes
        rti_list = _get_iosxr_rt(r"import\s+route-target(.+?)!",vrf)
        sub_dict.update({"route_import":rti_list})

        #import routes
        rte_list = _get_iosxr_rt(r"export\s+route-target(.+?)!",vrf)
        sub_dict.update({"route_export":rte_list})

        return_dict.update(vrf_dict)
    return return_dict

def _get_iosxr_rt(regex_str, vrf_str):
    regex = re.compile(regex_str, re.DOTALL)
    rt_matches = regex.findall(vrf_str, re.DOTALL)
    if rt_matches:
        rt_list = [ruta.strip() for ruta in rt_matches[0].strip().split("\n")]
    else:
        rt_list = []
    return rt_list

if __name__ == "__main__":
    with open('facts/vrfxr_config','r') as file:
        output = file.read()
    pprint(parse_rt_iosxr(output))