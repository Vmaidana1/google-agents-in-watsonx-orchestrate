# get_connectbase_network_serviceability_lookup
from ibm_watsonx_orchestrate.agent_builder.tools import tool
import requests
from datetime import datetime
BASE_URL = "https://watsonx-chat.20pttk3h2ear.us-south.codeengine.appdomain.cloud/"
OWNER_USER_ID = "003924631"
OWNER_USER_EMAIL = "vinicius.maidana@ibm.com"
UNIQUE_ID_PREFIX = "ADDR-"
@tool
def get_connectbase_network_serviceability_lookup(address: str = None):
    """
    Get ConnectBase Network Serviceability Lookup items for physical addresses.

    Args:
        address (str, optional): The physical address to search for (e.g., "123 Industrial Ave"). 
                                 If provided, filters the results to match exactly this address.

    Returns:
        list: Data structure containing the serviceability items. If address is provided, returns only the matching location.
    """
    try:
        response = requests.get(
            f"{BASE_URL}api/playground/custom-tools/connectbase_network_serviceability_lookup",
            params={"userId": OWNER_USER_ID, "email": OWNER_USER_EMAIL},
            timeout=30,
        )

        if response.status_code != 200:
            try:
                return response.json()
            except Exception:
                return {"error": f"HTTP {response.status_code} error occurred"}

        payload = response.json()
        items = payload.get("items", [])

        # Filter the items if the agent passed an address
        if address:
            filtered_items = [
                item for item in items 
                if item.get("address", "").strip().lower() == address.strip().lower()
            ]
            return filtered_items

        # If no address was passed, return the full list
        return items

    except requests.RequestException as e:
        return {"error": f"Network request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

# Made with Bob
