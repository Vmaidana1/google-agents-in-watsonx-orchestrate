# get_salesforce_b2b_enterprise_account_lookup
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from typing import Optional

@tool()
def get_salesforce_b2b_enterprise_account_lookup(account_name: Optional[str] = None):
    """
    Get Salesforce B2B Enterprise Account Lookup items.
    This tool simulates API responses with hardcoded data.

    Args:
        account_name (str, optional): The name of the enterprise account to search for (e.g., "Global Logistics Corp"). If provided, filters the results to match exactly this account.

    Returns:
        list: Data structure containing the tool items. If account_name is provided, returns only the matching account.
    """
    # Simulated API response data
    items = [
        {
            "enterpriseaccountname": "Global Logistics Corp",
            "b2baccountid": "ENT-8A000abc12",
            "accounttier": "Strategic VIP",
            "msaactive": True,
            "msadiscountpercentage": 20,
            "dedicatedaccountexec": "Sarah Jenkins",
            "contractexpiration": "2028-12-31"
        },
        {
            "enterpriseaccountname": "Acme Corporation",
            "b2baccountid": "ENT-8A000xyz98",
            "accounttier": "Mid-Market",
            "msaactive": True,
            "msadiscountpercentage": 5,
            "dedicatedaccountexec": "Marcus Vance",
            "contractexpiration": "2027-06-15"
        },
        {
            "enterpriseaccountname": "Initech",
            "b2baccountid": "ENT-8A000foo45",
            "accounttier": "Standard",
            "msaactive": False,
            "msadiscountpercentage": 0,
            "dedicatedaccountexec": "Unassigned",
            "contractexpiration": None
        },
        {
            "enterpriseaccountname": "Stark Industries",
            "b2baccountid": "ENT-8A000bar88",
            "accounttier": "Prospect",
            "msaactive": False,
            "msadiscountpercentage": 0,
            "dedicatedaccountexec": "Sarah Jenkins",
            "contractexpiration": None
        },
        {
            "enterpriseaccountname": "Wayne Enterprises",
            "b2baccountid": "ENT-8A000bat99",
            "accounttier": "Legacy VIP",
            "msaactive": True,
            "msadiscountpercentage": 15,
            "dedicatedaccountexec": "Marcus Vance",
            "contractexpiration": "2026-11-01"
        }
    ]

    # Filter the items if the agent passed an account_name
    if account_name:
        filtered_items = [
            item for item in items 
            if item.get("enterpriseaccountname", "").strip().lower() == account_name.strip().lower()
        ]
        return filtered_items

    # If no account_name was passed, return the full list
    return items

# Made with Bob