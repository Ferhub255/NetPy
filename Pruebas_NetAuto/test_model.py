#!/usr/bin/env python3
# pytest -s test_model.py
from parse_model import (
    parse_model_ios,
    parse_model_iosxr,
    parse_rt_ios,
    parse_rt_iosxr,
    get_rt_parser,
    rt_diff,
)


def test_parse_model_ios():
    """
    Unit test para Cisco IOS XE
    """
    # output modelo de prueba
    model_output = """
        cisco CSR1000V (VXE) processor (revision VXE) with 31l/32k memory.
        Processor board ID 9TH4AXIT7I
        1 Gigabit Ethernet interface
        32768K bytes of non-volatile configuration memory.
    """
    print("Positive Case" + "-" * 100)
    print(model_output)
    print("*" * 100)
    model_data = parse_model_ios(model_output)
    print(model_data)
    print("-" * 100)
    assert model_data == "CSR1000V"

    model_output = """
        cisco (VXE) processor (revision VXE) with 31l/32k memory.
        Processor board ID 9TH4AXIT7I
        1 Gigabit Ethernet interface
        32768K bytes of non-volatile configuration memory.
    """
    print("Negative Case" + "-" * 100)
    print(model_output)
    print("*" * 100)
    model_data = parse_model_ios(model_output)
    print(model_data)
    print("-" * 100)
    assert model_data is None


def test_parse_model_iosxr():
    """
        Unit test para Cisco XR
        """
    model_input_list = [
        """
        0/RP0-Fake-IDPROM - Cisco XRv9k Centralized...
          Info:
            PID                 : R-IOSXRV9000-RP-C
            Version Identifier  : v01
            UDI Description     : Cisco XRv9k Centralized ...
            CLEI Code           : N/A
        """,
        """
        0/RP0-Fake-IDPROM - Cisco XRv9k Centralized...
          Info:
            PID                 : 
            Version Identifier  : v01
            UDI Description     : Cisco XRv9k Centralized ...
            CLEI Code           : N/A
        """,
    ]
    model_answer_list = ["R-IOSXRV9000-RP-C", None]
    for model_output, answer in zip(model_input_list, model_answer_list):
        print("-" * 100)
        print(model_output)
        print("*" * 100)
        model_data = parse_model_iosxr(model_output)
        print(model_data)
        print("-" * 100)
        assert model_data == answer


def test_parse_rt_ios():
    vrf_output = """
            vrf definition CHEMICAL
            description CHEMICAL ENGINEERING FIRM
            rd 65000:2
            route-target export 65000:2
            route-target export 65000:5
            route-target export 65666:2
            route-target import 65000:2

            vrf definition CHEM_MGMT
            description CHEMICAL ENGINEERING MANAGER
            rd 65000:3

            route-target import 65000:4

    """
    print("Case" + "-" * 100)
    print(vrf_output)
    print("*" * 100)
    vrf_data = parse_rt_ios(vrf_output)
    print(vrf_data)
    print("-" * 100)
    _check_vrf_data(vrf_data)


def _check_vrf_data(vrf_data):
    assert len(vrf_data) == 2

    # vrf CHEMICAL
    assert len(vrf_data["CHEMICAL"]["route_import"]) == 1
    assert vrf_data["CHEMICAL"]["route_import"][0] == "65000:2"
    assert len(vrf_data["CHEMICAL"]["route_export"]) == 3
    assert vrf_data["CHEMICAL"]["route_export"][0] == "65000:2"
    assert vrf_data["CHEMICAL"]["route_export"][1] == "65000:5"
    assert vrf_data["CHEMICAL"]["route_export"][2] == "65666:2"

    # vrf CHEM_MGMT
    assert len(vrf_data["CHEM_MGMT"]["route_import"]) == 1
    assert vrf_data["CHEM_MGMT"]["route_import"][0] == "65000:4"
    assert len(vrf_data["CHEM_MGMT"]["route_export"]) == 0
    # assert vrf_data["CHEM_MGMT"]["route_export"][0] == "65000:3"
    # assert vrf_data["CHEM_MGMT"]["route_export"][1] == "65000:9"


def test_parse_rt_iosxr():
    vrf_output = """
        
        vrf CHEMICAL
        address-family ipv4 unicast
            import route-target
            65000:2
            !
            export route-target
            65000:2
            65000:5
            65666:2
        !

        vrf CHEM_MGMT
        address-family ipv4 unicast
            import route-target
            65000:4
        !


        !
    """
    print("Case" + "-" * 100)
    print(vrf_output)
    print("*" * 100)
    vrf_data = parse_rt_iosxr(vrf_output)
    print(vrf_data)
    print("-" * 100)
    _check_vrf_data(vrf_data)


def test_get_rt_parser():
    assert get_rt_parser("ios") == parse_rt_ios
    assert get_rt_parser("iosxr") == parse_rt_iosxr
    assert get_rt_parser("bogus") is None


def test_rt_diff():
    run_vrf_dict = {
        "VPN1": {"route_import": ["65000:1"], "route_export": []},
        "VPN2": {
            "route_import": ["65000:222", "65000:1"],
            "route_export": ["65000:2"],
        },
        "VPN3": {"route_import": ["65000:2", "65000:3"], "route_export": []},
    }

    int_vrf_list = [
        {
            "name": "VPN1",
            "description": "first VRF",
            "rd": "65000:1",
            "route_import": ["65000:1"],
            "route_export": ["65000:2"],
        },
        {
            "name": "VPN2",
            "description": "second VRF",
            "rd": "65000:2",
            "route_import": ["65000:1"],
            "route_export": ["65000:2"],
        },
        {
            "name": "VPN3",
            "description": "third VRF",
            "rd": "65000:3",
            "route_import": ["65000:2", "65000:3"],
            "route_export": [],
        },
        {
            "name": "VPN4",
            "description": "new VRF",
            "rd": "65000:4",
            "route_import": ["65000:4", "65000:3"],
            "route_export": ["65000:4"],
        },
    ]

    # verify run config and actual
    rt_updates = rt_diff(int_vrf_list, run_vrf_dict)

    # verify elements
    assert len(rt_updates) == 4

    # Check Results
    # VPN1
    assert rt_updates[0]["name"] == "VPN1"
    assert rt_updates[0]["description"] == "first VRF"
    assert rt_updates[0]["rd"] == "65000:1"
    assert len(rt_updates[0]["add_rte"]) == 1
    assert rt_updates[0]["add_rte"][0] == "65000:2"
    assert rt_updates[0]["del_rte"] == []
    assert rt_updates[0]["add_rti"] == []
    assert rt_updates[0]["del_rti"] == []

    # VPN2
    assert rt_updates[1]["name"] == "VPN2"
    assert rt_updates[1]["description"] == "second VRF"
    assert rt_updates[1]["rd"] == "65000:2"
    assert rt_updates[1]["del_rte"] == []
    assert rt_updates[1]["add_rte"] == []
    assert rt_updates[1]["add_rti"] == []
    assert rt_updates[1]["del_rti"][0] == "65000:222"
    assert len(rt_updates[1]["del_rti"]) == 1

    # VPN3
    assert rt_updates[2]["name"] == "VPN3"
    assert rt_updates[2]["description"] == "third VRF"
    assert rt_updates[2]["rd"] == "65000:3"
    assert rt_updates[2]["del_rte"] == []
    assert rt_updates[2]["add_rte"] == []
    assert rt_updates[2]["add_rti"] == []
    assert rt_updates[2]["del_rti"] == []
    assert rt_updates[2]["del_rti"] == []

    # VPN4
    assert rt_updates[3]["name"] == "VPN4"
    assert rt_updates[3]["description"] == "new VRF"
    assert rt_updates[3]["rd"] == "65000:4"
    assert rt_updates[3]["del_rte"] == []
    assert rt_updates[3]["add_rte"][0] == "65000:4"
    assert rt_updates[3]["add_rti"][0] == "65000:4"
    assert rt_updates[3]["add_rti"][1] == "65000:3"
    assert rt_updates[3]["del_rti"] == []


if __name__ == "__main__":
    get_rt_parser("ios")
    get_rt_parser("iosxr")
    get_rt_parser("bogus")
    test_rt_diff()
