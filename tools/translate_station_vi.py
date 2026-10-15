#!/usr/bin/env python3
"""Translate the ORIGINAL station descriptions, by publisher IDs, without touching game logic.

Source: web/assets/station/station.json (read-only).
Output: web/assets/station/station-vi.json (translation overlay).
Helsinki-NLP/opus-mt-en-vi, offline inference after model download.
Machine translation requires editorial review of game terminology.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "web/assets/station/station.json"
DEST = ROOT / "web/assets/station/station-vi.json"
MODEL = "Helsinki-NLP/opus-mt-en-vi"
VI = re.compile(r"[À-ỹĐđ]")
ENGLISH_WORDS = re.compile(r"\b(the|their|which|against|damage|increases|enemies)\b", re.I)
NUMBER = re.compile(r"(?<!\w)\d+(?:[.,]\d+)?%?")
BREAK = re.compile(r"(?<=[.!?;])\s+")
GLOSSARY = {
    "House Ghost": "Nhà Linh Hồn",
    "House Human": "Nhà Nhân Loại",
    "House Monster": "Nhà Quái Vật",
    "House Fairy": "Nhà Tiên",
    "House Demon": "Nhà Ác Quỷ",
    "House Angel": "Nhà Thiên Thần",
}
EXPECTED_PROFILES = 105
EXPECTED_SKILLS = 417
REVIEW_WARNINGS = []


def source():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    girls = data["girls"]
    profiles = {str(cid): g["desc"] for cid, g in girls.items() if g.get("desc", "").strip()}
    skills = {(str(cid), str(skill["id"])): skill["desc"]
              for cid, g in girls.items() for skill in g.get("skills", [])
              if skill.get("desc", "").strip()}
    if len(profiles) != EXPECTED_PROFILES or len(skills) != EXPECTED_SKILLS:
        raise RuntimeError(
            f"Source changed: profiles={len(profiles)} skills={len(skills)}; "
            "review new publisher tables before translating."
        )
    return profiles, skills, hashlib.sha256(SOURCE.read_bytes()).hexdigest()


def segments(line: str, max_chars: int = 240) -> list[str]:
    if len(line) <= max_chars:
        return [line] if line.strip() else []
    sentences = BREAK.split(line.strip())
    result, buff = [], ""
    for sentence in sentences:
        pieces = []
        if len(sentence) > max_chars:
            cur = ""
            for word in sentence.split():
                if cur and len(cur) + len(word) + 1 > max_chars:
                    pieces.append(cur)
                    cur = ""
                cur = (cur + " " + word).strip()
            if cur:
                pieces.append(cur)
        else:
            pieces = [sentence]
        for piece in pieces:
            if buff and len(buff) + len(piece) + 1 > max_chars:
                result.append(buff)
                buff = ""
            buff = (buff + " " + piece).strip()
    if buff:
        result.append(buff)
    return result


def build_plan(profiles, skills):
    all_values = list(profiles.values()) + list(skills.values())
    plans, unique = {}, set()
    for value in all_values:
        parts = []
        for line in value.split("\n"):
            prefix = re.match(r"^(\s*(?:\d+[.)]\s*|[•*-]\s*))", line)
            mark = prefix.group(0) if prefix else ""
            payload = line[len(mark):].strip()
            chunks = segments(payload) if payload else []
            unique.update(chunks)
            parts.append((mark, chunks))
        plans[value] = parts
    return plans, sorted(unique)


def model_translate(chunks: list[str], batch: int) -> dict[str, str]:
    # Import heavyweight dependencies only for --apply, never for runtime or --verify.
    import torch
    from transformers import MarianMTModel, MarianTokenizer

    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))
    print(f"Loading {MODEL}; {len(chunks)} distinct text segments", flush=True)
    tokenizer = MarianTokenizer.from_pretrained(MODEL)
    model = MarianMTModel.from_pretrained(MODEL)
    model.eval()
    translated = {}
    for start in range(0, len(chunks), batch):
        group = chunks[start:start + batch]
        inputs = tokenizer(group, return_tensors="pt", padding=True,
                           truncation=True, max_length=380)
        with torch.inference_mode():
            tokens = model.generate(**inputs, max_new_tokens=380, num_beams=2)
        output = tokenizer.batch_decode(tokens, skip_special_tokens=True)
        for original, vietnamese in zip(group, output):
            text = vietnamese.strip()
            if not text or text == original:
                raise RuntimeError(f"Missing translation for: {original[:120]}")
            translated[original] = text
        if start == 0 or (start // batch + 1) % 20 == 0:
            print(f"Translated {min(start + batch, len(chunks))}/{len(chunks)} segments", flush=True)
    return translated


def render(value, plans, translated):
    result = []
    for prefix, chunks in plans[value]:
        if not chunks:
            result.append(prefix)
            continue
        translated_line = " ".join(translated[c] for c in chunks).strip()
        for src, target in GLOSSARY.items():
            translated_line = re.sub(re.escape(src), target, translated_line, flags=re.I)
        result.append(prefix + translated_line)
    text = "\n".join(result)
    if not text.strip():
        raise RuntimeError("Empty translated description")
    # Never mutate numeric quantities, damage multipliers, time, or percentage data.
    before, after = NUMBER.findall(value), NUMBER.findall(text)
    # Marian may spell 10 as "mười", 5 as "năm", etc. Restore the explicit
    # source numerals where unambiguous; flag anything still missing for QA.
    from collections import Counter
    numerals = {
        "1": ("một",), "2": ("hai",), "3": ("ba",),
        "4": ("bốn", "tư"), "5": ("năm",), "6": ("sáu",),
        "7": ("bảy",), "8": ("tám",), "9": ("chín",),
        "10": ("mười",), "12": ("mười hai",),
        "15": ("mười lăm",), "20": ("hai mươi",),
    }
    missing = Counter(before) - Counter(after)
    for num, needed in missing.items():
        if num not in numerals:
            continue
        for _ in range(needed):
            for word in numerals[num]:
                updated, changes = re.subn(
                    r"(?<!\w)" + re.escape(word) + r"(?!\w)", num,
                    text, count=1, flags=re.I)
                if changes:
                    text = updated
                    break
    after = NUMBER.findall(text)
    still_missing = Counter(before) - Counter(after)
    if still_missing:
        REVIEW_WARNINGS.append({
            "source": value[:160],
            "missing_numeric_tokens": list(still_missing.elements()),
        })
    if not VI.search(text):
        REVIEW_WARNINGS.append({"source": value[:160], "reason": "No Vietnamese diacritics detected"})
    return text


def verify():
    profiles, skills, digest = source()
    if not DEST.exists():
        raise RuntimeError("Translation file not generated")
    data = json.loads(DEST.read_text(encoding="utf-8"))
    if data.get("source_sha256") != digest:
        raise RuntimeError("Translation out of date: station source digest mismatch")
    got = data.get("girls", {})
    assert sum(bool(v.get("desc")) for v in got.values()) == EXPECTED_PROFILES
    assert sum(len(v.get("skills", {})) for v in got.values()) == EXPECTED_SKILLS
    for cid, original in profiles.items():
        target = got[cid]["desc"]
        if target == original or not target.strip():
            raise RuntimeError(f"Untranslated profile {cid}")
    for (cid, sid), original in skills.items():
        target = got[cid]["skills"][sid]
        if target == original or not target.strip():
            raise RuntimeError(f"Untranslated skill {cid}/{sid}")
    print(f"PASS | {len(profiles)} strategy profiles and {len(skills)} skill descriptions | source SHA256 {digest[:16]}", flush=True)
    return data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply", action="store_true")
    p.add_argument("--verify", action="store_true")
    p.add_argument("--batch-size", type=int, default=12)
    args = p.parse_args()
    profiles, skills, digest = source()
    print(f"Original publisher data: {len(profiles)} profiles; {len(skills)} skill descriptions", flush=True)
    if args.apply:
        plans, chunks = build_plan(profiles, skills)
        translated = model_translate(chunks, max(1, args.batch_size))
        girls = {}
        for cid, text in profiles.items():
            girls.setdefault(cid, {"desc": "", "skills": {}})["desc"] = render(text, plans, translated)
        for (cid, sid), text in skills.items():
            girls.setdefault(cid, {"desc": "", "skills": {}})["skills"][sid] = render(text, plans, translated)
        doc = {"source_sha256": digest, "generator": MODEL, "reviewed": False,
               "review_warnings": REVIEW_WARNINGS, "girls": girls}
        tmp = DEST.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(DEST)
        print(f"Created {DEST.relative_to(ROOT)} ({DEST.stat().st_size} bytes); "
              f"{len(REVIEW_WARNINGS)} items flagged for editorial review", flush=True)
    if args.verify:
        verify()


if __name__ == "__main__":
    main()
