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
def send_text(
    account_instance: str, 
    phone_number: str, 
    text: str
    ) -> dict:
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

        raw_data = response.json()

        
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
def send_image(
    account_instance: str, 
    phone_number: str, 
    image_url: str, 
    caption: Optional[str] = None
    ) -> dict:
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
def send_video(
    account_instance: str, 
    phone_number: str, 
    video_url: str, 
    caption: Optional[str] = None
    ) -> dict:
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



@mcp.tool()
def send_voice_note(
    account_instance: str, 
    phone_number: str, 
    audio_url: str
    ) -> dict:
    """
    Send a whatsApp native voice note to the user.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        phone_number: The user's WhatsApp number with country code, no '+' or leading zeros. This is provided to you in your prompt. Example: 233XXXXXXXXX@s.whatsapp.net
        audio_url: The URL to the audio you want to send as voice note.
    """

    try:
        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendWhatsAppAudio/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json={
                "number": phone_number,
                "audio": audio_url #  "audio/ogg; codecs=opus"
            }
        )
        response.raise_for_status()
        raw_data = response.json()
        
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
def react_to_message(
    account_instance: str, 
    phone_number: str, 
    message_id: str, 
    emoji: str
    ) -> dict:
    """
    React to a WhatsApp message with an emoji. This can be a user message or your own.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        phone_number: The user's WhatsApp number with country code, no '+' or leading zeros. This is provided to you in your prompt. Example: 233XXXXXXXXX@s.whatsapp.net
        message_id: The ID of the message you want to react to.
        emoji: A single emoji you want to use to react to the message. 
    """

    try:
        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendReaction/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json={
                "key": {
                "remoteJid": phone_number, 
                "fromMe": True,
                "id": message_id
                },
                "reaction": emoji
            }
        )
        response.raise_for_status()
        
        return {"success": True, "data": f"Reacted to {message_id} successfully with {emoji}"}

    except Exception as e:
        return {"success": False, "error": str(e)}



@mcp.tool()
def send_quick_replies(
    account_instance: str, 
    phone_number: str,
    title: str, 
    text_content: str, 
    reply_buttons: list[dict],
    footer: Optional[str] = None
) -> dict:
    """
    Send a WhatsApp message with up to 3 quick reply buttons.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        phone_number: The user's WhatsApp number with country code, no '+' or leading zeros. This is provided to you in your prompt. Example: 233XXXXXXXXX@s.whatsapp.net
        title: A short, bold header text displayed at the very top of the message (⚠️ Do not bold, it would be done automatically). Example: "Order Status Update")
        text_content: The main text message body displayed in the middle above the buttons.
        reply_buttons: A list of quick reply buttons. Each button is a dictionary with two keys:
                       'displayText' (⚠️ MAXIMUM 20 CHARACTERS, including spaces) and 'id' (the return value).
                       Maximum 3 buttons allowed.
                       Example: [{"displayText": "Small Package", "id": "small-package"}, {"displayText": "Large Package", "id": "large-package"}].
        footer: An optional line of small, muted gray text displayed below the main body or buttons (e.g., "Reply by clicking a button").
    """
    try:
        # Programmatically inject the mandatory 'type': 'reply' into each button
        formatted_buttons = []
        for btn in reply_buttons[:3]:  # Enforce max 3 buttons safely
            formatted_buttons.append({
                "type": "reply",
                "displayText": btn.get("displayText", "")[:20],  # Enforce max 20 chars safely
                "id": btn.get("id", "")
            })


        # Assemble the JSON payload structure
        json_payload = {
            "number": phone_number,
            "title": title,
            "description": text_content,
            "buttons": formatted_buttons
        }

        # Only inject the footer if the model actually provided one
        if footer:
            json_payload["footer"] = footer

        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendButtons/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json=json_payload
        )

        response.raise_for_status()
        raw_data = response.json()

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
def send_cta_url(
    account_instance: str, 
    phone_number: str,
    title: str, 
    text_content: str, 
    button_label: str,
    button_url: str,
    footer: Optional[str] = None
) -> dict:
    """
    Send a WhatsApp message with a single clickable Call-To-Action (CTA) URL button.
    
    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        phone_number: The user's WhatsApp number with country code, no '+' or leading zeros. This is provided to you in your prompt. Example: 233XXXXXXXXX@s.whatsapp.net
        title: A short, bold header text displayed at the very top of the message (⚠️ Do not bold, it would be done automatically). Example: "Order Status Update")
        text_content: The main text message body displayed in the middle above the cta button.
        button_label: The text inside the action button (MAX 20 CHARACTERS). E.g., "Pay Invoice".
        button_url: This is the URL to the page that would open in the browser when clicked. E.g., "https://checkout.stripe.com/...".
        footer: An optional line of small, muted gray text displayed below the main body or buttons (e.g., "Clicking takes you to the payment page")
    """

    try:
        # Assemble the JSON payload structure
        json_payload = {
            "number": phone_number,
            "title": title,
            "description": text_content,
            "buttons": [
                {
                "type": "url",
                "displayText": button_label[:20],
                "url": button_url
                }
            ]
        }

        if footer:
            json_payload["footer"] = footer

        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendButtons/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json=json_payload
        )

        response.raise_for_status()
        raw_data = response.json()

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
def send_list_message(
    account_instance: str, 
    phone_number: str, 
    title: str,
    text_content: str, 
    button_label: str, 
    sections: list[dict], 
    footer: str
) -> dict:
    """
    Send an interactive WhatsApp list message with selectable rows grouped into sections natively for the Evolution API.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        phone_number: The user's WhatsApp number with country code, no '+' or leading zeros. This is provided to you in your prompt. Example: 233XXXXXXXXX@s.whatsapp.net
        title: A short, bold header text displayed at the very top of the list message (e.g., "Main Menu").
        text_content: The main message description text shown above the list menu button.
        button_label: The label on the button that the user taps to open the list layout selection menu (e.g., "Click Here").
        sections: A list of dict sections matching the Evolution API payload natively. Max 10 total rows across all sections combined.
                  Each section MUST contain:
                  - 'title': The string category title for the section rows.
                  - 'rows': A list of row dicts where each row dictionary MUST contain exactly:
                    * 'title': The visible option text (str).
                    * 'rowId': The unique string key returned when tapped (str).
                    * 'description': (Optional) Subtext details for the item.
                  Example: [{"title": "Select Fruit", "rows": [{"title": "Apple", "rowId": "fruit_apple", "description": "Crisp and sweet"}]}]
        footer: A string line of helper text shown at the bottom of the message. (e.g., "The button opens a menu to select from").
    """
    try:
        
        json_payload = {
            "number": phone_number,
            "title": title,
            "description": text_content,
            "buttonText": button_label,
            "footerText": footer,
            "sections": sections
        }

        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendList/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json=json_payload
        )
        response.raise_for_status()
        raw_data = response.json()

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
def send_carousel(
    account_instance: str, 
    phone_number: str,
    main_body: str,
    cards: list[dict]
) -> dict:
    """
    Send a swipeable WhatsApp carousel containing up to 10 product/info cards. 
    Each card can have up to 3 quick reply action buttons.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        phone_number: The user's WhatsApp number with country code, no '+' or leading zeros. This is provided to you in your prompt. Example: 233XXXXXXXXX@s.whatsapp.net
        main_body: The text message intro shown above the whole carousel slider layout (e.g., "Check out this week's catalog!").
        cards: A list of dict cards. MAXIMUM 10 cards allowed. 
               Each card dictionary MUST contain:
               - 'body': The primary message body text for this card slide.
               - 'footer': A mandatory string line text shown at the bottom of the card (e.g., price or category).
               - 'imageUrl': Direct image web address shown on the card layout.
               - 'buttons': A list of quick reply button dictionaries. MAXIMUM 3 buttons per card.
                 Each button dict must contain exactly:
                 * 'text': Visible label text on the card button (MAX 20 CHARACTERS).
                 * 'id': Unique tracking key string returned when clicked.
               Example: [{"body": "Product A", "footer": "$99.00", "imageUrl": "https://picsum.photos/seed/a/600/400", "buttons": [{"text": "Buy Now", "id": "buy_a"}]}]
    """
    try:
        formatted_cards = []
        
        # Enforce WhatsApp's native maximum limit of 10 slider cards safely
        for card in cards[:10]:
            formatted_buttons = []
            
            # Enforce WhatsApp's native maximum limit of 3 quick replies per card card
            for btn in card.get("buttons", [])[:3]:
                formatted_buttons.append({
                    "type": "reply",
                    "displayText": str(btn.get("text", ""))[:20], # Strict 20 char truncation guard
                    "id": str(btn.get("id", ""))
                })
                
            formatted_cards.append({
                "body": card.get("body"),
                "footer": card.get("footer"),
                "imageUrl": card.get("imageUrl"),
                "buttons": formatted_buttons
            })

        json_payload = {
            "number": phone_number,
            "body": main_body,
            "cards": formatted_cards
        }

        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendCarousel/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json=json_payload
        )
        response.raise_for_status()
        raw_data = response.json()

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
def find_messages(
    account_instance: str,
    remote_jid: str,
    page: int = 1,
    offset: int = 10
) -> dict:
    """
    Query and retrieve historical message records for a specific conversation chat thread.

    Args:
        account_instance: The unique identifier of the WhatsApp account instance.
        remote_jid: The target user's chat identifier with suffix (e.g., "233596603296@s.whatsapp.net" or "264724990148861@lid").
        page: The page number to retrieve for pagination. Defaults to 1.
        offset: The number of message records to return per page. Defaults to 10.
    """
    try:
        payload = {
            "where": {
                "key": {
                    "remoteJid": remote_jid
                }
            },
            "page": page,
            "offset": offset
        }

        response = requests.post(
            f"{EVOLUTION_API_URL}/chat/findMessages/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json=payload
        )
        response.raise_for_status()
        raw_data = response.json()

        # Extract root-level pagination info
        message_data = raw_data.get("messages", {})
        pagination_info = {
            "total_records": message_data.get("total", 0),
            "total_pages": message_data.get("pages", 0),
            "current_page": message_data.get("currentPage", 1)
        }

        # Structure only the vital message histories
        structured_records = []
        for record in message_data.get("records", []):
            msg_type = record.get("messageType", "unknown")
            msg_content = record.get("message", {})
            
            # Extract readable content based on the message type context
            text_body = ""
            if msg_type == "conversation":
                text_body = msg_content.get("conversation", "")
            elif msg_type == "extendedTextMessage":
                text_body = msg_content.get("extendedTextMessage", {}).get("text", "")
            elif msg_type == "interactiveMessage":
                text_body = msg_content.get("interactiveMessage", {}).get("body", {}).get("text", "")
            elif msg_type == "listMessage":
                text_body = msg_content.get("listMessage", {}).get("description", "")

            structured_records.append({
                "message_id": record.get("key", {}).get("id"),
                "from_me": record.get("key", {}).get("fromMe", False),
                "timestamp": record.get("messageTimestamp"),
                "message_type": msg_type,
                "text_content": text_body,
                "status": record.get("MessageUpdate", [{}])[-1].get("status", "SENT") if record.get("MessageUpdate") else "SENT"
            })

        return {
            "success": True, 
            "pagination": pagination_info, 
            "messages": structured_records
        }

    except Exception as e:
        return {"success": False, "error": str(e)}




if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app = mcp.http_app(transport="streamable-http", middleware=[Middleware(APIKeyMiddleware)])
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    server.run()