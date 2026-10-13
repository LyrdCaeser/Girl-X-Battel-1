#!/usr/bin/env python3
"""Offline English -> Vietnamese dialogue migration. Never changes gameplay keys or IDs.

Uses Helsinki-NLP/opus-mt-en-vi (Apache-2.0). Run on a PC or GitHub Actions,
NOT on the memory-limited production VPS. Machine translations need editorial QA.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "Helsinki-NLP/opus-mt-en-vi"
SPECS = {
    "data/story.json": ("story",),
    "data/partner_plot.json": ("plot",),
    "web/assets/girl-details.json": ("quotes",),
}
VIET = re.compile(r"[À-ỹĐđ]")
LATIN = re.compile(r"[A-Za-z]")
MARKUP = re.compile(r"(\{[^{}]+\}|\[[^\[\]]+\]|<[^<>]+>|\n)")
GLOSSARY = {
    "Yes": "Có", "No": "Không", "OK": "Đồng ý", "Cancel": "Hủy",
    "Next": "Tiếp theo", "Back": "Quay lại", "Skip": "Bỏ qua",
    "Victory": "Chiến thắng", "Defeat": "Thất bại",
    "Opening Ceremony": "Lễ Khai Giảng", "Newbies": "Tân Sinh",
    "House Human": "Nhà Nhân Loại", "Chapter 1": "Chương 1",
    "Chapter 2": "Chương 2", "Chapter 3": "Chương 3",
}
EXCLUDE = {"Gambler", "Saint", "Joan", "Zombia", "Miya", "Nun", "Yume", "Senpai"}
VIET_LEXEMES = re.compile(r"\b(tôi|cậu|bạn|người|thế|này|một|của|không|đã|được|sẽ|đến|có|chưa)\b", re.I)


def load_sources():
    return {path: json.loads((ROOT / path).read_text(encoding="utf-8")) for path in SPECS}


def fields(sources):
    """Yield (file, mutable dictionary, key); game-logic fields stay untouched."""
    for file, (kind,) in SPECS.items():
        doc = sources[file]
        if kind == "quotes":
            for row in doc.values():
                if isinstance(row, dict) and isinstance(row.get("quote"), str):
                    yield file, row, "quote"
        elif kind == "plot":
            for row in doc.get("lines", {}).values():
                if isinstance(row, dict) and isinstance(row.get("d"), str):
                    yield file, row, "d"
            for key in doc.get("titles", {}):
                yield file, doc["titles"], key
        elif kind == "story":
            for row in doc.get("lines", {}).values():
                if isinstance(row, dict) and isinstance(row.get("d"), str):
                    yield file, row, "d"
            for category, keys in (("list", ("name",)), ("forts", ("name", "desc")),
                                   ("episodes", ("name",))):
                for row in doc.get(category, []):
                    for key in keys:
                        if isinstance(row.get(key), str):
                            yield file, row, key
            for key in doc.get("text", {}):
                if isinstance(doc["text"][key], str):
                    yield file, doc["text"], key


def needs_translation(s):
    x = s.strip()
    return bool(LATIN.search(x)) and not VIET.search(x) and x not in EXCLUDE


def parts(value):
    """Do not translate placeholders, inline game markup, or hard newlines."""
    return MARKUP.split(value)


def fragments(value):
    return [piece for piece in parts(value) if needs_translation(piece)]


def pieces_for_model(s, max_length=280):
    if len(s) <= max_length:
        return [s]
    sections = re.split(r"(?<=[.!?;])\s+", s)
    out, current = [], ""
    for section in sections:
        if not section:
            continue
        if len(section) > max_length:
            if current:
                out.append(current)
                current = ""
            words = section.split()
            buf = ""
            for word in words:
                if len(buf) + len(word) + 1 > max_length and buf:
                    out.append(buf)
                    buf = ""
                buf = (buf + " " + word).strip()
            if buf:
                out.append(buf)
        elif len(current) + len(section) + 1 > max_length and current:
            out.append(current)
            current = section
        else:
            current = (current + " " + section).strip()
    if current:
        out.append(current)
    return out or [s]


def gather(sources):
    items, unique = [], set()
    for path, row, key in fields(sources):
        value = row[key]
        if not needs_translation(value):
            continue
        segments = parts(value)
        todo = []
        for part in segments:
            if not needs_translation(part):
                continue
            if part.strip() in GLOSSARY:
                continue
            for block in pieces_for_model(part.strip()):
                unique.add(block)
            todo.append(part)
        items.append((path, row, key, segments, todo))
    return items, sorted(unique)


def translate_all(chunks, batch_size):
    # Import large packages only in apply mode, so stats and auditing run on VPS.
    import torch
    from transformers import MarianMTModel, MarianTokenizer

    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))
    print("Loading translation model:", MODEL, flush=True)
    tokenizer = MarianTokenizer.from_pretrained(MODEL)
    model = MarianMTModel.from_pretrained(MODEL)
    model.eval()
    target_tag = ">>vie<<"
    supported = set(getattr(tokenizer, "supported_language_codes", []) or [])
    use_tag = target_tag in supported
    result = {}
    for i in range(0, len(chunks), batch_size):
        group = chunks[i:i + batch_size]
        texts = [((target_tag + " ") if use_tag else "") + s for s in group]
        x = tokenizer(texts, return_tensors="pt", padding=True,
                      truncation=True, max_length=430)
        with torch.inference_mode():
            y = model.generate(**x, max_new_tokens=256, num_beams=3)
        translated = tokenizer.batch_decode(y, skip_special_tokens=True)
        for src, dst in zip(group, translated):
            dst = dst.strip()
            if not dst:
                raise RuntimeError("Empty translation, original retained: " + src[:70])
            result[src] = dst
        if i == 0 or (i // batch_size + 1) % 25 == 0:
            print(f"Translated {min(i + batch_size, len(chunks))}/{len(chunks)} fragments", flush=True)
    return result


def apply(sources, items, translated, limit):
    edited = 0
    for path, row, key, segments, _ in items:
        if limit and edited >= limit:
            break
        new_parts = []
        for part in segments:
            if not needs_translation(part):
                new_parts.append(part)
                continue
            pad_l = part[: len(part) - len(part.lstrip())]
            pad_r = part[len(part.rstrip()):]
            core = part.strip()
            if core in GLOSSARY:
                replacement = GLOSSARY[core]
            else:
                replacement = " ".join(translated[x] for x in pieces_for_model(core))
            new_parts.append(pad_l + replacement + pad_r)
        new_value = "".join(new_parts)
        if new_value and new_value != row[key]:
            row[key] = new_value
            edited += 1
    for path, doc in sources.items():
        out = ROOT / path
        tmp = out.with_suffix(out.suffix + ".vi-tmp")
        tmp.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        os.replace(tmp, out)
    return edited


def stats(sources):
    report = {}
    for file in SPECS:
        vals = [row[key] for p, row, key in fields(sources) if p == file]
        remaining = [(i, v[:110]) for i, v in enumerate(vals) if needs_translation(v)]
        report[file] = {"total": len(vals), "english_candidates": len(remaining),
                        "sample": remaining[:3]}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="translate and rewrite only dialogue fields")
    parser.add_argument("--verify", action="store_true", help="exit 1 if any English candidates remain")
    parser.add_argument("--limit", type=int, default=0, help="maximum dialogue fields per run (0=all)")
    parser.add_argument("--batch-size", type=int, default=12)
    args = parser.parse_args()
    sources = load_sources()
    before = stats(sources)
    print("Before:", json.dumps(before, ensure_ascii=False))
    if args.apply:
        items, chunks = gather(sources)
        if args.limit:
            # Translate only text needed for the selected fields.
            chosen = items[:args.limit]
            chunks = sorted({b for _, _, _, _, sections in chosen
                             for s in sections for b in pieces_for_model(s.strip())})
        translated = translate_all(chunks, max(1, args.batch_size)) if chunks else {}
        n = apply(sources, items, translated, args.limit)
        print("Changed dialogue fields:", n)
    after = stats(sources)
    print("After:", json.dumps(after, ensure_ascii=False))
    if args.verify and any(x["english_candidates"] for x in after.values()):
        raise SystemExit("INCOMPLETE: untranslated English candidates remain (review the report).")


if __name__ == "__main__":
    main()
