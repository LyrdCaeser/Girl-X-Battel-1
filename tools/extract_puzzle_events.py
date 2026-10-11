"""Read-only extraction of Jigsaw 37 and Puppet Parade 189 client tables/art."""
import hashlib
import json
from pathlib import Path
import re
import shutil
from tools.extract_acquisition import read_table, SOURCE, CUT, ROOT


def main():
    tables = ('activity_jigsaw_pic', 'activity_jigsaw_buy', 'activity_jigsaw_award', 'activity_puppet_award')
    data = {name: read_table(name) for name in tables}
    misc = (SOURCE / 'lua/data/tables/misc.lua').read_text(encoding='utf-8-sig')
    def value(key):
        match = re.search(r'\b' + key + r' = \{\s*"' + key + r'",\s*"([^"]+)"', misc)
        if not match:
            raise ValueError(key)
        return match.group(1)
    data['misc'] = {key: value(key) for key in ('activity_jigsaw_buy_limit', 'activity_jigsaw_energy_init', 'activity_jigsaw_use_cost', 'activity_puppet_item')}
    out = ROOT / 'web/assets/puzzle-events'
    out.mkdir(parents=True, exist_ok=True)
    sources = [SOURCE / f'lua/data/tables/{name}.lua' for name in tables] + [SOURCE / 'lua/data/tables/misc.lua']
    missing = []
    for row in data['activity_jigsaw_pic'].values():
        for name in [row['avatar_png']] + [row['picture_png'] + '_' + str(i) for i in range(1, 10)]:
            path = CUT / (name + '.png')
            if path.exists():
                shutil.copyfile(path, out / path.name)
                sources.append(path)
            else:
                missing.append(name)
    for pattern in ('activity_jigsaw*.png', 'activity_puppet*.png'):
        for path in CUT.glob(pattern):
            shutil.copyfile(path, out / path.name)
            sources.append(path)
    for name in ('activity_jigsaw_bg', 'activity_puppet_bg'):
        path = SOURCE / f'unity/Assets/hotres/textures/scenes_web/{name}.png'
        if path.exists():
            shutil.copyfile(path, out / path.name)
            sources.append(path)
    data['missing_art'] = missing
    data['sources'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    (ROOT / 'data/puzzle_events.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print('Jigsaw:', len(data[tables[0]]), 'pictures; Puppet:', len(data[tables[3]]), 'tiers; missing art:', len(missing))


if __name__ == '__main__':
    main()
