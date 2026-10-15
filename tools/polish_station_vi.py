#!/usr/bin/env python3
"""Clean and audit all 105 + 417 Station translations against original IDs and values.

Reads publisher station.json and a machine-translated candidate. The original
file is never modified. Emits station-vi.json only when ALL checks pass.
Machine prose still requires independent editorial review before claiming 100%
semantic accuracy. Run with --check to verify the released overlay.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "web/assets/station/station.json"
CANDIDATE = ROOT / "web/assets/station/station-vi-candidate.json"
RELEASE = ROOT / "web/assets/station/station-vi.json"
NUMBER = re.compile(r"\d+(?:[.,]\d+)?%?")
MARKUP = re.compile(r"\[\s*(?:/?c|-|[0-9a-f][0-9a-f ]{4,15})\s*\]", re.I)
VIETNAMESE = re.compile(r"[àáạảãăắằặẳẵâấầậẩẫèéẹẻẽêếềệểễìíịỉĩòóọỏõôốồộổỗơớờợởỡùúụủũưứừựửữỳýỵỷỹđ]", re.I)
UNTRANSLATED = re.compile(
    r"\b(?:House|Damage Dealer|Damage|Attack|Buff|Debuff|Skill|Basic|Active|"
    r"Frontline|Back.line|Front.line|Warrior|Mage|Assassin|Ranger|Priest|"
    r"Monster|Ghost|Human|Fairy|Demon|Angel|Armor|Block|Speed|Control|"
    r"Healing|Crit|Petrify|Stun|Silence|Poison|Burn|Bleed|Taunt|Heal|"
    r"Round|Dodge|Supporter|Tank|Precision|Accuracy|Energy|"
    r"Mark|Star|Barrier|Starburst)\b", re.I
)
# Longest-match-first so a stat like Crit Damage is not split by a short token.
GLOSSARY = {
    "House Ghost": "Phe Linh Hồn", "House Human": "Phe Nhân Loại",
    "House Monster": "Phe Quái Vật", "House Fairy": "Phe Tiên",
    "House Demon": "Phe Ác Quỷ", "House Angel": "Phe Thiên Thần",
    "House Cosmos": "Phe Vũ Trụ",
    "gia tộc Ghost": "phe Linh Hồn", "gia tộc Human": "phe Nhân Loại",
    "gia tộc Monster": "phe Quái Vật", "gia tộc Fairy": "phe Tiên",
    "gia tộc Demon": "phe Ác Quỷ", "gia tộc Angel": "phe Thiên Thần",
    "gia tộc Cosmos": "phe Vũ Trụ",
    "Nhà Ghost": "Phe Linh Hồn", "Nhà Human": "Phe Nhân Loại",
    "Nhà Monster": "Phe Quái Vật", "Nhà Fairy": "Phe Tiên",
    "Nhà Demon": "Phe Ác Quỷ", "Nhà Angel": "Phe Thiên Thần",
    "Nhà Cosmos": "Phe Vũ Trụ",
    "Nhà Người": "Phe Nhân Loại", "Nhà Tiên Xứ": "Phe Tiên",
    "Nhà Thiên Thần": "Phe Thiên Thần",
    "Nhà Ác Quỷ": "Phe Ác Quỷ", "gia tộc Thiên Thần": "Phe Thiên Thần",
    "Ranger-class": "hệ Xạ Thủ", "Warrior-class": "hệ Chiến Binh",
    "Assassin-class": "hệ Sát Thủ", "Mage-class": "hệ Pháp Sư",
    "Priest-class": "hệ Tu Sĩ",
    "Damage Dealer": "chủ lực gây sát thương",
    "Armor Break": "Xuyên Giáp", "Armor Ignoring": "Xuyên Giáp",
    "Damage Reduction": "Giảm Sát Thương",
    "Damage Depletion": "Tiêu Hao Sát Thương",
    "Damage over Time": "Sát Thương Theo Thời Gian",
    "Damage Over Time": "Sát Thương Theo Thời Gian",
    "Crit Damage": "Sát Thương Chí Mạng",
    "Crit Resist": "Kháng Chí Mạng",
    "Crit Rate": "Tỷ Lệ Chí Mạng",
    "Basic Attacks": "Đòn Đánh Thường",
    "Basic Attack": "Đòn Đánh Thường",
    "Active Skills": "Kỹ Năng Chủ Động", "Active Skill": "Kỹ Năng Chủ Động",
    "Passive Skills": "Kỹ Năng Bị Động", "Passive Skill": "Kỹ Năng Bị Động",
    "Buff Skill": "Kỹ Năng Tăng Cường",
    "Front Row": "Hàng Trước", "Back Row": "Hàng Sau",
    "Front-line": "Hàng Trước", "Back-line": "Hàng Sau",
    "Frontline": "Hàng Trước", "Backline": "Hàng Sau",
    "Control Immunity": "Kháng Khống Chế",
    "Control Effects": "Hiệu Ứng Khống Chế",
    "Critical Strike": "Đòn Chí Mạng",
    "Heal Received": "Lượng Hồi Máu Nhận",
    "Magick Barriers": "Khiên Ma Thuật",
    "Magick Barrier": "Khiên Ma Thuật",
    "Barrier Points": "Điểm Khiên",
    "Primal Blue": "Sắc Lam Nguyên Sơ",
    "Primal Colors": "Sắc Màu Nguyên Sơ",
    "Pisces' Gift": "Quà Tặng Song Ngư",
    "Hunter's Mark": "Dấu Ấn Thợ Săn",
    "Sanguine Snare": "Bẫy Huyết Sắc",
    "Dark Star Mark": "Dấu Ấn Sao Tối",
    "Attribute Increase Buff": "Hiệu Ứng Tăng Chỉ Số",
    "Attribute Reduction": "Giảm Chỉ Số",
    "Peacock Feather": "Lông Công",
    "Hounded": "Bị Truy Đuổi",
    "Canine Protection": "Hộ Vệ Khuyển",
    "Blood Bats": "Dơi Máu",
    "Nightmare": "Ác Mộng",
    "Malediction": "Lời Nguyền",
    "Magick": "Ma Thuật",
    "Precision": "Độ Chính Xác", "Accuracy": "Độ Chính Xác",
    "Supporter": "nhân vật hỗ trợ",
    "Warrior": "Chiến Binh", "Mage": "Pháp Sư",
    "Assassin": "Sát Thủ", "Ranger": "Xạ Thủ",
    "Priest": "Tu Sĩ", "Healer": "Trị Liệu",
    "Buff": "hiệu ứng tăng cường",
    "Debuff": "hiệu ứng bất lợi",
    "Attack": "Tấn Công", "Armor": "Giáp", "Block": "Chặn Đòn",
    "Speed": "Tốc Độ", "Crit": "Chí Mạng",
    "Dodge": "Né Tránh", "Round": "hiệp",
    "Damage": "Sát Thương", "Skill": "Kỹ Năng",
    "Stun": "Làm Choáng", "Petrify": "Hóa Đá",
    "Silence": "Câm Lặng", "Poison": "Trúng Độc",
    "Burn": "Thiêu Đốt", "Bleed": "Chảy Máu",
    "Taunt": "Khiêu Khích", "Heal": "Hồi Máu",
    "Healing": "Hồi Máu", "Energy": "Năng Lượng",
    "Mark": "Dấu Ấn",
    "Starburst": "Bùng Nổ Tinh Tú",
    "Control": "Khống Chế",
    "Ghost": "Linh Hồn", "Human": "Nhân Loại",
    "Monster": "Quái Vật", "Fairy": "Tiên",
    "Demon": "Ác Quỷ", "Angel": "Thiên Thần",
}
PATTERNS = [(re.compile(r"(?<![A-Za-z])" + re.escape(src) + r"(?![A-Za-z])", re.I), vi)
            for src, vi in sorted(GLOSSARY.items(), key=lambda pair: -len(pair[0]))]
BAD_TRANSLATION_FIXES = {
    r"\b(?:một )?(?:kẻ|người|đại lý|thương nhân|buôn bán|chuyên gia)\s+(?:buôn bán|gây)?\s*(?:thiệt hại|sát thương)\b": "một nhân vật gây sát thương chủ lực",
    r"\b(?:một )?kẻ buôn bán(?: gây)?\s*(?:thiệt hại|sát thương)\b": "một nhân vật gây sát thương chủ lực",
    r"\b(?:một )?chuyên gia (?:gây )?(?:thiệt hại|sát thương)\b": "một nhân vật gây sát thương chủ lực",
    r"\bđại lý (?:gây )?(?:thiệt hại|sát thương)\b": "nhân vật gây sát thương chủ lực",
    r"\bthiệt hại\b": "sát thương",
    r"\btổn thương\b": "sát thương",
    r"\bchữa lành\b": "hồi máu",
    r"\bxử lý sát thương\b": "gây sát thương",
    r"\bđối phó với sát thương\b": "gây sát thương",
    r"\btiến hành sát thương\b": "gây sát thương",
    r"\bkỹ năng bò\b": "kỹ năng tăng cường",
    r"\bkỹ năng đánh da\b": "kỹ năng tăng cường",
    r"\bNâng cao kỹ năng\b": "Kỹ năng tăng cường",
    r"\bBuff kỹ năng\b": "Kỹ năng tăng cường",
    r"\bKỹ năng (?:của )?Buff\b": "Kỹ năng tăng cường",
    r"\bKỹ năng buff\b": "Kỹ năng tăng cường",
    r"\bKỹ năng (?:chủ động|hoạt động)\b": "Kỹ năng chủ động",
    r"\bbộ đồ da\b": "hiệu ứng tăng cường",
    r"\bTỷ lệ khối\b": "tỷ lệ chặn đòn",
    r"\btỷ lệ khối lượng\b": "tỷ lệ chặn đòn",
    r"\bLối sai\b": "Lời Nguyền",
    r"\bhuyết áp\b": "HP",
    r"\bBảo vệ Canine\b": "Hộ Vệ Khuyển",
    r"\bChúa tể Dracula\b": "Lord Dracula",
    r"\bHậu quả\b": "Dư Ảnh",
}
BAD_FIXES = [(re.compile(src, re.I), vi) for src, vi in BAD_TRANSLATION_FIXES.items()]
# Carefully compared against the original source, including all numeric values and target rules.
OVERRIDES = {
 "profile/852018": """1. Hermes là nhân vật gây sát thương chủ lực thuộc phe Nhân Loại.
2. Hermes có thể tạo Khiên Ma Thuật khi gây sát thương lên kẻ địch để tự bảo vệ.
3. Khiên Ma Thuật có thể gánh chịu mọi sát thương thay cho Hermes.
4. Khi đang có Khiên Ma Thuật, Hermes dùng kỹ năng chủ động sẽ chắc chắn gây chí mạng (100%) và gây thêm sát thương lên một kẻ địch ngẫu nhiên.
5. Cuối mỗi hiệp, Hermes gây sát thương cho 1 kẻ địch ngẫu nhiên và tiếp tục gây sát thương cho kẻ địch có HP thấp nhất. Cô nhận thêm Điểm Khiên tương ứng với sát thương gây ra; nếu chưa có Khiên Ma Thuật, cô sẽ nhận một Khiên Ma Thuật mới.""",
 "profile/854011": """1. Mio là nhân vật gây sát thương dựa trên HP tối đa của bản thân, thuộc phe Tiên.
2. Mio có khả năng sinh tồn khá tốt và có thể giảm Tấn Công của mục tiêu để hỗ trợ đồng đội.
3. Sát thương chủ yếu của Mio đến từ hiệu ứng Thiêu Đốt theo thời gian, được tính theo HP tối đa của cô. Vì vậy, tăng HP cũng giúp tăng sát thương.
4. Mio gây sát thương lớn lên kẻ địch có HP cao nhất, cho phép cô liên tục tấn công 1 mục tiêu cụ thể.
5. Mio có thể hồi máu cho bản thân và gây thêm sát thương ngay cả khi chịu hiệu ứng khống chế, phù hợp với nhiều tình huống.""",
 "skill/855011/75501001": """Kỹ năng chủ động của Maia gây sát thương cho 4 kẻ địch ngẫu nhiên và có cơ hội xóa 1 hiệu ứng tăng cường của mỗi mục tiêu. Kỹ năng còn gây hiệu ứng Lời Nguyền lên các mục tiêu.
Lời Nguyền kích hoạt khi mục tiêu nhận hiệu ứng tăng chỉ số. Khi kích hoạt, hiệu ứng sẽ xóa 1 cộng dồn tăng chỉ số vừa nhận và gây sát thương lên mục tiêu.""",
 "skill/857002/757002401": """Kỹ năng tăng cường: Khi bắt đầu trận, Elysia phủ cả ba loại Sắc Màu Nguyên Sơ lên 2 kẻ địch ngẫu nhiên.
Cuối mỗi hiệp, Elysia nhận 1 cộng dồn Quà Tặng Song Ngư. Khi đạt 3 cộng dồn, cô tiêu hao 2 cộng dồn để phủ 1 cộng dồn Sắc Lam Nguyên Sơ lên 2 kẻ địch ngẫu nhiên.""",
 "skill/853015/75301504": """Kỹ năng tăng cường: Sao chép hiệu ứng Sát Thương Theo Thời Gian hoặc Giảm Chỉ Số đang có trên 1 kẻ địch ngẫu nhiên sang 2 kẻ địch khác.""",
 "skill/855012/75501102": """Kỹ năng tăng cường: Tăng HP, Tấn Công, Chặn Đòn, Lượng Hồi Máu Nhận và Kháng Chí Mạng của Promethea.""",
 "skill/854016/75401602": """Kỹ năng tăng cường: Tăng Tấn Công, HP, Sát Thương Chí Mạng, Giảm Sát Thương và Tốc Độ của Kassy.""",
 "skill/854016/75401604": """Kỹ năng tăng cường: Khi bắt đầu trận, Kassy tăng Tốc Độ và Sát Thương Chí Mạng cho toàn đội. Cuối mỗi hiệp, cô tăng Tấn Công và Chí Mạng cho toàn đội. Các nhân vật hệ Sát Thủ nhận hiệu quả tăng cường gấp đôi.""",
 "skill/851019/75101902": """Kỹ năng tăng cường: Tăng HP, Tấn Công, Chí Mạng, Xuyên Giáp và Giảm Sát Thương của Raenvya.""",
 "skill/851008/75101004": """Kỹ năng tăng cường: Tăng Giảm Sát Thương của Sakura trong vài hiệp khi HP của cô giảm xuống dưới ngưỡng nhất định.""",
 "skill/851009/75100403": """Kỹ năng tăng cường: Tăng Giảm Sát Thương, HP và Tấn Công của Giana.""",
}
EMPTY_SOURCE = "此處為填充文本"


def strip_markup(s: str) -> str:
    s = MARKUP.sub("", str(s))
    s = re.sub(r"\(\s*-\s*\]|\[\s*/c\)|\(\s*/c\)", "", s, flags=re.I)
    return re.sub(r"[ \t]{2,}", " ", s).strip()


def polish(source: str, translated: str, identifier: str) -> str:
    if source.strip() == EMPTY_SOURCE:
        return ("Chưa có mô tả chiến thuật trong dữ liệu gốc."
                if identifier.startswith("profile/") else
                "Chưa có mô tả kỹ năng trong dữ liệu gốc.")
    if identifier in OVERRIDES:
        return OVERRIDES[identifier]
    text = strip_markup(translated)
    # Clear mistranslations before applying English/Vietnamese combat glossary.
    for exp, value in BAD_FIXES:
        text = exp.sub(value, text)
    for exp, value in PATTERNS:
        text = exp.sub(value, text)
    # Some model outputs mix original English terms into split colour tags.
    text = re.sub(r"\b(\w+)'\s+s\b", r"\1", text)
    text = re.sub(r"\b10-Star\b", "10 sao", text, flags=re.I)
    text = re.sub(r"\b6-Star\b", "6 sao", text, flags=re.I)
    text = re.sub(r"\bPVE\b", "đấu với máy", text, flags=re.I)
    text = re.sub(r"\bPVP\b", "đấu người chơi", text, flags=re.I)
    text = re.sub(r"\bDoT\b", "sát thương theo thời gian", text, flags=re.I)
    text = re.sub(r"[ \t]+([,.;:])", r"\1", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def data():
    publisher = json.loads(SOURCE.read_text(encoding="utf-8"))["girls"]
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if candidate.get("source_sha256") != digest:
        raise ValueError("Original Station publisher file changed: abort")
    return publisher, candidate, digest


def build():
    publisher, candidate, digest = data()
    output, warnings = {}, []
    for cid, g in publisher.items():
        candidate_row = candidate.get("girls", {}).get(cid) or {}
        row = {"desc": "", "skills": {}}
        if g.get("desc", "").strip():
            row["desc"] = polish(g["desc"], candidate_row.get("desc", ""), f"profile/{cid}")
            warnings.extend(audit(g["desc"], row["desc"], f"profile/{cid}"))
        for sk in g.get("skills", []):
            if sk.get("desc", "").strip():
                sid = str(sk["id"])
                tr = candidate_row.get("skills", {}).get(sid, "")
                row["skills"][sid] = polish(sk["desc"], tr, f"skill/{cid}/{sid}")
                warnings.extend(audit(sk["desc"], row["skills"][sid], f"skill/{cid}/{sid}"))
        if row["desc"] or row["skills"]:
            output[cid] = row
    if sum(bool(v["desc"]) for v in output.values()) != 105 or sum(len(v["skills"]) for v in output.values()) != 417:
        raise ValueError("522 publisher records not all translated")
    document = {"source_sha256": digest, "generator": "VietAI/envit5-translation + publisher-constrained glossary",
                "reviewed": False, "review_warnings": warnings, "girls": output}
    return document


def audit(src: str, text: str, item_id: str):
    problems = []
    original = strip_markup(src)
    if not text or MARKUP.search(text) or "[c]" in text or "[-]" in text or "[/c]" in text:
        problems.append({"id":item_id, "reason":"missing translation or raw markup"})
    if UNTRANSLATED.search(text):
        problems.append({"id":item_id, "reason":"untranslated English combat term",
                         "matched": sorted(set(x.lower() for x in UNTRANSLATED.findall(text)))})
    original_values = Counter(NUMBER.findall(original))
    new_values = Counter(NUMBER.findall(strip_markup(text)))
    if original_values != new_values:
        problems.append({"id":item_id, "reason":"numeric drift",
                         "missing": list((original_values-new_values).elements()),
                         "unexpected": list((new_values-original_values).elements())})
    if not VIETNAMESE.search(text):
        problems.append({"id":item_id, "reason":"not Vietnamese"})
    return problems


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--apply",action="store_true")
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    doc=build()
    issues=doc["review_warnings"]
    profiles=sum(bool(v["desc"]) for v in doc["girls"].values())
    skills=sum(len(v["skills"]) for v in doc["girls"].values())
    print(f"Station localization: profiles={profiles} skills={skills} QA issues={len(issues)}",flush=True)
    for issue in issues[:70]:
        print(json.dumps(issue,ensure_ascii=False),flush=True)
    if args.apply:
        if issues:
            raise SystemExit("STOP: remaining localized content issues; existing live overlay preserved")
        RELEASE.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("PASSED. Saved production Station Vietnamese overlay.",flush=True)
    if args.check:
        if not RELEASE.exists(): raise SystemExit("Translation overlay missing")
        live=json.loads(RELEASE.read_text(encoding="utf-8"))
        if live["source_sha256"]!=doc["source_sha256"] or live["girls"]!=doc["girls"] or live.get("review_warnings"):
            raise SystemExit("Live station-vi.json does not match fully-audited source")
        print("PASS | 105 original character profiles; 417 original skill descriptions; no formatting or numeric mismatches",flush=True)
    if issues: sys.exit(1)


if __name__=="__main__":
    main()
