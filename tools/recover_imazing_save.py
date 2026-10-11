"""Sanitized, account-separated audit of GxB2 .imazingapp exports.

Never extracts the full archive or grants characters from stale client caches.
"""
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import plistlib
import sqlite3
import tempfile
import zipfile

from tools.recover_original_save import audit_original_save

DB_ENTRY = 'Container/Documents/Databases/game.db'


def audit_imazing(source: Path) -> dict:
    source = Path(source)
    with zipfile.ZipFile(source) as archive, tempfile.TemporaryDirectory() as tmp:
        entry = archive.getinfo(DB_ENTRY)
        if entry.file_size > 32 * 1024 * 1024:
            raise ValueError('Base local demasiado grande para este analizador')
        companions = [DB_ENTRY + suffix for suffix in ('-wal', '-journal') if DB_ENTRY + suffix in archive.namelist()]
        if companions:
            raise ValueError('Hay un journal/WAL: requiere consolidar una copia antes de analizar')
        data = archive.read(entry)
        original = Path(tmp) / 'original.db'
        original.write_bytes(data)
        report = {'report_format': 1, 'scope': 'ios_imazing_local_cache', 'database_sha256': hashlib.sha256(data).hexdigest(),
                  'archive_entry_count': len(archive.infolist()), 'full_progress_migration_possible': False, 'accounts': [],
                  'missing': ['complete_roster', 'current_inventory_and_currencies', 'confirmed_campaign_progress']}
        pref_paths = [i for i in archive.infolist() if i.filename.startswith('Container/Library/Preferences/com.carolgames.moemoegirls') and i.filename.endswith('.plist')]
        for pref in pref_paths:
            if pref.file_size <= 2 * 1024 * 1024:
                values = plistlib.loads(archive.read(pref))
                detail = values.get('game_detail')
                report['game_detail_cache_bytes'] = len(detail) if isinstance(detail, bytes) else None
        with closing(sqlite3.connect(original.as_uri() + '?mode=ro&immutable=1', uri=True)) as db:
            if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('Base corrupta')
            report['table_rows'] = {t: db.execute('SELECT count(*) FROM "' + t + '"').fetchone()[0]
                                    for t in ('player_info', 'formation', 'misc', 'activity', 'table_data', 'hot_fix')}
            accounts = {str(r[0]) for r in db.execute('SELECT DISTINCT playerID FROM misc')}
            formations = list(db.execute('SELECT key,value FROM formation ORDER BY key'))
            accounts.update(str(k).partition(':')[2] for k, _ in formations)
            for index, account in enumerate(sorted(accounts, key=str), 1):
                alias = f'A{index:03d}'
                account_forms = [(k, v) for k, v in formations if str(k).partition(':')[2] == str(account)]
                rows = list(db.execute('SELECT key,value FROM misc WHERE playerID=?', (account,)))
                safe_db = Path(tmp) / f'{alias}.db'
                # Reuse the validated allowlist auditor with an account-isolated temporary DB.
                with sqlite3.connect(safe_db) as isolated:
                    isolated.executescript('CREATE TABLE formation(key TEXT,value TEXT); CREATE TABLE misc(playerID TEXT,key TEXT,value TEXT);')
                    isolated.executemany('INSERT INTO formation VALUES (?,?)', [(str(k).partition(':')[0] + ':local', v) for k, v in account_forms])
                    isolated.executemany('INSERT INTO misc VALUES (?,?,?)', [('local', k, v) for k, v in rows])
                recovered = audit_original_save(safe_db)
                result = {'account_alias': alias, 'misc_rows': len(rows),
                          **{k: recovered[k] for k in ('formations', 'preferences', 'selected_outfit_styles', 'unresolved_hero_count', 'unresolved_pet_count', 'warnings')}}
                values = dict(rows)
                def decode(key):
                    try:
                        value = json.loads(values.get(key, '{}'))
                        return value if isinstance(value, dict) else {}
                    except (TypeError, ValueError):
                        return {}
                special = decode('guild_competition_special_partner')
                true = decode('guild_competition_special_true_partner_info')
                result['guild_special_snapshot'] = {k: special[k] for k in ('tableID', 'star', 'grade', 'level', 'awake')
                                                   if isinstance(special.get(k), int) and not isinstance(special.get(k), bool)}
                true_table = true.get('trueTableID')
                if isinstance(true_table, int) and not isinstance(true_table, bool):
                    result['historical_guild_base_table_id'] = true_table
                result['historical_outfit_group_cache'] = {str(k): v for k, v in decode('local_dress_save_office_active_new').items()
                                                          if str(k).isdigit() and isinstance(v, int) and not isinstance(v, bool)}
                report['accounts'].append(result)
        report['notes'] = [
            'Accounts remain separated and anonymized; no credentials, chat, device IDs or original instance IDs are exported.',
            'Guild special snapshot can be modified for its mode and is not an authentic current character build.',
            'Outfit group cache indicates historical activation, not current quantities, stars or ownership.',
            'No playable save is created or overwritten; full migration remains unverified.',
        ]
        return report


def main():
    parser = argparse.ArgumentParser(description='Audita una exportación GxB2 de iMazing sin modificarla.')
    parser.add_argument('source', type=Path)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    try:
        result = audit_imazing(args.source)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open('x') as file:
            json.dump(result, file, ensure_ascii=False, indent=2)
            file.write('\n')
    except (OSError, ValueError, KeyError, sqlite3.Error, zipfile.BadZipFile) as exc:
        parser.exit(1, f'Error: {exc}\n')
    print(f'Informe guardado; cuentas separadas: {len(result["accounts"])}; no se creó una partida importada.')


if __name__ == '__main__':
    main()
