#!/usr/bin/env python3
"""쿠팡 리뷰 활동 기록 + 체험단 마감일 관리.

기록은 ~/.claude/coupang-review/ 에 쌓인다(플러그인 업데이트로 지워지지 않음).
  reviews.jsonl  리뷰 한 건당 한 줄
  invites.jsonl  체험단 초대 한 건당 한 줄

명령:
  status                          최근 활동 + 진행 중인 체험단 마감
  add --product P [--chars N] [--photos N] [--video] [--trial] [--url U] [--date D]
  invite --product P [--date D]   체험단 초대 기록(마감일 계산)
  ordered --product P             체험단 상품 주문 완료 표시
  history [-n 20]                 최근 리뷰 목록
"""
import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

HOME = Path.home() / ".claude" / "coupang-review"
REVIEWS = HOME / "reviews.jsonl"
INVITES = HOME / "invites.jsonl"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def load(path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def save_all(path, rows):
    HOME.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def append(path, row):
    HOME.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_day(s):
    return date.fromisoformat(s) if s else date.today()


def deadlines(invited):
    # 주문: 초대일로부터 3일 이내 → 보수적으로 초대일 포함 3일째(초대일+2)
    # 후기: 초대일 포함 14일 이내 → 초대일+13
    return invited + timedelta(days=2), invited + timedelta(days=13)


def dday(d, today):
    n = (d - today).days
    return "D-day" if n == 0 else (f"D-{n}" if n > 0 else f"{-n}일 지남")


def cmd_status(_):
    today = date.today()
    reviews = load(REVIEWS)
    days = [date.fromisoformat(r["date"]) for r in reviews]
    last30 = sum(1 for d in days if (today - d).days < 30)
    last7 = sum(1 for d in days if (today - d).days < 7)
    print(f"리뷰 누적 {len(reviews)}건 · 최근 7일 {last7}건 · 최근 30일 {last30}건")
    if days:
        gap = (today - max(days)).days
        print(f"마지막 리뷰: {max(days)} ({gap}일 전)")
        if gap >= 14:
            print("  → 2주 넘게 쉬었어요. 최근 산 물건 중 아직 후기 안 쓴 게 있는지 확인해 보세요.")
    if reviews:
        recent = [r for r in reviews if (today - date.fromisoformat(r["date"])).days < 30]
        if recent:
            photos = [r.get("photos", 0) for r in recent]
            no_photo = sum(1 for p in photos if not p)
            if no_photo:
                print(f"  → 최근 30일 중 사진 없는 리뷰 {no_photo}건")
    opens = [i for i in load(INVITES) if not i.get("done")]
    if opens:
        print("진행 중인 체험단:")
        for i in opens:
            inv = date.fromisoformat(i["invited"])
            order_by, review_by = deadlines(inv)
            ordered = "주문함" if i.get("ordered") else f"주문 마감 {order_by} ({dday(order_by, today)})"
            print(f"  - {i['product']} · 초대 {inv} · {ordered} · 후기 마감 {review_by} ({dday(review_by, today)})")
    else:
        print("진행 중인 체험단 없음")


def cmd_add(a):
    d = parse_day(a.date)
    row = {
        "date": d.isoformat(),
        "logged_at": datetime.now().isoformat(timespec="seconds"),
        "product": a.product,
        "chars": a.chars,
        "photos": a.photos,
        "video": a.video,
        "trial": a.trial,
        "url": a.url,
    }
    append(REVIEWS, row)
    print(f"기록함: {d} {a.product} ({a.chars or '?'}자, 사진 {a.photos}장{', 영상' if a.video else ''}{', 체험단' if a.trial else ''})")
    if a.trial:
        invites = load(INVITES)
        hit = next((i for i in invites if not i.get("done") and (a.product in i["product"] or i["product"] in a.product)), None)
        if hit:
            hit["done"] = d.isoformat()
            save_all(INVITES, invites)
            print(f"체험단 완료 처리: {hit['product']}")
    cmd_status(a)


def cmd_invite(a):
    inv = parse_day(a.date)
    append(INVITES, {"invited": inv.isoformat(), "product": a.product, "ordered": False, "done": None})
    order_by, review_by = deadlines(inv)
    print(f"체험단 초대 기록: {a.product} ({inv})")
    print(f"  주문 마감(보수적): {order_by}  · 주말·공휴일이 끼면 쿠팡 안내 날짜가 더 늦을 수 있음")
    print(f"  후기 마감: {review_by}  · 초대일 포함 14일, 배송일 기준 아님")


def cmd_ordered(a):
    invites = load(INVITES)
    hit = next((i for i in invites if not i.get("done") and (a.product in i["product"] or i["product"] in a.product)), None)
    if not hit:
        print("일치하는 진행 중 체험단이 없어요.")
        return
    hit["ordered"] = True
    save_all(INVITES, invites)
    print(f"주문 완료 처리: {hit['product']}")


def cmd_history(a):
    rows = load(REVIEWS)[-a.n:]
    if not rows:
        print("기록 없음")
        return
    for r in rows:
        tag = " [체험단]" if r.get("trial") else ""
        print(f"{r['date']} {r['product']}{tag} · {r.get('chars') or '?'}자 · 사진 {r.get('photos', 0)}장")


def main():
    p = argparse.ArgumentParser(description="쿠팡 리뷰 활동·체험단 마감 기록")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(fn=cmd_status)

    s = sub.add_parser("add")
    s.add_argument("--product", required=True)
    s.add_argument("--chars", type=int, default=0)
    s.add_argument("--photos", type=int, default=0)
    s.add_argument("--video", action="store_true")
    s.add_argument("--trial", action="store_true")
    s.add_argument("--url", default="")
    s.add_argument("--date", default="")
    s.set_defaults(fn=cmd_add)

    s = sub.add_parser("invite")
    s.add_argument("--product", required=True)
    s.add_argument("--date", default="")
    s.set_defaults(fn=cmd_invite)

    s = sub.add_parser("ordered")
    s.add_argument("--product", required=True)
    s.set_defaults(fn=cmd_ordered)

    s = sub.add_parser("history")
    s.add_argument("-n", type=int, default=20)
    s.set_defaults(fn=cmd_history)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
