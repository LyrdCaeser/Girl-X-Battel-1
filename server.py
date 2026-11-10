#!/usr/bin/env python3
from __future__ import annotations
import argparse
from email.parser import BytesParser
from email.policy import default
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie
import json, re
from decimal import Decimal
import hashlib
import hmac
import os
import secrets
from pathlib import Path
import socketserver
import struct
import threading
import time
from urllib.parse import parse_qs, urlparse
from gxb2.engine import Engine, GameError, LOCAL_TOKEN
from gxb2.story import catalog as story_catalog
from gxb2.dress import catalog as dress_catalog
from gxb2.skins import catalog as skins_catalog
from gxb2.souls import catalog as souls_catalog
from gxb2 import protocol as p, local_promotion, local_config, world_live_config, topup, live_service, auth, database, gm_catalog, giftcodes, studio_sso, skin_store, skin_bank, skin_gifts, owner_recovery
from gxb2.player_engines import PlayerEnginePool
from gxb2.battle import simulate as simulate_battle, ONLINE_BATTLE_ID, normalize_online_seed
from gxb2.security import FixedWindowRateLimiter, DEFAULT_LIMITS, env_bool, validate_production_config
from gxb2.production import run_startup_preflight

ROOT = Path(__file__).resolve().parent
ADMIN_KEY = os.environ.get('GXB3_ADMIN_KEY', '').strip()
CHARACTER_ART = set(json.loads((ROOT/'web/assets/characters.json').read_text()))
BATTLE_MAPS = set(json.loads((ROOT/'web/assets/battle-maps.json').read_text()))
CARD_ART = set(json.loads((ROOT/'web/assets/cards.json').read_text()))
def _card_aliases():
    # Re-issued girls (e.g. Selene 546003 → 46003, 656012 → 546003) have no card of their own: serve their host's card.
    rows = {int(g['id']): g for g in json.loads((ROOT/'web/assets/girls-catalog.json').read_text())}
    out = {}
    for gid in rows:
        cur, hops = gid, 0
        while cur not in CARD_ART and rows.get(cur, {}).get('host') and hops < 5:
            cur, hops = int(rows[cur]['host']), hops + 1
        if gid not in CARD_ART and cur in CARD_ART: out[gid] = cur
    return out
CARD_ALIAS = _card_aliases()

def _json_default(value):
    # PostgreSQL NUMERIC values can reach public read-only payloads as Decimal.
    # Emit them as JSON numbers without changing the existing response schema.
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
_MISC = {}
def misc_spine(name):
    """On demand: any UI animation of the original client ("Animation (Misc)", 982 Spine 3.6 skeletons, read only) becomes
    web/assets/spine/<name>/ (model.json + model.atlas + pages) the first time it is requested."""
    import re, shutil, sys
    out = ROOT / 'web/assets/spine' / name
    if (out / 'model.json').exists() or not re.fullmatch(r'[A-Za-z0-9_\-]+', name): return
    if not _MISC:
        src = Path.home() / 'Downloads/Decompiled/Animation (Misc)'
        _MISC['_'] = None
        if src.is_dir():
            for sk in src.rglob('*.skel'): _MISC.setdefault(sk.stem, sk)
    sk = _MISC.get(name)
    if not sk: return
    try:
        sys.path.insert(0, str(ROOT / 'tools'))
        from spine36 import decode
        atlas = sk.with_suffix('.atlas').read_text()
        out.mkdir(parents=True, exist_ok=True)
        for page in re.findall(r'^([^\r\n]+\.png)\r?$', atlas, re.M): shutil.copyfile(sk.parent / page, out / page)
        (out / 'model.atlas').write_text(atlas)
        (out / 'model.json').write_text(json.dumps(decode(sk.read_bytes()), separators=(',', ':')))
    except Exception:
        shutil.rmtree(out, ignore_errors=True)


ITEM_ICONS = set(json.loads((ROOT/'web/assets/item-icons.json').read_text()))
CAMPUS_ICONS = {p.stem for p in (ROOT/'web/assets/campus').glob('*.png')}
LIFE_ICONS = {p.stem for p in (ROOT/'web/assets/life').glob('*.png')}
VOICE_SOURCES = json.loads((ROOT/'data/relations.json').read_text()).get('sounds', {}) if (ROOT/'data/relations.json').exists() else {}
VOICE_ROOT = Path.home()/'Downloads/Decomp files/unity/Assets/hotres/sounds'
def voice_file(sound_id):
    """Girl voice lines: converted from the read-only Ogg sources to a local MP3 cache on first use."""
    res = VOICE_SOURCES.get(sound_id)
    if not res or not sound_id.isdigit(): return None
    out = ROOT/'web/assets/voices'/f'{sound_id}.mp3'
    if out.is_file() and out.stat().st_size > 0:
        return out
    src = VOICE_ROOT/f'{res}.ogg'
    if not src.is_file(): return None
    out.parent.mkdir(parents=True, exist_ok=True)
    # Several mobile clients can request the same voice after a cold cache. Convert
    # into a private temporary file and publish only a complete MP3 atomically.
    import os, subprocess, threading
    tmp = out.with_name(f'.{out.name}.{os.getpid()}.{threading.get_ident()}.tmp')
    try:
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(src), '-b:a', '96k', str(tmp)], check=False, timeout=30)
        if tmp.is_file() and tmp.stat().st_size > 0:
            os.replace(tmp, out)
    except (OSError, subprocess.SubprocessError):
        pass
    finally:
        try: tmp.unlink()
        except FileNotFoundError: pass
    return out if out.is_file() and out.stat().st_size > 0 else None
EQUIP_ASSETS = {p.stem for p in (ROOT/'web/assets/equipment').glob('*.png')}
EVENT_ASSETS = {p.stem for p in (ROOT/'web/assets/events').glob('*.png')}
LEAGUE_ICONS = {p.stem for p in (ROOT/'web/assets/league').glob('*.png')}
HOME_SYSTEM_ICONS = {p.stem for p in (ROOT/'web/assets/home-systems').glob('*.png')}
MENU_ICONS = {p.stem for p in (ROOT/'web/assets/menus').glob('*.png')}
NAV_ICONS = {p.stem for p in (ROOT/'web/assets/nav').glob('*.png')}
CURRENCY_ICONS = {p.stem for p in (ROOT/'web/assets/currency').glob('*.png')}
PROFILE_ICONS = {p.stem for p in (ROOT/'web/assets/profile').glob('*.png')}
DAILY_QUIZ_ICONS = {p.stem for p in (ROOT/'web/assets/daily-quiz').glob('*.png')}
TOWER_ICONS = {p.stem for p in (ROOT/'web/assets/tower').glob('*.png')}
UI_ICONS = {'win_back_btn', 'switch_btn', 'chat_return_icon', 'btn_partner_station', 'partner_station_change', 'partner_data_btn', 'item_bg', 'equip_star',
            'partner_card', 'partner_card_2', 'quality_0', 'quality_1', 'quality_2',
            'quality_3', 'quality_4', 'quality_5', 'quality_6', 'quality_7',
            'quality_select', 'new_formation_team_nav_icon1', 'new_formation_team_nav_icon2'}
DETAIL_ICONS = {'partner_battle_point_icon', 'attr_hp_icon', 'attr_atk_icon', 'attr_def_icon', 'attr_spd_icon',
                'partner_star_red', 'partner_detail_arrow', 'partner_detail_bubble_bg', 'partner_cv_bg',
                'partner_like01', 'partner_like02', 'skill_icon_bg', 'grade_crown', 'partner_weapon',
                'partner_cloth', 'partner_shoes', 'partner_treasure', 'partner_new_bg_cloud'}
SKILL_ICONS = {p.stem for p in (ROOT/'web/assets/skills').glob('skill_icon_*.png')}

class LocalHTTPServer(ThreadingHTTPServer):
    """The default listen backlog (5) refused connections when a screen loads dozens of images at once (Closet,
    Gallery, maps): the stylesheet or /api/state could be among the rejected requests."""
    request_queue_size = 128
    daemon_threads = True


class ThreadTCP(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

class TCPHandler(socketserver.BaseRequestHandler):
    def read_exact(self, count):
        parts = bytearray()
        while len(parts) < count:
            chunk = self.request.recv(count-len(parts))
            if not chunk: raise EOFError
            parts.extend(chunk)
        return bytes(parts)

    def handle(self):
        self.request.settimeout(60)
        authenticated = False
        sequence = 1
        while True:
            try:
                size, mid = p.HEADER.unpack(self.read_exact(p.HEADER.size))
                if size > p.MAX_PAYLOAD: return
                payload = self.read_exact(size)
            except (EOFError, OSError): return
            try:
                name = p.NAMES.get(mid)
                if name is None: raise GameError(f'ID không hợp lệ: {mid}')
                if not authenticated and name not in ('CHECK_LOGIN', 'RECONNECT'):
                    raise GameError('Vui lòng đăng nhập trước khi thao tác')
                typ = p.message_type(mid, 'req')
                if typ not in p.CLASSES:
                    raise GameError(f'{name}: định dạng yêu cầu chưa được hỗ trợ')
                data = p.decode(typ, payload)
                if name == 'RECONNECT':
                    candidate = data.get('next_seq', sequence)
                    if not 1 <= candidate < 0xFFFFFFFF: raise GameError('Thứ tự gói tin không hợp lệ')
                    sequence = candidate
                packets = self.server.engine.handle(name, data)
                if name in ('CHECK_LOGIN', 'RECONNECT'):
                    authenticated = data.get('token') == LOCAL_TOKEN and data.get('player_id') == 1
            except (ValueError, KeyError) as exc:
                packets = [(p.MIDS['ERROR_MESSAGE'], 'error_message', {'error_code': -1, 'error_msg': str(exc), 'error_mid': mid})]
            except Exception as exc:
                print(f'Error de procesamiento en ID {mid}: {type(exc).__name__}', flush=True)
                packets = [(p.MIDS['ERROR_MESSAGE'], 'error_message', {'error_code': -1, 'error_msg': 'Lỗi xử lý nội bộ', 'error_mid': mid})]
            try:
                for out_mid, out_type, body in packets:
                    self.request.sendall(p.frame(out_mid, p.encode(out_type, body), sequence))
                    sequence = (sequence+1) & 0xFFFFFFFF
            except OSError: return

class HTTPHandler(BaseHTTPRequestHandler):
    def client_ip(self):
        if getattr(self.server, 'trust_proxy', False):
            forwarded=self.headers.get('X-Forwarded-For','')
            if forwarded:
                candidate=forwarded.split(',')[0].strip()
                if candidate: return candidate[:128]
        return (self.client_address[0] if self.client_address else 'unknown')[:128]

    def request_is_https(self):
        if str(getattr(self.server,'public_origin','')).startswith('https://'):
            return True
        return bool(getattr(self.server,'trust_proxy',False) and self.headers.get('X-Forwarded-Proto','').split(',')[0].strip().lower()=='https')

    def rate_limit(self, bucket, key=None):
        spec=DEFAULT_LIMITS.get(bucket)
        limiter=getattr(self.server,'rate_limiter',None)
        if not spec or limiter is None: return True
        allowed,retry=limiter.allow(bucket,key or self.client_ip(),limit=spec[0],window=spec[1])
        if not allowed:
            self.send(429,{'error':'RATE_LIMITED','retry_after':retry},headers={'Retry-After':str(retry)})
            return False
        return True

    def is_super_gm(self):
        """Bind SUPER GM to the existing owner account, never to a client-supplied email/key."""
        ctx = self.auth_context()
        account = (ctx or {}).get('account') or {}
        owner_email = os.environ.get('GXB3_OWNER_EMAIL', 'trieuquangholuxury@gmail.com').strip().casefold()
        owner_uid = os.environ.get('GXB3_OWNER_UID', 'GXB3-00000001').strip()
        return bool(
            ctx and owner_email and owner_uid
            and str(account.get('email') or '').strip().casefold() == owner_email
            and str(account.get('uid') or '') == owner_uid
        )

    def admin_authorized(self):
        # An old shared GM key alone must never grant account or developer privileges.
        return self.is_super_gm()

    def gm_key_authorized(self):
        """Second factor for value-moving GM commands, never a substitute for the owner session."""
        if not self.is_super_gm():
            return False
        supplied = self.headers.get('X-GXB3-GM-Key', '')
        return owner_recovery.verify_key('gm', supplied)

    def reject_unauthorized_admin_mode(self):
        if self.headers.get('X-GXB2-Mode') == 'developer' and not self.admin_authorized():
            self.send(403, {'error': 'QTV_KEY_REQUIRED'})
            return True
        return False

    def session_token(self):
        cookie = SimpleCookie()
        try: cookie.load(self.headers.get('Cookie', ''))
        except Exception: return ''
        morsel = cookie.get('gxb3_session')
        return morsel.value if morsel else ''

    def auth_context(self):
        cached = getattr(self, '_auth_context', None)
        if cached is not None:
            return cached
        ctx = auth.session(self.session_token())
        self._auth_context = ctx
        return ctx

    def require_auth(self):
        ctx = self.auth_context()
        if not ctx:
            self.send(401, {'error': 'AUTH_REQUIRED'})
            return None
        return ctx

    @property
    def engine(self):
        if self.headers.get('X-GXB2-Mode') == 'developer' and self.server.developer_engine and self.admin_authorized():
            return self.server.developer_engine
        ctx = self.auth_context()
        if not ctx:
            return self.server.engine
        account = ctx['account']
        return self.server.player_engines.get(account['uid'], account['server_id'], ctx['character_name'])

    server_version = 'GXB3/0.3'
    protocol_version = 'HTTP/1.1'
    def log_message(self, fmt, *args):
        # Request bodies and local session fields are not written to logs.
        pass
    def send(self, status, content, content_type='application/json; charset=utf-8', headers=None):
        if isinstance(content, (dict, list)): content = json.dumps(content, ensure_ascii=False, default=_json_default).encode()
        elif isinstance(content, str): content = content.encode()
        extra = {}
        if content_type == 'audio/mpeg':
            # Safari only plays media served with byte ranges.
            extra['Accept-Ranges'] = 'bytes'
            match = re.match(r'bytes=(\d*)-(\d*)$', self.headers.get('Range', ''))
            if match and status == 200 and (match.group(1) or match.group(2)):
                size = len(content)
                start = int(match.group(1)) if match.group(1) else max(0, size - int(match.group(2)))
                end = min(int(match.group(2)), size - 1) if match.group(1) and match.group(2) else size - 1
                content, status = content[start:end + 1], 206
                extra['Content-Range'] = f'bytes {start}-{end}/{size}'
        self.send_response(status)
        for key, value in extra.items(): self.send_header(key, value)
        for key, value in (headers or {}).items(): self.send_header(key, value)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        request_path = urlparse(self.path).path
        static_cacheable = (
            self.command == 'GET' and status == 200 and request_path != '/asset-config.js' and
            (request_path.startswith('/assets/') or request_path.startswith('/vendor/') or
             request_path.startswith('/localization/') or
             request_path.lower().endswith(('.js', '.css', '.json', '.png', '.webp', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.mp3', '.ogg')))
        )
        self.send_header('Cache-Control', 'public, max-age=3600' if static_cacheable else 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'same-origin')
        self.send_header('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        asset_origin = ''
        configured_asset_base = os.environ.get('GXB_ASSET_BASE_URL', '').strip().rstrip('/')
        if configured_asset_base:
            try:
                parsed_asset_base = urlparse(configured_asset_base)
                if parsed_asset_base.scheme == 'https' and parsed_asset_base.netloc and not parsed_asset_base.query and not parsed_asset_base.fragment:
                    asset_origin = f'{parsed_asset_base.scheme}://{parsed_asset_base.netloc}'
            except ValueError:
                asset_origin = ''
        # asset-runtime.js redirects immutable CSS/JS/images/media to the configured CDN.
        # Keep API/auth/WebSocket connections same-origin; only static resource types use CDN.
        asset_sources = f' {asset_origin}' if asset_origin else ''
        self.send_header(
            'Content-Security-Policy',
            "default-src 'self'; "
            f"script-src 'self'{asset_sources}; "
            f"style-src 'self'{asset_sources} 'unsafe-inline'; "
            f"img-src 'self'{asset_sources} data: blob:; "
            f"font-src 'self'{asset_sources} data:; "
            f"media-src 'self'{asset_sources} blob:; "
            "connect-src 'self'; frame-ancestors 'none'"
        )
        if self.request_is_https():
            self.send_header('Strict-Transport-Security','max-age=31536000; includeSubDomains')
        self.end_headers()
        self.wfile.write(content)
    def send_sse(self, ctx, mode='arena'):
        account=ctx['account']
        self.send_response(200)
        self.send_header('Content-Type','text/event-stream; charset=utf-8')
        self.send_header('Cache-Control','no-cache, no-store')
        self.send_header('Connection','keep-alive')
        self.send_header('X-Accel-Buffering','no')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers()
        last_payload=None
        for _ in range(20):
            try:
                pvp=live_service.pvp_status(account['uid'],account['server_id'],mode)
                if pvp.get('status')=='matched' and pvp.get('match'):
                    try:
                        live_service.heartbeat_pvp_match(pvp['match']['id'],account['uid'],True)
                        pvp=live_service.pvp_status(account['uid'],account['server_id'],mode)
                    except Exception:
                        pass
                guild=live_service.guild_for_player(account['uid'],account['server_id'])
                payload={
                    'server_time':int(time.time()),
                    'server_id':account['server_id'],
                    'online_count':len(live_service.online_players(account['server_id'])),
                    'pvp':pvp,
                    'guild':{'id':guild.get('id'),'level':guild.get('level'),'exp':guild.get('exp'),
                             'member_count':guild.get('member_count')} if guild else None,
                    'wars':live_service.guild_wars(account['server_id'],20),
                }
                raw=json.dumps(payload,ensure_ascii=False,separators=(',',':'))
                if raw!=last_payload:
                    self.wfile.write(f"event: snapshot\ndata: {raw}\n\n".encode())
                    self.wfile.flush()
                    last_payload=raw
                else:
                    self.wfile.write(b": keepalive\n\n"); self.wfile.flush()
                time.sleep(2)
            except (BrokenPipeError,ConnectionResetError):
                break
            except Exception as exc:
                try:
                    err=json.dumps({'error':str(exc)},ensure_ascii=False)
                    self.wfile.write(f"event: error\ndata: {err}\n\n".encode()); self.wfile.flush()
                except Exception:
                    break
                time.sleep(2)
        self.close_connection=True

    def do_GET(self):
        if self.reject_unauthorized_admin_mode():
            return
        parsed = urlparse(self.path)
        path = parsed.path
        if path == '/healthz':
            return self.send(200,{'ok':True,'service':'gxb3','database':database.backend_name()})
        if path == '/readyz':
            try:
                worlds=live_service.worlds()
                return self.send(200,{'ready':True,'database':database.backend_name(),'worlds':len(worlds)})
            except Exception:
                return self.send(503,{'ready':False,'database':database.backend_name()})
        if path == '/api/auth/me':
            ctx = self.auth_context()
            return self.send(200, {'authenticated': bool(ctx), 'session': ctx, 'worlds': live_service.worlds(), 'is_super_gm': self.is_super_gm()})
        if path == '/api/auth/sessions':
            ctx = self.require_auth()
            if not ctx: return
            try:
                sessions = auth.sessions_for_token(self.session_token())
            except ValueError as exc:
                # The session may expire between require_auth() and the query.
                # Return a normal auth response instead of logging a traceback.
                return self.send(401, {'error': str(exc)})
            return self.send(200, {'sessions': sessions})
        if path in ('/giftcode-studio','/giftcode-studio/'):
            # Always use the dedicated Vercel Studio, preserving the game login
            # through a short-lived one-time ticket rather than a shared cookie.
            path='/api/giftcode/sso/start'
        if path == '/api/giftcode/sso/start':
            ctx = self.require_auth()
            if not ctx: return
            from html import escape
            from urllib.parse import quote
            confirmation = (parse_qs(parsed.query).get('confirm') or [''])[0]
            if not confirmation:
                # The game, not Vercel, shows the authenticated identity before
                # offering to transfer the session. Do not silently sync players.
                proof = studio_sso.confirmation_proof(self.session_token())
                account = ctx['account']
                def safe(value):
                    return escape(str(value or ''), quote=True)
                name = safe(account.get('username'))
                uid = safe(account.get('display_uid') or account.get('uid'))
                character = safe(ctx.get('character_name'))
                world = safe(account.get('server_id'))
                privilege = 'SUPER GM' if self.is_super_gm() else 'Người chơi (không có quyền SUPER GM)'
                href = '/api/giftcode/sso/start?confirm=' + quote(proof, safe='')
                page = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Xác nhận tài khoản GXB 3 — Giftcode Studio</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;min-height:100dvh;display:grid;place-items:center;background:#0b1023;color:#eaf1ff;font-family:system-ui,'Segoe UI',sans-serif;padding:18px}}
article{{width:min(100%,570px);padding:28px;background:#151e37;border:1px solid #35466d;border-radius:20px;box-shadow:0 15px 50px #0006}}
small{{color:#acbce2}}h1{{font-size:25px;margin:13px 0}}p{{line-height:1.7;color:#bcc9e7}}
dl{{display:grid;grid-template-columns:minmax(110px,160px) 1fr;gap:13px;padding:17px;background:#0c152b;border-radius:12px;overflow-wrap:anywhere}}
dt{{color:#9caed6}}dd{{margin:0;font-weight:700}}a{{text-decoration:none;color:white}}.cta{{display:block;text-align:center;background:#675cdb;border-radius:11px;padding:15px;margin-top:20px;font-weight:800}}
.back{{display:block;color:#b7c9ff;text-align:center;padding:16px 4px}}.warning{{font-size:13px;color:#ffd6ab}}
</style></head><body><article><small>GXB 3 · BẢO VỆ TÀI KHOẢN</small>
<h1>Xác nhận tài khoản trước khi đồng bộ</h1>
<p>Giftcode Studio sẽ đăng nhập bằng <strong>chính phiên game hiện tại</strong>. Kiểm tra kỹ thông tin, đặc biệt khi bạn quản lý nhiều tài khoản.</p>
<dl><dt>Tài khoản</dt><dd>{name}</dd><dt>UID</dt><dd>{uid}</dd>
<dt>Nhân vật</dt><dd>{character}</dd><dt>Máy chủ</dt><dd>{world}</dd>
<dt>Quyền</dt><dd>{privilege}</dd></dl>
<a class="cta" href="{href}">Đúng tài khoản này · Xác nhận đồng bộ</a>
<a class="back" href="/">Không đúng? Quay lại game và đổi tài khoản</a>
<p class="warning">Nếu muốn đăng nhập tài khoản khác chỉ tại Studio, hãy chọn “Đổi tài khoản Studio” trên trang Studio. Không cần xóa dữ liệu game.</p>
</article></body></html>"""
                return self.send(200, page, 'text/html; charset=utf-8', headers={
                    'Referrer-Policy': 'no-referrer',
                    'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
                })
            studio_sso.require_confirmation(self.session_token(), confirmation)
            ticket = studio_sso.start(self.session_token())
            # Finite HTTP/1.1 redirect avoids a hanging Chrome tab.
            self.send_response(303)
            self.send_header('Location', studio_sso.STUDIO_ORIGIN + '/?ticket=' + quote(ticket, safe=''))
            self.send_header('Content-Length', '0')
            self.send_header('Connection', 'close')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.close_connection = True
            return
        if path in ('/giftcode-studio/app.js','/giftcode-studio/style.css'):
            file=ROOT/'giftcode-studio'/path.rsplit('/',1)[-1]
            return self.send(200,file.read_bytes(),
                'application/javascript; charset=utf-8' if file.suffix=='.js' else 'text/css; charset=utf-8')
        if path == '/api/payment/packages':
            return self.send(200, topup.public_catalog())
        if path == '/api/skin-shop/catalog':
            # Safe for anonymous browsing; all purchases require player login.
            return self.send(200, skin_store.catalogue())
        if path.startswith('/api/') and not self.require_auth():
            return
        if path == '/api/events/stream':
            ctx=self.auth_context()
            mode=(parse_qs(parsed.query).get('mode') or ['arena'])[0]
            return self.send_sse(ctx,mode)
        if path == '/api/world/online':
            ctx = self.auth_context()
            server_id = (parse_qs(parsed.query).get('server_id') or [ctx['account']['server_id']])[0]
            rows = live_service.online_players(server_id)
            return self.send(200, {'server_id': server_id, 'count': len(rows), 'players': rows})
        if path == '/api/leaderboard':
            ctx = self.auth_context()
            query = parse_qs(parsed.query)
            server_id = (query.get('server_id') or [ctx['account']['server_id']])[0]
            limit = int((query.get('limit') or ['100'])[0])
            return self.send(200, {'server_id': server_id, 'ranking': live_service.leaderboard(server_id, limit)})
        if path == '/api/chat/messages':
            ctx = self.auth_context()
            account = ctx['account']
            query = parse_qs(parsed.query)
            channel = (query.get('channel') or ['world'])[0]
            target = (query.get('recipient_uid') or [''])[0]
            return self.send(200, {
                'server_id': account['server_id'],
                'channel': channel,
                'messages': live_service.chat_messages(
                    account['uid'], account['server_id'], channel, target)
            })
        if path == '/api/world-guild':
            ctx = self.auth_context(); account = ctx['account']
            guild = live_service.guild_for_player(account['uid'], account['server_id'])
            payload = {
                'guild': guild,
                'guilds': live_service.world_guilds(account['server_id']),
                'ranking': live_service.guild_ranking(account['server_id'], 100),
                'wars': live_service.guild_wars(account['server_id'], 50),
            }
            if guild:
                try: payload['chat'] = live_service.guild_chat(account['uid'], account['server_id'], 100)
                except Exception: payload['chat'] = []
                if guild.get('role') in ('leader','deputy'):
                    try: payload['applications'] = live_service.guild_applications(account['uid'], account['server_id'])
                    except Exception: payload['applications'] = []
            return self.send(200, payload)
        if path == '/api/guild-war':
            ctx=self.auth_context(); account=ctx['account']
            war_id=(parse_qs(parsed.query).get('war_id') or [''])[0]
            return self.send(200,live_service.guild_war_detail(account['uid'],account['server_id'],war_id))
        if path == '/api/pvp/status':
            ctx = self.auth_context(); account = ctx['account']
            query = parse_qs(parsed.query)
            mode = (query.get('mode') or ['arena'])[0]
            return self.send(200, {
                'pvp': live_service.pvp_status(account['uid'], account['server_id'], mode),
                'rating': live_service.pvp_rating(account['uid'], account['server_id'], mode),
                'rating_board': live_service.pvp_rating_board(mode, limit=50),
                'season_reward': live_service.pvp_season_claim_status(account['uid'], account['server_id'], mode),
                'history': live_service.pvp_history(account['uid'], 20),
            })
        if path == '/api/skin-shop/admin/catalog':
            if not self.admin_authorized(): return self.send(403,{'error':'Yêu cầu SUPER GM'})
            return self.send(200,skin_store.catalogue(admin=True))
        if path == '/api/owner-security/status':
            if not self.is_super_gm():
                return self.send(403, {'error':'Chỉ chủ tài khoản SUPER GM được quản lý khôi phục'})
            return self.send(200,owner_recovery.status(self.session_token()))
        if path == '/api/giftskin/orders':
            return self.send(200,skin_gifts.mine(self.auth_context()['account']['uid']))
        if path == '/api/giftskin/admin/orders':
            if not self.admin_authorized(): return self.send(403,{'error':'Yêu cầu SUPER GM'})
            status=(parse_qs(parsed.query).get('status') or ['pending'])[0]
            return self.send(200,skin_gifts.admin_orders(status))
        if path == '/api/skin-shop/bank/orders':
            account=self.auth_context()['account']
            return self.send(200,skin_bank.mine(account['uid'],account['server_id']))
        if path == '/api/skin-shop/admin/bank/orders':
            if not self.admin_authorized(): return self.send(403,{'error':'Yêu cầu SUPER GM'})
            status=(parse_qs(parsed.query).get('status') or ['pending'])[0]
            return self.send(200,skin_bank.admin_orders(status))
        if path == '/api/giftcode/check':
            if not self.admin_authorized(): return self.send(403,{'error':'Yêu cầu SUPER GM'})
            code=(parse_qs(parsed.query).get('code') or [''])[0]
            return self.send(200,{'code':code,'exists':giftcodes.exists(code)})
        if path == '/api/giftcode/catalog':
            if not self.admin_authorized(): return self.send(403,{'error':'Cần tài khoản SUPER GM'})
            return self.send(200,{'catalog':gm_catalog.catalog(),'worlds':live_service.worlds()})
        if path == '/api/giftcode/list':
            if not self.admin_authorized(): return self.send(403,{'error':'Cần tài khoản SUPER GM'})
            return self.send(200,{'codes':giftcodes.list_codes()})
        if path == '/api/giftcode/redemptions':
            if not self.admin_authorized(): return self.send(403,{'error':'Cần tài khoản SUPER GM'})
            code=(parse_qs(parsed.query).get('code') or [''])[0]
            return self.send(200,{'redemptions':giftcodes.redemptions(code)})
        if path == '/api/admin/config':
            if not self.admin_authorized():
                return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
            return self.send(200, local_config.public_config())
        if path == '/api/admin/world-config':
            if not self.admin_authorized():
                return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
            server_id=(parse_qs(parsed.query).get('server_id') or ['S1'])[0]
            return self.send(200, {'server_id':str(server_id).upper(),
                                   'config':world_live_config.public_config(server_id)})
        if path == '/api/admin/topup-packages':
            if not self.admin_authorized():
                return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
            return self.send(200, topup.get())
        if path == '/api/admin/gift-catalog':
            if not self.admin_authorized():
                return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
            return self.send(200, gm_catalog.catalog())
        if path == '/api/admin/dashboard':
            if not self.admin_authorized():
                return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
            return self.send(200, {'worlds': live_service.worlds(), 'players': live_service.players(), 'online': live_service.online_players(), 'accounts': auth.accounts(), 'orders': live_service.orders(), 'audit': live_service.audit()})
        for prefix, folder in (('/vendor/', ROOT/'web/vendor'), ('/assets/detail/sheet/', ROOT/'web/assets/detail/sheet'), ('/assets/souls/', ROOT/'web/assets/souls'), ('/assets/menu/', ROOT/'web/assets/menu'), ('/assets/stellar/', ROOT/'web/assets/stellar'), ('/assets/story-items/', ROOT/'web/assets/story-items'), ('/assets/assistant/', ROOT/'web/assets/assistant'), ('/assets/ev-sand/', ROOT/'web/assets/ev-sand'), ('/assets/guild/', ROOT/'web/assets/guild'), ('/assets/jackpot/', ROOT/'web/assets/jackpot'), ('/assets/firework-project/', ROOT/'web/assets/firework-project'), ('/assets/puzzle-events/', ROOT/'web/assets/puzzle-events'), ('/assets/blind-box/', ROOT/'web/assets/blind-box'), ('/assets/pirate/', ROOT/'web/assets/pirate'), ('/assets/wish/', ROOT/'web/assets/wish'), ('/assets/magic-card/', ROOT/'web/assets/magic-card'), ('/assets/two-love/', ROOT/'web/assets/two-love'), ('/assets/lost-space/', ROOT/'web/assets/lost-space'), ('/assets/pumpkin/', ROOT/'web/assets/pumpkin'), ('/assets/chimes/', ROOT/'web/assets/chimes'), ('/assets/altar/', ROOT/'web/assets/altar'), ('/assets/battle-loading/', ROOT/'web/assets/battle-loading'), ('/assets/summon-result/', ROOT/'web/assets/summon-result'), ('/assets/dress-show/', ROOT/'web/assets/dress-show'), ('/assets/chibis/', ROOT/'web/assets/chibis'), ('/assets/original-ui/', ROOT/'web/assets/original-ui'),
                               ('/assets/spine/', ROOT/'web/assets/spine'), ('/assets/lihui/', ROOT/'web/assets/lihui'), ('/assets/scenes/', ROOT/'web/assets/scenes'),
                               ('/assets/sounds/', ROOT/'web/assets/sounds'), ('/assets/girl-ui/', ROOT/'web/assets/girl-ui'), ('/assets/station/', ROOT/'web/assets/station'), ('/assets/battle-fx/', ROOT/'web/assets/battle-fx'), ('/assets/growth-diary/', ROOT/'web/assets/growth-diary'), ('/assets/newbie-camp/', ROOT/'web/assets/newbie-camp'), ('/assets/remaining-systems/', ROOT/'web/assets/remaining-systems'), ('/assets/fantasy-book/', ROOT/'web/assets/fantasy-book'), ('/assets/pictures/', ROOT/'web/assets/pictures'), ('/assets/campaign/', ROOT/'web/assets/campaign'), ('/assets/enroll/', ROOT/'web/assets/enroll'), ('/assets/servant/', ROOT/'web/assets/servant'), ('/assets/excursion/', ROOT/'web/assets/excursion'), ('/assets/dates/', ROOT/'web/assets/dates'), ('/assets/missions/', ROOT/'web/assets/missions'), ('/assets/shops/', ROOT/'web/assets/shops'), ('/assets/arena/', ROOT/'web/assets/arena'), ('/assets/patrol/', ROOT/'web/assets/patrol'), ('/assets/house-exam/', ROOT/'web/assets/house-exam'), ('/assets/summon/', ROOT/'web/assets/summon'), ('/assets/hero-challenge/', ROOT/'web/assets/hero-challenge'), ('/assets/sanctuary/', ROOT/'web/assets/sanctuary'), ('/assets/internship/', ROOT/'web/assets/internship'), ('/assets/midas/', ROOT/'web/assets/midas'), ('/assets/old-campus/', ROOT/'web/assets/old-campus'), ('/assets/echoes/', ROOT/'web/assets/echoes'), ('/assets/shrine/', ROOT/'web/assets/shrine'), ('/assets/galaxy/', ROOT/'web/assets/galaxy'), ('/assets/group-buff/', ROOT/'web/assets/group-buff'), ('/assets/story/', ROOT/'web/assets/story'), ('/assets/dress/', ROOT/'web/assets/dress'), ('/assets/skins/', ROOT/'web/assets/skins'), ('/assets/slots/', ROOT/'web/assets/slots')):
            if path.startswith(prefix):
                candidate = (folder / path[len(prefix):]).resolve()
                if prefix == '/assets/spine/' and candidate.is_relative_to(folder.resolve()) and not candidate.is_file(): misc_spine(candidate.parent.name)
                if candidate.is_relative_to(folder.resolve()) and candidate.is_file():
                    mime = {'.js':'application/javascript', '.png':'image/png', '.json':'application/json', '.atlas':'text/plain', '.mp3':'audio/mpeg', '.webp':'image/webp', '.ogg':'audio/ogg'}.get(candidate.suffix)
                    if mime: return self.send(200, candidate.read_bytes(), mime)
                return self.send(404, {'error':'Recurso inexistente'})
        # On demand from the read-only originals, cached in web/assets/: any cut sprite (/assets/sprite/<name>.png) and any scene
        # background (/assets/bg/<name>.webp, from Images (backgrounds)/scenes · scenes_big · battle_map).
        if path == '/asset-config.js':
            asset_base = os.environ.get('GXB_ASSET_BASE_URL', '').strip().rstrip('/')
            if asset_base and (not asset_base.startswith('https://') or urlparse(asset_base).query or urlparse(asset_base).fragment or not urlparse(asset_base).netloc):
                return self.send(500, {'error': 'GXB_ASSET_BASE_URL must be an HTTPS URL without query or fragment'})
            body = ('window.GXB_ASSET_BASE_URL = ' + json.dumps(asset_base) + ';\n').encode('utf-8')
            return self.send(200, body, 'application/javascript; charset=utf-8')
        if path.startswith('/assets/sprite/') and path.endswith('.png'):
            stem = path[len('/assets/sprite/'):-4]
            if re.fullmatch(r'[A-Za-z0-9_\-]+', stem):
                dst = ROOT / 'web/assets/sprite' / f'{stem}.png'
                if not dst.is_file():
                    src = Path.home() / 'Downloads/Decompiled/Sprites (atlases, cut)' / f'{stem}.png'
                    if src.is_file():
                        dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(src.read_bytes())
                if dst.is_file(): return self.send(200, dst.read_bytes(), 'image/png')
            return self.send(404, {'error':'Recurso inexistente'})
        if path.startswith('/assets/bg/') and path.endswith('.webp'):
            stem = path[len('/assets/bg/'):-5]
            if re.fullmatch(r'[A-Za-z0-9_\-]+', stem):
                dst = ROOT / 'web/assets/bg' / f'{stem}.webp'
                if not dst.is_file():
                    for sub in ('scenes', 'scenes_big', 'battle_map'):
                        base = Path.home() / 'Downloads/Decompiled/Images (backgrounds)' / sub
                        src = next((q for q in (base / f'{stem}.png', base / f'{stem}.jpg') if q.is_file()), None)
                        if src:
                            try:
                                from PIL import Image
                                dst.parent.mkdir(parents=True, exist_ok=True); Image.open(src).save(dst, 'WEBP', quality=86)
                            except Exception: pass
                            break
                if dst.is_file(): return self.send(200, dst.read_bytes(), 'image/webp')
            return self.send(404, {'error':'Recurso inexistente'})
        if path.startswith('/localization/') and path.endswith('.json'):
            name=path.rsplit('/',1)[-1]
            if name == 'vi.json':
                return self.send(200,(ROOT/'localization'/'vi.json').read_bytes(),'application/json; charset=utf-8')
            return self.send(404, {'error':'Chỉ hỗ trợ Tiếng Việt'})
        if path == '/health': return self.send(200, {'ok': True, 'scope': 'gxb3-private', 'database': database.backend_name(), 'schema_messages': len(p.SCHEMA)})
        if path == '/api/state': return self.send(200, self.engine.snapshot())
        if path == '/api/bootstrap': return self.send(200, {'payload': self.bootstrap()})
        if path == '/assets/characters.json': return self.send(200, sorted(CHARACTER_ART))
        if path == '/assets/battle-maps.json': return self.send(200, sorted(BATTLE_MAPS))
        if path == '/assets/girls-catalog.json': return self.send(200, (ROOT/'web/assets/girls-catalog.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/cards.json': return self.send(200, sorted(CARD_ART | set(CARD_ALIAS)))
        if path == '/assets/items-catalog.json': return self.send(200, (ROOT/'web/assets/items-catalog.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/item-icons.json': return self.send(200, sorted(ITEM_ICONS))
        if path == '/assets/profile/catalog.json': return self.send(200, (ROOT/'web/assets/profile/catalog.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/girl-details.json': return self.send(200, (ROOT/'web/assets/girl-details.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/local-promotion.json': return self.send(200, json.dumps(local_promotion.RECIPES).encode(), 'application/json; charset=utf-8')
        if path == '/assets/graduate.json': return self.send(200, (ROOT/'data/graduate.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/ascension.json': return self.send(200, (ROOT/'data/ascension.json').read_bytes(), 'application/json; charset=utf-8')
        if path.startswith('/assets/campus/') and path.endswith('.png'):
            stem = path[len('/assets/campus/'):-4]
            if stem in CAMPUS_ICONS:
                return self.send(200, (ROOT/'web/assets/campus'/f'{stem}.png').read_bytes(), 'image/png')
        for folder, icons in (('life', LIFE_ICONS), ('league', LEAGUE_ICONS), ('menus', MENU_ICONS)):
            prefix = f'/assets/{folder}/'
            if path.startswith(prefix) and path.endswith('.png'):
                stem = path[len(prefix):-4]
                if stem in icons:
                    return self.send(200, (ROOT/'web/assets'/folder/f'{stem}.png').read_bytes(), 'image/png')
        if path.startswith('/assets/nav-reference/bottom-') and path.endswith('.png'):
            stem = path.rsplit('/', 1)[-1]
            if stem in {f'bottom-{i}.png' for i in range(1, 7)}:
                return self.send(200, (ROOT/'web/assets/nav-reference'/stem).read_bytes(), 'image/png')
        if path.startswith('/assets/nav/') and path.endswith('.png'):
            stem = path[len('/assets/nav/'):-4]
            if stem in NAV_ICONS:
                return self.send(200, (ROOT/'web/assets/nav'/f'{stem}.png').read_bytes(), 'image/png')
        if path.startswith('/assets/currency/') and path.endswith('.png'):
            stem = path[len('/assets/currency/'):-4]
            if stem in CURRENCY_ICONS:
                return self.send(200, (ROOT/'web/assets/currency'/f'{stem}.png').read_bytes(), 'image/png')
        if path.startswith('/assets/profile/') and path.endswith('.png'):
            stem = path[len('/assets/profile/'):-4]
            if stem in PROFILE_ICONS:
                return self.send(200, (ROOT/'web/assets/profile'/f'{stem}.png').read_bytes(), 'image/png')
        if path.startswith('/assets/daily-quiz/') and path.endswith('.png'):
            stem = path[len('/assets/daily-quiz/'):-4]
            if stem in DAILY_QUIZ_ICONS:
                return self.send(200, (ROOT/'web/assets/daily-quiz'/f'{stem}.png').read_bytes(), 'image/png')
        if path.startswith('/assets/tower/') and path.endswith('.png'):
            stem = path[len('/assets/tower/'):-4]
            if stem in TOWER_ICONS:
                return self.send(200, (ROOT/'web/assets/tower'/f'{stem}.png').read_bytes(), 'image/png')
        if path == '/assets/home-systems/catalog.json':
            return self.send(200, (ROOT/'web/assets/home-systems/catalog.json').read_bytes(), 'application/json')
        if path.startswith('/assets/home-systems/') and path.endswith('.png'):
            stem=path[len('/assets/home-systems/'):-4]
            if stem in HOME_SYSTEM_ICONS:
                return self.send(200, (ROOT/'web/assets/home-systems'/f'{stem}.png').read_bytes(), 'image/png')
        if path.startswith('/assets/detail/') and path.endswith('.png'):
            stem = path[len('/assets/detail/'):-4]
            if stem in DETAIL_ICONS:
                return self.send(200, (ROOT/'web/assets/detail'/f'{stem}.png').read_bytes(), 'image/png')
        if path.startswith('/assets/skills/') and path.endswith('.png'):
            stem = path[len('/assets/skills/'):-4]
            if stem in SKILL_ICONS:
                return self.send(200, (ROOT/'web/assets/skills'/f'{stem}.png').read_bytes(), 'image/png')
        if path.startswith('/assets/cards/partner_card_') and path.endswith('.png'):
            stem = path[len('/assets/cards/partner_card_'):-4]
            if stem.isdecimal() and stem == str(int(stem)) and (int(stem) in CARD_ART or int(stem) in CARD_ALIAS):
                real = CARD_ALIAS.get(int(stem), int(stem))
                return self.send(200, (ROOT/'web/assets/cards'/f'partner_card_{real}.png').read_bytes(), 'image/png')
        if path.startswith('/assets/item-icons/') and path.endswith('.png'):
            stem = path[len('/assets/item-icons/'):-4]
            if stem in ITEM_ICONS:
                return self.send(200, (ROOT/'web/assets/item-icons'/f'{stem}.png').read_bytes(), 'image/png')
        if path.startswith('/assets/ui/') and path.endswith('.png'):
            stem = path[len('/assets/ui/'):-4]
            if stem in UI_ICONS:
                return self.send(200, (ROOT/'web/assets/ui'/f'{stem}.png').read_bytes(), 'image/png')
        if path.startswith('/assets/factions/') and path.endswith('.png'):
            stem = path.rsplit('/', 1)[-1][:-4]
            if stem.isdecimal() and 1 <= int(stem) <= 7:
                return self.send(200, (ROOT/'web/assets/factions'/f'group{int(stem)}.png').read_bytes(), 'image/png')
        if path.startswith('/assets/capsule/') and path.endswith('.png'):
            stem = path.rsplit('/', 1)[-1]
            capsule_assets = {'summon-scene.png', 'regular-panel.png', 'advanced-panel.png', 'bff-panel.png',
                              'regular-title.png', 'advanced-title.png', 'bff-title.png', 'button-blue.png',
                              'button-gold.png', 'pity-bar.png', 'pity-fill.png', 'summon_record_friendship_icon.png', 'summon_record_ticket_icon.png', 'summon_res.png'}
            if stem in capsule_assets:
                return self.send(200, (ROOT/'web/assets/capsule'/stem).read_bytes(), 'image/png')
        if path.startswith('/assets/battle-maps/') and path.endswith('.png'):
            stem = path[len('/assets/battle-maps/'):-4]
            if stem in BATTLE_MAPS:
                return self.send(200, (ROOT/'web/assets/battle-maps'/f'{stem}.png').read_bytes(), 'image/png')
        if path.startswith('/assets/characters/') and path.endswith('.png'):
            stem = path[len('/assets/characters/'):-4]
            if stem.isdecimal() and int(stem) in CHARACTER_ART and stem == str(int(stem)):
                return self.send(200, (ROOT/'web/assets/characters'/f'{stem}.png').read_bytes(), 'image/png')
        if path == '/assets/partner-pictures.json':
            return self.send(200, (ROOT/'data/partner_pictures.json').read_bytes(), 'application/json')
        # Keep both spellings: the original route was singular, while the
        # restored mobile/frontend clients use the natural plural /voices/ path.
        for voice_prefix in ('/assets/voice/', '/assets/voices/'):
            if path.startswith(voice_prefix) and path.endswith('.mp3'):
                sound_id = path[len(voice_prefix):-4]
                f = voice_file(sound_id)
                return self.send(200, f.read_bytes(), 'audio/mpeg') if f else self.send(404, {'error': 'Voz no disponible'})
        if path == '/assets/dress-show.json':
            return self.send(200, (ROOT/'data/dress_show.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/chimes.json':
            return self.send(200, (ROOT/'data/chimes.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/pumpkin.json':
            return self.send(200, (ROOT/'data/pumpkin.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/lost-space.json':
            return self.send(200, (ROOT/'data/lost_space.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/pirate.json':
            return self.send(200, (ROOT/'data/pirate.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/firework-project.json':
            return self.send(200, (ROOT/'data/firework_project.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/puzzle-events.json':
            return self.send(200, (ROOT/'data/puzzle_events.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/blind-box.json':
            return self.send(200, (ROOT/'data/blind_box.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/jackpot.json':
            return self.send(200, (ROOT/'data/jackpot.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/activity-draw.json':
            return self.send(200, (ROOT/'data/activity_draw.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/guild.json':
            import json as _j
            d = _j.loads((ROOT/'data/guild.json').read_text()); d['bosses'] = __import__('gxb2.guild', fromlist=['x']).bosses(); d.pop('boss', None)
            return self.send(200, _j.dumps(d, ensure_ascii=False).encode(), 'application/json; charset=utf-8')
        if path == '/assets/activity-kit.json':
            return self.send(200, (ROOT/'data/activity_kit.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/two-love.json':
            return self.send(200, (ROOT/'data/two_love.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/magic-card.json':
            return self.send(200, (ROOT/'data/magic_card.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/wish.json':
            return self.send(200, (ROOT/'data/wish.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/ev-sand.json':
            return self.send(200, (ROOT/'data/ev_sand.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/dropbox-80001.json':
            rows = [r for r in json.loads((ROOT/'data/dropbox.json').read_text()).values() if int(r['dropbox_id']) == 80001 and int(r['weight']) > 0]
            return self.send(200, rows)
        if path == '/assets/astral.json':
            return self.send(200, (ROOT/'data/astral.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/partner-return.json':
            return self.send(200, (ROOT/'data/partner_return.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/resonate.json':
            return self.send(200, (ROOT/'data/resonate.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/potentials.json':
            return self.send(200, (ROOT/'data/potentials.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/house-exam.json':
            return self.send(200, (ROOT/'data/house_exam.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/shops.json':
            return self.send(200, (ROOT/'data/shops.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/relations.json':
            return self.send(200, (ROOT/'data/relations.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/servants.json':
            return self.send(200, (ROOT/'data/servants.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/campaign.json':
            return self.send(200, (ROOT/'data/campaign.json').read_bytes(), 'application/json; charset=utf-8')
        if path == '/assets/pictures.json':
            f = ROOT/'data/pictures.json'
            return self.send(200, f.read_bytes() if f.exists() else b'[]', 'application/json')
        if path == '/assets/lihui.json':
            return self.send(200, (ROOT/'data/lihui.json').read_bytes(), 'application/json')
        if path == '/assets/equipment/catalog.json':
            return self.send(200, (ROOT/'data/equipment.json').read_bytes(), 'application/json; charset=utf-8')
        if path.startswith('/assets/equipment/') and path.endswith('.png'):
            stem = path[len('/assets/equipment/'):-4]
            if stem in EQUIP_ASSETS:
                return self.send(200, (ROOT/'web/assets/equipment'/f'{stem}.png').read_bytes(), 'image/png')
        if path == '/api/partners/power':
            return self.send(200, self.engine.partners_power())
        if path.startswith('/api/partner/') and path.endswith('/attrs'):
            try: return self.send(200, self.engine.partner_attributes(int(path.split('/')[3])))
            except (ValueError, GameError) as exc: return self.send(404, {'error': str(exc)})
        if path == '/assets/events/catalog.json':
            return self.send(200, (ROOT/'data/events.json').read_bytes(), 'application/json; charset=utf-8')
        if path.startswith('/assets/events/') and path.endswith('.png'):
            stem = path[len('/assets/events/'):-4]
            if stem in EVENT_ASSETS:
                return self.send(200, (ROOT/'web/assets/events'/f'{stem}.png').read_bytes(), 'image/png')
        if path.startswith('/api/battle/'):
            try: return self.send(200, self.engine.get_battle(int(path.rsplit('/', 1)[-1])))
            except (ValueError, GameError): return self.send(404, {'error': 'Không tìm thấy trận đấu'})
        if path.startswith('/assets/img-guides/'):
            filename = path.rsplit('/', 1)[-1]
            folder = ROOT/'web/assets/img-guides'
            if path == '/assets/img-guides/'+filename and filename in {p.name for p in folder.iterdir() if p.suffix in ('.png', '.json')}:
                return self.send(200, (folder/filename).read_bytes(), 'application/json; charset=utf-8' if filename.endswith('.json') else 'image/png')
        files = {'/lobby-dialogue.js':('lobby-dialogue.js','application/javascript; charset=utf-8'),'/lobby-dialogue.css':('lobby-dialogue.css','text/css; charset=utf-8'),'/admin.js':('admin.js','application/javascript; charset=utf-8'),'/admin.css':('admin.css','text/css; charset=utf-8'),'/payment.js':('payment.js','application/javascript; charset=utf-8'),'/payment.css':('payment.css','text/css; charset=utf-8'),'/mail.js':('mail.js','application/javascript; charset=utf-8'),'/mail.css':('mail.css','text/css; charset=utf-8'),'/auth.js':('auth.js','application/javascript; charset=utf-8'),'/auth.css':('auth.css','text/css; charset=utf-8'),'/online-hub.js':('online-hub.js','application/javascript; charset=utf-8'),'/online-hub.css':('online-hub.css','text/css; charset=utf-8'),'/localization.js':('localization.js','application/javascript; charset=utf-8'),'/i18n-vi.js':('i18n-vi.js','application/javascript; charset=utf-8'),'/hero-glow.js':('hero-glow.js','application/javascript; charset=utf-8'),'/hero-glow.css':('hero-glow.css','text/css; charset=utf-8'),'/img-guides.js':('img-guides.js','application/javascript; charset=utf-8'),'/img-guides.css':('img-guides.css','text/css; charset=utf-8'),'/graduate.css':('graduate.css','text/css'), '/firework-project.js':('firework-project.js','application/javascript'), '/firework-project.css':('firework-project.css','text/css'), '/arena3v3.js':('arena3v3.js','application/javascript'), '/arena3v3.css':('arena3v3.css','text/css'), '/settings-menu.js':('settings-menu.js','application/javascript'), '/settings-menu.css':('settings-menu.css','text/css'), '/house-dress.js':('house-dress.js','application/javascript'), '/house-dress.css':('house-dress.css','text/css'), '/guild-lab.js':('guild-lab.js','application/javascript'), '/guild-lab.css':('guild-lab.css','text/css'), '/slots.js': ('slots.js','application/javascript'), '/slots.css': ('slots.css','text/css'), '/home-menus.js': ('home-menus.js', 'application/javascript'), '/home-menus.css': ('home-menus.css', 'text/css'), '/assets/avatars.png': ('assets/avatars.png', 'image/png'), '/assets/avatars.json': ('assets/avatars.json', 'application/json'), '/assets/home-bg.png': ('assets/home-bg.png', 'image/png'), '/assets/home-icons.png': ('assets/home-icons.png', 'image/png'), '/assets/home-icons-alpha.png': ('assets/home-icons-alpha.png', 'image/png'), '/assets/home-icons.json': ('assets/home-icons.json', 'application/json'), '/': ('index.html', 'text/html; charset=utf-8'), '/battle-animation.js': ('battle-animation.js', 'application/javascript'), '/developer.js': ('developer.js', 'application/javascript'), '/campaign-ui.js': ('campaign-ui.js', 'application/javascript; charset=utf-8'), '/campaign-ui.css': ('campaign-ui.css', 'text/css; charset=utf-8'), '/arena.js': ('arena.js', 'application/javascript; charset=utf-8'), '/patrol.js': ('patrol.js', 'application/javascript; charset=utf-8'), '/house-exam.js': ('house-exam.js', 'application/javascript; charset=utf-8'), '/summon-anim.js': ('summon-anim.js', 'application/javascript; charset=utf-8'), '/hero-challenge.js': ('hero-challenge.js', 'application/javascript; charset=utf-8'), '/sanctuary.js': ('sanctuary.js', 'application/javascript; charset=utf-8'), '/internship.js': ('internship.js', 'application/javascript; charset=utf-8'), '/midas.js': ('midas.js', 'application/javascript; charset=utf-8'), '/old-campus.js': ('old-campus.js', 'application/javascript; charset=utf-8'), '/old-campus.css': ('old-campus.css', 'text/css; charset=utf-8'), '/echoes.js': ('echoes.js', 'application/javascript; charset=utf-8'), '/echoes.css': ('echoes.css', 'text/css; charset=utf-8'), '/shrine.js': ('shrine.js', 'application/javascript; charset=utf-8'), '/shrine.css': ('shrine.css', 'text/css; charset=utf-8'), '/galaxy.js': ('galaxy.js', 'application/javascript; charset=utf-8'), '/galaxy.css': ('galaxy.css', 'text/css; charset=utf-8'), '/story.js': ('story.js', 'application/javascript; charset=utf-8'), '/story.css': ('story.css', 'text/css; charset=utf-8'), '/dress.js': ('dress.js', 'application/javascript; charset=utf-8'), '/dress.css': ('dress.css', 'text/css; charset=utf-8'), '/skins.js': ('skins.js', 'application/javascript; charset=utf-8'), '/souls.js': ('souls.js', 'application/javascript; charset=utf-8'), '/souls.css': ('souls.css', 'text/css; charset=utf-8'), '/soul-land.js': ('soul-land.js', 'application/javascript; charset=utf-8'), '/soul-land.css': ('soul-land.css', 'text/css; charset=utf-8'), '/stellar-altar.js': ('stellar-altar.js', 'application/javascript; charset=utf-8'), '/stellar-altar.css': ('stellar-altar.css', 'text/css; charset=utf-8'), '/quick-formation.js': ('quick-formation.js', 'application/javascript; charset=utf-8'), '/quick-formation.css': ('quick-formation.css', 'text/css; charset=utf-8'), '/skin-collection.js': ('skin-collection.js', 'application/javascript; charset=utf-8'), '/skin-collection.css': ('skin-collection.css', 'text/css; charset=utf-8'), '/profile-senpai.js': ('profile-senpai.js', 'application/javascript; charset=utf-8'), '/story-items.js': ('story-items.js', 'application/javascript; charset=utf-8'), '/game-assistant.js': ('game-assistant.js', 'application/javascript; charset=utf-8'), '/ev-sand.js': ('ev-sand.js', 'application/javascript; charset=utf-8'), '/ev-sand.css': ('ev-sand.css', 'text/css; charset=utf-8'), '/wallpaper.js': ('wallpaper.js', 'application/javascript; charset=utf-8'), '/summon-result.js': ('summon-result.js', 'application/javascript; charset=utf-8'), '/summon-result.css': ('summon-result.css', 'text/css; charset=utf-8'), '/campaign-flow.js': ('campaign-flow.js', 'application/javascript; charset=utf-8'), '/campaign-flow.css': ('campaign-flow.css', 'text/css; charset=utf-8'), '/altar.js': ('altar.js', 'application/javascript; charset=utf-8'), '/altar.css': ('altar.css', 'text/css; charset=utf-8'), '/chimes.js': ('chimes.js', 'application/javascript; charset=utf-8'), '/chimes.css': ('chimes.css', 'text/css; charset=utf-8'), '/pumpkin.js': ('pumpkin.js', 'application/javascript; charset=utf-8'), '/pumpkin.css': ('pumpkin.css', 'text/css; charset=utf-8'), '/lost-space.js': ('lost-space.js', 'application/javascript; charset=utf-8'), '/lost-space.css': ('lost-space.css', 'text/css; charset=utf-8'), '/pirate.js': ('pirate.js', 'application/javascript; charset=utf-8'), '/pirate.css': ('pirate.css', 'text/css; charset=utf-8'), '/puzzle-events.js': ('puzzle-events.js', 'application/javascript; charset=utf-8'), '/puzzle-events.css': ('puzzle-events.css', 'text/css; charset=utf-8'), '/blind-box.js': ('blind-box.js', 'application/javascript; charset=utf-8'), '/blind-box.css': ('blind-box.css', 'text/css; charset=utf-8'), '/jackpot.js': ('jackpot.js', 'application/javascript; charset=utf-8'), '/jackpot.css': ('jackpot.css', 'text/css; charset=utf-8'), '/guild.js': ('guild.js', 'application/javascript; charset=utf-8'), '/guild.css': ('guild.css', 'text/css; charset=utf-8'), '/act-kit.js': ('act-kit.js', 'application/javascript; charset=utf-8'), '/act-kit.css': ('act-kit.css', 'text/css; charset=utf-8'), '/two-love.js': ('two-love.js', 'application/javascript; charset=utf-8'), '/two-love.css': ('two-love.css', 'text/css; charset=utf-8'), '/magic-card.js': ('magic-card.js', 'application/javascript; charset=utf-8'), '/magic-card.css': ('magic-card.css', 'text/css; charset=utf-8'), '/wish.js': ('wish.js', 'application/javascript; charset=utf-8'), '/wish.css': ('wish.css', 'text/css; charset=utf-8'), '/dress-show.js': ('dress-show.js', 'application/javascript; charset=utf-8'), '/dress-show.css': ('dress-show.css', 'text/css; charset=utf-8'), '/skins.css': ('skins.css', 'text/css; charset=utf-8'), '/internship.css': ('internship.css', 'text/css; charset=utf-8'), '/sanctuary.css': ('sanctuary.css', 'text/css; charset=utf-8'), '/hero-challenge.css': ('hero-challenge.css', 'text/css; charset=utf-8'), '/summon-anim.css': ('summon-anim.css', 'text/css; charset=utf-8'), '/house-exam.css': ('house-exam.css', 'text/css; charset=utf-8'), '/patrol.css': ('patrol.css', 'text/css; charset=utf-8'), '/arena.css': ('arena.css', 'text/css; charset=utf-8'), '/shops.js': ('shops.js', 'application/javascript; charset=utf-8'), '/shops.css': ('shops.css', 'text/css; charset=utf-8'), '/missions.js': ('missions.js', 'application/javascript; charset=utf-8'), '/missions.css': ('missions.css', 'text/css; charset=utf-8'), '/dates.js': ('dates.js', 'application/javascript; charset=utf-8'), '/station.js': ('station.js', 'application/javascript; charset=utf-8'), '/bots.js': ('bots.js', 'application/javascript; charset=utf-8'), '/bots.css': ('bots.css', 'text/css; charset=utf-8'), '/remaining-systems.js': ('remaining-systems.js','application/javascript; charset=utf-8'), '/newbie-camp.js': ('newbie-camp.js', 'application/javascript; charset=utf-8'), '/growth-diary.js': ('growth-diary.js', 'application/javascript; charset=utf-8'), '/growth-diary.css': ('growth-diary.css', 'text/css; charset=utf-8'), '/fantasy-book.js': ('fantasy-book.js', 'application/javascript; charset=utf-8'), '/fantasy-book.css': ('fantasy-book.css', 'text/css; charset=utf-8'), '/station.css': ('station.css', 'text/css; charset=utf-8'), '/dates.css': ('dates.css', 'text/css; charset=utf-8'), '/excursion.js': ('excursion.js', 'application/javascript; charset=utf-8'), '/excursion.css': ('excursion.css', 'text/css; charset=utf-8'), '/servant.js': ('servant.js', 'application/javascript; charset=utf-8'), '/servant.css': ('servant.css', 'text/css; charset=utf-8'), '/frame.js': ('frame.js', 'application/javascript; charset=utf-8'), '/frame.css': ('frame.css', 'text/css; charset=utf-8'), '/enroll.js': ('enroll.js', 'application/javascript; charset=utf-8'), '/enroll.css': ('enroll.css', 'text/css; charset=utf-8'), '/campaign-map.js': ('campaign-map.js', 'application/javascript; charset=utf-8'), '/campaign-map.css': ('campaign-map.css', 'text/css; charset=utf-8'), '/girl-ui.js': ('girl-ui.js', 'application/javascript; charset=utf-8'), '/girl-ui.css': ('girl-ui.css', 'text/css; charset=utf-8'), '/equipment.js': ('equipment.js', 'application/javascript; charset=utf-8'), '/equipment.css': ('equipment.css', 'text/css; charset=utf-8'), '/events.js': ('events.js', 'application/javascript; charset=utf-8'), '/events.css': ('events.css', 'text/css; charset=utf-8'), '/app.js': ('app.js', 'application/javascript; charset=utf-8'), '/style.css': ('style.css', 'text/css; charset=utf-8'),'/assets/stage-lock.png': ('assets/stage-lock.png', 'image/png'), '/assets/stage-check.png': ('assets/stage-check.png', 'image/png')}
        for character in (41001, 42001, 43001):
            files[f'/assets/hero-{character}.png'] = (f'assets/hero-{character}.png', 'image/png')
        if path in files:
            filename, mime = files[path]
            return self.send(200, (ROOT/'web'/filename).read_bytes(), mime)
        # Root-level JS/CSS are public client assets. Files added after the
        # manual registry should not become 404s, but nothing outside web/
        # (including nested paths and server configuration) is exposed.
        if path.startswith('/') and path.count('/') == 1:
            filename = path[1:]
            suffix = Path(filename).suffix.lower()
            mime = {'.js': 'application/javascript; charset=utf-8',
                    '.css': 'text/css; charset=utf-8'}.get(suffix)
            if mime and filename and not filename.startswith('.'):
                static_file = ROOT / 'web' / filename
                if static_file.is_file():
                    return self.send(200, static_file.read_bytes(), mime)
        return self.send(404, {'error': 'Đường dẫn không tồn tại'})
    def bootstrap(self):
        ctx = self.auth_context()
        account = ctx['account'] if ctx else {'uid': 'local-player-1', 'server_id': 'S1'}
        return {'uid': account['uid'], 'player_id': 1, 'token': LOCAL_TOKEN, 'server_id': account['server_id'],
                'gate_host': '127.0.0.1', 'gate_port': self.server.tcp_port, 'is_new': 0,
                'server_time': int(time.time()), 'log_url': f'http://localhost:{self.server.server_port}/local-log'}
    def read_body(self):
        length = int(self.headers.get('Content-Length', '0'))
        if not 0 <= length <= 1024*1024: raise GameError('Dữ liệu gửi lên quá lớn')
        raw = self.rfile.read(length)
        content_type = self.headers.get('Content-Type', '')
        if content_type.startswith('application/json'):
            data = json.loads(raw)
        elif content_type.startswith('application/x-www-form-urlencoded'):
            values = parse_qs(raw.decode())
            data = json.loads(values.get('payload', ['{}'])[0])
        elif content_type.startswith('multipart/form-data'):
            message = BytesParser(policy=default).parsebytes(('Content-Type: '+content_type+'\r\nMIME-Version: 1.0\r\n\r\n').encode()+raw)
            payload = next((part.get_payload(decode=True) for part in message.iter_parts() if part.get_param('name', header='content-disposition') == 'payload'), b'{}')
            data = json.loads(payload)
        else: raise GameError('Định dạng dữ liệu không được hỗ trợ')
        if not isinstance(data, dict): raise GameError('Dữ liệu yêu cầu phải là đối tượng JSON')
        return data
    def do_POST(self):
        if self.reject_unauthorized_admin_mode():
            return
        origin = self.headers.get('Origin')
        host = self.headers.get('Host', f'localhost:{self.server.server_port}')
        allowed = {f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}',
                   f'http://{host}', f'https://{host}'}
        if getattr(self.server, 'public_origin', ''):
            allowed.add(self.server.public_origin.rstrip('/'))
        if origin and origin not in allowed: return self.send(403, {'error': 'Nguồn truy cập không được phép'})
        try:
            data = self.read_body()
            path = urlparse(self.path).path
            if path == '/api/auth/register' and not self.rate_limit('auth_register'): return
            if path == '/api/auth/login' and not self.rate_limit('auth_login'): return
            if path == '/api/auth/reset-password' and not self.rate_limit('auth_reset'): return
            if path == '/api/auth/recovery-code' and not self.rate_limit('recovery_rotate'): return
            if path == '/api/order/create' and not self.rate_limit('order_create'): return
            if path == '/api/pvp/queue' and not self.rate_limit('pvp_queue'): return
            if path in ('/api/pvp/match/battle','/api/guild-war/battle') and not self.rate_limit('battle'): return
            if path.startswith('/api/admin/') and not self.rate_limit('admin'): return
            if path == '/api/giftcode/redeem' and not self.rate_limit('giftcode_redeem'): return
            if path == '/api/giftcode/sso/exchange' and not self.rate_limit('auth_login'): return
            if path == '/api/giftcode/admin/unlock' and not self.rate_limit('giftcode_unlock'): return
            if path.startswith('/api/owner-security/') and not self.rate_limit('giftcode_unlock'): return
            if path.startswith('/api/giftcode/admin/') and not self.rate_limit('admin'): return
            if path == '/api/skin-shop/bank/create' and not self.rate_limit('order_create'): return
            if path in ('/api/giftskin/verify','/api/giftskin/crystal','/api/giftskin/bank/create') and not self.rate_limit('order_create'): return
            if path == '/api/giftskin/admin/review' and not self.rate_limit('admin'): return
            if path.startswith('/api/skin-shop/admin/') and not self.rate_limit('admin'): return
            if path == '/api/world-guild/manage' and str(data.get('action') or '') == 'chat' and not self.rate_limit('guild_chat'): return
            if path == '/api/chat/send' and not self.rate_limit('world_chat'): return
            if path in ('/api/auth/register','/api/auth/login'):
                if path.endswith('/register'):
                    result = auth.register(data.get('username'), data.get('password'), data.get('character_name'),
                                           data.get('server_id','S1'), data.get('email',''),
                                           self.headers.get('User-Agent',''), self.client_ip())
                else:
                    result = auth.login(data.get('username'), data.get('password'), data.get('server_id','S1'),
                                        self.client_ip(), self.headers.get('User-Agent',''))
                secure = self.request_is_https()
                cookie = f"gxb3_session={result['token']}; Path=/; HttpOnly; SameSite=Lax"
                # "Lưu đăng nhập" persists an opaque HttpOnly cookie only when selected.
                # Otherwise it is a browser-session cookie; the password is never stored.
                if path.endswith('/login') and data.get('remember_login') is True:
                    cookie += f"; Max-Age={auth.SESSION_TTL}"
                if secure: cookie += '; Secure'
                body = {'account': result['account'], 'character_name': result['character_name'], 'session_id': result.get('session_id')}
                if result.get('recovery_code'): body['recovery_code'] = result['recovery_code']
                return self.send(200, body, headers={'Set-Cookie': cookie})
            if path == '/api/auth/reset-password':
                return self.send(200, auth.reset_password(data.get('username'), data.get('recovery_code'), data.get('new_password')))
            if path == '/api/auth/recovery-code':
                ctx = self.require_auth()
                if not ctx: return
                return self.send(200, auth.rotate_recovery_code(self.session_token()))
            if path == '/api/auth/session/revoke':
                ctx = self.require_auth()
                if not ctx: return
                target = str(data.get('session_id') or '')
                current_sessions = auth.sessions_for_token(self.session_token())
                is_current = any(x.get('session_id') == target and x.get('current') for x in current_sessions)
                result = auth.revoke_session(self.session_token(), target)
                headers = {'Set-Cookie': 'gxb3_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0'} if is_current else None
                return self.send(200, result, headers=headers)
            if path == '/api/auth/logout':
                auth.logout(self.session_token())
                self._auth_context = None
                return self.send(200, {'ok': True}, headers={'Set-Cookie': 'gxb3_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0'})
            if path == '/api/auth/switch-server':
                ctx = self.require_auth()
                if not ctx: return
                updated = auth.switch_server(self.session_token(), data.get('server_id'))
                self._auth_context = updated
                return self.send(200, {'session': updated})
            if path == '/api/auth/create-character':
                ctx = self.require_auth()
                if not ctx: return
                updated = auth.create_character(self.session_token(), data.get('server_id'), data.get('character_name'))
                self._auth_context = updated
                return self.send(200, {'session': updated})
            if path == '/api/giftcode/sso/exchange':
                token=studio_sso.exchange(data.get('ticket'),self.headers.get('User-Agent',''),self.client_ip())
                cookie=f"gxb3_session={token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age={auth.SESSION_TTL}"
                return self.send(200,{'authenticated':True},headers={'Set-Cookie':cookie})
            if not self.require_auth():
                return
            if path == '/api/chat/send':
                ctx = self.auth_context()
                account = ctx['account']
                return self.send(200, {
                    'message': live_service.send_chat_message(
                        account['uid'], account['server_id'],
                        data.get('channel'), data.get('message'), data.get('recipient_uid', ''))
                })
            if path.startswith('/api/owner-security/'):
                if not self.is_super_gm():
                    return self.send(403,{'error':'Chỉ chủ tài khoản SUPER GM được khôi phục khóa'})
                token = self.session_token()
                if path == '/api/owner-security/enroll/start':
                    return self.send(200,owner_recovery.enrollment_start(token,{
                        'admin':data.get('admin_key'),'panel':data.get('panel_key'),
                        'gm':data.get('gm_key')}))
                if path == '/api/owner-security/enroll/confirm':
                    return self.send(200,owner_recovery.enrollment_confirm(token,data.get('code')))
                if path == '/api/owner-security/keys/reset':
                    return self.send(200,owner_recovery.reset_keys(token,data.get('code'),{
                        'admin':data.get('admin_key'),'panel':data.get('panel_key'),
                        'gm':data.get('gm_key')}))
                if path == '/api/owner-security/backups/rotate':
                    return self.send(200,owner_recovery.rotate_backups(token,data.get('code')))
                return self.send(404,{'error':'API khôi phục không tồn tại'})
            if path == '/api/giftcode/admin/unlock':
                if not self.admin_authorized(): return self.send(403,{'error':'Yêu cầu SUPER GM'})
                return self.send(200,{'access':studio_sso.unlock(data.get('password'),self.session_token(),data.get('admin_key'),data.get('gm_key')),'expires_in':studio_sso.PANEL_TTL})
            if path == '/api/inventory/options':
                return self.send(200, self.engine.bag_use_options(data.get('item_id')))
            if path == '/api/inventory/use':
                return self.send(200, self.engine.use_bag_item(
                    data.get('item_id'), data.get('reward_id'), data.get('count', 1)))
            if path == '/api/giftskin/verify':
                a=self.auth_context()['account']
                return self.send(200,skin_gifts.view_recipient(
                    a['uid'],data.get('recipient_uid'),data.get('recipient_name'),data.get('recipient_server')))
            if path == '/api/giftskin/crystal':
                return self.send(200,self.engine.gift_skin_crystal(data))
            if path == '/api/giftskin/bank/create':
                a=self.auth_context()['account']
                return self.send(200,skin_gifts.create_bank(
                    a['uid'],a['server_id'],data.get('recipient_uid'),
                    data.get('recipient_name'),data.get('recipient_server'),data.get('skin_id')))
            if path == '/api/giftskin/admin/review':
                if not self.admin_authorized(): return self.send(403,{'error':'Chỉ SUPER GM được duyệt GiftSkin'})
                if not studio_sso.authorized(self.headers.get('X-GXB3-Giftcode-Access'),self.session_token()):
                    return self.send(403,{'error':'Vui lòng mở khóa quản trị'})
                if not self.gm_key_authorized(): return self.send(403,{'error':'Khóa hành động QTV không hợp lệ'})
                return self.send(200,skin_gifts.review(data.get('order_id'),data.get('approve'),
                    self.auth_context()['account']['uid']))
            if path == '/api/skin-shop/bank/create':
                account=self.auth_context()['account']
                return self.send(200,skin_bank.create(account['uid'],account['server_id'],
                    self.auth_context()['character_name'],data.get('skin_id')))
            if path == '/api/giftcode/redeem':
                ctx=self.auth_context()
                account=ctx['account']
                return self.send(200,giftcodes.redeem(data.get('code'),account['uid'],account['server_id']))
            if path.startswith('/api/skin-shop/admin/'):
                if not self.admin_authorized():
                    return self.send(403,{'error':'Chỉ SUPER GM được chỉnh cửa hàng Skin'})
                if not studio_sso.authorized(self.headers.get('X-GXB3-Giftcode-Access'),self.session_token()):
                    return self.send(403,{'error':'Vui lòng mở khóa bảng quản trị'})
                if not self.gm_key_authorized():
                    return self.send(403,{'error':'Khóa hành động QTV không hợp lệ'})
                if path == '/api/skin-shop/admin/bank/review':
                    return self.send(200,skin_bank.review(data.get('order_id'),data.get('approve'),
                        self.auth_context()['account']['uid']))
                if path == '/api/skin-shop/admin/update':
                    return self.send(200,skin_store.update_configs([data],self.auth_context()['account']['uid']))
                if path == '/api/skin-shop/admin/bulk':
                    return self.send(200,skin_store.update_configs(data.get('changes'),self.auth_context()['account']['uid']))
                return self.send(404,{'error':'Không tìm thấy thao tác quản lý skin'})
            if path.startswith('/api/giftcode/admin/'):
                if not self.admin_authorized(): return self.send(403,{'error':'Chỉ SUPER GM được tạo mã'})
                if not studio_sso.authorized(self.headers.get('X-GXB3-Giftcode-Access'),self.session_token()):
                    return self.send(403,{'error':'Vui lòng mở khóa mục Tạo Giftcode'})
                if not self.gm_key_authorized(): return self.send(403,{'error':'Khóa hành động QTV không hợp lệ'})
                operator=self.auth_context()['account']['uid']
                if path == '/api/giftcode/admin/create':
                    return self.send(200,giftcodes.create(data,operator))
                if path == '/api/giftcode/admin/revoke':
                    return self.send(200,giftcodes.revoke(data.get('code'),operator))
                return self.send(404,{'error':'Đường dẫn giftcode không tồn tại'})
            if path == '/api/admin/check':
                if not self.admin_authorized():
                    return self.send(403, {'error': 'QTV_KEY_INVALID'})
                return self.send(200, {'ok': True})
            if path == '/api/admin/config':
                if not self.admin_authorized():
                    return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
                if data.get('action') == 'reset':
                    return self.send(200, local_config.reset())
                return self.send(200, local_config.save(data))
            if path == '/api/admin/world':
                if not self.admin_authorized(): return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
                if data.get('action') == 'create':
                    return self.send(200, live_service.create_world(data.get('server_id'), data.get('name')))
                if data.get('action') == 'status':
                    return self.send(200, live_service.set_world_status(str(data.get('server_id') or '').upper(), data.get('status')))
                if data.get('action') == 'policy':
                    return self.send(200, live_service.set_world_policy(
                        str(data.get('server_id') or '').upper(),
                        data.get('registration_open'), data.get('character_creation_open'), data.get('message')))
                raise ValueError('Thao tác server không hợp lệ')
            if path == '/api/admin/account/sessions':
                if not self.admin_authorized(): return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
                return self.send(200, {'sessions': auth.account_sessions(data.get('uid'))})
            if path == '/api/admin/account/revoke-sessions':
                if not self.admin_authorized(): return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
                return self.send(200, auth.revoke_account_sessions(data.get('uid')))
            if path == '/api/admin/account/status':
                if not self.admin_authorized(): return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
                action = data.get('action')
                if action not in ('ban','unban'): raise ValueError('Thao tác tài khoản không hợp lệ')
                return self.send(200, auth.set_account_status(data.get('uid'), action == 'ban', data.get('reason','')))
            if path == '/api/admin/player/status':
                if not self.admin_authorized(): return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
                action = data.get('action')
                if action not in ('ban','unban'): raise ValueError('Thao tác tài khoản không hợp lệ')
                return self.send(200, live_service.set_ban(data.get('uid'), data.get('server_id'), action == 'ban', data.get('reason','')))
            if path == '/api/admin/topup-packages':
                if not self.admin_authorized(): return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
                if not self.gm_key_authorized(): return self.send(403, {'error': 'Khóa QTV không chính xác hoặc chưa cấu hình trên VPS'})
                action=str(data.get('action') or 'save')
                if action=='reset':
                    cfg=topup.reset()
                elif action=='save':
                    cfg=topup.save(data.get('config') or {})
                else:
                    raise ValueError('Thao tác Top-up Package không hợp lệ')
                db=live_service._db()
                live_service._audit(db,'admin.topup_packages','GLOBAL',{'action':action,'packages':len(cfg.get('packages') or [])},'SUPER_GM')
                db.commit();db.close()
                return self.send(200,cfg)
            if path == '/api/admin/world-config':
                if not self.admin_authorized(): return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
                server_id=str(data.get('server_id') or 'S1').upper()
                action=str(data.get('action') or 'save')
                if action=='reset':
                    cfg=world_live_config.reset(server_id)
                elif action=='save':
                    cfg=world_live_config.save(server_id,data.get('config') or {})
                else:
                    raise ValueError('Thao tác World Live Config không hợp lệ')
                db=live_service._db()
                live_service._audit(db,'admin.world_live_config',server_id,{'action':action,'config':cfg},'SUPER_GM')
                db.commit();db.close()
                return self.send(200,{'server_id':server_id,'config':cfg})
            if path == '/api/admin/live-service':
                if not self.admin_authorized(): return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
                action=str(data.get('action') or '')
                if action=='pvp_rating':
                    return self.send(200,live_service.admin_set_pvp_rating(
                        data.get('uid'),data.get('server_id'),data.get('mode','arena'),data.get('rating'),
                        data.get('season_id') or None,'SUPER_GM'))
                if action=='guild_progress':
                    return self.send(200,live_service.admin_add_guild_progress(
                        data.get('uid'),data.get('server_id'),data.get('exp_gain',0),data.get('contribution_gain',0),'SUPER_GM'))
                if action=='force_settle_war':
                    return self.send(200,live_service.admin_force_settle_guild_war(data.get('war_id'),'SUPER_GM'))
                if action=='maintenance':
                    return self.send(200,live_service.maintenance_tick())
                raise ValueError('Thao tác SUPER GM live-service không hợp lệ')
            if path == '/api/admin/gm/verify-key':
                if not self.admin_authorized():
                    return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
                if not os.environ.get('GXB3_GM_ACTION_KEY'):
                    return self.send(503, {'error': 'Khóa hành động QTV chưa được cấu hình trên VPS'})
                if not self.gm_key_authorized():
                    return self.send(403, {'error': 'Khóa QTV không chính xác'})
                return self.send(200, {'verified': True})
            if path == '/api/admin/mail/send':
                if not self.admin_authorized(): return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
                if not self.gm_key_authorized(): return self.send(403, {'error': 'Khóa QTV không chính xác hoặc chưa cấu hình trên VPS'})
                # Item IDs and quantities are validated server-side; client icons or names grant no authority.
                gift = gm_catalog.validate_gift(data.get('attachments') or {})
                return self.send(200, live_service.send_mail(data.get('uid'), data.get('server_id'), data.get('character_name'),
                    data.get('title'), data.get('body'), gift, 'SUPER_GM'))
            if path == '/api/admin/order/review':
                if not self.admin_authorized(): return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
                if not self.gm_key_authorized(): return self.send(403, {'error': 'Khóa QTV không chính xác hoặc chưa cấu hình trên VPS'})
                action = data.get('action')
                if action not in ('approve','reject'): raise ValueError('Thao tác đơn hàng không hợp lệ')
                return self.send(200, live_service.review_order(data.get('order_id'), action == 'approve', data.get('reward') or {}, 'SUPER_GM'))
            if path == '/api/guild-war/battle':
                ctx=self.auth_context(); account=ctx['account']
                war_id=str(data.get('war_id') or '')
                defender_uid=str(data.get('defender_uid') or '')
                prep=live_service.prepare_guild_war_attack(account['uid'],account['server_id'],war_id,defender_uid)
                attacker=prep['attacker']; defender=prep['defender']
                engine_a=self.server.player_engines.get(account['uid'],account['server_id'],attacker['character_name'])
                engine_b=self.server.player_engines.get(defender_uid,account['server_id'],defender['character_name'])
                snap_a=engine_a.pvp_team_snapshot(); snap_b=engine_b.pvp_team_snapshot()
                seed=normalize_online_seed(int.from_bytes(hashlib.sha256(f"{war_id}:{account['uid']}:{defender_uid}".encode()).digest()[:4],'big'))
                report=simulate_battle(
                    snap_a['team'],snap_b['team'],battle_id=ONLINE_BATTLE_ID,seed=seed,
                    pet_a=snap_a.get('pet'),pet_b=snap_b.get('pet'),
                    guild_skills_a=snap_a.get('guild_skills') or [],
                    guild_skills_b=snap_b.get('guild_skills') or [],
                    chime_bonus_a=snap_a.get('chime_bonus') or [],
                    chime_bonus_b=snap_b.get('chime_bonus') or [],
                    battle_type=1,
                )
                result=live_service.record_guild_war_battle(war_id,account['uid'],defender_uid,snap_a,snap_b,report)
                return self.send(200,{'result':result,'detail':live_service.guild_war_detail(account['uid'],account['server_id'],war_id)})
            if path == '/api/guild-war/settle':
                ctx=self.auth_context(); account=ctx['account']
                detail=live_service.guild_war_detail(account['uid'],account['server_id'],data.get('war_id'))
                if detail['war']['status']!='finished':
                    raise ValueError('Guild War chưa kết thúc')
                return self.send(200,{'war':live_service.settle_guild_war(data.get('war_id'))})
            if path == '/api/world-guild/manage':
                ctx = self.auth_context(); account = ctx['account']; player = ctx['player']
                current = self.engine.snapshot(); power = int(current.get('power',0))
                action = str(data.get('action') or '')
                if action == 'apply':
                    result = live_service.apply_world_guild(account['uid'], account['server_id'], player['character_name'],
                                                            data.get('guild_id'), power)
                elif action == 'review':
                    result = live_service.review_guild_application(account['uid'], account['server_id'],
                                                                   data.get('target_uid'), bool(data.get('approve')))
                elif action == 'role':
                    result = live_service.set_guild_role(account['uid'], account['server_id'],
                                                         data.get('target_uid'), data.get('role'))
                elif action == 'kick':
                    result = live_service.kick_guild_member(account['uid'], account['server_id'], data.get('target_uid'))
                elif action == 'transfer':
                    result = live_service.transfer_guild_leader(account['uid'], account['server_id'], data.get('target_uid'))
                elif action == 'notice':
                    result = live_service.update_world_guild(account['uid'], account['server_id'], data.get('notice'))
                elif action == 'chat':
                    result = live_service.send_guild_chat(account['uid'], account['server_id'], player['character_name'], data.get('message'))
                elif action == 'mail':
                    result = live_service.send_guild_mail(account['uid'], account['server_id'], data.get('title'), data.get('body'))
                elif action == 'war':
                    result = live_service.schedule_guild_war(account['uid'], account['server_id'], data.get('opponent_guild_id'), data.get('duration',86400))
                else:
                    raise ValueError('Thao tác quản trị Guild không hợp lệ')
                return self.send(200, {'result': result,
                                       'guild': live_service.guild_for_player(account['uid'], account['server_id']),
                                       'guilds': live_service.world_guilds(account['server_id']),
                                       'ranking': live_service.guild_ranking(account['server_id'], 100),
                                       'wars': live_service.guild_wars(account['server_id'], 50)})
            if path == '/api/world-guild/action':
                ctx = self.auth_context(); account = ctx['account']; player = ctx['player']
                current = self.engine.snapshot()
                power = int(current.get('power', 0)); action = str(data.get('action') or '')
                if action == 'create':
                    result = live_service.create_world_guild(account['uid'], account['server_id'], player['character_name'],
                                                             data.get('name'), data.get('notice',''), power)
                elif action == 'join':
                    result = live_service.apply_world_guild(account['uid'], account['server_id'], player['character_name'],
                                                            data.get('guild_id'), power)
                elif action == 'leave':
                    result = live_service.leave_world_guild(account['uid'], account['server_id'])
                else:
                    raise ValueError('Thao tác Guild không hợp lệ')
                return self.send(200, {'result': result,
                                       'guild': live_service.guild_for_player(account['uid'], account['server_id']),
                                       'guilds': live_service.world_guilds(account['server_id'])})
            if path == '/api/pvp/season/claim':
                ctx = self.auth_context(); account = ctx['account']; player = ctx['player']
                return self.send(200, live_service.claim_pvp_season_reward(
                    account['uid'], account['server_id'], player['character_name'], data.get('mode','arena')))
            if path == '/api/pvp/queue':
                ctx = self.auth_context(); account = ctx['account']; player = ctx['player']
                current = self.engine.snapshot()
                action = str(data.get('action') or 'join')
                mode = str(data.get('mode') or 'arena')
                if action == 'join':
                    result = live_service.enqueue_pvp(account['uid'], account['server_id'], player['character_name'],
                                                      mode, int(current.get('power',0)))
                elif action == 'cancel':
                    result = live_service.cancel_pvp(account['uid'], account['server_id'], mode)
                else:
                    raise ValueError('Thao tác hàng chờ PvP không hợp lệ')
                return self.send(200, result)
            if path == '/api/pvp/match/activate':
                ctx = self.auth_context(); account = ctx['account']
                return self.send(200, {'match': live_service.activate_pvp_match(data.get('match_id'), account['uid'])})
            if path == '/api/pvp/match/heartbeat':
                ctx = self.auth_context(); account = ctx['account']
                return self.send(200, live_service.heartbeat_pvp_match(data.get('match_id'), account['uid'], data.get('ready', True)))
            if path == '/api/pvp/match/session':
                ctx = self.auth_context(); account = ctx['account']
                return self.send(200, live_service.pvp_match_session(data.get('match_id'), account['uid']))
            if path == '/api/pvp/match/battle':
                ctx = self.auth_context(); account = ctx['account']
                session = live_service.pvp_match_session(data.get('match_id'), account['uid'])
                match = live_service.pvp_match_internal(data.get('match_id'), account['uid'])
                if match.get('status') == 'finished':
                    return self.send(200, {'result': live_service.pvp_match_result(match['id'], account['uid'])})
                server_a = str(match.get('server_a') or match.get('server_id') or '').upper()
                server_b = str(match.get('server_b') or match.get('server_id') or '').upper()
                if server_a in ('', 'CROSS') or server_b in ('', 'CROSS'):
                    raise ValueError('Match cũ thiếu thông tin server; hãy ghép trận mới')
                pa = live_service.player(match['player_a'], server_a)
                pb = live_service.player(match['player_b'], server_b)
                if not pa or not pb:
                    raise ValueError('Không thể tải hồ sơ một trong hai người chơi')
                engine_a = self.server.player_engines.get(match['player_a'], server_a, pa['character_name'])
                engine_b = self.server.player_engines.get(match['player_b'], server_b, pb['character_name'])
                snap_a = engine_a.pvp_team_snapshot()
                snap_b = engine_b.pvp_team_snapshot()
                ready = live_service.heartbeat_pvp_match(match['id'], account['uid'], True)
                if ready['match'].get('status') != 'active':
                    return self.send(409, {'error': 'Đang chờ đối thủ sẵn sàng', 'session': ready})
                report = simulate_battle(
                    snap_a['team'], snap_b['team'],
                    battle_id=ONLINE_BATTLE_ID,
                    seed=normalize_online_seed(int(match.get('seed') or 1)),
                    pet_a=snap_a.get('pet'), pet_b=snap_b.get('pet'),
                    guild_skills_a=snap_a.get('guild_skills') or [],
                    guild_skills_b=snap_b.get('guild_skills') or [],
                    chime_bonus_a=snap_a.get('chime_bonus') or [],
                    chime_bonus_b=snap_b.get('chime_bonus') or [],
                    battle_type=1,
                )
                result = live_service.finish_authoritative_pvp(match['id'], account['uid'], snap_a, snap_b, report)
                return self.send(200, {'result': result})
            if path == '/api/pvp/match/result':
                ctx = self.auth_context(); account = ctx['account']
                return self.send(200, {'result': live_service.pvp_match_result(data.get('match_id'), account['uid'])})
            if path == '/api/order/create':
                state = self.engine.snapshot()
                return self.send(200, live_service.create_order(state.get('uid'), state.get('server_id'), state.get('name'), data.get('package'), data.get('note','')))
            if path == '/api/mail/claim':
                return self.send(200, self.engine.claim_live_mail(data.get('mail_id')))
            if self.headers.get('X-GXB2-Mode') != 'developer':
                account_state = self.engine.snapshot()
                if account_state.get('account_status') == 'banned':
                    return self.send(403, {'error': 'Tài khoản đã bị khóa bởi GM'})
            if path == '/api/v1':
                if data.get('mid') != 1 or data.get('local_mode') is not True:
                    raise GameError('Este endpoint acepta solo RETRIEVE_TOKEN con local_mode=true')
                return self.send(200, {'payload': self.bootstrap()})
            if path == '/api/action':
                name = data.get('message')
                allowed_actions = {'GUILD_GET_SKILLS','GUILD_UPGRADE_SKILL','GUILD_RESET_SKILL','MAP_FIGHT', 'PARTNER_LEVUP', 'SET_HANG_TEAM', 'STAGE_HANG', 'SUMMON', 'COMPOSE_PARTNER', 'AWAKE_PARTNER', 'PARTNER_GRADEUP', 'UPGRADE_PARTNER_EX_SKILL', 'CHOOSE_PARTNER_POTENTIAL', 'REPLACE_10_STAR', 'ROLLBACK_PARTNER', 'DECOMPOSE_PARTNERS', 'UPGRADE_STAR_ORIGIN', 'RESET_STAR_ORIGIN', 'PROPHET_REPLACE', 'PROPHET_REPLACE_SAVE', 'GAMBLE_GET_INFO', 'GAMBLE_GET_AWARD', 'GAMBLE_REFRESH', 'LOCK_PARTNER', 'GET_SHOP_INFO', 'REFRESH_SHOP', 'BUY_SHOP_ITEM'}
                if name not in allowed_actions: raise GameError('Acción no disponible')
                request = data.get('data', {})
                if not isinstance(request, dict): raise GameError('Datos inválidos')
                packets = self.engine.handle(name, request)
                return self.send(200, {'state': self.engine.snapshot(), 'messages': [{'id': mid, 'type': typ, 'data': body} for mid, typ, body in packets]})
            if path == '/api/developer':
                if not self.admin_authorized():
                    return self.send(403, {'error': 'QTV_KEY_REQUIRED'})
                return self.send(200, {'state': self.engine.developer_action(data, super_gm=True)})
            if path == '/api/home/action':
                return self.send(200, self.engine.home_action(data))
            if path == '/api/dress-show/action':
                return self.send(200, self.engine.dress_show_action(data))
            if path == '/api/campaign/hang-team':
                return self.send(200, self.engine.set_campaign_hang(data))
            if path == '/api/altar/preview':
                return self.send(200, self.engine.altar_preview(data))
            if path == '/api/chimes/action':
                return self.send(200, self.engine.chimes_action(data))
            if path == '/api/pumpkin/action':
                return self.send(200, self.engine.pumpkin_action(data))
            if path == '/api/relations/plot':
                from gxb2 import relations as _rel
                return self.send(200, {'lines': _rel.plot_scene(int(data.get('plot', 0) or 0)), 'title': _rel.PLOT['titles'].get(str(data.get('plot', 0)), '')})
            if path == '/api/arena3v3/action':
                return self.send(200, self.engine.arena3v3_action(data))
            if path in ('/api/friend-boss/action','/api/pet-training/action','/api/practical-work/action'):
                return self.send(200, self.engine.remaining_system_action(path.split('/')[2],data))
            if path == '/api/newbie-camp/action':
                return self.send(200, self.engine.newbie_camp_action(data))
            if path == '/api/growth-diary/action':
                return self.send(200, self.engine.growth_diary_action(data))
            if path == '/api/hearts/action':
                return self.send(200, self.engine.hearts_action(data))
            if path == '/api/fantasy-book/action':
                return self.send(200, self.engine.fantasy_book_action(data))
            if path == '/api/collection/action':
                return self.send(200, self.engine.collection_action(data))
            if path == '/api/lost-space/action':
                return self.send(200, self.engine.lost_space_action(data))
            if path == '/api/pirate/action':
                return self.send(200, self.engine.pirate_action(data))
            if path == '/api/firework-project/action':
                return self.send(200, self.engine.firework_project_action(data))
            if path == '/api/puzzle-events/action':
                return self.send(200, self.engine.puzzle_events_action(data))
            if path == '/api/blind-box/action':
                return self.send(200, self.engine.blind_box_action(data))
            if path == '/api/jackpot/action':
                return self.send(200, self.engine.jackpot_action(data))
            if path == '/api/act-draw/action':
                return self.send(200, self.engine.act_draw_action(data))
            if path == '/api/guild/action':
                return self.send(200, self.engine.guild_action(data))
            if path == '/api/act-kit/action':
                return self.send(200, self.engine.act_kit_action(data))
            if path == '/api/two-love/action':
                return self.send(200, self.engine.two_love_action(data))
            if path == '/api/magic-card/action':
                return self.send(200, self.engine.magic_card_action(data))
            if path == '/api/wish/action':
                return self.send(200, self.engine.wish_action(data))
            if path == '/api/events/sand':
                return self.send(200, self.engine.ev_sand_action(data))
            if path == '/api/assistant/run':
                return self.send(200, self.engine.assistant_run(data))
            if path == '/api/quick-formation/action':
                return self.send(200, self.engine.quick_formation_action(data))
            if path == '/api/stellar-altar/action':
                return self.send(200, self.engine.stellar_altar_action(data))
            if path == '/api/soul-land/action':
                return self.send(200, self.engine.soul_land_action(data))
            if path == '/api/souls/action':
                return self.send(200, self.engine.souls_action(data))
            if path == '/api/souls/catalog':
                return self.send(200, souls_catalog())
            if path == '/api/skin-shop/catalog':
                return self.send(200,skin_store.catalogue())
            if path == '/api/skins/action':
                return self.send(200, self.engine.skins_action(data))
            if path == '/api/graduate/preview':
                return self.send(200, self.engine.graduate_preview(int(data.get('partner_id', 0)), int(data.get('target_id', 0))))
            if path == '/api/skins/catalog':
                return self.send(200, skins_catalog())
            if path == '/api/dress/action':
                return self.send(200, self.engine.dress_action(data))
            if path == '/api/dress/catalog':
                return self.send(200, dress_catalog())
            if path == '/api/story/action':
                return self.send(200, self.engine.story_action(data))
            if path == '/api/story/scene':
                return self.send(200, self.engine.story_scene(data.get('plot', 0)))
            if path == '/api/story/stage':
                return self.send(200, self.engine.story_stage(data.get('stage', 0)))
            if path == '/api/story/catalog':
                return self.send(200, story_catalog())
            if path == '/api/galaxy/action':
                return self.send(200, self.engine.galaxy_action(data))
            if path == '/api/shrine/action':
                return self.send(200, self.engine.shrine_action(data))
            if path == '/api/shrine/story':
                return self.send(200, self.engine.shrine_story(data.get('text_id', 1)))
            if path == '/api/echoes/action':
                return self.send(200, self.engine.echoes_action(data))
            if path == '/api/old-campus/action':
                return self.send(200, self.engine.old_campus_action(data))
            if path == '/api/midas/action':
                return self.send(200, self.engine.midas_action(data))
            if path == '/api/house-dress/action':
                return self.send(200, self.engine.house_dress_action(data))
            if path == '/api/internship/action':
                return self.send(200, self.engine.internship_action(data))
            if path == '/api/sanctuary/action':
                return self.send(200, self.engine.sanctuary_action(data))
            if path == '/api/hero-challenge/action':
                return self.send(200, self.engine.hero_challenge_action(data))
            if path == '/api/house-exam/action':
                return self.send(200, self.engine.house_exam_action(data))
            if path == '/api/patrol/action':
                return self.send(200, self.engine.patrol_action(data))
            if path == '/api/arena/action':
                return self.send(200, self.engine.arena_action(data))
            if path == '/api/shops/action':
                return self.send(200, self.engine.shops_action(data))
            if path == '/api/missions/action':
                return self.send(200, self.engine.missions_action(data))
            if path == '/api/relations/action':
                return self.send(200, self.engine.relations_action(data))
            if path == '/api/explore/action':
                return self.send(200, self.engine.explore_action(data))
            if path == '/api/campaign/action':
                return self.send(200, self.engine.campaign_action(data))
            if path == '/api/equipment/action':
                return self.send(200, self.engine.equipment_action(data))
            if path == '/api/events/action':
                return self.send(200, self.engine.events_action(data))
            if path == '/api/profile':
                return self.send(200, {'state': self.engine.update_profile(data)})
            if path == '/api/daily-quiz/fight':
                return self.send(200, self.engine.run_daily_quiz(data))
            if path == '/api/daily-quiz/sweep':
                return self.send(200, self.engine.run_daily_quiz(data, sweep=True))
            if path == '/api/tower/fight':
                return self.send(200, self.engine.run_tower(data))
            return self.send(404, {'error': 'Đường dẫn không tồn tại'})
        except (ValueError, KeyError) as exc: return self.send(400, {'error': str(exc)})
        except Exception as exc:
            print(f'Error local: {type(exc).__name__}: {exc}', flush=True)
            return self.send(500, {'error': 'Máy chủ gặp lỗi xử lý. Vui lòng thử lại sau hoặc liên hệ QTV.'})

def make_servers(engine, http_port=9080, tcp_port=9081, developer_engine=None, player_engines=None,
                 http_host='127.0.0.1', public_origin='', admin_key=None, trust_proxy=None):
    tcp = ThreadTCP(('127.0.0.1', tcp_port), TCPHandler)
    tcp.engine = engine
    try: http = LocalHTTPServer((http_host, http_port), HTTPHandler)
    except Exception:
        tcp.server_close()
        raise
    http.developer_engine = developer_engine
    http.player_engines = player_engines or PlayerEnginePool()
    http.admin_key = str(ADMIN_KEY if admin_key is None else admin_key).strip()
    http.public_origin = str(public_origin or '').strip().rstrip('/')
    http.trust_proxy = env_bool('GXB3_TRUST_PROXY',False) if trust_proxy is None else bool(trust_proxy)
    http.rate_limiter = FixedWindowRateLimiter()
    http.engine = engine; http.tcp_port = tcp.server_address[1]
    return http, tcp

def maintenance_loop(stop_event):
    while not stop_event.wait(30):
        try:
            live_service.maintenance_tick()
        except Exception as exc:
            print(f'GXB3 maintenance: {type(exc).__name__}: {exc}', flush=True)


def main():
    parser = argparse.ArgumentParser(description='Backend local GxB2: combate original, perfil ficticio y guardado local')
    parser.add_argument('--http-port', type=int, default=int(os.environ.get('PORT', '9080')))
    parser.add_argument('--http-host', default=os.environ.get('GXB3_HOST', '127.0.0.1'))
    parser.add_argument('--public-origin', default=os.environ.get('GXB3_PUBLIC_ORIGIN', ''))
    parser.add_argument('--tcp-port', type=int, default=9081)
    parser.add_argument('--db', type=Path, default=ROOT/'state/profile.sqlite3')
    parser.add_argument('--open', action='store_true', help='Abrir la interfaz local de prueba')
    args = parser.parse_args()
    warnings=validate_production_config(
        http_host=args.http_host,
        public_origin=args.public_origin,
        admin_key=ADMIN_KEY,
        database_url=(os.environ.get('GXB3_DATABASE_URL') or os.environ.get('DATABASE_URL') or ''),
    )
    for warning in warnings: print('GXB3 WARNING: '+warning,flush=True)
    if env_bool('GXB3_PRODUCTION',False):
        proof=run_startup_preflight()
        print(f"GXB3 production preflight PASS: db={proof['database']} battle_frames={proof['battle_frames']} rounds={proof['battle_rounds']}",flush=True)
    engine = Engine(args.db)
    developer = Engine(args.db.with_name(args.db.stem + ".developer.sqlite3"), developer=True)
    player_engines = PlayerEnginePool()
    http, tcp = make_servers(engine, args.http_port, args.tcp_port, developer, player_engines,
                             args.http_host, args.public_origin)
    stop_event=threading.Event()
    threads = [threading.Thread(target=s.serve_forever, daemon=True) for s in (http, tcp)]
    threads.append(threading.Thread(target=maintenance_loop,args=(stop_event,),daemon=True))
    for thread in threads: thread.start()
    browse_host = 'localhost' if args.http_host in ('0.0.0.0','::') else args.http_host
    url = f'http://{browse_host}:{http.server_port}'
    public_note = args.public_origin or '(chưa cấu hình)'
    admin_note='đã bật từ GXB3_ADMIN_KEY' if http.admin_key else 'đang tắt (chưa có GXB3_ADMIN_KEY)'
    print(f'GXB 3 server sẵn sàng: {url}\nHTTP bind: {args.http_host}:{http.server_port}\nPublic origin: {public_note}\nSocket legacy: 127.0.0.1:{tcp.server_address[1]}\nQTV: {admin_note}.\nCtrl+C để dừng.', flush=True)
    if args.open:
        import webbrowser
        webbrowser.open(url)
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: pass
    finally:
        stop_event.set()
        for s in (http, tcp): s.shutdown(); s.server_close()
        engine.close()
        developer.close()
        player_engines.close()
        database.close_pool()

if __name__ == '__main__': main()
