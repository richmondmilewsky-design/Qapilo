"""Generate DE/ES translations of the 200-unit curriculum TITLES only
(unit title + subtitle, and the 3 lesson titles per unit).

Cheap pass: short strings, one Claude call per unit, resumable. Writes to
curriculum_titles.json which curriculum.py loads to localize UNIT_T / LESSON_T
titles. Does NOT touch cards/quizzes (curriculum_data.json).

Usage:  python generate_titles.py
"""
import os
import json
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

from curriculum_blueprint import UNITS_SPEC

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")
KEY = os.environ.get("EMERGENT_LLM_KEY", "").strip()
MODEL = "claude-sonnet-4-6"
OUT = ROOT / "curriculum_titles.json"


def build_prompt(unit):
    lessons_desc = "\n".join(
        f'  {l["id"]}: "{l["title"]}"' for l in unit["lessons"]
    )
    return f"""Translate these short UI strings for a stock-investing learning app into German (de) and Spanish (es).
Keep them concise and natural, suitable for a mobile app title/label. Do NOT translate brand names, ticker symbols or acronyms (ETF, IPO, P/E, EPS, GDP, VIX, DCF, WACC, ESG, VC, PE, REIT, APR, RSI).

UNIT title: "{unit['title']}"
UNIT subtitle: "{unit['subtitle']}"
LESSON titles:
{lessons_desc}

Return ONLY valid minified JSON, no markdown, with this EXACT shape:
{{"unit":{{"de":{{"title":"","subtitle":""}},"es":{{"title":"","subtitle":""}}}},"lessons":{{{",".join(f'"{l["id"]}":{{"de":"","es":""}}' for l in unit["lessons"])}}}}}"""


def extract_json(text):
    a = text.find("{")
    b = text.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no json braces")
    return json.loads(text[a:b + 1])


def validate(data, unit):
    for lg in ("de", "es"):
        assert data["unit"][lg].get("title") and data["unit"][lg].get("subtitle")
    for l in unit["lessons"]:
        e = data["lessons"][l["id"]]
        assert e.get("de") and e.get("es"), f"missing lesson {l['id']}"
    return True


async def gen_unit(unit, attempt=1):
    chat = LlmChat(
        api_key=KEY,
        session_id=f"title_{unit['id']}_{attempt}",
        system_message="You are a precise translator that outputs only strict JSON.",
    ).with_model("anthropic", MODEL)
    reply = await chat.send_message(UserMessage(text=build_prompt(unit)))
    data = extract_json(reply)
    validate(data, unit)
    return data


async def main():
    if not KEY:
        raise SystemExit("EMERGENT_LLM_KEY not set")
    store = {}
    if OUT.exists():
        store = json.loads(OUT.read_text())
    print(f"Resuming with {len(store)} units already done.", flush=True)

    todo = [u for u in UNITS_SPEC if u["id"] not in store]
    lock = asyncio.Lock()
    sem = asyncio.Semaphore(6)

    async def worker(unit):
        async with sem:
            for attempt in range(1, 4):
                try:
                    data = await gen_unit(unit, attempt)
                    async with lock:
                        store[unit["id"]] = data
                        OUT.write_text(json.dumps(store, ensure_ascii=False))
                        print(f"OK {unit['id']} [{len(store)}/{len(UNITS_SPEC)}]", flush=True)
                    return
                except Exception as e:
                    print(f"RETRY {unit['id']} attempt {attempt}: {e}", flush=True)
                    await asyncio.sleep(2)
            print(f"FAILED {unit['id']} after 3 attempts", flush=True)

    await asyncio.gather(*[worker(u) for u in todo])
    print(f"DONE. {len(store)}/{len(UNITS_SPEC)} units translated.", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
