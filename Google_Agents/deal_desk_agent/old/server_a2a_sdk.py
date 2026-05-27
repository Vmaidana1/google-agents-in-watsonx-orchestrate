"""
A2A Server for Google ADK Deal Desk Agent using A2A SDK
This implementation uses the a2a.server SDK for proper agent execution
"""

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import re
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.helpers import (
    new_task_from_user_message,
    new_text_artifact,
    new_text_message,
)
from a2a.types.a2a_pb2 import (
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
)

# Import the Google ADK tool
import sys
sys.path.append(os.path.dirname(__file__))
from tools.calculate_enterprise_quote import calculate_enterprise_quote

# Load environment variables
load_dotenv()

app = Flask(__name__)

class DealDeskAgentExecutor(AgentExecutor):
    """Agent executor for the Deal Desk CPQ agent"""
    
    def __init__(self):
        super().__init__()
        self.agent_name = "Deal Desk CPQ Agent"
    
    async def execute(self, context: RequestContext, event_queue) -> None:
        """
        Execute the agent logic
        
        Args:
            context: Request context containing task and message
            event_queue: Queue for pushing status updates and results
        """
        # Get the task or create one from the message
        task = context.current_task or new_task_from_user_message(context.message)
        
        # Send initial status update
        await event_queue.enqueue_event(task)
        await event_queue.enqueue_event(
            TaskStatus(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(
                    state=TaskState.TASK_STATE_COMPLETED,
                )
            )
        )
        
        # Extract message content
        message_content = context.message.content if hasattr(context.message, 'content') else str(context.message)
        
        # Parse parameters from the message using regex
        base_mrc_match = re.search(r'base[_ ]?mrc[:\s]+\$?(\d+(?:\.\d{2})?)', message_content, re.IGNORECASE)
        base_nrc_match = re.search(r'base[_ ]?nrc[:\s]+\$?(\d+(?:\.\d{2})?)', message_content, re.IGNORECASE)
        msa_discount_match = re.search(r'msa[_ ]?discount[:\s]+(\d+(?:\.\d+)?)%?', message_content, re.IGNORECASE)
        term_length_match = re.search(r'(\d+)[- ]?month', message_content, re.IGNORECASE)
        
        # Extract values or use defaults
        base_mrc = float(base_mrc_match.group(1)) if base_mrc_match else 1000.0
        base_nrc = float(base_nrc_match.group(1)) if base_nrc_match else 500.0
        msa_discount = float(msa_discount_match.group(1)) if msa_discount_match else 0.0
        term_length_months = int(term_length_match.group(1)) if term_length_match else 12
        
        # Call the CPQ tool
        result = calculate_enterprise_quote(
            base_mrc=base_mrc,
            base_nrc=base_nrc,
            msa_discount_percent=msa_discount,
            term_length_months=term_length_months
        )
        
        # Format the response
        response_text = f"""**Enterprise Quote Calculation**

**Input Parameters:**
- Base MRC: ${base_mrc:,.2f}
- Base NRC: ${base_nrc:,.2f}
- MSA Discount: {msa_discount}%
- Term Length: {term_length_months} months

**Calculated Quote:**
- Final MRC: ${result['final_mrc']:,.2f}
- Final NRC: ${result['final_nrc']:,.2f}
- Total Contract Value: ${result['total_contract_value']:,.2f}

**Applied Discounts:**
- MSA Discount Applied: {result['msa_discount_applied']}%
- Term Kicker Applied: {result['term_kicker_applied']}%
- NRC Waiver: {'Yes' if result['nrc_waiver_applied'] else 'No'}

**Breakdown:**
{result['breakdown']}
"""
        
        # Send the result as an artifact
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                artifact=new_text_artifact(name='result', text=response_text)
            )
        )
        
        # Send completion status
        await event_queue.enqueue_event(
            TaskStatus(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(
                    state=TaskState.TASK_STATE_COMPLETED,
                )
            )
        )

# Create the agent executor instance
agent_executor = DealDeskAgentExecutor()

@app.route('/agent/chat', methods=['POST'])
async def chat():
    """
    A2A chat endpoint using JSON-RPC 2.0
    """
    try:
        data = request.get_json()
        
        # Validate JSON-RPC 2.0 format
        if not data or 'jsonrpc' not in data or data['jsonrpc'] != '2.0':
            return jsonify({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Invalid Request - must be JSON-RPC 2.0"
                },
                "id": data.get('id') if data else None
            }), 400
        
        # Check for message/send method
        if data.get('method') != 'message/send':
            return jsonify({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {data.get('method')}"
                },
                "id": data.get('id')
            }), 404
        
        # Execute the agent using the SDK
        params = data.get('params', {})
        context = RequestContext(
            message=params.get('message', {}),
            task=params.get('task'),
            metadata=params.get('metadata', {})
        )
        
        # Create an event queue for async communication
        from asyncio import Queue
        event_queue = Queue()
        
        # Execute the agent
        await agent_executor.execute(context, event_queue)
        
        # Collect all events from the queue
        events = []
        while not event_queue.empty():
            events.append(await event_queue.get())
        
        # Return JSON-RPC 2.0 response
        return jsonify({
            "jsonrpc": "2.0",
            "result": {
                "events": [str(event) for event in events]
            },
            "id": data.get('id')
        }), 200
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            },
            "id": data.get('id') if 'data' in locals() else None
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "agent": "Deal Desk CPQ Agent (A2A SDK)"}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    print(f"Starting Deal Desk A2A Server (SDK version) on port {port}...")
    print(f"Agent: {agent_executor.agent_name}")
    print(f"Endpoint: http://localhost:{port}/agent/chat")
    app.run(host='0.0.0.0', port=port, debug=True)

# Made with Bob
