import os
import json
from datetime import datetime, timezone
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


def _to_utc_iso(unix_timestamp) -> Optional[str]:
    """Convert a Unix timestamp (seconds) from the Evolution API into a UTC ISO 8601 string."""
    if unix_timestamp is None:
        return None
    return datetime.fromtimestamp(unix_timestamp, tz=timezone.utc).isoformat()

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.headers.get("x-api-key") != API_KEY:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)
    


@mcp.tool()
def send_text(
    account_instance: str,
    whatsapp_id: str,
    text: str,
    message_id: Optional[str] = None
    ) -> dict:
    """
    Send a single WhatsApp bubble message

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
        text: The message to send to the user in WhatsApp in a single bubble (eg. How can I help you today?)
        message_id: Optional ID of a message to quote/reply to. If provided, this message is sent as a quoted reply; otherwise it is sent standalone.
    """
    try:
        json_payload = {
            "number": whatsapp_id,
            "text": text
        }

        if message_id:
            json_payload["quoted"] = {"key": {"id": message_id}}

        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendText/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json=json_payload
        )

        response.raise_for_status()

        raw_data = response.json()

        
        structured_data = {
            "message_id": raw_data.get("key", {}).get("id"),
            "whatsapp_id": raw_data.get("key", {}).get("remoteJid"),
            "status": raw_data.get("status"),
            "instance_id": raw_data.get("instanceId"),
            "timestamp": _to_utc_iso(raw_data.get("messageTimestamp"))
        }
        
        return {"success": True, "data": structured_data}

    except Exception as e:
        return {"success": False, "error": str(e)}




@mcp.tool()
def send_image(
    account_instance: str,
    whatsapp_id: str,
    image_url: str,
    caption: Optional[str] = None,
    message_id: Optional[str] = None
    ) -> dict:
    """
    Send a single WhatsApp image with an optional message caption

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
        image_url: The URL to the image you want to send.
        caption: This is an optional message you can send together with the image.
        message_id: Optional ID of a message to quote/reply to. If provided, this message is sent as a quoted reply; otherwise it is sent standalone.
    """

    try:
        json_payload = {
            "number": whatsapp_id,
            "mediatype": "image",
            "mimetype": "image/png",
            "media": image_url
        }

        if caption:
            json_payload["caption"] = caption

        if message_id:
            json_payload["quoted"] = {"key": {"id": message_id}}

        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendMedia/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json=json_payload
        )
        response.raise_for_status()
        
        raw_data = response.json()
        
        # Safely extract high-value metadata from the root level
        structured_data = {
            "message_id": raw_data.get("key", {}).get("id"),
            "whatsapp_id": raw_data.get("key", {}).get("remoteJid"),
            "status": raw_data.get("status"),
            "instance_id": raw_data.get("instanceId"),
            "timestamp": _to_utc_iso(raw_data.get("messageTimestamp"))
        }
        
        return {"success": True, "data": structured_data}
    
    except Exception as e:
        return {"success": False, "error": str(e)}




@mcp.tool()
def send_video(
    account_instance: str,
    whatsapp_id: str,
    video_url: str,
    caption: Optional[str] = None,
    message_id: Optional[str] = None
    ) -> dict:
    """
    Send a single WhatsApp video with an optional message caption

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
        video_url: The URL to the video you want to send.
        caption: This is an optional message you can send together with the video.
        message_id: Optional ID of a message to quote/reply to. If provided, this message is sent as a quoted reply; otherwise it is sent standalone.
    """

    try:
        json_payload = {
            "number": whatsapp_id,
            "mediatype": "video",
            "mimetype": "video/mp4",
            "media": video_url
        }

        if caption:
            json_payload["caption"] = caption

        if message_id:
            json_payload["quoted"] = {"key": {"id": message_id}}

        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendMedia/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json=json_payload
        )
        response.raise_for_status()
        raw_data = response.json()
        
        # Safely extract only what the model needs to confirm delivery
        structured_data = {
            "message_id": raw_data.get("key", {}).get("id"),
            "whatsapp_id": raw_data.get("key", {}).get("remoteJid"),
            "status": raw_data.get("status"),
            "instance_id": raw_data.get("instanceId"),
            "timestamp": _to_utc_iso(raw_data.get("messageTimestamp"))
        }
        
        return {"success": True, "data": structured_data}

    except Exception as e:
        return {"success": False, "error": str(e)}



@mcp.tool()
def send_document(
    account_instance: str,
    whatsapp_id: str,
    document_url: str,
    file_name: str,
    caption: Optional[str] = None,
    message_id: Optional[str] = None
    ) -> dict:
    """
    Send a single WhatsApp PDF document with an optional message caption

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
        document_url: The URL to the PDF document you want to send.
        file_name: The file name to display to the recipient (e.g. "invoice.pdf").
        caption: This is an optional message you can send together with the document.
        message_id: Optional ID of a message to quote/reply to. If provided, this message is sent as a quoted reply; otherwise it is sent standalone.
    """

    try:
        if not file_name.lower().endswith(".pdf"):
            file_name = f"{file_name}.pdf"

        json_payload = {
            "number": whatsapp_id,
            "mediatype": "document",
            "mimetype": "application/pdf",
            "fileName": file_name,
            "media": document_url
        }

        if caption:
            json_payload["caption"] = caption

        if message_id:
            json_payload["quoted"] = {"key": {"id": message_id}}

        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendMedia/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json=json_payload
        )
        response.raise_for_status()

        raw_data = response.json()

        structured_data = {
            "message_id": raw_data.get("key", {}).get("id"),
            "whatsapp_id": raw_data.get("key", {}).get("remoteJid"),
            "status": raw_data.get("status"),
            "instance_id": raw_data.get("instanceId"),
            "timestamp": _to_utc_iso(raw_data.get("messageTimestamp"))
        }

        return {"success": True, "data": structured_data}

    except Exception as e:
        return {"success": False, "error": str(e)}



@mcp.tool()
def send_voice_note(
    account_instance: str,
    whatsapp_id: str,
    audio_url: str,
    message_id: Optional[str] = None
    ) -> dict:
    """
    Send a whatsApp native voice note to the user.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
        audio_url: The URL to the audio you want to send as voice note.
        message_id: Optional ID of a message to quote/reply to. If provided, this message is sent as a quoted reply; otherwise it is sent standalone.
    """

    try:
        json_payload = {
            "number": whatsapp_id,
            "audio": audio_url #  "audio/ogg; codecs=opus"
        }

        if message_id:
            json_payload["quoted"] = {"key": {"id": message_id}}

        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendWhatsAppAudio/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json=json_payload
        )
        response.raise_for_status()
        raw_data = response.json()
        
        structured_data = {
            "message_id": raw_data.get("key", {}).get("id"),
            "whatsapp_id": raw_data.get("key", {}).get("remoteJid"),
            "status": raw_data.get("status"),
            "instance_id": raw_data.get("instanceId"),
            "timestamp": _to_utc_iso(raw_data.get("messageTimestamp"))
        }
        
        return {"success": True, "data": structured_data}

    except Exception as e:
        return {"success": False, "error": str(e)}



@mcp.tool()
def react_to_message(
    account_instance: str, 
    whatsapp_id: str, 
    message_id: str, 
    emoji: str
    ) -> dict:
    """
    React to a WhatsApp message with an emoji. This can be a user message or your own.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
        message_id: The ID of the message you want to react to.
        emoji: A single emoji you want to use to react to the message. 
    """

    try:
        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendReaction/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json={
                "key": {
                "remoteJid": whatsapp_id, 
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
def delete_message(
    account_instance: str,
    whatsapp_id: str,
    message_id: str
    ) -> dict:
    """
    Delete one of your own WhatsApp messages for everyone in the chat.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
        message_id: The ID of the message you want to delete.
    """

    try:
        response = requests.delete(
            f"{EVOLUTION_API_URL}/chat/deleteMessageForEveryone/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json={
                "id": message_id,
                "remoteJid": whatsapp_id,
                "fromMe": True
            }
        )
        response.raise_for_status()

        return {"success": True, "data": f"Deleted message {message_id} successfully"}

    except Exception as e:
        return {"success": False, "error": str(e)}



@mcp.tool()
def edit_message(
    account_instance: str,
    whatsapp_id: str,
    message_id: str,
    new_text: str
    ) -> dict:
    """
    Edit the text of one of your own previously sent WhatsApp messages.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
        message_id: The ID of the message you want to edit.
        new_text: The new text to replace the message's original content with.
    """

    try:
        response = requests.post(
            f"{EVOLUTION_API_URL}/chat/updateMessage/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json={
                "number": whatsapp_id,
                "key": {
                    "remoteJid": whatsapp_id,
                    "fromMe": True,
                    "id": message_id
                },
                "text": new_text
            }
        )
        response.raise_for_status()

        return {"success": True, "data": f"Updated message {message_id} successfully"}

    except Exception as e:
        return {"success": False, "error": str(e)}



@mcp.tool()
def send_contact_card(
    account_instance: str,
    whatsapp_id: str,
    full_name: str,
    phone_number: str,
    organization: Optional[str] = None,
    email: Optional[str] = None,
    url: Optional[str] = None
    ) -> dict:
    """
    Send a WhatsApp contact card to the user.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
        full_name: The full name of the contact being shared.
        phone_number: The phone number of the contact being shared (not the recipient), digits only without a leading + or spaces. Example: 233596603296
        organization: Optional company/organization name for the contact.
        email: Optional email address for the contact.
        url: Optional website URL for the contact.
    """

    try:
        contact_entry = {
            "fullName": full_name,
            "wuid": phone_number,
            "phoneNumber": f"+{phone_number}"
        }

        if organization:
            contact_entry["organization"] = organization

        if email:
            contact_entry["email"] = email

        if url:
            contact_entry["url"] = url

        json_payload = {
            "number": whatsapp_id,
            "contact": [contact_entry]
        }

        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendContact/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json=json_payload
        )
        response.raise_for_status()
        raw_data = response.json()

        structured_data = {
            "message_id": raw_data.get("key", {}).get("id"),
            "whatsapp_id": raw_data.get("key", {}).get("remoteJid"),
            "status": raw_data.get("status"),
            "instance_id": raw_data.get("instanceId"),
            "timestamp": _to_utc_iso(raw_data.get("messageTimestamp"))
        }

        return {"success": True, "data": structured_data}

    except Exception as e:
        return {"success": False, "error": str(e)}



@mcp.tool()
def send_quick_replies(
    account_instance: str,
    whatsapp_id: str,
    title: str,
    text_content: str,
    reply_buttons: list[dict],
    footer: Optional[str] = None,
    message_id: Optional[str] = None
) -> dict:
    """
    Send a WhatsApp message with up to 3 quick reply buttons.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
        title: A short, bold header text displayed at the very top of the message (⚠️ Do not bold, it would be done automatically). Example: "Order Status Update")
        text_content: The main text message body displayed in the middle above the buttons.
        reply_buttons: A list of quick reply buttons. Each button is a dictionary with two keys:
                       'displayText' (⚠️ MAXIMUM 20 CHARACTERS, including spaces) and 'id' (the return value).
                       Maximum 3 buttons allowed.
                       Example: [{"displayText": "Small Package", "id": "small-package"}, {"displayText": "Large Package", "id": "large-package"}].
        footer: An optional line of small, muted gray text displayed below the main body or buttons (e.g., "Reply by clicking a button").
        message_id: Optional ID of a message to quote/reply to. If provided, this message is sent as a quoted reply; otherwise it is sent standalone.
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
            "number": whatsapp_id,
            "title": title,
            "description": text_content,
            "buttons": formatted_buttons
        }

        # Only inject the footer if the model actually provided one
        if footer:
            json_payload["footer"] = footer

        if message_id:
            json_payload["quoted"] = {"key": {"id": message_id}}

        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendButtons/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json=json_payload
        )

        response.raise_for_status()
        raw_data = response.json()

        structured_data = {
            "message_id": raw_data.get("key", {}).get("id"),
            "whatsapp_id": raw_data.get("key", {}).get("remoteJid"),
            "status": raw_data.get("status"),
            "instance_id": raw_data.get("instanceId"),
            "timestamp": _to_utc_iso(raw_data.get("messageTimestamp"))
        }
        return {"success": True, "data": structured_data}

    except Exception as e:
        return {"success": False, "error": str(e)}




@mcp.tool()
def send_cta_url(
    account_instance: str,
    whatsapp_id: str,
    title: str,
    text_content: str,
    button_label: str,
    button_url: str,
    footer: Optional[str] = None,
    message_id: Optional[str] = None
) -> dict:
    """
    Send a WhatsApp message with a single clickable Call-To-Action (CTA) URL button.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
        title: A short, bold header text displayed at the very top of the message (⚠️ Do not bold, it would be done automatically). Example: "Order Status Update")
        text_content: The main text message body displayed in the middle above the cta button.
        button_label: The text inside the action button (MAX 20 CHARACTERS). E.g., "Pay Invoice".
        button_url: This is the URL to the page that would open in the browser when clicked. E.g., "https://checkout.stripe.com/...".
        footer: An optional line of small, muted gray text displayed below the main body or buttons (e.g., "Clicking takes you to the payment page")
        message_id: Optional ID of a message to quote/reply to. If provided, this message is sent as a quoted reply; otherwise it is sent standalone.
    """

    try:
        # Assemble the JSON payload structure
        json_payload = {
            "number": whatsapp_id,
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

        if message_id:
            json_payload["quoted"] = {"key": {"id": message_id}}

        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendButtons/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json=json_payload
        )

        response.raise_for_status()
        raw_data = response.json()

        structured_data = {
            "message_id": raw_data.get("key", {}).get("id"),
            "whatsapp_id": raw_data.get("key", {}).get("remoteJid"),
            "status": raw_data.get("status"),
            "instance_id": raw_data.get("instanceId"),
            "timestamp": _to_utc_iso(raw_data.get("messageTimestamp"))
        }
        return {"success": True, "data": structured_data}

    except Exception as e:
        return {"success": False, "error": str(e)}




@mcp.tool()
def send_list_message(
    account_instance: str,
    whatsapp_id: str,
    title: str,
    text_content: str,
    button_label: str,
    sections: list[dict],
    footer: str,
    message_id: Optional[str] = None
) -> dict:
    """
    Send an interactive WhatsApp list message with selectable rows grouped into sections natively for the Evolution API.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
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
        message_id: Optional ID of a message to quote/reply to. If provided, this message is sent as a quoted reply; otherwise it is sent standalone.
    """
    try:

        json_payload = {
            "number": whatsapp_id,
            "title": title,
            "description": text_content,
            "buttonText": button_label,
            "footerText": footer,
            "sections": sections
        }

        if message_id:
            json_payload["quoted"] = {"key": {"id": message_id}}

        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendList/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json=json_payload
        )
        response.raise_for_status()
        raw_data = response.json()

        structured_data = {
            "message_id": raw_data.get("key", {}).get("id"),
            "whatsapp_id": raw_data.get("key", {}).get("remoteJid"),
            "status": raw_data.get("status"),
            "instance_id": raw_data.get("instanceId"),
            "timestamp": _to_utc_iso(raw_data.get("messageTimestamp"))
        }
        return {"success": True, "data": structured_data}

    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def send_carousel(
    account_instance: str, 
    whatsapp_id: str,
    main_body: str,
    cards: list[dict]
) -> dict:
    """
    Send a swipeable WhatsApp carousel containing up to 10 product/info cards. 
    Each card can have up to 3 quick reply action buttons.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
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
            "number": whatsapp_id,
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
            "whatsapp_id": raw_data.get("key", {}).get("remoteJid"),
            "status": raw_data.get("status"),
            "instance_id": raw_data.get("instanceId"),
            "timestamp": _to_utc_iso(raw_data.get("messageTimestamp"))
        }
        return {"success": True, "data": structured_data}

    except Exception as e:
        return {"success": False, "error": str(e)}



@mcp.tool()
def get_whatsapp_number(
    account_instance: str,
    whatsapp_id: str
) -> dict:
    """
    Resolve the user's WhatsApp ID (@lid) to retrieve the contact's real phone number
    and whether they are a WhatsApp Business account.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
    """
    try:
        response = requests.post(
            f"{EVOLUTION_API_URL}/chat/fetchBusinessProfile/{account_instance}",
            headers={"apikey": EVOLUTION_API_KEY},
            json={"number": whatsapp_id}
        )
        response.raise_for_status()
        raw_data = response.json()

        phone_number = None
        jid = raw_data.get("jid", "")
        if jid:
            phone_number = jid.replace("@s.whatsapp.net", "")

        return {
            "success": True,
            "data": {
                "whatsapp_id": whatsapp_id,
                "phone_number": phone_number,
                "is_business": raw_data.get("isBusiness", False),
                "exists": raw_data.get("exists", False)
            }
        }

    except Exception as e:
        return {"success": False, "error": str(e)}





@mcp.tool()
def find_messages(
    account_instance: str,
    whatsapp_id: str,
    page: int = 1,
    offset: int = 10
) -> dict:
    """
    Query and retrieve historical message records for a specific conversation chat thread.

    Args:
        account_instance: The unique identifier of the WhatsApp account to send the message from, this is provided to you in your prompt.
        whatsapp_id: The user's WhatsApp ID that  uniquely identifiers them. This is provided in your prompt. Example: 264724990148861@lid
        page: The page number to retrieve for pagination. Defaults to 1.
        offset: The number of message records to return per page. Defaults to 10.
    """
    try:
        payload = {
            "where": {
                "key": {
                    "remoteJid": whatsapp_id
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
                "timestamp": _to_utc_iso(record.get("messageTimestamp")),
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