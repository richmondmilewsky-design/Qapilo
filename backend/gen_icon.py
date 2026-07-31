"""One-off: generate the Qapilo app icon via Gemini Nano Banana and build
the Expo asset variants (icon / adaptive-icon / splash / favicon)."""
import asyncio
import os
import base64
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv(Path(__file__).parent / ".env")

ASSETS = Path(__file__).parent.parent / "frontend" / "assets" / "images"
RAW = Path(__file__).parent / "qapilo_icon_raw.png"

PROMPT = (
    "A modern, minimal fintech mobile app icon, perfectly square. "
    "CRITICAL: the emerald green gradient background (deep green to bright emerald) must "
    "completely fill the ENTIRE square canvas, edge to edge, all the way into all four "
    "corners. Do NOT draw rounded corners. Do NOT add any white, light, or transparent "
    "border, margin, frame or padding around the artwork — it must be full-bleed. "
    "Centered in the foreground, a clean, bold, geometric letter 'Q' that seamlessly "
    "integrates a rising stock market line chart with an upward arrow forming part of the "
    "letter, in crisp white with a subtle mint highlight. "
    "Flat vector style, high contrast, no text, no words, no letters other than the Q motif, "
    "premium, professional, clean, centered composition, 1024x1024."
)


async def main():
    api_key = os.getenv("EMERGENT_LLM_KEY")
    chat = LlmChat(api_key=api_key, session_id="qapilo-icon-gen",
                   system_message="You are a professional app icon designer.")
    chat.with_model("gemini", "gemini-3.1-flash-image-preview").with_params(
        modalities=["image", "text"]
    )
    text, images = await chat.send_message_multimodal_response(UserMessage(text=PROMPT))
    print("text:", (text or "")[:80])
    if not images:
        raise SystemExit("No image returned")
    image_bytes = base64.b64decode(images[0]["data"])
    RAW.write_bytes(image_bytes)
    print("raw saved", RAW, len(image_bytes), "bytes")

    src = Image.open(RAW).convert("RGBA")
    # Square-crop centered just in case
    w, h = src.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    src = src.crop((left, top, left + side, top + side))

    icon = src.resize((1024, 1024), Image.LANCZOS)
    icon.save(ASSETS / "icon.png")
    icon.save(ASSETS / "adaptive-icon.png")
    icon.resize((512, 512), Image.LANCZOS).save(ASSETS / "favicon.png")
    icon.save(ASSETS / "splash-image.png")
    print("assets written to", ASSETS)


if __name__ == "__main__":
    asyncio.run(main())
