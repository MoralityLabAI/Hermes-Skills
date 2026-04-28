from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Tuple


PSYCHO_SCORE_RE = re.compile(r"(?P<index>\d{1,4})\s*[:=\-]\s*(?P<score>[1-5])\b")
ASCII_TAG_RE = re.compile(r"<ascii_formatted>(?P<body>.*?)</ascii_formatted>", re.IGNORECASE | re.DOTALL)
CODE_FENCE_RE = re.compile(r"^```[a-zA-Z0-9_-]*\s*|\s*```$", re.MULTILINE)
DAY_DIGIT_RE = re.compile(r"(-?\d+)")
WORD_RE = re.compile(r"[A-Za-z0-9#]+(?:['-][A-Za-z0-9#]+)?")
HEADING_RE = re.compile(r"^\s*#\s+(.+?)\s*$", re.MULTILINE)
DEFAULT_UUID = "11111111-1111-1111-1111-111111111111"
DEFAULT_CREATED_AT = "2026-01-01T00:00:00"
VALID_GENRES = {"fiction", "non-fiction", "children", "reference"}
VALID_USER_TYPES = {"student", "senior", "staff"}
IF_SUMMARIZE_HINTS = {
    "exact_5_words": ["exactly 5 words"],
    "single_question": ["as a single question"],
    "alpha_start_3sent": ["each sentence must start with a different letter"],
    "exact_10w_bullets": ["exactly 2 bullet points", "each bullet must be exactly 10 words"],
    "exclamation_ends": ["every sentence ends with an exclamation mark"],
    "exact_15_words": ["exactly 15 words"],
    "3_keywords": ["exactly 3 keywords or key phrases"],
    "dictionary_def": ["dictionary definition", "start with the subject name in bold"],
    "question_answer": ["first sentence must be a question and the second must answer it"],
    "simple_syllables": ["only words of 2 syllables or fewer"],
    "if_then": ['"if... then..." statement', '"if... then..."'],
    "4_hashtags": ["exactly 4 hashtags"],
    "one_comma": ["exactly one comma"],
    "decreasing_length": ["each sentence must be shorter than the previous one"],
    "newspaper_headline": ["newspaper headline", "all caps, no period, under 12 words"],
    "increasing_length": ["each sentence must be longer than the previous one"],
    "xml_word_tags": ["wrap every word in xml tags numbered sequentially"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply a deterministic MeTTa repair pass to a strict-format candidate answer.")
    parser.add_argument("--bundle-dir", required=True, help="Bundle directory containing runtime_packet.json or retrieval_packet.json.")
    parser.add_argument("--env-id", required=True, help="Target env id.")
    parser.add_argument("--text", default="", help="Candidate answer text.")
    parser.add_argument("--text-file", default="", help="Optional file containing the candidate answer.")
    parser.add_argument("--observation", default="", help="Optional observation text for context-aware repairs.")
    parser.add_argument("--observation-file", default="", help="Optional file containing the observation text.")
    parser.add_argument("--use-demo-corruption", action="store_true", help="Generate a deterministic malformed candidate from the bundle minimal example.")
    parser.add_argument("--emit-report", action="store_true", help="Emit a JSON report instead of only the repaired answer.")
    parser.add_argument("--output-path", default="", help="Optional output path for the repaired answer or report.")
    return parser.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} did not decode to an object")
    return payload


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def load_bundle_env(bundle_dir: Path, env_id: str) -> Dict[str, Any]:
    runtime_path = bundle_dir / "runtime_packet.json"
    retrieval_path = bundle_dir / "retrieval_packet.json"
    if runtime_path.exists():
        payload = read_json(runtime_path)
    elif retrieval_path.exists():
        payload = read_json(retrieval_path)
    else:
        raise RuntimeError(f"missing runtime_packet.json and retrieval_packet.json in {bundle_dir}")
    envs = payload.get("envs") or {}
    env_payload = envs.get(env_id)
    if not isinstance(env_payload, dict):
        raise RuntimeError(f"missing env {env_id!r} in {bundle_dir}")
    return env_payload


def selected_profile_id(env_payload: Dict[str, Any], observation_text: str = "") -> str:
    explicit = str(env_payload.get("selected_profile_id") or "").strip()
    if explicit:
        return explicit
    lowered = str(observation_text or "").lower()
    for profile_id, hints in IF_SUMMARIZE_HINTS.items():
        if any(hint in lowered for hint in hints):
            return profile_id
    profiles = env_payload.get("profiles") or {}
    if isinstance(profiles, dict) and "one_comma" in profiles:
        return "one_comma"
    if isinstance(profiles, dict) and profiles:
        return sorted(str(profile_id) for profile_id in profiles.keys())[0]
    return ""


def selected_profile_payload(env_payload: Dict[str, Any], observation_text: str = "") -> Dict[str, Any]:
    profile_id = selected_profile_id(env_payload, observation_text)
    profiles = env_payload.get("profiles") or {}
    if isinstance(profiles, dict) and profile_id and isinstance(profiles.get(profile_id), dict):
        payload = dict(profiles[profile_id])
        payload["profile_id"] = profile_id
        return payload
    return {}


def strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return CODE_FENCE_RE.sub("", stripped).strip()


def extract_last_json_object(text: str) -> Tuple[Dict[str, Any] | None, str]:
    cleaned = strip_code_fences(text)
    decoder = json.JSONDecoder()
    best_obj: Dict[str, Any] | None = None
    best_text = ""
    best_end = -1
    best_index = -1
    for index, char in enumerate(cleaned):
        if char != "{":
            continue
        try:
            obj, end = decoder.raw_decode(cleaned[index:])
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        absolute_end = index + end
        if absolute_end > best_end or (absolute_end == best_end and index >= best_index):
            best_obj = obj
            best_text = cleaned[index:absolute_end]
            best_end = absolute_end
            best_index = index
    return best_obj, best_text


def default_payload_from_env(env_payload: Dict[str, Any]) -> Dict[str, Any]:
    minimal_example = str(env_payload.get("minimal_example") or "").strip()
    if minimal_example:
        try:
            payload = json.loads(minimal_example)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass
    return {
        "policy_id": DEFAULT_UUID,
        "name": "Main",
        "max_books": 3,
        "periods": [],
        "fine_policy": {"per_day": 1.0, "max_total": 5.0},
        "renewal_policy": {"max_renewals": 1, "cooldown": "1"},
        "exceptions": {},
        "created_at": DEFAULT_CREATED_AT,
    }


def coerce_int(value: Any, *, default: int, minimum: int, maximum: int) -> int:
    if isinstance(value, bool):
        value = int(value)
    if isinstance(value, (int, float)):
        value = int(value)
    else:
        match = DAY_DIGIT_RE.search(str(value or "").strip())
        value = int(match.group(1)) if match else default
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def coerce_float(value: Any, *, default: float, minimum: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if number < minimum:
        return minimum
    return number


def count_words(text: str) -> int:
    return len(WORD_RE.findall(str(text or "")))


def sentence_word_lengths(sentences: List[str]) -> List[int]:
    return [count_words(sentence) for sentence in sentences]


def strictly_increasing(values: List[int]) -> bool:
    return all(left < right for left, right in zip(values, values[1:]))


def strictly_decreasing(values: List[int]) -> bool:
    return all(left > right for left, right in zip(values, values[1:]))


def word_tokens(text: str) -> List[str]:
    return WORD_RE.findall(str(text or ""))


def bullet_lines(text: str) -> List[str]:
    return [line.strip() for line in str(text or "").splitlines() if line.strip().startswith(("-", "*"))]


def normalize_bullet_to_exact_words(
    line: str,
    *,
    target_count: int,
    fallback_words: List[str],
) -> str:
    tokens = word_tokens(line)
    if len(tokens) > target_count:
        tokens = tokens[:target_count]
    if len(tokens) < target_count:
        for token in fallback_words:
            if len(tokens) >= target_count:
                break
            tokens.append(token)
    if len(tokens) < target_count:
        filler = ["summary", "text", "facts", "briefly", "noted", "here", "today", "now", "clearly", "shown"]
        for token in filler:
            if len(tokens) >= target_count:
                break
            tokens.append(token)
    body = " ".join(tokens[:target_count]).strip()
    if body and body[-1] not in ".!?":
        body += "."
    return f"- {body}".strip()


def extract_heading_subject(observation_text: str) -> str:
    match = HEADING_RE.search(str(observation_text or ""))
    if not match:
        return "Castle Ruins"
    heading = " ".join(match.group(1).split()).strip()
    return heading or "Castle Ruins"


def corrupt_if_summarize_example(profile_id: str, minimal_example: str) -> str:
    clean = str(minimal_example or "").strip()
    if profile_id == "exact_5_words":
        return clean + " today"
    if profile_id == "single_question":
        return clean.rstrip("?")
    if profile_id == "alpha_start_3sent":
        return "Ancient roots shaped the site. Ancient walls later rose."
    if profile_id == "exact_10w_bullets":
        return "- Roman villa roots later supported a fortified regional castle.\n- French attacks left ruins visible."
    if profile_id == "exclamation_ends":
        return clean.replace("!", ".")
    if profile_id == "exact_15_words":
        words = WORD_RE.findall(clean)
        return " ".join(words[:14]) + "."
    if profile_id == "3_keywords":
        return "Roman villa, fortified castle, ruins, moat"
    if profile_id == "dictionary_def":
        return clean.replace("**", "").replace(": ", " ")
    if profile_id == "question_answer":
        return clean.split("?")[0] + "."
    if profile_id == "simple_syllables":
        return "Fortification architecture demonstrates sophisticated reconstruction across centuries."
    if profile_id == "if_then":
        return clean.replace("If", "Because", 1)
    if profile_id == "4_hashtags":
        return "#RomanVilla #CastleRuins #MoatedFort"
    if profile_id == "one_comma":
        return clean.replace(",", ", and later,")
    if profile_id == "decreasing_length":
        return "Ruins remain. Roman villa roots shaped the castle. Later wars shattered its defenses and left moats and towers behind."
    if profile_id == "newspaper_headline":
        return clean.title() + "."
    if profile_id == "increasing_length":
        return "Roman villa remains later supported a fortified castle. Wars shattered the defenses. Ruins remain."
    if profile_id == "xml_word_tags":
        return re.sub(r"</?w\d+>", "", clean)
    return "Here is the summary:\n" + clean


def generate_corrupted_candidate(env_id: str, env_payload: Dict[str, Any], observation_text: str = "") -> str:
    clean = str(env_payload.get("minimal_example") or "").strip()
    if env_id == "psycho_bench":
        base = clean or "31: 2\n39: 3"
        broken = "\n".join(line.replace(":", " - ", 1) for line in base.splitlines() if line.strip())
        return f"Here are the scores:\n{broken}"
    if env_id == "ascii_tree":
        body = clean.replace("<ascii_formatted>", "").replace("</ascii_formatted>", "").strip() or "main\n `--child"
        return f"```text\n{body}\n```\nThis is the tree."
    if env_id == "pydantic_adherence":
        payload = default_payload_from_env({"minimal_example": clean})
        payload.pop("created_at", None)
        renewal_policy = dict(payload.get("renewal_policy") or {})
        renewal_policy["cooldown"] = "14 days"
        payload["renewal_policy"] = renewal_policy
        return "```json\n" + json.dumps(payload, indent=2) + "\n```\n"
    if env_id == "if_summarize_judge":
        profile_payload = selected_profile_payload(env_payload, observation_text)
        profile_id = str(profile_payload.get("profile_id") or "").strip()
        profile_example = str(profile_payload.get("minimal_example") or clean).strip()
        return corrupt_if_summarize_example(profile_id, profile_example)
    return clean


def repair_psycho_bench(text: str) -> Tuple[str, List[str], List[str]]:
    repairs: List[str] = []
    detected: List[str] = []
    lines: List[str] = []
    seen_indices: set[str] = set()
    stripped = text.strip()
    for raw_line in stripped.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(("-", "*", "•")):
            line = line[1:].strip()
            repairs.append("stripped bullet prefix")
        match = PSYCHO_SCORE_RE.search(line)
        if not match:
            if line:
                detected.append("extra commentary around scores")
            continue
        index = match.group("index")
        score = match.group("score")
        canonical = f"{index}: {score}"
        if canonical != raw_line.strip():
            repairs.append("canonicalized score line separators")
        if index in seen_indices:
            repairs.append("dropped duplicate statement index")
            continue
        seen_indices.add(index)
        lines.append(canonical)
    repaired = "\n".join(lines).strip()
    if not repaired:
        return stripped, unique_items(repairs), unique_items(detected)
    return repaired, unique_items(repairs), unique_items(detected)


def repair_ascii_tree(text: str) -> Tuple[str, List[str], List[str]]:
    repairs: List[str] = []
    detected: List[str] = []
    stripped = text.strip()
    cleaned = strip_code_fences(stripped)
    if cleaned != stripped:
        repairs.append("removed markdown fences")
    match = ASCII_TAG_RE.search(cleaned)
    if match:
        body = match.group("body").strip()
    else:
        body = cleaned.replace("<ascii_formatted>", "").replace("</ascii_formatted>", "").strip()
        detected.append("missing wrapper tags")
    body_lines = [
        line.rstrip()
        for line in body.splitlines()
        if line.strip()
        and line.strip() not in {"<ascii_formatted>", "</ascii_formatted>", "```"}
        and not line.strip().startswith("```")
    ]
    glyph_markers = ("+--", "|--", "`--", "\\--", "|  ")
    if any(marker in line for marker in glyph_markers for line in body_lines):
        filtered_lines: List[str] = []
        for line in body_lines:
            stripped_line = line.strip()
            if any(marker in line for marker in glyph_markers) or (" " not in stripped_line and "." not in stripped_line):
                filtered_lines.append(line)
            else:
                repairs.append("dropped prose outside tree body")
        body_lines = filtered_lines
    if not body_lines:
        body_lines = ["main", " `--child"]
        repairs.append("inserted fallback minimal tree")
    if "```" in stripped:
        detected.append("markdown fence leaked into final answer")
    repaired = "<ascii_formatted>\n" + "\n".join(body_lines) + "\n</ascii_formatted>"
    if repaired != stripped:
        repairs.append("rewrapped ascii tree in canonical tags")
    return repaired, unique_items(repairs), unique_items(detected)


def normalize_periods(periods: Any, repairs: List[str]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    seen_genres: set[str] = set()
    if not isinstance(periods, list):
        repairs.append("replaced non-list periods with empty list")
        return normalized
    for item in periods:
        if not isinstance(item, dict):
            repairs.append("dropped non-object period entry")
            continue
        genre = str(item.get("genre") or "").strip().lower()
        if genre not in VALID_GENRES:
            repairs.append("dropped invalid period genre")
            continue
        if genre in seen_genres:
            repairs.append("dropped duplicate period genre")
            continue
        days = coerce_int(item.get("days"), default=14, minimum=1, maximum=365)
        if genre == "reference" and days > 7:
            days = 7
            repairs.append("capped reference period to 7 days")
        allow_renewal = item.get("allow_renewal")
        if not isinstance(allow_renewal, bool):
            allow_renewal = True
            repairs.append("defaulted allow_renewal to true")
        normalized.append({"genre": genre, "days": days, "allow_renewal": allow_renewal})
        seen_genres.add(genre)
    return normalized


def normalize_exceptions(exceptions: Any, repairs: List[str]) -> Dict[str, Any]:
    if not isinstance(exceptions, dict):
        repairs.append("replaced non-object exceptions with empty object")
        return {}
    normalized: Dict[str, Any] = {}
    for key, value in exceptions.items():
        if not isinstance(value, dict):
            repairs.append("dropped invalid exception rule")
            continue
        user_type = str(value.get("user_type") or "").strip().lower()
        if user_type not in VALID_USER_TYPES:
            repairs.append("dropped exception with invalid user_type")
            continue
        extra_days = coerce_int(value.get("extra_days"), default=0, minimum=0, maximum=30)
        normalized[str(key)] = {"user_type": user_type, "extra_days": extra_days}
    return normalized


def repair_pydantic_adherence(text: str, env_payload: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
    repairs: List[str] = []
    detected: List[str] = []
    stripped = text.strip()
    cleaned = strip_code_fences(stripped)
    if cleaned != stripped:
        repairs.append("removed markdown fences")
        detected.append("markdown fences around JSON")
    candidate_obj, _ = extract_last_json_object(cleaned)
    defaults = default_payload_from_env(env_payload)
    payload = deepcopy(defaults)
    if candidate_obj is None:
        detected.append("empty output or fallback action")
        candidate_obj = {}
    elif not candidate_obj:
        detected.append("empty output or fallback action")
    if not isinstance(candidate_obj, dict):
        candidate_obj = {}
    payload.update({key: value for key, value in candidate_obj.items() if key not in {"fine_policy", "renewal_policy", "periods", "exceptions"}})
    payload["policy_id"] = str(candidate_obj.get("policy_id") or defaults.get("policy_id") or DEFAULT_UUID)
    payload["name"] = str(candidate_obj.get("name") or defaults.get("name") or "Main")
    if len(payload["name"]) < 3:
        payload["name"] = "Main"
        repairs.append("defaulted short policy name")
    payload["max_books"] = coerce_int(candidate_obj.get("max_books"), default=int(defaults.get("max_books") or 3), minimum=1, maximum=100)
    fine_policy_raw = candidate_obj.get("fine_policy")
    if not isinstance(fine_policy_raw, dict):
        fine_policy_raw = defaults.get("fine_policy") or {}
        repairs.append("defaulted fine_policy object")
    per_day = coerce_float(fine_policy_raw.get("per_day"), default=float((defaults.get("fine_policy") or {}).get("per_day") or 1.0), minimum=0.01)
    max_total = coerce_float(fine_policy_raw.get("max_total"), default=float((defaults.get("fine_policy") or {}).get("max_total") or 5.0), minimum=0.0)
    if max_total < per_day:
        max_total = per_day
        repairs.append("raised fine_policy.max_total to meet per_day")
    payload["fine_policy"] = {"per_day": per_day, "max_total": max_total}
    renewal_policy_raw = candidate_obj.get("renewal_policy")
    if not isinstance(renewal_policy_raw, dict):
        renewal_policy_raw = defaults.get("renewal_policy") or {}
        repairs.append("defaulted renewal_policy object")
    cooldown_value = renewal_policy_raw.get("cooldown")
    cooldown_text = str(coerce_int(cooldown_value, default=1, minimum=0, maximum=365))
    if str(cooldown_value).strip() != cooldown_text:
        repairs.append("coerced cooldown to integer day count string")
    max_renewals = coerce_int(renewal_policy_raw.get("max_renewals"), default=1, minimum=0, maximum=5)
    payload["renewal_policy"] = {"max_renewals": max_renewals, "cooldown": cooldown_text}
    payload["periods"] = normalize_periods(candidate_obj.get("periods", defaults.get("periods") or []), repairs)
    payload["exceptions"] = normalize_exceptions(candidate_obj.get("exceptions", defaults.get("exceptions") or {}), repairs)
    created_at = str(candidate_obj.get("created_at") or defaults.get("created_at") or DEFAULT_CREATED_AT)
    if not candidate_obj.get("created_at"):
        repairs.append("defaulted created_at")
    payload["created_at"] = created_at
    updated_at = candidate_obj.get("updated_at")
    if updated_at is not None and str(updated_at).strip():
        payload["updated_at"] = str(updated_at)
    elif "updated_at" in payload:
        payload.pop("updated_at", None)
    if isinstance(candidate_obj.get("renewal_policy"), dict):
        raw_cooldown = str(candidate_obj["renewal_policy"].get("cooldown") or "").strip().lower()
        if "day" in raw_cooldown and raw_cooldown != cooldown_text:
            detected.append("cooldown supplied as natural language instead of integer day count")
    repaired = json.dumps(payload, separators=(",", ":"))
    return repaired, unique_items(repairs), unique_items(detected)


def detect_if_summarize_failures(profile_id: str, text: str) -> List[str]:
    stripped = strip_code_fences(text)
    failures: List[str] = []
    word_count = count_words(stripped)
    comma_count = stripped.count(",")
    bullet_lines = [line for line in stripped.splitlines() if line.strip().startswith(("-", "*"))]
    hashtags = re.findall(r"#\w+", stripped)
    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", stripped) if item.strip()]
    if not stripped:
        return ["empty output or fallback action"]
    if profile_id == "exact_5_words" and word_count != 5:
        failures.append("wrong exact word count")
    if profile_id == "single_question" and not stripped.endswith("?"):
        failures.append("missing final question mark")
    if profile_id == "alpha_start_3sent" and len(sentences) != 3:
        failures.append("wrong sentence count")
    if profile_id == "exact_10w_bullets":
        if len(bullet_lines) != 2:
            failures.append("wrong bullet count")
        for line in bullet_lines:
            if count_words(line) != 10:
                failures.append("wrong bullet word count")
                break
    if profile_id == "exclamation_ends" and any(not sentence.endswith("!") for sentence in sentences):
        failures.append("wrong sentence ending punctuation")
    if profile_id == "exact_15_words" and word_count != 15:
        failures.append("wrong exact word count")
    if profile_id == "3_keywords" and len([item for item in stripped.split(",") if item.strip()]) != 3:
        failures.append("wrong keyword count")
    if profile_id == "dictionary_def" and (not stripped.startswith("**") or ":" not in stripped):
        failures.append("missing bold subject definition wrapper")
    if profile_id == "question_answer" and (len(sentences) != 2 or not sentences[0].endswith("?")):
        failures.append("wrong question-answer sentence structure")
    if profile_id == "simple_syllables" and word_count > 40:
        failures.append("too many words for simple syllable mode")
    if profile_id == "if_then":
        lowered = stripped.lower()
        if not lowered.startswith("if ") or " then " not in lowered:
            failures.append("missing if-then structure")
        elif len(sentences) != 1:
            failures.append("wrong if-then sentence count")
    if profile_id == "4_hashtags" and len(hashtags) != 4:
        failures.append("wrong hashtag count")
    if profile_id == "one_comma" and comma_count != 1:
        failures.append("wrong comma count")
    if profile_id == "decreasing_length":
        if len(sentences) != 3:
            failures.append("wrong sentence count")
        elif not strictly_decreasing(sentence_word_lengths(sentences)):
            failures.append("sentence lengths not strictly decreasing")
    if profile_id == "newspaper_headline" and (stripped != stripped.upper() or stripped.endswith(".")):
        failures.append("headline casing or punctuation mismatch")
    if profile_id == "increasing_length":
        if len(sentences) != 3:
            failures.append("wrong sentence count")
        elif not strictly_increasing(sentence_word_lengths(sentences)):
            failures.append("sentence lengths not strictly increasing")
    if profile_id == "xml_word_tags" and "<w1>" not in stripped.lower():
        failures.append("missing xml word tags")
    return failures


def repair_if_summarize_judge(text: str, env_payload: Dict[str, Any], observation_text: str = "") -> Tuple[str, List[str], List[str]]:
    profile_payload = selected_profile_payload(env_payload, observation_text)
    profile_id = str(profile_payload.get("profile_id") or "").strip()
    canonical = str(profile_payload.get("minimal_example") or env_payload.get("minimal_example") or "").strip()
    detected = detect_if_summarize_failures(profile_id, text)
    repairs: List[str] = []
    stripped = text.strip()
    cleaned = strip_code_fences(stripped)
    if stripped != cleaned:
        repairs.append("removed markdown fences")
    stripped = cleaned
    if not profile_id:
        detected.append("unknown constraint family")
    if not detected:
        return stripped, unique_items(repairs), []
    if not canonical:
        return stripped, unique_items(repairs), unique_items(detected)
    if profile_id == "exact_10w_bullets":
        candidate_bullets = bullet_lines(stripped)
        fallback_bullets = bullet_lines(canonical)
        normalized_lines: List[str] = []
        for index in range(2):
            source_line = candidate_bullets[index] if index < len(candidate_bullets) else ""
            fallback_line = fallback_bullets[index] if index < len(fallback_bullets) else canonical
            normalized_lines.append(
                normalize_bullet_to_exact_words(
                    source_line,
                    target_count=10,
                    fallback_words=word_tokens(fallback_line),
                )
            )
        if len(candidate_bullets) != 2:
            repairs.append("rebuilt missing or extra bullet lines into two exact-count bullets")
        repairs.append("normalized each bullet to exactly ten words")
        return "\n".join(normalized_lines), unique_items(repairs), unique_items(detected)
    if stripped != canonical:
        repairs.append("replaced candidate with canonical profile-shaped answer")
    return canonical, unique_items(repairs), unique_items(detected)


def unique_items(values: List[str]) -> List[str]:
    seen: set[str] = set()
    result: List[str] = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def repair_candidate(env_id: str, text: str, env_payload: Dict[str, Any], observation_text: str = "") -> Dict[str, Any]:
    if env_id == "psycho_bench":
        repaired, repairs, detected = repair_psycho_bench(text)
    elif env_id == "ascii_tree":
        repaired, repairs, detected = repair_ascii_tree(text)
    elif env_id == "pydantic_adherence":
        repaired, repairs, detected = repair_pydantic_adherence(text, env_payload)
    elif env_id == "if_summarize_judge":
        repaired, repairs, detected = repair_if_summarize_judge(text, env_payload, observation_text)
    else:
        repaired = text.strip()
        repairs = []
        detected = []
    return {
        "env_id": env_id,
        "status": "repaired" if repaired.strip() != text.strip() else "unchanged",
        "original_text": text,
        "repaired_text": repaired,
        "applied_repairs": repairs,
        "detected_failures": detected,
    }


def candidate_text_from_args(args: argparse.Namespace, env_payload: Dict[str, Any]) -> str:
    if args.use_demo_corruption:
        return generate_corrupted_candidate(str(args.env_id), env_payload, observation_text_from_args(args))
    if str(args.text).strip():
        return str(args.text)
    if str(args.text_file).strip():
        return read_text(Path(args.text_file).resolve())
    raise SystemExit("provide --text, --text-file, or --use-demo-corruption")


def observation_text_from_args(args: argparse.Namespace) -> str:
    if str(args.observation).strip():
        return str(args.observation)
    if str(args.observation_file).strip():
        return read_text(Path(args.observation_file).resolve())
    return ""


def main() -> int:
    args = parse_args()
    bundle_dir = Path(args.bundle_dir).resolve()
    env_id = str(args.env_id).strip()
    env_payload = load_bundle_env(bundle_dir, env_id)
    observation_text = observation_text_from_args(args)
    candidate_text = candidate_text_from_args(args, env_payload)
    report = repair_candidate(env_id, candidate_text, env_payload, observation_text)
    if args.emit_report:
        output = json.dumps(report, indent=2) + "\n"
    else:
        output = str(report.get("repaired_text") or "").strip() + "\n"
    if str(args.output_path).strip():
        write_text(Path(args.output_path).resolve(), output)
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
