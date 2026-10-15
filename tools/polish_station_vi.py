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
    "Basic": "Cơ Bản", "Active": "Chủ Động", "Star": "Sao", "House": "Phe",
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
    # Generic machine-translation artefacts found in all character skill records.
    r"\bKỹ năng (?:của )?hiệu ứng tăng cường\b": "Kỹ năng tăng cường",
    r"\bhiệu ứng tăng cường kỹ năng\b": "Kỹ năng tăng cường",
    r"\bKỹ năng(?:\s+của)?\s+hiệu ứng tăng cường\b": "Kỹ năng tăng cường",
    r"\bKỹ năng tích cực\b": "Kỹ năng chủ động",
    r"\bKỹ năng hoạt động\b": "Kỹ năng chủ động",
    r"\bĐòn (?:Tấn Công|tấn công) Cơ Bản\b": "Đòn đánh thường",
    r"\bTấn Công Cơ Bản\b": "Đòn đánh thường",
    r"\bđông lạnh\b": "Đóng Băng",
    r"\bFreeze\b": "Đóng Băng",
    r"\bFrozen\b": "Đóng Băng",
    r"\bPetrified\b": "Hóa Đá",
    r"\bCrits\b": "gây Chí Mạng",
    r"\bCrit Damage\b": "Sát Thương Chí Mạng",
    r"\bkhả năng kiểm soát đám đông\b": "khả năng khống chế diện rộng",
    r"\bngười ủng hộ\b": "nhân vật hỗ trợ",
    r"\bthầy thuốc\b": "nhân vật Hồi Máu",
    r"\btỷ lệ khối\b": "tỷ lệ Chặn Đòn",
    r"\bBóng ma nhà\b": "Phe Linh Hồn",
    r"\bNhà con người\b": "Phe Nhân Loại",
    r"\bcơn ác mộng\b": "Ác Mộng",
    r"\bHàng Tiền Tuyến\b": "hàng trước",
    r"\bHậu Tuyến\b": "hàng sau",
    r"\bTiền Tuyến\b": "hàng trước",
    r"\bsự tấn công cơ bản\b": "đòn đánh thường",
    r"\bđối phó với thiệt hại\b": "gây sát thương",
    r"\bxử lý thiệt hại\b": "gây sát thương",
    r"\bđánh bại kẻ thù\b": "hạ gục kẻ địch",

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
 "skill/853015/75301504": """Kỹ năng tăng cường: Sao chép hiệu ứng Sát Thương Theo Thời Gian hoặc Giảm Chỉ Số trên một kẻ địch ngẫu nhiên sang 2 kẻ địch khác.""",
 "skill/855012/75501102": """Kỹ năng tăng cường: Tăng HP, Tấn Công, Chặn Đòn, Lượng Hồi Máu Nhận và Kháng Chí Mạng của Promethea.""",
 "skill/854016/75401602": """Kỹ năng tăng cường: Tăng Tấn Công, HP, Sát Thương Chí Mạng, Giảm Sát Thương và Tốc Độ của Kassy.""",
 "skill/854016/75401604": """Kỹ năng tăng cường: Khi bắt đầu trận, Kassy tăng Tốc Độ và Sát Thương Chí Mạng cho toàn đội. Cuối mỗi hiệp, cô tăng Tấn Công và Chí Mạng cho toàn đội. Các nhân vật hệ Sát Thủ nhận hiệu quả tăng cường gấp đôi.""",
 "skill/851019/75101902": """Kỹ năng tăng cường: Tăng HP, Tấn Công, Chí Mạng, Xuyên Giáp và Giảm Sát Thương của Raenvya.""",
 "skill/851008/75101004": """Kỹ năng tăng cường: Tăng Giảm Sát Thương của Sakura trong vài hiệp khi HP của cô giảm xuống dưới ngưỡng nhất định.""",
 "skill/851009/75100403": """Kỹ năng tăng cường: Tăng Giảm Sát Thương, HP và Tấn Công của Giana.""",
 "skill/855003/75500401": """Kỹ năng chủ động của Wraith gây sát thương cho 1 kẻ địch ngẫu nhiên. Nếu mục tiêu có HP cao hơn Wraith, kỹ năng gây thêm sát thương tương ứng với một tỷ lệ HP tối đa của kẻ địch, đồng thời tăng Chí Mạng của Wraith.
Kỹ năng này đặc biệt hiệu quả trước các mục tiêu có HP cao. Khi đạt 10 sao, Wraith tấn công hai kẻ địch và gây sát thương mạnh hơn lên nhân vật hệ Tu Sĩ.""",
 "skill/854014/75401401": """Kỹ năng chủ động của Vera gây sát thương lên 1 kẻ địch ngẫu nhiên và áp dụng hiệu ứng Suy Yếu, khiến mục tiêu chịu thêm sát thương và gây ít sát thương hơn.
Kỹ năng cũng ban hiệu ứng bảo vệ Khúc Ru cho 3 đồng minh. Khi người được bảo vệ chịu Đòn Đánh Thường hoặc Kỹ Năng Chủ Động, Khúc Ru hồi HP cho họ và gây sát thương xuyên giáp lên kẻ tấn công.""",
 "skill/851014/75101401": """Kỹ năng chủ động của Von Helsing gây sát thương nhiều lần lên mục tiêu; mỗi lần gây sát thương sẽ tích 1 cộng dồn Dấu Ấn Thợ Săn.
Kỹ năng cho phép cô tiêu hao hiệu ứng Khát Máu để giảm HP của mục tiêu và hồi HP cho bản thân.
Có cơ hội gây thêm sát thương dựa trên HP tối đa của mục tiêu.""",
 "skill/851014/75101403": """Kỹ năng tăng cường cho phép Von Helsing nhắm vào kẻ địch có chỉ số Tấn Công cao nhất.
Đòn Đánh Thường của cô có thể gây sát thương hai lần, đồng thời tích 1 cộng dồn Dấu Ấn Thợ Săn cho mỗi lần gây sát thương.""",
 "skill/854017/75401701": """Kỹ năng chủ động của Aurora tấn công 1 kẻ địch ngẫu nhiên, có cơ hội Hóa Tinh Thể mục tiêu và áp dụng hiệu ứng Nảy Bật.
Khi Nảy Bật kích hoạt, đòn tấn công chuyển sang 1 kẻ địch ngẫu nhiên khác; sát thương và xác suất Hóa Tinh Thể tăng dần.
Không tấn công cùng một mục tiêu hai lần liên tiếp. Sát thương có thể nảy tối đa 5 lần; hiệu ứng kết thúc nếu trên sân còn ít hơn 2 kẻ địch hoặc đòn tấn công bị Né Tránh.""",
 "skill/852018/75201804": """Kỹ năng tăng cường của Hermes gây sát thương cho 1 kẻ địch ngẫu nhiên rồi gây thêm sát thương cho kẻ địch có HP thấp nhất.
Dựa trên sát thương gây ra, cô nhận thêm Điểm Khiên cho Khiên Ma Thuật. Nếu chưa có Khiên Ma Thuật, cô sẽ nhận một Khiên Ma Thuật mới.""",
 "skill/851018/75101803": """Kỹ năng tăng cường cho phép Chizuko hồi HP cho đồng minh có HP thấp nhất, ban Khiên Ma Thuật cho đồng minh này và loại bỏ 1 hiệu ứng bất lợi ngẫu nhiên trên họ.""",
 "skill/856011/75601101": """Kỹ năng chủ động của Poseidia giảm Giáp của 1 kẻ địch ngẫu nhiên, gây sát thương lên mục tiêu đó 3 lần và tăng Chặn Đòn cho toàn bộ đồng minh.""",
 "profile/856012": """1. Zeusia là nhân vật chủ lực gây sát thương thuộc phe Thiên Thần.
2. Kỹ năng chủ động của cô gây sát thương lên toàn bộ kẻ địch, giảm Tấn Công của chúng và tăng sát thương chúng phải chịu từ hiệu ứng Thiêu Đốt.
3. Khi Zeusia dùng kỹ năng chủ động lên mục tiêu đang chịu hiệu ứng Lôi Kích, hiệu ứng đó được kích hoạt thêm một lần ngay lập tức. Nếu mục tiêu không có Lôi Kích, Zeusia nhận hiệu ứng Thần Tính.
4. Khi có 12 cộng dồn Thần Tính, Zeusia thi triển Lôi Kích lên toàn bộ kẻ địch.""",
 "skill/856012/75601204": """Kỹ năng tăng cường: Mỗi khi đồng minh sử dụng kỹ năng chủ động, Zeusia nhận hiệu ứng Thần Tính. Khi đạt 12 cộng dồn Thần Tính, cô thi triển Lôi Kích lên toàn bộ kẻ địch.""",
}
# Editorially checked against original publisher descriptions (no gameplay values changed).
# IDs are Station publisher keys, not hero names; reissues share their source record.
OVERRIDES.update({
 "profile/851001": """1. Sapphire là nhân vật hệ Tu Sĩ chuyên gây sát thương, thuộc phe Linh Hồn.
2. Kỹ năng chủ động của cô có xác suất Hóa Đá kẻ địch ở hàng sau và tăng Độ Chính Xác cho đồng đội. Đòn đánh thường của Sapphire giảm tỷ lệ Chặn Đòn của mục tiêu, giúp cả đội gây sát thương ổn định hơn.
3. Tốc Độ cơ bản của Sapphire khá thấp. Tăng Tốc Độ giúp cô ra đòn sớm hơn trong hiệp, phát huy tốt hơn ở Thử Thách và PvP.""",
 "profile/851002": """1. Gambler là Sát Thủ thuộc phe Linh Hồn, có khả năng tự hồi máu và đặc biệt nguy hiểm khi tấn công mục tiêu đang chịu hiệu ứng Chảy Máu.
2. Cô rất hữu ích trong các trận PvE.
3. Gambler có khả năng sinh tồn kém, nên cần đồng đội hoặc trang bị tăng sức chống chịu.""",
 "profile/851003": """1. Succuba là Chiến Binh phe Linh Hồn, thường được bố trí ở hàng trước.
2. Chỉ số ban đầu của cô thấp hơn một số nhân vật khác, nhưng khi Thức Tỉnh lên 10 sao, Succuba được tăng cường mạnh và có thêm khả năng khống chế kẻ địch.""",
 "profile/851004": """1. Dracula là nhân vật gây sát thương thuộc phe Linh Hồn.
2. Kỹ năng chủ động của cô khắc chế nhân vật hệ Pháp Sư, phù hợp để đối phó đội hình có nhiều Pháp Sư.
3. Dracula ưu tiên kẻ địch có HP thấp nhất, giúp đội tập trung hạ mục tiêu yếu và nhanh chóng tạo lợi thế quân số.""",
 "profile/851005": """1. Wu Kong là nhân vật gây sát thương thuộc phe Linh Hồn.
2. Kỹ năng chủ động của cô khắc chế Sát Thủ, đặc biệt hữu ích khi đối đầu đội hình có nhiều nhân vật hệ này.
3. Tốc Độ cơ bản của Wu Kong khá thấp. Tăng Tốc Độ giúp cô hành động sớm hơn trong mỗi hiệp và chiến đấu hiệu quả hơn ở Thử Thách lẫn PvP.""",
 "profile/851006": """1. Fencer là Chiến Binh phe Linh Hồn có khả năng khống chế bằng hiệu ứng Đóng Băng.
2. Kỹ năng chủ động gây sát thương lên hàng trước của địch và có xác suất cao khiến chúng Đóng Băng.
3. Khi bị tấn công, Fencer có cơ hội Đóng Băng kẻ tấn công. Cô còn có kỹ năng tăng HP và Giáp để nâng khả năng sinh tồn.
4. Fencer không có giai đoạn sức mạnh suy giảm rõ rệt, nên phù hợp ở nhiều cấp sao.""",
 "profile/851007": """1. Wildtress là nhân vật gây sát thương thuộc phe Linh Hồn.
2. Cô có khả năng tấn công khá tốt. Kỹ năng chủ động còn làm giảm chỉ số Tấn Công của mục tiêu, giúp đồng đội sống sót lâu hơn.""",
 "profile/851008": """1. Sakura là nhân vật khống chế thuộc phe Linh Hồn, có thể Hóa Đá kẻ địch và gây thêm sát thương lên chúng.
2. Các kỹ năng giúp Sakura dễ Hóa Đá mục tiêu và giảm Giáp của chúng, khiến cô phù hợp với PvP.
3. Sakura có chỉ số Giảm Sát Thương cao và miễn nhiễm Hóa Đá, nhờ vậy sở hữu khả năng sinh tồn tốt.""",
 "profile/851009": """1. Giana là nhân vật gây sát thương thuộc phe Linh Hồn.
2. Sức tấn công thông thường của cô không quá nổi bật, nhưng kỹ năng kích hoạt khi tử trận có thể gây lượng sát thương rất lớn.
3. Giana phối hợp tốt với nhân vật hưởng lợi từ việc đồng đội tử trận, chẳng hạn Saint Esau & Jacob.""",
 "profile/851010": """1. Ennmaya là Sát Thủ thuộc phe Linh Hồn.
2. Đòn đánh thường của cô có thể Làm Choáng một kẻ địch ngẫu nhiên ở hàng sau.
3. Các chỉ số tấn công cao biến Ennmaya thành nhân vật gây sát thương rất nguy hiểm.
4. Từ 8 sao, đòn đánh thường của cô có xác suất Làm Choáng mục tiêu 100%, đặc biệt mạnh trong các trận đấu 1 chọi 1. Kỹ năng chủ động còn tăng Giảm Sát Thương để giúp cô trụ vững.""",
 "profile/851011": """1. Valeera là nhân vật đa dụng thuộc phe Linh Hồn.
2. Cô có Tấn Công khá cao; kỹ năng có thể gây Đóng Băng hoặc Hóa Đá mục tiêu.
3. Khi chịu sát thương từ kỹ năng chủ động của địch, Valeera có cơ hội tự hồi một lượng HP lớn, tăng mạnh khả năng sinh tồn.
4. Cô còn giảm Tấn Công của mục tiêu, nên phù hợp với nhiều đội hình.""",
 "profile/851012": """1. Fenrir là Chiến Binh phe Linh Hồn có khả năng gây sát thương tốt và càng đánh càng mạnh.
2. Kỹ năng chủ động của cô gây áp lực lên cả mục tiêu HP cao lẫn HP thấp. Sau khi Chặn Đòn thành công 3 lần, Fenrir có thể phản công một lần và hồi HP nhờ đòn phản công đó, phù hợp với vai trò bảo vệ đội.
3. Fenrir mạnh dần theo thời gian giao tranh; cô phối hợp tốt với các nhân vật kéo dài trận đấu như Raphael hoặc CapsuGirl.""",
 "profile/851013": """1. Vivian là nhân vật hỗ trợ thuộc phe Linh Hồn.
2. Cô có thể Hồi Máu, xóa hiệu ứng bất lợi cho đồng minh; đồng thời xóa hiệu ứng tăng cường của kẻ địch và áp dụng hiệu ứng bất lợi lên chúng.
3. Hiệu ứng “Galaxy” giúp Vivian tiếp tục hỗ trợ đội hiệu quả khi cô trụ vững lâu trên chiến trường.""",
 "profile/851014": """1. Von Helsing là nhân vật gây sát thương thuộc phe Linh Hồn.
2. Cô ưu tiên mục tiêu có Tấn Công cao nhất. Sát thương tăng theo số Dấu Ấn cộng dồn trên mục tiêu.
3. Von Helsing có khả năng sinh tồn tốt: cô có thể chuyển hiệu ứng bất lợi trên bản thân thành Khát Máu và tự hồi HP khi kích hoạt kỹ năng chủ động.
4. Chế độ “Feast” còn tăng mạnh sức chiến đấu của cô.""",
 "profile/851015": """1. Blair là nhân vật gây sát thương thuộc phe Linh Hồn.
2. Đòn đánh thường và kỹ năng chủ động cùng nhắm vào kẻ địch có HP thấp nhất.
3. Khi tấn công, cô cũng gây sát thương tương đương lên các mục tiêu mang cộng dồn “Moon Dust” và khiến chúng Trúng Độc.
4. Nếu đòn đánh gây Chí Mạng, Blair còn áp dụng Chảy Máu lên mục tiêu.
5. Khi hạ gục kẻ địch, Blair được tăng Xuyên Giáp và đặt “Moon Dust” lên một mục tiêu ngẫu nhiên mới.""",
 "profile/851016": """1. Diana là nhân vật gây sát thương thuộc phe Linh Hồn.
2. Khi dùng kỹ năng chủ động hoặc đòn đánh thường, Diana gây thêm sát thương dựa trên chỉ số Tấn Công của mục tiêu.
3. Kỹ năng chủ động cho phép cô đánh cắp Tấn Công của mục tiêu. Nếu mục tiêu có từ 90 Năng Lượng trở lên, kỹ năng có cơ hội gây Câm Lặng; nếu dưới 90 Năng Lượng, kỹ năng có cơ hội gây Khiếp Sợ.
4. Kỹ năng bị động giúp đòn đánh thường nhắm vào kẻ địch có Tấn Công cao nhất. Cuối mỗi hiệp, nếu Tấn Công của kẻ địch mạnh nhất cao hơn Diana, cô có thể hoán đổi chỉ số Tấn Công với kẻ đó.
5. Khi kẻ địch hạ gục Diana, cô áp dụng hiệu ứng “Malediction” lên kẻ đó để gây thêm sát thương.""",
 "profile/851017": """1. Lord Dracula là nhân vật chủ lực gây sát thương thuộc phe Linh Hồn.
2. Kỹ năng chủ động vừa gây sát thương vừa giảm Tấn Công của mục tiêu, đồng thời áp dụng “Bẫy Huyết Sắc” để gây sát thương theo thời gian và hồi máu cho bản thân.
3. Khi Lord Dracula dùng đòn đánh thường hoặc bất kỳ nhân vật nào tử trận, cô có cơ hội nhận hiệu ứng tăng cường đặc biệt, khiến lần áp dụng “Bẫy Huyết Sắc” tiếp theo gây nhiều sát thương hơn.
4. Khi Chặn Đòn thành công trước sát thương trực tiếp từ đòn đánh thường hoặc kỹ năng chủ động, Lord Dracula áp dụng “Bẫy Huyết Sắc” lên 2 kẻ địch ngẫu nhiên.""",
 "profile/851018": """1. Chizuko là nhân vật hỗ trợ thuộc phe Linh Hồn.
2. Cô áp dụng hiệu ứng bất lợi để giảm Tấn Công của kẻ địch và tăng sát thương chúng phải chịu.
3. Chizuko có thể tăng cường bảo vệ đồng minh bằng cách vô hiệu hóa sát thương sắp nhận và chuyển thành Điểm Khiên (BP), rất phù hợp với vai trò phòng thủ.""",
 "profile/851019": """1. Raenvya là Chiến Binh thuộc phe Linh Hồn.
2. Cô có thể chịu sát thương thay cho đồng minh có Tấn Công cao nhất.
3. Khi tử trận, Raenvya nhập vào đồng minh có Tấn Công cao nhất và tăng mạnh chỉ số cho họ. Mỗi khi đồng minh bị nhập dùng đòn đánh thường hoặc kỹ năng chủ động, Raenvya truy kích mục tiêu. Nếu hạ được kẻ địch nhờ hiệu ứng này, cô sẽ hồi sinh ở hiệp kế tiếp.""",
 "profile/852001": """1. Hottie là nhân vật hỗ trợ thuộc phe Nhân Loại.
2. Cô tăng mạnh Tốc Độ của đồng đội, giúp đội hình tối ưu thứ tự hành động trong hiệp.
3. Ngoài việc tăng Tấn Công và Tốc Độ cho đồng đội, khi HP của Hottie xuống dưới một ngưỡng nhất định, cô còn tăng Tấn Công cho cả đội và giảm Giáp của toàn bộ kẻ địch (mỗi trận chỉ kích hoạt một lần).""",
 "profile/852002": """1. Blowie là nhân vật hỗ trợ thuộc phe Nhân Loại.
2. Cô sở hữu khả năng Hồi Máu mạnh, giúp đồng minh trụ vững trong chiến đấu.
3. Tốc Độ của Blowie thấp hơn nhiều nhân vật khác; nên tăng chỉ số này để cô hành động sớm hơn trong mỗi hiệp.""",
 "profile/852003": """1. Chevalir là Chiến Binh thuộc phe Nhân Loại, thường đứng ở hàng trước.
2. Khi HP giảm xuống dưới ngưỡng nhất định, cô có thể tăng Giáp cho toàn đội. Hiệu ứng này phối hợp tốt với nhân vật như Sonya.""",
 "profile/852004": """1. Saint là một trong những nhân vật gây sát thương chủ lực của phe Nhân Loại.
2. Các kỹ năng của Saint đều tăng mạnh khả năng tấn công. Cô càng tồn tại lâu trong trận thì sát thương tiềm năng càng lớn.
3. Saint nhận hiệu ứng tăng cường khi có nhân vật tử trận, vì vậy cô phối hợp tốt với các nhân vật có kỹ năng kích hoạt khi bị hạ gục.""",
 "profile/852005": """1. Javelin là nhân vật gây sát thương thuộc phe Nhân Loại.
2. Cô vừa gây sát thương diện rộng lên toàn bộ kẻ địch vừa có cơ hội Đóng Băng chúng. Javelin gây thêm sát thương lên mục tiêu đang Đóng Băng, nên phối hợp tốt với nhân vật có kỹ năng khống chế Đóng Băng.
3. Nếu được trang bị để tăng khả năng sinh tồn, Javelin có thể đứng ở hàng trước và giảm Tấn Công của kẻ địch khi chịu đòn.""",
 "profile/852006": """1. Geisha là nhân vật khống chế thuộc phe Nhân Loại.
2. Sau khi tử trận, Geisha gây sát thương lên toàn bộ kẻ địch ở hàng sau, nhờ vậy có thể hữu ích tại chế độ Thử Thách.
3. Khi đạt 10 sao, đòn đánh thường của Geisha có xác suất cao Làm Choáng mục tiêu.""",
 "profile/852007": """1. Sonya là một trong những nhân vật chủ lực gây sát thương của phe Nhân Loại.
2. Sonya có Giáp cơ bản cao; khi chịu đòn từ kẻ địch có Giáp thấp hơn, cô sẽ phản công. Lợi thế này đặc biệt hữu ích trong PvP.
3. Trong PvE, Sonya còn hỗ trợ đội bằng cách giảm Giáp của kẻ địch.
4. Cô có thể sử dụng trong nhiều kiểu đội hình.""",
 "profile/852008": """1. Caitlyn là nhân vật gây sát thương thuộc phe Nhân Loại.
2. Cô ưu tiên tấn công kẻ địch có HP thấp nhất, giúp đội nhanh chóng giảm quân số đối phương.
3. Cô còn gây lượng lớn sát thương theo thời gian (DoT) lên kẻ địch.""",
 "profile/852009": """1. Guan Yin là nhân vật phe Nhân Loại nổi bật nhờ tỷ lệ Chặn Đòn cao.
2. Cô có thể tăng tỷ lệ Chặn Đòn của bản thân thông qua tấn công, cải thiện khả năng sinh tồn.
3. Sau khi Tiến Hóa lên 6 sao, đòn đánh thường của Guan Yin sẽ đánh trúng toàn bộ kẻ địch hàng trước, tạo sức ép lớn lên tuyến đầu đối phương.""",
 "profile/852010": """1. Librarian là nhân vật gây sát thương thuộc phe Nhân Loại.
2. Đòn tấn công của cô gây sát thương lên 3 kẻ địch ngẫu nhiên.
3. Librarian khắc chế nhân vật hệ Tu Sĩ, nên hiệu quả trước đội hình có nhiều nhân vật hệ này.
4. Cô còn có thể giảm Tấn Công của kẻ địch để đồng đội sống sót lâu hơn.""",
 "profile/852011": """1. CapsuGirl là nhân vật khống chế thuộc phe Nhân Loại.
2. Kỹ năng chủ động gây sát thương lên 4 kẻ địch ngẫu nhiên; trong đó 3 mục tiêu có thể bị Làm Choáng.
3. Khi đồng minh kích hoạt kỹ năng chủ động, CapsuGirl có cơ hội hỗ trợ bằng hiệu ứng Làm Choáng.
4. Chỉ số Giảm Sát Thương cao và miễn nhiễm Làm Choáng giúp cô có khả năng sinh tồn tốt.
5. CapsuGirl đặc biệt hiệu quả trong PvP.""",
 "profile/852012": """1. Ithil là Sát Thủ phe Nhân Loại, có khả năng kết thúc trận đấu nhanh.
2. Ithil cộng dồn “Pursue” qua đòn đánh thường và những lần Chặn Đòn. Hiệu ứng này giúp cô gây sát thương lớn lên kẻ địch có HP thấp nhất. Cô còn tự hồi máu khi hạ gục thành công một mục tiêu.
3. Tốc Độ cơ bản khá cao kết hợp với tỷ lệ Chặn Đòn từ kỹ năng bị động giúp Ithil trụ vững.""",
 "profile/852013": """1. Empress Saint là nhân vật phe Nhân Loại có khả năng gây sát thương liên tục và ổn định.
2. Bộ kỹ năng của cô xoay quanh Thiêu Đốt. Cô có cơ hội nhận hiệu ứng tăng cường khi áp dụng Thiêu Đốt; đồng thời có thể giảm thời gian Thiêu Đốt trên đồng minh và tăng thời gian Thiêu Đốt trên kẻ địch.
3. Bản thân Empress Saint miễn nhiễm Thiêu Đốt và chịu ít sát thương hơn từ kẻ địch đang Thiêu Đốt.
4. Nhờ các kỹ năng bị động, cô đặc biệt phù hợp với đội hình chuyên áp dụng Thiêu Đốt, chẳng hạn Mio và Sonya.""",
 "profile/852014": """1. Rogue là nhân vật gây sát thương phe Nhân Loại, đồng thời có sức chống chịu tốt.
2. Kỹ năng chủ động ưu tiên kẻ địch có HP cao nhất. Kết hợp “Additional Chips” và “Royal Flush”, cô có thể gây sức ép lên cả đội địch.
3. Rogue áp dụng “Dauntless” để phản lại sát thương nhận vào và dùng “Disrespect” giúp bản thân miễn nhiễm hiệu ứng khống chế.""",
 "profile/852015": """1. Mika là Chiến Binh phe Nhân Loại, thường đảm nhiệm vị trí hàng đầu.
2. Cô có khả năng Khiêu Khích, thu hút đòn tấn công của đối phương.
3. Mika có sức chống chịu và Giảm Sát Thương cao.
4. Từ hiệp thứ 3, Mika được tăng cường mạnh: đòn đánh thường và kỹ năng chủ động gây sát thương Chí Mạng không thể bị Chặn Đòn.
5. Khiêu Khích là một hiệu ứng khống chế, nên sẽ kém hiệu quả trước các nhân vật có Kháng Khống Chế cao như Michael và Esau & Jacob, đồng thời có thể bị hóa giải.""",
 "profile/852016": """1. Teresa là nhân vật đa dụng thuộc phe Nhân Loại.
2. Cô có thể giam kẻ địch trong “Blade Prison”, khiến chúng không thể hành động.
3. Teresa tiêu hao “Righteous Might” để xóa Dấu Ấn và chuyển hiệu ứng khống chế sang kẻ địch.
4. Khi HP thấp hơn 30%, Teresa có thể hoán đổi lượng HP với kẻ địch có HP hiện tại cao nhất để tự hồi phục, nhưng chỉ khi HP của cô thấp hơn mục tiêu.
5. Các kỹ năng cần “Righteous Might” sẽ không kích hoạt nếu cô không đủ cộng dồn.
“Blade Prison” không vô hiệu hóa hiệu ứng tăng cường từ kỹ năng bị động và không ngăn kỹ năng bị động kích hoạt khi nhân vật tử trận. Hiệu ứng “Galaxy” của Vivian vẫn hoạt động, nhưng “Blade Prison” có thể ngăn Vivian kích hoạt các kỹ năng khác khi đang bị giam.""",
})

# Second editorial pass: source-specific tactics, conditions and target priority.
OVERRIDES.update({
 "profile/852017": """1. Monica là nhân vật hỗ trợ thuộc phe Nhân Loại.
2. Cô tăng mạnh sức chống chịu và khả năng tấn công cho đồng minh. Monica ưu tiên hỗ trợ đồng minh đứng ngay sau vị trí của mình trong đội hình.
3. Khi đồng minh sắp nhận sát thương chí tử, Monica có thể bảo vệ để người đó bỏ qua cả sát thương chí tử lẫn mọi sát thương còn lại trong hiệp. Mỗi đồng minh chỉ được hiệu ứng này cứu một lần trong mỗi trận.""",
 "profile/852019": """1. Eve là nhân vật hỗ trợ thuộc phe Nhân Loại.
2. Cô bảo vệ đồng đội bằng hiệu ứng Khiên Ma Thuật, đồng thời dùng “Hộ Vệ Khuyển” để hồi HP cho họ theo HP tối đa.
3. Khi Eve sử dụng đòn đánh thường, cô có cơ hội xóa một hiệu ứng khống chế khỏi đồng minh.""",
 "profile/852020": """1. Azucena là nhân vật gây sát thương thuộc phe Nhân Loại.
2. Khi chịu sát thương từ đòn đánh thường hoặc kỹ năng chủ động của kẻ địch đang mang “Lông Công”, cô được giảm sát thương nhận vào và chuyển một phần sát thương đó thành Khiên Ma Thuật có lượng Điểm Khiên (BP) tương ứng.
3. Azucena có thể gây “Mê Hoặc”: mục tiêu chịu sát thương ngay khi bị áp dụng và vào đầu mỗi hiệp. Kẻ địch bị Mê Hoặc còn chịu nhiều sát thương hơn từ các hiệu ứng sát thương theo thời gian.""",
 "profile/853001": """1. Priestess là một trong những nhân vật gây sát thương chủ lực của phe Quái Vật.
2. Đòn đánh thường của cô tấn công toàn bộ kẻ địch.
3. Trong PvE, các Dấu Ấn mà Priestess áp dụng lên mục tiêu có thể cộng dồn, khiến sát thương do cô gây ra tăng dần.
4. Cách nhanh nhất để tích Dấu Ấn là xếp thêm một Priestess cùng đội.
5. Priestess không miễn nhiễm khống chế nên cần nhân vật hỗ trợ để bảo đảm kỹ năng được kích hoạt.""",
 "profile/853002": """1. Alice là Chiến Binh phe Quái Vật, thường đứng ở hàng trước.
2. Kỹ năng chủ động của Alice đặc biệt khắc chế Chiến Binh, phù hợp đối đầu đội hình có nhiều nhân vật hệ này.
3. Cô tự hồi HP sau khi chịu đòn; các kỹ năng khác của Alice cũng bổ trợ cho khả năng hồi phục ấy.""",
 "profile/853003": """1. Nia là nhân vật gây sát thương thuộc phe Quái Vật.
2. Cô có thể khiến kẻ địch Trúng Độc bằng nhiều cách.
3. Nia phối hợp tốt với các nhân vật có kỹ năng liên quan đến Trúng Độc để tăng hiệu quả cả đội.""",
 "profile/853004": """1. Muppet là nhân vật gây sát thương thuộc phe Quái Vật, sở hữu Giáp cơ bản cao.
2. Kỹ năng chủ động gây sát thương dựa trên HP tối đa của mục tiêu, đồng thời tăng Tấn Công và Xuyên Giáp cho Muppet. Đòn đánh thường còn có thể đánh cắp Giáp của kẻ địch, nên cô rất hữu ích trong PvE.
3. Sau một vài hiệp, Muppet được tăng Chí Mạng và Sát Thương Chí Mạng. Cần giúp cô tồn tại đủ lâu để phát huy toàn bộ sức mạnh.""",
 "profile/853005": """1. Nobunaga là nhân vật gây sát thương phe Quái Vật với tỷ lệ Chí Mạng cao.
2. Cô giảm Chí Mạng và Sát Thương Chí Mạng của kẻ địch, đồng thời tăng Sát Thương Chí Mạng của bản thân, nhờ vậy hoạt động tốt trong nhiều chế độ.
3. Nobunaga dễ bị khống chế; đội hình nên có nhân vật giúp cô chống hoặc giải hiệu ứng khống chế.""",
 "profile/853006": """1. Silvia là Chiến Binh phe Quái Vật, có HP rất cao và thường đứng hàng trước.
2. Cô khó bị hạ gục trong một hiệp, còn kỹ năng chủ động có thể hỗ trợ đồng minh.
3. Silvia là lựa chọn đáng tin cậy khi đội cần nhân vật chịu sát thương thay cho đồng đội.""",
 "profile/853007": """1. Turin là Chiến Binh phe Quái Vật, thường đứng hàng trước và có thể phản công toàn bộ kẻ địch cùng lúc.
2. Khi bị tấn công, Turin phản công tất cả kẻ địch, tạo tiềm năng gây sát thương lớn. Cô còn có xác suất miễn nhiễm khống chế để bảo đảm đòn phản công được kích hoạt.
3. Bộ kỹ năng giúp Turin hữu ích cả trong PvP lẫn PvE.""",
 "profile/853008": """1. Toyo là nhân vật gây sát thương thuộc phe Quái Vật.
2. Cô có nhiều cách áp dụng hiệu ứng Thiêu Đốt lên kẻ địch.
3. Lượng HP cao giúp Toyo đủ sức trụ vững để phát huy bộ kỹ năng của mình.""",
 "profile/853009": """1. Masamune là Chiến Binh phe Quái Vật, thường được xếp hàng trước.
2. Kỹ năng chủ động có xác suất Làm Choáng mục tiêu, giúp đội chiếm lợi thế.
3. Cô còn có thể phản công sau khi chịu sát thương Chí Mạng.""",
 "profile/853010": """1. Hexa là nhân vật gây sát thương bộc phát thuộc phe Quái Vật.
2. Khi Tiến Hóa lên 6 sao, kỹ năng chủ động của cô nhắm vào hàng sau, còn đòn đánh thường ưu tiên kẻ địch có HP thấp nhất. Nhờ đó Hexa gây áp lực lớn lên các chủ lực sát thương của đối phương.
3. Từ 9 sao, Hexa còn tự hồi HP khi tấn công kẻ địch, nâng cao khả năng sinh tồn.""",
 "profile/853011": """1. Psychic là nhân vật hỗ trợ phổ biến của phe Quái Vật.
2. Cô làm suy yếu kẻ địch và cung cấp thêm Năng Lượng cho đồng minh, giúp đội sử dụng kỹ năng gây sát thương hiệu quả hơn trong PvE.
3. Khi HP giảm xuống 50%, Psychic có thể khống chế diện rộng toàn bộ đội địch (mỗi trận một lần), tạo lợi thế lớn trong PvP.""",
 "profile/853012": """1. N-Gen Iron Fist là nhân vật gây sát thương, sức mạnh tăng mạnh khi có kẻ địch bị Làm Choáng.
2. Khi một nhân vật bị Làm Choáng, cô được tăng Tấn Công và tự hồi HP. Nếu phải chịu sát thương vượt quá 50% HP tối đa từ 1 đòn đánh, cô cũng có thể Làm Choáng kẻ tấn công.
3. Nên trang bị Cổ Vật tăng Năng Lượng hoặc ghép đội cùng các nhân vật gây Làm Choáng để phát huy sức mạnh.""",
 "profile/853013": """1. Trinity là nhân vật chủ lực gây sát thương mạnh thuộc phe Quái Vật.
2. Đòn đánh thường ưu tiên kẻ địch có HP thấp nhất.
3. Kỹ năng của cô áp dụng Chảy Máu và Dấu Ấn “Disintegration” lên kẻ địch, giúp Trinity tự gây sát thương lớn mà không phụ thuộc nhiều vào hỗ trợ, đồng thời tăng sát thương cho đồng minh.""",
 "profile/853014": """1. Skye là nhân vật hỗ trợ thuộc phe Quái Vật.
2. Kỹ năng chủ động gây thêm sát thương dựa trên chênh lệch Tốc Độ giữa Skye và mục tiêu; đồng thời cộng dồn Dấu Ấn “Anoxia” để giảm Tốc Độ của mục tiêu.
3. Đòn đánh thường ưu tiên kẻ địch có Tốc Độ cao nhất và làm chậm chúng.
4. Skye còn tăng Tốc Độ cho cả đội và nhận thêm hiệu ứng bảo vệ khi HP thấp.""",
 "profile/853015": """1. Estel là nhân vật gây sát thương thuộc phe Quái Vật.
2. Khi phối hợp cùng nhân vật có khả năng cộng dồn hiệu ứng bất lợi, Estel gây thêm sát thương và có cơ hội kéo dài số hiệp duy trì hiệu ứng đó.
3. Cô có thể sao chép hiệu ứng Sát Thương Theo Thời Gian và Giảm Chỉ Số từ kẻ địch sang các mục tiêu khác.""",
 "profile/853016": """1. Sivney là nhân vật hỗ trợ thuộc phe Quái Vật.
2. Cô hy sinh một phần HP bản thân để Hồi Máu cho đồng minh, giúp họ sống sót lâu hơn.
3. Sivney áp dụng hiệu ứng bất lợi khiến kẻ địch chịu thêm sát thương.
4. Khi Sivney tử trận, một đồng minh đứng cạnh cô được hồi HP và Năng Lượng, có thể giúp đảo ngược cục diện.""",
 "profile/853017": """1. Robbie là Chiến Binh phe Quái Vật, thường đứng hàng trước.
2. Khi HP giảm, cô tăng khả năng tấn công và sinh tồn.
3. Nếu HP xuống dưới 30%, Robbie có thể tự hồi một lượng HP lớn (mỗi trận chỉ một lần).
4. Khi dùng kỹ năng chủ động, Robbie tiêu hao các cộng dồn “Laser Charge”. Mỗi cộng dồn bị tiêu hao khiến hiệu ứng kỹ năng lặp lại một lần lên mục tiêu ngẫu nhiên mới, ngoại trừ việc tiêu hao và hồi HP.
5. Mỗi cộng dồn “Laser Charge” còn tăng Kháng Giảm Năng Lượng, giúp Robbie chống lại kỹ năng rút Năng Lượng của đối phương.""",
 "profile/853018": """1. Cygmar là nhân vật khống chế thuộc phe Quái Vật.
2. Cô có xác suất cao Làm Choáng nhiều kẻ địch.
3. Cygmar có thể tự Hồi Máu và nhận Khiên Ma Thuật để tăng khả năng sống sót.
4. Cô còn tăng Kháng Khống Chế và Độ Chính Xác cho đồng minh, giúp đội gây sát thương hiệu quả hơn.""",
 "profile/853019": """1. Nymphaea là nhân vật gây sát thương thuộc phe Quái Vật.
2. Hiệu ứng “Untainted” hồi HP cho người sở hữu dựa trên lượng HP đã mất và tăng Tấn Công khi họ chịu sát thương từ đòn đánh thường hoặc kỹ năng chủ động của kẻ địch đang bị Chảy Máu.
3. Hiệu ứng “Full Bloom” khiến kẻ địch chịu thêm sát thương dựa trên HP tối đa khi chúng bị áp dụng Chảy Máu.""",
 "profile/854001": """1. Amazon là nhân vật gây sát thương kiêm khống chế thuộc phe Tiên.
2. Đòn đánh thường tấn công 3 kẻ địch ngẫu nhiên.
3. Tốc Độ cơ bản cao giúp Amazon hành động sớm hơn trong hiệp.
4. Kỹ năng có cơ hội Câm Lặng mọi mục tiêu bị đánh trúng; cô còn tăng Giảm Sát Thương và Kháng Khống Chế để tấn công an toàn hơn.""",
 "profile/854002": """1. Bud Elf là Chiến Binh có sức chống chịu tốt thuộc phe Tiên, thường đứng hàng trước.
2. Lượng HP lớn giúp cô chịu nhiều sát thương. Bud Elf còn tự hồi HP nhờ những đòn Chí Mạng của đồng minh, phù hợp vai trò đỡ đòn.
3. Cô áp dụng Thiêu Đốt lên kẻ địch khi dùng kỹ năng chủ động hoặc chịu đòn, qua đó bổ sung sát thương cho đội.""",
 "profile/854003": """1. Himoto là nhân vật gây sát thương bộc phát thuộc phe Tiên.
2. Các kỹ năng bị động tăng Chí Mạng và Sát Thương Chí Mạng cho Himoto. Đòn đánh thường ưu tiên kẻ địch có HP thấp nhất, đe dọa mạnh các mục tiêu ít chống chịu.
3. Kỹ năng chủ động còn gây Chảy Máu lên các mục tiêu hệ Pháp Sư.""",
 "profile/854004": """1. Nani là nhân vật hỗ trợ linh hoạt của phe Tiên, phù hợp nhiều đội hình.
2. Cô tăng Tấn Công và Giáp cho đồng minh, đồng thời giảm hai chỉ số này của kẻ địch.
3. Dù đa dụng, Nani vẫn là nhân vật hỗ trợ và cần phối hợp với các chủ lực mạnh.""",
 "profile/854005": """1. Lavia là nhân vật gây sát thương bộc phát thuộc phe Tiên.
2. Tấn Công cơ bản khá tốt; kỹ năng của cô còn bổ sung khả năng sinh tồn và khống chế.""",
 "profile/854006": """1. Susan là Chiến Binh có khả năng chịu đòn tốt của phe Tiên, thường đứng hàng trước.
2. Giảm Sát Thương và HP cao giúp cô sống sót tốt.
3. Sau khi chịu đòn, Susan có thể phản công và giảm Chí Mạng của kẻ địch. Kỹ năng chủ động còn đánh cắp Giáp của mục tiêu và Hồi Máu cho bản thân, nâng khả năng chống chịu.""",
 "profile/854007": """1. Aquaris là nhân vật linh hoạt thuộc phe Tiên.
2. Cô được tăng những chỉ số khác nhau tùy vị trí trong đội hình: đứng hàng sau giúp tăng khả năng tấn công, còn đứng hàng trước giúp tăng sức chống chịu. Khi HP xuống dưới ngưỡng nhất định, cô còn tăng Tấn Công và Chí Mạng cho bản thân.""",
 "profile/854008": """1. KongMing là nhân vật Hồi Máu xuất sắc thuộc phe Tiên, đồng thời có thể gây sát thương tốt.
2. Cô Hồi Máu cho toàn bộ đồng minh và tăng Tấn Công, Chí Mạng, HP bản thân. Trang bị tăng Tấn Công sẽ đồng thời cải thiện lượng Hồi Máu và sát thương.
3. Khi đạt 9 sao, nếu HP dưới 50%, KongMing có xác suất 100% Câm Lặng toàn bộ kẻ địch (mỗi trận một lần).
4. Cô phù hợp nhiều đội hình và chế độ.""",
 "profile/854009": """1. Pandaria là nhân vật gây sát thương thuộc phe Tiên.
2. Đòn đánh thường tấn công 3 kẻ địch ngẫu nhiên.
3. Pandaria có nhiều cách áp dụng Trúng Độc.
4. Cô gây thêm sát thương lên kẻ địch đang Trúng Độc, phối hợp tốt với các đồng minh dùng kỹ năng hệ Độc.""",
 "profile/854010": """1. Linky là nhân vật hỗ trợ thuộc phe Tiên, tăng sát thương cho đồng đội bằng cách gắn Dấu Ấn lên kẻ địch.
2. Mục tiêu mang Dấu Ấn của Linky sẽ chịu nhiều sát thương hơn từ mỗi đòn đánh; mọi đồng minh đều hưởng lợi từ hiệu ứng này.
3. Linky có thể tự Hồi Máu sau khi gây một đòn Chí Mạng.""",
 "profile/854012": """1. Krystal là nhân vật gây sát thương kiêm khống chế thuộc phe Tiên.
2. Hiệu ứng Kết Tinh kích hoạt chậm giúp hiệu ứng khống chế của cô tác động trọn vẹn lên mục tiêu.
3. Kỹ năng “Mighty Prayer” gần như chắc chắn khống chế mục tiêu của đòn đánh thường nếu mục tiêu không có Kháng Khống Chế cao.
4. Khi mục tiêu bị Kết Tinh, Krystal còn có thể tự Hồi Máu, tăng Tấn Công và khiến mục tiêu Trúng Độc. Cô đặc biệt mạnh trong trận đấu kéo dài.""",
})

# Third editorial pass: higher-tier Fairy, Demon, Angel and Cosmos tactics.
OVERRIDES.update({
 "profile/854013": """1. Joan là nhân vật gây sát thương thuộc phe Tiên.
2. Joan cần cộng dồn “Remnants” để phát huy toàn bộ sức mạnh. Cô nhận cộng dồn này khi đồng minh tấn công hoặc có bất kỳ nhân vật nào tử trận. Khi dùng kỹ năng chủ động, Joan tiêu hao toàn bộ “Remnants” để gây sát thương lớn.
3. Kỹ năng “Oath of Peach Garden” giúp Joan hỗ trợ hiệu quả trong nhiều kiểu đội hình.""",
 "profile/854014": """1. Vera là nhân vật hỗ trợ thuộc phe Tiên, vừa Hồi Máu cho đồng minh vừa làm suy yếu kẻ địch.
2. Các kỹ năng hỗ trợ đa dạng giúp Vera phù hợp hầu hết đội hình. “Diminish” khiến địch chịu thêm sát thương và giảm sát thương chúng gây ra. “Lullaby” hồi HP cho đồng minh và gây sát thương lên địch; lượng hồi và sát thương phụ thuộc chỉ số Tấn Công của đồng minh nhận “Lullaby”.
3. Kỹ năng bị động thứ 3 còn cho phép Vera hoán đổi Tốc Độ với một kẻ địch ngẫu nhiên có Tốc Độ cao hơn, giúp cô hành động sớm hơn từ hiệp thứ 2 trở đi.""",
 "profile/854015": """1. Holly là nhân vật hỗ trợ thuộc phe Tiên.
2. Bằng cách cộng dồn “Parasites”, Holly giảm Tấn Công và Lượng Hồi Máu Nhận của kẻ địch. Hiệu ứng “Parasites” không thể bị xóa.
3. Đầu trận, “Natural Order” khiến kẻ địch có đòn đánh thường, kỹ năng chủ động hoặc kỹ năng bị động nhắm mục tiêu ngẫu nhiên phải ưu tiên tấn công Holly. Nhờ đó, các đồng minh, đặc biệt là chủ lực, có thêm thời gian gây sát thương. Tuy nhiên, kẻ địch đang bị Khiêu Khích vẫn ưu tiên tấn công nhân vật đã Khiêu Khích chúng.""",
 "profile/854016": """1. Kassy là nhân vật hỗ trợ thuộc phe Tiên.
2. Kỹ năng chủ động và đòn đánh thường của cô chắc chắn gây Chí Mạng lên mục tiêu có HP thấp; cô còn gây sát thương bổ sung và tự hồi HP theo tổng sát thương đã gây.
3. Khi dùng kỹ năng chủ động, Kassy ban “Cat Eyes” cho đồng minh, giúp họ gây thêm sát thương và hồi HP theo lượng sát thương gây ra.
4. Kassy tăng cường toàn đội khi bắt đầu trận và cuối mỗi hiệp. Nhân vật hệ Sát Thủ được hưởng gấp đôi hiệu quả; các hiệu ứng tăng cường từ nhiều Kassy có thể cộng dồn.""",
 "profile/854017": """1. Aurora là nhân vật hỗ trợ thuộc phe Tiên.
2. Khi trên sân có từ 2 kẻ địch trở lên, kỹ năng chủ động của cô gây sát thương nảy giữa các mục tiêu, mỗi lần chọn 1 kẻ địch ngẫu nhiên.
3. Số lần nảy càng nhiều, sát thương và xác suất gây khống chế càng tăng.
4. Sau khi mở kỹ năng bị động tương ứng, đòn đánh thường của Aurora gây Trúng Độc. Sát thương Độc không thể vượt quá 1500% Tấn Công của cô.
5. Khi chịu đòn đánh thường hoặc sát thương từ kỹ năng bị động, Aurora giảm sát thương mà kẻ tấn công gây ra trong trận.
6. Aurora còn gây thêm sát thương lên kẻ địch đang chịu hiệu ứng Kết Tinh.""",
 "profile/854018": """1. K.M. Enlightened là nhân vật hỗ trợ thuộc phe Tiên.
2. Kỹ năng chủ động của cô giảm Tấn Công của kẻ địch và áp dụng hiệu ứng bất lợi gây sát thương về sau, đồng thời có tác dụng khống chế diện rộng.
3. Trong trận, cô ban hiệu ứng tăng cường cho đồng minh, giúp họ gây sát thương mạnh hơn.""",
 "profile/855002": """1. Amelia là nhân vật gây sát thương kiêm khống chế thuộc phe Ác Quỷ.
2. Khi Thức Tỉnh lên 10 sao, kỹ năng chủ động của Amelia tấn công toàn bộ kẻ địch và có cơ hội đánh cắp Năng Lượng của chúng. Xác suất Hóa Đá từ đòn đánh thường tăng lên; kỹ năng bị động còn tăng Tốc Độ, HP và Sát Thương Kỹ Năng, giúp cô hữu ích trong nhiều tình huống.
3. Nhân vật phe Ác Quỷ thường khó nâng cấp hơn; cần phân bổ tài nguyên hợp lý nếu muốn đưa Amelia lên cấp sao cao.""",
 "profile/855003": """1. Wraith là nhân vật gây sát thương bộc phát mạnh thuộc phe Ác Quỷ.
2. Mỗi khi đồng minh dùng kỹ năng chủ động, kỹ năng bị động của Wraith cho cô thêm Năng Lượng để sử dụng kỹ năng chủ động thường xuyên hơn.
3. Nếu HP của kẻ địch cao hơn Wraith, cô gây thêm sát thương dựa trên tỷ lệ HP tối đa của mục tiêu, tối đa bằng 1500% Tấn Công của bản thân. Vì vậy Wraith rất hữu ích khi đánh Boss, gồm Boss Bạn Bè và Boss Bang Hội.
4. Kỹ năng bị động còn tăng Năng Lượng và HP, cải thiện khả năng sinh tồn của cô.
5. Nhân vật phe Ác Quỷ khó nâng cấp, nên cần quản lý tài nguyên cẩn thận trước khi tăng sao.""",
 "profile/855004": """1. Scythe là Chiến Binh có khả năng hồi sinh thuộc phe Ác Quỷ.
2. Cô gây sát thương lớn bằng “Dấu Ấn Hiệp” và có thể Hóa Đá kẻ địch. Khả năng tự Hồi Máu và hồi sinh giúp Scythe trụ ở hàng trước, chịu sát thương thay đồng minh.
3. Khả năng hồi sinh phối hợp tốt với Esau & Jacob (gây thêm sát thương toàn địch) hoặc Saint (tăng Tấn Công và Sát Thương Kỹ Năng), từ đó khuếch đại sát thương của đội.
4. Do nhân vật phe Ác Quỷ khó nâng cấp, nên cần lập kế hoạch tài nguyên trước khi tăng sao.""",
 "profile/855005": """1. Lucifer là nhân vật chuyên gây sát thương theo thời gian thuộc phe Ác Quỷ.
2. Mỗi khi đồng minh dùng kỹ năng chủ động, Lucifer nhận thêm Năng Lượng và Sát Thương Kỹ Năng, giúp cô tung kỹ năng thường xuyên hơn. Sát Thương Kỹ Năng tăng dần khi trận đấu kéo dài; cộng với Chảy Máu từ kỹ năng chủ động, cô có thể gây sát thương rất lớn.
3. Lucifer phát huy tốt khi ghép đội với nhân vật liên tục dùng kỹ năng chủ động, giúp cô kết thúc trận nhanh hơn.
4. Kỹ năng chủ động khắc chế Xạ Thủ, phù hợp đối phó đội hình nhiều Xạ Thủ như trong Thử Thách.
5. Nên cân nhắc tài nguyên vì nhân vật phe Ác Quỷ thường khó nâng cấp hơn.""",
 "profile/855006": """1. Esau & Jacob là cặp nhân vật gây sát thương thuộc phe Ác Quỷ.
2. Hai người có Tốc Độ cao, cùng với Giảm Sát Thương, Kháng Khống Chế và khả năng rút Năng Lượng của địch. Nhờ vậy họ vừa gây sát thương vừa hỗ trợ đội trong nhiều chế độ.
3. Khi phối hợp cùng Giana và Diva, hiệu ứng kích hoạt lúc các nhân vật đó tử trận có thể gây lượng sát thương lớn lên địch.
4. Nhân vật phe Ác Quỷ khó nâng cấp; cần cân nhắc tài nguyên khi tăng sao.""",
 "profile/855007": """1. Kratos là nhân vật đa dụng thuộc phe Ác Quỷ.
2. Mỗi kỹ năng của cô đều tăng khả năng tấn công lẫn sinh tồn; Kratos còn đối phó tốt với kẻ địch có HP cao.
3. Kỹ năng chủ động và kỹ năng bị động “Killing Intent” có cơ hội gây “Terrorize”, đặc biệt hiệu quả trước kẻ địch phụ thuộc đòn đánh thường. Hiệu ứng này còn cản chúng nhận Năng Lượng từ đòn đánh thường.
4. Muốn phát huy toàn bộ sức mạnh của Kratos, cần trang bị tốt và cấp sao cao; nên quản lý tài nguyên hợp lý.""",
 "profile/855008": """1. Izanami là nhân vật hỗ trợ bảo vệ đồng minh thuộc phe Ác Quỷ.
2. Kỹ năng chủ động ban “Lily Shield” cho đồng minh, biến sát thương của đòn đánh thường hoặc kỹ năng chủ động tiếp theo mà họ phải nhận thành Hồi Máu.
3. Kỹ năng bị động áp dụng “Lời Nguyền Hồi Phục” lên mục tiêu, biến lần Hồi Máu tiếp theo của mục tiêu thành sát thương.
4. “Lily Shield” và “Lời Nguyền Hồi Phục” không thể kích hoạt lẫn nhau.""",
 "profile/855009": """1. Apate là nhân vật gây sát thương mạnh thuộc phe Ác Quỷ.
2. Kỹ năng chủ động đặc biệt khắc chế kẻ địch có Năng Lượng cao.
3. Đòn đánh thường rút Năng Lượng mục tiêu và gây thêm sát thương dựa trên lượng Năng Lượng đã rút.
4. Ngay cả khi Apate bị hạ gục, cô vẫn có thể hồi sinh; trong lúc cô vắng mặt, Volo xuất hiện thay thế để tiếp tục gây sát thương cho đội.""",
 "profile/855010": """1. Frexie là nhân vật gây sát thương thuộc phe Ác Quỷ.
2. Đòn đánh thường nhắm vào kẻ địch có tỷ lệ HP hiện tại thấp nhất và gắn “Dấu Ấn Sao Tối” lên chúng. Nếu mục tiêu đã có Dấu Ấn này, nó sẽ chịu thêm sát thương theo HP tối đa, giúp Frexie kết liễu địch.
3. Kỹ năng bị động “Phew that was close” giảm Giáp, Giảm Sát Thương, Tiêu Hao Sát Thương, tỷ lệ Chặn Đòn và Né Tránh của kẻ địch có tỷ lệ HP thấp nhất vào đầu trận và cuối mỗi hiệp, giúp đồng minh gây thêm sát thương.""",
 "profile/855011": """1. Maia là nhân vật đa dụng thuộc phe Ác Quỷ.
2. Kỹ năng chủ động gây sát thương lên 4 kẻ địch ngẫu nhiên, có cơ hội xóa 1 hiệu ứng tăng cường trên mỗi mục tiêu.
3. Khi phải chịu sát thương chí tử, Maia có thể bỏ qua sát thương đó và miễn nhiễm mọi sát thương cho đến hết hiệp.
4. Maia cộng dồn “Chaos Scars” để giảm HP tối đa của địch. Phần HP tối đa bị giảm không thể phục hồi bằng Hồi Máu; mức giảm tối đa là 40%.""",
 "profile/855013": """1. Hadea là nhân vật gây sát thương thuộc phe Ác Quỷ.
2. Kỹ năng chủ động tấn công 2 kẻ địch có HP thấp nhất và áp dụng “Irreversible Death” cùng “Doom's Arrival” lên toàn bộ kẻ địch.
3. Khi Hadea hoặc đồng minh tử trận, những hiệu ứng liên quan có thể thay đổi đáng kể cục diện.
4. Cuối mỗi hiệp, Hadea gây sát thương lên toàn bộ kẻ địch dựa trên lượng HP còn lại của chúng.""",
 "profile/855014": """1. Apollis là nhân vật gây sát thương thuộc phe Ác Quỷ.
2. Kỹ năng chủ động đánh cắp Tấn Công và Giáp của kẻ địch; đòn đánh thường đánh cắp Năng Lượng.
3. Cả hai loại đòn đánh đều tăng xác suất Né Tránh của Apollis.
4. Các hiệu ứng đặc biệt kích hoạt khi cô chịu Khống Chế, hiệu ứng bất lợi khác, sát thương thường hoặc sát thương chí tử.""",
 "profile/856001": """1. Angel là nhân vật đa dụng thuộc phe Thiên Thần.
2. Khi bị tấn công, Angel có thể tự Hồi Máu để duy trì khả năng sinh tồn.
3. Mỗi đòn đánh thường tăng thêm Sát Thương Thánh, giúp cô gây sát thương mạnh hơn khi trận kéo dài.
4. Nhân vật phe Thiên Thần khó nâng cấp hơn; nên lên kế hoạch dùng tài nguyên trước khi tăng sao.""",
 "profile/856002": """1. Gabriel là nhân vật gây sát thương diện rộng bộc phát thuộc phe Thiên Thần.
2. Đòn đánh thường ưu tiên các kẻ địch ở hàng trước.
3. Gabriel có sức chống chịu tốt và khi được đầu tư đầy đủ có thể hấp thụ lượng sát thương lớn.
4. Bộ kỹ năng xoay quanh Chí Mạng: cô gắn Dấu Ấn Chí Mạng lên kẻ địch để kích hoạt khi đòn đánh chí mạng trúng mục tiêu; đồng thời tăng Chí Mạng sau mỗi đòn đánh thường.
5. Nhân vật phe Thiên Thần khó nâng cấp hơn; cần phân bổ tài nguyên hợp lý.""",
 "profile/856003": """1. Michael là nhân vật hỗ trợ có khả năng hồi sinh thuộc phe Thiên Thần.
2. Michael hữu dụng ở nhiều chế độ: từ 10 sao cô miễn nhiễm mọi loại Khống Chế; kỹ năng chủ động vừa gây sát thương vừa Hồi Máu cho đồng minh; khi tử trận, cô có thể hồi sinh với đầy HP.
3. Nhân vật phe Thiên Thần khó nâng cấp hơn; nên cân nhắc tài nguyên khi tăng sao.""",
 "profile/856004": """1. Phoenix là nhân vật gây sát thương thuộc phe Thiên Thần.
2. Tốc Độ cao giúp cô thường được ra đòn trước. Kỹ năng bị động ưu tiên kẻ địch có HP thấp nhất; khi có địch tử trận, Phoenix nhận 100 Năng Lượng và thêm Sát Thương Thánh để sớm dùng kỹ năng chủ động.
3. Phoenix miễn nhiễm Làm Choáng nên thích hợp với nhiều tình huống.
4. Nhân vật phe Thiên Thần khó nâng cấp hơn; cần quản lý tài nguyên hợp lý.""",
 "profile/856005": """1. Raphael là nhân vật hỗ trợ tăng Tốc Độ và Tấn Công cho đồng minh thuộc phe Thiên Thần.
2. Cô vừa Hồi Máu vừa tăng Tốc Độ, Tấn Công cho đội. Ngay cả khi tử trận, Raphael vẫn có thể tiếp tục Hồi Máu cho đồng minh trong vài hiệp.
3. Khả năng sinh tồn cao giúp Raphael hỗ trợ đội đặc biệt tốt trong các trận kéo dài.
4. Nhân vật phe Thiên Thần khó nâng cấp hơn; nên phân bổ tài nguyên trước khi tăng sao.""",
 "profile/856006": """1. Nephilim là nhân vật phe Thiên Thần có thể gây sát thương lớn bằng nhiều cách.
2. Tốc Độ cơ bản cao kết hợp kỹ năng bị động “Duality” cho phép cô dùng kỹ năng chủ động sớm, giúp Dấu Ấn “Equilibrium” phát huy hiệu quả.
3. Kỹ năng chủ động cùng “Sacred Purification” giúp Nephilim gây thêm sát thương lên nhân vật có HP cao. “Embrace of Darkness” tiếp tục gây một đợt sát thương vào cuối mỗi hiệp, giúp cô nhanh chóng hạ những mục tiêu nguy hiểm.
4. Nephilim thuộc phe Thiên Thần nên cần nhiều tài nguyên để nâng cấp; hãy cân nhắc trước khi đưa cô vào đội.""",
 "profile/856007": """1. Uriel là Chiến Binh có khả năng khống chế diện rộng thuộc phe Thiên Thần.
2. Kỹ năng chủ động tăng Sát Thương Thánh. Kỹ năng bị động tăng HP và Giảm Sát Thương, giúp Uriel chịu đòn tốt, đặc biệt khi có nhân vật Hồi Máu hỗ trợ.
3. Uriel áp dụng “Scars of Belinus” lên kẻ địch. Khi có 2 cộng dồn, hiệu ứng chuyển thành “Trial of Belinus”, ngăn mục tiêu kích hoạt kỹ năng bị động.
Lưu ý: “Trial of Belinus” chỉ vô hiệu hóa các kỹ năng bị động cần điều kiện kích hoạt. Nếu Vivian đã áp dụng “Galaxy” trước đó, hiệu ứng ấy vẫn hoạt động, nhưng Vivian không thể chọn mục tiêu “Galaxy” tiếp theo khi đang chịu “Trial of Belinus”.""",
 "profile/856008": """1. Angelica là nhân vật gây sát thương thuộc phe Thiên Thần.
2. Kỹ năng chủ động có cơ chế “Preparation” đặc biệt và tấn công toàn bộ kẻ địch với sát thương lớn. Tăng Sát Thương Thánh và Sát Thương Kỹ Năng sẽ giúp cô mạnh hơn.
3. Trong trận, Angelica cộng dồn “Sun Slayer”; khi dùng kỹ năng chủ động hoặc đòn đánh thường, cộng dồn này truy kích kẻ địch có HP thấp nhất để kết liễu.
4. Hiệu ứng “Dazed” nhắm vào kẻ địch có HP thấp nhất, buộc các loại đòn đánh của mục tiêu chỉ đánh một đối tượng thay vì nhiều đối tượng, giúp đội giảm sát thương nhận vào.""",
 "profile/856009": """1. Gwen & Brigit là cặp nhân vật gây sát thương thuộc phe Thiên Thần.
2. Họ tung nhiều đòn đánh dựa trên số cộng dồn “Gilded Butterfly” trên mục tiêu. Khi mục tiêu có từ 5 cộng dồn trở lên, giữ lại 1 cộng dồn và tiêu hao phần còn lại để gây lượng lớn sát thương bổ sung.
3. Sau Thức Tỉnh, đòn đánh thường chuyển sang tấn công 3 kẻ địch có HP thấp nhất, giúp nhanh chóng kết liễu mục tiêu yếu.
4. Khi đồng minh gây Chí Mạng, Gwen & Brigit được Hồi Máu và tăng Tốc Độ, cải thiện sức chống chịu.
Khi bị kẻ địch mang “Gilded Butterfly” do chính họ áp dụng tấn công, đồng minh ở hàng trước có thể chịu thay một phần sát thương.""",
 "profile/856010": """1. Cupid là nhân vật hỗ trợ Hồi Máu thuộc phe Thiên Thần.
2. Kỹ năng chủ động giảm Tấn Công của kẻ địch, giảm sát thương đồng minh phải chịu và hồi HP nhiều lần.
3. Nếu lượng Hồi Máu từ kỹ năng vượt HP tối đa của mục tiêu, phần dư chuyển thành Điểm Khiên (BP) của Khiên Ma Thuật.
4. Số lần Hồi Máu phụ thuộc cộng dồn “Heartbeat” của Cupid, giúp đồng minh sống sót lâu hơn.""",
 "profile/856011": """1. Poseidia là Chiến Binh thuộc phe Thiên Thần.
2. Kỹ năng chủ động giảm Giáp địch, gây sát thương nhiều lần và tăng Chặn Đòn cho toàn bộ đồng minh.
3. Đòn đánh thường giúp Poseidia tự Hồi Máu và tăng Chặn Đòn cho đồng minh hàng trước.
4. Đầu trận, Poseidia có thể Khiêu Khích toàn bộ kẻ địch. Khi đồng minh Chặn Đòn thành công, cô nhận 1 cộng dồn “Gift of the Sea”, tự hồi HP và có cơ hội Kết Tinh 2 kẻ địch ngẫu nhiên.""",
 "profile/857001": """1. Syrcotte là nhân vật gây sát thương thuộc phe Vũ Trụ.
2. Kỹ năng chủ động gây lượng lớn sát thương xuyên Giáp lên kẻ địch có HP thấp.
3. Đòn đánh thường cũng bỏ qua Giáp và áp dụng “Miasma” lên mục tiêu.
4. Syrcotte có thể giảm sát thương mà kẻ địch có HP thấp nhất gây ra và tự Hồi Máu.
5. Khi đạt đầy Năng Lượng, cô xóa các hiệu ứng Khống Chế, Dấu Ấn và Sát Thương Theo Thời Gian trên bản thân, sau đó được tăng cường bằng “Bùng Nổ Tinh Tú”.""",
 "profile/857002": """1. Elysia là nhân vật khống chế diện rộng thuộc phe Vũ Trụ.
2. Kỹ năng chủ động gây sát thương lên toàn bộ kẻ địch và truy kích dựa trên HP tối đa của mục tiêu. Cô đồng thời xóa tất cả “Primal Colors” trên chúng và kích hoạt các hiệu ứng bất lợi tương ứng.
3. Elysia có thể tô các loại “Primal Colors” khác nhau lên kẻ địch để giảm Tốc Độ, Giáp hoặc Tấn Công.
4. Đầu mỗi hiệp, cô có cơ hội Câm Lặng hoặc gây Khiếp Sợ lên kẻ địch.
5. “Pisces' Gift” tăng Xác Suất Khống Chế Bổ Sung và Giảm Sát Thương Chí Mạng nhận vào. Khi có 3 cộng dồn, đòn đánh thường tiếp theo áp dụng “Primal Blue” lên mục tiêu.""",
 "profile/857003": """1. Effy là nhân vật gây sát thương thuộc phe Vũ Trụ.
2. Kỹ năng chủ động gây nhiều đợt sát thương bộc phát lên kẻ địch.
3. Đòn đánh thường có cơ hội gây “Afterimage”, khiến kẻ địch mang hiệu ứng dễ đánh trượt khi dùng đòn đánh thường hoặc kỹ năng chủ động.
4. Effy giảm Chí Mạng bản thân nhưng tăng giới hạn tối đa của Sát Thương Chí Mạng; sát thương từ kỹ năng bị động vẫn có thể gây Chí Mạng.
5. Cô áp dụng “Kaus Australis” lên địch, khiến hiệu ứng Hồi Máu của chúng bị trì hoãn và chịu thêm sát thương cố định dựa trên HP tối đa mỗi khi bị đòn đánh thường hoặc kỹ năng chủ động tấn công.
6. Kỹ năng chủ động xóa “Kaus Australis” trên địch và thay bằng “Alnasl”, khiến chúng chịu một phần sát thương sau khi dùng đòn đánh thường hoặc kỹ năng chủ động.""",
})

OVERRIDES.update({
 "profile/855012": """1. Promethea là Chiến Binh kiêm khống chế thuộc phe Ác Quỷ.
2. Hiệu ứng “Starflare” tăng khả năng Tiêu Hao Sát Thương và phản lại một phần sát thương mà người mang hiệu ứng phải nhận lên kẻ tấn công.
3. Hiệu ứng “Hellfire” làm giảm Lượng Hồi Máu Nhận, tỷ lệ Chặn Đòn và Năng Lượng nhận được của kẻ địch.
4. Lần đầu HP của Promethea xuống dưới 30%, hoặc khi bắt đầu hiệp 5, cô lập tức hồi HP và được tăng cường sức mạnh đáng kể.""",
})
# Source-verified early Ghost skill descriptions; preserve exact target and trigger.
OVERRIDES.update({
 "skill/851001/75100501": """Kỹ năng chủ động của Sapphire gây sát thương lên kẻ địch hàng sau và có cơ hội Hóa Đá chúng.
Sapphire có Tấn Công cơ bản cao; dùng kỹ năng càng sớm càng phát huy lợi thế.""",
 "skill/851001/75100502": """Kỹ năng tăng cường cho phép đòn đánh thường của Sapphire tấn công toàn bộ kẻ địch hàng trước, đặc biệt làm suy yếu các nhân vật có tỷ lệ Chặn Đòn cao như Guan Yin, Javelin và Nobunaga.""",
 "skill/851001/75100503": """Kỹ năng tăng cường: Tăng Độ Chính Xác và Tấn Công của Sapphire.""",
 "skill/851001/75100504": """Kỹ năng tăng cường: Khi HP xuống dưới ngưỡng nhất định, Sapphire được tăng mạnh Tấn Công trong 3 hiệp. Hiệu ứng chỉ kích hoạt một lần mỗi trận.""",
 "skill/851002/75100801": """Kỹ năng chủ động của Gambler gây sát thương lên 2 kẻ địch ngẫu nhiên và áp dụng Chảy Máu. Nếu mục tiêu là Xạ Thủ, sát thương Chảy Máu được tăng thêm.
Sau khi Gambler Tiến Hóa lên 6 sao, kỹ năng tấn công 3 kẻ địch ngẫu nhiên.
Khi đạt 10 sao, cô còn có thể hồi HP từ kỹ năng này.""",
 "skill/851002/75100802": """Kỹ năng tăng cường: Mỗi đòn đánh của Gambler giúp cô tăng Xuyên Giáp và gây Chảy Máu lên mục tiêu.""",
 "skill/851002/75100803": """Kỹ năng tăng cường: Tăng Độ Chính Xác, giúp các đòn đánh của Gambler ít trượt hơn, đồng thời tăng khả năng gây sát thương.""",
 "skill/851002/75100804": """Kỹ năng Hồi Máu: Khi một kẻ địch bị hạ gục, Gambler hồi HP dựa trên chỉ số Tấn Công của bản thân.""",
 "skill/851003/75100101": """Kỹ năng chủ động của Succuba gây sát thương lên kẻ địch hàng sau và Hồi Máu cho chính cô.
Khi đạt 10 sao, kỹ năng còn có cơ hội Đóng Băng mục tiêu.
Lượng Hồi Máu dựa trên Tấn Công của Succuba và được tăng đáng kể khi cô đạt 10 sao.""",
 "skill/851003/75100102": """Kỹ năng tăng cường: Tăng Độ Chính Xác và HP của Succuba.""",
 "skill/851003/75100103": """Kỹ năng Hồi Máu: Succuba tự hồi HP mỗi khi kẻ địch Chặn Đòn thành công trước một đòn tấn công.""",
 "skill/851003/75100104": """Kỹ năng Hồi Máu: Succuba hồi HP sau mỗi lần bản thân tấn công; hiệu quả hồi phục tăng khi cô đạt 9 sao.""",
 "skill/851004/75100201": """Kỹ năng chủ động của Dracula gây sát thương lên 3 kẻ địch ngẫu nhiên và có cơ hội Làm Choáng nếu mục tiêu là Pháp Sư.
Sau khi Tiến Hóa lên 6 sao, kỹ năng tấn công 4 mục tiêu ngẫu nhiên.
Khi đạt 10 sao, kỹ năng gây thêm sát thương lên các mục tiêu hệ Pháp Sư.""",
 "skill/851004/75100202": """Kỹ năng tăng cường: Tăng Xuyên Giáp, Tấn Công và HP cho Dracula.""",
 "skill/851004/75100203": """Kỹ năng tăng cường: Cải thiện đòn đánh thường của Dracula, giúp cô ưu tiên kẻ địch có HP thấp nhất.""",
 "skill/851004/75100204": """Kỹ năng tăng cường: Khi HP của Dracula xuống dưới ngưỡng nhất định, cô được tăng mạnh Xuyên Giáp và tự Hồi Máu trong 5 hiệp. Hiệu ứng chỉ kích hoạt một lần mỗi trận.""",
 "skill/851005/75100601": """Kỹ năng chủ động của Wu Kong gây sát thương lên 3 kẻ địch ngẫu nhiên. Nếu mục tiêu là Sát Thủ, kỹ năng còn có cơ hội Làm Choáng.
Sau khi Tiến Hóa lên 6 sao, số mục tiêu tăng thành 4.
Khi đạt 10 sao, kỹ năng còn gây Trúng Độc lên các mục tiêu hệ Sát Thủ.
Kỹ năng có sát thương cao và đặc biệt khắc chế Sát Thủ.""",
 "skill/851005/75100602": """Kỹ năng khống chế: Các đòn đánh và kỹ năng của Wu Kong có cơ hội Làm Choáng mục tiêu.""",
 "skill/851005/75100603": """Kỹ năng tăng cường: Wu Kong gây thêm sát thương lên mục tiêu đang bị Làm Choáng.""",
 "skill/851005/75100604": """Kỹ năng tăng cường: Tăng Xuyên Giáp và Tấn Công của Wu Kong.""",
 "skill/851006/75100901": """Kỹ năng chủ động của Fencer gây sát thương lên kẻ địch hàng trước và có cơ hội Đóng Băng chúng, đồng thời Hồi Máu cho bản thân.""",
 "skill/851006/75100902": """Kỹ năng khống chế: Khi Fencer chịu sát thương, cô có cơ hội Đóng Băng kẻ tấn công; xác suất càng cao nếu đối phương là Chiến Binh.""",
 "skill/851006/75100903": """Kỹ năng tăng cường: Tăng Tấn Công, HP và Giáp của Fencer, đồng thời giúp cô miễn nhiễm Đóng Băng.""",
 "skill/851006/75100904": """Kỹ năng Hồi Máu: Khi HP của Fencer xuống dưới ngưỡng nhất định, cô tự hồi một lượng HP lớn. Mỗi trận chỉ kích hoạt một lần.""",
})

OVERRIDES.update({
 "skill/851007/75100301": """Kỹ năng chủ động của Wildtress ưu tiên kẻ địch có HP thấp nhất và giảm Tấn Công của mục tiêu.
Khi Wildtress đạt 10 sao, kỹ năng còn có cơ hội gây thêm sát thương.""",
 "skill/851007/75100302": """Kỹ năng tăng cường: Tăng HP và Xuyên Giáp của Wildtress.""",
 "skill/851007/75100303": """Kỹ năng tăng cường: Mỗi đòn tấn công giúp Wildtress tăng Xuyên Giáp và Chí Mạng.""",
 "skill/851007/75100304": """Kỹ năng tăng cường: Wildtress được tăng mạnh Tấn Công khi HP xuống dưới ngưỡng nhất định.""",
 "skill/851008/75101001": """Kỹ năng chủ động của Sakura gây sát thương lên kẻ địch hàng sau, có cơ hội Hóa Đá và giảm Giáp của chúng.""",
 "skill/851008/75101002": """Kỹ năng tăng cường: Tăng Tấn Công, HP và Giáp của Sakura, đồng thời giúp cô miễn nhiễm Hóa Đá.""",
 "skill/851008/75101003": """Kỹ năng tăng cường: Đổi mục tiêu đòn đánh thường của Sakura thành kẻ địch hàng sau và tăng sát thương lên mục tiêu đang bị Hóa Đá.""",
 "skill/851009/75100401": """Kỹ năng chủ động của Giana gây sát thương diện rộng lên toàn bộ kẻ địch và có cơ hội Câm Lặng các mục tiêu hệ Chiến Binh.
Khi Giana đạt 10 sao, kỹ năng còn tăng Tấn Công cho bản thân.""",
 "skill/851009/75100402": """Kỹ năng tăng cường: Sau khi bất kỳ đồng minh nào bị hạ gục, Giana được tăng Chí Mạng và Tấn Công.""",
 "skill/851009/75100404": """Kỹ năng cốt lõi của Giana: Khi cô tử trận, kỹ năng kích hoạt và gây lượng lớn sát thương diện rộng lên toàn bộ kẻ địch.""",
 "skill/851010/75100701": """Kỹ năng chủ động của Ennmaya gây sát thương lên một kẻ địch ngẫu nhiên ở hàng sau, khiến mục tiêu Trúng Độc và có cơ hội Làm Choáng.
Sau khi Tiến Hóa lên 6 sao, số mục tiêu tăng thành 2.
Khi đạt 10 sao, kỹ năng còn tăng Giảm Sát Thương cho Ennmaya.
Kỹ năng phối hợp tốt với các đồng minh sử dụng hiệu ứng Trúng Độc.""",
 "skill/851010/75100702": """Kỹ năng tăng cường: Tăng Xuyên Giáp, Tấn Công, HP và sát thương của Ennmaya lên các mục tiêu đang Trúng Độc.""",
 "skill/851010/75100703": """Kỹ năng tăng cường: Các đòn đánh của Ennmaya có cơ hội Làm Choáng mục tiêu.""",
 "skill/851010/75100704": """Kỹ năng tăng cường: Khi HP của Ennmaya xuống dưới ngưỡng, cô gây Trúng Độc lên 2 kẻ địch ngẫu nhiên ở hàng sau (mỗi trận một lần).
Khi đạt 10 sao, hiệu ứng Trúng Độc sẽ tác động lên toàn bộ kẻ địch hàng sau.""",
 "skill/851011/75101101": """Kỹ năng chủ động của Valeera gây sát thương lên 4 kẻ địch ngẫu nhiên, khiến chúng Trúng Độc và có cơ hội Đóng Băng hoặc Hóa Đá.""",
 "skill/851011/75101102": """Kỹ năng tăng cường: Đòn đánh thường của Valeera chuyển sang tấn công 2 kẻ địch ngẫu nhiên và đánh cắp Tấn Công của chúng, gián tiếp giúp cả đội chịu đòn tốt hơn.""",
 "skill/851011/75101103": """Kỹ năng tăng cường: Tăng Tấn Công, Chí Mạng và HP của Valeera.""",
 "skill/851011/75101104": """Kỹ năng Hồi Máu: Mỗi khi kẻ địch bị Hóa Đá hoặc Đóng Băng, Valeera tự hồi HP và phục hồi Năng Lượng.
Kỹ năng giúp cô vừa sinh tồn tốt hơn vừa dùng kỹ năng tấn công thường xuyên hơn.""",
 "skill/851012/75101201": """Kỹ năng tấn công của Fenrir gây sát thương lên 3 kẻ địch ngẫu nhiên; sát thương bổ sung phụ thuộc vị trí của chúng và kỹ năng gây Chảy Máu.
Khi Fenrir đạt 10 sao, tỷ lệ sát thương kỹ năng tăng lên 206%; Chảy Máu còn giúp cô phối hợp với nhân vật tăng sát thương hiệu ứng này.
Đòn đánh chắc chắn Chí Mạng nếu trúng mục tiêu hàng sau, nhờ vậy Fenrir có thể uy hiếp cả các chủ lực được đồng đội bảo vệ.""",
 "skill/851012/75101202": """Kỹ năng tăng cường: Tăng HP, Tấn Công, Xuyên Giáp và tỷ lệ Chặn Đòn cho Fenrir.
Xuyên Giáp giúp cô gây thêm sát thương.
Tỷ lệ Chặn Đòn cao giúp cô kích hoạt “Desperado” thường xuyên hơn.""",
 "skill/851012/75101203": """Kỹ năng tăng cường: Mỗi lần kỹ năng chủ động được kích hoạt, Fenrir được cộng thêm Tấn Công và Sát Thương Chí Mạng.
Các cộng dồn này không tự hết hạn trong trận, giúp Fenrir ngày càng mạnh khi giao tranh kéo dài.""",
 "skill/851012/75101204": """Kỹ năng cốt lõi của Fenrir: Sau khi Chặn Đòn thành công 3 lần, cô xóa mọi hiệu ứng khống chế trên bản thân, phản công 3 kẻ địch ngẫu nhiên và tự Hồi Máu.
Đây là kỹ năng quan trọng giúp Fenrir sống lâu hơn và gây nhiều sát thương lên mục tiêu có HP cao.""",
})

# Senior-character skill review: publisher-specific triggers, not machine paraphrases.
OVERRIDES.update({
 "skill/855012/75501101": """Kỹ năng chủ động của Promethea gây sát thương dựa trên chỉ số Tấn Công của mục tiêu lên 3 kẻ địch ngẫu nhiên, giảm Năng Lượng của chúng và có cơ hội Khiêu Khích.
Cô còn tiêu hao một phần HP bản thân để gây sát thương dựa trên HP tối đa của mình lên kẻ địch hàng trước, đồng thời ban hiệu ứng “Starflare” cho đồng minh hàng sau, giúp giảm sát thương nhận vào và phản sát thương.""",
 "skill/855012/75501103": """Kỹ năng tăng cường: Đầu trận, Promethea đánh cắp Tốc Độ và Năng Lượng của một kẻ địch, đồng thời ban “Starflare” cho đồng minh hàng sau để giảm sát thương nhận vào và phản lại một phần sát thương.
Đòn đánh thường của Promethea tiêu hao HP bản thân để ban Khiên Ma Thuật cho đồng minh hàng sau, đồng thời áp dụng “Hellfire” lên kẻ địch hàng trước, giảm Lượng Hồi Máu Nhận, tỷ lệ Chặn Đòn và lượng Năng Lượng chúng nhận được.""",
 "skill/855012/75501104": """Kỹ năng tăng cường: Lần đầu HP của Promethea giảm xuống dưới 30% hoặc khi bắt đầu hiệp 5, cô lập tức hồi HP và được tăng cường:
Đòn đánh thường và kỹ năng chủ động không còn tiêu hao HP; kỹ năng chủ động còn gây Thiêu Đốt lên kẻ địch hàng sau.
Khi ban “Starflare”, Promethea tăng hiệu quả Tiêu Hao Sát Thương cho người sở hữu. Nếu Promethea đứng hàng trước, cô cũng có thể nhận hiệu ứng này và lượng sát thương được giảm sẽ gấp đôi.
Khi áp dụng “Hellfire”, cô khiến mục tiêu chịu thêm sát thương.""",
 "skill/856006/75600601": """Kỹ năng chủ động của Nephilim gây sát thương bỏ qua Giáp lên 4 kẻ địch ngẫu nhiên và đặt Dấu Ấn “Equilibrium” lên từng mục tiêu.
Nhờ Tốc Độ cao, Dấu Ấn có thể phát huy hiệu quả gần như ngay lập tức, khắc chế những kẻ địch phụ thuộc vào kỹ năng chủ động để gây sát thương.""",
 "skill/856006/75600602": """Kỹ năng tăng cường: Tăng HP, Sát Thương Thánh, Giảm Sát Thương và Tốc Độ cho Nephilim, giúp cô vừa sống sót lâu hơn vừa gây sát thương mạnh hơn.""",
 "skill/856006/75600603": """Kỹ năng tăng cường: Đòn đánh thường của Nephilim nhắm vào kẻ địch có HP cao nhất, gây thêm sát thương dựa trên HP tối đa của chúng và tự Hồi Máu.
Nhờ vậy, Nephilim khắc chế mục tiêu nhiều HP và duy trì khả năng sinh tồn khi tấn công.""",
 "skill/856006/75600604": """Kỹ năng tăng cường: Nephilim gây lượng sát thương lớn lên các chủ lực gây sát thương của đối phương.
Kỹ năng còn giảm hiệu quả Hồi Máu mà kẻ địch nhận được, giúp Nephilim chiếm lợi thế khi trận đấu kéo dài.
Ngoài ra, hiệu ứng tự hồi HP tiếp tục tăng khả năng sinh tồn của cô.""",
 "skill/856007/75600701": """Kỹ năng chủ động của Uriel gây sát thương nhiều lần lên 1 kẻ địch ngẫu nhiên và đặt 1 cộng dồn “Scars of Belinus” lên mục tiêu; sau khi kích hoạt, Sát Thương Thánh của Uriel tăng.
Khi đạt 10 sao, kỹ năng còn có cơ hội đặt thêm 1 cộng dồn “Scars of Belinus” lên kẻ địch đã có hiệu ứng này.""",
 "skill/856007/75600702": """Kỹ năng tăng cường: Tăng HP, Sát Thương Thánh, Kháng Khống Chế và Giảm Sát Thương của Uriel, giúp cô vừa chịu đòn tốt hơn vừa gây thêm sát thương.""",
 "skill/856007/75600703": """Kỹ năng tăng cường: Đòn đánh thường của Uriel nhắm vào một kẻ địch ngẫu nhiên và đặt 1 cộng dồn “Scars of Belinus” lên mục tiêu.""",
 "skill/856007/75600704": """Kỹ năng tăng cường: Mỗi khi Uriel sử dụng đòn đánh thường hoặc kỹ năng chủ động, cô gây sát thương diện rộng lên toàn bộ kẻ địch và có cơ hội đặt 1 cộng dồn “Scars of Belinus” lên chúng.""",
 "skill/856008/75600801": """Khi kích hoạt kỹ năng chủ động, Angelica bước vào giai đoạn “Preparation”, được tăng Chí Mạng và Giảm Sát Thương. Trong giai đoạn này, cô miễn nhiễm Khống Chế, đồng thời Năng Lượng không thể tăng hay giảm. Ở hiệp kế tiếp, cô gây lượng sát thương lớn lên toàn bộ kẻ địch và nhận cộng dồn “Sun Slayer”.""",
 "skill/856008/75600802": """Kỹ năng tăng cường: Tăng Tấn Công, Sát Thương Thánh, Sát Thương Chí Mạng, Kháng Khống Chế và Tốc Độ của Angelica.""",
 "skill/856008/75600803": """Kỹ năng tăng cường: Mỗi khi Angelica dùng đòn đánh thường, cô nhận thêm cộng dồn “Sun Slayer”.
Sau khi nâng cấp thành Kỹ Năng Tinh Anh, đòn đánh thường có cơ hội xóa 1 hiệu ứng Dấu Ấn ngẫu nhiên trên bản thân.""",
 "skill/856008/75600804": """Kỹ năng tăng cường: Đầu trận và cuối mỗi hiệp, Angelica áp dụng “Dazed” lên kẻ địch có HP thấp nhất, buộc kỹ năng chủ động, đòn đánh thường hoặc kỹ năng bị động vốn đánh nhiều mục tiêu của kẻ đó chỉ được nhắm vào một mục tiêu ngẫu nhiên.
Khi Angelica Thức Tỉnh lên 9 sao, cô tự Hồi Máu và nhận thêm cộng dồn “Sun Slayer” cuối mỗi hiệp.""",
})

EMPTY_SOURCE = "此處為填充文本"


def strip_markup(s: str) -> str:
    s = MARKUP.sub("", str(s))
    s = re.sub(r"\(\s*-\s*\]|\[\s*/c\)|\(\s*/c\)", "", s, flags=re.I)
    # The neural translator sometimes turns [c][e28002] into (c) (e 28002).
    s = re.sub(r"\(\s*(?:c|/c|-|[0-9a-f][0-9a-f ]{4,15})\s*\)", "", s, flags=re.I)
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
    text = re.sub(r"(?<=[A-Za-z])['’]s\b", "", text)
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
    # Ignore quoted source-defined skill/effect titles and one proper character name,
    # but keep catching untranslated combat mechanics in ordinary prose.
    scan_text = re.sub(r'[“][^”]*[”]|"[^"]*"', "", text)
    if item_id == "profile/856001":
        scan_text = re.sub(r"\bAngel\b", "", scan_text)
    if UNTRANSLATED.search(scan_text):
        problems.append({"id":item_id, "reason":"untranslated English combat term",
                         "matched": sorted(set(x.lower() for x in UNTRANSLATED.findall(scan_text)))})
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
