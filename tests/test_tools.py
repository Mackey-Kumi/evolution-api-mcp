import httpx
import pytest
import respx

import main

BASE_URL = "https://evolution.test"
INSTANCE = "my-instance"


@pytest.fixture(autouse=True)
def _configured_instance(monkeypatch):
    monkeypatch.setattr(main, "EVOLUTION_API_URL", BASE_URL)
    monkeypatch.setattr(main, "EVOLUTION_API_KEY", "evo-key")


@respx.mock
async def test_send_text_success():
    route = respx.post(f"{BASE_URL}/message/sendText/{INSTANCE}").mock(
        return_value=httpx.Response(
            201,
            json={
                "key": {"id": "MSG1", "remoteJid": "1234@s.whatsapp.net"},
                "status": "PENDING",
                "instanceId": "inst-1",
                "messageTimestamp": 1700000000,
            },
        )
    )

    result = await main.send_text(
        account_instance=INSTANCE, whatsapp_id="1234@s.whatsapp.net", text="hi"
    )

    assert route.called
    sent_body = route.calls.last.request.content
    assert b'"text":"hi"' in sent_body or b'"text": "hi"' in sent_body
    assert result == {
        "success": True,
        "data": {
            "message_id": "MSG1",
            "whatsapp_id": "1234@s.whatsapp.net",
            "status": "PENDING",
            "instance_id": "inst-1",
            "timestamp": "2023-11-14T22:13:20+00:00",
        },
    }


@respx.mock
async def test_send_text_reports_http_errors_without_raising():
    respx.post(f"{BASE_URL}/message/sendText/{INSTANCE}").mock(
        return_value=httpx.Response(500, json={"error": "boom"})
    )

    result = await main.send_text(
        account_instance=INSTANCE, whatsapp_id="1234@s.whatsapp.net", text="hi"
    )

    assert result["success"] is False
    assert "500" in result["error"]


@respx.mock
async def test_send_quick_replies_truncates_to_three_buttons_of_20_chars():
    route = respx.post(f"{BASE_URL}/message/sendButtons/{INSTANCE}").mock(
        return_value=httpx.Response(
            201,
            json={"key": {"id": "MSG2", "remoteJid": "1234@s.whatsapp.net"}, "status": "PENDING"},
        )
    )

    too_many_buttons = [
        {"displayText": "This label is way too long for a button", "id": f"opt-{i}"}
        for i in range(5)
    ]

    result = await main.send_quick_replies(
        account_instance=INSTANCE,
        whatsapp_id="1234@s.whatsapp.net",
        title="Pick one",
        text_content="Choose an option",
        reply_buttons=too_many_buttons,
    )

    assert result["success"] is True
    import json

    sent_payload = json.loads(route.calls.last.request.content)
    assert len(sent_payload["buttons"]) == 3
    assert all(len(btn["displayText"]) <= 20 for btn in sent_payload["buttons"])
    assert all(btn["type"] == "reply" for btn in sent_payload["buttons"])


@respx.mock
async def test_react_to_message_success():
    route = respx.post(f"{BASE_URL}/message/sendReaction/{INSTANCE}").mock(
        return_value=httpx.Response(201, json={})
    )

    result = await main.react_to_message(
        account_instance=INSTANCE,
        whatsapp_id="1234@s.whatsapp.net",
        message_id="MSG1",
        emoji="👍",
    )

    assert route.called
    assert result == {"success": True, "data": "Reacted to MSG1 successfully with 👍"}


@respx.mock
async def test_delete_message_uses_delete_verb():
    route = respx.delete(f"{BASE_URL}/chat/deleteMessageForEveryone/{INSTANCE}").mock(
        return_value=httpx.Response(200, json={})
    )

    result = await main.delete_message(
        account_instance=INSTANCE, whatsapp_id="1234@s.whatsapp.net", message_id="MSG1"
    )

    assert route.called
    assert result["success"] is True


@respx.mock
async def test_find_messages_extracts_text_by_message_type():
    respx.post(f"{BASE_URL}/chat/findMessages/{INSTANCE}").mock(
        return_value=httpx.Response(
            200,
            json={
                "messages": {
                    "total": 1,
                    "pages": 1,
                    "currentPage": 1,
                    "records": [
                        {
                            "key": {"id": "MSG1", "fromMe": False},
                            "messageTimestamp": 1700000000,
                            "messageType": "conversation",
                            "message": {"conversation": "hello there"},
                        }
                    ],
                }
            },
        )
    )

    result = await main.find_messages(account_instance=INSTANCE, whatsapp_id="1234@s.whatsapp.net")

    assert result["success"] is True
    assert result["pagination"] == {"total_records": 1, "total_pages": 1, "current_page": 1}
    assert result["messages"][0]["text_content"] == "hello there"
    assert result["messages"][0]["message_type"] == "conversation"


@respx.mock
async def test_check_whatsapp_numbers_maps_each_entry():
    respx.post(f"{BASE_URL}/chat/whatsappNumbers/{INSTANCE}").mock(
        return_value=httpx.Response(
            200,
            json=[
                {"number": "233593021563", "jid": "233593021563@s.whatsapp.net", "exists": True},
                {"number": "10000000000", "exists": False},
            ],
        )
    )

    result = await main.check_whatsapp_numbers(
        account_instance=INSTANCE, phone_numbers=["233593021563", "10000000000"]
    )

    assert result["success"] is True
    assert result["data"] == [
        {"phone_number": "233593021563", "whatsapp_id": "233593021563@s.whatsapp.net", "exists": True},
        {"phone_number": "10000000000", "whatsapp_id": None, "exists": False},
    ]
