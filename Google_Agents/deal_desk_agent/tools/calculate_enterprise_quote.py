# tools/cpq.py

def calculate_enterprise_quote(base_mrc: float, base_nrc: float, msa_discount_percent: float, term_months: int) -> dict:
    """
    Calculates the final enterprise quote applying standard discounts and term-based promotions.
    
    Args:
        base_mrc: The base Monthly Recurring Charge.
        base_nrc: The base Non-Recurring Charge (installation fee).
        msa_discount_percent: The customer's Master Service Agreement discount percentage (e.g., 10.0 for 10%).
        term_months: The contract term in months (e.g., 12, 24, 36).
        
    Returns:
        A dictionary containing the final financial metrics including TCV, finalized MRC/NRC, and applied promotions.
    """
    term_discount_kicker = 0.0
    waive_nrc = False
    promotions = []

    # Business Rule: 36-month term gets extra 5% off MRC and waived NRC
    if term_months >= 36:
        term_discount_kicker = 5.0
        waive_nrc = True
        promotions.append("36-Month Term Kicker: Extra 5% Off MRC")
        promotions.append("36-Month Term Promotion: NRC Waived")

    total_discount = msa_discount_percent + term_discount_kicker
    discount_multiplier = 1.0 - (total_discount / 100.0)

    final_mrc = base_mrc * discount_multiplier
    final_nrc = 0.0 if waive_nrc else base_nrc

    tcv = (final_mrc * term_months) + final_nrc
    
    # Calculate savings vs a 12-month base cost
    base_annual_cost = (base_mrc * 12) + base_nrc
    discounted_annual_cost = (final_mrc * 12) + final_nrc
    annual_savings = base_annual_cost - discounted_annual_cost

    return {
        "monthly_recurring_charge": round(final_mrc, 2),
        "non_recurring_charge": round(final_nrc, 2),
        "total_contract_value": round(tcv, 2),
        "annualized_savings": round(annual_savings, 2),
        "applied_promotions": promotions
    }