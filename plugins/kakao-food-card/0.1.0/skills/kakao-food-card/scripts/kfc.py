#!/usr/bin/env python3
"""kakao-food-card 데이터 수집·사진·빌드 도구.

사용법 (WORK = 작업 폴더, 스크래치패드 하위 권장):
  kfc.py fetch   WORK "가게명1" "가게명2" ... [--region 부천]
  kfc.py photos  WORK [--n 4] [--ids id1,id2] [--src food|all|blog]
  kfc.py digest  WORK                                # 리뷰 요약 작성용 다이제스트 재출력
  kfc.py sheet   WORK [--ids id1,id2] [--dir cand-food]  # 후보 사진 컨택트시트(sheet-*.jpg)
  kfc.py pick    WORK ID 경로1 경로2 ...              # 대표사진 순서 확정 → site/img/ID-k.jpg
  kfc.py build   WORK                                # data.json + meta.json → site/index.html

WORK 구조:
  raw/ID.json, raw/ID-reviews.json   카카오 원본
  data.json                          카드 데이터(Claude가 section·sum·pros·cons 채움)
  meta.json                          {title, subtitle, note, sections:[{key,label,sub,tone}]}
  cand-{food,all,blog}/ID-k.jpg      사진 후보
  site/index.html, site/img/         게시용
"""
import glob
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

UA = "Mozilla/5.0"
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "template.html")


def get_json(url, ref):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": ref, "pf": "web"})
    return json.load(urllib.request.urlopen(req, timeout=20))


def get_bytes(url):
    url = url.replace("http://", "https://", 1)
    ref = "https://blog.naver.com/" if "pstatic" in url else "https://place.map.kakao.com/"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": ref})
    return urllib.request.urlopen(req, timeout=20).read()


def place_api(path):
    return get_json("https://place-api.map.kakao.com/" + path, "https://place.map.kakao.com/")


def fetch(work, names, region):
    os.makedirs(f"{work}/raw", exist_ok=True)
    rows = load(work, "data.json", [])
    known = {r["id"] for r in rows}
    for n in names:
        q = f"{n} {region}".strip()
        s = get_json("https://search.map.kakao.com/mapsearch/map.daum?msFlag=A&sort=0&q=" + urllib.parse.quote(q),
                     "https://map.kakao.com/")
        cands = [x for x in s.get("place", []) if not region or region in x["address"]] or s.get("place", [])
        if not cands:
            print("NOT FOUND", n)
            continue
        p = cands[0]
        cid = p["confirmid"]
        panel = place_api(f"places/panel3/{cid}")
        reviews = []
        for order in ("LATEST", "RECOMMENDED"):
            j = place_api(f"places/tab/reviews/kakaomap/{cid}?order={order}&only_photo_review=false")
            for r in j.get("reviews", []):
                if r["review_id"] not in {x["review_id"] for x in reviews}:
                    reviews.append(r)
        json.dump({"search": p, "panel": panel}, open(f"{work}/raw/{cid}.json", "w"), ensure_ascii=False)
        json.dump(reviews, open(f"{work}/raw/{cid}-reviews.json", "w"), ensure_ascii=False)
        if cid not in known:
            rows.append(normalize(panel))
            known.add(cid)
        print(n, "→", cid, p["name"], p["address"])
        time.sleep(1)
    save(work, "data.json", rows)
    digest(work)


def normalize(d):
    s = d["summary"]
    sub = (d.get("find_way") or {}).get("subway") or {}
    sc = (d.get("kakaomap_review") or {}).get("score_set") or {}
    desc = {x["id"]: x["name"] for x in (d.get("kakaomap_review") or {}).get("strength_description", [])}
    am = d.get("ai_mate") or {}
    tr = d.get("trend_rank") or {}
    wk = ((d.get("open_hours") or {}).get("week_from_today") or {}).get("week_periods", [{}])[0].get("days", [])
    return {
        "id": s["confirm_id"], "name": s["name"], "cat": s["category"].get("name"), "section": "",
        "rating": sc.get("average_score"), "rc": sc.get("review_count", 0),
        "blog": (d.get("blog_review") or {}).get("review_count", 0),
        "st": sub.get("station_simple_name"), "line": (sub.get("subway_list") or [{}])[0].get("subway_line_icon_name"),
        "exit": sub.get("exit_num"), "m": sub.get("to_exit_minute"), "dist": sub.get("to_exit_distance"),
        "ai": (am.get("summary") or {}).get("title", ""), "tags": (am.get("summary") or {}).get("contents", []),
        "price": (am.get("price_level") or {}).get("symbol"),
        "badge": tr.get("display_text"), "rank": (tr.get("menu_rank") or {}).get("rank"),
        "str": [(desc.get(x["id"], "?"), x["count"]) for x in sc.get("strength_counts", [])][:3],
        "menu": [{"n": x["name"], "p": x.get("price")} for x in (d.get("menu") or {}).get("menus", {}).get("items", [])[:3]],
        "hours": [(x["day_of_the_week_desc"].split("(")[0], (x.get("on_days") or {}).get("start_end_time_desc") or "휴무") for x in wk],
        "addr": s["address"].get("road"), "imgs": [],
        "sum": "", "pros": [], "cons": [],
    }


def digest(work):
    """요약 작성용 다이제스트를 출력한다."""
    for r in load(work, "data.json", []):
        d = json.load(open(f"{work}/raw/{r['id']}.json"))["panel"]
        revs = json.load(open(f"{work}/raw/{r['id']}-reviews.json"))
        stars = [x["star_rating"] for x in revs]
        am = d.get("ai_mate") or {}
        print(f"\n===== {r['name']} ({r['id']}) ★{r['rating']} ({r['rc']}) 배지={r['badge']} 역={r['st']} {r['m']}분")
        print("AI요약:", (am.get("bottom_sheet") or {}).get("summary"))
        print("블로그키워드:", [(x["title"], x["keywords"]) for x in am.get("blog_summaries", [])])
        print("별점분포:", {k: stars.count(k) for k in range(1, 6)}, "리뷰월:", sorted({x["registered_at"][:7] for x in revs})[-5:])
        for x in revs[:15]:
            c = re.sub(r"\s+", " ", x.get("contents", "")).strip()
            if c:
                print(f"  {x['star_rating']} {x['registered_at'][:7]} {c[:120]}")
        for b in (d.get("blog_review") or {}).get("reviews", [])[:3]:
            print("  B", b["title"][:80])


def photos(work, n, ids, src):
    folder = f"cand-{src}"
    os.makedirs(f"{work}/{folder}", exist_ok=True)
    for r in load(work, "data.json", []):
        if ids and r["id"] not in ids:
            continue
        d = json.load(open(f"{work}/raw/{r['id']}.json"))["panel"]
        if src == "blog":
            urls = [p["url"] for b in (d.get("blog_review") or {}).get("reviews", []) for p in b.get("photos", [])]
        else:
            tag = "&tag=FOOD" if src == "food" else ""
            urls = []
            for pg in (1, 2):
                j = place_api(f"places/tab/photos/{r['id']}?page={pg}{tag}")
                urls += [p["url"] for p in j.get("photos", []) if p.get("media_type", "PHOTO") == "PHOTO" and "thumb.kakaocdn.net/dna" not in p["url"]]
                if not j.get("has_next"):
                    break
        for f in glob.glob(f"{work}/{folder}/{r['id']}-*.jpg"):
            os.remove(f)
        got = 0
        for u in urls:
            try:
                b = get_bytes(u)
            except Exception:
                continue
            if len(b) < 15000:  # 아이콘·깨진 이미지 제외
                continue
            open(f"{work}/{folder}/{r['id']}-{got}.jpg", "wb").write(b)
            got += 1
            if got >= n:
                break
        print(r["name"], src, len(urls), "→", got)


def sheet(work, ids, folder):
    from PIL import Image, ImageDraw  # 시스템 python3 (-I 없이) 에 PIL 있음
    rows = [r for r in load(work, "data.json", []) if not ids or r["id"] in ids]
    W, H, C = 200, 150, 8
    groups = [(r, sorted(glob.glob(f"{work}/{folder}/{r['id']}-*.jpg"), key=lambda p: int(p.rsplit("-", 1)[1][:-4]))) for r in rows]
    nrow = sum(max(1, -(-len(g) // C)) for _, g in groups)
    im = Image.new("RGB", (W * C, H * nrow), "white")
    y = 0
    for r, g in groups:
        for k, p in enumerate(g):
            t = Image.open(p).convert("RGB")
            t.thumbnail((W, H))
            x, yy = (k % C) * W, y + (k // C) * H
            im.paste(t, (x, yy))
            ImageDraw.Draw(im).text((x + 3, yy + 3), f"{r['id']}-{k}", fill="red")
        y += max(1, -(-len(g) // C)) * H
    out = f"{work}/sheet-{folder}.jpg"
    im.save(out, quality=70)
    print(out)


def pick(work, cid, paths):
    os.makedirs(f"{work}/site/img", exist_ok=True)
    rows = load(work, "data.json", [])
    imgs = []
    for k, p in enumerate(paths):
        p = p if os.path.isabs(p) else f"{work}/{p}"
        out = f"{work}/site/img/{cid}-{k}.jpg"
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "70", "-Z", "900", p, "--out", out], capture_output=True, check=True)
        imgs.append(f"img/{cid}-{k}.jpg")
    for r in rows:
        if r["id"] == cid:
            r["imgs"] = imgs
    save(work, "data.json", rows)
    print(cid, imgs)


def build(work):
    rows = load(work, "data.json", [])
    meta = load(work, "meta.json", None)
    keys = {s["key"] for s in meta["sections"]}
    bad = [r["name"] for r in rows if r["section"] not in keys or not r["imgs"] or not r["sum"]]
    if bad:
        sys.exit(f"미완성(section/imgs/sum): {bad}")
    t = open(TEMPLATE).read()
    t = t.replace("__TITLE__", meta["title"]).replace("__META__", json.dumps(meta, ensure_ascii=False))
    t = t.replace("__DATA__", json.dumps(rows, ensure_ascii=False))
    open(f"{work}/site/index.html", "w").write(t)
    files = sorted("img/" + f for f in os.listdir(f"{work}/site/img"))
    print(json.dumps(files))


def load(work, name, default):
    p = f"{work}/{name}"
    return json.load(open(p)) if os.path.exists(p) else default


def save(work, name, obj):
    json.dump(obj, open(f"{work}/{name}", "w"), ensure_ascii=False, indent=1)


def opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        v = args[i + 1]
        del args[i:i + 2]
        return v
    return default


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd, work = a[0], os.path.abspath(a[1])
    rest = a[2:]
    region = opt(rest, "--region", "")
    n = int(opt(rest, "--n", "4"))
    ids = [x for x in (opt(rest, "--ids", "") or "").split(",") if x]
    src = opt(rest, "--src", "food")
    folder = opt(rest, "--dir", "cand-food")
    os.makedirs(work, exist_ok=True)
    if cmd == "fetch":
        fetch(work, rest, region)
    elif cmd == "digest":
        digest(work)
    elif cmd == "photos":
        photos(work, n, ids, src)
    elif cmd == "sheet":
        sheet(work, ids, folder)
    elif cmd == "pick":
        pick(work, rest[0], rest[1:])
    elif cmd == "build":
        build(work)
    else:
        sys.exit(__doc__)
