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
        phone_number: The user's WhatsApp number with country code, no '+' or leading zeros. This is provided to you in your prompt. Example: 233XXXXXXXXX@s.whatsapp.net
        text: The message to send to the user in WhatsApp in a single bubble (eg. How can I help you today?)
    """
    try:
        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendText/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json={
                "number": phone_number,
                "text": text
            }
        )
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}




@mcp.tool()
def send_image(account_instance: str, phone_number: str, image_url: str, caption: Optional[str] = None) -> dict:
    """
    Send a single WhatsApp image with an optional message caption

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        phone_number: The user's WhatsApp number with country code, no '+' or leading zeros. This is provided to you in your prompt. Example: 233XXXXXXXXX@s.whatsapp.net
        image_url: The URL to the image you want to send.
        caption: This is an optional message you can send together with the image.
    """

    try:
        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendMedia/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json={
                "number": phone_number,
                "mediatype": "image",
                "mimetype": "image/png",
                "caption": caption,
                "media": image_url
            }
        )
        response.raise_for_status()
        
        raw_data = response.json()
        
        # Safely extract high-value metadata from the root level
        structured_data = {
            "message_id": raw_data.get("key", {}).get("id"),
            "remote_jid": raw_data.get("key", {}).get("remoteJid"),
            "status": raw_data.get("status"),
            "instance_id": raw_data.get("instanceId"),
            "timestamp": raw_data.get("messageTimestamp")
        }
        
        return {"success": True, "data": structured_data}
    
    except Exception as e:
        return {"success": False, "error": str(e)}




@mcp.tool()
def send_video(account_instance: str, phone_number: str, video_url: str, caption: Optional[str] = None) -> dict:
    """
    Send a single WhatsApp video with an optional message caption

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        phone_number: The user's WhatsApp number with country code, no '+' or leading zeros. This is provided to you in your prompt. Example: 233XXXXXXXXX@s.whatsapp.net
        video_url: The URL to the video you want to send.
        caption: This is an optional message you can send together with the video.
    """

    try:
        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendMedia/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json={
                "number": phone_number,
                "mediatype": "video",
                "mimetype": "video/mp4",
                "caption": caption,
                "media": video_url
            }
        )
        response.raise_for_status()
        
        
        raw_data = response.json()
        
        # Safely extract only what the model needs to confirm delivery
        structured_data = {
            "message_id": raw_data.get("key", {}).get("id"),
            "remote_jid": raw_data.get("key", {}).get("remoteJid"),
            "status": raw_data.get("status"),
            "instance_id": raw_data.get("instanceId"),
            "timestamp": raw_data.get("messageTimestamp")
        }
        
        return {"success": True, "data": structured_data}

    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app = mcp.http_app(transport="streamable-http", middleware=[Middleware(APIKeyMiddleware)])
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    server.run()