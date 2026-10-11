"""Menu (SettingUpWindow), Yume Collection (CollectionWindow) and Manga (ComicWindow) assets and data.

- SettingUpWindow: setting_up_bg + white_cyan_btn_60_128 buttons with setting_icon_* (Memories, Collection | Game: Notice,
  Help, Tips, Social, GM | Others: Manga, Image, Redeem), texts SETTING_UP_*.
- CollectionWindow: collection_scene / collection_main_bg1 / collection_main_hero, logo, 7 entrances
  (SEVEN_COLLECTION_TITLES) and collection.lua rows by type (1 skin, 2 antique, 3 avatar, 4 frame, 5 furniture, 6 background,
  7 story item, 8 emoji, 9 outfit) with item_id and collect points (awards 123#n).
- ComicWindow: comic_en_en episode list (the pages themselves were served from the publisher's website, not in the client).
Output web/assets/menu/* and web/assets/menu/menu.json. Sources in ~/Downloads are read only."""
import json, re, shutil, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DL = Path.home() / 'Downloads'
T = DL / 'Decomp files/lua/data/tables'
S = DL / 'Decompiled/Sprites (atlases, cut)'
OUT = ROOT / 'web/assets/menu'
OUT.mkdir(parents=True, exist_ok=True)


def lua_table(path):
    text = path.read_text(encoding='utf-8-sig')
    keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', text.split('table.keys = {', 1)[1].split('}', 1)[0])}
    rows = {}
    for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\n\s*\}', text, re.S):
        vals = [json.loads(p) if p.startswith('"') else float(p) if '.' in p else int(p) for p in re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))]
        rows[m.group(1)] = {k: vals[i] for k, i in keys.items() if i < len(vals)}
    return rows


sprites = ['white_cyan_btn_60_128', 'title_line02', 'setting_icon_memories', 'setting_icon_achieve', 'setting_icon_notice', 'setting_icon_help',
           'setting_icon_enhance', 'setting_icon_community', 'setting_icon_gm', 'setting_icon_comic', 'setting_icon_background', 'setting_icon_award',
           'collection_dress_new_entrance', 'collection_skin_bg', 'collection_frame_icon', 'collection_soul_icon', 'collection_story_icon',
           'collection_furniture_icon', 'collection_face_icon', 'collection_bg_icon', 'collection_main_hero', 'collection_logo_en_en',
           'collection_scroller_bar', 'collection_scroller_bar_bg', 'shop', 'help_2', 'comic_frame', 'comic_newest_frame', 'comic_icon_new',
           'comic_double_arrow', 'comic_arrow', 'comic_banner_1', 'comic_banner_2', 'comic_content_bg', 'nav_btn_white_mid', 'nav_btn_blue_mid',
           'nav_btn_white_left', 'nav_btn_white_right', 'icon_123', 'setting_up_pick', 'setting_up_unpick', 'white_btn_0', 'white_btn_65_65', 'blue_btn_65_65', 'setting_up_lan1', 'setting_up_lan2', 'person_small_title_bg']
for n in sprites:
    src = S / (n + '.png')
    if src.exists(): shutil.copy(src, OUT / src.name)
    else: print('missing', n)
for sub, n in (('Images (backgrounds)/scenes', 'setting_up_bg'), ('Images (other)/collection', 'collection_main_bg1'), ('Images (other)/collection', 'collection_main_bg2'), ('Sprites (atlases, cut)', 'collection_scene')):
    shutil.copy(DL / 'Decompiled' / sub / (n + '.png'), OUT / (n + '.png'))

db = sqlite3.connect(DL / 'Decomp files/data/en_en.db')
names = dict(db.execute('select id, name from collection_text_en_en'))
coll = {}
for r in lua_table(T / 'collection.lua').values():
    pts = re.search(r'(?:^|\|)123#(\d+)', str(r.get('new_awards') or '') + '|' + str(r.get('awards') or ''))  # skins: new_awards is 377#n, the points are in awards
    coll.setdefault(str(r['type']), []).append([r['id'], r['item_id'], int(pts.group(1)) if pts else 0, names.get(r['id'], '')])
comics = [[int(i), c] for i, c in db.execute('select id, get_chapter from comic_en_en order by cast(id as integer)')]
tr = (T / 'en_en/translation_en_en.lua').read_text(encoding='utf-8-sig')
def text(k):
    m = re.search(r'\t' + k + r' = \{\s*"' + k + r'",\s*"((?:\\.|[^"\\])*)"', tr)
    return json.loads('"' + m.group(1) + '"') if m else k
keys = ['SETTING_UP_1', 'SETTING_UP_2', 'SETTING_UP_3', 'COLLECTION_TITLE', 'SETTING_UP_5', 'SETTING_UP_6', 'SETTING_UP_7', 'SETTING_UP_9',
        'SETTING_UP_10', 'SETTING_UP_AWARD_1', 'SETTING_UP_BACKGROUND', 'CHAT_LABEL_1', 'SEVEN_COLLECTION_TITLES']
out = {'collection': coll, 'comics': comics, 'text': {k: text(k) for k in keys}}
(OUT / 'menu.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
print({k: len(v) for k, v in coll.items()}, len(comics), 'comics', out['text'])
