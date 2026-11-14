from __future__ import annotations
import json
import struct
from pathlib import Path
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'data/schema.json').read_text())
MIDS = json.loads((ROOT / 'data/message_ids.json').read_text())
NAMES = {v: k for k, v in MIDS.items()}
HEADER = struct.Struct('<IH')
MAX_PAYLOAD = 16 * 1024 * 1024
file = descriptor_pb2.FileDescriptorProto(name='gxb2_apk.proto', syntax='proto2')
for name, entry in SCHEMA.items():
    message = file.message_type.add(name=name)
    for field in entry['fields']:
        f = message.field.add(name=field['name'], number=field['number'], label=field['label'], type=field['type'])
        if field.get('message_type'):
            f.type_name = '.' + field['message_type']
POOL = descriptor_pool.DescriptorPool()
POOL.Add(file)
CLASSES = {name: message_factory.GetMessageClass(POOL.FindMessageTypeByName(name)) for name in SCHEMA}
ALIASES = {'GET_BACKPACK_INFO': 'backpack_info'}

def message_type(mid: int, direction: str) -> str:
    name = NAMES.get(mid)
    if not name:
        raise ValueError(f'Unknown message ID: {mid}')
    base = ALIASES.get(name, name.lower())
    return base if name == 'ERROR_MESSAGE' else base + '_' + direction

# Fields the local save keeps next to an original message but that never go on the wire: partner `soul_infos` is the
# Anima Gear params for ReportHero / HeroAttr (the original sends only `souls`, the equipped ids).
LOCAL_ONLY = {'partners_info': {'soul_infos'}}

def normalize(name: str, data: dict, *, strict: bool = True) -> dict:
    fields = {f['name']: f for f in SCHEMA[name]['fields']}
    if name in LOCAL_ONLY and LOCAL_ONLY[name] & set(data):
        data = {k: v for k, v in data.items() if k not in LOCAL_ONLY[name]}
    if strict and set(data) - fields.keys():
        raise ValueError(f'Unexpected {name} fields: {sorted(set(data)-fields.keys())}')
    out = {}
    for key, value in data.items():
        if key not in fields or value is None:
            continue
        field = fields[key]
        if field['label'] == 3:
            if value == {}:
                value = []  # Lua's empty table represents empty repeated fields.
            if not isinstance(value, list):
                raise ValueError(f'{name}.{key} must be a list')
            out[key] = [normalize(field['message_type'], v, strict=strict) for v in value] if field['type'] == 11 else value
        elif field['type'] == 11:
            if not isinstance(value, dict):
                raise ValueError(f'{name}.{key} must be an object')
            out[key] = normalize(field['message_type'], value, strict=strict)
        else:
            if name == 'battle_data' and key == 'total_harm':
                # The original client defines total_harm as signed int32.
                # LuaJIT legitimately accumulates more than 2**31-1 at 25★.
                # Saturate ONLY the legacy protobuf copy, not the actual
                # authoritative LuaJIT report saved as exact JSON. Otherwise
                # MAP_FIGHT raises "Value out of range: 3192954487" and
                # rolls back the player fight and rewards.
                if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                    raise ValueError('battle_data.total_harm must be a nonnegative integer')
                value = min(value, 2**31 - 1)
            out[key] = value
    return out

def assign(message, data):
    for key, value in data.items():
        field = message.DESCRIPTOR.fields_by_name[key]
        if field.is_repeated:
            if field.message_type:
                for item in value:
                    assign(getattr(message, key).add(), item)
            else:
                getattr(message, key).extend(value)
        elif field.message_type:
            child = getattr(message, key)
            child.SetInParent()
            assign(child, value)
        else:
            setattr(message, key, value)

def encode(name: str, data: dict, *, strict=True) -> bytes:
    msg = CLASSES[name]()
    assign(msg, normalize(name, data, strict=strict))
    if not msg.IsInitialized():
        raise ValueError(f'{name}: missing required fields {msg.FindInitializationErrors()}')
    return msg.SerializeToString()

def as_dict(msg) -> dict:
    out = {}
    for field, value in msg.ListFields():
        if field.is_repeated:
            out[field.name] = [as_dict(v) for v in value] if field.message_type else list(value)
        else:
            out[field.name] = as_dict(value) if field.message_type else value
    return out

def decode(name: str, payload: bytes) -> dict:
    msg = CLASSES[name]()
    msg.ParseFromString(payload)
    if not msg.IsInitialized():
        raise ValueError(f'{name}: missing required fields {msg.FindInitializationErrors()}')
    return as_dict(msg)

def frame(mid: int, payload: bytes, sequence: int | None = None) -> bytes:
    if sequence is not None:
        payload = struct.pack('<I', sequence) + payload
    if len(payload) > MAX_PAYLOAD:
        raise ValueError('Frame too large')
    return HEADER.pack(len(payload), mid) + payload

def defaults(name: str) -> dict:
    """Required structural fields only; callers must supply meaningful game values."""
    out = {}
    for f in SCHEMA[name]['fields']:
        if f['label'] != 2:
            continue
        out[f['name']] = defaults(f['message_type']) if f['type'] == 11 else ('' if f['type'] in (9, 12) else False if f['type'] == 8 else 0)
    return out
