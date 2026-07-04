import os
import json
from typing import Optional
from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import uvicorn
from starlette.middleware import Middleware
import requests


load_dotenv()

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
API_KEY = os.getenv("MCP_API_KEY")

mcp = FastMCP("Evolution API MCP")

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.headers.get("x-api-key") != API_KEY:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)
    


@mcp.tool()
def send_text(account_instance: str, phone_number: str, text: str) -> dict:
    """
    Send a single WhatsApp bubble message
    
    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        phone_number: The user's WhatsApp number with country code, no '+' or leading zeros. This is provided to you in your prompt. Example: 233XXXXXXXXX.
        text: The message to send to the user in WhatsApp in a single bubble (eg. How can I help you today?)
    """
    try:
        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendText/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json={
                "number": f"{phone_number}@s.whatsapp.net",
                "text": text
            }
        )
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}




if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app = mcp.http_app(transport="streamable-http", middleware=[Middleware(APIKeyMiddleware)])
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    server.run()