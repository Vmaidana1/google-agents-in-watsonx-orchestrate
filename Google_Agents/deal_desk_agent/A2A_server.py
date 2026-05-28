"""
A2A Server for Deal Desk CPQ Agent
Implements the A2A 0.3.0 protocol over JSON-RPC 2.0 for integration with watsonx Orchestrate.

Architecture note:
    This server calls the CPQ tool directly rather than routing through the Google ADK
    agent runner. The ADK Runner API (BaseNode.run()) does not accept a message argument
    in the version used here — see TROUBLESHOOTING.md Issue 2 for details.
    The CPQ tool (calculate_enterprise_quote) is deterministic and requires no LLM
    reasoning, so direct invocation is functionally equivalent for this use case.

A2A 0.3.0 response format (critical — do not restructure without testing):
    {
        "jsonrpc": "2.0",
        "result": {
            "role": "assistant",
            "parts": [{"kind": "text", "text": "..."}],
            "kind": "message"
        },
        "id": <request id>
    }
    Message fields MUST be directly in 'result', NOT nested under a 'message' key.
    See TROUBLESHOOTING.md Issue 7 for the full trial-and-error history.
"""

import logging
import os
import re
import sys

from dotenv import load_dotenv
from flask import Flask, jsonify, request

# Ensure the project root is on the path so 'tools' is importable
sys.path.append(os.path.dirname(__file__))
from tools.calculate_enterprise_quote import calculate_enterprise_quote

# ── Environment & logging ──────────────────────────────────────────────────────

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

app = Flask(__name__)

# ── Helpers ────────────────────────────────────────────────────────────────────

def extract_message_content(data: dict) -> str:
    """
    Extract plain text from an incoming A2A / JSON-RPC 2.0 request.

    watsonx Orchestrate wraps the message under params.message.parts[].text.
    A bare curl test may send it under message.parts[].text or message.content.
    All three layouts are handled here so local testing and production behave
    identically.

    Returns an empty string if no text content is found.
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


def parse_cpq_params(text: str) -> tuple[dict, list[str]]:
    """
    Extract CPQ parameters from a natural-language message using regex.

    Returns:
        params  — dict with keys base_mrc, base_nrc, msa_discount, term_months
                  (only populated keys are present)
        missing — list of human-readable labels for values that could not be parsed
    """
    patterns = {
        "base_mrc":    r"base[_ ]?mrc[:\s]+\$?(\d+(?:\.\d+)?)",
        "base_nrc":    r"base[_ ]?nrc[:\s]+\$?(\d+(?:\.\d+)?)",
        "msa_discount": r"msa[_ ]?discount[:\s]+(\d+(?:\.\d+)?)%?",
        "term_months": r"(\d+)[- ]?month",
    }
    labels = {
        "base_mrc":    "Base MRC (monthly recurring charge, in dollars)",
        "base_nrc":    "Base NRC (installation fee, in dollars)",
        "msa_discount": "MSA discount percentage (e.g. 20 for 20%)",
        "term_months": "Contract term (in months, e.g. 12, 24, 36)",
    }

    parsed = {}
    missing = []

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            parsed[key] = (
                int(match.group(1)) if key == "term_months"
                else float(match.group(1))
            )
        else:
            missing.append(labels[key])

    return parsed, missing


def build_a2a_response(text: str, request_id) -> dict:
    """
    Wrap a plain-text reply in the A2A 0.3.0 / JSON-RPC 2.0 envelope that
    watsonx Orchestrate expects.  Do not change the structure — see module
    docstring for the format requirements.
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


def format_quote_response(params: dict, result: dict) -> str:
    """Render the CPQ tool output as a markdown table response."""
    promotions = result.get("applied_promotions", [])
    if promotions:
        promo_rows = "\n".join(
            f"| {i + 1} | {promo} |" for i, promo in enumerate(promotions)
        )
        promo_table = f"| # | Promotion |\n|---|---|\n{promo_rows}"
    else:
        promo_table = "| # | Promotion |\n|---|---|\n| — | None |"

    return f"""\
## Enterprise Quote Calculation Complete

### Input Parameters
| Parameter    | Value |
|--------------|-------|
| Base MRC     | ${params['base_mrc']:,.2f} |
| Base NRC     | ${params['base_nrc']:,.2f} |
| MSA Discount | {params['msa_discount']}% |
| Term Length  | {params['term_months']} months |

### Calculated Quote
| Metric                   | Amount |
|--------------------------|--------|
| Monthly Recurring Charge | ${result['monthly_recurring_charge']:,.2f} |
| Non-Recurring Charge     | ${result['non_recurring_charge']:,.2f} |
| Total Contract Value     | ${result['total_contract_value']:,.2f} |
| Annualized Savings       | ${result['annualized_savings']:,.2f} |

### Applied Promotions
{promo_table}"""


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/agent/chat", methods=["POST"])
def chat():
    """
    Primary A2A endpoint called by watsonx Orchestrate.

    Flow:
        1. Parse and validate the incoming JSON-RPC 2.0 request.
        2. Extract the plain-text message from the A2A parts array.
        3. Parse CPQ parameters from the message via regex.
        4. If any parameter is missing, return a conversational reply asking
           for the specific missing value(s) — do NOT silently fall back to
           defaults, as that would produce a confident-looking but incorrect quote.
        5. Run the CPQ calculation and return a formatted markdown response.
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

        # ── 2. Parse CPQ parameters ────────────────────────────────────────
        params, missing = parse_cpq_params(message_content)
        log.info("Parsed params: %s | Missing: %s", params, missing)

        # ── 3. Ask for missing values rather than silently defaulting ──────
        if missing:
            items = "\n".join(f"  - {m}" for m in missing)
            reply = (
                f"To complete the quote I still need the following value(s):\n\n"
                f"{items}\n\n"
                f"Could you provide those?"
            )
            log.info("Returning clarification request for: %s", missing)
            return jsonify(build_a2a_response(reply, request_id)), 200

        # ── 4. Run CPQ calculation ─────────────────────────────────────────
        result = calculate_enterprise_quote(
            base_mrc=params["base_mrc"],
            base_nrc=params["base_nrc"],
            msa_discount_percent=params["msa_discount"],
            term_months=params["term_months"],
        )
        log.info("CPQ result: %s", result)

        # ── 5. Format and return ───────────────────────────────────────────
        response_text = format_quote_response(params, result)
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
    return jsonify({"status": "healthy", "agent": "Deal Desk CPQ Agent"}), 200


# ── Entrypoint ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    log.info("=" * 60)
    log.info("Starting Deal Desk A2A Server")
    log.info("Port    : %d", port)
    log.info("Debug   : %s", debug)
    log.info("Endpoint: http://localhost:%d/agent/chat", port)
    log.info("Health  : http://localhost:%d/health", port)
    log.info("=" * 60)

    app.run(host="0.0.0.0", port=port, debug=debug)
