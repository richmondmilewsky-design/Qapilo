"""Fallback generator for units that failed bulk generation: generates each
lesson separately (smaller JSON = reliable parsing) and assembles the unit."""
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
OUT = ROOT / "curriculum_data.json"
SPEC = {u["id"]: u for u in UNITS_SPEC}


def extract_json(text):
    a = text.find("{")
    obj, _ = json.JSONDecoder().raw_decode(text[a:])
    return obj


async def gen_lesson(unit, lspec):
    prompt = f"""Write ONE lesson for a stock-investing app.
DIFFICULTY: {unit['difficulty']}
Lesson title: "{lspec['title']}" — {lspec['focus']}

Produce exactly 3 teaching cards (heading 2-5 words, body 1-2 sentences) and exactly 4 multiple-choice questions (q, options=EXACTLY 4, answer index 0-3, explain=1 short sentence), in English (en), German (de) and Spanish (es). Keep option ORDER identical across languages; include "answer" only in english.
Return ONLY strict minified JSON:
{{"en":{{"title":"","cards":[{{"heading":"","body":""}}],"questions":[{{"q":"","options":["","","",""],"answer":0,"explain":""}}]}},"de":{{"title":"","cards":[{{"heading":"","body":""}}],"questions":[{{"q":"","options":["","","",""],"explain":""}}]}},"es":{{"title":"","cards":[{{"heading":"","body":""}}],"questions":[{{"q":"","options":["","","",""],"explain":""}}]}}}}"""
    chat = LlmChat(api_key=KEY, session_id=f"lg_{lspec['id']}",
                   system_message="You output only strict JSON.").with_model("anthropic", MODEL)
    reply = await chat.send_message(UserMessage(text=prompt))
    d = extract_json(reply)
    for lg in ("en", "de", "es"):
        assert len(d[lg]["cards"]) == 3 and len(d[lg]["questions"]) == 4
    return d


async def gen_unit_titles(unit):
    prompt = (f'Translate this app unit title and subtitle to German and Spanish. '
              f'Title: "{unit["title"]}". Subtitle: "{unit["subtitle"]}". '
              'Return ONLY JSON: {"de":{"title":"","subtitle":""},"es":{"title":"","subtitle":""}}')
    chat = LlmChat(api_key=KEY, session_id=f"ut_{unit['id']}",
                   system_message="You output only strict JSON.").with_model("anthropic", MODEL)
    reply = await chat.send_message(UserMessage(text=prompt))
    return extract_json(reply)


async def build_unit(uid):
    unit = SPEC[uid]
    titles = await gen_unit_titles(unit)
    lessons = []
    for lspec in unit["lessons"]:
        for attempt in range(3):
            try:
                lessons.append(await gen_lesson(unit, lspec))
                break
            except Exception as e:
                print(f"  {lspec['id']} retry {attempt}: {e}", flush=True)
                await asyncio.sleep(1)
    return {"unit": titles, "lessons": lessons}


async def main():
    store = json.loads(OUT.read_text()) if OUT.exists() else {}
    missing = [u["id"] for u in UNITS_SPEC if u["id"] not in store]
    print("missing:", missing, flush=True)
    for uid in missing:
        data = await build_unit(uid)
        if len(data["lessons"]) == len(SPEC[uid]["lessons"]):
            store[uid] = data
            OUT.write_text(json.dumps(store, ensure_ascii=False))
            print(f"OK {uid} [{len(store)}/50]", flush=True)
        else:
            print(f"INCOMPLETE {uid}: {len(data['lessons'])} lessons", flush=True)
    print(f"DONE {len(store)}/50", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
