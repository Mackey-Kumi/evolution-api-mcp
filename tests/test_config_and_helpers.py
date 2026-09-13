import pytest

import main


def test_validate_config_raises_when_a_var_is_missing(monkeypatch):
    monkeypatch.setattr(main, "EVOLUTION_API_URL", None)
    monkeypatch.setattr(main, "EVOLUTION_API_KEY", "key")
    monkeypatch.setattr(main, "API_KEY", "key")

    with pytest.raises(RuntimeError, match="EVOLUTION_API_URL"):
        main._validate_config()


def test_validate_config_lists_every_missing_var(monkeypatch):
    monkeypatch.setattr(main, "EVOLUTION_API_URL", None)
    monkeypatch.setattr(main, "EVOLUTION_API_KEY", None)
    monkeypatch.setattr(main, "API_KEY", "key")

    with pytest.raises(RuntimeError) as exc_info:
        main._validate_config()

    assert "EVOLUTION_API_URL" in str(exc_info.value)
    assert "EVOLUTION_API_KEY" in str(exc_info.value)
    assert "MCP_API_KEY" not in str(exc_info.value)


def test_validate_config_passes_when_everything_is_set(monkeypatch):
    monkeypatch.setattr(main, "EVOLUTION_API_URL", "https://evo.test")
    monkeypatch.setattr(main, "EVOLUTION_API_KEY", "evo-key")
    monkeypatch.setattr(main, "API_KEY", "mcp-key")

    main._validate_config()  # should not raise


def test_to_utc_iso_converts_unix_seconds():
    assert main._to_utc_iso(1700000000) == "2023-11-14T22:13:20+00:00"


def test_to_utc_iso_passes_through_none():
    assert main._to_utc_iso(None) is None


def test_extract_message_result_pulls_expected_fields():
    raw = {
        "key": {"id": "MSG1", "remoteJid": "1234@s.whatsapp.net"},
        "status": "PENDING",
        "instanceId": "inst-1",
        "messageTimestamp": 1700000000,
    }

    result = main._extract_message_result(raw)

    assert result == {
        "message_id": "MSG1",
        "whatsapp_id": "1234@s.whatsapp.net",
        "status": "PENDING",
        "instance_id": "inst-1",
        "timestamp": "2023-11-14T22:13:20+00:00",
    }


def test_extract_message_result_tolerates_missing_fields():
    assert main._extract_message_result({}) == {
        "message_id": None,
        "whatsapp_id": None,
        "status": None,
        "instance_id": None,
        "timestamp": None,
    }


def test_tool_error_shape_matches_what_tools_return():
    result = main._tool_error("some_tool", ValueError("boom"))

    assert result == {"success": False, "error": "boom"}
