# get_salesforce_b2b_enterprise_account_lookup
from ibm_watsonx_orchestrate.agent_builder.tools import tool
import requests

BASE_URL = "https://watsonx-chat.20pttk3h2ear.us-south.codeengine.appdomain.cloud/"
OWNER_USER_ID = "003924631"
OWNER_USER_EMAIL = "vinicius.maidana@ibm.com"
UNIQUE_ID_PREFIX = "ACC"

@tool
def get_salesforce_b2b_enterprise_account_lookup(account_name: str = None):
    """
    Get Salesforce B2B Enterprise Account Lookup items.

    Args:
        account_name (str, optional): The name of the enterprise account to search for (e.g., "Global Logistics Corp"). If provided, filters the results to match exactly this account.

    Returns:
        list: Data structure containing the tool items. If account_name is provided, returns only the matching account.
    """
    try:
        response = requests.get(
            f"{BASE_URL}api/playground/custom-tools/salesforce_b2b_enterprise_account_lookup",
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

        # Filter the items if the agent passed an account_name
        if account_name:
            filtered_items = [
                item for item in items 
                if item.get("enterpriseaccountname", "").strip().lower() == account_name.strip().lower()
            ]
            return filtered_items

        # If no account_name was passed, return the full list
        return items

    except requests.RequestException as e:
        return {"error": f"Network request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}