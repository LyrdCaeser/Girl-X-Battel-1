"""Extract profile UI, portraits and frames from the original Unity atlases."""
from pathlib import Path
import json
import re
from extract_navigation_assets import ATLAS, OUT, extract


def names(atlas, pattern=None):
    source = (ATLAS / atlas / f'{atlas}.prefab').read_text(errors='ignore')
    result = re.findall(r'- name: ([^\r\n]+)\s+x:', source)
    return {name for name in result if pattern is None or re.fullmatch(pattern, name)}


def main():
    dest = OUT / 'profile'
    ui = names('person_info_web')
    heads = names('head_web', r'head_\d+')
    frames = names('head_frame_web', r'frame_\d+') | names('head_frame2_web', r'frame_\d+')
    extract('person_info_web', ui, dest)
    extract('head_web', heads, dest)
    extract('head_frame_web', names('head_frame_web'), dest)
    extract('head_frame2_web', names('head_frame2_web'), dest)
    found = set()
    for atlas_dir in sorted(ATLAS.glob('partner_avatar_*_web')):
        if not atlas_dir.is_dir():
            continue
        available = names(atlas_dir.name, r'partner_avatar_\d+')
        if available:
            extract(atlas_dir.name, available, dest)
            found |= available
    catalog = {'heads': sorted(heads), 'frames': sorted(frames, key=lambda s: int(s.split('_')[1])),
               'partners': sorted(found), 'ui': sorted(ui)}
    (dest / 'catalog.json').write_text(json.dumps(catalog, indent=2) + '\n')


if __name__ == '__main__':
    main()
