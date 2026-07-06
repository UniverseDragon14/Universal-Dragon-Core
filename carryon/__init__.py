"""Carry-On automation & intelligence core for Universal Dragon.

Three modules:
  - whatsapp_voice : WhatsApp voice-note -> STT -> LLM -> TTS response engine
  - media_pipeline : FFmpeg + OpenCV automated photo/video editing
  - carryon_gateway: authenticated local command gateway (Nova Guard routed)

All modules log to stderr only (MCP JSON-RPC safe) and target ARM64/Termux/Linux.
"""

VERSION = "0.1.0"
