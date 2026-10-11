"""Make or restore a consistent GxB2 SQLite save without overwriting a profile.

Examples:
    python3 tools/save_archive.py backup state/profile.sqlite3 backups/profile-2026-09-30.sqlite3
    python3 tools/save_archive.py restore backups/profile-2026-09-30.sqlite3 state/restored.sqlite3

Start the game with ``python3 server.py --db state/restored.sqlite3`` to use a
restored copy. Keep the usual server running during backup; stop the restored
server before moving or renaming its database.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import tempfile


def _read_only(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise ValueError(f'No existe el archivo: {path}')
    return sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True, timeout=20)


def validate_save(path: Path) -> dict:
    """Check SQLite integrity and the minimum local profile contract."""
    with closing(_read_only(Path(path))) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('La base de datos no supera la comprobación de integridad')
        names = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {'profile', 'clock', 'battles'} <= names:
            raise ValueError('Faltan tablas de la partida local')
        rows = db.execute('SELECT id, data FROM profile').fetchall()
        if len(rows) != 1 or rows[0][0] != 1:
            raise ValueError('La partida debe tener un único perfil local')
        try:
            state = json.loads(rows[0][1])
        except (TypeError, ValueError) as exc:
            raise ValueError('El perfil no contiene JSON válido') from exc
        if not isinstance(state, dict) or not isinstance(state.get('items'), dict) or not isinstance(state.get('partners'), list):
            raise ValueError('El perfil no tiene la estructura mínima esperada')
        return {'format': state.get('format', 1), 'partners': len(state['partners'])}


def copy_save(source: Path, destination: Path) -> dict:
    """Online SQLite backup, verified and published only if destination is absent."""
    source = Path(source)
    destination = Path(destination)
    validate_save(source)
    if destination.exists():
        raise FileExistsError(f'Ya existe el destino; no se sobrescribe: {destination}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f'.{destination.name}.', suffix='.tmp', dir=destination.parent)
    os.close(fd)
    temporary = Path(name)
    try:
        with closing(_read_only(source)) as original, closing(sqlite3.connect(temporary, timeout=20)) as copy:
            original.backup(copy)
            # The live profile uses WAL; a single-file archive must be self-contained.
            copy.execute('PRAGMA journal_mode=DELETE')
        details = validate_save(temporary)
        # Hard-link creation fails atomically if another process created the destination.
        os.link(temporary, destination)
        return details
    finally:
        temporary.unlink(missing_ok=True)
        for suffix in ('-wal', '-shm'):
            Path(str(temporary) + suffix).unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description='Copia o restaura una partida local GxB2 en una ruta nueva.')
    parser.add_argument('operation', choices=('backup', 'restore'))
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    try:
        info = copy_save(args.source, args.destination)
    except (ValueError, FileExistsError, sqlite3.Error, OSError) as exc:
        parser.exit(1, f'Error: {exc}\n')
    print(f'{args.operation}: {args.destination} — formato {info["format"]}, {info["partners"]} chicas')


if __name__ == '__main__':
    main()
