"""Recover literal client tables without executing Lua or modifying source/save files.

Raw cells and declared positional keys are retained: SQLite game columns are not
trusted as replacements for Lua keys. A mention is evidence of a reference only,
never proof of implemented gameplay. Run with --source to select a source archive.
"""
import argparse
import hashlib
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'\s+|--[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|[^\W\d]\w*|[{}\[\],;=]', re.S)


def lua_string(s):
    body = s[1:-1]
    escapes = {'a': '\a', 'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t', 'v': '\v', '\\': '\\', '"': '"', "'": "'"}
    def sub(m):
        v = m.group(1)
        if v.isdigit():
            n = int(v)
            if n > 255:
                raise ValueError('Lua byte escape out of range')
            return chr(n)
        if v not in escapes:
            raise ValueError(f'Unsupported string escape {v!r}')
        return escapes[v]
    return re.sub(r'\\(\d{1,3}|.)', sub, body, flags=re.S)


def literal(text):
    tokens = []
    pos = 0
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m:
            raise ValueError(f'Unsupported Lua at offset {pos}: {text[pos:pos+40]!r}')
        pos = m.end()
        t = m.group()
        if not t.isspace() and not t.startswith('--'):
            tokens.append(t)
    i = 0
    def value():
        nonlocal i
        t = tokens[i]; i += 1
        if t == '{':
            pairs, array = {}, []
            while tokens[i] != '}':
                if tokens[i] == '[':
                    i += 1; key = value()
                    if tokens[i:i+2] != [']', '=']: raise ValueError('Invalid key')
                    i += 2; pairs[str(key)] = value()
                elif re.fullmatch(r'[^\W\d]\w*', tokens[i]) and tokens[i+1] == '=':
                    key = tokens[i]; i += 2; pairs[key] = value()
                else:
                    array.append(value())
                if tokens[i] in (',', ';'): i += 1
                elif tokens[i] != '}': raise ValueError('Invalid separator')
            i += 1
            if pairs and array: raise ValueError('Mixed keyed/array constructor')
            return pairs if pairs else array
        if t.startswith(('"', "'")): return lua_string(t)
        if t in ('true', 'false', 'nil'): return {'true': True, 'false': False, 'nil': None}[t]
        if re.fullmatch(r'-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?', t):
            return float(t) if any(c in t for c in '.eE') else int(t)
        raise ValueError(f'Nonliteral value {t!r}')
    result = value()
    if i != len(tokens): raise ValueError('Trailing tokens')
    return result


def read_table(path):
    text = path.read_text(encoding='utf-8-sig')
    keys_text, rest = text.split('table.keys =', 1)[1].split('table.rows =', 1)
    parts = re.findall(r'local table\d+ = import\("\.([a-z0-9_]+)"\)', rest)
    if parts:
        # Known generated import/metatable chain: earlier segments override later ones.
        own_rows = literal(rest.split('local table', 1)[0].strip())
        if own_rows != []: raise ValueError('Unexpected composite own rows')
        keys = literal(keys_text.strip())
        if keys != []: raise ValueError('Unexpected composite own keys')
        keys, rows = {}, {}
        for name in reversed(parts):
            child_keys, child_rows, _ = read_table(path.with_name(name+'.lua'))
            keys.update(child_keys); rows.update(child_rows)
        id_match = re.search(r'table.ids\s*=\s*(\{.*?\})\s*return table', rest, re.S)
        if not id_match: raise ValueError('Composite has no ordered ids')
        ids = literal(id_match.group(1))
        if len(ids) != len(set(ids)) or set(map(str, ids)) != set(rows):
            raise ValueError('Composite ids do not match resolved rows')
        rows = {str(rid): rows[str(rid)] for rid in ids}
    else:
        rows_text = rest.rsplit('return table', 1)[0].strip()
        keys, rows = literal(keys_text.strip()), literal(rows_text)
        if rows == []: rows = {}
    if not isinstance(keys, dict) or not isinstance(rows, dict):
        raise ValueError('Invalid schema or keyed rows')
    if any(not isinstance(v, int) or v < 1 for v in keys.values()):
        raise ValueError('Invalid field position')
    widths = defaultdict(int)
    for rid, cells in rows.items():
        if not isinstance(cells, list): raise ValueError(f'Row {rid} is not a cell array')
        widths[len(cells)] += 1
        if len(cells) > max(keys.values(), default=0):
            raise ValueError(f'Row {rid} exceeds schema')
    return keys, rows, dict(widths)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, default=Path.home()/'Downloads/Decomp files')
    ap.add_argument('--output', type=Path, default=ROOT/'data/recovered')
    args = ap.parse_args()
    source, out = args.source, args.output
    data = source/'lua/data/tables'
    files = sorted(data.glob('*.lua'))
    if not files: raise SystemExit('No source tables found')
    # Baseline excludes this extractor and generated files: recovery must not inflate usage.
    local = {}
    for pattern in ('gxb2/*.py', 'tools/*.py', 'web/*.js', 'server.py'):
        for p in ROOT.glob(pattern):
            if p.name in ('recover_client_tables.py', 'build_client_inventory.py'): continue
            local[str(p.relative_to(ROOT))] = set(re.findall(r'[A-Za-z_][A-Za-z_0-9]*', p.read_text(errors='replace')))
    classes = source/'lua/app/common/tables'
    tm = (classes/'TableManager.lua').read_text(encoding='utf-8-sig')
    accessor_class = dict(re.findall(r'metatable\.(\w+)\s*=\s*"app\.common\.tables\.(\w+)"', tm))
    class_tables = {}
    for p in classes.glob('*.lua'):
        class_tables[p.stem] = sorted(set(re.findall(r'ctor\(self,\s*"([a-z0-9_]+?)_?"', p.read_text(encoding='utf-8-sig'))))
    consumers = defaultdict(list)
    client_files = {}
    for folder in ('models', 'windows'):
        for p in sorted((source/f'lua/app/{folder}').glob('*.lua')):
            t = p.read_text(encoding='utf-8-sig')
            accessors = sorted(set(re.findall(r'xyd\.tables\.(\w+)', t)))
            tables = sorted({n for a in accessors for n in class_tables.get(accessor_class.get(a, ''), [])})
            rel = str(p.relative_to(source))
            for name in tables: consumers[name].append(rel)
            client_files[rel] = {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'tables': tables,
                                'messages': sorted(set(re.findall(r'xyd\.mid\.([A-Z0-9_]+)', t)))}
    entries, errors = [], []
    for p in files:
        try:
            keys, rows, widths = read_table(p)
            parts = re.findall(r'local table\d+ = import\("\.([a-z0-9_]+)"\)', p.read_text(encoding='utf-8-sig'))
            payload = {'name': p.stem, 'keys': keys, 'rows': rows, 'components': parts}
            target = out/'tables'/f'{p.stem}.json'
            write_json(target, payload)
            entries.append({'name': p.stem, 'source': str(p.relative_to(source)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                            'json_sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'rows': len(rows), 'components': parts, 'fields': list(sorted(keys, key=keys.get)),
                            'row_widths': widths, 'client_consumers': consumers[p.stem],
                            'local_references': sorted(n for n, words in local.items() if p.stem in words)})
        except Exception as exc:
            errors.append({'table': p.stem, 'error': str(exc)})
    texts = []
    db = source/'data/en_en.db'
    with sqlite3.connect(db.resolve().as_uri()+'?mode=ro', uri=True) as con:
        for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
            quoted = '"'+name.replace('"', '""')+'"'
            cursor = con.execute('SELECT * FROM '+quoted)
            columns = [c[0] for c in cursor.description]
            rows = [list(row) for row in cursor]
            target = out/'texts/en_en'/f'{name}.json'
            write_json(target, {'name': name, 'columns': columns, 'rows': rows})
            texts.append({'name': name, 'rows': len(rows), 'columns': columns, 'json_sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    manifest = {'format_version': 1, 'source_table_count': len(files), 'tables': entries, 'errors': errors,
                'english_source_sha256': hashlib.sha256(db.read_bytes()).hexdigest(), 'english_tables': texts,
                'client_files': client_files,
                'limits': ['Local references are lexical evidence, not proof of gameplay integration.',
                           'Static table accessors only; dynamic references can be missing.',
                           'Rows preserve cell order and short rows. Omitted cells are not invented.',
                           'Recovered data does not supply missing server code or historical calendars.']}
    write_json(out/'manifest.json', manifest)
    # Research packets for client systems without a dedicated local module.
    packets = []
    for model in ('ArenaTeam', 'FairArena', 'GuildWar', 'GrowthDiary', 'NewbieCamp', 'ArenaAllServerNew', 'ArenaAllServerScore', 'PetTraining'):
        rel = f'lua/app/models/{model}.lua'
        own = [n for n in client_files if Path(n).stem.startswith(model)]
        names = sorted({t for n in own for t in client_files[n]['tables']})
        mids = sorted({m for n in own for m in client_files[n]['messages']})
        schemas = json.loads((ROOT/'data/schema.json').read_text())
        ids = json.loads((ROOT/'data/message_ids.json').read_text())
        model_source = (source/rel).read_text(encoding='utf-8-sig')
        request_names = sorted(set(re.findall(r'messages_pb[.:]([a-z_0-9]+)', model_source)))
        defs = {n: schemas[n] for n in request_names if n in schemas}
        # Preserve complete methods as evidence, not invented server implementations.
        methods = [{'name': m.group(1), 'line': model_source[:m.start()].count('\n')+1}
                   for m in re.finditer(r'^function ([^\n]+)', model_source, re.M)]
        packet = {'model': model, 'client_files': {n: client_files[n] for n in own},
                  'tables': names, 'messages': {m: ids.get(m) for m in mids},
                  'request_schemas': defs, 'unresolved_request_schemas': [n for n in request_names if n not in schemas],
                  'methods': methods, 'research_only': True}
        write_json(out/'systems'/f'{model}.json', packet)
        doc = [f'# {model} — contrato recuperado', '',
               'Investigación del cliente; no certifica implementación local ni reglas del servidor.', '',
               '## Tablas originales', '']
        lookup = {e['name']: e for e in entries}
        for name in names:
            e = lookup.get(name)
            doc.append(f'- `{name}`: '+(f"{e['rows']} filas; campos: "+', '.join(e['fields']) if e else 'sin datos resueltos'))
        doc += ['', '## Mensajes y esquemas de solicitud', '']
        doc += [f'- `{m}`: ID {ids.get(m, "no resuelto")}' for m in mids]
        for name, definition in defs.items():
            fields = ', '.join(f"{f['name']} (campo {f['number']}, tipo {f['type']}, label {f['label']})" for f in definition['fields'])
            doc.append(f'- `{name}`: {fields}')
        doc += ['', '## Métodos del modelo (líneas de la fuente original)', '']
        doc += [f"- Línea {m['line']}: `{m['name']}`" for m in methods]
        doc += ['', '## Evidencia de costes, límites y tiempo', '',
                'Fragmentos originales del modelo y sus ventanas propias; requieren revisar el contexto antes de convertirlos en reglas.', '']
        for n in own:
            original = (source/n).read_text(encoding='utf-8-sig').splitlines()
            evidence = [(i+1, line.strip()) for i, line in enumerate(original)
                        if re.search(r'cost|limit|award|[sS]erverTime|[sS]tartTime|[eE]ndTime|[cC]ool|[bB]uyTimes', line)]
            if evidence:
                doc += [f'### `{n}`', '', '```lua']
                doc += [f'-- {i}: {line}' for i, line in evidence[:100]]
                doc += ['```', '']
        doc += ['## Pendiente para volverlo jugable', '',
                'Definir equivalentes locales para respuestas, rivales/calendario y estado persistente; '
                'validar las referencias de coste/recompensa y desbloqueo; probar reinicio, límites, doble reclamación y combate. '
                'Los métodos y mensajes recuperados no contienen la implementación del servidor.']
        (out/'systems'/f'{model}.md').write_text('\n'.join(doc)+'\n')
        packets.append(model)

    unreferenced = [e for e in entries if not e['local_references']]
    lines = ['# Recuperación de tablas — 01/10/2026', '',
             f'**{len(entries)}/{len(files)} tablas Lua recuperadas**, {sum(e["rows"] for e in entries if not e["components"]):,} filas en segmentos originales; '
             f'{sum(bool(e["components"]) for e in entries)} tablas compuestas resueltas; '
             f'**{len(texts)} tablas inglesas**, {sum(e["rows"] for e in texts):,} filas. Errores: {len(errors)}.', '',
             'Generado con `python3 tools/recover_client_tables.py`. Fuentes originales en solo lectura; no se ejecuta Lua. '
             'Los nombres y posiciones de columnas se toman de `table.keys`, evitando las columnas desalineadas de `data.db`.', '',
             f'{len(entries)-len(unreferenced)} tablas tienen referencias léxicas locales; **{len(unreferenced)} no las tienen**. '
             'Una referencia puede pertenecer únicamente a un extractor. Recuperado no significa jugable ni verificado.', '',
             '## Archivos y uso', '',
             '- `data/recovered/manifest.json`: hashes, campos, tamaños, consumidores del cliente y referencias locales.',
             '- `data/recovered/tables/<nombre>.json`: `keys` conserva posiciones desde 1; `rows` conserva los arrays originales; las tablas compuestas se resuelven con prioridad del primer segmento y se enumeran en `components`. '
             'Para leer un campo: `rows[id][keys[campo] - 1]`, comprobando antes la longitud de la fila.',
             '- `data/recovered/texts/en_en/`: textos originales con columnas y filas completas.', '',
             'Se preservan listas/costes/premios codificados como cadenas, celdas vacías, ceros y -1; no se deducen reglas de servidor. '
             'No se conectan estos datos automáticamente al runtime ni se cambian partidas.', '',
             '## Contratos de sistemas para continuar', '',
             ', '.join(f'`data/recovered/systems/{n}.md`' for n in packets), '',
             'Cada dossier incluye tablas/campos, métodos con líneas de origen, mensajes/IDs, esquemas protobuf recuperados y evidencias de costes/tiempo. Son investigación, no funciones jugables.', '',
             '## Tablas pendientes de referencias locales', '',
             '| Tabla | Filas | Campos | Modelos/ventanas del cliente |', '|---|---:|---|---|']
    for e in sorted(unreferenced, key=lambda e: (not bool(e['client_consumers']), e['name'])):
        clients = ', '.join(Path(n).stem for n in e['client_consumers'][:6])
        if len(e['client_consumers']) > 6: clients += f' (+{len(e["client_consumers"])-6})'
        lines.append(f'| `{e["name"]}` | {e["rows"]} | '+', '.join(e['fields'][:10])+(' …' if len(e['fields'])>10 else '')+f' | {clients or "Sin acceso estático detectado"} |')
    if errors:
        lines += ['', '## Errores de recuperación', '', *[f'- `{e["table"]}`: {e["error"]}' for e in errors]]
    lines += ['', '## Relevo y límites', '',
              'Priorizar tablas con consumidores y sin referencias locales; revisar mensajes del consumidor en el manifest, '
              'costes/premios/desbloqueos y sus ventanas antes de implementar. Los nombres internos se conservan porque no '
              'todos tienen una etiqueta visible inequívoca. El calendario, rivales, rankings y sorteos que generaba '
              'el servidor siguen requiriendo contratos locales explícitos y pruebas.',
              'Los textos de otras lenguas permanecen en sus bases originales; esta tanda exporta inglés, idioma de la interfaz actual.']
    (ROOT/'TABLAS_RECUPERADAS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'recovered': len(entries), 'source_tables': len(files), 'rows': sum(e['rows'] for e in entries),
                      'unreferenced': len(unreferenced), 'text_tables': len(texts), 'errors': errors}, ensure_ascii=False))
    return int(bool(errors))

if __name__ == '__main__':
    raise SystemExit(main())
