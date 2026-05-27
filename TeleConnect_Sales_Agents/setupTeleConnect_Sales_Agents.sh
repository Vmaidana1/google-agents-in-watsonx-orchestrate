#!/bin/bash

# Setup script for TeleConnect Sales Agents Demo
# This script imports agents, tools, and knowledge bases for the TeleConnect Sales suite

# Exit immediately if a command exits with a non-zero status
set -e

# Function to handle errors
error_exit() {
    echo ""
    echo "=========================================="
    echo "❌ SETUP FAILED!"
    echo "=========================================="
    echo "Error: $1"
    echo ""
    echo "Please fix the error and run the script again."
    echo ""
    exit 1
}

# Activate your environment first (uncomment one of the following):
# For SaaS:
# orchestrate env activate YOUR_ENVIRONMENT_NAME --apikey YOUR_API_KEY_HERE
# For local:
# orchestrate env activate local

echo "=========================================="
echo "TeleConnect Sales Agents Setup"
echo "=========================================="
echo ""

# Track what was successfully deployed
TOOLS_IMPORTED=()
KB_IMPORTED=false
AGENTS_IMPORTED=()

# Step 1: Import Python Tools
echo "Step 1: Importing Python Tools..."

echo "  - Importing get_salesforce_b2b_enterprise_account_lookup..."
if orchestrate tools import -k python -f Tools/get_salesforce_b2b_enterprise_account_lookup.py; then
    TOOLS_IMPORTED+=("get_salesforce_b2b_enterprise_account_lookup")
    echo "    ✓ Success"
else
    error_exit "Failed to import get_salesforce_b2b_enterprise_account_lookup tool"
fi

echo "  - Importing get_connectbase_network_serviceability_lookup..."
if orchestrate tools import -k python -f Tools/get_connectbase_network_serviceability_lookup.py; then
    TOOLS_IMPORTED+=("get_connectbase_network_serviceability_lookup")
    echo "    ✓ Success"
else
    error_exit "Failed to import get_connectbase_network_serviceability_lookup tool"
fi

echo "  - Importing calculate_enterprise_quote..."
if orchestrate tools import -k python -f Tools/calculate_enterprise_quote.py; then
    TOOLS_IMPORTED+=("calculate_enterprise_quote")
    echo "    ✓ Success"
else
    error_exit "Failed to import calculate_enterprise_quote tool"
fi

echo "✓ All tools imported successfully"
echo ""

# Step 2: Import Knowledge Base
echo "Step 2: Importing Knowledge Base..."
if orchestrate knowledge-bases import -f Knowledge/sales_knowledge_base.yaml; then
    KB_IMPORTED=true
    echo "✓ Knowledge base imported successfully"
else
    error_exit "Failed to import sales_knowledge_base"
fi
echo ""

# Step 3: Import Agents (in dependency order)
echo "Step 3: Importing Agents..."

echo "  - Importing Network Serviceability Agent..."
if orchestrate agents import -f Agents/network_serviceability_agent.yaml; then
    AGENTS_IMPORTED+=("network_serviceability_agent")
    echo "    ✓ Success"
else
    error_exit "Failed to import network_serviceability_agent"
fi

echo "  - Importing Deal Desk & CPQ Agent..."
if orchestrate agents import -f Agents/deal_desk_cpq_agent_google_adk.yaml; then
    AGENTS_IMPORTED+=("deal_desk_cpq_agent")
    echo "    ✓ Success"
else
    error_exit "Failed to import deal_desk_cpq_agent"
fi

echo "  - Importing TeleCorp Enterprise Sales Agent (main orchestrator)..."
if orchestrate agents import -f Agents/telecorp_enterprise_sales_agent.yaml; then
    AGENTS_IMPORTED+=("TeleConnect_enterprise_sales_agent")
    echo "    ✓ Success"
else
    error_exit "Failed to import TeleConnect_enterprise_sales_agent"
fi

echo "✓ All agents imported successfully"
echo ""

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "What was deployed:"
echo "  ✓ ${#TOOLS_IMPORTED[@]} Python Tools:"
for tool in "${TOOLS_IMPORTED[@]}"; do
    echo "    - $tool"
done
echo ""
if [ "$KB_IMPORTED" = true ]; then
    echo "  ✓ 1 Knowledge Base:"
    echo "    - sales_knowledge_base (5G FWA & Fiber DIA battlecards)"
    echo ""
fi
echo "  ✓ ${#AGENTS_IMPORTED[@]} Agents:"
for agent in "${AGENTS_IMPORTED[@]}"; do
    echo "    - $agent"
done
echo ""
echo "Next Steps:"
echo "  1. Verify deployment:"
echo "     orchestrate agents list"
echo "     orchestrate tools list"
echo "     orchestrate knowledge-bases list"
echo ""
echo "  2. Test the main agent in Draft environment"
echo ""
echo "  3. Deploy to Live when ready:"
echo "     orchestrate agents deploy -k native -n TeleConnect_enterprise_sales_agent"
echo "     orchestrate agents deploy -k native -n network_serviceability_agent"
echo "     orchestrate agents deploy -k native -n deal_desk_cpq_agent"
echo ""

# Made with Bob