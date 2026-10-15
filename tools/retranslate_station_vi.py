#!/usr/bin/env python3
"""Build a Vietnamese Station overlay from original publisher descriptions.

Uses VietAI EnViT5 instead of generic Marian; never edits station.json.
Translation is machine-generated, and requires editorial QA before declaring final.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "web/assets/station/station.json"
DEST = ROOT / "web/assets/station/station-vi-candidate.json"
MODEL = "VietAI/envit5-translation"
EXPECTED = (105, 417)
NUM_RE = re.compile(r"(?<!\w)\d+(?:[.,]\d+)?%?")
EMBEDDED_ENGLISH = re.compile(r"\b(?:House|Back.line|Front.line|Damage Dealer|Armor Break|Active skill|Basic Attack|Buff skill|Debuff|Petrify|Assassin.class|Warrior.class|Priest.class)\b", re.I)
DIACRITIC = re.compile(r"[àáạảãăắằặẳẵâấầậẩẫèéẹẻẽêếềệểễìíịỉĩòóọỏõôốồộổỗơớờợởỡùúụủũưứừựửữỳýỵỷỹđ]", re.I)


def load():
    raw = SOURCE.read_bytes()
    girls = json.loads(raw)["girls"]
    profiles = {k: v["desc"] for k, v in girls.items() if v.get("desc", "").strip()}
    skills = {(gid, str(row["id"])): row["desc"]
              for gid, g in girls.items() for row in g.get("skills", []) if row.get("desc", "").strip()}
    if (len(profiles), len(skills)) != EXPECTED:
        raise ValueError(f"Publisher source has changed: {len(profiles)} profiles/{len(skills)} skills")
    return profiles, skills, hashlib.sha256(raw).hexdigest()


def split_english(text, limit=210):
    """Retain paragraph breaks and sentence numbering; split at punctuation to avoid truncation."""
    out = []
    for line in text.split("\n"):
        number = re.match(r"^(\s*\d+[.)]\s*)", line)
        prefix = number.group(0) if number else ""
        remaining = line[len(prefix):].strip()
        chunks, buff = [], ""
        sentences = re.split(r"(?<=[.!?;])\s+", remaining)
        for sentence in sentences:
            words = sentence.split()
            for word in words:
                if buff and len(buff) + len(word) + 1 > limit:
                    chunks.append(buff)
                    buff = ""
                buff = (buff + " " + word).strip()
            if buff and buff[-1] in ".!?;":
                chunks.append(buff)
                buff = ""
        if buff:
            chunks.append(buff)
        out.append((prefix, chunks))
    return out


def translate(chunks, size):
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    print(f"Loading {MODEL}, distinct chunks={len(chunks)}", flush=True)
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL)
    model.eval()
    result = {}
    for off in range(0, len(chunks), size):
        batch = chunks[off:off + size]
        inputs = tok(["en: " + x for x in batch], return_tensors="pt", padding=True,
                     truncation=True, max_length=420)
        with torch.inference_mode():
            outputs = model.generate(**inputs, max_new_tokens=350, num_beams=2)
        decoded = tok.batch_decode(outputs, skip_special_tokens=True)
        for en, vi in zip(batch, decoded):
            clean = re.sub(r"^\s*vi:\s*", "", vi).strip()
            if not clean:
                raise ValueError("Empty translation at " + en[:100])
            result[en] = clean
        if off == 0 or off // size % 20 == 0:
            print(f"Translated {min(off+size,len(chunks))}/{len(chunks)}", flush=True)
    return result


def assemble(src, plan, outputs, warnings, context):
    translated = "\n".join(prefix + " ".join(outputs[c] for c in parts)
                           for prefix, parts in plan)
    for old, new in (("Nhà Ghost", "Nhà Linh Hồn"), ("Nhà Human", "Nhà Nhân Loại"),
                     ("Nhà Monster", "Nhà Quái Vật"), ("Nhà Fairy", "Nhà Tiên"),
                     ("Nhà Demon", "Nhà Ác Quỷ"), ("Nhà Angel", "Nhà Thiên Thần")):
        translated = translated.replace(old, new)
    orig_nums = collections.Counter(NUM_RE.findall(src))
    trans_nums = collections.Counter(NUM_RE.findall(translated))
    missing = list((orig_nums - trans_nums).elements())
    unexpected = list((trans_nums - orig_nums).elements())
    if missing or unexpected:
        warnings.append({"id":context, "reason":"numeric drift", "missing":missing,"unexpected":unexpected})
    if EMBEDDED_ENGLISH.search(translated):
        warnings.append({"id":context, "reason":"English combat term remains"})
    if not DIACRITIC.search(translated):
        warnings.append({"id":context, "reason":"No Vietnamese diacritics"})
    if len(translated) < min(20, max(8, len(src)//5)):
        warnings.append({"id":context, "reason":"Suspiciously short translation"})
    return translated


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    p.add_argument("--verify", action="store_true")
    p.add_argument("--batch-size", type=int, default=8)
    args = p.parse_args()
    prof, skills, digest = load()
    if args.apply:
        plans = {value: split_english(value) for value in set(prof.values()) | set(skills.values())}
        all_chunks = sorted({chunk for rows in plans.values() for _, parts in rows for chunk in parts})
        trans = translate(all_chunks, max(1,args.batch_size))
        girls, warnings = {}, []
        for cid, text in prof.items():
            girls.setdefault(cid, {"desc": "", "skills": {}})["desc"] = assemble(
                text, plans[text], trans, warnings, "profile/" + cid)
        for (cid, sid), text in skills.items():
            girls.setdefault(cid, {"desc": "", "skills": {}})["skills"][sid] = assemble(
                text, plans[text], trans, warnings, "skill/" + cid + "/" + sid)
        doc = {"source_sha256":digest, "generator":MODEL, "reviewed":False,
               "review_warnings":warnings, "girls":girls}
        tmp = DEST.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        tmp.replace(DEST)
        print(f"Candidate generated. Problems flagged: {len(warnings)}", flush=True)
    if args.verify:
        if not DEST.exists():
            raise SystemExit("Translation candidate file not yet generated")
        doc = json.loads(DEST.read_text(encoding="utf-8"))
        assert doc["source_sha256"] == digest, "Publisher source hash mismatch"
        got=doc["girls"]
        assert sum(bool(v.get("desc")) for v in got.values()) == 105
        assert sum(len(v.get("skills", {})) for v in got.values()) == 417
        for cid, s in prof.items():
            assert got[cid]["desc"] and got[cid]["desc"] != s, f"Untranslated profile {cid}"
        for (cid,sid),s in skills.items():
            assert got[cid]["skills"][sid] and got[cid]["skills"][sid] != s, f"Untranslated skill {cid}/{sid}"
        print(f"PASS | 105+417 candidate translated; {len(doc['review_warnings'])} warnings", flush=True)


if __name__ == "__main__":
    main()
