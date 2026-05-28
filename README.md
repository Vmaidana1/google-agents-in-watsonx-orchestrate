# Google Agents in watsonx Orchestrate

A demonstration of cross-framework agent collaboration, integrating Google ADK agents with IBM watsonx Orchestrate using the A2A (Agent-to-Agent) 0.3.0 protocol.

## 🎯 Project Overview

This repository showcases a multi-agent AI system for **TeleConnect**, a telecommunications company, demonstrating:

- **Cross-platform agent integration** (Google ADK ↔ IBM watsonx Orchestrate)
- **Multi-agent orchestration** with specialized roles
- **Enterprise AI patterns** (RAG, tool calling, agent delegation)
- **Real-world business workflows** (CPQ, network serviceability, sales automation)

## 🏗️ Architecture

### TeleConnect Sales Agents (3-Agent System)

```
┌─────────────────────────────────────────────────────────────┐
│         TeleCorp Enterprise Sales Agent (Main)              │
│              (watsonx Orchestrate Native)                   │
└────────────────┬────────────────────────────┬───────────────┘
                 │                            │
        ┌────────▼────────┐          ┌───────▼────────────┐
        │   Network       │          │  Deal Desk & CPQ   │
        │ Serviceability  │          │      Agent         │
        │     Agent       │          │  (Google ADK via   │
        │  (watsonx)      │          │   A2A Protocol)    │
        └─────────────────┘          └────────────────────┘
```

**Workflow**: Address check → Get base costs → Lookup customer discount → Calculate final quote → Present proposal

## ✨ Key Features

### Sales System
- **Product Knowledge**: 5G FWA vs Fiber DIA comparison with battlecards
- **Network Serviceability**: Real-time infrastructure availability checks
- **Customer Intelligence**: Salesforce account lookup with MSA discounts
- **Automated Quoting**: CPQ calculations with business rule enforcement
- **Multi-Agent Coordination**: Seamless delegation between specialized agents

### Cross-Framework Integration
- **A2A Protocol 0.3.0**: JSON-RPC 2.0 message format
- **Google ADK Agent**: External agent integration
- **Flask Server**: A2A endpoint implementation
- **Cloudflare Tunnel**: Local development networking

## 📁 Project Structure

```
google-agents-in-watsonx-orchestrate/   ← repo root after cloning
├── google_agents/
│   └── deal_desk_agent/          # Google ADK CPQ agent
│       ├── A2A_server.py          # A2A protocol server
│       ├── agent.py               # Google ADK agent definition
│       ├── tools/                 # CPQ calculation tool
│       │   └── calculate_enterprise_quote.py
│       ├── requirements.txt
│       ├── TROUBLESHOOTING.md     # Debugging guide
│       └── .env.example           # Environment template
│
├── watsonx_orchestrate_agents/
│   ├── setupTeleConnect_Sales_Agents.sh  # Deployment script
│   └── TeleConnect_Sales_Agents/
│       ├── Agents/                # Agent YAML definitions
│       │   ├── telecorp_enterprise_sales_agent.yaml
│       │   ├── network_serviceability_agent.yaml
│       │   └── deal_desk_cpq_agent_google_adk.yaml
│       ├── Tools/                 # Python tools (simulated data)
│       │   ├── __init__.py
│       │   ├── get_salesforce_b2b_enterprise_account_lookup.py
│       │   └── get_connectbase_network_serviceability_lookup.py
│       ├── Knowledge/             # Sales battlecards & docs
│       │   ├── 5G_FWA_Sales_Battlecard.pdf
│       │   ├── Fiber_DIA_Sales_Battlecard.pdf
│       │   ├── Fiber_vs_5G_FWA_Comparison_Slide.pdf
│       │   └── sales_knowledge_base.yaml
│       └── Data/                  # Reference data (Salesforce, ConnectBase)
│           ├── salesforceb2bdata.json
│           └── connectbasedata.json
│
├── .gitignore
└── README.md
```

## 🛠️ Technology Stack

- **IBM watsonx Orchestrate**: Primary agent orchestration platform
- **Google ADK**: External agent framework
- **A2A Protocol 0.3.0**: Agent-to-Agent communication standard
- **Python**: Tool implementations and Flask server
- **Flask**: A2A server endpoint
- **Cloudflare Tunnel**: Local development networking

### Data Sources
- **Salesforce**: B2B enterprise accounts, customer profiles (simulated with hardcoded data)
- **ConnectBase**: Network infrastructure and serviceability (simulated with hardcoded data)
- **Knowledge Bases**: Sales battlecards (RAG)

**Note**: The Salesforce and ConnectBase tools use embedded hardcoded data for demonstration purposes. They do not make actual API calls to external services, making them suitable for testing and demo environments without requiring API credentials or network access.

## 📋 Prerequisites

- **Python 3.11+**: Required by the IBM watsonx Orchestrate ADK
- **IBM watsonx Orchestrate account**: SaaS or on-premises instance
- **Google API key**: For Google ADK (get from [Google AI Studio](https://aistudio.google.com/app/apikey))
- **Git**: For cloning the repository
- **Cloudflare Tunnel** (or alternative): For exposing local server to watsonx Orchestrate
  - Install: `brew install cloudflare/cloudflare/cloudflared` (macOS) or [download](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Vmaidana1/google-agents-in-watsonx-orchestrate.git
cd google-agents-in-watsonx-orchestrate
```

### 2. Set Up Google ADK Agent

```bash
cd google_agents/deal_desk_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 3. Start the A2A Server

```bash
# From google_agents/deal_desk_agent/
python A2A_server.py
```

The server will start on `http://localhost:5001`

### 4. Expose Server (for watsonx Orchestrate)

Since watsonx Orchestrate runs on IBM Cloud SaaS, your local server needs to be publicly accessible.

**Note**: This guide uses Cloudflare Tunnel by default in all examples. If you choose a different option, adapt the URLs accordingly throughout the setup process.

#### Option A: Cloudflare Tunnel ✅ Recommended for Development

```bash
# In a new terminal
cloudflared tunnel --url http://localhost:5001
```

Copy the generated URL (e.g., `https://xyz.trycloudflare.com`)

- **Pros**: Free, fast setup, no account required
- **Cons**: URL changes on each restart

#### Other Tunneling Options

| Option | Command | Pros | Cons |
|--------|---------|------|------|
| **ngrok** | `ngrok http 5001` | Stable URLs with paid plan | Free tier limited, requires account |
| **localtunnel** | `npm i -g localtunnel && lt --port 5001` | Free, open source | Less stable |

#### Option B: Deploy to Cloud ✅ Recommended for Production

Deploy your A2A server to a cloud platform for a stable, production-ready URL:

| Platform | Notes |
|----------|-------|
| IBM Cloud Code Engine | Best fit — serverless containers, native to the IBM ecosystem |
| Google Cloud Run | Containerized deployment, pairs well with Google ADK |
| AWS Lambda + API Gateway | Serverless function approach |
| Azure Container Apps | Container hosting |

> **Tip**: See [`google_agents/deal_desk_agent/`](google_agents/deal_desk_agent/) for the server code you'll be deploying. A `Dockerfile` is a natural next step if you're targeting any of these platforms.

### 5. Configure External Agent URL

**IMPORTANT**: Do this BEFORE running the setup script!

Edit `watsonx_orchestrate_agents/TeleConnect_Sales_Agents/Agents/deal_desk_cpq_agent_google_adk.yaml` and replace the placeholder with your actual tunnel URL:

```yaml
# Change this:
api_url: https://YOUR-TUNNEL-URL-HERE.trycloudflare.com/agent/chat

# To your actual URL from step 4 (Cloudflare example):
api_url: https://abc-xyz-123.trycloudflare.com/agent/chat

# Or if using ngrok:
api_url: https://abc123.ngrok.io/agent/chat
```

### 6. Deploy to watsonx Orchestrate

```bash
cd watsonx_orchestrate_agents

# Activate your watsonx Orchestrate environment
orchestrate env activate YOUR_ENVIRONMENT_NAME --apikey YOUR_API_KEY

# Run setup script — imports all agents, tools, and knowledge bases
bash setupTeleConnect_Sales_Agents.sh
```

The script will:
1. Import the two Python tools (Salesforce lookup and ConnectBase serviceability) with watsonx Orchestrate
2. Upload the knowledge base documents (sales battlecards)
3. Import the three agent YAML definitions
4. Wire the Deal Desk CPQ agent to the tunnel URL you set in Step 5

**Note**: The Python tools use simulated data and do not require external API credentials.

**Note**: The setup script will import the Deal Desk CPQ agent with the URL you configured in step 5.

## 📖 Documentation

- **[Setup Script](watsonx_orchestrate_agents/setupTeleConnect_Sales_Agents.sh)**: Automates the full deployment of agents, tools, and knowledge bases to watsonx Orchestrate. Run it from the `watsonx_orchestrate_agents/` directory after activating your environment.
- **[Agent YAML definitions](watsonx_orchestrate_agents/TeleConnect_Sales_Agents/Agents/)**: Declarative definitions for all three agents — edit these to customize agent behavior, descriptions, or collaborator URLs.
- **[A2A Server](google_agents/deal_desk_agent/A2A_server.py)**: Flask server implementing the A2A 0.3.0 protocol. The entry point for the Google ADK integration.
- **[Python Tools](watsonx_orchestrate_agents/TeleConnect_Sales_Agents/Tools/)**: Simulated implementations for Salesforce B2B account lookup and ConnectBase network serviceability checks. These tools use hardcoded data and do not require external API access.

## 🛠️ Tool Architecture

### Python Tools (watsonx Orchestrate Native)

The system includes two Python tools that run natively in watsonx Orchestrate:

1. **`get_salesforce_b2b_enterprise_account_lookup.py`**
   - Simulates Salesforce B2B API responses
   - Returns enterprise account details including MSA discounts, account tiers, and contract information
   - Contains hardcoded data for 5 sample enterprise accounts
   - No external API calls or credentials required

2. **`get_connectbase_network_serviceability_lookup.py`**
   - Simulates ConnectBase network infrastructure API responses
   - Returns network serviceability data including fiber availability, distance to fiber, and pricing
   - Contains hardcoded data for 5 sample locations
   - No external API calls or credentials required

**Why Simulated Data?**
- **Demo-Ready**: Works immediately without API credentials or network access
- **Consistent Results**: Predictable responses for testing and demonstrations
- **No Dependencies**: Eliminates external service dependencies and potential API failures
- **Easy Customization**: Modify the hardcoded data arrays to add new test scenarios

**Data Location**: The original JSON data files are preserved in [`watsonx_orchestrate_agents/TeleConnect_Sales_Agents/Data/`](watsonx_orchestrate_agents/TeleConnect_Sales_Agents/Data/) for reference.

### External Agent (Google ADK via A2A)

The **Deal Desk & CPQ Agent** runs as an external Google ADK agent and performs actual quote calculations using business logic:

- **`calculate_enterprise_quote.py`** (in google_agents/deal_desk_agent/tools/)
  - Applies MSA discounts from customer data
  - Calculates term-length kickers (additional discounts for longer contracts)
  - Computes Total Contract Value (TCV)
  - Applies promotional rules (e.g., NRC waiver for 36-month terms)

## 🔑 Key Learnings

### A2A 0.3.0 Protocol

- **Incoming messages**: Extract text from `params.message.parts[0].text`
- **Outgoing messages**: Fields go directly in `result` — **not** nested under a `message` key
- **`parts` array**: Use `kind: "text"` for all entries inside `parts`
- **Top-level `kind`**: The `kind: "message"` field belongs on the `result` object itself, not inside `parts`

### Response Format

```json
{
  "jsonrpc": "2.0",
  "result": {
    "role": "assistant",
    "kind": "message",
    "parts": [
      { "kind": "text", "text": "Your response here..." }
    ]
  },
  "id": 1
}
```

### Networking
- watsonx Orchestrate SaaS requires publicly accessible URLs
- Cloudflare Tunnel is effective for development
- For production, use stable URLs or proper cloud deployment

## 🧪 Testing

### Test the A2A Server

Use this `curl` command to validate the server is responding correctly before connecting it to watsonx Orchestrate. The `"id"` in your request must match the `"id"` in the response — this is a JSON-RPC 2.0 requirement.

```bash
curl -X POST http://localhost:5001/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "chat",
    "params": {
      "message": {
        "parts": [{
          "kind": "text",
          "text": "Calculate quote with base MRC $1000, base NRC $500, MSA discount 20%, 36-month term"
        }]
      }
    },
    "id": 1
  }'
```

### Test in watsonx Orchestrate

1. Open the TeleCorp Enterprise Sales Agent
2. Ask: "Help me prepare a quote for Acme Corporation at 123 Industrial Ave, 36-month term"
3. The agent should delegate to Network Serviceability, then to Deal Desk CPQ

## 💬 User Interaction Guide

This guide demonstrates how to interact with the TeleConnect Sales Agents system through a complete sales workflow. The example shows a realistic scenario: working on a deal for Global Logistics Corp with a tight 14-day deadline.

### Complete Sales Workflow Example

#### Step 1: Retrieve Customer Account Information

**What to ask:**
```
I'm working on a new deal for Global Logistics Corp. Can you pull up their account details and check their current discount tier?
```

**What the agent does:**
- Uses the Salesforce lookup tool to retrieve account information
- Returns a formatted table with complete account details

**Expected response:**
| Field | Value |
|-------|-------|
| **Company Name** | Global Logistics Corp |
| **Account ID** | ENT-8A000abc12 |
| **Account Tier** | Strategic VIP |
| **MSA Active** | ✓ Yes |
| **MSA Discount** | 20% |
| **Account Executive** | Sarah Jenkins |
| **Contract Expires** | December 31, 2028 |

**Summary provided:**
- Active MSA with 20% discount
- Strategic VIP account classification
- Account executive and contract details

---

#### Step 2: Check Network Serviceability

**What to ask:**
```
They are opening a new site at 123 Industrial Ave. Check the network serviceability for that address and tell me the delivery timelines for fiber versus 5G
```

**What the agent does:**
- Delegates to the **Network Serviceability Agent**
- Checks infrastructure availability at the specified address
- Returns comparison of available connectivity options

**Expected response:**

**Network Serviceability for 123 Industrial Ave**

| Connectivity Option | Availability | Delivery Timeline | Base MRC | Base NRC |
|---------------------|--------------|-------------------|----------|----------|
| **Fiber DIA** (Dedicated Internet Access) | ✅ Available | 30 days | $1,000/month | $500 (install) |
| **5G FWA** (Fixed Wireless Access) | ✅ Available | 2 days | $350/month | $0 |

**Key Takeaways:**
- Site is Near-Net (fiber conduit 450 ft away)
- Fiber requires 30-day build-out
- 5G FWA can be provisioned in just 2 days
- Both solutions are serviceable

---

#### Step 3: Handle Objections and Position Solutions

**What to ask:**
```
Here is the problem: The client has a hard deadline and needs the site online in 14 days. The fiber timeline won't work. How should we position this?
```

**What the agent does:**
- Analyzes the constraint (14-day deadline vs 30-day fiber build)
- Provides strategic sales guidance from knowledge base
- Offers positioning framework for 5G FWA as a solution

**Expected response:**

**How to Position 5G FWA for the 14-Day Deadline**

| Reason | Talking Point | Value to Customer |
|--------|---------------|-------------------|
| **Speed to Market** | "We can have a fully-tested, production-ready connection up and running in 2 days – well under your 14-day deadline." | Guarantees the hard-deadline is met, avoiding project delays and penalties |
| **Zero Installation Overhead** | "Because the 5G Fixed-Wireless Access solution requires no trenching or fiber-pull, there is no installation fee and no site-work schedule to coordinate." | Saves time and upfront cost (NRC $0) |
| **Immediate Bandwidth** | "The baseline 5G FWA package delivers up to 350 Mbps symmetric bandwidth, which covers most warehouse, office, or IoT use-cases out of the box." | Meets typical data-intake needs for a new site |
| **Scalable & Future-Proof** | "If you later decide you need higher capacity, the same 5G antenna can be upgraded to a higher-tier plan, or we can transition to fiber once the build-out is complete – the two solutions are fully interoperable." | Gives a clear upgrade path without a lock-in |
| **Resilience & Redundancy** | "5G FWA can serve as a temporary backup for any future fiber connection, providing added network resiliency." | Improves business continuity |
| **Cost Transparency** | "The base MRC is $350/month with no NRC, so you know exactly what you'll pay from day 1." | Predictable budgeting, no hidden fees |
| **Enterprise-Grade SLA** | "Even though it's wireless, our 5G FWA service carries a 99.5% uptime SLA and 24/7 enterprise support, identical to our fiber offering." | Reassures quality will not be compromised |

**Suggested Pitch Flow:**
1. Acknowledge the deadline constraint
2. Present 5G FWA as the only viable path to meet the 14-day requirement
3. Walk through the benefits using the table above
4. Address wireless concerns by emphasizing enterprise-grade SLA
5. Offer a roadmap: "Start with 5G now, transition to fiber later when ready"

---

#### Step 4: Generate Pricing Quote

**What to ask:**
```
I love that play. Run the pricing for the 5G FWA solution, making sure to apply their corporate discount
```

**What the agent does:**
- Delegates to the **Deal Desk & CPQ Agent** (Google ADK via A2A)
- Applies MSA discount (20%) from Salesforce data
- Applies term-length kicker (additional 5% for 36-month term)
- Calculates Total Contract Value and savings

**Expected response:**

**Enterprise Quote Calculation Complete**

**Input Parameters**
| Parameter | Value |
|-----------|-------|
| Base MRC | $350.00 |
| Base NRC | $0.00 |
| MSA Discount | 20.0% |
| Term Length | 36 months |

**Calculated Quote**
| Metric | Amount |
|--------|--------|
| Monthly Recurring Charge | $262.50 |
| Non-Recurring Charge | $0.00 |
| Total Contract Value | $9,450.00 |
| Annualized Savings | $1,050.00 |

**Applied Promotions**
- 36-Month Term Kicker: Extra 5% Off MRC
- 36-Month Term Promotion: NRC Waived

---

#### Step 5: Secure Long-Term Revenue

**What to ask:**
```
Let's secure the long-term revenue. I want to pitch the dedicated fiber as their permanent solution once the 30-day construction is done. If they sign a 36-month contract, what financial incentives are automatically triggered by the Deal Desk?
```

**What the agent does:**
- Provides detailed explanation of CPQ business rules
- Shows how incentives stack for 36-month contracts
- Presents example with Fiber DIA pricing

**Expected response:**

**Financial Incentives for 36-Month Contracts**

| Incentive | How It Is Applied | What It Means for the Customer |
|-----------|-------------------|--------------------------------|
| **MSA Discount** | Customer's active MSA (20% discount) is applied to the base MRC | Immediate reduction on list price |
| **Term-Length Kicker** | An extra 5% off the MRC is added when the contract is 36 months or longer (stacked on top of MSA) | Guarantees a deeper price break for committing to a longer term |
| **NRC Waiver** | For 36-month (or longer) terms, the installation (NRC) fee is fully waived | Customer pays $0 for site-build costs, eliminating upfront capital expense |
| **Total Discount Display** | CPQ automatically shows the combined discount (e.g., 20% + 5% = 25% total) | Makes the value proposition transparent |
| **TCV Calculation** | CPQ multiplies the discounted MRC by the contract length and adds any applicable NRC | Provides a single, audit-ready figure for quota-tracking |
| **Annual Savings Indicator** | CPQ computes the annual dollar savings versus the list price | Helps highlight the ROI of the long-term commitment |

**Example (Fiber DIA) – What the Numbers Look Like**

| Item | Base Price | Discounts Applied | Final Price |
|------|------------|-------------------|-------------|
| **Monthly Recurring Charge (MRC)** | $1,000/mo | 20% MSA + 5% term kicker = 25% total | $750/mo |
| **Installation (NRC)** | $500 | Waived (36-mo term) | $0 |
| **Contract Length** | 36 months | – | – |
| **Total Contract Value (TCV)** | – | – | $27,000 ($750 × 36) |
| **Annual Savings** | – | – | $3,000 per year (vs. list price $12,000/yr) |

**Bottom Line:** Position 5G FWA as the only viable path to meet the 14-day go-live requirement, while still delivering enterprise-grade performance, zero upfront installation cost, and a clear upgrade path to fiber when the timeline allows.

---

### Understanding Agent Collaboration

The system uses **three specialized agents** working together:

1. **TeleCorp Enterprise Sales Agent** (Main Orchestrator)
   - Manages the conversation flow
   - Routes requests to specialized agents
   - Synthesizes information from multiple sources
   - Presents unified responses to the user

2. **Network Serviceability Agent** (watsonx Orchestrate)
   - Checks address serviceability
   - Provides infrastructure availability data
   - Returns base costs and delivery timelines

3. **Deal Desk & CPQ Agent** (Google ADK via A2A)
   - Performs financial calculations
   - Applies business rules and discounts
   - Calculates Total Contract Value
   - Generates audit-ready quotes

### Viewing Agent Reasoning

To see how the agents collaborated behind the scenes:

1. Click **"Show Reasoning"** dropdown on any agent response
2. View the step-by-step execution trace:
   - Tool calls made (e.g., `get_salesforce_b2b_enterprise_account_lookup`)
   - Agent delegations (e.g., `chat_with_collaborator_network_serviceability_agent`)
   - Data passed between agents
   - Raw API responses

This provides full transparency and auditability for enterprise compliance.

### Tips for Best Results

- **Be specific with addresses**: Include street number and name for serviceability checks
- **Mention customer names**: The agent will automatically look up account details
- **Specify contract terms**: Default is 36 months, but you can request different terms
- **Ask for comparisons**: Request "fiber vs 5G" to see side-by-side options
- **Request explanations**: Ask "how should I position this?" for sales guidance
- **Generate quotes**: Say "run pricing" or "calculate quote" to trigger CPQ calculations

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Port Conflicts
**Issue**: Server fails to start on port 5000
**Cause**: macOS AirPlay Receiver uses port 5000 by default
**Solution**: Use port 5001 or another available port in your `.env` file:
```bash
PORT=5001
```

#### Empty Message in watsonx Orchestrate
**Issue**: UI shows "LLM has responded with empty message"
**Cause**: Incorrect A2A response structure
**Solution**: Ensure message fields are directly in `result`, not nested under `message`:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "role": "assistant",
    "kind": "message",
    "parts": [{ "kind": "text", "text": "..." }]
  },
  "id": 1
}
```

#### Networking Issues
**Issue**: watsonx Orchestrate cannot reach local server
**Cause**: watsonx Orchestrate runs on IBM Cloud SaaS, not locally
**Solutions**:
- ✅ **Development**: Use Cloudflare Tunnel (`cloudflared tunnel --url http://localhost:5001`)
- ✅ **Production**: Deploy to cloud platform (IBM Cloud Code Engine, AWS Lambda, Google Cloud Run, etc.)
- ❌ **Don't use**: `localhost`, `127.0.0.1`, or local IP addresses

#### Message Extraction Errors
**Issue**: Server logs show empty extracted message
**Cause**: Incorrect parsing of watsonx Orchestrate's message format
**Solution**: Extract from `parts` array:
```python
if 'parts' in msg and isinstance(msg['parts'], list) and len(msg['parts']) > 0:
    first_part = msg['parts'][0]
    if isinstance(first_part, dict) and 'text' in first_part:
        message_content = first_part['text']
```

#### HTTP 500 Errors
**Issue**: Server returns 500 error during processing
**Causes**:
- Function parameter mismatches
- Missing required fields in response
- Unhandled exceptions in business logic

**Solution**: Check server logs for detailed error messages and stack traces. The server should always return a valid JSON-RPC 2.0 error object rather than letting exceptions bubble up:
```json
{
  "jsonrpc": "2.0",
  "error": { "code": -32603, "message": "Internal error: <details>" },
  "id": 1
}
```

### Debugging Tips

1. **Check Server Logs**: Always monitor the Flask server output for request/response details
2. **Test with curl**: Isolate issues by testing the A2A endpoint directly:
   ```bash
   curl -X POST http://localhost:5001/agent/chat \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"chat","params":{"message":{"parts":[{"kind":"text","text":"test"}]}},"id":1}'
   ```
3. **Verify Tunnel**: Ensure Cloudflare tunnel is running and URL is correctly configured in agent YAML
4. **Check Response Structure**: Validate that your response matches A2A 0.3.0 format exactly
5. **Monitor Network**: Use browser dev tools or Postman to inspect HTTP requests/responses

### A2A Protocol Requirements

**Critical Points**:
- Incoming messages: `params.message.parts[0].text`
- Outgoing messages: Fields directly in `result` (not nested under `message`)
- `result` must include: `role`, `kind`, and `parts` fields
- `parts` entries use `kind: "text"` — not `kind: "message"` (that belongs on `result`)
- Always return valid JSON-RPC 2.0 format with a matching `id`

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository and create a branch from `main`
2. Make your changes and test them locally (see the [Testing](#-testing) section)
3. Ensure the A2A server responds correctly before submitting
4. Open a Pull Request with a clear description of what changed and why

**Keep in mind**: contributors will need access to IBM watsonx Orchestrate and a Google API key to run the full system end-to-end. The A2A server and CPQ tools can be tested independently with `curl`.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2025 Vmaidana1

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Acknowledgments

- Built with **IBM watsonx Orchestrate**
- Powered by **Google ADK**
- A2A Protocol implementation inspired by Microsoft Copilot Studio examples

## 📞 Support

For questions or issues:
- Check the [watsonx Orchestrate documentation](https://developer.watson-orchestrate.ibm.com/)
- Open an issue in this repository

---

*Built on IBM watsonx Orchestrate* 🤖
