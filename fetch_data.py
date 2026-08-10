"""
被 GitHub Actions 定时调用，抓取最新数据后写入 data.json。
逻辑和之前 generate_calendar_report.py 里的 build_data 完全一样，
只是这里输出的是纯数据文件，不掺HTML。
"""

import json
import requests
from datetime import date, timedelta, datetime, timezone

NAME_A = "郑艺彬"
NAME_B = "叶筱玮"

BASE = "https://y.saoju.net/yyj/api"
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})


def find_artist_pks(name, artists):
    return [a["pk"] for a in artists if a["fields"]["name"] == name]


def musical_ids_for_artist(artist_pks, musicalcasts, roles):
    role_ids = {mc["fields"]["role"] for mc in musicalcasts if mc["fields"]["artist"] in artist_pks}
    return {r["fields"]["musical"] for r in roles if r["pk"] in role_ids}


def fetch_shows_for_musical(musical_obj, end_date_str):
    name = musical_obj["fields"]["name"]
    begin_date = musical_obj["fields"].get("premiere_date") or "2010-01-01"
    url = (f"{BASE}/search_musical_show/"
           f"?musical={requests.utils.quote(name)}&begin_date={begin_date}&end_date={end_date_str}")
    resp = session.get(url, timeout=15)
    resp.raise_for_status()
    shows = resp.json().get("show_list", [])
    for s in shows:
        s["musical"] = name
    return shows


def build_data(name_a, name_b):
    artists = session.get(f"{BASE}/artist/", timeout=15).json()
    musicalcasts = session.get(f"{BASE}/musicalcast/", timeout=15).json()
    roles = session.get(f"{BASE}/role/", timeout=15).json()
    musicals = session.get(f"{BASE}/musical/", timeout=15).json()
    musical_by_pk = {m["pk"]: m for m in musicals}

    pks_a = find_artist_pks(name_a, artists)
    pks_b = find_artist_pks(name_b, artists)
    if not pks_a or not pks_b:
        raise ValueError("有一方没找到，检查名字写法")

    mids_a = musical_ids_for_artist(pks_a, musicalcasts, roles)
    mids_b = musical_ids_for_artist(pks_b, musicalcasts, roles)
    all_mids = mids_a | mids_b

    end_date_str = (date.today() + timedelta(days=365)).isoformat()

    merged = {}
    for mid in all_mids:
        m = musical_by_pk.get(mid)
        if not m:
            continue
        for s in fetch_shows_for_musical(m, end_date_str):
            cast = s.get("cast", [])
            role_a = next((c["role"] for c in cast if c["artist"] == name_a), None)
            role_b = next((c["role"] for c in cast if c["artist"] == name_b), None)
            if not role_a and not role_b:
                continue
            key = (s["musical"], s.get("city"), s.get("theatre"), s.get("time"))
            merged[key] = {
                "musical": s["musical"], "city": s.get("city") or "",
                "theatre": s.get("theatre") or "", "time": s.get("time"),
                "roleA": role_a, "roleB": role_b,
            }

    return sorted(merged.values(), key=lambda r: r["time"])


if __name__ == "__main__":
    rows = build_data(NAME_A, NAME_B)
    output = {
        "name_a": NAME_A,
        "name_b": NAME_B,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "shows": rows,
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"写入 data.json，共 {len(rows)} 场")
