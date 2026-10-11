"""Read-only inventory of GxB2 files in an unencrypted Finder backup.

Does not extract files, inspect other apps, or print account values.
"""
import argparse
from contextlib import closing
from pathlib import Path
import plistlib
import sqlite3


def inspect_backup(root: Path) -> dict:
    root = Path(root).resolve()
    manifest = root / 'Manifest.plist'
    if not manifest.is_file():
        raise ValueError('No se encuentra Manifest.plist en esta copia')
    with manifest.open('rb') as file:
        encrypted = bool(plistlib.load(file).get('IsEncrypted'))
    if encrypted:
        return {'encrypted': True, 'files': [], 'next_step': 'La copia necesita desbloqueo local; no envíes la contraseña por el chat.'}
    database = root / 'Manifest.db'
    if not database.is_file():
        raise ValueError('No se encuentra Manifest.db')
    files = []
    with closing(sqlite3.connect(database.as_uri() + '?mode=ro&immutable=1', uri=True)) as db:
        rows = db.execute("SELECT fileID,domain,relativePath FROM Files WHERE domain LIKE 'AppDomain-%moemoegirls%' OR domain LIKE 'AppDomain-%girlsxbattle%' OR domain LIKE 'AppDomain-%gxb2%'")
        for file_id, domain, relative in rows:
            # File IDs are hashes, not filesystem paths supplied by the backup.
            if not isinstance(file_id, str) or len(file_id) != 40 or any(c not in '0123456789abcdef' for c in file_id):
                continue
            present = (root / file_id[:2] / file_id).is_file() or (root / file_id).is_file()
            files.append({'domain': domain, 'relative_path': relative, 'payload_present': present})
    return {'encrypted': False, 'files': sorted(files, key=lambda x: (x['domain'], x['relative_path'])),
            'note': 'Lista de archivos candidatos; no confirma que exista una partida recuperable. Un resultado vacío requiere identificar el bundle de iOS.'}


def main():
    import json
    parser = argparse.ArgumentParser(description='Localiza archivos candidatos de GxB2 en una copia Finder sin extraerlos.')
    parser.add_argument('backup', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect_backup(args.backup), ensure_ascii=False, indent=2))
    except (OSError, ValueError, sqlite3.Error, plistlib.InvalidFileException) as exc:
        parser.exit(1, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
