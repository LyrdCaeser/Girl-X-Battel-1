"""Bundle original voice lines as MP3; never modify the source Ogg files."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path.home() / 'Downloads/Decomp files/unity/Assets/hotres/sounds')
    parser.add_argument('--check', action='store_true', help='Only check that every voice is bundled')
    parser.add_argument('--jobs', type=int, default=6)
    args = parser.parse_args()
    sounds = json.loads((ROOT / 'data/relations.json').read_text()).get('sounds', {})
    target = ROOT / 'web/assets/voices'
    missing = [(sid, res) for sid, res in sounds.items() if not (target / f'{sid}.mp3').is_file() or not (target / f'{sid}.mp3').stat().st_size]
    print(f'Voices: {len(sounds) - len(missing)}/{len(sounds)} bundled', flush=True)
    if args.check:
        return int(bool(missing))
    target.mkdir(parents=True, exist_ok=True)
    def convert(item):
        sid, res = item
        source = args.source / f'{res}.ogg'
        if not source.is_file():
            raise FileNotFoundError(source)
        output = target / f'{sid}.mp3'
        temporary = target / f'{sid}.tmp.mp3'
        try:
            subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-i', str(source), '-b:a', '96k', str(temporary)], check=True, capture_output=True, timeout=60)
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)
    failures = 0
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = [pool.submit(convert, item) for item in missing]
        for done, future in enumerate(as_completed(futures), 1):
            try:
                future.result()
            except Exception as exc:
                failures += 1
                print(f'Conversion failed: {exc}', flush=True)
            if done % 500 == 0 or done == len(futures):
                print(f'Processed: {done}/{len(futures)}, failures: {failures}', flush=True)
    return int(bool(failures))

if __name__ == '__main__':
    raise SystemExit(main())
