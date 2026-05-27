# Google Agents in watsonx Orchestrate

A demonstration of cross-framework agent collaboration, integrating Google ADK agents with IBM watsonx Orchestrate using the A2A (Agent-to-Agent) 0.3.0 protocol.

## 🎯 Project Overview

This repository showcases a production-ready multi-agent AI system for **TeleConnect**, a telecommunications company, demonstrating:

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

## 🚀 Key Features

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
TeleConnect_Agents/
├── Google_Agents/
│   └── deal_desk_agent/          # Google ADK CPQ agent
│       ├── A2A_server.py          # A2A protocol server
│       ├── agent.py               # Google ADK agent definition
│       ├── tools/                 # CPQ calculation tool
│       ├── requirements.txt
│       └── .env.example           # Environment template
│
└── TeleConnect_Sales_Agents/
    ├── Agents/                    # Agent YAML definitions
    │   ├── telecorp_enterprise_sales_agent.yaml
    │   ├── network_serviceability_agent.yaml
    │   └── deal_desk_cpq_agent_google_adk.yaml
    ├── Tools/                     # Python tools
    │   ├── get_salesforce_b2b_enterprise_account_lookup.py
    │   ├── get_connectbase_network_serviceability_lookup.py
    │   └── calculate_enterprise_quote.py
    ├── Knowledge/                 # Sales battlecards & docs
    ├── Data/                      # Mock data (Salesforce, ConnectBase)
    └── setupTeleConnect_Sales_Agents.sh
```

## 🛠️ Technology Stack

- **IBM watsonx Orchestrate**: Primary agent orchestration platform
- **Google ADK**: External agent framework
- **A2A Protocol 0.3.0**: Agent-to-Agent communication standard
- **Python**: Tool implementations and Flask server
- **Flask**: A2A server endpoint
- **Cloudflare Tunnel**: Local development networking

### Data Sources
- **Salesforce**: B2B enterprise accounts, customer profiles
- **ConnectBase**: Network infrastructure and serviceability
- **Knowledge Bases**: Sales battlecards (RAG)

## 📋 Prerequisites

- **Python 3.8+**: For running the A2A server and tools
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
cd Google_Agents/deal_desk_agent

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
# From Google_Agents/deal_desk_agent/
python A2A_server.py
```

The server will start on `http://localhost:5001`

### 4. Expose Server (for watsonx Orchestrate)

Since watsonx Orchestrate runs on IBM Cloud SaaS, your local server needs to be publicly accessible.

**Note**: This guide uses Cloudflare Tunnel by default in all examples. If you choose a different option, adapt the URLs accordingly throughout the setup process.

Choose one of these options:

#### Option A: Cloudflare Tunnel (Recommended for Development)

```bash
# In a new terminal
cloudflared tunnel --url http://localhost:5001
```

Copy the generated URL (e.g., `https://xyz.trycloudflare.com`)

**Pros**: Free, fast setup, no account required
**Cons**: URL changes on each restart

#### Option B: ngrok

```bash
# In a new terminal
ngrok http 5001
```

Copy the forwarding URL (e.g., `https://abc123.ngrok.io`)

**Pros**: Stable URLs with paid plan, custom domains available
**Cons**: Free tier has limitations, requires account

#### Option C: localtunnel

```bash
# Install localtunnel
npm install -g localtunnel

# In a new terminal
lt --port 5001
```

Copy the generated URL (e.g., `https://xyz.loca.lt`)

**Pros**: Free, open source
**Cons**: Less stable than alternatives

#### Option D: Deploy to Cloud (Recommended for Production)

Deploy your A2A server to a cloud platform:
- **IBM Cloud Code Engine**: Serverless container deployment
- **AWS Lambda + API Gateway**: Serverless function
- **Google Cloud Run**: Containerized deployment
- **Azure Container Apps**: Container hosting
- **Heroku**: Simple PaaS deployment

**Pros**: Production-ready, stable URLs, scalable
**Cons**: Requires cloud account and setup

### 5. Configure External Agent URL

**IMPORTANT**: Do this BEFORE running the setup script!

Edit `TeleConnect_Sales_Agents/Agents/deal_desk_cpq_agent_google_adk.yaml` and replace the placeholder with your actual tunnel URL:

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
cd TeleConnect_Sales_Agents

# Activate your watsonx Orchestrate environment
orchestrate env activate YOUR_ENVIRONMENT_NAME --apikey YOUR_API_KEY

# Run setup script (this will import all agents, tools, and knowledge bases)
bash setupTeleConnect_Sales_Agents.sh
```

**Note**: The setup script will import the Deal Desk CPQ agent with the URL you configured in step 5.

## 📖 Documentation

- **Setup Script**: Automated deployment for sales agents

## 🔑 Key Learnings

### A2A 0.3.0 Protocol
- **Incoming messages**: `params.message.parts[0].text`
- **Outgoing messages**: Fields directly in `result`, not nested under `message`
- **Structure**: Use `parts` array with `kind: "text"` and `kind: "message"`

### Response Format
```json
{
  "jsonrpc": "2.0",
  "result": {
    "role": "assistant",
    "parts": [{"kind": "text", "text": "..."}],
    "kind": "message"
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
    "parts": [{"kind": "text", "text": "..."}],
    "kind": "message"
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

**Solution**: Check server logs for detailed error messages and stack traces

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
- Outgoing messages: Fields directly in `result` (not nested)
- Response must include: `role`, `parts`, and `kind` fields
- Use `parts` array with `kind: "text"` for message content
- Always return valid JSON-RPC 2.0 format with matching `id`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is provided as-is for demonstration purposes.

## 🙏 Acknowledgments

- Built with **IBM watsonx Orchestrate**
- Powered by **Google ADK**
- A2A Protocol implementation inspired by Microsoft Copilot Studio examples

## 📞 Support

For questions or issues:
- Check watsonx Orchestrate documentation
- Open an issue in this repository

---

**Made with IBM Bob** 🤖