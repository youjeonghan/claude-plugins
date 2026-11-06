#!/usr/bin/env python3
"""kakao-food-card 데이터 수집·판정·사진·빌드 도구.

사용법 (WORK = 작업 폴더, 스크래치패드 하위 권장):
  kfc.py scan    WORK "검색어1" "검색어2" ... [--near 신용산역,삼각지역] [--walk 10] [--area 동이름,..] [--pages 3] [--cafe]
                                                     # 지역 검색 모드: 후보 수집 + 도보 거리 필터 + 평점 관문 → scan.json
  kfc.py fetch   WORK ID|"가게명" ... [--region 부천]   # 패널·리뷰 수집 + 판정 태그 → data.json
  kfc.py tag     WORK                                  # 저장된 원본으로 판정 태그만 다시 계산
  kfc.py blogs   WORK [--ids id1,id2] [--n 8]          # 블로그 후기 수집 + 협찬 판별 → 근거 후보
  kfc.py digest  WORK                                  # 리뷰 요약 작성용 다이제스트 재출력
  kfc.py photos  WORK [--n 4] [--ids id1,id2] [--src food|all|blog]
  kfc.py sheet   WORK [--ids id1,id2] [--dir cand-food]  # 후보 사진 컨택트시트(sheet-*.jpg)
  kfc.py pick    WORK ID 경로1 경로2 ...                # 대표사진 순서 확정 → site/img/ID-k.jpg
  kfc.py build   WORK                                  # data.json + meta.json → site/index.html

WORK 구조:
  scan-search.json, scan.json        지역 검색 원본·관문 결과
  raw/ID.json, raw/ID-reviews.json   카카오 원본(패널·리뷰)
  raw/ID-blogs.json                  블로그 후기 + 협찬 판별
  data.json                          카드 데이터(Claude가 section·sum·pros·cons·ev 채움)
  meta.json                          {title, subtitle, note, day?, sections:[{key,label,sub,tone}]}
  cand-{food,all,blog}/ID-k.jpg      사진 후보
  site/index.html, site/img/         게시용

플랫폼: macOS·Windows 공통. 파일은 항상 UTF-8로 읽고 쓰고(Windows 기본 cp949 회피),
사진 변환(sheet·pick)은 Pillow를 쓴다(macOS에서 Pillow가 없으면 pick만 sips로 대체).
"""
import datetime
import glob
import html
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

# ── 판정 기준 (SKILL.md "판정 기준"과 같은 값) ─────────────────────────────
GATE_RATING = 3.0     # 평점이 보이면 이 점수 이상만 후보
HIDDEN_RANK = 30      # 평점 비공개면: 메뉴 랭킹 이 순위 이내거나
HIDDEN_BLOG = 300     #              블로그 후기 이 건수 이상이거나, 인기 맛집 태그가 있으면 후보
FEW_REVIEWS = 10      # 카카오 리뷰가 이보다 적으면 '리뷰 적음'(제외하지 않음)
SUS_NEW_MAX = 2       # 작성자 리뷰가 이 개수 이하인 계정의 5점 = 의심
SUS_ALL5_MIN = 5      # 작성자 리뷰가 이 개수 이상인데 평균 5.0인 계정의 5점 = 의심
SUS_WINDOW = 7        # 의심 리뷰가 이 일수 안에
SUS_MIN = 3           #   이 건수 이상 몰리면 '리뷰 의심'
RECENT_DAYS = 180     # 최근 리뷰 기준 기간(최근 하락·최근 리뷰 없음)
DROP_GAP = 0.5        # 최근 평균이 전체 평균보다 이만큼 낮으면 '최근 하락'
DROP_MIN = 5          #   최근 리뷰가 이 건수 이상일 때만 판정
REVIEW_PAGES = 3      # 최신순 리뷰를 몇 페이지(페이지당 약 20건) 볼지
WALK_MIN = 10         # scan --near: 지정 역 중 하나에서 이 분 안에 걸어갈 수 있으면 후보
WALK_MPM = 67         #   도보 속도(m/분, 약 4km/h)
DETOUR = 1.25         #   직선거리 → 실제 걷는 거리 보정
CAFE_CATS = {"카페", "간식"}
AD_WORDS = ("원고료", "제공받아", "제공 받아", "제공받았", "제공 받았", "협찬", "체험단", "업체로부터",
            "지원받아", "지원 받아", "광고를 포함", "유료광고", "유료 광고", "소정의", "무상으로 제공", "무료로 제공")
# 협찬 표시가 이미지 배너로만 붙는 체험단 플랫폼(본문 HTML의 이미지·링크 주소로 판별)
AD_HOSTS = ("revu.net", "reviewnote", "dinnerqueen", "gangnam-mat", "seoulouba", "mrblog", "ringble", "tble",
            "reviewplace", "chehumview", "modublog", "storyn", "cometoplay", "assaview", "popomon", "4blog")
BURST_SAME_DAY = 3    # 같은 날 블로그 후기가 이 건수 이상이면 체험단 몰림으로 보고 근거에서 뺀다
TASTE_WORDS = ("맛있", "존맛", "맛집", "또 갈", "또갈", "재방문", "인생", "최고", "강추", "추천")
NEG_WORDS = ("재방문은 안", "다시는 안", "안 갈", "안갈", "실망", "별로", "비추", "아쉬")
NOT_BRANCH = {"주점", "상점", "매점", "정육점"}

# Windows 콘솔·파이프 기본 인코딩(cp949)에서도 리뷰의 한글·이모지 출력이 깨지지 않게 한다.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def rjson(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def wjson(path, obj, **kw):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, **kw)


def pil():
    """Pillow 모듈을 돌려준다. 없으면 None (-I는 사용자 site-packages를 막으므로 sheet·pick은 -I 없이 실행)."""
    try:
        from PIL import Image, ImageDraw, ImageOps
        return Image, ImageDraw, ImageOps
    except ImportError:
        return None


NO_PIL = "Pillow를 찾지 못했어요. -I 없이 실행하거나 `python3 -m pip install --user pillow`(Windows는 python)로 설치하세요."


# ── HTTP ─────────────────────────────────────────────────────────────────
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


def search(q, page=1):
    return get_json(f"https://search.map.kakao.com/mapsearch/map.daum?msFlag=A&sort=0&page={page}&q="
                    + urllib.parse.quote(q), "https://map.kakao.com/")


# ── 공통 추출 ─────────────────────────────────────────────────────────────
def score(panel):
    """(평점 또는 None, 리뷰 수). 리뷰 0건의 0.0점은 평점 없음으로 본다."""
    sc = (panel.get("kakaomap_review") or {}).get("score_set") or {}
    rating, rc = sc.get("average_score"), sc.get("review_count") or 0
    if rating is not None and not rc and not rating:
        rating = None
    return rating, rc


def trend(panel):
    tr = panel.get("trend_rank") or {}
    return tr.get("display_text"), (tr.get("menu_rank") or {}).get("rank")


def blog_count(panel):
    return (panel.get("blog_review") or {}).get("review_count", 0) or 0


def chain_reason(name, srch):
    """체인점이면 이유 문장, 아니면 None. 카카오 프랜차이즈 분류(catetype G) 또는 상호 끝 지점명."""
    if (srch or {}).get("catetype") == "G" and srch.get("last_cate_name"):
        return f"카카오가 프랜차이즈 브랜드 '{srch['last_cate_name']}'로 분류해요."
    m = re.search(r"\s(\S+점)$", name or "")
    if m and m.group(1) not in NOT_BRANCH:
        return f"상호에 지점명 '{m.group(1)}'이 붙어 있어요."
    return None


def gate(rating, badge, rank, blog):
    """(후보 여부, 이유). 평점이 보이면 3.0 이상, 비공개면 인기 신호가 하나라도 있어야 한다."""
    if rating is not None:
        return rating >= GATE_RATING, f"평점 {rating:.1f}"
    why = []
    if badge:
        why.append(f"인기 맛집 태그({badge})")
    if rank and rank <= HIDDEN_RANK:
        why.append(f"메뉴 랭킹 {rank}위")
    if blog >= HIDDEN_BLOG:
        why.append(f"블로그 후기 {blog:,}건")
    return bool(why), (", ".join(why) if why else "평점 없음 + 인기 신호 없음")


def raw_path(work, cid):
    return f"{work}/raw/{cid}.json"


def cached(work, cid):
    p = raw_path(work, cid)
    return rjson(p) if os.path.exists(p) else None


def get_panel(work, cid, srch=None, fresh=False):
    """패널을 raw/ID.json에 캐시한다. 새로 받았으면 True를 함께 돌려준다."""
    c = None if fresh else cached(work, cid)
    if c and c.get("panel"):
        if srch and not c.get("search"):
            c["search"] = srch
            wjson(raw_path(work, cid), c)
        return c, False
    panel = place_api(f"places/panel3/{cid}")
    c = {"search": srch or (c or {}).get("search"), "panel": panel}
    wjson(raw_path(work, cid), c)
    return c, True


# ── scan: 지역 검색 모드 ──────────────────────────────────────────────────
def station_coords(names):
    """역 이름 → (이름, 위도, 경도). 카카오 검색에서 교통·수송 분류의 첫 결과를 쓴다."""
    out = []
    for n in names:
        base = n if n.endswith("역") else n + "역"
        hit = next((p for p in search(base).get("place", [])
                    if p.get("cate_name_depth1") == "교통,수송" and p["name"].startswith(base)), None)
        if not hit:
            sys.exit(f"역을 찾지 못했어요: {n}")
        out.append((base, float(hit["lat"]), float(hit["lon"])))
        time.sleep(1)
    return out


def walk_minutes(lat1, lon1, lat2, lon2):
    """두 좌표 사이 도보 예상 분(직선거리 × 우회 보정 ÷ 도보 속도)."""
    import math
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    meters = 2 * r * math.asin(math.sqrt(a))
    return math.ceil(meters * DETOUR / WALK_MPM)


def nearest(p, stations):
    """가게 검색 항목에서 가장 가까운 지정 역 (역 이름, 도보 분). 좌표가 없으면 None."""
    try:
        lat, lon = float(p["lat"]), float(p["lon"])
    except (KeyError, TypeError, ValueError):
        return None
    return min(((s, walk_minutes(slat, slon, lat, lon)) for s, slat, slon in stations), key=lambda x: x[1])


def scan(work, queries, area, pages, cafe, near, walk):
    """지역 검색 모드. 지역은 --near 역 이름 + --walk 도보 분(권장) 또는 --area 동 이름으로 거른다.
    기준에 없는 이유(쇼핑몰·체인·분위기 등)로는 거르지 않는다 — 체인은 태그로만 표시한다."""
    os.makedirs(f"{work}/raw", exist_ok=True)
    stations = station_coords(near) if near else []
    found = load(work, "scan-search.json", {})
    for q in queries:
        for pg in range(1, pages + 1):
            places = search(q, pg).get("place", [])
            for p in places:
                found.setdefault(p["confirmid"], p)
            time.sleep(1)
            if len(places) < 15:
                break
    save(work, "scan-search.json", found)
    tokens = [t.strip() for t in area.split(",") if t.strip()]
    cands = []
    for p in found.values():
        if p.get("cate_name_depth1") != "음식점" or (not cafe and p.get("cate_name_depth2") in CAFE_CATS):
            continue
        if tokens and not any(t in p.get("address", "") for t in tokens):
            continue
        near_st = nearest(p, stations) if stations else None
        if stations and (near_st is None or near_st[1] > walk):
            continue
        cands.append((p, near_st))
    where = (f"{', '.join(s for s, _, _ in stations)}에서 도보 {walk}분 안" if stations else "") + \
            (f"{' + ' if stations else ''}주소에 {', '.join(tokens)}" if tokens else "")
    print(f"검색 {len(found)}곳 → 음식점{' · ' + where if where else ''} {len(cands)}곳, 패널 확인 중…", flush=True)
    rows = []
    for i, (p, near_st) in enumerate(cands, 1):
        c, new = get_panel(work, p["confirmid"], p)
        if new:
            time.sleep(1.2)
        panel = c["panel"]
        rating, rc = score(panel)
        badge, rank = trend(panel)
        blog = blog_count(panel)
        ok, why = gate(rating, badge, rank, blog)
        sub = (panel.get("find_way") or {}).get("subway") or {}
        rows.append({"id": p["confirmid"], "name": p["name"], "cat": p.get("last_cate_name"),
                     "cat2": p.get("cate_name_depth2"), "rating": rating, "rc": rc, "blog": blog,
                     "badge": badge, "rank": rank, "st": sub.get("station_simple_name"), "m": sub.get("to_exit_minute"),
                     "near": f"{near_st[0]} {near_st[1]}분" if near_st else None,
                     "price": ((panel.get("ai_mate") or {}).get("price_level") or {}).get("symbol"),
                     "chain": bool(chain_reason(p["name"], p)), "pass": ok, "why": why})
        if i % 25 == 0:
            print(f"  {i}/{len(cands)}", flush=True)
    rows.sort(key=lambda r: (not r["pass"], -(r["rating"] or 0), -r["blog"]))
    save(work, "scan.json", rows)
    passed = [r for r in rows if r["pass"]]
    print(f"\n후보 {len(passed)}곳 (관문 탈락 {len(rows) - len(passed)}곳) — scan.json")
    for r in passed:
        rk = f"{r['rank']}위" if r["rank"] else ""
        print("\t".join(str(x) for x in (
            r["id"], r["name"], r["cat"], f"★{r['rating']:.1f}({r['rc']})" if r["rating"] is not None else f"비공개({r['rc']})",
            f"블로그{r['blog']}", (r["badge"] or "-") + (f"/{rk}" if rk else ""),
            r["near"] or f"{r['st']}{r['m']}분",
            r["price"] or "", "체인" if r["chain"] else "", "" if r["rating"] is not None else r["why"])))
    out = [r for r in rows if not r["pass"]]
    if out:
        print("\n탈락:", ", ".join(f"{r['name']}({r['why']})" for r in out))


# ── fetch: 패널·리뷰 + 판정 태그 ──────────────────────────────────────────
def get_reviews(cid):
    reviews, seen = [], set()

    def add(items):
        for r in items:
            if r["review_id"] not in seen:
                seen.add(r["review_id"])
                reviews.append(r)

    last = None
    for _ in range(REVIEW_PAGES):
        q = f"places/tab/reviews/kakaomap/{cid}?order=LATEST&only_photo_review=false"
        j = place_api(q + (f"&previous_last_review_id={last}" if last else ""))
        items = j.get("reviews", [])
        add(items)
        if not j.get("has_next") or not items:
            break
        last = items[-1]["review_id"]
        time.sleep(0.8)
    add(place_api(f"places/tab/reviews/kakaomap/{cid}?order=RECOMMENDED&only_photo_review=false").get("reviews", []))
    return reviews


def resolve(name, region):
    """가게 이름(또는 카카오 장소 ID)을 (ID, 검색 항목)으로 바꾼다."""
    if name.isdigit():
        return name, None
    s = search(f"{name} {region}".strip())
    cands = [x for x in s.get("place", []) if not region or region in x["address"]] or s.get("place", [])
    if not cands:
        return None, None
    return cands[0]["confirmid"], cands[0]


def fetch(work, names, region):
    os.makedirs(f"{work}/raw", exist_ok=True)
    rows = load(work, "data.json", [])
    known = {r["id"] for r in rows}
    scanned = load(work, "scan-search.json", {})
    for n in names:
        cid, srch = resolve(n, region)
        if not cid:
            print("NOT FOUND", n)
            continue
        srch = srch or scanned.get(cid)
        c, _ = get_panel(work, cid, srch, fresh=not n.isdigit())  # 이름으로 찾은 건 새로 받음, ID는 scan 캐시 재사용
        reviews = get_reviews(cid)
        wjson(f"{work}/raw/{cid}-reviews.json", reviews)
        row = normalize(c["panel"])
        row["flags"] = analyze(c["panel"], reviews, c.get("search"))
        if cid in known:
            rows = [dict(r, flags=row["flags"]) if r["id"] == cid else r for r in rows]
        else:
            rows.append(row)
            known.add(cid)
        tags = ", ".join(f["t"] for f in row["flags"]) or "-"
        print(n, "→", cid, row["name"], row["addr"], "| 태그:", tags, flush=True)
        time.sleep(1)
    save(work, "data.json", rows)
    digest(work)


def normalize(d):
    s = d["summary"]
    sub = (d.get("find_way") or {}).get("subway") or {}
    sc = (d.get("kakaomap_review") or {}).get("score_set") or {}
    desc = {x["id"]: x["name"] for x in (d.get("kakaomap_review") or {}).get("strength_description", [])}
    am = d.get("ai_mate") or {}
    badge, rank = trend(d)
    rating, rc = score(d)
    wk = ((d.get("open_hours") or {}).get("week_from_today") or {}).get("week_periods", [{}])[0].get("days", [])
    return {
        "id": s["confirm_id"], "name": s["name"], "cat": s["category"].get("name"), "section": "",
        "rating": rating, "rc": rc, "blog": blog_count(d),
        "st": sub.get("station_simple_name"), "line": (sub.get("subway_list") or [{}])[0].get("subway_line_icon_name"),
        "exit": sub.get("exit_num"), "m": sub.get("to_exit_minute"), "dist": sub.get("to_exit_distance"),
        "ai": (am.get("summary") or {}).get("title", ""), "tags": (am.get("summary") or {}).get("contents", []),
        "price": (am.get("price_level") or {}).get("symbol"),
        "badge": badge, "rank": rank,
        "str": [(desc.get(x["id"], "?"), x["count"]) for x in sc.get("strength_counts", [])][:3],
        # 가격 미기재 메뉴는 price가 -1로 와서 '-1원'으로 보이므로 None으로 바꾼다.
        "menu": [{"n": x["name"], "p": x["price"] if (x.get("price") or 0) > 0 else None}
                 for x in (d.get("menu") or {}).get("menus", {}).get("items", [])[:3]],
        "hours": [(x["day_of_the_week_desc"].split("(")[0], (x.get("on_days") or {}).get("start_end_time_desc") or "휴무") for x in wk],
        "vis": visitors(d),
        "addr": s["address"].get("road"), "imgs": [],
        "sum": "", "pros": [], "cons": [], "flags": [], "ev": [],
    }


def visitors(d):
    """요일(0=일)별 시간대(0~23시) 방문자 수. 데이터가 없으면 None."""
    v = d.get("visitor") or {}
    keys = ("sunday_uv", "monday_uv", "tuesday_uv", "wednesday_uv", "thursday_uv", "friday_uv", "saturday_uv")
    if not all(isinstance(v.get(k), list) and len(v[k]) == 24 for k in keys):
        return None
    return [[max(x, 0) for x in v[k]] for k in keys]


def parse_day(s):
    return datetime.datetime.strptime(s[:10], "%Y-%m-%d").date()


def suspicious(r):
    """5점 리뷰의 의심 종류: 'new'(리뷰 1~2개 계정) / 'all5'(어디든 5점만 주는 계정) / None."""
    if r.get("star_rating") != 5:
        return None
    o = (r.get("meta") or {}).get("owner") or {}
    cnt, avg = o.get("review_count") or 0, o.get("average_score")
    if cnt <= SUS_NEW_MAX:
        return "new"
    if avg is not None and avg >= 5.0 and cnt >= SUS_ALL5_MIN:
        return "all5"
    return None


def analyze(panel, reviews, srch):
    """카드 태그 목록 [{k, t, tip}]. k: warn(주의) / info(참고) / good(장점)."""
    flags = []
    rating, rc = score(panel)
    badge, rank = trend(panel)
    today = datetime.date.today()

    if rating is None:
        _, why = gate(rating, badge, rank, blog_count(panel))
        flags.append({"k": "info", "t": "평점 비공개",
                      "tip": f"카카오 평점이 표시되지 않는 가게예요. 후보에 넣은 근거: {why}."})
    elif rc < FEW_REVIEWS:
        flags.append({"k": "info", "t": "리뷰 적음", "tip": f"카카오 리뷰가 {rc}건뿐이라 평점을 믿기 어려워요."})

    # 리뷰 의심: 의심 5점이 SUS_WINDOW일 안에 SUS_MIN건 이상
    sus = sorted((parse_day(r["registered_at"]), suspicious(r)) for r in reviews if suspicious(r))
    best, span = 0, None
    for i, (d0, _) in enumerate(sus):
        j = i
        while j + 1 < len(sus) and (sus[j + 1][0] - d0).days < SUS_WINDOW:
            j += 1
        if j - i + 1 >= best:  # 같은 건수면 더 최근 구간을 보여 준다
            best, span = j - i + 1, (d0, sus[j][0], [k for _, k in sus[i:j + 1]])
    clean = [r["star_rating"] for r in reviews if not suspicious(r)]
    if best >= SUS_MIN:
        d0, d1, kinds = span
        tip = (f"{d0:%Y-%m-%d}~{d1:%m-%d}에 의심스러운 5점 리뷰 {best}건이 몰렸어요"
               f"(리뷰 1~2개뿐인 계정 {kinds.count('new')}건, 어디서나 5점만 주는 계정 {kinds.count('all5')}건)."
               f" 확인한 리뷰 {len(reviews)}건 중 의심 리뷰는 모두 {len(sus)}건이에요.")
        if len(clean) >= 3:
            tip += f" 의심 리뷰를 빼고 계산한 평균은 ★{sum(clean) / len(clean):.1f}."
        flags.append({"k": "warn", "t": "리뷰 의심", "tip": tip})

    # 최근 하락·최근 리뷰 없음 (의심 리뷰는 빼고 본다)
    recent = [r["star_rating"] for r in reviews
              if not suspicious(r) and (today - parse_day(r["registered_at"])).days <= RECENT_DAYS]
    if rating is not None and len(recent) >= DROP_MIN:
        avg = sum(recent) / len(recent)
        if avg <= rating - DROP_GAP:
            flags.append({"k": "warn", "t": "최근 하락",
                          "tip": f"최근 6개월 리뷰 {len(recent)}건의 평균(★{avg:.1f})이 전체 평균(★{rating:.1f})보다 {rating - avg:.1f}점 낮아요."})
    if reviews and rating is not None:  # 평점 비공개 가게는 리뷰창이 닫혀 있어 마지막 리뷰가 오래된 게 정상
        last = max(parse_day(r["registered_at"]) for r in reviews)
        if (today - last).days > RECENT_DAYS:
            flags.append({"k": "info", "t": "최근 리뷰 없음",
                          "tip": f"마지막 카카오 리뷰가 {last:%Y-%m-%d}이에요. 영업 중인지 확인해 주세요."})

    icons = [x.get("text", "") for x in
             (((panel.get("place_add_info") or {}).get("ai_mate") or {}).get("store_facility_icons") or [])]
    if any("예약가능" in t.replace(" ", "") for t in icons):
        flags.append({"k": "good", "t": "예약 가능",
                      "tip": "카카오맵 매장 정보에 '예약가능'으로 나와요. 원격 줄서기만 되는 곳도 이렇게 표시될 수 있어서 카카오맵에서 방법을 확인해 주세요."})

    price = ((panel.get("ai_mate") or {}).get("price_level") or {}).get("symbol") or ""
    if len(price) >= 5:
        flags.append({"k": "info", "t": "비싼 편", "tip": f"카카오 가격대가 최고 단계({price})예요."})

    why = chain_reason(panel["summary"]["name"], srch)
    if why:
        flags.append({"k": "info", "t": "체인점", "tip": why})
    return flags


def retag(work):
    """저장된 raw로 판정 태그만 다시 계산한다(기준을 바꾼 뒤 재수집 없이)."""
    rows = load(work, "data.json", [])
    for r in rows:
        c = rjson(raw_path(work, r["id"]))
        r["flags"] = analyze(c["panel"], rjson(f"{work}/raw/{r['id']}-reviews.json"), c.get("search"))
        print(r["name"], "|", ", ".join(f["t"] for f in r["flags"]) or "-")
    save(work, "data.json", rows)


# ── blogs: 근거 후보(블로그 후기) ──────────────────────────────────────────
def naver_post(url):
    """네이버 블로그 본문 (텍스트, 체험단 배너 호스트 목록). 네이버가 아니면 (None, [])."""
    m = re.search(r"blog\.naver\.com/([^/?#]+)/(\d+)", url or "")
    if not m:
        return None, []
    req = urllib.request.Request(f"https://m.blog.naver.com/{m.group(1)}/{m.group(2)}",
                                 headers={"User-Agent": UA, "Referer": "https://m.blog.naver.com/"})
    raw = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    i = raw.find("se-main-container")
    if i < 0:
        return None, []
    body = raw[raw.find(">", i) + 1:]
    for end in ('class="post_footer', 'id="post_footer', 'class="btn_area'):
        j = body.find(end)
        if j > 0:
            body = body[:j]
            break
    hosts = [h for h in AD_HOSTS if h in body.lower()]
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", body, flags=re.S)
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body))).replace("​", "").strip()
    return text, hosts


def taste_lines(text, k=3):
    """맛 칭찬 문장(부정 표현·해시태그 줄 제외)을 최대 k개."""
    out = []
    for s in re.split(r"(?<=[.!?~])\s+|\s{2,}|(?<=[다요음])\s", text or ""):
        s = s.strip()
        if s.count("#") >= 2:
            continue
        if 8 <= len(s) <= 120 and any(w in s for w in TASTE_WORDS) and not any(w in s for w in NEG_WORDS):
            out.append(s)
            if len(out) >= k:
                break
    return out


def blogs(work, ids, n):
    for r in load(work, "data.json", []):
        if ids and r["id"] not in ids:
            continue
        posts, page = [], 1
        while len(posts) < n:
            j = place_api(f"places/tab/reviews/blog/{r['id']}?page={page}")
            items = j.get("reviews", [])
            posts += items
            if not items or len(posts) >= (j.get("review_count") or 0):
                break
            page += 1
            time.sleep(0.8)
        out = []
        days = [(b.get("registered_at") or "")[:10] for b in posts]
        for b in posts[:n]:
            url = b.get("origin_url", "")
            try:
                text, hosts = naver_post(url)
            except Exception:
                text, hosts = None, []
            body = text or b.get("contents", "")
            day = (b.get("registered_at") or "")[:10]
            out.append({"title": b.get("title", ""), "url": url, "author": b.get("author", ""), "date": day,
                        "full": text is not None, "ad": [w for w in AD_WORDS if w in body] + hosts,
                        "burst": days.count(day) >= BURST_SAME_DAY,
                        "neg": [w for w in NEG_WORDS if w in body], "lines": taste_lines(body)})
            if text is not None:
                time.sleep(0.8)
        wjson(f"{work}/raw/{r['id']}-blogs.json", out)
        print(f"\n===== {r['name']} ({r['id']}) 블로그 {len(out)}건")
        for i, b in enumerate(out):
            mark = ("광고" if b["ad"] else "몰림" if b["burst"]
                    else "부정" if b["neg"] and not b["lines"] else "OK")
            src = "본문" if b["full"] else "요약만"
            print(f"  [{i}] [{mark}] {b['date']} {b['title'][:60]} ({src}) {b['url']}")
            if b["ad"]:
                print("      협찬 표시:", ", ".join(b["ad"]))
            if b["burst"] and not b["ad"]:
                print(f"      같은 날({b['date']}) 후기 {days.count(b['date'])}건 — 체험단 몰림 가능성")
            for s in b["lines"]:
                print("      +", s[:110])
            if b["neg"]:
                print("      - 부정 표현:", ", ".join(b["neg"]))


# ── digest·사진·빌드 ──────────────────────────────────────────────────────
def digest(work):
    """요약 작성용 다이제스트를 출력한다."""
    for r in load(work, "data.json", []):
        d = rjson(raw_path(work, r["id"]))["panel"]
        revs = rjson(f"{work}/raw/{r['id']}-reviews.json")
        stars = [x["star_rating"] for x in revs]
        am = d.get("ai_mate") or {}
        print(f"\n===== {r['name']} ({r['id']}) ★{r['rating']} ({r['rc']}) 배지={r['badge']} 랭킹={r.get('rank')} 역={r['st']} {r['m']}분")
        for f in r.get("flags", []):
            print(f"태그[{f['t']}]: {f['tip']}")
        print("AI요약:", (am.get("bottom_sheet") or {}).get("summary"))
        print("블로그키워드:", [(x["title"], x["keywords"]) for x in am.get("blog_summaries", [])])
        print("별점분포:", {k: stars.count(k) for k in range(1, 6)}, "리뷰월:", sorted({x["registered_at"][:7] for x in revs})[-5:])
        for x in revs[:15]:
            c = re.sub(r"\s+", " ", x.get("contents", "")).strip()
            if c:
                mark = {"new": " [신규계정]", "all5": " [전부5점]"}.get(suspicious(x), "")
                print(f"  {x['star_rating']} {x['registered_at'][:7]}{mark} {c[:120]}")
        for b in (d.get("blog_review") or {}).get("reviews", [])[:3]:
            print("  B", b["title"][:80])


def photos(work, n, ids, src):
    folder = f"cand-{src}"
    os.makedirs(f"{work}/{folder}", exist_ok=True)
    for r in load(work, "data.json", []):
        if ids and r["id"] not in ids:
            continue
        d = rjson(raw_path(work, r["id"]))["panel"]
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
            with open(f"{work}/{folder}/{r['id']}-{got}.jpg", "wb") as f:
                f.write(b)
            got += 1
            if got >= n:
                break
        print(r["name"], src, len(urls), "→", got)


def sheet(work, ids, folder):
    mods = pil()
    if not mods:
        sys.exit(NO_PIL)
    Image, ImageDraw, ImageOps = mods
    rows = [r for r in load(work, "data.json", []) if not ids or r["id"] in ids]
    W, H, C = 200, 150, 8
    groups = [(r, sorted(glob.glob(f"{work}/{folder}/{r['id']}-*.jpg"), key=lambda p: int(p.rsplit("-", 1)[1][:-4]))) for r in rows]
    nrow = sum(max(1, -(-len(g) // C)) for _, g in groups)
    im = Image.new("RGB", (W * C, H * nrow), "white")
    y = 0
    for r, g in groups:
        for k, p in enumerate(g):
            t = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
            t.thumbnail((W, H))
            x, yy = (k % C) * W, y + (k // C) * H
            im.paste(t, (x, yy))
            ImageDraw.Draw(im).text((x + 3, yy + 3), f"{r['id']}-{k}", fill="red")
        y += max(1, -(-len(g) // C)) * H
    out = f"{work}/sheet-{folder}.jpg"
    im.save(out, quality=70)
    print(out)


def to_jpeg(src, out, size=900, quality=70):
    """사진을 긴 변 size px, JPEG quality로 저장한다. Pillow 우선, 없으면 macOS에서만 sips."""
    mods = pil()
    if mods:
        Image, _, ImageOps = mods
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")  # 폰 사진 회전 정보 반영
        im.thumbnail((size, size))
        im.save(out, "JPEG", quality=quality)
    elif sys.platform == "darwin":
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(quality), "-Z", str(size), src, "--out", out],
                       capture_output=True, check=True)
    else:
        sys.exit(NO_PIL)


def pick(work, cid, paths):
    os.makedirs(f"{work}/site/img", exist_ok=True)
    rows = load(work, "data.json", [])
    imgs = []
    for k, p in enumerate(paths):
        p = p if os.path.isabs(p) else f"{work}/{p}"
        to_jpeg(p, f"{work}/site/img/{cid}-{k}.jpg")
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
    for r in rows:  # 0.1.x에서 만든 data.json도 빌드되게 기본값을 채운다
        r.setdefault("flags", [])
        r.setdefault("ev", [])
        r.setdefault("vis", None)
        r.setdefault("rank", None)
    with open(TEMPLATE, encoding="utf-8") as f:
        t = f.read()
    t = t.replace("__TITLE__", html.escape(meta["title"])).replace("__META__", json.dumps(meta, ensure_ascii=False))
    t = t.replace("__DATA__", json.dumps(rows, ensure_ascii=False).replace("</", "<\\/"))
    os.makedirs(f"{work}/site/img", exist_ok=True)
    with open(f"{work}/site/index.html", "w", encoding="utf-8") as f:
        f.write(t)
    files = sorted("img/" + f for f in os.listdir(f"{work}/site/img"))
    print(json.dumps(files))


def load(work, name, default):
    p = f"{work}/{name}"
    return rjson(p) if os.path.exists(p) else default


def save(work, name, obj):
    wjson(f"{work}/{name}", obj, indent=1)


def opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        v = args[i + 1]
        del args[i:i + 2]
        return v
    return default


def flag(args, name):
    if name in args:
        args.remove(name)
        return True
    return False


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    cmd, work = a[0], os.path.abspath(a[1])
    rest = a[2:]
    region = opt(rest, "--region", "")
    area = opt(rest, "--area", "")
    pages = int(opt(rest, "--pages", "3"))
    n = int(opt(rest, "--n", "4" if cmd == "photos" else "8"))
    ids = [x for x in (opt(rest, "--ids", "") or "").split(",") if x]
    src = opt(rest, "--src", "food")
    folder = opt(rest, "--dir", "cand-food")
    cafe = flag(rest, "--cafe")
    near = [x.strip() for x in (opt(rest, "--near", "") or "").split(",") if x.strip()]
    walk = int(opt(rest, "--walk", str(WALK_MIN)))
    os.makedirs(work, exist_ok=True)
    if cmd == "scan":
        scan(work, rest, area, pages, cafe, near, walk)
    elif cmd == "fetch":
        fetch(work, rest, region)
    elif cmd == "tag":
        retag(work)
    elif cmd == "blogs":
        blogs(work, ids, n)
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
