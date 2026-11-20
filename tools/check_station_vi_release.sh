#!/usr/bin/env bash
# Run AFTER git merge --ff-only on GXB 3 VPS. Does not modify player data.
set -euo pipefail
cd /opt/gxb3

echo '=== GXB3 STATION VI | BRANCH ==='
test "$(git branch --show-current)" = "snez-vietnamese"
git rev-parse --short HEAD

echo '=== CHECK 105 PROFILES + 417 SKILLS ==='
.venv/bin/python tools/translate_station_vi.py --verify
.venv/bin/python tools/station_vi_quality.py

echo '=== CHECK SCRIPTS ==='
node --check web/station.js
node --check web/i18n-vi.js
node --check web/dates.js
node tests/test_frontend_runtime.cjs

echo '=== CHECK SOURCE CONTRACT ==='
.venv/bin/python -m unittest discover -s tests -p 'test_station_vi_coverage.py' -v

echo '=== RESTART ==='
systemctl restart gxb3

echo '=== WAIT FOR POSTGRES READINESS ==='
READY=0
for i in $(seq 1 30); do
  if curl --fail --silent --show-error --max-time 3 \
      http://127.0.0.1:9080/readyz; then
    printf '\n'
    READY=1
    break
  fi
  sleep 3
done
if [ "$READY" -ne 1 ]; then
  journalctl -u gxb3 -n 50 --no-pager
  echo 'FAIL: Server not ready'
  exit 1
fi

echo '=== VERIFY PUBLIC RELEASE ==='
.venv/bin/python tools/verify_vps_release.py

echo '=== CONFIRM TRANSLATION FILE SERVED ==='
curl --fail --silent --show-error --max-time 10 \
  'http://127.0.0.1:9080/assets/station/station-vi.json' \
  | .venv/bin/python -c 'import sys,json; d=json.load(sys.stdin); v=list(d["girls"].values());p=sum(bool(x.get("desc")) for x in v);s=sum(len(x.get("skills",{})) for x in v);print("HTTP translated profiles:",p,"translated skills:",s);assert (p,s)==(105,417)'

echo '=== GXB3 STATION VI RELEASE COMPLETE ==='
git rev-parse HEAD
