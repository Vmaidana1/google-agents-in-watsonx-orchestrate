"""
Simple A2A Server for Google ADK Deal Desk Agent
Minimal implementation focusing on correct response format
"""

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import re

# Import the Google ADK tool
import sys
sys.path.append(os.path.dirname(__file__))
from tools.calculate_enterprise_quote import calculate_enterprise_quote

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/agent/chat', methods=['POST'])
def chat():
    """
    A2A chat endpoint - simplified version
    Returns the agent's response directly in the expected format
    """
    try:
        data = request.get_json()
        print(f"Received request: {data}")
        
        # Extract message content from various possible formats
        message_content = ""
        if 'params' in data:
            params = data['params']
            if 'message' in params:
                msg = params['message']
                # watsonx Orchestrate sends message in 'parts' array format
                if isinstance(msg, dict):
                    if 'parts' in msg and isinstance(msg['parts'], list) and len(msg['parts']) > 0:
                        # Extract text from first part
                        first_part = msg['parts'][0]
                        if isinstance(first_part, dict) and 'text' in first_part:
                            message_content = first_part['text']
                    elif 'content' in msg:
                        message_content = msg['content']
                elif isinstance(msg, str):
                    message_content = msg
        elif 'message' in data:
            msg = data['message']
            if isinstance(msg, dict):
                if 'parts' in msg and isinstance(msg['parts'], list) and len(msg['parts']) > 0:
                    first_part = msg['parts'][0]
                    if isinstance(first_part, dict) and 'text' in first_part:
                        message_content = first_part['text']
                elif 'content' in msg:
                    message_content = msg['content']
            elif isinstance(msg, str):
                message_content = msg
        
        print(f"Extracted message: {message_content}")
        
        # Parse parameters from the message using regex
        base_mrc_match = re.search(r'base[_ ]?mrc[:\s]+\$?(\d+(?:\.\d{2})?)', message_content, re.IGNORECASE)
        base_nrc_match = re.search(r'base[_ ]?nrc[:\s]+\$?(\d+(?:\.\d{2})?)', message_content, re.IGNORECASE)
        msa_discount_match = re.search(r'msa[_ ]?discount[:\s]+(\d+(?:\.\d+)?)%?', message_content, re.IGNORECASE)
        term_length_match = re.search(r'(\d+)[- ]?month', message_content, re.IGNORECASE)
        
        # Extract values or use defaults
        base_mrc = float(base_mrc_match.group(1)) if base_mrc_match else 1000.0
        base_nrc = float(base_nrc_match.group(1)) if base_nrc_match else 500.0
        msa_discount = float(msa_discount_match.group(1)) if msa_discount_match else 0.0
        term_months = int(term_length_match.group(1)) if term_length_match else 12
        
        print(f"Parsed params - MRC: {base_mrc}, NRC: {base_nrc}, Discount: {msa_discount}%, Term: {term_months} months")
        
        # Call the CPQ tool
        result = calculate_enterprise_quote(
            base_mrc=base_mrc,
            base_nrc=base_nrc,
            msa_discount_percent=msa_discount,
            term_months=term_months
        )
        
        print(f"CPQ result: {result}")
        
        # Format the response text with markdown tables for better readability
        promotions_list = result.get('applied_promotions', [])
        if promotions_list:
            promotions_rows = "\n".join([f"| {promo} |" for promo in promotions_list])
            promotions_table = f"""
| Applied Promotions |
|-------------------|
{promotions_rows}
"""
        else:
            promotions_table = """
| Applied Promotions |
|-------------------|
| None |
"""
        
        response_text = f"""## Enterprise Quote Calculation Complete

### Input Parameters
| Parameter | Value |
|-----------|-------|
| Base MRC | ${base_mrc:,.2f} |
| Base NRC | ${base_nrc:,.2f} |
| MSA Discount | {msa_discount}% |
| Term Length | {term_months} months |

### Calculated Quote
| Metric | Amount |
|--------|--------|
| Monthly Recurring Charge | ${result['monthly_recurring_charge']:,.2f} |
| Non-Recurring Charge | ${result['non_recurring_charge']:,.2f} |
| Total Contract Value | ${result['total_contract_value']:,.2f} |
| Annualized Savings | ${result['annualized_savings']:,.2f} |
{promotions_table}"""
        
        # Return response in the format watsonx Orchestrate expects
        # Based on A2A 0.3.0 protocol
        # Try returning just the message parts directly in result
        response = {
            "jsonrpc": "2.0",
            "result": {
                "role": "assistant",
                "parts": [
                    {
                        "kind": "text",
                        "text": response_text
                    }
                ],
                "kind": "message"
            },
            "id": data.get('id', 1)
        }
        
        print(f"Sending response: {response}")
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            },
            "id": data.get('id', 1) if 'data' in locals() and data else 1
        }
        return jsonify(error_response), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "agent": "Deal Desk CPQ Agent"}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    print(f"=" * 60)
    print(f"Starting Deal Desk A2A Server (Simple version)")
    print(f"Port: {port}")
    print(f"Endpoint: http://localhost:{port}/agent/chat")
    print(f"=" * 60)
    app.run(host='0.0.0.0', port=port, debug=True)

# Made with Bob
