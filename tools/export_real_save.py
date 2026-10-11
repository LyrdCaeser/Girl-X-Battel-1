"""Export recoverable, non-account data from the user's Android/data copy.

This script only reads the original files. It never exports meta, chat, session
values, account IDs, or raw partner instance IDs.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID = Path('/Users/schroyle/Downloads/com.carolgames.moemoegirls/files')
DECOMP = Path('/Users/schroyle/Downloads/Decomp files')
OUT = ROOT / 'real_save_export'


def connect_readonly(path: Path):
    return sqlite3.connect(f'file:{path}?mode=ro&immutable=1', uri=True)


def write_json(name: str, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def write_csv(name: str, fields, rows):
    with (OUT / name).open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def formation_export(game):
    modes = {}
    source = (DECOMP / 'lua/app/common/enums.lua').read_text(errors='ignore')
    block = source.split('xyd.BattleType = {', 1)[1].split('\n}', 1)[0]
    for name, number in re.findall(r'\b([A-Z][A-Za-z0-9_]*)\s*=\s*(\d+)', block):
        modes[int(number)] = name

    aliases = {'hero': {}, 'pet': {}}

    def alias(kind, raw):
        if not isinstance(raw, int) or raw <= 0:
            return None
        bucket = aliases[kind]
        if raw not in bucket:
            bucket[raw] = f'{"H" if kind == "hero" else "P"}{len(bucket)+1:03d}'
        return bucket[raw]

    rows = []
    for key, value in game.execute('select key,value from formation order by key'):
        mode_key = key.split(':', 1)[0]  # omit the account identifier suffix
        base = mode_key.split('_', 1)[0]
        try:
            mode_number = int(base)
        except ValueError:
            mode_number = None
        data = json.loads(value)
        partners = data.get('partners')
        if isinstance(partners, list):
            slots = {str(i): alias('hero', raw) for i, raw in enumerate(partners, 1)}
        elif isinstance(partners, dict):
            slots = {str(k): alias('hero', raw) for k, raw in sorted(partners.items(), key=lambda x: int(x[0]))}
        else:
            slots = {}
        pet_ids = data.get('pet_ids')
        rows.append({
            'mode': mode_key,
            'battle_type': modes.get(mode_number, 'UNKNOWN'),
            'slots': slots,
            'pet': alias('pet', data.get('pet_id')),
            'pets': [alias('pet', x) for x in pet_ids] if isinstance(pet_ids, list) else [],
        })
    write_json('formations_anonymized.json', {
        'note': 'H/P aliases preserve repeated units across saved formations; original account and instance IDs are omitted. These are presets, not a complete roster.',
        'formation_count': len(rows),
        'distinct_hero_aliases': len(aliases['hero']),
        'distinct_pet_aliases': len(aliases['pet']),
        'formations': rows,
    })
    return len(rows), len(aliases['hero']), len(aliases['pet'])


def outfit_export(game, tables):
    value = game.execute("select value from misc where key='local_sava_chose_style_by_dress_id'").fetchone()
    selected = json.loads(value[0]) if value else {}
    result = []
    for dress_id, style_id in sorted(selected.items()):
        row = tables.execute('select id,name,dress_id,image,resource from senpai_dress_style where id=?', (str(style_id),)).fetchone()
        if not row:
            result.append({'dress_slot_id': dress_id, 'style_id': style_id, 'asset_name': None})
            continue
        asset = row[1]
        files = sorted((ANDROID / 'Bundles/Android/spine').rglob(asset + '.bytes'))
        result.append({
            'dress_slot_id': dress_id,
            'style_id': style_id,
            'asset_name': asset,
            'bundle_path': files[0].relative_to(ANDROID / 'Bundles/Android').as_posix() if files else None,
            'bundle_present': bool(files),
        })
    write_json('outfit_styles.json', {
        'note': 'Local style selections only; they do not prove ownership of outfits or skins.',
        'selected_styles': result,
    })
    return len(result)


def bundle_export():
    base = ANDROID / 'Bundles/Android'
    rows = []
    for path in sorted(base.rglob('*.bytes')):
        relative = path.relative_to(base)
        if relative.parts[0] == 'src':
            continue
        rows.append({'bundle_path': relative.as_posix(), 'asset_name': path.stem, 'category': relative.parts[0], 'bytes': path.stat().st_size})
    write_csv('bundle_assets.csv', ['bundle_path', 'asset_name', 'category', 'bytes'], rows)
    return len(rows)


def webview_export():
    base = ANDROID / 'Download/webview/cache/resource'
    records = {}
    for manifest in sorted(base.glob('*/*.res.json')):
        if manifest.name not in {'default.res.json', 'partners.res.json', 'tables.res.json'}:
            continue
        try:
            data = json.loads(manifest.read_text(errors='replace'))
        except (OSError, ValueError):
            continue
        for item in data.get('resources', []):
            name, url = item.get('name'), item.get('url')
            if not isinstance(name, str) or not isinstance(url, str) or '://' in url or '..' in Path(url).parts:
                continue
            records[(name, url)] = {
                'name': name,
                'type': item.get('type', ''),
                'relative_url': url,
                'cached': (base / url).is_file(),
            }
    rows = sorted(records.values(), key=lambda r: (r['name'], r['relative_url']))
    write_csv('webview_resources.csv', ['name', 'type', 'relative_url', 'cached'], rows)
    files = [
        {'relative_path': path.relative_to(base).as_posix(), 'bytes': path.stat().st_size}
        for path in sorted(base.rglob('*'))
        if path.is_file() and path.suffix in {'.png', '.json', '.dbbin', '.mp3'}
    ]
    write_csv('webview_cached_files.csv', ['relative_path', 'bytes'], files)
    return len(rows), sum(row['cached'] for row in rows), len(files)


def extra_textures(extract_images: bool):
    real = ANDROID / 'Bundles/Android/textures'
    decomp = DECOMP / 'unity/Assets/hotres/textures'
    known = {p.stem.lower() for p in decomp.rglob('*.png')}
    extras = sorted(p for p in real.rglob('*.bytes') if p.stem.lower() not in known)
    rows = []
    if extract_images:
        try:
            import UnityPy
        except ImportError as exc:
            raise RuntimeError('UnityPy is required only for --extract-textures') from exc
        (OUT / 'extra_textures').mkdir(exist_ok=True)
    for path in extras:
        name = path.stem
        relative = path.relative_to(ANDROID / 'Bundles/Android').as_posix()
        extracted = []
        if extract_images:
            try:
                for obj in UnityPy.load(str(path)).objects:
                    if obj.type.name != 'Texture2D':
                        continue
                    image = obj.read().image
                    target = OUT / 'extra_textures' / (name + '.png')
                    image.save(target, optimize=True)
                    extracted.append(target.name)
            except Exception:
                extracted.append('conversion_failed')
        rows.append({'bundle_path': relative, 'asset_name': name, 'extracted_images': extracted})
    write_json('additional_texture_names.json', rows)
    return len(rows), sum(bool(r['extracted_images']) and r['extracted_images'][0] != 'conversion_failed' for r in rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--extract-textures', action='store_true', help='Decode additional UnityFS textures (requires UnityPy)')
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    game = connect_readonly(ANDROID / 'Databases/game.db')
    tables = connect_readonly(DECOMP / 'data/data.db')
    formations = formation_export(game)
    outfits = outfit_export(game, tables)
    bundles = bundle_export()
    webview = webview_export()
    extras = extra_textures(args.extract_textures)
    print(f'formations={formations}, outfit_styles={outfits}, bundle_assets={bundles}, webview_resources={webview}, extra_textures={extras}')


if __name__ == '__main__':
    main()
