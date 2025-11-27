"""
IoT Sensor Analysis Agent - AgentCore Runtime
Strands agent for analyzing IoT sensor data using AgentCore Runtime
Adapted from device-management-agent for IoT sensor analysis
"""
import os
import json
import logging
from dotenv import load_dotenv
import access_token

# Import Strands Agents SDK
from strands import Agent
from strands.models import BedrockModel
from strands.agent.conversation_manager import SlidingWindowConversationManager
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp import MCPClient
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Load environment variables
load_dotenv()

# Configure logging FIRST (before patch uses logger)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize the AgentCore Runtime App
app = BedrockAgentCoreApp()

# MONKEY PATCH: Fix empty body issue in framework
# The framework validates JSON before calling _handle_invocation
# We need to patch the FastAPI/Starlette request handling at a lower level
# Patch the app's underlying FastAPI app to handle empty bodies

try:
    # Get the underlying FastAPI app
    if hasattr(app, 'app'):
        fastapi_app = app.app
    elif hasattr(app, '_app'):
        fastapi_app = app._app
    else:
        fastapi_app = None
    
    if fastapi_app:
        from fastapi import Request
        from fastapi.responses import JSONResponse
        import starlette
        
        # Patch the request.json() method to handle empty bodies
        original_json = Request.json
        
        async def patched_json(self):
            """Patched json() that handles empty bodies"""
            try:
                body = await self.body()
                if not body or len(body) == 0:
                    logger.warning("⚠️ Empty request body in patched json(), returning empty dict")
                    return {}
                return await original_json(self)
            except Exception as e:
                logger.warning(f"⚠️ Error in patched json(): {e}, returning empty dict")
                return {}
        
        # Apply patch to Request class
        Request.json = patched_json
        logger.info("✅ Patched FastAPI Request.json() to handle empty bodies")
    else:
        logger.warning("⚠️ Could not find FastAPI app to patch")
        
    # Also patch _handle_invocation as backup
    original_handle = app._handle_invocation
    
    async def patched_handle_invocation(self, request):
        """Patched handler that handles empty request bodies"""
        import time
        from fastapi.responses import JSONResponse, Response, StreamingResponse
        import inspect
        
        self.logger.info("🔧 PATCHED HANDLER CALLED - Processing request")
        request_context = self._build_request_context(request)
        start_time = time.time()
        
        try:
            # Read body FIRST (can only be read once)
            try:
                body_bytes = await request.body()
            except Exception as e:
                self.logger.warning(f"⚠️ Error reading request body: {e}, using default payload")
                body_bytes = b""
            
            # Parse JSON from body bytes
            payload = None
            if not body_bytes or len(body_bytes) == 0:
                self.logger.warning("⚠️ Empty request body, using default payload")
                payload = {}
            else:
                try:
                    body_str = body_bytes.decode('utf-8')
                    payload = json.loads(body_str)
                    self.logger.info(f"✅ Successfully parsed JSON payload: {payload}")
                except json.JSONDecodeError as e:
                    error_msg = str(e)
                    self.logger.warning(f"⚠️ JSON decode error: {error_msg}, treating as plain text")
                    try:
                        body_str = body_bytes.decode('utf-8', errors='ignore')
                        payload = {"prompt": body_str}
                    except:
                        payload = {}
                except Exception as e:
                    self.logger.warning(f"⚠️ Error parsing body: {e}, using default payload")
                    payload = {}
            
            if payload is None:
                payload = {}
            
            self.logger.debug("Processing invocation request")
            
            if self.debug:
                task_response = self._handle_task_action(payload)
                if task_response:
                    duration = time.time() - start_time
                    self.logger.info("Debug action completed (%.3fs)", duration)
                    return task_response
            
            handler = self.handlers.get("main")
            if not handler:
                self.logger.error("No entrypoint defined")
                return JSONResponse({"error": "No entrypoint defined"}, status_code=500)
            
            takes_context = self._takes_context(handler)
            handler_name = handler.__name__ if hasattr(handler, "__name__") else "unknown"
            self.logger.debug("Invoking handler: {handler_name}")
            result = await self._invoke_handler(handler, request_context, takes_context, payload)
            
            duration = time.time() - start_time
            if inspect.isgenerator(result):
                self.logger.info("Returning streaming response (generator) (%.3fs)", duration)
                return StreamingResponse(self._sync_stream_with_error_handling(result), media_type="text/event-stream")
            elif inspect.isasyncgen(result):
                self.logger.info("Returning streaming response (async generator) (%.3fs)", duration)
                return StreamingResponse(self._stream_with_error_handling(result), media_type="text/event-stream")
            
            self.logger.info("Invocation completed successfully (%.3fs)", duration)
            safe_json_string = self._safe_serialize_to_json_string(result)
            return Response(safe_json_string, media_type="application/json")
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.exception("Invocation failed (%.3fs)", duration)
            return JSONResponse({"error": str(e)}, status_code=500)
    
    import types
    app._handle_invocation = types.MethodType(patched_handle_invocation, app)
    logger.info("✅ Patched _handle_invocation as backup")
    
except Exception as e:
    logger.error(f"Error applying patches: {e}", exc_info=True)

# Set logging level for specific libraries
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('mcp').setLevel(logging.INFO)
logging.getLogger('strands').setLevel(logging.INFO)

# MCP Server configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")
logger.info(f"MCP_SERVER_URL set to: {MCP_SERVER_URL}")

# Configure conversation management
conversation_manager = SlidingWindowConversationManager(
    window_size=25,  # Limit history size
)

# Function to check if MCP server is running
def check_mcp_server():
    try:
        if not MCP_SERVER_URL:
            logger.warning("MCP_SERVER_URL is not set. Skipping MCP server check.")
            return False

        jwt_token = os.getenv("BEARER_TOKEN")
        
        logger.info(f"Checking MCP server at URL: {MCP_SERVER_URL}")
        
        if not jwt_token:
            logger.info("No bearer token available, trying to get one...")
            try:
                jwt_token = access_token.get_gateway_access_token()
                logger.info(f"Cognito token obtained: {'Yes' if jwt_token else 'No'}")
            except Exception as e:
                logger.error(f"Error getting token: {str(e)}", exc_info=True)
        
        if jwt_token:
            headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"}
            payload = {
                "jsonrpc": "2.0",
                "id": "test",
                "method": "tools/list",
                "params": {}
            }
            
            try:
                import requests
                response = requests.post(f"{MCP_SERVER_URL}/mcp", headers=headers, json=payload, timeout=10)
                response.raise_for_status()
                logger.info(f"MCP server response status: {response.status_code}")
                has_tools = "tools" in response.text
                return has_tools
            except Exception as e:
                logger.error(f"Request exception: {str(e)}")
                return False
        else:
            logger.info("No bearer token available, trying health endpoint")
            try:
                import requests
                response = requests.get(f"{MCP_SERVER_URL}/health", timeout=5)
                response.raise_for_status()
                logger.info(f"Health endpoint response status: {response.status_code}")
                return response.status_code == 200
            except Exception as e:
                logger.error(f"Health endpoint request exception: {str(e)}")
                return False
    except Exception as e:
        logger.error(f"Error checking MCP server: {str(e)}", exc_info=True)
        return False

# Initialize basic agent without tools (fallback)
def initialize_basic_agent():
    """Initialize a basic agent without MCP tools for graceful degradation"""
    try:
        logger.info("Initializing basic agent without tools...")
        # Use Claude 3 Haiku first (broader access, no Marketplace subscription needed)
        model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-haiku-20240307-v1:0")
        try:
            model = BedrockModel(model_id=model_id)
            logger.info(f"Using model: {model_id}")
        except Exception as e:
            logger.warning(f"Failed to use {model_id}, trying alternative: {e}")
            # Fallback to Claude 3.5 Sonnet
            model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
            try:
                model = BedrockModel(model_id=model_id)
                logger.info(f"Using fallback model: {model_id}")
            except Exception as e2:
                logger.error(f"Failed to use fallback model: {e2}")
                raise
        
        agent = Agent(
            model=model,
            tools=[],  # No tools
            conversation_manager=conversation_manager,
            system_prompt="""
            You are an AI assistant for IoT Sensor Data Analysis. Help users analyze sensor data from IoT devices.
            
            Note: IoT tools are currently unavailable, but you can still provide general guidance about:
            - Sensor data analysis best practices
            - IoT device management
            - Data interpretation strategies
            - Troubleshooting common IoT issues
            
            Provide helpful, accurate information based on your knowledge of IoT systems and sensor data analysis.
            """
        )
        logger.info("Basic agent created successfully")
        return agent
    except Exception as e:
        logger.error(f"Error creating basic agent: {str(e)}", exc_info=True)
        return None

# Initialize Strands Agent with MCP tools
def initialize_agent():
    try:
        logger.info("Starting agent initialization...")
        
        jwt_token = os.getenv("BEARER_TOKEN")
        
        if not jwt_token:
            logger.info("No token in environment, trying to get one...")
            try:
                jwt_token = access_token.get_gateway_access_token()
                logger.info("Token retrieved successfully")
            except Exception as e:
                logger.error(f"Error getting token: {str(e)}", exc_info=True)
        
        gateway_endpoint = os.getenv("gateway_endpoint", MCP_SERVER_URL)
        logger.info(f"Using gateway endpoint: {gateway_endpoint}")
        
        headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else {}
        
        try:
            logger.info("Creating MCP client...")
            
            mcp_client = MCPClient(lambda: streamablehttp_client(
                url=f"{gateway_endpoint}/mcp",
                headers=headers
            ))
            logger.info("MCP Client setup complete")
            
            mcp_client.__enter__()
            
            logger.info("Listing tools from MCP server...")
            try:
                tools = mcp_client.list_tools_sync()
                logger.info(f"Loaded {len(tools)} tools from MCP server")
            except Exception as e:
                logger.error(f"Error listing tools: {str(e)}")
                logger.warning("Continuing with empty tools list")
                tools = []
            
            if tools and len(tools) > 0:
                tool_names = []
                for tool in tools:
                    if hasattr(tool, 'schema') and hasattr(tool.schema, 'name'):
                        tool_names.append(tool.schema.name)
                    elif hasattr(tool, 'tool_name'):
                        tool_names.append(tool.tool_name)
                    elif '_name' in vars(tool):
                        tool_names.append(vars(tool)['_name'])
                    else:
                        tool_names.append(f"Tool-{id(tool)}")
                
                logger.info(f"Available tools: {', '.join(tool_names)}")
            
        except Exception as e:
            logger.error(f"Error setting up MCP client: {str(e)}", exc_info=True)
            return None, None
        
            # Create an agent with these tools
        try:
            logger.info("Creating Strands Agent with tools...")
            # Use Claude 3 Haiku first (broader access, no Marketplace subscription needed)
            model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-haiku-20240307-v1:0")
            try:
                model = BedrockModel(model_id=model_id)
                logger.info(f"Using model: {model_id}")
            except Exception as e:
                logger.warning(f"Failed to use {model_id}, trying alternative: {e}")
                # Fallback to Claude 3.5 Sonnet
                model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
                try:
                    model = BedrockModel(model_id=model_id)
                    logger.info(f"Using fallback model: {model_id}")
                except Exception as e2:
                    logger.error(f"Failed to use fallback model: {e2}")
                    raise
            
            agent = Agent(
                model=model,
                tools=tools,
                conversation_manager=conversation_manager,
                system_prompt="""
                You are an AI assistant for IoT Sensor Data Analysis. Help users analyze sensor data from IoT devices.
                You have access to tools that can retrieve and analyze real sensor data from IoT devices.
                
                Available tools:
                - analyze_sensor_data: Analyze sensor readings (temperature, humidity, pressure, motion)
                - get_device_status: Get status and information about an IoT device
                - publish_command: Send commands to IoT devices
                - list_things: List all IoT devices in the system
                
                Use these tools to help users understand their sensor data, detect anomalies, and manage their IoT devices.
                Provide clear, actionable insights based on the sensor data.
                """
            )
            logger.info("Agent created successfully")
            
            return agent, mcp_client
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}", exc_info=True)
            return None, None
    except Exception as e:
        logger.error(f"Error initializing agent: {str(e)}", exc_info=True)
        return None, None

# Initialize the agent if MCP server is running
agent = None
mcp_client = None
if check_mcp_server():
    agent, mcp_client = initialize_agent()
    if agent:
        logger.info("Agent initialized successfully")
    else:
        logger.warning("Failed to initialize agent")
else:
    logger.warning("MCP server is not running. Agent initialization skipped.")

@app.entrypoint
async def process_request(payload=None):
    """
    Process requests from AgentCore Runtime with streaming support
    This is the entry point for the AgentCore Runtime
    
    The framework validates JSON before calling this function.
    If validation fails, this function won't be called.
    However, we handle all cases just in case.
    """
    global agent, mcp_client
    try:
        # If payload is None or empty, create default
        if payload is None:
            payload = {}
        logger.info(f"Entrypoint called with payload type: {type(payload)}, value: {payload}")
        
        # Handle None, empty, or invalid payloads
        if payload is None:
            logger.warning("Received None payload, using default message")
            user_message = "Hello! How can I help you with IoT sensor data analysis?"
        elif isinstance(payload, str):
            if not payload.strip():
                logger.warning("Received empty string payload, using default message")
                user_message = "Hello! How can I help you with IoT sensor data analysis?"
            else:
                # Try to parse as JSON first
                try:
                    payload_dict = json.loads(payload)
                    user_message = (
                        payload_dict.get("prompt") or 
                        payload_dict.get("message") or 
                        payload_dict.get("input") or 
                        payload_dict.get("text") or
                        payload  # Fallback to original string
                    )
                except json.JSONDecodeError:
                    # Not JSON, treat as plain text prompt
                    user_message = payload
        elif isinstance(payload, dict):
            # Extract user message from various possible formats
            # Handle different input formats from Agent Sandbox
            user_message = None
            
            # Try different keys in order of preference
            if payload.get("prompt"):
                user_message = payload.get("prompt")
            elif payload.get("input"):
                user_message = payload.get("input")
            elif payload.get("message"):
                user_message = payload.get("message")
            elif payload.get("text"):
                user_message = payload.get("text")
            elif payload.get("body"):
                user_message = payload.get("body")
            elif payload.get("params") and isinstance(payload.get("params"), dict):
                # Handle MCP/RPC format: {"jsonrpc": "2.0", "method": "tools/call", "params": {...}}
                params = payload.get("params")
                if params.get("arguments"):
                    # Extract from arguments
                    args = params.get("arguments")
                    if isinstance(args, dict):
                        # Try to find a text/input field
                        user_message = args.get("input") or args.get("text") or args.get("prompt") or str(args)
                    else:
                        user_message = str(args)
                else:
                    user_message = str(params)
            
            # If still no message, try to extract from dict
            if not user_message:
                # Check if it's an empty dict
                if not payload or payload == {}:
                    user_message = "Hello! How can I help you with IoT sensor data analysis?"
                else:
                    # Try to find any string value
                    for key, value in payload.items():
                        if isinstance(value, str) and value.strip():
                            user_message = value
                            break
                    # Last resort: convert dict to string
                    if not user_message:
                        user_message = str(payload) if str(payload) != "{}" else "Hello! How can I help you with IoT sensor data analysis?"
            
            # Final fallback
            if not user_message or not user_message.strip():
                user_message = "Hello! How can I help you with IoT sensor data analysis?"
        else:
            # Convert non-dict to string
            user_message = str(payload) if payload else "Hello! How can I help you with IoT sensor data analysis?"
        
        logger.info(f"Extracted user message: {user_message}")
        
        # Initialize agent if not already done (with or without tools)
        if not agent:
            logger.info("Agent not initialized, attempting to initialize...")
            # Try to initialize with MCP tools first
            if check_mcp_server():
                logger.info("MCP server is running, attempting to initialize agent with tools...")
                agent, mcp_client = initialize_agent()
                if agent:
                    logger.info("Agent initialized successfully with MCP tools")
                else:
                    logger.warning("Failed to initialize with MCP tools, initializing basic agent...")
                    agent = initialize_basic_agent()
            else:
                logger.warning("MCP server not available, initializing basic agent without tools...")
                agent = initialize_basic_agent()
            
            if not agent:
                error_msg = "Failed to initialize agent. Please check logs for details."
                logger.error(error_msg)
                yield {"error": error_msg}
                return
        
        logger.info("Processing message with Strands Agent (streaming)...")
        try:
            stream = agent.stream_async(user_message)
            async for event in stream:
                logger.debug(f"Streaming event: {event}")
                
                if "data" in event:
                    chunk = event["data"]
                    yield {
                        "type": "chunk",
                        "data": chunk
                    }
                elif "current_tool_use" in event:
                    tool_info = event["current_tool_use"]
                    yield {
                        "type": "tool_use",
                        "tool_name": tool_info.get("name", "Unknown tool"),
                        "tool_input": tool_info.get("input", {}),
                        "tool_id": tool_info.get("toolUseId", "")
                    }
                elif "reasoning" in event and event["reasoning"]:
                    yield {
                        "type": "reasoning",
                        "reasoning_text": event.get("reasoningText", "")
                    }
                elif "result" in event:
                    result = event["result"]
                    if hasattr(result, 'message') and hasattr(result.message, 'content'):
                        if isinstance(result.message.content, list) and len(result.message.content) > 0:
                            final_response = result.message.content[0].get('text', '')
                        else:
                            final_response = str(result.message.content)
                    else:
                        final_response = str(result)
                    
                    yield {
                        "type": "complete",
                        "final_response": final_response
                    }
                else:
                    yield event
                
        except Exception as e:
            logger.error(f"Error in streaming mode: {str(e)}", exc_info=True)
            yield {"error": f"Error processing request with agent (streaming): {str(e)}"}
        
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        logger.error(error_msg, exc_info=True)
        yield {"error": error_msg}

if __name__ == "__main__":
    if MCP_SERVER_URL:
        logger.info("Testing MCP server connection at startup...")
        try:
            import requests
            jwt_token = access_token.get_gateway_access_token()
            headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"} if jwt_token else {"Content-Type": "application/json"}
            payload = {
                "jsonrpc": "2.0",
                "id": "startup-test",
                "method": "tools/list",
                "params": {}
            }
            response = requests.post(f"{MCP_SERVER_URL}/mcp", headers=headers, json=payload, timeout=10)
            logger.info(f"Direct test response status: {response.status_code}")
        except Exception as e:
            logger.error(f"Error in direct test: {str(e)}", exc_info=True)
    else:
        logger.info("MCP_SERVER_URL not set. Skipping MCP direct test (local run).")
    
    app.run()

