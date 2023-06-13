#!/usr/bin/env python3

from .agent_based_api.v1 import (
    register,
    Result,
    Service,
    State,
    get_value_store,
)

from .utils.df import df_check_filesystem_single

def parse_quobyte_devices(string_table):
    """
    Parse Device Data to Dict
    """
    parsed = {}
    for line in string_table:
        if line[0] == 'device_serial_number':
            current_device = line[1]
        elif line[0] == 'device_label':
            if line[1]:
                current_device = line[1]
        else:
            parsed.setdefault(current_device, {})
            parsed[current_device][line[0]]=line[1]
    return parsed

def discover_quobyte_devices(section):
    """
    Discover one Service per Device
    """
    for device_id in section:
        yield Service(item=device_id)

def check_quobyte_devices(item, params, section):
    """
    Check single Device
    """
    try:
        device = section[item]
    except:
        yield Result(state=State.CRIT, summary="Device not found anymore")
        return

    # Check Device Mode
    state = State.OK
    if device['device_status'] in params['modes']['critical']:
        state = State.CRIT
    elif device['device_status'] in params['modes']['warning']:
        state  = State.WARN
    yield Result(state=state, summary=f"Device Mode: {device['device_status']}")

    # Check Usage
    yield from df_check_filesystem_single(
        get_value_store(),
        item,
        float(device['total_disk_space_bytes'])/1024,
        (float(device['total_disk_space_bytes']) - float(device["used_disk_space_bytes"]))/1024,
        0,
        None,
        None,
        {'levels' : params['usage_levels'],
         'trend_range': 1,
        },
    )

register.agent_section(
    name="quobyte_devices",
    parse_function=parse_quobyte_devices,
)

register.check_plugin(
    name="quobyte_devices",
    sections=["quobyte_devices"],
    service_name="Device %s",
    discovery_function=discover_quobyte_devices,
    check_function=check_quobyte_devices,
    check_default_parameters={
        'usage_levels': (90.0, 95.0),
        'modes' : {
            'warning' : ['DECOMMISSIONED', 'DRAIN', 'REGENERATE'],
            'critical' : ['OFFLINE'],
        }
    },
    check_ruleset_name="quobyte_devices",
)
