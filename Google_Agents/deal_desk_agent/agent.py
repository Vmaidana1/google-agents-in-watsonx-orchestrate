import os
import sys
from dotenv import load_dotenv
from google.adk.agents import Agent

# 1. Force Python to look in this exact folder (deal_desk_agent) so it finds your 'tools' directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 2. Load API keys from the .env right next to this file
load_dotenv()

# 3. Import your mathematical tool using the newly renamed file
from tools.calculate_enterprise_quote import calculate_enterprise_quote

# 4. Define the standalone agent
root_agent = Agent(
    name="deal_desk_cpq_agent",
    model="gemini-2.5-flash",
    description="The strict deterministic calculator for financial metrics and enterprise quotes.",
    instruction="""
    You are the Deal Desk & CPQ (Configure, Price, Quote) Agent.
    Your ONLY job is to execute financial calculations based on strict business rules.
    
    Wait until you have the following four inputs:
    1. Base MRC (Monthly Recurring Charge)
    2. Base NRC (Non-Recurring Charge)
    3. MSA Discount Percentage
    4. Contract Term (in months)
    
    Once you have all four, you MUST use the 'calculate_enterprise_quote' tool to determine the final pricing.
    
    CRITICAL: Format your response using markdown tables for maximum readability:
    
    ## Enterprise Quote Calculation Complete
    
    ### Input Parameters
    | Parameter | Value |
    |-----------|-------|
    | Base MRC | $[base_mrc] |
    | Base NRC | $[base_nrc] |
    | MSA Discount | [msa_discount]% |
    | Term Length | [term_months] months |
    
    ### Calculated Quote
    | Metric | Amount |
    |--------|--------|
    | Monthly Recurring Charge | $[monthly_recurring_charge] |
    | Non-Recurring Charge | $[non_recurring_charge] |
    | Total Contract Value | $[total_contract_value] |
    | Annualized Savings | $[annualized_savings] |
    
    ### Applied Promotions
    | Applied Promotions |
    |-------------------|
    | [List each promotion in a table row] |
    
    Use the exact numbers from the tool's JSON output. Do NOT generate sales copy, do NOT estimate numbers, and do NOT make up discounts.
    """,
    tools=[calculate_enterprise_quote]
)
