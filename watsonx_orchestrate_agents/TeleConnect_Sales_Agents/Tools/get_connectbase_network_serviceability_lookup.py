# get_connectbase_network_serviceability_lookup
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from typing import Optional

@tool()
def get_connectbase_network_serviceability_lookup(address: Optional[str] = None):
    """
    Get ConnectBase Network Serviceability Lookup items for physical addresses.
    This tool simulates API responses with hardcoded data.

    Args:
        address (str, optional): The physical address to search for (e.g., "123 Industrial Ave"). 
                                 If provided, filters the results to match exactly this address.

    Returns:
        list: Data structure containing the serviceability items. If address is provided, returns only the matching location.
    """
    # Simulated API response data
    items = [
        {
            "address": "123 Industrial Ave",
            "networkstatus": "Near-Net",
            "distancetofiberft": 450,
            "fiberavailable": True,
            "fiberdeliverydays": 30,
            "fibermrc": 1000,
            "fibernrc": 500,
            "fwaavailable": True,
            "fwadeliverydays": 2,
            "fwamrc": 350,
            "fwanrc": 0
        },
        {
            "address": "456 Market St",
            "networkstatus": "On-Net",
            "distancetofiberft": 0,
            "fiberavailable": True,
            "fiberdeliverydays": 5,
            "fibermrc": 800,
            "fibernrc": 0,
            "fwaavailable": True,
            "fwadeliverydays": 2,
            "fwamrc": 350,
            "fwanrc": 0
        },
        {
            "address": "789 Rural Road",
            "networkstatus": "Off-Net",
            "distancetofiberft": 15000,
            "fiberavailable": False,
            "fiberdeliverydays": 0,
            "fibermrc": 0,
            "fibernrc": 0,
            "fwaavailable": False,
            "fwadeliverydays": 0,
            "fwamrc": 0,
            "fwanrc": 0
        },
        {
            "address": "101 Startup Blvd",
            "networkstatus": "Off-Net",
            "distancetofiberft": 8500,
            "fiberavailable": False,
            "fiberdeliverydays": 0,
            "fibermrc": 0,
            "fibernrc": 0,
            "fwaavailable": True,
            "fwadeliverydays": 2,
            "fwamrc": 350,
            "fwanrc": 0
        },
        {
            "address": "222 Enterprise Way",
            "networkstatus": "Near-Net",
            "distancetofiberft": 2500,
            "fiberavailable": True,
            "fiberdeliverydays": 90,
            "fibermrc": 1200,
            "fibernrc": 15000,
            "fwaavailable": True,
            "fwadeliverydays": 3,
            "fwamrc": 400,
            "fwanrc": 0
        }
    ]

    # Filter the items if the agent passed an address
    if address:
        filtered_items = [
            item for item in items 
            if item.get("address", "").strip().lower() == address.strip().lower()
        ]
        return filtered_items

    # If no address was passed, return the full list
    return items

# Made with Bob
