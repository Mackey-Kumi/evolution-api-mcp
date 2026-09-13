import os

# main.py reads these at import time; set safe test values before any test
# module imports it, so _validate_config() and friends see a "configured" server
# without touching a developer's real .env.
os.environ.setdefault("EVOLUTION_API_URL", "https://evolution.test")
os.environ.setdefault("EVOLUTION_API_KEY", "test-evolution-key")
os.environ.setdefault("MCP_API_KEY", "test-mcp-key")
