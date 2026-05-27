from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool
def calculate_enterprise_quote(base_mrc: float, base_nrc: float, discount_percentage: float, contract_term_months: int = 36) -> dict:
    """
    Calculates the final Configure, Price, Quote (CPQ) numbers for an enterprise telecom deal.
    
    Args:
        base_mrc (float): The base Monthly Recurring Charge (MRC) retrieved from ConnectBase.
        base_nrc (float): The base Non-Recurring Charge (NRC) retrieved from ConnectBase.
        discount_percentage (float): The customer's Master Service Agreement (MSA) discount percentage retrieved from Salesforce.
        contract_term_months (int, optional): The length of the contract in months (e.g., 12, 24, or 36). Defaults to 36.
        
    Returns:
        dict: The final calculated pricing, Total Contract Value (TCV), and applied business rules.
    """
    
    # Step 1: Ensure strict type casting
    try:
        base_mrc = float(base_mrc)
        base_nrc = float(base_nrc)
        discount_percentage = float(discount_percentage)
        contract_term_months = int(contract_term_months)
    except (ValueError, TypeError):
        return {"error": "Invalid input. Please provide numerical values for base prices, discount, and contract term."}

    # --- BUSINESS RULE 1: Term-Length Kicker ---
    # Add an extra 5% discount incentive for signing a 3-year (36 month) contract.
    term_kicker_discount = 5.0 if contract_term_months >= 36 else 0.0
    total_discount_percentage = discount_percentage + term_kicker_discount
    
    discount_multiplier = (100 - total_discount_percentage) / 100.0
    final_mrc = base_mrc * discount_multiplier

    # --- BUSINESS RULE 2: NRC Waiver ---
    # Waive the installation/construction fees completely for 36-month commitments.
    if contract_term_months >= 36:
        final_nrc = 0.0
        nrc_waived = True
    else:
        final_nrc = base_nrc * discount_multiplier
        nrc_waived = False
        
    # --- BUSINESS RULE 3: Total Contract Value (TCV) ---
    # Calculate the total value of the deal over its lifespan (crucial for sales quotas).
    tcv = (final_mrc * contract_term_months) + final_nrc
    
    # Calculate savings metrics
    monthly_savings = base_mrc - final_mrc
    annual_savings = monthly_savings * 12
    
    # Step 5: Return the structured, legally sound pricing data
    return {
        "contract_term_months": contract_term_months,
        "original_mrc": round(base_mrc, 2),
        "final_mrc": round(final_mrc, 2),
        "original_nrc": round(base_nrc, 2),
        "final_nrc": round(final_nrc, 2),
        "nrc_waived_due_to_term": nrc_waived,
        "total_contract_value_tcv": round(tcv, 2),
        "annual_savings": round(annual_savings, 2),
        "base_msa_discount": discount_percentage,
        "total_applied_discount": total_discount_percentage
    }