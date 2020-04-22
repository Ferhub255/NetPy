#!/usr/bin/python3
"""
Parsing text using Python re
"""
import re


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

if __name__ == "__main__":
    with open('facts/showIOS15','r') as file:
        output = file.read()
    print(parse_model_ios1215(output))