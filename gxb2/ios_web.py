"""Dedicated iOS web-app entrance. Device hints are not hardware attestation."""
import hashlib
import hmac
import re
import secrets
import time

ORIGIN = 'https://goddessbattle3-ios.vercel.app'
PREFIX = '/ios-gateway'
COOKIE = 'gxb_ios_launch'
KEY = secrets.token_bytes(32)
TTL = 86400 * 7

def candidate(ua):
    return bool(re.search(r'iPhone|iPad|iPod|Macintosh', ua or '', re.I) and
                not re.search(r'Android|Windows|CrOS', ua or '', re.I))

def mint(ua):
    stamp = str(int(time.time()) + TTL)
    sig = hmac.new(KEY, (stamp+'|'+ua).encode(), hashlib.sha256).hexdigest()
    return stamp+'.'+sig

def valid(ua, token):
    try:
        stamp, sig = token.split('.', 1)
        if not int(time.time()) < int(stamp) <= int(time.time()) + TTL: return False
        expected = hmac.new(KEY, (stamp+'|'+ua).encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected)
    except (ValueError, AttributeError, TypeError): return False
