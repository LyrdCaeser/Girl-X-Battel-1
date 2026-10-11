"""Audit an original Android game.db, exporting only recoverable non-account data.

This is a recovery report, not a fabricated playable account. The original
client's formation IDs cannot identify girls without a GET_SLOT_INFO snapshot.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3

SAFE_FLAGS = ('gamble_skip_1', 'gamble_skip_2', 'set_summon_skip')


def audit_original_save(source: Path) -> dict:
    source = Path(source).resolve()
    if not source.is_file():
        raise ValueError('No existe la base original')
    report = {
        'report_format': 1,
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'scope': 'original_android_local_cache',
        'full_progress_migration_possible': False,
        'missing': ['girl_identity_mapping', 'girl_levels_and_builds', 'inventory_and_currencies', 'confirmed_campaign_progress'],
        'formations': [], 'preferences': {}, 'selected_outfit_styles': {},
        'warnings': [],
    }
    with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('La base no supera la comprobación de integridad')
        tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {'formation', 'misc'} <= tables:
            raise ValueError('No es la caché local Android esperada')
        # Never select values from meta/chat, or copy raw player/partner IDs.
        report['table_rows'] = {name: db.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0]
                                for name in ('formation', 'misc', 'player_info', 'activity', 'table_data', 'hot_fix') if name in tables}
        account_count = db.execute('SELECT count(distinct playerID) FROM misc').fetchone()[0]
        report['local_account_count'] = account_count
        formation_rows = list(db.execute('SELECT key,value FROM formation ORDER BY key'))
        formation_accounts = {str(k).partition(':')[2] for k, _ in formation_rows}
        if account_count > 1 or len(formation_accounts) > 1:
            report['warnings'].append('multiple_accounts: selections excluded to avoid merging accounts')
            return report

        aliases = {'hero': {}, 'pet': {}}
        def alias(kind, raw):
            if isinstance(raw, bool) or not isinstance(raw, int) or raw <= 0:
                return None
            bucket = aliases[kind]
            if raw not in bucket:
                bucket[raw] = ('H' if kind == 'hero' else 'P') + f'{len(bucket) + 1:03d}'
            return bucket[raw]

        for key, value in formation_rows:
            mode = str(key).partition(':')[0]
            if not re.fullmatch(r'\d+(?:_\d+)?', mode):
                report['warnings'].append('unknown_formation_key_excluded')
                continue
            try:
                data = json.loads(value)
            except (ValueError, TypeError):
                report['warnings'].append('invalid_formation_json')
                continue
            if not isinstance(data, dict):
                report['warnings'].append('invalid_formation_structure')
                continue
            partners = data.get('partners', {})
            if isinstance(partners, list):
                slots = {str(i): alias('hero', raw) for i, raw in enumerate(partners, 1)}
            elif isinstance(partners, dict):
                slots = {str(k): alias('hero', raw) for k, raw in partners.items() if str(k).isdigit() and 1 <= int(k) <= 18}
            else:
                slots = {}
            report['formations'].append({'mode': mode, 'slots': slots, 'pet': alias('pet', data.get('pet_id')),
                                          'pets': [alias('pet', raw) for raw in data.get('pet_ids', [])] if isinstance(data.get('pet_ids'), list) else []})
        report['unresolved_hero_count'] = len(aliases['hero'])
        report['unresolved_pet_count'] = len(aliases['pet'])

        def value_for(key):
            row = db.execute('SELECT value FROM misc WHERE key=?', (key,)).fetchone()
            return row[0] if row else None

        for key in SAFE_FLAGS:
            value = value_for(key)
            if value is not None and str(value).strip().lower() in ('0', '1', '0.0', '1.0', 'false', 'true'):
                report['preferences'][key] = str(value).strip().lower() in ('1', '1.0', 'true')
        speed = value_for('battle_speed_new')
        if speed is not None and str(speed).strip() in ('1', '2', '3', '1.0', '2.0', '3.0'):
            report['preferences']['battle_speed'] = int(float(speed))
        selected = value_for('local_sava_chose_style_by_dress_id')
        try:
            selected = json.loads(selected) if selected else {}
            if isinstance(selected, dict):
                report['selected_outfit_styles'] = {str(k): int(v) for k, v in selected.items()
                                                    if str(k).isdigit() and isinstance(v, int) and not isinstance(v, bool) and v > 0}
        except (ValueError, TypeError):
            report['warnings'].append('invalid_outfit_style_json')
    report['notes'] = [
        'Formation aliases are saved selections; they are not a complete roster and cannot grant characters.',
        'Outfit style selections do not prove ownership or star level.',
        'Shop new-item markers, downloaded assets, selected exam stages and story prompts are not ownership/progress records.',
        'Account credentials, player identity, chat and original instance IDs are excluded.',
    ]
    return report


def main():
    parser = argparse.ArgumentParser(description='Informe anónimo de recuperación de game.db (solo lectura).')
    parser.add_argument('source', type=Path)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    try:
        report = audit_original_save(args.source)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open('x') as out:
            json.dump(report, out, ensure_ascii=False, indent=2)
            out.write('\n')
    except (ValueError, sqlite3.Error, OSError) as exc:
        parser.exit(1, f'Error: {exc}\n')
    print(f'Informe: {args.report}; formaciones: {len(report["formations"])}; chicas sin identificar: {report.get("unresolved_hero_count", 0)}')
    print('Migración completa: no; se necesita un snapshot del roster/inventario original.')


if __name__ == '__main__':
    main()
