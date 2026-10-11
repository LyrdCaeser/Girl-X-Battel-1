"""Extract Daily Quiz tables and artwork from the user's original client export."""
from pathlib import Path
import json
import re
import shutil
from extract_navigation_assets import ATLAS, ROOT, extract

LUA_TABLES = Path('/Users/schroyle/Downloads/Decomp files/lua/data/tables')


def rows(table, fields):
    source = (LUA_TABLES / f'{table}.lua').read_text(errors='ignore')
    entries = re.findall(r'\["(\d+)"\] = \{(.*?)\n\s*\}', source, re.S)
    result = {}
    for row_id, body in entries:
        values = [quoted if quoted != '' else numeric for quoted, numeric in re.findall(r'"([^"]*)"|(-?\d+)', body)]
        if len(values) != len(fields):
            raise ValueError(f'{table} row {row_id}: expected {len(fields)} values, got {len(values)}')
        result[row_id] = {field: int(value) if value.lstrip('-').isdigit() else value for field, value in zip(fields, values)}
    return result


def main():
    data = {'quizzes': rows('quiz', ['id', 'type', 'level', 'random_stages', 'show_awards', 'power', 'difficulty']),
            'stages': rows('quiz_stage', ['id', 'map', 'battle_id', 'awards'])}
    if len(data['quizzes']) != 24 or len(data['stages']) != 64:
        raise ValueError('Daily Quiz table count changed')
    (ROOT / 'data/daily_quiz.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    atlas = 'daily_quiz_web'
    source = (ATLAS / atlas / f'{atlas}.prefab').read_text(errors='ignore')
    available = set(re.findall(r'- name: ([^\r\n]+)\s+x:', source))
    extract(atlas, available, ROOT / 'web/assets/daily-quiz')
    battles = json.loads((ROOT / 'data/battle.json').read_text())
    maps = {battles[str(stage['battle_id'])]['map'] for stage in data['stages'].values()}
    map_dir = ROOT / 'web/assets/battle-maps'
    source_maps = ATLAS.parent / 'textures/battle_map_web'
    for name in maps:
        shutil.copyfile(source_maps / f'{name}.png', map_dir / f'{name}.png')
    catalog_file = ROOT / 'web/assets/battle-maps.json'
    catalog_file.write_text(json.dumps(sorted(set(json.loads(catalog_file.read_text())) | maps), indent=2) + '\n')


if __name__ == '__main__':
    main()
