# tools/calculate_enterprise_quote.py


def calculate_enterprise_quote(
    base_mrc: float,
    base_nrc: float,
    msa_discount_percent: float,
    term_months: int,
) -> dict:
    """
    Calculate the final enterprise quote by applying MSA and term-based discounts.

    Business rules applied (in order):
        1. MSA discount — applied to base MRC for all customers with an active MSA.
        2. 24-month term kicker — extra 3% off MRC; NRC reduced by 50%.
        3. 36-month term kicker — extra 5% off MRC; NRC fully waived.
           (Only one term tier applies; the higher tier takes precedence.)

    Args:
        base_mrc:             Base Monthly Recurring Charge in dollars (must be >= 0).
        base_nrc:             Base Non-Recurring Charge / installation fee in dollars (must be >= 0).
        msa_discount_percent: Customer's MSA discount as a percentage (0–100, e.g. 20.0 for 20%).
        term_months:          Contract term in months (must be > 0, e.g. 12, 24, 36).

    Returns:
        dict with keys:
            monthly_recurring_charge  — final MRC after all discounts
            non_recurring_charge      — final NRC after any waivers
            total_contract_value      — (final MRC × term_months) + final NRC
            annualized_savings        — yearly savings vs. the list-price 12-month cost
            total_discount_percent    — combined discount applied to MRC
            applied_promotions        — list of promotion labels that were triggered

    Raises:
        ValueError: if any input is outside its valid range.
    """

    # ── Input validation ───────────────────────────────────────────────────────
    if base_mrc < 0:
        raise ValueError(f"base_mrc must be >= 0, got {base_mrc}")
    if base_nrc < 0:
        raise ValueError(f"base_nrc must be >= 0, got {base_nrc}")
    if not (0.0 <= msa_discount_percent <= 100.0):
        raise ValueError(
            f"msa_discount_percent must be between 0 and 100, got {msa_discount_percent}"
        )
    if term_months <= 0:
        raise ValueError(f"term_months must be a positive integer, got {term_months}")

    # ── Term-based promotion rules ─────────────────────────────────────────────
    term_discount_kicker = 0.0
    nrc_reduction_percent = 0.0   # 0 = no reduction, 50 = half off, 100 = fully waived
    promotions = []

    if term_months >= 36:
        # 36-month tier: 5% MRC kicker + NRC fully waived
        term_discount_kicker = 5.0
        nrc_reduction_percent = 100.0
        promotions.append("36-Month Term Kicker: Extra 5% Off MRC")
        promotions.append("36-Month Term Promotion: NRC Waived")

    elif term_months >= 24:
        # 24-month tier: 3% MRC kicker + NRC reduced by 50%
        term_discount_kicker = 3.0
        nrc_reduction_percent = 50.0
        promotions.append("24-Month Term Kicker: Extra 3% Off MRC")
        promotions.append("24-Month Term Promotion: 50% Off NRC")

    # ── Calculations ───────────────────────────────────────────────────────────
    total_discount = msa_discount_percent + term_discount_kicker
    discount_multiplier = 1.0 - (total_discount / 100.0)

    final_mrc = base_mrc * discount_multiplier
    final_nrc = base_nrc * (1.0 - nrc_reduction_percent / 100.0)

    tcv = (final_mrc * term_months) + final_nrc

    # Annualized savings: how much the customer saves per year compared to
    # paying full list price on a 12-month baseline (MRC × 12 + full NRC).
    # This is intentionally a per-year figure, not the full TCV delta,
    # so it stays comparable regardless of the selected term length.
    list_price_annual = (base_mrc * 12) + base_nrc
    discounted_annual = (final_mrc * 12) + final_nrc
    annual_savings = list_price_annual - discounted_annual

    return {
        "monthly_recurring_charge": round(final_mrc, 2),
        "non_recurring_charge":     round(final_nrc, 2),
        "total_contract_value":     round(tcv, 2),
        "annualized_savings":       round(annual_savings, 2),
        "total_discount_percent":   round(total_discount, 2),
        "applied_promotions":       promotions,
    }