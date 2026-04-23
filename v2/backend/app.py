# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime

import requests
from flask import Flask, Response, request


def json_utf8(payload, status: int = 200):
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return Response(body, status=status, content_type="application/json; charset=utf-8")


app = Flask(__name__)

API_KEY = (os.environ.get("API_SPORTS_KEY") or "").strip()
API_HOST = "v3.football.api-sports.io"
FIXTURES_URL = f"https://{API_HOST}/fixtures"

HOT_LEAGUES = [
    {"id": 39, "name": "\u82f1\u8d85"},
    {"id": 140, "name": "\u897f\u7532"},
    {"id": 135, "name": "\u610f\u7532"},
    {"id": 78, "name": "\u5fb7\u7532"},
    {"id": 61, "name": "\u6cd5\u7532"},
    {"id": 2, "name": "\u6b27\u51a0"},
    {"id": 98, "name": "\u65e5\u804c\u8054"},
    {"id": 99, "name": "\u65e5\u804c\u4e59"},
    {"id": 79, "name": "\u5fb7\u4e59"},
    {"id": 62, "name": "\u6cd5\u4e59"},
    {"id": 188, "name": "\u6fb3\u8d85"},
    {"id": 71, "name": "\u5df4\u7532"},
    {"id": 1, "name": "\u4e16\u754c\u676f"},
]


def api_headers():
    return {"x-apisports-key": API_KEY, "x-rapidapi-host": API_HOST}


def status_to_cn(short: str):
    mapping = {
        "NS": "\u672a\u5f00\u8d5b",
        "1H": "\u4e0a\u534a\u573a",
        "HT": "\u4e2d\u573a",
        "2H": "\u4e0b\u534a\u573a",
        "FT": "\u5b8c\u573a",
        "AET": "\u52a0\u65f6\u5b8c",
        "PEN": "\u70b9\u7403\u5b8c",
        "PST": "\u63a8\u8fdf",
        "CANC": "\u53d6\u6d88",
        "ABD": "\u4e2d\u65ad",
        "SUSP": "\u6682\u505c",
    }
    return mapping.get(short, short or "")


@app.get("/api/health")
def health():
    return json_utf8(
        {
            "ok": True,
            "now": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "msg": "\u4e2d\u6587\u6d4b\u8bd5\uff1a\u82f1\u8d85/\u897f\u7532/\u610f\u7532",
        }
    )


@app.get("/api/leagues/hot")
def leagues_hot():
    return json_utf8({"leagues": HOT_LEAGUES})


@app.get("/api/fixtures")
def fixtures():
    if not API_KEY:
        return json_utf8({"error": "missing API_SPORTS_KEY"}, status=500)

    date_str = (request.args.get("date") or datetime.now().strftime("%Y-%m-%d")).strip()
    league_raw = (request.args.get("league") or "").strip()
    status = (request.args.get("status") or "all").strip().lower()
    if status not in {"all", "live", "ns", "ft"}:
        return json_utf8({"error": "invalid status"}, status=400)

    params = {"date": date_str, "timezone": "Asia/Shanghai"}
    if league_raw:
        try:
            params["league"] = int(league_raw)
        except ValueError:
            return json_utf8({"error": "invalid league"}, status=400)

    resp = requests.get(FIXTURES_URL, headers=api_headers(), params=params, timeout=20)
    if resp.status_code >= 400:
        return json_utf8({"error": f"upstream {resp.status_code}", "body": resp.text[:500]}, status=502)

    data = resp.json()
    raw = data.get("response", [])

    hot_ids = {x["id"] for x in HOT_LEAGUES}
    out = []
    for item in raw:
        f = item.get("fixture") or {}
        teams = item.get("teams") or {}
        league = item.get("league") or {}
        goals = item.get("goals") or {}
        st = (f.get("status") or {})
        short = st.get("short")

        lid = league.get("id")
        if lid not in hot_ids:
            continue

        if status == "live" and short not in {"1H", "2H", "HT"}:
            continue
        if status == "ns" and short != "NS":
            continue
        if status == "ft" and short not in {"FT", "AET", "PEN"}:
            continue

        out.append(
            {
                "id": f.get("id"),
                "league": {"id": lid, "name": next((x["name"] for x in HOT_LEAGUES if x["id"] == lid), str(league.get("name") or ""))},
                "kickoffTime": (f.get("date") or "").replace("T", " ")[:16],
                "status": {"code": short, "text": status_to_cn(short), "minute": st.get("elapsed")},
                "home": {"name": (teams.get("home") or {}).get("name"), "logo": (teams.get("home") or {}).get("logo")},
                "away": {"name": (teams.get("away") or {}).get("name"), "logo": (teams.get("away") or {}).get("logo")},
                "score": {"home": goals.get("home"), "away": goals.get("away")},
            }
        )

    out.sort(key=lambda x: x.get("kickoffTime") or "")
    return json_utf8({"date": date_str, "timezone": "Asia/Shanghai", "fixtures": out})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)

