"""Generate trilingual (EN/DE/ES) lesson content for all 50 Qapilo units.

Runs Claude (via Emergent LLM key) once per unit, validates the JSON, and writes
incrementally to curriculum_data.json so it is fully resumable. Safe to re-run.

Usage:  python generate_curriculum.py
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
OUT = ROOT / "curriculum_data.json"

CARDS_PER_LESSON = 3
Q_PER_LESSON = 4


def build_prompt(unit):
    lessons_desc = "\n".join(
        f'  Lesson {i+1} (id {l["id"]}): "{l["title"]}" — {l["focus"]}'
        for i, l in enumerate(unit["lessons"])
    )
    return f"""You are writing content for a Duolingo-style stock-investing learning app.

UNIT: "{unit['title']}" — {unit['subtitle']}
DIFFICULTY (follow strictly): {unit['difficulty']}

Write the 3 lessons below. For EACH lesson produce:
- exactly {CARDS_PER_LESSON} teaching cards (each: short "heading" 2-5 words, "body" 1-2 clear sentences)
- exactly {Q_PER_LESSON} multiple-choice questions (each: "q", "options" = EXACTLY 4 options, "answer" = index 0-3 of the correct option, "explain" = one short sentence why)

Lessons:
{lessons_desc}

Produce the SAME content in three languages: English (en), German (de), Spanish (es).
CRITICAL: keep the option ORDER identical across all three languages so the answer index is valid for all. Include "answer" only in the English version.
Also translate the unit title and subtitle into German and Spanish.

Return ONLY valid minified JSON, no markdown, with this EXACT shape:
{{"unit":{{"de":{{"title":"","subtitle":""}},"es":{{"title":"","subtitle":""}}}},"lessons":[{{"en":{{"title":"","cards":[{{"heading":"","body":""}}],"questions":[{{"q":"","options":["","","",""],"answer":0,"explain":""}}]}},"de":{{"title":"","cards":[{{"heading":"","body":""}}],"questions":[{{"q":"","options":["","","",""],"explain":""}}]}},"es":{{"title":"","cards":[{{"heading":"","body":""}}],"questions":[{{"q":"","options":["","","",""],"explain":""}}]}}}}]}}
The "lessons" array must have exactly 3 items in the same order as listed above."""


def extract_json(text):
    a = text.find("{")
    b = text.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("no json braces")
    return json.loads(text[a:b + 1])


def validate(data, unit):
    assert "unit" in data and "de" in data["unit"] and "es" in data["unit"]
    for lg in ("de", "es"):
        assert data["unit"][lg].get("title") and data["unit"][lg].get("subtitle")
    lessons = data["lessons"]
    assert len(lessons) == len(unit["lessons"]), f"lesson count {len(lessons)}"
    for lesson in lessons:
        for lg in ("en", "de", "es"):
            L = lesson[lg]
            assert L.get("title")
            assert len(L["cards"]) == CARDS_PER_LESSON, f"cards {len(L['cards'])}"
            assert len(L["questions"]) == Q_PER_LESSON, f"q {len(L['questions'])}"
            for c in L["cards"]:
                assert c.get("heading") and c.get("body")
            for q in L["questions"]:
                assert q.get("q") and len(q["options"]) == 4 and all(q["options"])
                assert q.get("explain")
        ans = lesson["en"]["questions"]
        for q in ans:
            assert isinstance(q["answer"], int) and 0 <= q["answer"] <= 3
    return True


async def gen_unit(unit, attempt=1):
    chat = LlmChat(
        api_key=KEY,
        session_id=f"gen_{unit['id']}_{attempt}",
        system_message="You are a precise curriculum author that outputs only strict JSON.",
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
    sem = asyncio.Semaphore(6)  # concurrent Claude calls

    async def worker(unit):
        async with sem:
            for attempt in range(1, 4):
                try:
                    data = await gen_unit(unit, attempt)
                    async with lock:
                        store[unit["id"]] = data
                        OUT.write_text(json.dumps(store, ensure_ascii=False))
                        print(f"OK {unit['id']} ({unit['title']}) [{len(store)}/50]", flush=True)
                    return
                except Exception as e:
                    print(f"RETRY {unit['id']} attempt {attempt}: {e}", flush=True)
                    await asyncio.sleep(2)
            print(f"FAILED {unit['id']} after 3 attempts", flush=True)

    await asyncio.gather(*[worker(u) for u in todo])
    print(f"DONE. {len(store)}/50 units generated.", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
