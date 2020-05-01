#!/usr/bin/env python

from nornir import InitNornir # tareas, manejo de inventorio etc...
# funciones especificas
from nornir.plugins.tasks.networking import napalm_get
from nornir.plugins.functions.text import print_result


def main():
     # Inicializar
     nornir = InitNornir()
    # Docu https://nornir.readthedocs.io/en/stable/plugins/tasks/networking.html
     result = nornir.run(task=napalm_get, getters=["get_facts"])
     breakpoint()
     print_result(result)

if __name__ == "__main__":
    main()