from __future__ import annotations
import json
import os
import shutil
import sys
from pathlib import Path
import subprocess
import tempfile
from .local_promotion import combat_partner

ROOT = Path(__file__).resolve().parents[1]

# Online PvP/Guild War are hero-vs-hero fights. Keep the report's battle
# configuration ID stable and use random_seed only for combat randomness.
# 100001 is the original BattleCreateReport-compatible baseline used by the
# archived runtime host itself.
ONLINE_BATTLE_ID = 100001
ONLINE_SEED_MODULUS = 233280


def normalize_online_seed(value: int) -> int:
    """Map arbitrary IDs/hashes into the original runtime's safe seed range."""
    seed = int(value) % ONLINE_SEED_MODULUS
    return seed if seed > 0 else 1

def luajit_runtime() -> Path:
    """Choose the bundled desktop runtime, or an explicit/native override."""
    override = os.environ.get('GXB2_LUAJIT')
    if override:
        return Path(override)
    if sys.platform == 'win32':
        return ROOT / 'runtime/luajit-windows-x64.exe'
    if sys.platform == 'darwin':
        return ROOT / 'runtime/luajit-macos-x64'
    native = shutil.which('luajit')
    if native:
        return Path(native)
    raise RuntimeError('Falta LuaJIT compatible. Instálalo o configura GXB2_LUAJIT; consulta README.md.')

def lua_literal(value):
    if value is None: return 'nil'
    if value is True: return 'true'
    if value is False: return 'false'
    if isinstance(value, (int, float)): return repr(value)
    if isinstance(value, str):
        # Bytewise decimal escaping is independent of Lua source string syntax.
        return '"' + ''.join('\\%03d' % b for b in value.encode('utf-8')) + '"'
    if isinstance(value, list): return '{' + ','.join(lua_literal(v) for v in value) + '}'
    if isinstance(value, dict): return '{' + ','.join('[' + lua_literal(k) + ']=' + lua_literal(v) for k, v in value.items()) + '}'
    raise TypeError(type(value))

def attributes(partners: list, guild_skills: list | None = None, chime_bonus: list | None = None) -> dict:
    """Original HeroAttr:attr for each partner (level, grade, awake, equips, suits)."""
    runtime = luajit_runtime()
    with tempfile.TemporaryDirectory(prefix='gxb2-attr-') as temp:
        path = Path(temp) / 'input.lua'
        path.write_text('return ' + lua_literal({'partners':[combat_partner(p) for p in partners],'guildSkills':guild_skills or [],'chimeBonus':chime_bonus if chime_bonus is not None else []}))
        result = subprocess.run([str(runtime), str(ROOT / 'runtime/battle_host.lua'), str(ROOT / 'runtime/lua'), 'attrs', str(path)], capture_output=True, text=True, timeout=20)
    if result.returncode:
        raise RuntimeError('Cálculo de atributos falló: ' + result.stderr[-800:])
    return json.loads(result.stdout)

def simulate(team_a: list, team_b: list, battle_id: int, seed: int, pet_a: dict | None = None, battle_type: int = 1,
             guild_skills_a: list | None = None, guild_skills_b: list | None = None, pet_b: dict | None = None,
             god_skills: list | None = None, shrine_id: int | None = None, max_round: int | None = None,
             galaxy_info: dict | None = None, chime_bonus_a: list | None = None, chime_bonus_b: list | None = None) -> dict:
    runtime = luajit_runtime()
    if not runtime.exists():
        raise RuntimeError('Falta el intérprete LuaJIT compatible. Consulta LEEME.md.')
    request = dict(
        guildSkillsA=guild_skills_a or [], guildSkillsB=guild_skills_b or [],
        god_skills=[int(x) for x in (god_skills or [])],
        teamA=[combat_partner(p) for p in team_a], teamB=[combat_partner(p) for p in team_b],
        battle_id=battle_id, random_seed=seed, battle_type=battle_type,
        chimeBonusA=chime_bonus_a or [], chimeBonusB=chime_bonus_b or [],
    )
    if pet_a:
        request['petA'] = pet_a
    if pet_b:
        request['petB'] = pet_b
    if shrine_id:
        request['shrine_id'] = int(shrine_id)
    if max_round:
        request['max_round'] = int(max_round)
    if galaxy_info:
        request['galaxy_info'] = galaxy_info
    if chime_bonus_a:
        request['chimeBonusA'] = chime_bonus_a
    if chime_bonus_b:
        request['chimeBonusB'] = chime_bonus_b
    with tempfile.TemporaryDirectory(prefix='gxb2-battle-') as temp:
        path = Path(temp) / 'input.lua'
        path.write_text('return ' + lua_literal(request))
        result = subprocess.run([str(runtime), str(ROOT / 'runtime/battle_host.lua'), str(ROOT / 'runtime/lua'), 'battle', str(path)], capture_output=True, text=True, timeout=20)
    if result.returncode:
        raise RuntimeError('El motor de combate falló: ' + result.stderr[-1600:])
    report = json.loads(result.stdout)
    # Lua table parsing retains aura IDs as decimal strings. The original wire
    # descriptor represents these IDs as repeated int32 values.
    for field in ('groupBuffA', 'groupBuffB'):
        if isinstance(report.get(field), list):
            report[field] = [int(value) for value in report[field]]
    if not isinstance(report.get('frames'), list) or report.get('isWin') not in (0, 1):
        raise RuntimeError('Informe de combate incompleto')
    return report
