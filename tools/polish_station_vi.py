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
 "profile/852002": """1. Blowie là nhân vật hỗ trợ thuộc phe Nhân Loại, sở hữu khả năng Hồi Máu mạnh.
2. Cô có Tốc Độ thấp hơn nhiều nhân vật khác, vì vậy nên tăng Tốc Độ để giúp Blowie hành động sớm hơn trong mỗi hiệp.""",
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
