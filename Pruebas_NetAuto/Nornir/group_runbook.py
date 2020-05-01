#!/usr/bin/env python

import json
from nornir import InitNornir
from nornir.plugins.functions.text import print_result
from nornir.plugins.tasks.networking import napalm_get
from nornir.plugins.tasks.files import write_file

def write_facts(task):
    '''
    This is a grouped task that runs once per host. This iteration happens inside nonir automatically.
    Anytime task.run() is invoked, a new result is automatically added to MultiResult assembled
    on a per-host basis. if the grouped task returns anything, that object is stored in MultiResult[0]
    and all subsequent results are store thereafter.
    '''
    # gather facts using napalm to get model ID
    task1_result = task.run(task=napalm_get, getters=['get_facts'])
    # write to json file for use later.
    task.run(
        task = write_file,
        content = json.dumps(task1_result[0].result['get_facts'], indent=2),
        filename=f"{task.host.name}_facts.json",
    )


def main():
     # Inicializar
     nornir = InitNornir()

     result = nornir.run(task=write_facts)
     breakpoint()
     print_result(result)

if __name__ == "__main__":
    main()