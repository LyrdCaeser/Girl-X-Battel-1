"""All the game audio that is not a girl voice or a story line: ui_sound / ui_sound_web / battle_sound_web / music_game effects
and the music (ui_sound_web tracks + the ten Music Game songs). WAV → MP3 (ffmpeg) into web/assets/sounds/ (flat, by sound
name), sounds/battle/ and sounds/music/. sounds.json: SoundID → name / volume / delay / loops for the ids of sound1 / sound2
whose file exists (xyd.SoundManager:playSound(id)), plus the song list. Sources are read only."""
import json, re, sqlite3, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SRC = Path.home() / 'Downloads/Decompiled'
OUT = ROOT / 'web/assets/sounds'
(OUT / 'battle').mkdir(parents=True, exist_ok=True); (OUT / 'music').mkdir(exist_ok=True)


def conv(src, dst, q='5'):
    if dst.exists(): return
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-codec:a', 'libmp3lame', '-q:a', q, str(dst)], check=True)


have = {}
for folder, sub in (('Sound (Effects)/ui_sound', ''), ('Sound (Effects)/ui_sound_web', ''), ('Sound (Effects)/music_game', ''),
                    ('Sound (Effects)/battle_sound_web', 'battle'), ('Sound (Music)/ui_sound_web', '')):
    for p in sorted((SRC / folder).glob('*.wav')):
        name = re.sub(r'[^a-z0-9_\-]', '_', p.stem.lower())
        conv(p, OUT / sub / f'{name}.mp3'); have[(folder.split('/')[-1] + '/' + p.stem).lower()] = (sub + '/' if sub else '') + name
# local_sound (17 .ogg kept inside the client, the first girls' attack / skill sounds) only exists in the Unity project
for p in sorted((Path.home() / 'Downloads/Decomp files/unity/Assets/hotres/sounds/local_sound').glob('*.ogg')):
    name = re.sub(r'[^a-z0-9_\-]', '_', p.stem.lower()); conv(p, OUT / 'battle' / f'{name}.mp3'); have['local_sound/' + p.stem.lower()] = 'battle/' + name
songs = []
for p in sorted((SRC / 'Sound (Music)/music_game').glob('*.wav'), key=lambda p: int(p.name.split(')')[0])):
    n = int(p.name.split(')')[0]); title, _, artist = p.stem.split(') ', 1)[1].partition(' - by ')
    conv(p, OUT / 'music' / f'song_{n}.mp3', '4'); songs.append({'id': n, 'title': title, 'artist': artist, 'file': f'music/song_{n}'})
db = sqlite3.connect(Path.home() / 'Downloads/Decomp files/data/data.db')
ids = {}
for t in ('sound1', 'sound2'):
    # the sqlite column names are shuffled; by position (sound1.lua keys): id, res, length, loops, is_play_self, delay, type, desc, volume
    for row in db.execute(f'select * from {t}'):
        sid, res, delay, vol = row[0], row[1], row[5], row[8]
        key = str(res or '').lower()
        if key in have:
            ids[str(sid)] = {'f': have[key], 'v': round(float(vol) / 100, 2) if str(vol or '').replace('.', '').isdigit() else 1}
            if str(delay or '').replace('.', '').isdigit() and float(delay) > 0: ids[str(sid)]['d'] = float(delay)
(OUT / 'sounds.json').write_text(json.dumps({'ids': ids, 'songs': songs,
                                             'tracks': ['home_bg_music', 'old_home_bg_music', 'campaign_bg_music', 'battle_bg_music_1', 'main_story_battle', 'main_story_campus', 'story_vow']},
                                            ensure_ascii=False, separators=(',', ':')))
# skill id → its sound (skill*.lua `sound`, first id of "a|b"); played when the skill is used in battle
T = Path.home() / 'Downloads/Decomp files/lua/data/tables'
skills = {}
for f in sorted(T.glob('skill[0-9]*.lua')):
    t = f.read_text(encoding='utf-8-sig')
    keys = {k: int(i) - 1 for k, i in re.findall(r'(\w+)\s*=\s*(\d+)', t.split('table.keys = {', 1)[1].split('}', 1)[0])}
    for m in re.finditer(r'\["(\d+)"\]\s*=\s*\{(.*?)\n\s*\}', t, re.S):
        v = re.findall(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?', m.group(2))
        snd = v[keys['sound']].strip('"') if keys['sound'] < len(v) else ''
        first = re.split(r'[|#]', snd)[0] if snd else ''
        if first in ids: skills[m.group(1)] = first
(OUT / 'skills.json').write_text(json.dumps(skills, separators=(',', ':')))
print(len(skills), 'skill sounds')
print(len(have), 'files,', len(ids), 'sound ids,', len(songs), 'songs')
