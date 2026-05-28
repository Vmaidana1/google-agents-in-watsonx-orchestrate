"""
A2A Server for Deal Desk CPQ Agent - PROPERLY INTEGRATED WITH GOOGLE ADK
Implements the A2A 0.3.0 protocol over JSON-RPC 2.0 for integration with watsonx Orchestrate.

This version uses the correct Google ADK Runner API to invoke the agent.
"""

import logging
import os
import sys
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types as genai_types

# Ensure the project root is on the path
sys.path.append(os.path.dirname(__file__))

# Import the Google ADK agent
from agent import root_agent

# ── Environment & logging ──────────────────────────────────────────────────────

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

app = Flask(__name__)

# ── Initialize Google ADK Runner ───────────────────────────────────────────────

# Create a session service (required by Runner)
session_service = InMemorySessionService()

# Create the runner with our agent
runner = Runner(
    app_name="deal_desk_cpq_app",
    agent=root_agent,
    session_service=session_service,
    auto_create_session=True
)

log.info("Google ADK Runner initialized with agent: %s", root_agent.name)

# ── Helpers ────────────────────────────────────────────────────────────────────

def extract_message_content(data: dict) -> str:
    """
    Extract plain text from an incoming A2A / JSON-RPC 2.0 request.
    """
    candidates = []

    # Layout 1: params.message  (watsonx Orchestrate / A2A standard)
    if isinstance(data.get("params"), dict):
        candidates.append(data["params"].get("message"))

    # Layout 2: top-level message  (direct curl / test clients)
    if "message" in data:
        candidates.append(data["message"])

    for msg in candidates:
        if msg is None:
            continue
        if isinstance(msg, str):
            return msg
        if isinstance(msg, dict):
            # parts array (A2A format)
            parts = msg.get("parts")
            if isinstance(parts, list) and parts:
                first = parts[0]
                if isinstance(first, dict) and "text" in first:
                    return first["text"]
            # plain content field (fallback)
            if "content" in msg:
                return msg["content"]

    return ""


def build_a2a_response(text: str, request_id) -> dict:
    """
    Wrap a plain-text reply in the A2A 0.3.0 / JSON-RPC 2.0 envelope.
    Message fields MUST be directly in 'result', NOT nested under a 'message' key.
    """
    return {
        "jsonrpc": "2.0",
        "result": {
            "role": "assistant",
            "parts": [{"kind": "text", "text": text}],
            "kind": "message",
        },
        "id": request_id,
    }


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/agent/chat", methods=["POST"])
def chat():
    """
    Primary A2A endpoint called by watsonx Orchestrate.

    Flow:
        1. Parse and validate the incoming JSON-RPC 2.0 request.
        2. Extract the plain-text message from the A2A parts array.
        3. Invoke the Google ADK agent via the Runner.
        4. Return the agent's response in A2A 0.3.0 format.
    """
    request_id = 1  # default; overridden once data is parsed

    try:
        data = request.get_json(silent=True)

        if data is None:
            log.warning("Request body is empty or not valid JSON")
            return jsonify({
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error: request body must be valid JSON"},
                "id": request_id,
            }), 400

        request_id = data.get("id", 1)
        log.debug("Received request id=%s: %s", request_id, data)

        # ── 1. Extract message ─────────────────────────────────────────────
        message_content = extract_message_content(data)
        log.info("Extracted message: %r", message_content)

        if not message_content.strip():
            reply = "I didn't receive any message content. Please send your quote request with the required parameters."
            return jsonify(build_a2a_response(reply, request_id)), 200

        # ── 2. Invoke the Google ADK agent via Runner ──────────────────────
        log.info("Sending message to ADK runner...")
        
        # Generate unique IDs for this conversation
        user_id = "watsonx_user"
        session_id = str(uuid.uuid4())
        
        # Create the message content in the format expected by Runner
        # Runner.run expects a types.Content object with parts
        message_parts = [genai_types.Part(text=message_content)]
        content = genai_types.Content(parts=message_parts, role="user")
        
        # Run the agent and collect events
        events = list(runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ))
        
        log.info("Agent returned %d events", len(events))
        
        # Extract the final response from events
        response_text = ""
        for event in events:
            log.debug("Event type: %s", type(event).__name__)
            # Look for the agent's response in the events
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
        
        if not response_text:
            # Fallback: try to extract from last event
            if events:
                last_event = events[-1]
                response_text = str(last_event)
        
        log.info("Agent final response: %r", response_text[:200] + "..." if len(response_text) > 200 else response_text)

        # ── 3. Format and return ───────────────────────────────────────────
        response = build_a2a_response(response_text, request_id)
        log.debug("Sending response: %s", response)
        return jsonify(response), 200

    except Exception as exc:
        log.exception("Unhandled error processing request id=%s", request_id)
        return jsonify({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": f"Internal error: {exc}"},
            "id": request_id,
        }), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check — useful for verifying the tunnel is live before configuring watsonx."""
    return jsonify({"status": "healthy", "agent": f"Deal Desk CPQ Agent (Google ADK - {root_agent.name})"}), 200


# ── Entrypoint ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    log.info("=" * 60)
    log.info("Starting Deal Desk A2A Server (WITH GOOGLE ADK AGENT)")
    log.info("Agent  : %s", root_agent.name)
    log.info("Model  : %s", root_agent.model)
    log.info("Port   : %d", port)
    log.info("Debug  : %s", debug)
    log.info("Endpoint: http://localhost:%d/agent/chat", port)
    log.info("Health  : http://localhost:%d/health", port)
    log.info("=" * 60)

    app.run(host="0.0.0.0", port=port, debug=debug)

# Made with Bob
