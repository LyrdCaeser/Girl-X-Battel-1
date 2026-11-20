#!/usr/bin/env python3
"""Structural/terminology audit of GXB3 Station Vietnamese descriptions.

Does not claim human translation quality: warns about possible translation mistakes.
Never modifies publisher gameplay data.
"""
import argparse
import collections
import json
import re
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "web/assets/station/station.json"
TOKENS = re.compile(r"\[(?:c|/c|-|#?[0-9a-fA-F]{6,8})\]")
NUMBER = re.compile(r"(?<!\w)\d+(?:[.,]\d+)?%?")
ENGLISH = re.compile(
    r"\b(?:House|Front.line|Back.line|Damage Dealer|Active skill|Basic Attack|Armor Break|Petrify|Bleeding|Ranger.class|Priest.class)\b", re.I)
VN = re.compile(r"[àáạảãăắằặẳẵâấầậẩẫèéẹẻẽêếềệểễìíịỉĩòóọỏõôốồộổỗơớờợởỡùúụủũưứừựửữỳýỵỷỹđ]", re.I)


def numeric_tokens(value):
    # Hex markup values (e.g. [01a310]) are NOT gameplay numbers.
    return collections.Counter(NUMBER.findall(TOKENS.sub("", value)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--target", default="web/assets/station/station-vi.json")
    p.add_argument("--max-samples", type=int, default=10)
    args = p.parse_args()
    path = ROOT / args.target
    original = json.loads(SOURCE.read_text(encoding="utf-8"))["girls"]
    translated = json.loads(path.read_text(encoding="utf-8"))
    if translated.get("source_sha256") != hashlib.sha256(SOURCE.read_bytes()).hexdigest():
        raise SystemExit("FAIL: publisher source digest mismatch")
    records = translated["girls"]
    cases, issues, pcount, scount = [], [], 0, 0
    for cid, girl in original.items():
        if girl.get("desc", "").strip():
            pcount += 1
            cases.append(("profile/" + cid, girl["desc"], records.get(cid, {}).get("desc")))
        for skill in girl.get("skills", []):
            if skill.get("desc", "").strip():
                scount += 1
                cases.append(("skill/" + cid + "/" + str(skill["id"]), skill["desc"],
                              records.get(cid, {}).get("skills", {}).get(str(skill["id"]))))
    if (pcount, scount) != (105, 417):
        raise SystemExit(f"FAIL: source expected 105/417; got {pcount}/{scount}")
    for key, english, vietnamese in cases:
        if not isinstance(vietnamese, str) or not vietnamese.strip() or vietnamese == english:
            raise SystemExit(f"FAIL: empty/missing or unchanged translation: {key}")
        if len(english.splitlines()) != len(vietnamese.splitlines()):
            issues.append((key,"line count differs"))
        if TOKENS.search(vietnamese):
            issues.append((key,"raw markup tokens remain"))
        missing = numeric_tokens(english) - numeric_tokens(vietnamese)
        added = numeric_tokens(vietnamese) - numeric_tokens(english)
        if missing or added:
            issues.append((key,f"numeric changed, missing={list(missing.elements())}, added={list(added.elements())}"))
        if ENGLISH.search(vietnamese):
            issues.append((key, "English game terminology remains"))
        if not VN.search(vietnamese):
            issues.append((key, "No accented Vietnamese detected"))
    cats = collections.Counter(msg.split(",")[0] for _, msg in issues)
    print(f"Coverage: {pcount}/{pcount} profiles + {scount}/{scount} skills")
    print(f"Source SHA256: {translated['source_sha256']}")
    print(f"Generator: {translated.get('generator', 'unknown')}")
    print(f"QA status: machine-reviewed={bool(translated.get('reviewed'))}")
    print(f"Potential problems: {len(issues)} in {len(set(k for k,_ in issues))} records, categories={dict(cats)}")
    for item in issues[:args.max_samples]:
        print(" -", *item)
    print("PASS | Structural coverage 105+417" if not issues else "WARNING | Semantic QA still required")


if __name__ == "__main__":
    main()
