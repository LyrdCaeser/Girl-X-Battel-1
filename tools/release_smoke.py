#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import ssl
import urllib.error
import urllib.request


def request(opener, base, path, method="GET", payload=None):
    data=None
    headers={"Accept":"application/json","User-Agent":"GXB3-Release-Smoke/1.0"}
    if payload is not None:
        data=json.dumps(payload).encode("utf-8")
        headers["Content-Type"]="application/json"
    req=urllib.request.Request(base.rstrip("/")+path,data=data,headers=headers,method=method)
    try:
        with opener.open(req,timeout=15) as response:
            raw=response.read()
            return response.status,json.loads(raw.decode("utf-8")) if raw else {}
    except urllib.error.HTTPError as exc:
        raw=exc.read()
        try: body=json.loads(raw.decode("utf-8"))
        except Exception: body={"raw":raw.decode("utf-8","replace")}
        raise RuntimeError(f"{method} {path} -> HTTP {exc.code}: {body}") from exc


def main():
    parser=argparse.ArgumentParser(description="Smoke-test a deployed GXB 3 server without changing gameplay data")
    parser.add_argument("--base-url",default=os.environ.get("GXB3_SMOKE_URL",""))
    parser.add_argument("--username",default=os.environ.get("GXB3_SMOKE_USERNAME",""))
    parser.add_argument("--password",default=os.environ.get("GXB3_SMOKE_PASSWORD",""))
    parser.add_argument("--server-id",default=os.environ.get("GXB3_SMOKE_SERVER","S1"))
    args=parser.parse_args()
    if not args.base_url.startswith("https://"):
        raise SystemExit("FAIL: smoke test production yêu cầu --base-url HTTPS.")

    jar=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    status,health=request(opener,args.base_url,"/healthz")
    if status!=200 or not health.get("ok"): raise SystemExit("FAIL healthz")
    print("OK healthz",health)

    status,ready=request(opener,args.base_url,"/readyz")
    if status!=200 or not ready.get("ready"): raise SystemExit("FAIL readyz")
    print("OK readyz",ready)

    status,packages=request(opener,args.base_url,"/api/payment/packages")
    print("OK public payment catalog")

    if not args.username or not args.password:
        print("SKIP authenticated smoke: set GXB3_SMOKE_USERNAME/GXB3_SMOKE_PASSWORD.")
        return

    _,login=request(opener,args.base_url,"/api/auth/login","POST",{
        "username":args.username,"password":args.password,"server_id":args.server_id,
    })
    print("OK login",login.get("account",{}).get("uid",""))

    _,me=request(opener,args.base_url,"/api/auth/me")
    if not me.get("authenticated"): raise SystemExit("FAIL auth/me")
    print("OK authenticated session")

    _,ranking=request(opener,args.base_url,f"/api/leaderboard?server_id={args.server_id}&limit=5")
    print("OK leaderboard rows=",len(ranking.get("ranking") or []))

    _,guild=request(opener,args.base_url,"/api/world-guild")
    print("OK guild endpoint member=",bool(guild.get("guild")))

    request(opener,args.base_url,"/api/auth/logout","POST",{})
    print("OK logout")
    print("PASS release smoke.")


if __name__=="__main__":
    main()
