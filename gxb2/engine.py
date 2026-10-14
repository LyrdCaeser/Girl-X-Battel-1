from __future__ import annotations
import copy
import math
import json
import secrets
from pathlib import Path
import sqlite3
import threading
import time
from . import protocol as p
from .battle import simulate
from . import pumpkin, chimes
from . import collection as collection_mod
from . import bots
from . import game_calendar
from . import hearts
from . import fantasy_book, growth_diary, newbie_camp, friend_boss, pet_training, practical_work
from . import arena3v3
from . import puzzle_events, firework_project, local_promotion
from . import wish, magic_card, two_love, lost_space, vip, activity_kit, activity_draw, jackpot, blind_box, pirate, guild
from . import home_systems, events, equipment, campaign, point_events, acquisition, clock, explore, relations, missions, shops, arena, patrol, house_exam, hero_challenge, sanctuary, internship, midas, old_campus, guild_lab, echoes, shrine, galaxy, story, dress, skins, house_dress, souls, soul_land, stellar_altar, quick_formation, ev_sand, dress_show, local_config, world_live_config, live_service, database
from .player_state_db import ScopedPostgresPlayerDB
from .battle import attributes

ROOT = Path(__file__).resolve().parents[1]
TABLES = {name: json.loads((ROOT / f'data/{name}.json').read_text()) for name in ('partner', 'monster', 'stage', 'battle', 'exp_partner', 'exp_player', 'names', 'summon', 'dropbox')}
DEBRIS = json.loads((ROOT / 'data/debris.json').read_text())
GRADUATE = json.loads((ROOT / 'data/graduate.json').read_text())
ASCENSION = json.loads((ROOT / 'data/ascension.json').read_text())
EXSKILL = json.loads((ROOT / 'data/exskill.json').read_text())  # partner_exskill_cost
RESONATE = json.loads((ROOT / 'data/resonate.json').read_text())
RETURN = json.loads((ROOT / 'data/partner_return.json').read_text())
ASTRAL = json.loads((ROOT / 'data/astral.json').read_text())  # Astral Core (star_origin*)  # Reverse / 10★ Exchange  # Skill-Synchronize of the Cosmic girls (skill_resonate_*)
DAILY_QUIZ = json.loads((ROOT / 'data/daily_quiz.json').read_text())
TOWER = json.loads((ROOT / 'data/tower.json').read_text())
SHOW_FUNC = [0]  # function id of the mode being fought (Outfit Showcase buffs, dress_show.battle_skills)


def show_mode(func):
    """Mark an action's battles as mode `func` (15 Tests, 19 Patrol, 35 House Exams, 39 Old Campus) for the Showcase buffs."""
    def wrap(fn):
        def run(self, *a, **k):
            SHOW_FUNC[0] = func
            try: return fn(self, *a, **k)
            finally: SHOW_FUNC[0] = 0
        run.__name__, run.__doc__ = fn.__name__, fn.__doc__
        return run
    return wrap
MODELS = json.loads((ROOT / 'data/models.json').read_text())  # model.lua: scale, battle_pos (BaseFighter:getScale / getModelOffset)
LOCAL_TOKEN = 'gxb2-local-preservation'
AWAKE_LEVEL_STEP = 20                       # misc.awake_add_level_limit
BREAK_LEVEL_CAP = (260, 270, 290, 310, 330)  # misc.hero_break_lv_cap (11–15★)
PROPHET_SUMMONS = (10, 11, 12, 13, 14, 17, 18, 19, 20, 21)  # Prophet.SUMMONMID: factions 1–5, ×1 and ×10 (Enroll)
STARTERS = (41001, 42001, 43001)
PROFILE_CATALOG = json.loads((ROOT / 'web/assets/profile/catalog.json').read_text())


def mark_bosses(report):
    """Boss monsters (is_boss / is_real_boss) keep their model scale and offset in the replay instead of the common
    chibi size (BattleWindow:newFighter + BaseFighter:getScale); is_boss ones stand between two positions."""
    if not report:
        return report  # sweeps (Daily Quiz Raid) have no battle
    for u in report.get('display_units', []):
        if u['pos'] <= 6:
            # Skins (equipments[7] + show_skin): the replay draws the skin's chibi (skin_id is in the original report)
            src = next((x for x in report.get('teamA', []) if x['pos'] == u['pos']), None)
            if src and int(src.get('skin_id') or 0) and int(src.get('show_skin', 1) or 0):
                u['skin_id'] = int(src['skin_id'])
            continue
        side = report['teamB']
        src = next((x for x in side if x['pos'] + 6 == u['pos'] and x.get('isMonster')), None)
        mon = TABLES['monster'].get(str(src['table_id'])) if src else None
        if not mon or not (str(mon.get('is_boss')) == '1' or str(mon.get('is_real_boss')) == '1'):
            continue
        model = MODELS.get(str(TABLES['partner'].get(str(u['table_id']), {}).get('partner_model')), {})
        u['boss'] = {'scale': float(model.get('scale') or 1) + float(mon.get('scale') or 0), 'offset': model.get('battle_pos', [0, 0]),
                     'center': str(mon.get('is_boss')) == '1'}
    return report

class GameError(ValueError):
    pass

def integer(value, name, low=0, high=2**31-1):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise GameError(f'{name}: valor fuera del intervalo permitido')
    return value

def item_pairs(text):
    if text in ('', 0, None): return {}
    result = {}
    for part in str(text).split('|'):
        key, value = part.split('#')
        result[int(key)] = int(value)
    return result

def quiz_reward_pairs(text):
    result = {}
    for part in str(text).split('|'):
        item_id, amount = part.split('#')
        result[item_id] = result.get(item_id, 0) + int(amount)
    return result

def quiz_day(now=None):
    # The archived client exposes a server end_time. The local replacement resets at the player's local midnight.
    return clock.day(now)

def player_level(state):
    exp = state['items'].get('3', 0)
    return max(int(k) for k, row in TABLES['exp_player'].items() if int(row['all_exp']) <= exp)

def new_state(now=None):
    now = clock.epoch(now)
    starters = local_config.starter_girls()
    valid_starters = [tid for tid in starters if str(tid) in TABLES['partner']][:6] or list(STARTERS)
    return {'format': 2, 'created': now, 'uid': 'GXB3-000001', 'server_id': 'S1', 'name': 'Nữ Thần',
            'profile': {'avatar': 'head_1001', 'frame': 'frame_8007', 'signature': ''},
            'max_stage': 0, 'current_stage': 1, 'hang': {'since': now, 'drop_since': now},
            'battle_count': 0, 'cleared': [], 'last_battle': None, 'next_partner_id': len(valid_starters) + 1, 'summon_free_at': 0,
            'senior_summon_free_at': 0,
            'items': local_config.starting_resources(),
            'partners': [{'partner_id': i+1, 'table_id': tid, 'lv': 1, 'grade': 0, 'awake': 0,
                          'equips': [], 'pos': i+1, 'show_skin': 1} for i, tid in enumerate(valid_starters)],
            'formation': [{'partner_id': i+1, 'pos': i+1} for i in range(len(valid_starters))]}

_EQ = json.loads((ROOT / 'data/equipment.json').read_text())['items']
DEV_GEAR = [str(r['id']) for r in _EQ.values() if r['pos'] in (1, 2, 3, 4) and r.get('job') and int(r.get('item_lv') or 0) >= 24] + \
           [str(r['id']) for r in sorted((r for r in _EQ.values() if r['pos'] == 6), key=lambda r: -int(r.get('item_lv') or 0))[:12]]

class Engine:
    def __init__(self, db_path: Path, developer=False, clock_source=None, identity=None):
        self._raw_now = clock_source or time.time
        self.developer = developer
        self.now = self._monotonic_now
        self._floor = self._floor_saved = 0
        db_path = Path(db_path)
        self.lock = threading.RLock()
        if identity and database.is_postgres() and not developer:
            self.db = ScopedPostgresPlayerDB(identity[0], identity[1])
        else:
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self.db = sqlite3.connect(db_path, check_same_thread=False)
            self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('CREATE TABLE IF NOT EXISTS profile(id INTEGER PRIMARY KEY CHECK(id=1), data TEXT NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS clock(id INTEGER PRIMARY KEY CHECK(id=1), floor INTEGER NOT NULL)')
        row = self.db.execute('SELECT floor FROM clock WHERE id=1').fetchone()
        self._floor = self._floor_saved = int(row[0]) if row else 0
        self.db.execute('CREATE TABLE IF NOT EXISTS battles(id INTEGER PRIMARY KEY, stage INTEGER, report TEXT NOT NULL)')
        if not self.db.execute('SELECT 1 FROM profile WHERE id=1').fetchone():
            self.db.execute('INSERT INTO profile VALUES(1,?)', (json.dumps(new_state(self.now())),))
            self.db.commit()
        else:
            state = self._load()
            changed = False
            if state.get('format', 1) < 2:
                state['format'] = 2
                state.setdefault('items', {}).setdefault('33', 10)
                state['next_partner_id'] = max(v['partner_id'] for v in state['partners']) + 1
                state['summon_free_at'] = 0
                changed = True
            state.setdefault('items', {})
            for item_id, starter_amount in (('12', 1000), ('36', 10)):
                if item_id not in state['items']:
                    state['items'][item_id] = starter_amount
                    changed = True
            if 'senior_summon_free_at' not in state:
                state['senior_summon_free_at'] = 0
                changed = True
            if 'profile' not in state:
                state['profile'] = {'avatar': 'head_1001', 'frame': 'frame_8007', 'signature': ''}
                changed = True
            if 'hang' not in state:
                state['hang'] = {'since': self.now(), 'drop_since': self.now()}
                changed = True
            if changed:
                self._save_profile(state)
                self.db.commit()
        if self.developer:
            # the developer save owns one copy of every girl of the guide (Cosmic ones included) to check every sheet
            state = self._load()
            # and one of every Anima Artifact plus a full 6★ Anima Stone set of every group (granted once)
            added = self._add_all_girls(state); granted = not state.get('souls', {}).get('dev_granted'); souls.grant_dev(state)
            # every Outfit piece at its top star, to try the Outfit Showcase and Senpai attributes
            owned = dress.saved(state)['owned']
            for did in dress.PIECES:
                stars = [k + 1 for k, it in enumerate(dress.piece_items(did)) if int(it) in dress.ITEMS]
                if str(did) not in owned and stars: owned[str(did)] = max(stars); granted = True
            # every open Servant, to try the Servant in the formation windows
            pets = home_systems.saved(state, self.now())['pets']
            for pid, row in home_systems.ROWS['pet'].items():
                if row.get('is_open') == '1' and pid not in pets: pets[pid] = {'lv': 1, 'grade': 1, 'skills': [0, 0, 0, 0]}; granted = True
            # an advanced account (once): the campaign up to stage 480 of 530 (the last 50 still to fight, idle there),
            # Tests floor 300, Patrol stage 300 and every girl at her level cap, so late-game systems can be tried
            if state.get('patrol') and 'current_stage' not in state['patrol']: state['patrol'] = {**patrol.fresh(0), **state['patrol']}; granted = True
            if not state.get('dev_advanced'):
                state['dev_advanced'] = 1; granted = True
                state['max_stage'] = max(int(state.get('max_stage', 0)), 480); state['current_stage'] = state['max_stage']
                tower = state.setdefault('tower', {'tickets': 10, 'at': self.now()}); tower['max_stage'] = max(int(tower.get('max_stage', 0)), 300)
                old = state.get('patrol') or {}; state['patrol'] = {**patrol.fresh(0), **old, 'max_stage': max(int(old.get('max_stage', 0)), 300)}
                for girl in state['partners']:
                    girl['grade'] = max(int(girl.get('grade', 0)), int(TABLES['partner'][str(girl['table_id'])].get('max_grade') or 0))
                    girl['lv'] = max(int(girl.get('lv', 1)), self.level_cap(girl, real=True))
            # one copy of every skin (once), to try Skins, Costume Wardrobe and the Wallpaper list
            if not state.get('dev_skins'):
                from . import skins as skins_mod
                state['dev_skins'] = 1; granted = True
                for sid in skins_mod.SKINS: state['items'][str(sid)] = max(1, int(state['items'].get(str(sid), 0)))
            if added or granted:
                self._save_profile(state)
                self.db.commit()

    @staticmethod
    def guide_girls():
        # same rule as tools/extract_girls_catalog.py: show_in_guide 1 (launch roster) or a release timestamp
        return [int(k) for k, v in sorted(TABLES['partner'].items(), key=lambda kv: int(kv[0])) if str(v.get('show_in_guide') or 0) not in ('0', '')]

    def _add_all_girls(self, state, level=None):
        owned = {int(p['table_id']) for p in state['partners']}
        added = 0
        for tid in self.guide_girls():
            if tid in owned: continue
            row = TABLES['partner'][str(tid)]
            pid = state['next_partner_id']; state['next_partner_id'] += 1
            state['partners'].append({'partner_id': pid, 'table_id': tid, 'lv': level or int(row.get('max_lv') or 100), 'grade': int(row.get('max_grade') or 0),
                                      'awake': 0, 'equips': [], 'pos': 0, 'show_skin': 1})
            added += 1
        return added

    def _monotonic_now(self):
        """Game time never goes backwards (LOCAL-057): daily/weekly resets compare `day != saved day`, so a system clock
        moved back and forward again would reset them twice. The highest time seen is kept in the save; the developer
        save follows the raw clock so QA can time-travel."""
        raw = int(self._raw_now())
        if self.developer:
            return raw
        with self.lock:
            if raw > self._floor:
                self._floor = raw
                if raw - self._floor_saved >= 30:
                    self._save_floor()
            return self._floor

    def _save_floor(self):
        self.db.execute('INSERT INTO clock(id, floor) VALUES(1, ?) ON CONFLICT(id) DO UPDATE SET floor=excluded.floor', (self._floor,))
        self.db.commit()
        self._floor_saved = self._floor

    def clock_behind(self):
        """Seconds the system clock is behind the game clock (0 when in sync)."""
        return 0 if self.developer else max(0, self._floor - int(self._raw_now()))

    def bind_identity(self, uid, server_id, character_name):
        with self.lock:
            state = self._load()
            changed = False
            if state.get('uid') != str(uid):
                state['uid'] = str(uid); changed = True
            if state.get('server_id') != str(server_id).upper():
                state['server_id'] = str(server_id).upper(); changed = True
            if character_name and state.get('name') != str(character_name):
                state['name'] = str(character_name); changed = True
            if changed:
                self._save_profile(state)
                self.db.commit()
        return None

    def close(self):
        if not self.developer and self._floor != self._floor_saved:
            self._save_floor()
        self.db.close()

    def _load(self):
        state = json.loads(self.db.execute('SELECT data FROM profile WHERE id=1').fetchone()[0])
        if self.developer:
            for item_id in ('1', '2', '4', '7', '9', '10', '11', '12', '13', '33', '36', '26', '27', '203', '204', '205', '216', '221', '222', '232', '358', '359', '360'):
                state['items'][item_id] = 1000000000
            for item_id in DEBRIS: state['items'][item_id] = 1000000000
            # gear to try the Gear tab: every job's top weapon / clothes / accessory / shoes and the top antiques
            for item_id in ('19', '20', '14', '47', '358', '390', '391', '417', '418', '419', '420', '422', '423', '424', '426', '435', '314', '315', '180', '427', '349', '182', '325', '326', '982001', '983001', '984001', '984002', '984003', '984004', '985001', '985002', '985003', '986001', '35', '29', '6', '69', '258', '259', '34', '74', '43', '44', '45', *(str(1000001 + k) for k in range(40))): state['items'][item_id] = max(1000000, int(state['items'].get(item_id, 0)))
            for item_id in DEV_GEAR: state['items'][item_id] = max(5, int(state['items'].get(item_id, 0)))
            state['items']['3'] = max(int(r['all_exp']) for r in TABLES['exp_player'].values())
            state['summon_free_at'] = state['senior_summon_free_at'] = 0
        vip.apply(state, self.developer)
        # Establish special-objective baselines before the first successful action.
        growth_diary.prepare(state, self.missions_probe(dict(state)), player_level(state))
        return state

    @staticmethod
    def _attributes(state, partners, **kwargs):
        """Calculate attributes with bonuses from this save, never another request."""
        kwargs.setdefault('chime_bonus', chimes.bonus(state))
        return attributes(partners, **kwargs)

    @staticmethod
    def _simulate(state, *args, **kwargs):
        """Run the original battle with this save's Tree of Chimes (and the Outfit Showcase buffs of the current mode)."""
        kwargs.setdefault('chime_bonus_a', chimes.bonus(state))
        if SHOW_FUNC[0]:
            extra = dress_show.battle_skills(state, SHOW_FUNC[0])
            if extra: kwargs['god_skills'] = list(kwargs.get('god_skills') or []) + extra
        return simulate(*args, **kwargs)

    def _save_profile(self, state):
        probe = dict(state)
        growth_diary.observe(state, self.missions_probe(probe), player_level(state))
        newbie_camp.observe(state, self.missions_probe(dict(state)), player_level(state), self.now())
        self.db.execute('UPDATE profile SET data=? WHERE id=1', (json.dumps(state, ensure_ascii=False),))

    def pvp_team_snapshot(self):
        with self.lock:
            state = self._load()
            by_id = {int(p['partner_id']): p for p in state.get('partners', [])}
            team = []
            for slot in sorted(state.get('formation', []), key=lambda x: int(x.get('pos', 0))):
                partner = by_id.get(int(slot.get('partner_id', 0)))
                if not partner:
                    continue
                unit = copy.deepcopy(partner)
                unit['pos'] = int(slot.get('pos', unit.get('pos', 0) or 0))
                team.append(unit)
            if not team:
                team = [copy.deepcopy(p) for p in state.get('partners', [])[:6]]
                for i, unit in enumerate(team, 1):
                    unit['pos'] = i
            if not team:
                raise GameError('Đội hình PvP đang trống')
            power = self._friend_power(state)
            return {
                'uid': state.get('uid'),
                'server_id': state.get('server_id'),
                'name': state.get('name'),
                'level': player_level(state),
                'power': int(power),
                'team': team[:6],
                'pet': self.battle_pet(state),
                'guild_skills': guild_lab.skills(state),
                'chime_bonus': chimes.bonus(state),
            }

    def claim_live_mail(self, mail_id):
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                uid = state.setdefault('uid', 'GXB3-000001')
                server_id = state.setdefault('server_id', 'S1')
                profile = live_service.player(uid, server_id)
                if profile and profile.get('status') == 'banned':
                    raise GameError('Tài khoản đang bị khóa')
                # Neon: claim + reward update are one transaction, so a failed
                # player-save cannot leave a paid/GM mail marked claimed.
                # ScopedPostgresPlayerDB is a player-persistence adapter, not
                # a live_service.DBConnection and has no .backend attribute.
                # Borrow its active PostgreSQL connection so claiming the mail
                # and persisting rewards are ONE atomic transaction.
                live_db = self.db.borrowed_live_transaction() if isinstance(
                    self.db, ScopedPostgresPlayerDB) else None
                attachments = live_service.claim_mail(str(mail_id), uid, server_id,
                    db=live_db)
                inventory = dict(attachments)
                vip.claim_reward(state, inventory)
                for item_id, amount in inventory.items():
                    state['items'][str(item_id)] = int(state['items'].get(str(item_id), 0)) + int(amount)
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
        return {'state': self.snapshot(), 'attachments': attachments}

    def use_bag_item(self, item_id, reward_id, count=1):
        """Use verified original selectable chests. Debit & shard grant commit together."""
        recipes = {
            133: (930187, 930188),       # Girls Chest: Kratos / Nephilim
            4102003: (930187, 930188),   # Kratos or Nephilim Chest
            207: (930195, 930194),       # Girls Customized: Izanami / Uriel
        }
        if any(isinstance(value, (bool, float, dict, list)) for value in (item_id, reward_id, count)):
            raise GameError('Vật phẩm không hợp lệ')
        try:
            item_id, reward_id, count = int(item_id), int(reward_id), int(count)
        except (TypeError, ValueError, OverflowError):
            raise GameError('Vật phẩm không hợp lệ') from None
        if item_id not in recipes:
            raise GameError('Vật phẩm này chưa hỗ trợ sử dụng trực tiếp trên máy chủ')
        if reward_id not in recipes[item_id]:
            raise GameError('Phần thưởng chọn không thuộc rương này')
        if not 1 <= count <= 50:
            raise GameError('Mỗi lần chỉ được dùng từ 1 đến 50 rương')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                owned = int(state['items'].get(str(item_id), 0))
                if owned < count:
                    raise GameError('Không đủ rương trong Túi Đồ')
                state['items'][str(item_id)] = owned - count
                amount = 50 * count
                state['items'][str(reward_id)] = int(state['items'].get(str(reward_id), 0)) + amount
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
        return {'state': self.snapshot(),
                'used': {'item_id': item_id, 'count': count},
                'rewards': {str(reward_id): 50 * count}}

    def growth_diary_action(self, request):
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); probe = dict(state)
                try: result = growth_diary.action(state, request, self.missions_probe(probe), player_level(state))
                except ValueError as exc: raise GameError(str(exc))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def newbie_camp_action(self, request):
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); probe = dict(state)
                try: result = newbie_camp.action(state, request, self.missions_probe(probe), player_level(state), self.now())
                except ValueError as exc: raise GameError(str(exc))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def _remaining_battle(self, state, row, request, battle_type):
        formation=self.validate_formation(state,request.get('partners') or state['formation'])
        owned={p['partner_id']:p for p in state['partners']}
        team_a=[{**copy.deepcopy(owned[x['partner_id']]),'pos':x['pos']} for x in formation]
        battle=TABLES['battle'][str(row['battle_id'])]
        pct=max(1,min(100,math.ceil(int(row['remaining_hp'])*100/int(row['hp'])))) if 'remaining_hp' in row else 100
        team_b=[{'table_id':int(t),'pos':int(q),'isMonster':True,'status':{'hp':pct,'mp':50}} for t,q in zip(str(battle['monsters']).split('|'),str(battle['stands']).split('|'))]
        pet=self.battle_pet(state)
        if 'pet' in request:
            pid=home_systems.checked(request['pet'],'Servant',0)
            info=((state.get('home_systems') or {}).get('pets') or {}).get(str(pid))
            if pid and not info:raise GameError('No tienes ese Servant')
            pet={'pet_id':pid,'lv':info['lv'],'grade':info['grade'],'skills':info['skills'],'ex_lv':info.get('exlv',0)} if info else None
        report=self._simulate(state,team_a,team_b,int(row['battle_id']),secrets.randbelow(233280),pet,battle_type,guild_skills_a=guild_lab.skills(state))
        report['map_asset']=battle['map'];report['display_units']=[]
        for side in ('teamA','teamB'):
            for u in report[side]:
                tid=int(TABLES['monster'][str(u['table_id'])]['partner_link']) if u.get('isMonster') else u['table_id']
                report['display_units'].append({'pos':u['pos']+(6 if side=='teamB' else 0),'table_id':tid,'name':TABLES['names'].get(str(tid),str(tid)),'level':u['level']})
        mark_bosses(report)
        return report

    def _friend_power(self,state):
        attrs=self._attributes(state,state['partners'],guild_skills=guild_lab.skills(state))
        return sum(sorted((int(v.get('power',0)) for v in attrs.values()),reverse=True)[:6])

    def remaining_system_action(self, system, request):
        if not isinstance(request,dict):raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state=self._load();now=self.now()
                if system=='friend-boss':
                    friend_boss.observe_power(state,now,self._friend_power(state))
                    result=friend_boss.action(state,request,now,player_level(state),fight=lambda row:self._remaining_battle(state,row,request,7))
                elif system=='pet-training':result=pet_training.action(state,request,now)
                elif system=='practical-work':result=practical_work.action(state,request,now,fight=lambda row:self._remaining_battle(state,row,request,13))
                else:raise GameError('Sistema desconocido')
                self._save_profile(state);self.db.commit()
            except Exception:
                self.db.rollback();raise
            return {'state':self.snapshot(),**result}

    def developer_action(self, request, *, super_gm=False):
        if not self.developer and not super_gm: raise GameError('Chỉ SUPER GM mới có quyền dùng công cụ này')
        with self.lock:
            state = self._load()
            action = request.get('action')
            if action == 'girl':
                tid = integer(request.get('table_id'), 'Chica', 1)
                if str(tid) not in TABLES['partner']: raise GameError('Chica desconocida')
                count = integer(request.get('count', 1), 'Copias', 1, 20)
                level = integer(request.get('level', 1), 'Nivel', 1, 330)
                for _ in range(count):
                    pid = state['next_partner_id']; state['next_partner_id'] += 1
                    state['partners'].append({'partner_id': pid, 'table_id': tid, 'lv': level,
                                              'grade': 0, 'awake': 0, 'equips': [], 'pos': 0, 'show_skin': 1})
            elif action == 'max_stars':
                # every copy of the chosen 10★ girl goes to 15★ (Limit-Break 5, level 330) to try potentials / Astral Core
                tid = integer(request.get('table_id'), 'Chica', 1)
                if int(TABLES['partner'].get(str(tid), {}).get('max_star') or 0) != 10: raise GameError('Solo chicas de 10★')
                for girl in state['partners']:
                    if girl['table_id'] == tid: girl['awake'] = 5; girl['lv'] = 330
            elif action == 'all_girls':
                self._add_all_girls(state)
            elif action == 'levels':
                level = integer(request.get('level'), 'Nivel', 1, 330)
                for girl in state['partners']: girl['lv'] = level
            elif action == 'tower':
                floor = integer(request.get('floor'), 'Piso', 1, 1500)
                state['tower'] = {'max_stage': floor - 1, 'tickets': 10, 'at': self.now()}
            elif action == 'campaign':
                state['max_stage'] = 29; state['current_stage'] = 30
            else: raise GameError('Herramienta desconocida')
            self._save_profile(state)
            self.db.commit()
            return self.snapshot()

    def home_action(self, request):
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                result = home_systems.action(state, request, self.developer, now=self.now())
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def events_action(self, request):
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                result = events.action(state, request, now=self.now())
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def equipment_action(self, request):
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                result = equipment.action(state, request)
                if result.get('forged'): missions.record(state, 'forge', sum(result['forged'].values()), self.now())
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def battle_pet(self, state):
        """Selected Servant as the original ReportPet params (pet_id, grade, lv, skills, ex_lv)."""
        home = state.get('home_systems') or {}
        pid = home.get('selected_pet')
        pet = (home.get('pets') or {}).get(str(pid)) if pid else None
        if not pet: return None
        return {'pet_id': int(pid), 'grade': int(pet.get('grade', 1)), 'lv': int(pet.get('lv', 1)),
                'skills': [int(x) for x in pet.get('skills', [0, 0, 0, 0])], 'ex_lv': int(pet.get('exlv', 0))}

    def campaign_action(self, request):
        if not isinstance(request, dict) or request.get('action') != 'collect': raise GameError('Acción de campaña no disponible')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                awards = campaign.collect(state, now=self.now())
                growth_diary.record(state, 'growth_idle_gold', int(awards.get('1', 0)))
                missions.record(state, 'idle', 1, self.now())
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), 'awards': awards}

    def partners_power(self):
        """Power of every Girl (original HeroAttr) for formation windows, in one engine call."""
        with self.lock:
            state = self._load()
        rows = []
        for girl in state['partners']:
            row = copy.deepcopy(girl); equipment.equips_of(row); rows.append(row)
        if not rows:
            return {}
        attrs = self._attributes(state, rows, guild_skills=guild_lab.skills(state))
        return {pid: int(a.get('power', 0)) for pid, a in attrs.items()}

    def partner_attributes(self, partner_id):
        with self.lock:
            state = self._load()
        partner = next((girl for girl in state['partners'] if girl['partner_id'] == partner_id), None)
        if not partner: raise GameError('Chica inexistente')
        partner = copy.deepcopy(partner); equipment.equips_of(partner)
        result = self._attributes(state, [partner], guild_skills=guild_lab.skills(state))[str(partner_id)]
        if partner.get('tmp_treasure'):
            preview = copy.deepcopy(partner); preview['equips'][4] = preview['tmp_treasure']
            result['treasure_preview'] = self._attributes(state, [preview], guild_skills=guild_lab.skills(state))[str(partner_id)]
        return result

    def graduate_preview(self, partner_id, target_id=0):
        """Read-only comparison using the same attribute engine as battle."""
        with self.lock:
            state = self._load()
        host = next((g for g in state['partners'] if g['partner_id'] == partner_id), None)
        if not host: raise GameError('Chica inexistente')
        before = copy.deepcopy(host); equipment.equips_of(before)
        star = int(TABLES['partner'][str(host['table_id'])]['max_star']) + int(host.get('awake', 0))
        compose = (GRADUATE.get(str(target_id)) or ASCENSION.get(f'{target_id}:6')) if star in (4, 5) and not int(host.get('awake', 0)) else None
        if compose and int(compose['source']) != int(host['table_id']): raise GameError('La base no coincide con la receta')
        recipe = compose or ASCENSION.get(f"{host['table_id']}:{star+1}") or local_promotion.recipe(host) or self.awake_recipe(host)
        if not recipe: raise GameError('Selecciona una base que pueda ascender')
        after = copy.deepcopy(before)
        if compose: after['table_id'] = int(target_id)
        elif recipe.get('local'): after['awake'] = int(after.get('awake', 0)) + 1
        elif star + 1 == 10:
            after['table_id'] = int(recipe['target']); after['awake'] = 0
        else: after['awake'] = int(after.get('awake', 0)) + 1
        skills = guild_lab.skills(state)
        return {'before': self._attributes(state, [before], guild_skills=skills)[str(partner_id)],
                'after': self._attributes(state, [after], guild_skills=skills)[str(partner_id)],
                'from_star': star, 'to_star': star+1, 'level': host['lv'],
                'level_cap_before': self.level_cap(before), 'level_cap_after': self.level_cap(after),
                'local': bool(recipe.get('local'))}

    def profile_unlocks(self, state):
        """Profile cosmetics unlocked by actual collection/roster progress.

        Heads/frames follow Collection types 3/4. Girl portraits unlock when the
        corresponding Girl (or a released avatar variant of that Girl) is owned.
        The currently equipped cosmetic remains valid for legacy saves.
        """
        got = collection_mod.owned_ids(state)
        heads = {'head_1001'}
        frames = set()
        for cid, typ, item, _points in collection_mod.ROWS:
            if cid not in got:
                continue
            if int(typ) == 3:
                raw = int(item)
                hid = raw if raw < 100000 else raw % 10000
                if hid:
                    heads.add(f'head_{hid}')
            elif int(typ) == 4:
                frames.add(f'frame_{int(item)}')
        owned_ids = {str(int(p.get('table_id', 0))) for p in state.get('partners', []) if int(p.get('table_id', 0) or 0)}
        partners = set()
        for name in PROFILE_CATALOG.get('partners', []):
            suffix = str(name).removeprefix('partner_avatar_')
            if any(suffix == tid or suffix.startswith(tid) for tid in owned_ids):
                partners.add(name)
        current = state.get('profile') or {}
        avatar = str(current.get('avatar') or '')
        frame = str(current.get('frame') or '')
        if avatar.startswith('head_'):
            heads.add(avatar)
        elif avatar.startswith('partner_avatar_'):
            partners.add(avatar)
        if frame:
            frames.add(frame)
        return {'heads': sorted(heads), 'partners': sorted(partners), 'frames': sorted(frames)}

    def update_profile(self, changes):
        if not isinstance(changes, dict) or not changes or set(changes) - {'name', 'signature', 'avatar', 'frame', 'wallpapers', 'wallpaper_random'}:
            raise GameError('Campos de perfil inválidos')
        with self.lock:
            state = self._load()
            profile = state.setdefault('profile', {})
            for key, value in changes.items():
                if key == 'wallpapers':
                    # Wallpaper Girls list: up to 6 owned girls (table ids) or owned skins (7xxx) shown on the Front Page
                    owned = {int(p['table_id']) for p in state['partners']} | set(skins.collected(state))
                    if not isinstance(value, list) or len(value) > 6 or any(int(v) not in owned for v in value):
                        raise GameError('Wallpaper inválido')
                    if profile.get('wallpapers') != [int(v) for v in value]: growth_diary.record(state,'newbie_wallpaper')
                    profile['wallpapers'] = [int(v) for v in value]; continue
                if key == 'wallpaper_random':
                    profile['wallpaper_random'] = 1 if value else 0; continue
                if not isinstance(value, str):
                    raise GameError(f'{key}: valor inválido')
                value = value.strip() if key in ('name', 'signature') else value
                if key == 'name':
                    if not 1 <= len(value) <= 20 or any(ord(c) < 32 for c in value):
                        raise GameError('El nombre debe tener entre 1 y 20 caracteres')
                    state['name'] = value
                    try: live_service.register_player(state.get('uid','GXB3-000001'), state.get('server_id','S1'), value)
                    except Exception: pass
                elif key == 'signature':
                    if len(value) > 100 or any(ord(c) < 32 and c != '\n' for c in value):
                        raise GameError('La firma debe tener como máximo 100 caracteres')
                    profile['signature'] = value
                elif key == 'avatar':
                    if value not in PROFILE_CATALOG['heads'] and value not in PROFILE_CATALOG['partners']:
                        raise GameError('Avatar không hợp lệ')
                    unlocked = self.profile_unlocks(state)
                    if value not in unlocked['heads'] and value not in unlocked['partners']:
                        raise GameError('Avatar này chưa được mở khóa')
                    profile['avatar'] = value
                elif key == 'frame':
                    if value not in PROFILE_CATALOG['frames']:
                        raise GameError('Khung avatar không hợp lệ')
                    if value not in self.profile_unlocks(state)['frames']:
                        raise GameError('Khung avatar này chưa được mở khóa')
                    profile['frame'] = value
            self._save_profile(state)
            self.db.commit()
        return self.snapshot()

    def snapshot(self):
        with self.lock:
            state = self._load()
        state.setdefault('uid', 'GXB3-000001')
        state.setdefault('server_id', 'S1')
        try:
            player = live_service.register_player(state['uid'], state['server_id'], state['name'])
            state['account_status'] = player.get('status','active') if player else 'active'
            state['mail_info'] = live_service.mailbox(state['uid'], state['server_id'])
            state['worlds'] = live_service.worlds()
        except Exception:
            state['account_status'] = 'active'; state['mail_info'] = []; state['worlds'] = []
        state['profile_unlocks'] = self.profile_unlocks(state)
        state['home_systems'] = home_systems.snapshot(state, now=self.now())
        state['event_hub'] = events.snapshot(state, now=self.now())
        state['hang_info'] = campaign.pending(state, now=self.now())
        state['point_events_info'] = point_events.snapshot(state, now=self.now())
        state['explore_info'] = explore.snapshot(state, self.now())
        _probe = dict(state); _roster = self.missions_probe(_probe)
        state['missions_info'] = missions.snapshot(_probe, player_level(state), _roster, self.now())
        state['growth_diary_info'] = growth_diary.snapshot(_probe, _roster, player_level(state))
        state['newbie_camp_info'] = newbie_camp.snapshot(_probe, _roster, player_level(state))
        state['friend_boss_info'] = friend_boss.snapshot(state,self.now(),player_level(state))
        state['pet_training_info'] = pet_training.snapshot(state,self.now())
        state['practical_work_info'] = practical_work.snapshot(state,self.now())
        state['hearts_info'] = hearts.snapshot(state, self.now())
        state['fantasy_book_info'] = fantasy_book.snapshot(_probe, player_level(state), _roster, self.now())
        state['shops_info'] = shops.snapshot(state, player_level(state), self.now())
        state['arena_info'] = arena.snapshot(state, player_level(state), self.now())
        state['arena3v3_info'] = arena3v3.snapshot(state, player_level(state), self.now())
        state['patrol_info'] = patrol.snapshot(state, self.now())
        state['house_dress_info'] = house_dress.snapshot(state)
        state['guild_lab_info'] = guild_lab.snapshot(state)
        state['house_exam_info'] = house_exam.snapshot(state, self.now())
        state['hero_challenge_info'] = hero_challenge.snapshot(state, self.now())
        state['sanctuary_info'] = sanctuary.snapshot(state, self.now())
        state['internship_info'] = internship.snapshot(state, self.now())
        state['midas_info'] = midas.snapshot(state, player_level(state), self.now())
        state['old_campus_info'] = old_campus.snapshot(state, self.now())
        state['echoes_info'] = echoes.snapshot(state, self.now())
        state['shrine_info'] = shrine.snapshot(state, self.now())
        state['galaxy_info'] = galaxy.snapshot(state, self.now())
        state['story_info'] = story.snapshot(state)
        state['dress_info'] = dress.snapshot(state, self.now())
        state['skins_info'] = skins.snapshot(state)
        state['souls_info'] = souls.snapshot(state)
        state['ev_sand_info'] = ev_sand.snapshot(state)
        state['wish_info'] = wish.snapshot(state, self.now())
        state['magic_card_info'] = magic_card.snapshot(state, self.now())
        state['two_love_info'] = two_love.snapshot(state, self.now())
        state['act_kit_info'] = activity_kit.snapshot(state, self.now())
        state['act_draw_info'] = activity_draw.snapshot(state, self.now())
        state['jackpot_info'] = jackpot.snapshot(state, self.now())
        state['firework_project_info'] = firework_project.snapshot(state, self.now())
        state['puzzle_events_info'] = puzzle_events.snapshot(state, self.now())
        state['blind_box_info'] = blind_box.snapshot(state, self.now())
        state['pirate_info'] = pirate.snapshot(state, self.now())
        state['guild_info'] = guild.snapshot(state, self.now(), player_level(state))
        state['lost_space_info'] = lost_space.snapshot(state, self.now())
        state['pumpkin_info'] = pumpkin.snapshot(state, self.now())
        state['collection_info'] = collection_mod.snapshot(state, self.now())
        state['dates_info'] = relations.dates_info(state)
        state['chimes_info'] = chimes.snapshot(state)
        state['dress_show_info'] = dress_show.snapshot(state, self.now())
        state['quick_formation_info'] = quick_formation.snapshot(copy.deepcopy(state), self.developer)
        state['stellar_altar_info'] = stellar_altar.snapshot(copy.deepcopy(state), self.developer)
        state['soul_land_info'] = soul_land.snapshot(copy.deepcopy(state), self.now())
        state['vip_info'] = vip.info(state, self.developer)
        state['acquisition'] = acquisition.snapshot(state, now=self.now(), developer=self.developer)
        state['server_time'] = self.now()
        state['clock_behind'] = self.clock_behind()
        state['developer'] = self.developer
        state['level'] = player_level(state)
        current_exp = int(state['items'].get('3', 0))
        level_row = TABLES['exp_player'][str(state['level'])]
        next_row = TABLES['exp_player'].get(str(state['level'] + 1))
        state['experience'] = {'current': current_exp - int(level_row['all_exp']),
                               'needed': int(next_row['all_exp']) - int(level_row['all_exp']) if next_row else 0}
        state['next_stage'] = self.next_stage(state)
        state['daily_quiz'] = self.daily_quiz_info(state)
        state['tower'] = self.tower_info(state)
        now = self.now()
        state['summon'] = {
            'free_at': state.get('summon_free_at', 0),
            'free_ready': now >= state.get('summon_free_at', 0),
            'senior_free_at': state.get('senior_summon_free_at', 0),
            'senior_free_ready': now >= state.get('senior_summon_free_at', 0),
            'basic_scrolls': state['items'].get('33', 0),
            'senior_scrolls': state['items'].get('36', 0),
            'friend_hearts': state['items'].get('11', 0),
            'egg_points': state['items'].get('12', 0),
            'egg_cost': int(item_pairs(TABLES['summon']['9']['cost'])[12]),
        }
        state['debris'] = []
        for item_id, item in DEBRIS.items():
            count = int(state['items'].get(item_id, 0))
            if not count or not item.get('summon_id') or str(item['summon_id']) not in TABLES['summon']:
                continue
            config = TABLES['summon'][str(item['summon_id'])]
            costs = item_pairs(config.get('cost', ''))
            need = costs.get(int(item_id), 0)
            target = int(str(item.get('partner_cost') or '0#0').split('#')[0])
            shard_stars = int(TABLES['partner'].get(str(target), {}).get('max_star') or item.get('qlt') or 1) + int(config.get('awaken_lv') or 0)
            state['debris'].append({**item, 'count': count, 'need': need, 'stars': shard_stars,
                                    'summon_id': int(item['summon_id']),
                                    'draws': int(config.get('summon_num') or 1),
                                    'can_compose': need > 0 and count >= need})
        state['debris'].sort(key=lambda x: (-int(x['qlt']), int(x['group']), x['name']))
        state['roster'] = []
        for partner in state['partners']:
            row = TABLES['partner'][str(partner['table_id'])]
            cost = {k: local_config.scale_cost(v) for k, v in item_pairs(TABLES['exp_partner'][str(partner['lv'] + 1)]['cost']).items()} if partner['lv'] < self.level_cap(partner) else {}
            stars = int(row['max_star']) + int(partner.get('awake', 0))
            grade, max_grade = int(partner.get('grade', 0)), int(row.get('max_grade') or 0)
            awake = ASCENSION.get(f"{partner['table_id']}:{stars+1}") or local_promotion.recipe(partner) or self.awake_recipe(partner)
            if awake and awake.get('cost'):
                awake = {**awake, 'cost': {str(k): local_config.scale_cost(v) for k, v in awake['cost'].items()}}
            state['roster'].append({**partner, 'name': TABLES['names'].get(str(partner['table_id']), str(partner['table_id'])),
                                    'local_promotion': int(partner['table_id']) in local_promotion.BASE, 'stars': stars, 'level_cap': self.level_cap(partner), 'next_cost': cost,
                                    'group': int(row['group']), 'job': int(row['job']), 'max_grade': max_grade,
                                    'grade_cost': {k: local_config.scale_cost(v) for k, v in item_pairs(row.get(f'grade_exp{grade+1}')).items()} if grade < max_grade else {},
                                    'next_awake': awake if awake and awake.get('kind') == 'awake' else None,
                                    'star_10': int(row.get('star_10') or 0), 'astral_list': int(row.get('star_origin') or 0) if stars >= 15 else 0, 'namesake': int(str(row.get('material') or '').split('|')[0] or 0) if int(row['max_star']) > 5 else int(partner['table_id']), 'potential_options': [[int(x) for x in st.split('#') if x] for st in str(row.get('potential') or '').split('|') if st] if int(row['max_star']) == 10 else [],
                                    'has_ex_skills': stars >= 10 and str(row.get('ex_skill')) == '1', 'gift_like': str(row.get('gift_type1') or ''),
                                    'ex_skill_cost': item_pairs(EXSKILL['cost'].get(str(min((partner.get('ex_skills') or [0])) + 1), '')),
                                    'resonate': {'costs': [item_pairs(RESONATE['cost'].get(str(v + 1), '')) for v in (list(partner.get('ex_skills') or []) + [0, 0, 0, 0])[:4]], 'max': RESONATE['max'], 'effects': RESONATE['effects'].get(str(partner['table_id']), [])} if int(row['group']) == 7 else None})
        stages = sorted(TABLES['stage'].values(), key=lambda row: row['id'])
        state['stages'] = [{'id': row['id'], 'level_required': row['lv'], 'unlocked': row['id'] <= state['next_stage'],
                            'cleared': row['id'] in state['cleared'], 'chapter': row['fort_id'],
                            'chapter_stage': row['name'], 'map': row['set_map']} for row in stages]
        # Game calendar (gxb2/game_calendar.py): periods, the limited events open now / next and every countdown in one place
        _resets = [{'key': 'book', 'label': 'Fantasy Book season ends', 'at': (state.get('fantasy_book_info') or {}).get('end', 0)},
                   {'key': 'arena', 'label': 'Junior Varsity season ends', 'at': (state.get('arena_info') or {}).get('season_end', 0)},
                   {'key': 'arena3v3', 'label': 'Varsity season ends', 'at': (state.get('arena3v3_info') or {}).get('season_end', 0)},
                   {'key': 'exam', 'label': 'House Exams season ends', 'at': (state.get('house_exam_info') or {}).get('season_end', 0)}]
        state['calendar_info'] = game_calendar.snapshot(self.now(), _resets)
        state['bots_info'] = bots.snapshot(state, player_level(state), self.now())  # simulated players: rankings and chat (LOCAL-085)
        if not self.developer:
            try:
                state['power'] = self._friend_power(state)
                live_service.touch_presence(state['uid'], state['server_id'], state['name'], state['level'], state['power'])
                state['online_count'] = len(live_service.online_players(state['server_id']))
                state['leaderboard_preview'] = live_service.leaderboard(state['server_id'], 20)
            except Exception:
                state['power'] = int(state.get('power', 0))
                state['online_count'] = 0
                state['leaderboard_preview'] = []
        return state

    def tower_info(self, state):
        saved = state.get('tower', {})
        now = self.now()
        tickets = 10 if self.developer else min(10, int(saved.get('tickets', state['items'].get('13', 10))))
        at = int(saved.get('at', now))
        if tickets < 10 and now > at:
            tickets = min(10, tickets + (now - at) // 1800)
            at += ((now - at) // 1800) * 1800
        if tickets == 10: at = now
        floor = min(len(TOWER) + 1, int(saved.get('max_stage', 0)) + 1)
        floors = []
        for number in range(max(1, floor - 5), min(len(TOWER), floor + 9) + 1):
            row = TOWER[str(number)]
            battle = TABLES['battle'].get(str(row['battle_id']))
            enemies = []
            if battle:
                for monster_id in str(battle['monsters']).split('|'):
                    monster = TABLES['monster'].get(monster_id)
                    if not monster:
                        battle = None
                        enemies = []
                        break
                    enemies.append({'id': int(monster_id), 'partner_id': int(monster['partner_link']),
                                    'level': int(monster['lv_show'])})
            floors.append({'id': number, 'power': row['power'], 'rewards': quiz_reward_pairs(row['reward']),
                           'enemies': enemies, 'current': number == floor, 'cleared': number < floor,
                           'available': bool(battle), 'visible': number <= floor + 9})
        return {'floor': floor, 'max_stage': floor - 1, 'tickets': tickets,
                'next_ticket_seconds': 0 if tickets == 10 else max(0, 1800 - (now - at)),
                'floors': floors}

    def missions_probe(self, state):
        roster = self.snapshot_roster(state) if hasattr(self, 'snapshot_roster') else [
            {**p_, 'stars': int(TABLES['partner'][str(p_['table_id'])]['max_star']) + int(p_.get('awake', 0))} for p_ in state['partners']]
        cleared = int(state.get('max_stage', 0)); chapter = 0
        for row in TABLES['stage'].values():
            if int(row['id']) <= cleared: chapter = max(chapter, int(row.get('fort_finish') or 0))
        state['max_chapter'] = chapter
        return roster

    def missions_action(self, request):
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); roster = self.missions_probe(state)
                result = missions.action(state, request, player_level(state), roster, self.now())
                state.pop('max_chapter', None)
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def shops_action(self, request):
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                result = shops.action(state, request, player_level(state), self.now())
                if request.get('action') == 'buy':
                    if int(request.get('shop', 0)) == 7: growth_diary.record(state, 'growth_market', max(1, int(request.get('num', 1))))
                    if int(request.get('shop', 0)) == 13: growth_diary.record(state, 'growth_league_shop', max(1, int(request.get('num', 1))))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def relations_action(self, request):
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                result = relations.action(state, request)
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def arena_action(self, request):
        """Junior Varsity (gxb2/arena.py): fights run the original battle engine against the rival lineup."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); reports = []
                def fight(lineup):
                    formation = self.validate_formation(state, state['formation'])
                    owned = {x['partner_id']: x for x in state['partners']}
                    team_a = [{**copy.deepcopy(owned[x['partner_id']]), 'pos': x['pos']} for x in formation]
                    team_b = [{'partner_id': 1000 + u['pos'], 'table_id': u['table_id'], 'lv': u['lv'], 'grade': 0, 'awake': 0,
                               'equips': [], 'pos': u['pos'], 'show_skin': 1} for u in lineup]
                    battle_id = int(TABLES['stage']['1']['battle_id'])
                    report = self._simulate(state, team_a, team_b, battle_id, secrets.randbelow(233280), self.battle_pet(state), guild_skills_a=guild_lab.skills(state))
                    report['map_asset'] = TABLES['battle'][str(battle_id)]['map']; report['display_units'] = []
                    for side in ('teamA', 'teamB'):
                        for unit in report[side]:
                            tid = unit['table_id']
                            report['display_units'].append({'pos': unit['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                                                            'name': TABLES['names'].get(str(tid), f'Rival {tid}'), 'level': unit['level']})
                    mark_bosses(report); reports.append(report)
                    return bool(report['isWin']), len(reports) - 1
                result = arena.action(state, request, player_level(state), self.now(), fight=fight)
                if request.get('action') == 'fight':
                    missions.record(state, 'arena', 1, self.now())
                    if result.get('win'): missions.record(state, 'arena_win', 1, self.now())  # Fantasy Book "Win N battles"
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            if reports: result['report'] = reports[-1]
            return {'state': self.snapshot(), **result}

    def arena3v3_action(self, request):
        """Arena 3v3 (gxb2/arena3v3.py): best of three, each battle with the original engine (team k vs rival team k)."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); reports = []
                owned = {x['partner_id']: x for x in state['partners']}
                def fight(k, lineup):
                    team = state['arena3v3']['teams'][k]
                    team_a = [{**copy.deepcopy(owned[x['partner_id']]), 'pos': x['pos']} for x in team]
                    team_b = [{'partner_id': 1000 + u['pos'], 'table_id': u['table_id'], 'lv': u['lv'], 'grade': 0, 'awake': 0,
                               'equips': [], 'pos': u['pos'], 'show_skin': 1} for u in lineup]
                    battle_id = int(TABLES['stage']['1']['battle_id'])
                    report = self._simulate(state, team_a, team_b, battle_id, secrets.randbelow(233280), self.battle_pet(state), guild_skills_a=guild_lab.skills(state))
                    report['map_asset'] = TABLES['battle'][str(battle_id)]['map']; report['display_units'] = []
                    for side in ('teamA', 'teamB'):
                        for unit in report[side]:
                            tid = unit['table_id']
                            report['display_units'].append({'pos': unit['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                                                            'name': TABLES['names'].get(str(tid), f'Rival {tid}'), 'level': unit['level']})
                    mark_bosses(report); reports.append(report)
                    return bool(report['isWin']), len(reports) - 1
                try: result = arena3v3.action(state, request, player_level(state), set(owned), self.now(), fight=fight)
                except arena3v3.Arena3v3Error as e: raise GameError(str(e))
                if request.get('action') == 'fight':
                    missions.record(state, 'arena', 1, self.now())
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            if reports: result['reports'] = reports
            return {'state': self.snapshot(), **result}

    @show_mode(19)
    def patrol_action(self, request):
        """Patrol (gxb2/patrol.py): one Girl vs the stage enemies with the original engine, battle type DUNGEON and
        the kept HP/energy of both sides passed as ReportHero status (hp %, mp, Stationery buffs)."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); reports = []
                def fight(girl, enemies, battle_id, buffs):
                    unit = {k: copy.deepcopy(v) for k, v in girl.items() if k != 'status'}
                    unit.update(pos=1, status={'hp': int(girl['status']['hp']), 'mp': int(girl['status'].get('mp', 50)), 'buffs': buffs})
                    team_b = [{'table_id': e['table_id'], 'pos': e['pos'], 'isMonster': True,
                               'status': {'hp': int(e['status']['hp']), 'mp': int(e['status'].get('mp', 50))}} for e in enemies]
                    report = self._simulate(state, [unit], team_b, battle_id, secrets.randbelow(233280), None, patrol.BATTLE_TYPE, guild_skills_a=guild_lab.skills(state))
                    report['map_asset'] = TABLES['battle'][str(battle_id)]['map']; report['display_units'] = []
                    for side in ('teamA', 'teamB'):
                        for u in report[side]:
                            tid = int(TABLES['monster'][str(u['table_id'])]['partner_link']) if u.get('isMonster') else u['table_id']
                            report['display_units'].append({'pos': u['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                                                            'name': TABLES['names'].get(str(tid), f'Enemigo {tid}'), 'level': u['level']})
                    mark_bosses(report); reports.append(report)
                    return report
                result = patrol.action(state, request, self.now(), fight=fight)
                if reports: growth_diary.record(state,'newbie_patrol',len(reports))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            result.pop('battle', None)
            if reports: result['report'] = reports[-1]
            return {'state': self.snapshot(), **result}

    @show_mode(35)
    def house_exam_action(self, request):
        """House Exam (gxb2/house_exam.py): the saved house formation (only that faction) and the Servant fight this
        season's enemy variant of the stage with the original engine."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); reports = []
                def fight(team, battle_id):
                    owned = {x['partner_id']: x for x in state['partners']}
                    team_a = [{**copy.deepcopy(owned[t['partner_id']]), 'pos': t['pos']} for t in team]
                    battle = TABLES['battle'][str(battle_id)]
                    team_b = [{'table_id': int(t), 'pos': int(q), 'isMonster': True} for t, q in zip(str(battle['monsters']).split('|'), str(battle['stands']).split('|'))]
                    report = self._simulate(state, team_a, team_b, battle_id, secrets.randbelow(233280), self.battle_pet(state), guild_skills_a=guild_lab.skills(state))
                    report['map_asset'] = battle['map']; report['display_units'] = []
                    for side in ('teamA', 'teamB'):
                        for u in report[side]:
                            tid = int(TABLES['monster'][str(u['table_id'])]['partner_link']) if u.get('isMonster') else u['table_id']
                            report['display_units'].append({'pos': u['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                                                            'name': TABLES['names'].get(str(tid), f'Enemigo {tid}'), 'level': u['level']})
                    mark_bosses(report); reports.append(report)
                    return report
                result = house_exam.action(state, request, self.now(), fight=fight)
                if request.get('action') == 'fight': missions.record(state, 'house_exam', 1, self.now())
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            result.pop('battle', None)
            if reports: result['report'] = reports[-1]
            return {'state': self.snapshot(), **result}

    def hero_challenge_action(self, request):
        """Character Challenge (gxb2/hero_challenge.py): the challenge's monster Girls, its Servant (level 90) and the
        Blessings as god_skills fight the stage battle with the original engine."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); reports = []
                def fight(rows, battle_id, pet, gods):
                    team_a = [{'table_id': r['table_id'], 'pos': r['pos'], 'isMonster': True} for r in rows]
                    battle = TABLES['battle'][str(battle_id)]
                    team_b = [{'table_id': int(t), 'pos': int(q), 'isMonster': True} for t, q in zip(str(battle['monsters']).split('|'), str(battle['stands']).split('|'))]
                    report = self._simulate(state, team_a, team_b, battle_id, secrets.randbelow(233280), pet, god_skills=gods)
                    report['map_asset'] = battle['map']; report['display_units'] = []
                    for side in ('teamA', 'teamB'):
                        for u in report[side]:
                            tid = int(TABLES['monster'][str(u['table_id'])]['partner_link']) if u.get('isMonster') else u['table_id']
                            report['display_units'].append({'pos': u['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                                                            'name': TABLES['names'].get(str(tid), f'Enemigo {tid}'), 'level': u['level']})
                    mark_bosses(report); reports.append(report)
                    return report
                result = hero_challenge.action(state, request, self.now(), fight=fight)
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            result.pop('battle', None)
            if reports: result['report'] = reports[-1]
            return {'state': self.snapshot(), **result}

    def sanctuary_action(self, request):
        """Sanctuary (gxb2/sanctuary.py): your Girls with their kept HP and the round's Blessings (god_skills) against
        the mirrored lineup or the sanctum boss, original engine with battle type TRIAL_NEW."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); reports = []
                def fight(rows_a, team_b, battle_id, gods):
                    scene = next(x for x in sanctuary.DATA['boss_scenes'] if int(x['id']) == state['sanctuary']['round']['boss'])
                    if team_b is None:
                        battle = TABLES['battle'][str(battle_id)]
                        team_b = [{'table_id': int(t), 'pos': int(q), 'isMonster': True} for t, q in zip(str(battle['monsters']).split('|'), str(battle['stands']).split('|'))]
                        map_asset = scene['battle_scene_boss']
                    else:
                        battle_id = int(TABLES['stage']['1']['battle_id']); map_asset = scene['battle_scene']
                    report = self._simulate(state, rows_a, team_b, battle_id, secrets.randbelow(233280), self.battle_pet(state), sanctuary.BATTLE_TYPE, god_skills=gods)
                    # new_trial_boss_scenes names the Deep Sea maps bg_trail_sences_*; the battle map files are battle_map_trail_sences_*.
                    report['map_asset'] = 'battle_map_' + map_asset[3:] if map_asset.startswith('bg_') else map_asset; report['display_units'] = []
                    for side in ('teamA', 'teamB'):
                        for u in report[side]:
                            tid = int(TABLES['monster'][str(u['table_id'])]['partner_link']) if u.get('isMonster') else u['table_id']
                            report['display_units'].append({'pos': u['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                                                            'name': TABLES['names'].get(str(tid), f'Enemigo {tid}'), 'level': u['level']})
                    mark_bosses(report); reports.append(report)
                    return report
                result = sanctuary.action(state, request, player_level(state), self.now(), fight=fight)
                if reports: missions.record(state, 'sanctuary', len(reports), self.now())
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            result.pop('battle', None)
            if reports: result['report'] = reports[-1]
            return {'state': self.snapshot(), **result}

    def house_dress_action(self, request):
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                result = house_dress.action(state, request)
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def internship_action(self, request):
        """Internship (gxb2/internship.py); a completed quest counts for the Internship daily task."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                result = internship.action(state, request, self.now())
                if request.get('action') == 'complete':
                    missions.record(state, 'tavern', 1, self.now())
                    if int(result.get('star', 0)) >= 4: missions.record(state, 'tavern4', 1, self.now())
                    if int(result.get('star', 0)) >= 6: missions.record(state, 'tavern6', 1, self.now())
                    if int(result.get('star', 0)) >= 3: missions.record(state, 'tavern3', 1, self.now())
                    if int(result.get('star', 0)) >= 5: missions.record(state, 'tavern5', 1, self.now())
                    if int(result.get('star', 0)) >= 7: missions.record(state, 'tavern7', 1, self.now())
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def midas_action(self, request):
        """Alchemy (gxb2/midas.py); every claim counts for the Alchemy daily task."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                result = midas.action(state, request, player_level(state), self.now())
                missions.record(state, 'midas', 1, self.now())
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    @show_mode(39)
    def old_campus_action(self, request):
        """Old Campus Exploration (gxb2/old_campus.py): the stage team (+ Servant) against the stage battle, with the chosen
        Exploration Plans as god_skills (they strengthen the enemies)."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); reports = []
                def fight(team, battle_id, gods):
                    owned = {x['partner_id']: x for x in state['partners']}
                    team_a = [{**copy.deepcopy(owned[t['partner_id']]), 'pos': t['pos']} for t in team]
                    battle = TABLES['battle'][str(battle_id)]
                    team_b = [{'table_id': int(t), 'pos': int(q), 'isMonster': True} for t, q in zip(str(battle['monsters']).split('|'), str(battle['stands']).split('|'))]
                    report = self._simulate(state, team_a, team_b, battle_id, secrets.randbelow(233280), self.battle_pet(state), god_skills=gods)
                    report['map_asset'] = str(battle['map']).split('|')[0]; report['display_units'] = []
                    for side in ('teamA', 'teamB'):
                        for u in report[side]:
                            tid = int(TABLES['monster'][str(u['table_id'])]['partner_link']) if u.get('isMonster') else u['table_id']
                            report['display_units'].append({'pos': u['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                                                            'name': TABLES['names'].get(str(tid), f'Enemigo {tid}'), 'level': u['level']})
                    mark_bosses(report); reports.append(report)
                    return report
                result = old_campus.action(state, request, self.now(), fight=fight)
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            result.pop('battle', None)
            if reports: result['report'] = reports[-1]
            return {'state': self.snapshot(), **result}

    def galaxy_action(self, request):
        """Galaxy Voyage (gxb2/galaxy.py): enemies keep their HP between attempts (status per position), the Ruler is
        weakened through galaxy_info and the battles use GALAXY_TRIP_BATTLE (66)."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); reports = []
                def fight(rows, battle_id, gods, status, galaxy_info):
                    battle = TABLES['battle'][str(battle_id)]
                    team_b = []
                    for t, q in zip(str(battle['monsters']).split('|'), str(battle['stands']).split('|')):
                        unit = {'table_id': int(t), 'pos': int(q), 'isMonster': True}
                        if status and str(q) in status:
                            unit['status'] = status[str(q)]
                        team_b.append(unit)
                    report = self._simulate(state, rows, team_b, battle_id, secrets.randbelow(233280), self.battle_pet(state), battle_type=66,
                                      god_skills=gods, galaxy_info=galaxy_info)
                    report['map_asset'] = str(battle['map']).split('|')[0]; report['display_units'] = []
                    for side in ('teamA', 'teamB'):
                        for u in report[side]:
                            tid = int(TABLES['monster'][str(u['table_id'])]['partner_link']) if u.get('isMonster') else u['table_id']
                            report['display_units'].append({'pos': u['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                                                            'name': TABLES['names'].get(str(tid), f'Enemigo {tid}'), 'level': u['level']})
                    mark_bosses(report); reports.append(report)
                    return report
                result = galaxy.action(state, request, self.now(), fight=fight)
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            result.pop('battle', None)
            if reports: result['report'] = reports[-1]
            return {'state': self.snapshot(), **result}

    def shrine_action(self, request):
        """Tsuruga Grand Shrine (gxb2/shrine.py): Realm of Trials battles with persistent HP, buffs + environment as god
        skills, the difficulty applied by the original engine (shrineId) and 15-round battles (SHRINE_HURDLE = 61)."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); reports = []
                def fight(rows, battle_id, gods, diff):
                    battle = TABLES['battle'][str(battle_id)]
                    team_b = [{'table_id': int(t), 'pos': int(q), 'isMonster': True} for t, q in zip(str(battle['monsters']).split('|'), str(battle['stands']).split('|'))]
                    report = self._simulate(state, rows, team_b, battle_id, secrets.randbelow(233280), self.battle_pet(state), battle_type=shrine.BATTLE_TYPE,
                                      god_skills=gods, shrine_id=diff, max_round=shrine.MAX_ROUND)
                    report['map_asset'] = str(battle['map']).split('|')[0]; report['display_units'] = []
                    for side in ('teamA', 'teamB'):
                        for u in report[side]:
                            tid = int(TABLES['monster'][str(u['table_id'])]['partner_link']) if u.get('isMonster') else u['table_id']
                            report['display_units'].append({'pos': u['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                                                            'name': TABLES['names'].get(str(tid), f'Enemigo {tid}'), 'level': u['level']})
                    mark_bosses(report); reports.append(report)
                    return report
                result = shrine.action(state, request, self.now(), fight=fight)
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            result.pop('battle', None)
            if reports: result['report'] = reports[-1]
            return {'state': self.snapshot(), **result}

    def soul_land_action(self, request):
        """Land of Souls (gxb2/soul_land.py): stage fights with the stage god skill (BattleType SOUL_LAND = 71), idle
        Soul Branches and the Store."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); reports = []
                def fight(battle_id, gods):
                    formation = self.validate_formation(state, request.get('team') or state['formation'])
                    owned = {x['partner_id']: x for x in state['partners']}
                    team_a = [{**copy.deepcopy(owned[x['partner_id']]), 'pos': x['pos']} for x in formation]
                    battle = TABLES['battle'][str(battle_id)]
                    team_b = [{'table_id': int(t), 'pos': int(q), 'isMonster': True} for t, q in zip(str(battle['monsters']).split('|'), str(battle['stands']).split('|'))]
                    report = self._simulate(state, team_a, team_b, battle_id, secrets.randbelow(233280), self.battle_pet(state), battle_type=soul_land.BATTLE_TYPE, god_skills=gods)
                    report['map_asset'] = str(battle['map']).split('|')[0]; report['display_units'] = []
                    for side in ('teamA', 'teamB'):
                        for u in report[side]:
                            tid = int(TABLES['monster'][str(u['table_id'])]['partner_link']) if u.get('isMonster') else u['table_id']
                            report['display_units'].append({'pos': u['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                                                            'name': TABLES['names'].get(str(tid), f'Enemigo {tid}'), 'level': u['level']})
                    mark_bosses(report); reports.append(report)
                    return report
                try: result = soul_land.action(state, request, self.now(), fight=fight)
                except (soul_land.LandError, souls.SoulError) as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            if reports: result['report'] = reports[-1]
            return {'state': self.snapshot(), **result}

    def stellar_altar_action(self, request):
        """Stellar Altar (gxb2/stellar_altar.py): House Cosmos draws, reward mode / target, 100 shards → a 10★ Cosmos girl."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                def add_girl(tid):
                    pid = state['next_partner_id']; state['next_partner_id'] += 1
                    state['partners'].append({'partner_id': pid, 'table_id': int(tid), 'lv': 1, 'grade': 0, 'awake': 0, 'equips': [], 'pos': 0, 'show_skin': 1, 'create_time': self.now()})
                    return pid
                try: result = stellar_altar.action(state, request, add_girl, self.developer)
                except stellar_altar.AltarError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def quick_formation_action(self, request):
        """Lineup presets (gxb2/quick_formation.py): save / rename / clear / set (formation + gear + potentials)."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = quick_formation.action(state, request, self.developer)
                except (quick_formation.QuickError, ValueError) as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def dress_show_action(self, request):
        """Outfit Showcase (gxb2/dress_show.py): unlock / place slots, daily Tag rewards, Showcase Store."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = dress_show.action(state, request, self.now())
                except dress_show.ShowError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def set_campaign_hang(self, request):
        """Campaign idle team (CampaignHangFormationWindow: defaultMaxNum 3, container_1 front, containers 2-3 back): the
        chibis of the hang scene, kept apart from the battle formation."""
        partners = (request or {}).get('partners')
        if not isinstance(partners, list) or not 1 <= len(partners) <= 3: raise GameError('Elige entre una y tres chicas')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                team = self.validate_formation(state, partners)
                if any(x['pos'] > 3 for x in team): raise GameError('Posición inválida')
                state['campaign_hang'] = team
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot()}

    def chimes_action(self, request):
        """Tree of Chimes (gxb2/chimes.py): activate, charge, enchant, ascend, transfer spare shards."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = chimes.action(state, request)
                except chimes.ChimeError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def pumpkin_action(self, request):
        """Halloween Pumpkin Patch (gxb2/pumpkin.py): cut, claim the round reward, buy daggers."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = pumpkin.action(state, request, self.now())
                except pumpkin.PumpkinError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def hearts_action(self, request):
        """Friend Hearts (gxb2/hearts.py): send / claim / Claim & Send with the local contacts; add recommended contacts."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = hearts.action(state, request, self.now())
                except hearts.HeartError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def fantasy_book_action(self, request):
        """Fantasy Book (gxb2/fantasy_book.py): claims, Gem levels, tasks, the two stores and Flora Bookmark draws."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); probe = dict(state); roster = self.missions_probe(probe)
                try: result = fantasy_book.action(state, request, player_level(state), roster, self.now())
                except fantasy_book.BookError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def collection_action(self, request):
        """Collection Store (gxb2/collection.py): buy with Collect Points unlocked."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = collection_mod.action(state, request, self.now())
                except collection_mod.CollectionError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def lost_space_action(self, request):
        """Lost Space Zone (gxb2/lost_space.py): explore, claim, events, lasers, Auto Explore, radars."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = lost_space.action(state, request, self.now())
                except lost_space.SpaceError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def guild_action(self, request):
        """Guild v1 (gxb2/guild.py): create/edit, sign-in, Cafeteria orders and Gym bosses (original battle engine, your formation)."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); reports = []
                def fight(row):
                    formation = self.validate_formation(state, state['formation'])
                    owned = {x['partner_id']: x for x in state['partners']}
                    team_a = [{**copy.deepcopy(owned[x['partner_id']]), 'pos': x['pos']} for x in formation]
                    battle = TABLES['battle'][str(row['battle_id'])]
                    team_b = [{'table_id': int(t), 'pos': int(q), 'isMonster': True} for t, q in zip(str(battle['monsters']).split('|'), str(battle['stands']).split('|'))]
                    report = self._simulate(state, team_a, team_b, int(row['battle_id']), secrets.randbelow(233280), self.battle_pet(state), guild_skills_a=guild_lab.skills(state))
                    report['map_asset'] = battle['map']; report['display_units'] = []
                    for side in ('teamA', 'teamB'):
                        for u in report[side]:
                            tid = int(TABLES['monster'][str(u['table_id'])]['partner_link']) if u.get('isMonster') else u['table_id']
                            report['display_units'].append({'pos': u['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                                                            'name': TABLES['names'].get(str(tid), f'Enemigo {tid}'), 'level': u['level']})
                    growth_diary.record(state,'growth_guild_damage',int(report.get('total_harm') or sum(int(h.get('hurt',0)) for h in report.get('hurts',[]) if int(h.get('pos',0))<=6)))
                    mark_bosses(report); reports.append(report)
                    return bool(report['isWin']), len(reports) - 1
                try: result = guild.action(state, request, self.now(), fight=fight, player_level=player_level(state))
                except guild.GuildError as e: raise GameError(str(e))
                if request.get('action') == 'order_complete': missions.record(state, 'guild_orders', 1, self.now())  # Cafeteria ranking (gxb2/bots.py)
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            result.pop('report_index', None)
            if reports: result['report'] = reports[-1]
            return {'state': self.snapshot(), **result}

    def pirate_action(self, request):
        """Deep Sea Treasures (gxb2/pirate.py): raid a land, collection rewards, daily compasses, free pack."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = pirate.action(state, request, self.now())
                except pirate.PirateError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def firework_project_action(self, request):
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = firework_project.action(state, request, self.now())
                except firework_project.FireworkError as exc: raise GameError(str(exc))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def puzzle_events_action(self, request):
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = puzzle_events.action(state, request, self.now())
                except puzzle_events.PuzzleError as exc: raise GameError(str(exc))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def blind_box_action(self, request):
        """Blind Box Frenzy (gxb2/blind_box.py): select rewards, open boxes, next round, daily coupons."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = blind_box.action(state, request, self.now())
                except blind_box.BlindError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def jackpot_action(self, request):
        """Jackpot of Fortune (gxb2/jackpot.py): spin, progress awards, coin transfer."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = jackpot.action(state, request, self.now())
                except jackpot.JackpotError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def act_draw_action(self, request):
        """Token draw minigames (gxb2/activity_draw.py): draw, claim a milestone, buy tokens, daily tokens."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = activity_draw.action(state, request, self.now())
                except activity_draw.DrawError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def act_kit_action(self, request):
        """Generic event kit (gxb2/activity_kit.py): open, buy in the exchange, claim a mission, daily supply."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = activity_kit.action(state, request, self.now())
                except activity_kit.KitError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def two_love_action(self, request):
        """Matching Pairs (gxb2/two_love.py): Start, reveal a card, deal again, Recharge Task."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = two_love.action(state, request, self.now())
                except two_love.LoveError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def magic_card_action(self, request):
        """Magic Card (gxb2/magic_card.py): Ultimate Reward, start, flip, next round, Magician's Assistant missions."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = magic_card.action(state, request, self.now())
                except magic_card.MagicError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def wish_action(self, request):
        """Wish Capsule (gxb2/wish.py): choose / switch the Wish Girl, claim the draw-count rewards."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = wish.action(state, request)
                except wish.WishError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def ev_sand_action(self, request):
        """Beach Treasure Hunt (gxb2/ev_sand.py): dig / auto, Midsummer Task missions, Ocean Coin Exchange."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = ev_sand.action(state, request)
                except ev_sand.SandError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def assistant_run(self, request):
        """Game Assistant (models/GameAssistant.lua, capture 2026-09-29-fb/83): the day's routine in one tap, each step through
        the same engine action the player would use (so every rule and cost is the original one). Steps: Alchemy free,
        Campaign loot, free Regular / Adv. Capsule, mail, finished Internships, Junior Varsity free battles and daily tasks.
        A step that cannot run today is reported and skipped."""
        want = set((request or {}).get('steps') or ['midas', 'campaign', 'capsule', 'senior', 'mail', 'internship', 'arena', 'daily'])
        opts = (request or {}).get('opts') or {}
        def count(key, hi=99):
            try: return max(0, min(hi, int(opts.get(key, 0))))
            except (TypeError, ValueError): return 0
        report = []
        def step(key, label, fn):
            if key not in want: return
            try:
                got = fn(); report.append({'key': key, 'label': label, 'ok': True, 'got': got or {}})
            except Exception as e:  # noqa: BLE001 — each step is independent
                report.append({'key': key, 'label': label, 'ok': False, 'error': str(e)})
        now = self.now
        def capsule(sid):
            with self.lock: st = self._load()
            if now() < int(st.get('summon_free_at' if sid == 3 else 'senior_summon_free_at', 0)): raise GameError('Ya usada hoy')
            self.handle('SUMMON', {'summon_id': sid}); return {}
        def internships():
            done = [m for m in self.snapshot()['internship_info']['missions'] if m.get('end') and m['end'] <= now()]
            if not done: raise GameError('Ninguna terminada')
            got = {}
            for m in done:
                for k, n in (self.internship_action({'action': 'complete', 'id': m['id']}).get('got') or {}).items(): got[k] = got.get(k, 0) + n
            return got
        def arena():
            info = self.snapshot()['arena_info']; n = 0
            if not info.get('enemies'): self.arena_action({'action': 'open'}); info = self.snapshot()['arena_info']
            while info.get('free', 0) > 0 and info.get('enemies') and n < 5:
                self.arena_action({'action': 'fight', 'id': info['enemies'][-1]['id']}); n += 1; info = self.snapshot()['arena_info']
            if not n: raise GameError('Sin batallas gratis')
            return {'battles': n}
        def daily():
            got = {}
            for t in self.snapshot()['missions_info']['daily']:
                if not t['claimed'] and t['have'] >= t['need']:
                    try:
                        for k, n in (self.missions_action({'action': 'daily', 'id': t['id']}).get('got') or {}).items(): got[k] = got.get(k, 0) + n
                    except Exception: pass
            if not got: raise GameError('Nada que reclamar')
            return got
        def merge(into, got):
            for k, n in (got or {}).items(): into[k] = into.get(k, 0) + n
            return into
        def repeat(fn, n, what):
            got, done = {}, 0
            for _ in range(n):
                try: merge(got, fn()); done += 1
                except Exception:
                    if not done: raise
                    break
            if not done: raise GameError('Nada que hacer')
            return got
        def quiz():
            # Daily Quiz "Use Free Chance": sweep the highest cleared difficulty of each quiz with the day's remaining chances
            got, n = {}, 0
            for cat in self.snapshot()['daily_quiz']['categories']:
                top = max([t['id'] for t in cat['tiers'] if t['cleared']] or [0])
                for _ in range(max(0, cat['limit'] - cat['used'])):
                    if not top: break
                    try: merge(got, self.run_daily_quiz({'quiz_id': top}, sweep=True).get('rewards')); n += 1
                    except Exception: break
            if not n: raise GameError('Sin intentos o sin dificultades superadas')
            return got
        def exam():
            # House Exams: the chosen house's highest stage cleared this season, raided with certificates
            fort = count('house', 6) or 1; n = count('house_raids', 50)
            with self.lock: st = self._load()
            h = (st.get('house_exam') or {})
            ok = [int(r['id']) for r in house_exam.FORTS[fort] if h and house_exam.passed(h, fort, int(r['id']))]
            if not ok: raise GameError('Stage not cleared yet')
            if not n: raise GameError('Elige cuántos Raids')
            r = self.house_exam_action({'action': 'sweep', 'stage': max(ok, key=house_exam.sort_of), 'times': n})
            return r.get('got') or {}
        def excursion():
            got = {}
            for b in (self.snapshot().get('home_systems') or {}).get('buildings') or []:
                if b.get('stock', 0) > 0:
                    try: merge(got, self.home_action({'action': 'travel_collect', 'id': b['id']}).get('got'))
                    except Exception: pass
            if not got: raise GameError('Todavía no hay recursos para recoger')
            return got
        step('midas', 'Alchemy', lambda: self.midas_action({'action': 'free'}).get('got'))
        if count('midas_buy'): step('midas', 'Alchemy · Purchase with Gems', lambda: repeat(lambda: self.midas_action({'action': 'buy'}).get('got'), count('midas_buy', 20), 'buy'))
        step('dorm', 'Dorm Resource', lambda: self.house_dress_action({'action': 'hang_collect'}).get('got'))
        step('quiz', 'Daily Quiz Reward', quiz)
        step('exam', 'House Exam Raid Reward', exam)
        step('excursion', 'Excursion - Resource Collection', excursion)
        if count('bread'): step('excursion', 'Excursion - Tasty Bread Purchase', lambda: self.explore_action({'action': 'buy_bread', 'count': count('bread', 50)}).get('got') or {'203': 0})
        step('guild_sign', 'Guild - Sign in', lambda: self.guild_action({'action': 'checkin'}).get('got'))
        def orders():
            gi = self.snapshot().get('guild_info') or {}
            lst = (gi.get('orders') or {}).get('list') or []
            n = 0
            for i, o in enumerate(lst):
                if not o.get('start'):
                    try: self.guild_action({'action': 'order_start', 'slot': i}); n += 1
                    except Exception: pass
            if not n: raise GameError('No hay pedidos por empezar')
            return {'orders': n}
        step('guild_order', 'Cafeteria - Start Order', orders)
        step('campaign', 'Claim Campaign Loot', lambda: self.campaign_action({'action': 'collect'}).get('awards'))
        step('capsule', 'Regular Capsule', lambda: capsule(3))
        step('senior', 'Adv. Capsule', lambda: capsule(8))
        step('mail', 'Mail', lambda: self.home_action({'action': 'mail_claim_all'}).get('got'))
        step('internship', 'Internship', internships)
        step('arena', 'Junior Varsity', arena)
        step('daily', 'Daily Tasks', daily)
        return {'state': self.snapshot(), 'report': report}

    def souls_action(self, request):
        """Anima Gear (gxb2/souls.py): equip / unequip, level up, awaken, extra buffs, boxes and the Anima Stone Ritual."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                try: result = souls.action(state, request)
                except souls.SoulError as e: raise GameError(str(e))
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def skins_action(self, request):
        """Girl skins (gxb2/skins.py): wear / take off (equipments[7]) and show_skin."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                result = skins.action(state, request)
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def dress_action(self, request):
        """Outfits (gxb2/dress.py): Locker Room, Closet, piece upgrades and the Outfit Store / Sale."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                result = dress.action(state, request, self.now())
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def story_action(self, request):
        """Main story (gxb2/story.py): mark scenes as watched and unlock Memories with Key of Memory."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                result = story.action(state, request)
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            return {'state': self.snapshot(), **result}

    def story_scene(self, plot_id):
        return {'lines': story.scene(int(plot_id))}

    def story_stage(self, stage_id):
        with self.lock:
            state = self._load()
        pre, post = story.stage_plots(state, int(stage_id))
        return {'pre': pre, 'post': post}

    def shrine_story(self, text_id):
        return {'lines': shrine.plot_lines(int(text_id))}

    def echoes_action(self, request):
        """Echoes of Time (gxb2/echoes.py): Observations, Planetarium, Stages (original engine) and Achievements."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); reports = []
                def fight(team, battle_id):
                    owned = {x['partner_id']: x for x in state['partners']}
                    team_a = [{**copy.deepcopy(owned[int(t['partner_id'])]), 'pos': int(t['pos'])} for t in team]
                    battle = TABLES['battle'][str(battle_id)]
                    team_b = [{'table_id': int(t), 'pos': int(q), 'isMonster': True} for t, q in zip(str(battle['monsters']).split('|'), str(battle['stands']).split('|'))]
                    report = self._simulate(state, team_a, team_b, battle_id, secrets.randbelow(233280), self.battle_pet(state))
                    report['map_asset'] = str(battle['map']).split('|')[0]; report['display_units'] = []
                    for side in ('teamA', 'teamB'):
                        for u in report[side]:
                            tid = int(TABLES['monster'][str(u['table_id'])]['partner_link']) if u.get('isMonster') else u['table_id']
                            report['display_units'].append({'pos': u['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                                                            'name': TABLES['names'].get(str(tid), f'Enemigo {tid}'), 'level': u['level']})
                    mark_bosses(report); reports.append(report)
                    return report
                result = echoes.action(state, request, self.now(), fight=fight)
                if request.get('action') == 'claim':
                    growth_diary.record(state, 'growth_echoes_gold', int(result.get('got', {}).get('1', 0)))
                    missions.record(state, 'echoes_obs', 1, self.now())  # an Observation completed
                result['detail'] = echoes.detail(state, int(state['echoes'].get('world', 1)), self.now())
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            result.pop('battle', None)
            if reports: result['report'] = reports[-1]
            return {'state': self.snapshot(), **result}

    def explore_action(self, request):
        """Excursion → Explore (gxb2/explore.py). Enemy encounters run the original battle engine."""
        if not isinstance(request, dict): raise GameError('Datos inválidos')
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load(); reports = []
                def fight(battle_id):
                    formation = self.validate_formation(state, state['formation'])
                    owned = {x['partner_id']: x for x in state['partners']}
                    team_a = [{**copy.deepcopy(owned[x['partner_id']]), 'pos': x['pos']} for x in formation]
                    battle = TABLES['battle'][str(battle_id)]
                    team_b = [{'table_id': int(t), 'pos': int(q), 'isMonster': True} for t, q in zip(str(battle['monsters']).split('|'), str(battle['stands']).split('|'))]
                    report = self._simulate(state, team_a, team_b, battle_id, secrets.randbelow(233280), self.battle_pet(state), guild_skills_a=guild_lab.skills(state))
                    report['map_asset'] = battle['map']; report['display_units'] = []
                    for side in ('teamA', 'teamB'):
                        for unit in report[side]:
                            tid = int(TABLES['monster'][str(unit['table_id'])]['partner_link']) if unit.get('isMonster') else unit['table_id']
                            report['display_units'].append({'pos': unit['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                                                            'name': TABLES['names'].get(str(tid), f'Enemigo {tid}'), 'level': unit['level']})
                    mark_bosses(report); reports.append(report)
                    return bool(report['isWin']), len(reports) - 1
                result = explore.action(state, request, self.now(), fight=fight)
                self._save_profile(state)
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            if reports: result['report'] = reports[-1]
            return {'state': self.snapshot(), **result}

    @show_mode(15)
    def run_tower(self, request):
        floor = integer(request.get('floor'), 'floor', 1, len(TOWER))
        practice = request.get('practice', False) is True
        with self.lock:
            state = self._load()
            info = self.tower_info(state)
            if floor < info['floor']:
                raise GameError('This Tests stage is cleared. KEEP OUT.')
            if practice:
                if floor > info['floor']:
                    raise GameError('Todavía no has llegado a ese piso')
            elif floor != info['floor']:
                raise GameError('Solo puedes avanzar desde el piso actual')
            if not practice and info['tickets'] < 1:
                raise GameError('No quedan fichas de Tests; se recupera una cada 30 minutos')
            row = TOWER[str(floor)]
            if str(row['battle_id']) not in TABLES['battle']:
                raise GameError('Faltan datos de combate para este piso en el motor recuperado')
            formation = self.validate_formation(state, state['formation'])
            owned = {x['partner_id']: x for x in state['partners']}
            team_a = [{**copy.deepcopy(owned[x['partner_id']]), 'pos': x['pos']} for x in formation]
            battle = TABLES['battle'][str(row['battle_id'])]
            monsters = str(battle['monsters']).split('|')
            positions = str(battle['stands']).split('|')
            if len(monsters) != len(positions): raise GameError('Tabla de combate de Tests inconsistente')
            team_b = [{'table_id': int(tid), 'pos': int(pos), 'isMonster': True}
                      for tid, pos in zip(monsters, positions)]
            report = self._simulate(state, team_a, team_b, row['battle_id'], secrets.randbelow(233280), self.battle_pet(state), guild_skills_a=guild_lab.skills(state))
            report['map_asset'] = battle['map']
            report['display_units'] = []
            for side in ('teamA', 'teamB'):
                for unit in report[side]:
                    tid = unit['table_id']
                    if unit.get('isMonster'):
                        tid = int(TABLES['monster'][str(tid)]['partner_link'])
                    report['display_units'].append({'pos': unit['pos'] + (6 if side == 'teamB' else 0),
                                                    'table_id': tid, 'name': TABLES['names'].get(str(tid), f'Enemigo {tid}'),
                                                    'level': unit['level']})
            win = bool(report['isWin'])
            rewards = {k: local_config.scale_reward(v) for k, v in quiz_reward_pairs(row['reward']).items()} if win and not practice else {}
            if not practice:
                now = self.now()
                tickets = info['tickets'] - 1
                # Once full, the first spent ticket starts a fresh 30-minute recharge.
                at = now if info['tickets'] == 10 else now - (1800 - info['next_ticket_seconds'])
                state['tower'] = {'max_stage': floor if win else floor - 1, 'tickets': tickets, 'at': at}
                missions.record(state, 'tower', 1, now)
                state['items']['13'] = tickets
                for item_id, amount in rewards.items():
                    state['items'][item_id] = int(state['items'].get(item_id, 0)) + amount
                try:
                    self.db.execute('BEGIN IMMEDIATE')
                    self._save_profile(state)
                    self.db.commit()
                except Exception:
                    self.db.rollback()
                    raise
            return {'state': self.snapshot(), 'report': mark_bosses(report), 'win': win,
                    'practice': practice, 'floor': floor, 'rewards': rewards}

    def daily_quiz_info(self, state):
        saved = state.get('daily_quiz', {})
        today = max(quiz_day(self.now()), saved.get('day',''))
        used = saved.get('used', {}) if saved.get('day') == today else {}
        cleared = saved.get('cleared', {})
        categories = []
        for quiz_type, label, artwork in ((1, 'Recursos', 'quiz_mana'),
                                          (2, 'Experiencia', 'quiz_exp'),
                                          (3, 'Fragmentos', 'quiz_hero')):
            tiers = []
            for row in sorted((v for v in DAILY_QUIZ['quizzes'].values() if v['type'] == quiz_type), key=lambda v: v['id']):
                tiers.append({'id': row['id'], 'level': row['level'], 'difficulty': row['difficulty'],
                              'power': row['power'], 'rewards': quiz_reward_pairs(row['show_awards']),
                              'cleared': row['id'] <= int(cleared.get(str(quiz_type), 0))})
            categories.append({'type': quiz_type, 'name': label, 'art': artwork,
                               'used': 0 if self.developer else int(used.get(str(quiz_type), 0)), 'limit': 2,
                               'tiers': tiers})
        return {'day': today, 'categories': categories}

    def run_daily_quiz(self, request, sweep=False):
        quiz_id = integer(request.get('quiz_id'), 'quiz_id', 1)
        practice = request.get('practice', False) is True and not sweep
        row = DAILY_QUIZ['quizzes'].get(str(quiz_id))
        if row is None: raise GameError('Dificultad de Daily Quiz desconocida')
        with self.lock:
            state = self._load()
            saved = state.setdefault('daily_quiz', {'day': quiz_day(self.now()), 'used': {}, 'cleared': {}})
            today = max(quiz_day(self.now()), saved.get('day',''))
            if saved.get('day') != today:
                saved['day'], saved['used'] = today, {}
            quiz_type = str(row['type'])
            used = int(saved.setdefault('used', {}).get(quiz_type, 0))
            if not practice:
                if player_level(state) < row['level']:
                    raise GameError(f'Daily Quiz requiere nivel {row["level"]} para esta dificultad')
                if used >= 2 and not self.developer: raise GameError('Ya se usaron los dos intentos de hoy')
                if sweep and int(saved.setdefault('cleared', {}).get(quiz_type, 0)) < quiz_id:
                    raise GameError('Primero debes ganar esta dificultad')
            formation = self.validate_formation(state, state['formation'])
            owned = {x['partner_id']: x for x in state['partners']}
            team_a = [{**copy.deepcopy(owned[x['partner_id']]), 'pos': x['pos']} for x in formation]
            stages = []
            for part in row['random_stages'].split('|'):
                stage_id, weight = map(int, part.split('#'))
                if str(stage_id) not in DAILY_QUIZ['stages'] or weight <= 0:
                    raise GameError('Tabla original de Daily Quiz incompleta')
                stages.append((stage_id, weight))
            draw = secrets.randbelow(sum(weight for _, weight in stages))
            for stage_id, weight in stages:
                draw -= weight
                if draw < 0: break
            stage = DAILY_QUIZ['stages'][str(stage_id)]
            battle = TABLES['battle'][str(stage['battle_id'])]
            monsters = str(battle['monsters']).split('|')
            positions = str(battle['stands']).split('|')
            if len(monsters) != len(positions): raise GameError('Tabla de batalla inconsistente')
            team_b = [{'table_id': int(tid), 'pos': int(pos), 'isMonster': True}
                      for tid, pos in zip(monsters, positions)]
            report = None
            if not sweep:
                report = self._simulate(state, team_a, team_b, stage['battle_id'], secrets.randbelow(233280), self.battle_pet(state), guild_skills_a=guild_lab.skills(state))
                report['map_asset'] = battle['map']
                units = []
                for side in ('teamA', 'teamB'):
                    for unit in report[side]:
                        tid = unit['table_id']
                        if unit.get('isMonster'):
                            tid = int(TABLES['monster'][str(tid)]['partner_link'])
                        units.append({'pos': unit['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                                      'name': TABLES['names'].get(str(tid), f'Enemigo {tid}'), 'level': unit['level']})
                report['display_units'] = units
            win = bool(sweep or report['isWin'])
            rewards = {k: local_config.scale_reward(v) for k, v in quiz_reward_pairs(stage['awards']).items()} if win and not practice else {}
            if not practice and win:
                try:
                    self.db.execute('BEGIN IMMEDIATE')
                    saved['used'][quiz_type] = used + 1
                    home_systems.record(state, 'quiz', now=self.now())
                    saved.setdefault('cleared', {})[quiz_type] = max(quiz_id, int(saved['cleared'].get(quiz_type, 0)))
                    for item_id, amount in rewards.items():
                        state['items'][item_id] = int(state['items'].get(item_id, 0)) + amount
                    self._save_profile(state)
                    self.db.commit()
                except Exception:
                    self.db.rollback()
                    raise
            return {'state': self.snapshot(), 'report': mark_bosses(report), 'win': win, 'practice': practice,
                    'sweep': sweep, 'quiz_id': quiz_id, 'stage_id': stage_id, 'rewards': rewards}

    def match_materials(self, owned, ids, required, group):
        used = set()
        for needed in required:
            for pid in ids:
                if pid in used: continue
                girl = owned[pid]
                if acquisition.is_locked(girl):continue
                row = TABLES['partner'][str(girl['table_id'])]
                star = int(row['max_star']) + int(girl.get('awake', 0))
                exact = needed == girl['table_id'] and star == int(row['max_star'])
                wildcard_group = 0 if needed % 10000 == 9999 else (needed // 1000) % 10
                wildcard = needed % 1000 == 999 and star == needed // 10000 and (not wildcard_group or int(row['group']) == wildcard_group)
                if exact or wildcard:
                    used.add(pid)
                    break
            else: raise GameError('Los materiales no coinciden con la receta original')
        return used

    def next_stage(self, state):
        if state['max_stage'] == 0: return 1
        return int(TABLES['stage'][str(state['max_stage'])]['next']) or state['max_stage']

    def level_cap(self, partner, real=False):
        # Partner:getMaxLev(grade, awake) + PartnerTable:getMaxlev(id, grade).
        if self.developer and not real: return 330
        row = TABLES['partner'][str(partner['table_id'])]
        grade, awake = int(partner.get('grade', 0)), int(partner.get('awake', 0))
        if int(partner['table_id']) in local_promotion.BASE and awake:
            return local_promotion.CAPS[min(10,int(row['max_star'])+awake)]
        top = int(row['max_lv'])
        base = top if grade + 1 > int(row.get('max_grade') or 0) else int(row.get(f'grade_lv{grade+1}') or top)
        if not awake: return base
        if int(row['max_star']) + awake < 10: return base + AWAKE_LEVEL_STEP * awake
        return BREAK_LEVEL_CAP[min(awake, len(BREAK_LEVEL_CAP)) - 1]

    def altar_returns(self, state, ids):
        """AltarWindow (Campus → Transfer), Partner:getDecompose: the table's `decompose`, 70 % of the Grade Stones of her grades
        (and of her awakens below 10★) and 65 % of the girl EXP of her level; her gear goes back to the bag on retiring
        (equipment.release). Returns ({item: n}, number of 6★+ girls: altar_6up_day_limit allows 5 a day)."""
        if not isinstance(ids, list) or not 1 <= len(ids) <= 12 or len(set(ids)) != len(ids) or any(type(i) is not int for i in ids):
            raise GameError('Elige entre 1 y 12 chicas')
        owned = {g['partner_id']: g for g in state['partners']}
        if any(i not in owned for i in ids): raise GameError('No tienes esa chica')
        if len(ids) >= len(state['partners']): raise GameError('No puedes retirar a todas tus chicas')
        pending = (state.get('exchange') or {}).get('partner_id')
        got, six = {}, 0
        def add(k, n):
            if n > 0: got[str(k)] = got.get(str(k), 0) + int(n)
        for pid in ids:
            g = owned[pid]; row = TABLES['partner'][str(g['table_id'])]
            if any(g.get('flags') or []): raise GameError('Hay una chica bloqueada en la selección')
            if int(row['group']) == 7 or int(g['table_id']) in RETURN['puppets']: raise GameError('Las chicas Cosmos y las muñecas no van al Altar')
            if pid == pending: raise GameError('Resuelve primero el intercambio pendiente')
            star = int(row['max_star']) + int(g.get('awake', 0)); six += star >= 6
            for k, n in item_pairs(row.get('decompose') or '').items(): add(k, n)
            for i in range(1, int(g.get('grade', 0)) + 1):
                add('10', math.floor(item_pairs(row.get(f'grade_exp{i}') or '').get(10, 0) * 0.7))
            if star < 10:
                for i in range(int(g.get('awake', 0))):
                    rec = ASCENSION.get(f"{g['table_id']}:{int(row['max_star']) + i + 1}") or {}
                    add('10', math.floor(int((rec.get('cost') or {}).get('10', 0)) * 0.7))
            add('9', math.floor(0.65 * int(str(TABLES['exp_partner'][str(g['lv'])]['all_exp']).split('#')[1])))
        return got, six

    def altar_preview(self, request):
        with self.lock:
            state = self._load()
        got, six = self.altar_returns(state, (request or {}).get('partner_ids'))
        return {'items': got, 'six': six, 'six_left': 5 - int((state.get('altar') or {}).get('six', 0) if (state.get('altar') or {}).get('day') == clock.day(self.now()) else 0)}

    def awake_recipe(self, partner):
        """11–15★: awake_material / stone_material of the 10★ row (ASCENSION covers 6–10★)."""
        row = TABLES['partner'][str(partner['table_id'])]
        awake = int(partner.get('awake', 0))
        mats = [m for m in str(row.get('awake_material') or '').split('|') if m]
        if int(row['max_star']) != 10 or awake >= len(mats): return None
        costs = [c for c in str(row.get('stone_material') or '').split('|') if c]
        cost = {k: v for k, v in item_pairs(costs[awake]).items()} if awake < len(costs) else {}
        return {'kind': 'awake', 'material': [int(x) for x in mats[awake].split('#')], 'group': int(row['group']),
                'cost': {str(k): v for k, v in cost.items()}, 'star': 11 + awake}

    def validate_formation(self, state, formation):
        if not isinstance(formation, list) or not 1 <= len(formation) <= 6:
            raise GameError('Selecciona entre una y seis integrantes')
        owned = {v['partner_id'] for v in state['partners']}
        seen_ids, seen_positions = set(), set()
        out = []
        for slot in formation:
            if not isinstance(slot, dict): raise GameError('Formación inválida')
            pid = integer(slot.get('partner_id'), 'partner_id', 1)
            pos = integer(slot.get('pos'), 'pos', 1, 6)
            if pid not in owned or pid in seen_ids or pos in seen_positions:
                raise GameError('Formación con integrante o posición inválida o duplicada')
            seen_ids.add(pid); seen_positions.add(pos)
            out.append({'partner_id': pid, 'pos': pos})
        return sorted(out, key=lambda x: x['pos'])

    def map_info(self, state):
        return {'map_type': 1, 'max_stage': state['max_stage'], 'current_stage': state['current_stage'],
                'hang_time': self.now(), 'first_hang_time': state['created'],
                'hang_team': state['formation'], 'max_hang_stage': state['max_stage']}

    def backpack(self, state):
        return {'items': [{'item_id': int(k), 'item_num': v} for k, v in sorted(state['items'].items())]}

    def slot_info(self, state):
        return {'partners': state['partners'], 'details': {'buy_times': 0, 'sort_type': 0, 'max_num': 100,
                'replace_partner_id': (state.get('exchange') or {}).get('partner_id',0),
                'replace_table_id': (state.get('exchange') or {}).get('replace_id',0)},
                'gallery': [v['table_id'] for v in state['partners']]}

    def login_info(self, state):
        now = self.now()
        avatar_id = int(state.get('profile', {}).get('avatar', 'head_1001').split('_')[-1])
        return {'player_info': {'uid': 'local-player-1', 'player_id': 1, 'server_time': now, 'avatar_id': avatar_id,
                                'last_time': now, 'player_name': state['name'], 'server_id': 1, 'picture_id': avatar_id,
                                'language': 1, 'created_time': state['created'], 'is_played': 1},
                'backpack_info': self.backpack(state), 'summon_info': self.summon_info(state), 'map_info': self.map_info(state),
                'slot_info': self.slot_info(state), 'midas_info': {'next_buy_time': now+86400},
                'guide_info': {'version': 1, 'marks': '', 'guide_type': 0, 'func_ids': ''},
                'shop_info': {'refresh_time': now+86400, 'shop_type': 1},
                'online_info': {'id': 1, 'time': now}, 'achievement_info': {},
                'growth_diary_info': {'awards': (state.get('growth_diary') or {}).get('chapters',[])}}

    def summon_info(self, state):
        interval = int(TABLES['summon']['3']['freetime_interval'])
        return {'last_time_3': max(0, state.get('summon_free_at', 0) - interval)}

    def summon_pool(self, dropbox_id, server_id='S1'):
        rows = []
        for source in TABLES['dropbox'].values():
            if source['dropbox_id'] != dropbox_id or str(source['item']).split('#')[0] not in TABLES['partner']:
                continue
            weight = world_live_config.summon_weight(source, TABLES['partner'], server_id)
            if weight <= 0:
                continue
            row = dict(source)
            row['_local_weight'] = weight
            rows.append(row)
        if not rows: raise GameError('Pool Triệu Hồi không còn phần thưởng hợp lệ theo cấu hình Local')
        return rows, sum(int(row['_local_weight']) for row in rows)

    def handle(self, name: str, request: dict):
        """Apply one command transactionally; returns response + ordered push packets."""
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                state = self._load()
                packets, report = self._dispatch(name, request, state)
                if name == 'SUMMON':
                    sid=request.get('summon_id')
                    if sid in (1,2,3): home_systems.record(state,'regular',int(TABLES['summon'][str(sid)]['summon_num']),now=self.now())
                    elif sid in (4,5,6,7,8): home_systems.record(state,'advanced',int(TABLES['summon'][str(sid)]['summon_num']),now=self.now())
                    if sid in (4,5,6,7,8): point_events.add(state,'advanced',int(TABLES['summon'][str(sid)]['summon_num']),now=self.now())
                    if sid in (4,5,6,7,8): missions.record(state,'advanced',int(TABLES['summon'][str(sid)]['summon_num']),self.now())
                    got5=sum(1 for x in (packets[0][2].get('summon_result') or {}).get('partners',[]) if int(TABLES['partner'][str(x['table_id'])].get('max_star',0) or 0)>=5)
                    if got5: missions.record(state,'star5',got5,self.now())
                    if sid in PROPHET_SUMMONS: missions.record(state,'enroll',int(TABLES['summon'][str(sid)]['summon_num']),self.now())
                    if sid in PROPHET_SUMMONS: point_events.add(state,'prophet',int(TABLES['summon'][str(sid)]['summon_num']),now=self.now())
                elif name in ('COMPOSE_PARTNER','AWAKE_PARTNER'): home_systems.record(state,'graduate',now=self.now()); missions.record(state,'graduate',1,self.now())
                if name == 'SUMMON':
                    config = TABLES['summon'][str(request['summon_id'])]
                    if int(request['summon_id']) == 9: growth_diary.record(state, 'growth_bff', int(config['summon_num']))
                    fragment_ids = {int(x['summon_id']) for x in DEBRIS.values() if x.get('summon_id')}
                    if int(request['summon_id']) in fragment_ids:
                        count = sum(int(TABLES['partner'][str(x['table_id'])]['max_star']) >= 5 for x in packets[0][2].get('summon_result', {}).get('partners', []))
                        growth_diary.record(state, 'growth_shard5', count)
                if name == 'COMPOSE_PARTNER':
                    if int(TABLES['partner'][str(request['table_id'])]['max_star']) == 5: growth_diary.record(state, 'growth_graduate5')
                if name == 'MAP_FIGHT' and len(state.get('formation', [])) == 6: growth_diary.record(state, 'growth_full_team')
                if name == 'PROPHET_REPLACE_SAVE' and request.get('is_save'): growth_diary.record(state, 'growth_exchange')
                if name == 'GAMBLE_GET_AWARD' and int(request.get('gamble_type', 1)) == 2: growth_diary.record(state, 'growth_high_slots', max(1,len(packets[0][2].get('awards', []))))
                # Validate every emitted message before persisting the associated rewards/state.
                for mid, typ, payload in packets:
                    p.encode(typ, payload)
                self._save_profile(state)
                if report is not None:
                    self.db.execute('INSERT INTO battles VALUES(?,?,?)', (state['battle_count'], request['stage_id'], json.dumps(report)))
                self.db.commit()
                return packets
            except Exception:
                self.db.rollback()
                raise

    def _dispatch(self, name, request, state):
        def response(data, typ=None): return [(p.MIDS[name], typ or p.message_type(p.MIDS[name], 'res'), data)], None
        if name == 'CHECK_LOGIN':
            valid = request.get('player_id') == 1 and request.get('token') == LOCAL_TOKEN
            return response({'player_id': 1, 'check_token': valid, 'token': LOCAL_TOKEN if valid else ''})
        if name == 'RECONNECT':
            return response({'isSuccess': request.get('player_id') == 1 and request.get('token') == LOCAL_TOKEN})
        if name == 'HEART_BEAT_SYNC': return response({'server_time': self.now()})
        if name == 'GET_LOGIN_INFO': return response(self.login_info(state))
        if name in ('GET_FRIEND_BOSS_INFO','FRIEND_BOSS_FIGHT'):
            friend_boss.observe_power(state,self.now(),self._friend_power(state))
            if name=='GET_FRIEND_BOSS_INFO':
                info=friend_boss.snapshot(state,self.now(),player_level(state));f=friend_boss.saved(state,self.now())
                return response({'update_time':self.now(),'shared_times':0,'unlock_stage':info['unlock'],'is_done':int(info['done']),'self_win_counts':[f['wins'].get(str(i),0) for i in range(1,13)]})
            result=friend_boss.action(state,{'action':'fight','boss':request.get('stage_id')},self.now(),player_level(state),fight=lambda row:self._remaining_battle(state,row,{**request,**({'pet':request['pet_id']} if 'pet_id' in request else {})},7))
            packets=response({'battle_report':p.normalize('battle_data',result['report'],strict=False),'items':[{'item_id':int(i),'item_num':n} for i,n in result['got'].items()]})[0]
            packets.append((p.MIDS['ITEM_CHANGE'],'item_change_res',self.backpack(state)));return packets,None
        if name in ('ACTIVE_PET_EXLEVEL','UPGRADE_PET_EXLEVEL','RESET_PET_EXLEVEL') or name.startswith('PET_TRAINING_'):
            if name in ('ACTIVE_PET_EXLEVEL','UPGRADE_PET_EXLEVEL','RESET_PET_EXLEVEL'):
                actions={'ACTIVE_PET_EXLEVEL':'core_unlock','UPGRADE_PET_EXLEVEL':'core_upgrade','RESET_PET_EXLEVEL':'core_reset'}
                result=pet_training.action(state,{'action':actions[name],'pet':request.get('pet_id'),'count':request.get('num',1)},self.now());pid=result['pet'];pet=pet_training.pets(state)[str(pid)]
                payload={'pet_info':{'pet_id':pid,'lv':pet['lv'],'grade':pet['grade'],'skills':pet['skills'],'ex_lv':pet.get('exlv',0)}}
                if name=='RESET_PET_EXLEVEL':payload['restore_items']=[{'item_id':int(i),'item_num':n} for i,n in result['got'].items()]
            else:
                actions={'PET_TRAINING_GET_INFO':'open','PET_TRAINING_FIGHT':'fight','PET_TRAINING_SELECT_BOSS':'select','PET_TRAINING_BUY_TIMES':'buy','PET_TRAINING_GET_AWARD':'collect','PET_TRAINING_START_MISSION':'start','PET_TRAINING_CANCEL_MISSION':'cancel','PET_TRAINING_COMPLETE_MISSION':'complete'}
                if name not in actions:raise GameError('Mensaje Training no disponible')
                if request.get('pet_ids'):raise GameError('Esta variante del cliente utiliza un Servant por ataque')
                result=pet_training.action(state,{'action':actions[name],'pet':request.get('pet_id'),'boss':request.get('boss_id'),'slot':request.get('id'),'lesson':request.get('mission_id'),'pets':request.get('pets')},self.now())
                t=pet_training.saved(state,self.now());base={'times':t['times'],'pet_times':[t['pet_times'].get(str(i),0) for i in range(101,902,100)],'buy_times':t['buy_times']}
                payload={}
                if name=='PET_TRAINING_GET_INFO':payload={**base,'update_time':self.now(),'boss_id':t['boss_id'],'boss_hp':t['boss_hp'],'hang_time':t['hang_time'],'missions':[t['missions'].get(str(i),{}).get('mission_id',0) for i in range(1,4)],'mission_list':[p.normalize('pet_training_mission',t['missions'].get(str(i),{'start_time':0,'mission_id':0,'pets':[]}),strict=False) for i in range(1,4)]}
                elif name=='PET_TRAINING_FIGHT':payload={**base,'boss_hp':t['boss_hp'],'harm':result['harm'],'reborn_count':result['reborn_count']}
                elif name=='PET_TRAINING_SELECT_BOSS':payload={'boss_id':t['boss_id']}
                elif name=='PET_TRAINING_BUY_TIMES':payload={**base,'num':1}
                elif name=='PET_TRAINING_START_MISSION':payload={'id':request['id'],'info':p.normalize('pet_training_mission',t['missions'][str(request['id'])],strict=False)}
                elif name=='PET_TRAINING_CANCEL_MISSION':payload={'id':request['id']}
                elif name=='PET_TRAINING_COMPLETE_MISSION':payload={'id':request['id'],'items':[{'item_id':int(i),'item_num':n} for i,n in result['got'].items()]}
                elif name=='PET_TRAINING_GET_AWARD':payload={'hang_time':t['hang_time'],'items':[{'item_id':int(i),'item_num':n} for i,n in result['got'].items()]}
            packets=response(payload)[0]
            packets.append((p.MIDS['ITEM_CHANGE'],'item_change_res',self.backpack(state)));return packets,None

        if name in ('GET_ROOKIE_MISSION_LIST','GET_ROOKIE_MISSION_AWARD'):
            roster=self.missions_probe(dict(state));level=player_level(state)
            newbie_camp.observe(state,roster,level,self.now())
            snap=newbie_camp.snapshot(state,roster,level);d=newbie_camp.saved(state)
            if name=='GET_ROOKIE_MISSION_LIST':
                rows=[{'mission_id':t['id'],'value':t['have'],'is_completed':int(t['complete']),'is_awarded':int(t['claimed'])} for b in snap['phases'] for t in b['tasks']]
                for phase,b in newbie_camp.BOARDS.items():
                    count=sum(i in d['claimed'] for i in b['missions'])
                    rows.append({'mission_id':b['bonus_id'],'value':count,'is_completed':int(count==len(b['missions'])),'is_awarded':int(phase in d['bonuses'])})
                return response({'missions':sorted(rows,key=lambda r:r['mission_id'])})
            mid=growth_diary.checked(request.get('mission_id'));row=newbie_camp.TASKS.get(mid)
            if not row:raise GameError('Misión desconocida')
            if row['is_hide']:
                b=newbie_camp.BOARDS[int(row['phase_id'])]
                if not all(i in d['claimed'] for i in b['missions']):raise GameError('Reclama las misiones de esta etapa primero')
                newbie_camp.action(state,{'action':'open'},roster,level,self.now())
            else:newbie_camp.action(state,{'action':'mission','id':mid},roster,level,self.now())
            packets=response({'mission_id':mid})[0]
            packets.append((p.MIDS['ITEM_CHANGE'],'item_change_res',self.backpack(state)))
            return packets,None
        if name in ('GET_GROWTH_MISSIONS','GET_GROWTH_MISSIONS_AWARDS','GET_GROWTH_CHAPTER_AWARDS'):
            roster=self.missions_probe(dict(state));level=player_level(state)
            if name=='GET_GROWTH_CHAPTER_AWARDS':
                growth_diary.action(state,{'action':'chapter','id':request.get('id')},roster,level)
                packets=response({'id':request['id']})[0]
            else:
                ids=request.get('mission_ids',[])
                if not isinstance(ids,list) or len(ids)!=len(set(ids)):raise GameError('Misiones inválidas o repetidas')
                if any(growth_diary.checked(i) not in growth_diary.MISSIONS for i in ids):raise GameError('Misión desconocida')
                if name=='GET_GROWTH_MISSIONS':
                    snap=growth_diary.snapshot(state,roster,level)
                    tasks={t['id']:t for c in snap['chapters'] for t in c['tasks']}
                    packets=response({'missions':[{'mission_id':i,'value':tasks[i]['have'],'is_completed':int(tasks[i]['have']>=tasks[i]['need'] and tasks[i]['tracked']),'is_awarded':int(tasks[i]['claimed'])} for i in ids]})[0]
                else:
                    for i in ids:growth_diary.action(state,{'action':'mission','id':i},roster,level)
                    packets=response({'mission_ids':ids})[0]
            if name!='GET_GROWTH_MISSIONS':packets.append((p.MIDS['ITEM_CHANGE'],'item_change_res',self.backpack(state)))
            return packets,None
        if name == 'GET_MAP_INFO':
            if request.get('map_type', 1) != 1: raise GameError('Solo está implementado el mapa principal')
            return response(self.map_info(state))
        if name == 'GET_SLOT_INFO': return response(self.slot_info(state))
        if name in ('GUILD_GET_SKILLS', 'GUILD_UPGRADE_SKILL', 'GUILD_RESET_SKILL'):
            data=guild_lab.dispatch(state,name,request)
            packets=response(data)[0]
            if name!='GUILD_GET_SKILLS': packets.append((p.MIDS['ITEM_CHANGE'],'item_change_res',self.backpack(state)))
            return packets,None
        if name == 'GET_SUMMON_INFO': return response(self.summon_info(state))
        if name == 'GET_BACKPACK_INFO': return response(self.backpack(state), 'backpack_info_res')
        if name in ('PROPHET_REPLACE', 'PROPHET_REPLACE_SAVE', 'GAMBLE_GET_INFO', 'GAMBLE_REFRESH', 'GAMBLE_GET_AWARD', 'GET_SHOP_INFO', 'REFRESH_SHOP', 'BUY_SHOP_ITEM'):
            payload=acquisition.dispatch(state,name,request,now=self.now(),developer=self.developer)
            if name=='GAMBLE_GET_AWARD' and int((request or {}).get('gamble_type',1) or 1)==1: missions.record(state,'gamble',max(1,len((payload or {}).get('awards') or [])),self.now())
            packets=[(p.MIDS[name],p.message_type(p.MIDS[name],'res'),payload)]
            if name in ('PROPHET_REPLACE','PROPHET_REPLACE_SAVE','GAMBLE_GET_AWARD','GAMBLE_REFRESH','REFRESH_SHOP','BUY_SHOP_ITEM'):
                packets.append((p.MIDS['ITEM_CHANGE'],'item_change_res',self.backpack(state)))
            if name=='PROPHET_REPLACE_SAVE':
                packets.append((p.MIDS['GET_SLOT_INFO'],'get_slot_info_res',self.slot_info(state)))
            return packets,None
        if name == 'SUMMON':
            summon_id = integer(request.get('summon_id'), 'summon_id', 1)
            fragment_summon = summon_id in {int(item['summon_id']) for item in DEBRIS.values() if item.get('summon_id') and str(item['summon_id']) in TABLES['summon']}
            prophet = summon_id in PROPHET_SUMMONS
            if summon_id not in (1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 16) + wish.SUMMONS and not prophet and not fragment_summon: raise GameError('Tipo de invocación no disponible')
            if summon_id in wish.SUMMONS and not wish.data(state)['select']: raise GameError('Please choose your Wish Girl')
            config = TABLES['summon'][str(summon_id)]
            times = integer(request.get('times', 1), 'times', 1, 10)
            if times not in (1, 10): raise GameError('Cantidad de invocaciones inválida')
            if not fragment_summon and times != 1: raise GameError('Esta invocación usa un botón de cantidad propio')
            count = int(config['summon_num']) * (times if fragment_summon else 1)
            now = self.now()
            if summon_id == wish.FREE:
                w = wish.data(state)
                if now < int(w['free_at']): raise GameError('La invocación gratuita aún no está disponible')
                w['free_at'] = now + int(config['freetime_interval'])
            elif summon_id in (3, 8):
                free_key = 'summon_free_at' if summon_id == 3 else 'senior_summon_free_at'
                if now < state.get(free_key, 0): raise GameError('La invocación gratuita aún no está disponible')
                state[free_key] = now + int(config['freetime_interval'])
            else:
                cost = item_pairs(config['cost'])
                if fragment_summon:
                    cost = {key: value * times for key, value in cost.items()}
                for key, amount in cost.items():
                    if state['items'].get(str(key), 0) < amount:
                        raise GameError('No hay suficientes recursos para esta invocación')
                for key, amount in cost.items(): state['items'][str(key)] -= amount
            if str(config.get('is_partner')) == '0':
                # Item summons (Enroll): dropbox rows are shards/items, `id#n` or `id#min#max`.
                rows = [r for r in TABLES['dropbox'].values() if r['dropbox_id'] == int(config['dropbox_id']) and int(r['weight']) > 0]
                total = sum(int(r['weight']) for r in rows)
                items = {}
                for _ in range(count):
                    draw = secrets.randbelow(total)
                    for row in rows:
                        draw -= int(row['weight'])
                        if draw < 0: break
                    parts = str(row['item']).split('#'); low = int(parts[1]); high = int(parts[2]) if len(parts) > 2 else low
                    n = low + (secrets.randbelow(high - low + 1) if high > low else 0)
                    items[parts[0]] = items.get(parts[0], 0) + n
                for k, n in items.items(): state['items'][k] = int(state['items'].get(k, 0)) + n
                bonus = str(config.get('award') or '').split('#')
                if len(bonus) >= 2 and bonus[0] not in ('0', ''):
                    low = int(bonus[1]); high = int(bonus[2]) if len(bonus) > 2 else low
                    extra = low + (secrets.randbelow(high - low + 1) if high > low else 0)
                    state['items'][bonus[0]] = int(state['items'].get(bonus[0], 0)) + extra; items[bonus[0]] = items.get(bonus[0], 0) + extra
                data = {'summon_id': summon_id, 'summon_result': {'items': [{'item_id': int(k), 'item_num': n} for k, n in items.items()]}, 'summon_info': self.summon_info(state)}
                return [(p.MIDS[name], 'summon_res', data), (p.MIDS['ITEM_CHANGE'], 'item_change_res', self.backpack(state))], None
            rows, total = self.summon_pool(int(config['dropbox_id']), state.get('server_id', 'S1'))
            if summon_id == 9 and any(int(TABLES['partner'][str(row['item']).split('#')[0]]['max_star']) != 5 for row in rows):
                raise GameError('El huevo requiere una tabla de premios de cinco estrellas')
            new = []
            next_id = state.get('next_partner_id', max(v['partner_id'] for v in state['partners'])+1)
            for _ in range(count):
                draw = secrets.randbelow(total)
                for row in rows:
                    draw -= int(row.get('_local_weight', row['weight']))
                    if draw < 0: break
                table_id = int(str(row['item']).split('#')[0])
                if summon_id in wish.SUMMONS: table_id = wish.roll(state, table_id)
                partner = {'partner_id': next_id, 'table_id': table_id, 'lv': 1, 'grade': 0,
                           'awake': max(0, int(config.get('awaken_lv') or 0)), 'equips': [], 'pos': 0, 'show_skin': 1}
                next_id += 1
                new.append(partner)
                state['partners'].append(partner)
            state['next_partner_id'] = next_id
            # Original summon.award grants BAODI_ENERGY (12), distinct from FRIEND_LOVE (11).
            for key, amount in item_pairs(config.get('award')).items():
                if key and amount: state['items'][str(key)] = int(state['items'].get(str(key), 0)) + amount
            data = {'summon_id': summon_id, 'summon_result': {'partners': new}, 'summon_info': self.summon_info(state)}
            return [(p.MIDS[name], 'summon_res', data),
                    (p.MIDS['ITEM_CHANGE'], 'item_change_res', self.backpack(state)),
                    (p.MIDS['GET_SLOT_INFO'], 'get_slot_info_res', self.slot_info(state))], None
        if name == 'SET_HANG_TEAM':
            state['formation'] = self.validate_formation(state, request.get('partners'))
            return response({'hang_team': state['formation']})
        if name == 'STAGE_HANG':
            stage = integer(request.get('stage_id'), 'stage_id', 1)
            if str(stage) not in TABLES['stage'] or stage > max(1, state['max_stage']):
                raise GameError('Primero debes superar esa fase')
            campaign.change_stage(state,stage,now=self.now())
            data = self.map_info(state)
            return response(p.normalize('stage_hang_res', data, strict=False))
        if name == 'LOCK_PARTNER':
            pid=integer(request.get('partner_id'),'partner_id',1)
            locked=integer(request.get('is_lock'),'is_lock',0,1)
            partner=next((p for p in state['partners'] if p['partner_id']==pid),None)
            if not partner:raise GameError('Chica inexistente')
            flags=(list(partner.get('flags') or [])+[0]*12)[:12]
            flags[0]=locked;partner['flags']=flags
            return response({'partner_info':partner})
        if name == 'PARTNER_LEVUP':
            pid = integer(request.get('partner_id'), 'partner_id', 1)
            increment = integer(request.get('incr_lv'), 'incr_lv', 1, 10)
            partner = next((x for x in state['partners'] if x['partner_id'] == pid), None)
            if not partner: raise GameError('Integrante inexistente')
            end = partner['lv'] + increment
            if end > self.level_cap(partner): raise GameError('Se alcanzó el límite de nivel de este prototipo')
            costs = {}
            for level in range(partner['lv']+1, end+1):
                for key, value in item_pairs(TABLES['exp_partner'][str(level)]['cost']).items():
                    costs[key] = costs.get(key, 0) + local_config.scale_cost(value)
            for key, value in costs.items():
                if state['items'].get(str(key), 0) < value: raise GameError('No hay suficientes recursos')
            for key, value in costs.items(): state['items'][str(key)] -= value
            partner['lv'] = end
            return [(p.MIDS[name], 'partner_levup_res', {'partner_info': partner}),
                    (p.MIDS['ITEM_CHANGE'], 'item_change_res', self.backpack(state))], None
        if name == 'COMPOSE_PARTNER':
            pending=(state.get('exchange') or {}).get('partner_id')
            if pending and (request.get('partner_id')==pending or (isinstance(request.get('material_ids'),list) and pending in request['material_ids'])):
                raise GameError('Resuelve primero el intercambio pendiente')
            target = integer(request.get('table_id'), 'table_id', 1)
            recipe = GRADUATE.get(str(target)) or ASCENSION.get(f'{target}:6')
            if not recipe: raise GameError('Esta receta de Graduate no está disponible')
            ids = request.get('material_ids')
            required = list(recipe['material'])
            if not isinstance(ids, list) or len(ids) != len(required)+1 or any(type(i) is not int for i in ids) or len(set(ids)) != len(ids):
                raise GameError('La receta requiere una base y materiales distintos')
            owned = {girl['partner_id']: girl for girl in state['partners']}
            if any(pid not in owned for pid in ids): raise GameError('Falta una chica de la receta')
            host = owned[ids[0]]
            if host['table_id'] != recipe['source'] or host.get('awake', 0): raise GameError('La chica base no coincide con la receta')
            used = self.match_materials(owned, ids[1:], required, int(recipe['group']))
            if len(used) != len(required): raise GameError('Materiales de Graduate inválidos')
            host['table_id'] = target
            for girl in state['partners']:
                if girl['partner_id'] in used: equipment.release(state, girl)
            state['partners'] = [girl for girl in state['partners'] if girl['partner_id'] not in used]
            state['formation'] = [slot for slot in state['formation'] if slot['partner_id'] not in used]
            return [(p.MIDS[name], 'compose_partner_res', {'partner_info': host, 'material_ids': ids}),
                    (p.MIDS['GET_SLOT_INFO'], 'get_slot_info_res', self.slot_info(state))], None
        if name == 'UPGRADE_PARTNER_EX_SKILL':
            # ExSkillGradeUpWindow: 10★ girls with partner.ex_skill == 1 own 4 unique skills, Lv 0–5 each.
            pid = integer(request.get('partner_id'), 'partner_id', 1)
            index = integer(request.get('index'), 'index', 1, 4)
            host = next((g for g in state['partners'] if g['partner_id'] == pid), None)
            if not host: raise GameError('No tienes esa chica')
            row = TABLES['partner'][str(host['table_id'])]
            if int(row['max_star']) != 10 or str(row.get('ex_skill')) != '1': raise GameError('Esta chica no tiene habilidades únicas')
            skills = (list(host.get('ex_skills') or []) + [0, 0, 0, 0])[:4]
            # Cosmic girls (group 7): SkillResonateWindow, each skill 1→10 (stored 0-9) with skill_resonate_cost
            cosmic = int(row['group']) == 7
            top, costs = (RESONATE['max'], RESONATE['cost']) if cosmic else (EXSKILL['max'], EXSKILL['cost'])
            if skills[index-1] >= top: raise GameError('Habilidad al máximo')
            cost = item_pairs(costs[str(skills[index-1] + 1)])
            if any(int(state['items'].get(str(k), 0)) < n for k, n in cost.items()): raise GameError('Faltan materiales')
            for k, n in cost.items(): state['items'][str(k)] = int(state['items'].get(str(k), 0)) - n
            skills[index-1] += 1; host['ex_skills'] = skills
            growth_diary.record(state,'growth_elite_skill')
            return response({'partner_info': host})
        if name == 'CHOOSE_PARTNER_POTENTIAL':
            # PotentialityChooseWindow: Limit-Break stage i (11★+i-1) opens slot i; Partner.potentials[i] = 1..3 picks one of
            # the three skills of partner.potential (ReportHero:getSkillIDs adds it in battle). Changing it later is free.
            pid = integer(request.get('partner_id'), 'partner_id', 1)
            stage = integer(request.get('awake_index'), 'awake_index', 1, 5)
            index = integer(request.get('index'), 'index', 1, 3)
            host = next((g for g in state['partners'] if g['partner_id'] == pid), None)
            if not host: raise GameError('No tienes esa chica')
            row = TABLES['partner'][str(host['table_id'])]
            if int(row['max_star']) != 10 or int(host.get('awake', 0)) < stage: raise GameError(f'Se desbloquea en Limit-Break {stage}')
            options = [s for s in str(row.get('potential') or '').split('|')]
            if stage > len(options) or index > len([x for x in options[stage-1].split('#') if x]): raise GameError('Potencial inexistente')
            pots = (list(host.get('potentials') or []) + [0] * 5)[:5]
            pots[stage-1] = index; host['potentials'] = pots
            return response({'partner_info': host})
        if name in ('UPGRADE_STAR_ORIGIN', 'RESET_STAR_ORIGIN'):
            # StarOriginDetailWindow: 15★ girls with partner.star_origin > 0; node k (1-10) at level v = star_origin row
            # start_k + v (HeroAttr:getStarOrigin adds its cumulative effect); node k opens when limits[k] = "pre#lv" is met.
            pid = integer(request.get('partner_id'), 'partner_id', 1)
            host = next((g for g in state['partners'] if g['partner_id'] == pid), None)
            if not host: raise GameError('No tienes esa chica')
            row = TABLES['partner'][str(host['table_id'])]; lst = ASTRAL['lists'].get(str(row.get('star_origin') or 0))
            if not lst or int(row['max_star']) + int(host.get('awake', 0)) < 15: raise GameError('Astral Core se abre a 15★')
            levs = (list(host.get('star_origin') or []) + [0] * 10)[:10]
            if name == 'RESET_STAR_ORIGIN':
                cost = item_pairs(ASTRAL['reset_cost'])
                if any(int(state['items'].get(str(k), 0)) < n for k, n in cost.items()): raise GameError('Faltan gemas para reiniciar')
                for k, n in cost.items(): state['items'][str(k)] = int(state['items'].get(str(k), 0)) - n
                back = {}
                for k, v in enumerate(levs):
                    for lv in range(1, v + 1):
                        for i, n in item_pairs(ASTRAL['levels'][str(lst['start'][k] + lv)]['cost']).items(): back[str(i)] = back.get(str(i), 0) + n
                for i, n in back.items(): state['items'][i] = int(state['items'].get(i, 0)) + n
                host['star_origin'] = [0] * 10
                return response({'partner_info': host, 'items': [{'item_id': int(i), 'item_num': n} for i, n in back.items()]})
            node = integer(request.get('node'), 'node', 1, 10); times = integer(request.get('times', 1), 'times', 1, 60)
            pre, need = lst['limits'][node - 1]
            if pre > 0 and levs[pre - 1] < need: raise GameError(f'Sube el nodo {pre} a nivel {need}')
            top = lst['end'][node - 1] - lst['start'][node - 1]
            done = 0
            for _ in range(times):
                if levs[node - 1] >= top: break
                cost = item_pairs(ASTRAL['levels'][str(lst['start'][node - 1] + levs[node - 1] + 1)]['cost'])
                if any(int(state['items'].get(str(k), 0)) < n for k, n in cost.items()): break
                for k, n in cost.items(): state['items'][str(k)] = int(state['items'].get(str(k), 0)) - n
                levs[node - 1] += 1; done += 1
            if not done: raise GameError('Nodo al máximo' if levs[node - 1] >= top else 'Faltan materiales')
            host['star_origin'] = levs
            growth_diary.record(state,'growth_astral',done)
            return response({'partner_info': host})
        if name == 'REPLACE_10_STAR':
            # TenStarExchangeWindow: a 10★+ girl becomes the 10★ form (partner.star_10) of a 5★ girl of her house, paying
            # 5 Diplomas and replace_10_cost_hero[stage] identical copies of that 5★ girl; level, grade, gear, crystal,
            # antique, Limit-Break and potentials stay; the highest Intimacy among the consumed copies is kept.
            pid = integer(request.get('partner_id'), 'partner_id', 1)
            ids = request.get('material_ids')
            host = next((g for g in state['partners'] if g['partner_id'] == pid), None)
            if not host: raise GameError('No tienes esa chica')
            row = TABLES['partner'][str(host['table_id'])]
            stars = int(row['max_star']) + int(host.get('awake', 0))
            if int(row['max_star']) != 10 or int(row['group']) == 7: raise GameError('Solo chicas de 10★ o más (no cósmicas)')
            if not isinstance(ids, list) or not ids: raise GameError('Elige las copias de 5★')
            owned = {g['partner_id']: g for g in state['partners']}
            mats = [owned.get(integer(x, 'material', 1)) for x in ids]
            if any(m is None or m['partner_id'] == pid for m in mats) or len({m['partner_id'] for m in mats}) != len(mats): raise GameError('Materiales inválidos')
            tid = mats[0]['table_id']; mrow = TABLES['partner'][str(tid)]
            target = int(mrow.get('star_10') or 0)
            if any(m['table_id'] != tid or int(m.get('awake', 0)) for m in mats) or int(mrow['max_star']) != 5 or int(mrow['group']) != int(row['group']) or not target:
                raise GameError('Hacen falta copias idénticas de una chica de 5★ de la misma casa')
            if target == host['table_id']: raise GameError('No puedes intercambiarla por sí misma')
            need = RETURN['replace_cost_hero'][min(len(RETURN['replace_cost_hero']), stars - 9) - 1]
            if len(mats) != need: raise GameError(f'Necesitas {need} copias')
            cost = item_pairs(RETURN['replace_cost'])
            if any(int(state['items'].get(str(k), 0)) < n for k, n in cost.items()): raise GameError('Faltan Diplomas')
            for k, n in cost.items(): state['items'][str(k)] = int(state['items'].get(str(k), 0)) - n
            used = {m['partner_id'] for m in mats}
            for m in mats: equipment.release(state, m)
            host['love_point'] = max(int(m.get('love_point', 0)) for m in mats)
            skin = (host.get('equips') or [0] * 7)[6:7]
            if skin and skin[0]: equipment.add(state, skin[0], 1); host['equips'][6] = 0
            host['table_id'] = target; host['potentials'] = host.get('potentials') or []
            state['partners'] = [g for g in state['partners'] if g['partner_id'] not in used]
            state['formation'] = [x for x in state['formation'] if x['partner_id'] not in used]
            return response({'partner_id': pid, 'replace_table_id': target, 'material_ids': sorted(used), 'love_point': host['love_point'], 'is_vowed': int(host.get('is_vowed', 0)), 'wedding_date': int(host.get('wedding_date', 0))})
        if name == 'DECOMPOSE_PARTNERS':
            ids = request.get('partner_ids')
            got, six = self.altar_returns(state, ids)
            day = clock.day(self.now()); alt = state.setdefault('altar', {})
            if alt.get('day') != day: alt.update(day=day, six=0)
            if six and alt['six'] + six > 5: raise GameError('Solo puedes retirar 5 chicas de 6★ o más al día')
            alt['six'] += six
            owned = {g['partner_id']: g for g in state['partners']}
            for pid in ids: equipment.release(state, owned[pid])
            state['partners'] = [g for g in state['partners'] if g['partner_id'] not in ids]
            state['formation'] = [x for x in state['formation'] if x['partner_id'] not in ids]
            state['campaign_hang'] = [x for x in state.get('campaign_hang') or [] if x['partner_id'] not in ids]
            for k, n in got.items(): state['items'][k] = int(state['items'].get(k, 0)) + n
            growth_diary.record(state, 'growth_transfer', len(ids))
            state['last_decompose'] = got
            return response({'items': [{'item_id': int(k), 'item_num': n} for k, n in sorted(got.items(), key=lambda x: int(x[0]))], 'partner_ids': ids})
        if name == 'ROLLBACK_PARTNER':
            # PotentialityBackWindow / partner_return_rule2: the girl is removed and returns house dolls ("table#num@awake"),
            # award_self namesake 5★ copies (partner.material[1]), her gear, and part of the EXP juice / lunch boxes.
            pid = integer(request.get('partner_id'), 'partner_id', 1)
            host = next((g for g in state['partners'] if g['partner_id'] == pid), None)
            if not host: raise GameError('No tienes esa chica')
            if any(host.get('flags') or []): raise GameError('Desbloquea primero a la chica')
            row = TABLES['partner'][str(host['table_id'])]
            stars = int(row['max_star']) + int(host.get('awake', 0)); rule = RETURN['rules'].get(str(stars))
            if not rule or int(row['group']) == 7 or int(host['table_id']) in RETURN['puppets']: raise GameError('Esta chica no se puede revertir')
            cost = item_pairs(rule.get('cost') or '')
            if any(int(state['items'].get(str(k), 0)) < n for k, n in cost.items()): raise GameError('Faltan recursos para revertir')
            for k, n in cost.items(): state['items'][str(k)] = int(state['items'].get(str(k), 0)) - n
            back = []
            def give(tid, awake=0):
                nid = state['next_partner_id']; state['next_partner_id'] += 1
                state['partners'].append({'partner_id': nid, 'table_id': int(tid), 'lv': 1, 'grade': 0, 'awake': int(awake), 'equips': [], 'pos': 0, 'show_skin': 1})
                back.append(nid)
            for part in str(rule.get('group_' + str(row['group'])) or '').split('|'):
                if '#' not in part or part.startswith('0'): continue
                tid, rest = part.split('#'); num, _, awake = rest.partition('@')
                for _ in range(int(num)): give(tid, int(awake or 0))
            namesake = int(str(row.get('material') or '').split('|')[0] or 0) if int(row['max_star']) > 5 else int(host['table_id'])
            for _ in range(int(rule.get('award_self') or 0)): give(namesake or host['table_id'])
            if back: next(g for g in state['partners'] if g['partner_id'] == back[-1])['love_point'] = int(host.get('love_point', 0))
            exp = int(str(TABLES['exp_partner'][str(host['lv'])]['all_exp']).split('#')[1]); ratio = float(rule.get('exp') or 0)
            gained = {}
            if exp and ratio: gained['9'] = math.ceil(exp * ratio)
            for k, n in item_pairs(rule.get('bento_num') or '').items(): gained[str(k)] = gained.get(str(k), 0) + n
            for k, n in gained.items(): state['items'][k] = int(state['items'].get(k, 0)) + n
            equipment.release(state, host)
            state['partners'] = [g for g in state['partners'] if g['partner_id'] != pid]
            state['formation'] = [x for x in state['formation'] if x['partner_id'] != pid]
            # returned girls / items travel in the state snapshot (the wire rollback_partner_res only needs the id here)
            state['last_rollback'] = {'partner_ids': back, 'items': gained}
            return response({'partner_id': pid})
        if name == 'PARTNER_GRADEUP':
            pid = integer(request.get('partner_id'), 'partner_id', 1)
            host = next((g for g in state['partners'] if g['partner_id'] == pid), None)
            if not host: raise GameError('No tienes esa chica')
            row = TABLES['partner'][str(host['table_id'])]
            grade = int(host.get('grade', 0))
            if grade >= int(row.get('max_grade') or 0): raise GameError('Grado máximo alcanzado')
            if host['lv'] < self.level_cap(host): raise GameError('Sube primero al nivel máximo de este grado')
            cost = {k: local_config.scale_cost(v) for k, v in item_pairs(row[f'grade_exp{grade+1}']).items()}
            if any(int(state['items'].get(str(k), 0)) < n for k, n in cost.items()): raise GameError('Faltan recursos para subir de grado')
            for k, n in cost.items(): state['items'][str(k)] = int(state['items'].get(str(k), 0)) - n
            host['grade'] = grade + 1
            return response({'partner_info': host})
        if name == 'AWAKE_PARTNER':
            pending=(state.get('exchange') or {}).get('partner_id')
            if pending and (request.get('partner_id')==pending or (isinstance(request.get('material_ids'),list) and pending in request['material_ids'])):
                raise GameError('Resuelve primero el intercambio pendiente')
            host_id = integer(request.get('partner_id'), 'partner_id', 1)
            owned = {girl['partner_id']: girl for girl in state['partners']}
            host = owned.get(host_id)
            if not host: raise GameError('No tienes esa chica')
            star = int(TABLES['partner'][str(host['table_id'])]['max_star']) + int(host.get('awake', 0))
            recipe = ASCENSION.get(f"{host['table_id']}:{star+1}") or local_promotion.recipe(host) or self.awake_recipe(host)
            if not recipe or recipe['kind'] != 'awake': raise GameError('Ascensión no disponible para esta chica')
            ids = request.get('material_ids')
            if not isinstance(ids, list) or len(ids) != len(recipe['material']) or any(type(i) is not int for i in ids) or len(set(ids)) != len(ids) or host_id in ids:
                raise GameError('Los materiales deben ser chicas distintas de la base')
            if any(pid not in owned for pid in ids): raise GameError('Falta una chica de la receta')
            if recipe.get('local'):
                copies=[pid for pid in ids if owned[pid]['table_id']==host['table_id'] and not int(owned[pid].get('awake',0))]
                if not copies:raise GameError('Necesitas una copia con sus estrellas iniciales')
                ids=[copies[0]]+[pid for pid in ids if pid!=copies[0]]
            used = self.match_materials(owned, ids, recipe['material'], int(recipe['group']))
            scaled_awake_cost = {str(key): local_config.scale_cost(amount) for key, amount in recipe.get('cost', {}).items()}
            for key, amount in scaled_awake_cost.items():
                if int(state['items'].get(key, 0)) < amount: raise GameError('Không đủ tài nguyên để Thức Tỉnh')
            for key, amount in scaled_awake_cost.items(): state['items'][key] -= amount
            if recipe.get('local'):
                host['awake'] = int(host.get('awake',0))+1
            elif star+1 == 10:
                host['table_id'] = int(recipe['target'])
                host['awake'] = 0
            else:
                host['awake'] = int(host.get('awake', 0))+1
            for girl in state['partners']:
                if girl['partner_id'] in used: equipment.release(state, girl)
            state['partners'] = [girl for girl in state['partners'] if girl['partner_id'] not in used]
            state['formation'] = [slot for slot in state['formation'] if slot['partner_id'] not in used]
            return [(p.MIDS[name], 'awake_partner_res', {'partner_info': host, 'material_ids': ids}),
                    (p.MIDS['GET_SLOT_INFO'], 'get_slot_info_res', self.slot_info(state))], None
        if name == 'MAP_FIGHT':
            stage_id = integer(request.get('stage_id'), 'stage_id', 1)
            if request.get('map_type') != 1 or request.get('pet_id', 0) or request.get('formation_id', 0):
                raise GameError('Solo mapa principal sin mascota ni formación especial')
            stage = TABLES['stage'].get(str(stage_id))
            if not stage or stage_id > self.next_stage(state): raise GameError('Fase bloqueada')
            if player_level(state) < int(stage['lv']): raise GameError('El nivel del jugador es insuficiente para esa fase')
            formation = self.validate_formation(state, request.get('partners', state['formation']))
            owned = {x['partner_id']: x for x in state['partners']}
            team_a = [{**copy.deepcopy(owned[x['partner_id']]), 'pos': x['pos']} for x in formation]
            battle = TABLES['battle'][str(stage['battle_id'])]
            monster_ids = str(battle['monsters']).split('|'); positions = str(battle['stands']).split('|')
            if len(monster_ids) != len(positions): raise GameError('Tabla de batalla inconsistente')
            team_b = [{'table_id': int(tid), 'pos': int(pos), 'isMonster': True} for tid, pos in zip(monster_ids, positions)]
            seed = (12345 + state['battle_count'] * 7919) % 233280
            report = self._simulate(state, team_a, team_b, stage['battle_id'], seed, self.battle_pet(state), guild_skills_a=guild_lab.skills(state))
            state['battle_count'] += 1
            awarded = {}
            if report['isWin'] and not state['max_stage']:
                state['hang'] = {'since': self.now(), 'drop_since': self.now()}
            if report['isWin'] and stage_id not in state['cleared']:
                awarded = {k: local_config.scale_reward(v) for k, v in item_pairs(stage['reward']).items()}
                for key, count in awarded.items(): state['items'][str(key)] = state['items'].get(str(key), 0)+count
                state['cleared'].append(stage_id)
                campaign.change_stage(state,stage_id,now=self.now())
                state['max_stage'] = max(stage_id, state['max_stage'])
            state['formation'] = formation
            state['last_battle'] = {'id': state['battle_count'], 'stage': stage_id, 'win': bool(report['isWin']),
                                    'frames': len(report['frames']), 'rewards': awarded, 'seed': seed,
                                    'hurts': report.get('hurts', []), 'hp': report.get('hp', []), 'rounds': report.get('total_round')}
            # The wire schema omits client-only diagnostic fields in the Lua report.
            data = {'battle_report': p.normalize('battle_data', report, strict=False), 'is_win': report['isWin'], 'map_type': 1, 'stage_id': stage_id}
            return [(p.MIDS[name], 'map_fight_res', data), (p.MIDS['ITEM_CHANGE'], 'item_change_res', self.backpack(state)),
                    (p.MIDS['GET_MAP_INFO'], 'get_map_info_res', self.map_info(state))], report
        raise GameError(f'{name}: mensaje aún no implementado')

    def get_battle(self, battle_id: int):
        with self.lock:
            row = self.db.execute('SELECT report,stage FROM battles WHERE id=?', (battle_id,)).fetchone()
        if row is None: raise GameError('Batalla inexistente')
        report = json.loads(row[0])
        report['map_asset'] = TABLES['stage'][str(row[1])]['set_map']
        units = []
        for side in ('teamA', 'teamB'):
            for unit in report[side]:
                tid = unit['table_id']
                if unit.get('isMonster'):
                    tid = int(TABLES['monster'][str(tid)]['partner_link'])
                units.append({'pos': unit['pos'] + (6 if side == 'teamB' else 0), 'table_id': tid,
                              'name': TABLES['names'].get(str(tid), f'Enemigo {tid}'), 'level': unit['level']})
        report['display_units'] = units
        return mark_bosses(report)
