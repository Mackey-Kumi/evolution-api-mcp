# Evolution API MCP Server

An [MCP](https://modelcontextprotocol.io) server that exposes [Evolution API](https://github.com/EvolutionAPI/evolution-api) — a self-hosted, open-source WhatsApp gateway — as a set of tools an AI agent can call directly. Point any MCP-compatible agent (Claude, an n8n AI Agent node's MCP Client, etc.) at this server and it can send messages, manage sent messages, run interactive WhatsApp UI (buttons, lists, carousels), and read conversation history in a single WhatsApp account, without touching the Evolution API HTTP surface itself.

This was built for a specific 1:1 business-messaging use case, not as a general-purpose multi-tenant product — but since Evolution API itself is open source, the repo is public too. Feel free to fork or adapt it.

## How it fits together

```
Agent (Claude / n8n / etc.) --MCP--> this server --HTTP--> Evolution API --> WhatsApp
```

This server does not talk to WhatsApp directly. It requires a running Evolution API instance with a WhatsApp account already connected (instance created and QR-paired) — this project only wraps that instance's REST API as MCP tools.

## Prerequisites

- Python 3.10+
- A running [Evolution API](https://doc.evolution-api.com) instance (self-hosted or hosted) with a connected WhatsApp instance
- The Evolution API instance's name and its API key

## Setup

```bash
git clone <this-repo>
cd evolution-api-mcp
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
EVOLUTION_API_URL=https://your-evolution-api-host
EVOLUTION_API_KEY=your-evolution-api-key
MCP_API_KEY=choose-a-long-random-secret
PORT=8000
```

| Variable | Description |
|---|---|
| `EVOLUTION_API_URL` | Base URL of your Evolution API instance |
| `EVOLUTION_API_KEY` | API key Evolution API expects on the `apikey` header |
| `MCP_API_KEY` | Secret this server requires on every incoming request (see Authentication below) — you choose this value |
| `PORT` | Port to listen on (defaults to `8000` if unset) |

Run it:

```bash
python main.py
```

The server starts an HTTP-transport MCP endpoint (via [FastMCP](https://gofastmcp.com)) on `0.0.0.0:$PORT`.

A `Procfile` is included for platforms that use one (Railway, Heroku-style deploys).

## Authentication

Every request to this server must include:

```
x-api-key: <MCP_API_KEY>
```

Requests without a matching key get a `401 Unauthorized`. This is the key your MCP client (e.g. an n8n MCP Client node) needs to be configured with — it's separate from `EVOLUTION_API_KEY`, which this server uses on the *outbound* side to authenticate to Evolution API. `account_instance` (the Evolution API instance name) is passed per tool call, so one deployment of this server can drive multiple WhatsApp instances if you have them.

## Tools

**`whatsapp_id`** in the tools below refers to the contact's WhatsApp ID as provided by Evolution API (e.g. `264724990148861@lid`), not a raw phone number.

### Sending messages

| Tool | Description | `delay` |
|---|---|---|
| `send_text` | Send a text message, optionally as a quoted reply | ✓ |
| `send_image` | Send an image from a URL with an optional caption | ✓ |
| `send_video` | Send a video from a URL with an optional caption | ✓ |
| `send_document` | Send a PDF document from a URL with a display filename and optional caption | ✓ |
| `send_voice_note` | Send a native WhatsApp voice note from an audio URL | ✓ |
| `send_contact_card` | Share a contact card (name, phone number, optional org/email/URL) | — |

Tools marked ✓ accept an optional `delay` (milliseconds, defaults to `1200`) that shows a "typing…"/"recording…" indicator immediately before the message lands, so replies don't appear instantly out of nowhere. Since Evolution API only delivers the message after the delay elapses, the tool call blocks for that duration — set it to `0` for an instant send, or longer for a message that should feel like it took more effort to compose.

### Interactive messages

| Tool | Description | `delay` |
|---|---|---|
| `send_quick_replies` | Message with up to 3 tappable quick-reply buttons | ✓ |
| `send_cta_url` | Message with a single clickable call-to-action URL button | ✓ |
| `send_list_message` | Message with a tappable menu of rows grouped into sections | ✓ |
| `send_carousel` | Swipeable carousel of up to 10 cards, each with its own buttons | — |

### Managing sent messages

| Tool | Description |
|---|---|
| `react_to_message` | React to any message (yours or theirs) with an emoji |
| `edit_message` | Edit the text of a previously sent message |
| `delete_message` | Delete one of your own messages for everyone |

### Lookup

| Tool | Description |
|---|---|
| `get_whatsapp_number` | Resolve a WhatsApp ID to a real phone number and business-account status |
| `find_messages` | Paginated conversation history for a chat |

## Known limitation

`find_messages` only extracts text content for plain text, extended text, interactive, and list message types. If the user sends an image, voice note, or document, the tool will surface that *something* arrived but not its content — the agent currently has no way to view/transcribe/read inbound media.

## Deploying

Any platform that runs a Python web process from a `Procfile` (Railway, etc.) works — set the four environment variables above in the platform's config and deploy. Make sure `EVOLUTION_API_URL` is reachable from wherever this server runs, and that your MCP client is configured with the `x-api-key` header.
