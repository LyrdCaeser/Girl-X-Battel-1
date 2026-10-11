"""Print the NGUI layout tree of a Unity prefab: path, local x/y, scale, (width, height, depth, sprite/text).

Usage: python3 tools/prefab_layout.py windows/activity/check_in
       (path relative to ~/Downloads/Decomp files/unity/Assets/hotres/prefabs, without .prefab)
NGUI coordinates: origin at the parent's centre, y grows upwards. Positions are relative to the parent.
"""
import re, sys
from pathlib import Path

PREFABS = Path.home() / 'Downloads/Decomp files/unity/Assets/hotres/prefabs'


def main(name):
    text = (PREFABS / f'{name}.prefab').read_text(errors='replace')
    parts = re.split(r'\n--- !u!(\d+) &(\d+)', text)
    objs = {parts[i + 1]: (parts[i], parts[i + 2]) for i in range(1, len(parts), 3)}
    names = {fid: re.search(r'm_Name: (.*)', body).group(1) for fid, (cls, body) in objs.items() if cls == '1'}
    widgets = {}
    for cls, body in objs.values():
        go, w = re.search(r'm_GameObject: \{fileID: (\d+)', body), re.search(r'mWidth: (\d+)', body)
        if cls == '114' and go and w:
            h, d = re.search(r'mHeight: (\d+)', body), re.search(r'mDepth: (-?\d+)', body)
            tag = re.search(r'mSpriteName: (\S+)', body) or re.search(r'  mText: (.*)', body)
            widgets[go.group(1)] = (w.group(1), h.group(1), d.group(1) if d else '', tag.group(1) if tag else '')
    tr = {}
    for fid, (cls, body) in objs.items():
        if cls in ('4', '224'):
            go = re.search(r'm_GameObject: \{fileID: (\d+)', body).group(1)
            pos = re.search(r'm_LocalPosition: \{x: ([-\d.e]+), y: ([-\d.e]+)', body)
            scale = re.search(r'm_LocalScale: \{x: ([-\d.e]+)', body)
            father = re.search(r'm_Father: \{fileID: (\d+)', body)
            if not (pos and scale and father): continue  # stripped transforms of nested prefab instances
            father = father.group(1)
            tr[fid] = (go, names.get(go, '?'), float(pos.group(1)), float(pos.group(2)), scale.group(1), father)

    def path(fid):
        out = []
        while fid in tr:
            out.append(tr[fid][1]); fid = tr[fid][5]
        return '/'.join(reversed(out))
    for fid, (go, _, x, y, s, _) in tr.items():
        print(path(fid), round(x, 1), round(y, 1), s, widgets.get(go, ''))


if __name__ == '__main__':
    main(sys.argv[1])
