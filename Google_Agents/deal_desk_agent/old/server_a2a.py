"""
A2A 0.3.0 Protocol-compliant HTTP server wrapper for the Google ADK Deal Desk Agent.
This server implements JSON-RPC 2.0 over HTTP as required by watsonx Orchestrate.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Store conversation sessions
sessions: Dict[str, List[Dict[str, Any]]] = {}

# A2A Protocol Version
A2A_VERSION = "0.3.0"

def create_jsonrpc_response(result: Any, id: Any) -> Dict[str, Any]:
    """Create a JSON-RPC 2.0 response"""
    return {
        "jsonrpc": "2.0",
        "result": result,
        "id": id
    }

def create_jsonrpc_error(code: int, message: str, id: Any, data: Any = None) -> Dict[str, Any]:
    """Create a JSON-RPC 2.0 error response"""
    error = {
        "code": code,
        "message": message
    }
    if data:
        error["data"] = data
    
    return {
        "jsonrpc": "2.0",
        "error": error,
        "id": id
    }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "agent": "deal_desk_cpq_agent",
        "framework": "Google ADK",
        "a2a_version": A2A_VERSION
    }), 200


@app.route('/', methods=['POST'])
@app.route('/agent/chat', methods=['POST'])
def handle_jsonrpc():
    """
    A2A 0.3.0 JSON-RPC 2.0 endpoint
    Handles message/send requests according to A2A protocol
    """
    try:
        data = request.get_json()
        
        # Validate JSON-RPC 2.0 request
        if data.get('jsonrpc') != '2.0':
            return jsonify(create_jsonrpc_error(
                -32600, "Invalid Request: jsonrpc version must be 2.0", 
                data.get('id')
            )), 400
        
        method = data.get('method')
        params = data.get('params', {})
        request_id = data.get('id')
        
        # Handle message/send method (A2A 0.3.0)
        if method == 'message/send':
            return handle_message_send(params, request_id)
        
        # Handle unsupported methods
        return jsonify(create_jsonrpc_error(
            -32601, f"Method not found: {method}", request_id
        )), 404
        
    except json.JSONDecodeError:
        return jsonify(create_jsonrpc_error(
            -32700, "Parse error: Invalid JSON", None
        )), 400
    except Exception as e:
        return jsonify(create_jsonrpc_error(
            -32603, f"Internal error: {str(e)}", data.get('id') if 'data' in locals() else None
        )), 500


def handle_message_send(params: Dict[str, Any], request_id: Any) -> tuple:
    """
    Handle message/send method according to A2A 0.3.0 protocol
    """
    try:
        # Extract A2A protocol fields
        message_content = params.get('message', {}).get('content', '')
        task_id = params.get('task', {}).get('id', str(uuid.uuid4()))
        metadata = params.get('metadata', {})
        
        # Get or create session
        session_id = metadata.get('session_id', task_id)
        if session_id not in sessions:
            sessions[session_id] = []
        
        # Add user message to history
        sessions[session_id].append({
            "role": "user",
            "content": message_content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Process the message with CPQ tool
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from tools.calculate_enterprise_quote import calculate_enterprise_quote
            
            # Parse message to extract parameters
            import re
            mrc_match = re.search(r'MRC\s+\$?(\d+(?:\.\d+)?)', message_content, re.IGNORECASE)
            nrc_match = re.search(r'NRC\s+\$?(\d+(?:\.\d+)?)', message_content, re.IGNORECASE)
            discount_match = re.search(r'discount\s+(\d+(?:\.\d+)?)%?', message_content, re.IGNORECASE)
            term_match = re.search(r'(\d+)[-\s]month', message_content, re.IGNORECASE)
            
            if not all([mrc_match, nrc_match, discount_match, term_match]):
                response_text = """**CPQ CALCULATION ERROR**

Missing required parameters. Please provide:
- base_mrc: Base Monthly Recurring Charge (e.g., "base MRC $1000")
- base_nrc: Base Non-Recurring Charge (e.g., "base NRC $500")
- discount_percentage: MSA discount (e.g., "MSA discount 20%")
- term_months: Contract term (e.g., "36-month term")

Example: "Calculate quote with base MRC $1000, base NRC $500, MSA discount 20%, 36-month term"
"""
            else:
                # Extract values and call CPQ tool
                base_mrc = float(mrc_match.group(1))
                base_nrc = float(nrc_match.group(1))
                msa_discount_percent = float(discount_match.group(1))
                term_months = int(term_match.group(1))
                
                result = calculate_enterprise_quote(base_mrc, base_nrc, msa_discount_percent, term_months)
                
                # Format response
                response_text = f"""**CPQ CALCULATION COMPLETE**

**Contract Terms:**
- Contract Length: {term_months} months

**Monthly Recurring Charge (MRC):**
- Base MRC: ${base_mrc:,.2f}
- Final MRC: ${result['monthly_recurring_charge']:,.2f}
- Applied Discount: {msa_discount_percent + (5.0 if term_months >= 36 else 0.0)}%

**Non-Recurring Charge (NRC):**
- Base NRC: ${base_nrc:,.2f}
- Final NRC: ${result['non_recurring_charge']:,.2f}
- NRC Waived: {'Yes' if result['non_recurring_charge'] == 0 and base_nrc > 0 else 'No'}

**Contract Value:**
- Total Contract Value (TCV): ${result['total_contract_value']:,.2f}
- Annual Savings: ${result['annualized_savings']:,.2f}

**Applied Promotions:**
{chr(10).join('- ' + promo for promo in result['applied_promotions']) if result['applied_promotions'] else '- None'}
"""
            
            # Add response to session history
            sessions[session_id].append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Create A2A 0.3.0 compliant response
            a2a_response = {
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "task": {
                    "id": task_id,
                    "status": "completed"
                }
            }
            
            return jsonify(create_jsonrpc_response(a2a_response, request_id)), 200
            
        except Exception as agent_error:
            error_message = f"Agent execution error: {str(agent_error)}"
            
            a2a_error_response = {
                "message": {
                    "role": "assistant",
                    "content": error_message
                },
                "task": {
                    "id": task_id,
                    "status": "failed",
                    "error": str(agent_error)
                }
            }
            
            return jsonify(create_jsonrpc_response(a2a_error_response, request_id)), 200
    
    except Exception as e:
        return jsonify(create_jsonrpc_error(
            -32603, f"Internal error in message/send: {str(e)}", request_id
        )), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    
    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║  Deal Desk & CPQ Agent (Google ADK) - A2A 0.3.0 Server    ║
    ╠════════════════════════════════════════════════════════════╣
    ║  Framework: Google ADK                                     ║
    ║  Protocol: A2A 0.3.0 (JSON-RPC 2.0)                        ║
    ║  Port: {port}                                                   ║
    ╠════════════════════════════════════════════════════════════╣
    ║  Endpoints:                                                ║
    ║    GET  /health              - Health check                ║
    ║    POST /                    - JSON-RPC 2.0 endpoint       ║
    ║    POST /agent/chat          - JSON-RPC 2.0 endpoint       ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=False)

# Made with Bob