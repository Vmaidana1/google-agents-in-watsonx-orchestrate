"""
A2A-compliant HTTP server wrapper for the Google ADK Deal Desk Agent.
This server exposes the agent via HTTP endpoints compatible with watsonx Orchestrate's A2A protocol.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Import the Google ADK agent
from agent import root_agent

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Store conversation sessions
sessions: Dict[str, List[Dict[str, Any]]] = {}

# A2A Protocol Version
A2A_VERSION = "0.3.0"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "agent": "deal_desk_cpq_agent",
        "framework": "Google ADK",
        "a2a_version": A2A_VERSION
    }), 200


@app.route('/agent/info', methods=['GET'])
def agent_info():
    """
    A2A endpoint: Returns agent metadata and capabilities
    """
    return jsonify({
        "name": "deal_desk_cpq_agent",
        "display_name": "Deal Desk & CPQ Agent (Google ADK)",
        "description": "Strict financial deal desk analyst for deterministic pricing calculations using Google ADK",
        "version": "1.0.0",
        "framework": "Google ADK",
        "a2a_version": A2A_VERSION,
        "capabilities": {
            "streaming": False,
            "tools": [
                {
                    "name": "calculate_enterprise_quote",
                    "description": "Calculates final enterprise quote with MSA discounts and term-based promotions",
                    "parameters": {
                        "base_mrc": "Base Monthly Recurring Charge",
                        "base_nrc": "Base Non-Recurring Charge",
                        "msa_discount_percent": "MSA discount percentage",
                        "term_months": "Contract term in months"
                    }
                }
            ]
        }
    }), 200


@app.route('/agent/chat', methods=['POST'])
def agent_chat():
    """
    A2A endpoint: Main chat interface for agent interaction
    Accepts messages and returns agent responses
    """
    try:
        data = request.get_json()
        
        # Extract required fields
        message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Initialize session if new
        if session_id not in sessions:
            sessions[session_id] = []
        
        # Add user message to session history
        sessions[session_id].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Invoke the Google ADK agent
        try:
            # Import the tool directly for now
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from tools.calculate_enterprise_quote import calculate_enterprise_quote
            
            # Parse the message to extract parameters
            # Expected format: "Calculate quote with base MRC $1000, base NRC $500, MSA discount 20%, 36-month term"
            import re
            
            # Extract numeric values from the message
            mrc_match = re.search(r'MRC\s+\$?(\d+(?:\.\d+)?)', message, re.IGNORECASE)
            nrc_match = re.search(r'NRC\s+\$?(\d+(?:\.\d+)?)', message, re.IGNORECASE)
            discount_match = re.search(r'discount\s+(\d+(?:\.\d+)?)%?', message, re.IGNORECASE)
            term_match = re.search(r'(\d+)[-\s]month', message, re.IGNORECASE)
            
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
                # Extract values
                base_mrc = float(mrc_match.group(1))
                base_nrc = float(nrc_match.group(1))
                msa_discount_percent = float(discount_match.group(1))
                term_months = int(term_match.group(1))
                
                # Call the CPQ tool
                result = calculate_enterprise_quote(base_mrc, base_nrc, msa_discount_percent, term_months)
                
                # Format the response
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
            
            # Add agent response to session history
            sessions[session_id].append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Return A2A-compliant response
            return jsonify({
                "session_id": session_id,
                "message": response_text,
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "agent": "deal_desk_cpq_agent"
            }), 200
            
        except Exception as agent_error:
            error_message = f"Agent execution error: {str(agent_error)}"
            return jsonify({
                "session_id": session_id,
                "message": error_message,
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "agent": "deal_desk_cpq_agent"
            }), 500
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error",
            "timestamp": datetime.utcnow().isoformat()
        }), 400


@app.route('/agent/sessions/<session_id>', methods=['GET'])
def get_session(session_id: str):
    """
    A2A endpoint: Retrieve session history
    """
    if session_id not in sessions:
        return jsonify({
            "error": "Session not found",
            "session_id": session_id
        }), 404
    
    return jsonify({
        "session_id": session_id,
        "history": sessions[session_id],
        "message_count": len(sessions[session_id])
    }), 200


@app.route('/agent/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id: str):
    """
    A2A endpoint: Clear session history
    """
    if session_id in sessions:
        del sessions[session_id]
        return jsonify({
            "message": "Session deleted",
            "session_id": session_id
        }), 200
    
    return jsonify({
        "error": "Session not found",
        "session_id": session_id
    }), 404


if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.getenv('PORT', 5000))
    
    print(f"""
    ╔════════════════════════════════════════════════════════════╗
    ║  Deal Desk & CPQ Agent (Google ADK) - A2A Server          ║
    ╠════════════════════════════════════════════════════════════╣
    ║  Framework: Google ADK                                     ║
    ║  A2A Version: {A2A_VERSION}                                        ║
    ║  Port: {port}                                                   ║
    ╠════════════════════════════════════════════════════════════╣
    ║  Endpoints:                                                ║
    ║    GET  /health              - Health check                ║
    ║    GET  /agent/info          - Agent metadata              ║
    ║    POST /agent/chat          - Chat with agent             ║
    ║    GET  /agent/sessions/:id  - Get session history         ║
    ║    DELETE /agent/sessions/:id - Clear session              ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=False)

# Made with Bob
