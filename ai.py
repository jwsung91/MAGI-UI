"""Drop-in replacement for TomaszRewak/MAGI's ai.py that reads MAGI skill results.

The original ai.py calls OpenAI. This module keeps the same function names, so the
original layout (main.py) and graphics (components/*.js, assets/style.css) stay
untouched; only the data source changes.

Type a result file path into the question field and press Enter. Leave it empty or
type "latest" to load the newest *.json in MAGI_RESULTS_DIR (default: ./results).

Result format: version 2 of the MAGI skill's result.schema.json
(https://github.com/jwsung91/MAGI/blob/main/skills/magi/result.schema.json).
"""

import json
import os
from pathlib import Path

RESULTS_DIR = Path(os.getenv("MAGI_RESULTS_DIR", "results"))
LANG = os.getenv("MAGI_UI_LANG", "en").lower()

UNIT_KEYS = ("melchior", "balthasar", "casper")
UNIT_LABELS = {"melchior": "MELCHIOR-1", "balthasar": "BALTHASAR-2", "casper": "CASPER-3"}

# Units are identified by the personality strings in the original main.py.
PERSONALITY_KEYWORDS = {"scientist": "melchior", "mother": "balthasar", "woman": "casper"}

MODES = ("deliberation", "information")
GRADES = ("normal", "critical")
UNIT_VERDICTS = ("approve", "reject", "error")
VERDICTS = ("passed", "rejected", "on_hold", "error")

UNIT_VERDICT_TO_STATUS = {"approve": "yes", "reject": "no"}

# Result panel statuses of the original screen: yes, no, info, error.
# "On hold" has no label of its own, so it is shown as info and the modal says so.
VERDICT_TO_STATUS = {"passed": "yes", "rejected": "no", "on_hold": "info", "error": "error"}

# Text shown in the unit modal. JSON values are language-neutral; only the labels change.
TEXT = {
    "en": {
        "approve": "approve", "reject": "reject",
        "high": "high", "medium": "medium", "low": "low",
        "verdict": "[verdict]", "rationale": "[rationale]", "premise": "[doubted premise]",
        "recommend": "[recommendation]", "answer": "[answer]", "confidence": "confidence",
        "hold_note": "* Skill resolution: on hold (no matching screen label, shown as info)",
        "majority_note": "* Skill resolution: passed by {n}/3 majority (shown as passed even with a rejecting unit)",
        "not_found": "Result file not found: {q}",
        "empty_dir": "No result files (*.json) in {d}",
        "json_error": "JSON error ({f}): {e}",
        "format_error": "Result format error: {m}",
        "unknown_unit": "Cannot identify the unit (check the personality string)",
        "unit_error": "{u} error",
    },
    "ko": {
        "approve": "승인", "reject": "거부",
        "high": "높음", "medium": "중간", "low": "낮음",
        "verdict": "[판정]", "rationale": "[근거]", "premise": "[의심하는 전제]",
        "recommend": "[권고]", "answer": "[답]", "confidence": "확신도",
        "hold_note": "※ 결의 기준은 MAGI 스킬: 보류 (대응하는 화면 라벨이 없어 정보로 표시)",
        "majority_note": "※ 결의 기준은 MAGI 스킬: {n}/3 다수결 가결 (거부 패널이 있어도 가결로 표시)",
        "not_found": "결과 파일을 찾을 수 없습니다: {q}",
        "empty_dir": "{d} 에 결과 파일(*.json)이 없습니다.",
        "json_error": "JSON 형식 오류({f}): {e}",
        "format_error": "결과 형식 오류: {m}",
        "unknown_unit": "유닛을 식별할 수 없습니다(personality 문자열 확인)",
        "unit_error": "{u} 오류",
    },
}
T = TEXT.get(LANG, TEXT["en"])


class ResultError(Exception):
    """Result file missing or malformed."""


# ---------------------------------------------------------------- reading files

def resolve_path(query: str) -> Path:
    text = (query or "").strip()
    if text and text.lower() != "latest":
        candidate = Path(text).expanduser()
        for path in (candidate, RESULTS_DIR / candidate):
            if path.is_file():
                return path
        raise ResultError(T["not_found"].format(q=text))

    files = sorted(RESULTS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise ResultError(T["empty_dir"].format(d=RESULTS_DIR.resolve()))
    return files[0]


def load_result(query: str) -> dict:
    path = resolve_path(query)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ResultError(T["json_error"].format(f=path.name, e=e)) from e
    validate(data)
    data["_source"] = path.name
    return data


def validate(data: dict) -> None:
    """Checks the core rules of result.schema.json without extra dependencies."""
    def fail(msg):
        raise ResultError(T["format_error"].format(m=msg))

    if not isinstance(data, dict):
        fail("top level is not an object")
    if data.get("version") != 2:
        fail("version must be 2 (update the skill or this viewer)")
    if data.get("mode") not in MODES:
        fail(f"mode must be one of {MODES}")
    if not isinstance(data.get("agenda"), str) or not data["agenda"].strip():
        fail("agenda is empty")

    units = data.get("units")
    if not isinstance(units, dict) or set(units) != set(UNIT_KEYS):
        fail(f"units must contain exactly {UNIT_KEYS}")

    if data["mode"] == "deliberation":
        if data.get("grade") not in GRADES:
            fail(f"grade must be one of {GRADES}")
        if data.get("verdict") not in VERDICTS:
            fail(f"verdict must be one of {VERDICTS}")
        for key in UNIT_KEYS:
            if units[key].get("verdict") not in UNIT_VERDICTS:
                fail(f"units.{key}.verdict must be one of {UNIT_VERDICTS}")
    else:
        for key in UNIT_KEYS:
            if not isinstance(units[key].get("answer"), str):
                fail(f"units.{key}.answer is required in information mode")


def unit_key(personality: str) -> str:
    lowered = (personality or "").lower()
    for word, key in PERSONALITY_KEYWORDS.items():
        if word in lowered:
            return key
    raise ResultError(T["unknown_unit"])


# ---------------------------------------------------------------- modal text
# The original CSS (.modal-body) sets no white-space rule, so line breaks collapse.
# To leave the graphics untouched, the modal text reads well on one line:
# each item gets a [label], items are separated by ║, values inside an item by ·.
# The full resolution (debate, minority opinion, follow-ups) is in the skill's Markdown output.

SECTION = "   ║   "
ITEM = " · "


def _join(items):
    return ITEM.join(str(i) for i in items if i)


def verdict_note(data: dict) -> str:
    """A one-line note, only for the two cases the screen label alone would misrepresent."""
    if data["mode"] != "deliberation":
        return ""
    if data["verdict"] == "on_hold":
        return T["hold_note"]
    if data["verdict"] == "passed" and data.get("approve_count", 3) < 3:
        return T["majority_note"].format(n=data["approve_count"])
    return ""


def unit_text(data: dict, key: str) -> str:
    """The unit modal shows only that unit's opinion."""
    unit = data["units"][key]
    persp = f" ({unit['perspective']})" if unit.get("perspective") else ""
    if data["mode"] == "information":
        sections = [f"{T['answer']}{persp} {unit['answer']}"]
    else:
        conf = f"{T['confidence']} {T.get(unit.get('confidence'), unit.get('confidence'))}" if unit.get("confidence") else ""
        sections = [f"{T['verdict']} " + _join([T.get(unit["verdict"], unit["verdict"]), conf]) + persp]
        if unit.get("rationale"):
            sections.append(f"{T['rationale']} " + _join(unit["rationale"]))
        if unit.get("doubted_premise"):
            sections.append(f"{T['premise']} {unit['doubted_premise']}")
        if unit.get("recommendations"):
            sections.append(f"{T['recommend']} " + _join(unit["recommendations"]))
    note = verdict_note(data)
    if note:
        sections.append(note)
    return SECTION.join(sections)


# ---------------------------------------------------------------- same interface as the original ai.py

def is_yes_or_no_question(question: str, key: str = None) -> bool:
    return load_result(question)["mode"] == "deliberation"


def get_answer(question: str, personality: str, key: str = None) -> str:
    data = load_result(question)
    k = unit_key(personality)
    if data["units"][k].get("verdict") == "error":
        raise ResultError(data["units"][k].get("error") or T["unit_error"].format(u=UNIT_LABELS[k]))
    return unit_text(data, k)


def classify_answer(question: str, personality: str, answer: str, key: str = None) -> dict:
    data = load_result(question)
    unit = data["units"][unit_key(personality)]
    return {"status": UNIT_VERDICT_TO_STATUS[unit["verdict"]], "conditions": None}


# ---------------------------------------------------------------- used by main.py.patch

def get_verdict(question: str) -> str:
    """Result panel status: the skill's resolution instead of the original 'any no means no' rule."""
    data = load_result(question)
    if data["mode"] == "information":
        return "info"
    return VERDICT_TO_STATUS[data["verdict"]]


def display_query(question: str) -> str:
    """Show the proposal text in the modal's question row instead of the file path."""
    try:
        data = load_result(question)
    except ResultError as e:
        return f"{question} ({e})"
    return f"{data['agenda']}  [{data['_source']}]"
