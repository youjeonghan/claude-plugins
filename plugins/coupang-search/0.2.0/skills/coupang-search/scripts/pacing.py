#!/usr/bin/env python3
"""쿠팡 페이지 간격 관리 — 현재 간격·오늘 누적·단축 제안을 보여주고, 실행 결과를 히스토리에 남긴다.

데이터는 플러그인 밖(~/.claude/coupang-search/)에 둔다. 플러그인 업데이트로 지워지지 않고,
차단은 기기·IP 단위라 히스토리도 기기마다 따로 쌓는 게 맞다.

  pacing.py status
  pacing.py log --pages 15 [--detail 3] --actual 45 [--blocked-at 7 --elapsed-min 6.5] [--note "..."]

검색 목록·상세 페이지를 구분하지 않고 "연 페이지 수"로 센다(차단은 페이지 종류가 아니라 타이밍 문제).
히스토리 키는 호환을 위해 "searches"를 그대로 쓴다.
  pacing.py set-interval 35
  pacing.py history [-n 10]
"""
import argparse
import datetime as dt
import json
import math
import socket
import sys
from pathlib import Path

HOME = Path.home() / ".claude" / "coupang-search"
STATE = HOME / "state.json"
HISTORY = HOME / "history.jsonl"

DEFAULT_INTERVAL = 40   # 초
MIN_INTERVAL = 10       # 이 아래로는 단축 제안하지 않음
BLOCK_FACTOR = 1.5      # 막히면 1.5배
STREAK_RUNS = 3         # 같은 간격으로 연속 무차단 실행 수
STREAK_MIN_SEARCHES = 10  # 그 실행들의 최소 페이지 수


def now():
    return dt.datetime.now().astimezone()


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"interval": DEFAULT_INTERVAL, "since": None}


def save_state(s):
    HOME.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")


def load_history():
    if not HISTORY.exists():
        return []
    out = []
    for line in HISTORY.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def append_history(rec):
    HOME.mkdir(parents=True, exist_ok=True)
    with HISTORY.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def today_count(hist):
    d = now().date().isoformat()
    return sum(r.get("searches", 0) for r in hist if r.get("time", "").startswith(d))


def round5(x):
    return int(math.ceil(x / 5.0) * 5)


def shorter(interval):
    step = 10 if interval > 30 else 5
    return max(MIN_INTERVAL, interval - step)


def suggestion(state, hist):
    """같은 간격으로 무차단 실행이 STREAK_RUNS번 연속이면 단축 제안값을 돌려준다."""
    cur = state["interval"]
    if cur <= MIN_INTERVAL:
        return None
    runs = [r for r in hist if r.get("interval") == cur and (not state.get("since") or r["time"] >= state["since"])]
    tail = runs[-STREAK_RUNS:]
    if len(tail) < STREAK_RUNS:
        return None
    if any(r.get("blocked_at") for r in tail) or any(r.get("searches", 0) < STREAK_MIN_SEARCHES for r in tail):
        return None
    return shorter(cur)


def cmd_status(_):
    s, h = load_state(), load_history()
    print(f"간격: {s['interval']}초 (최소 {MIN_INTERVAL}초)")
    print(f"오늘 누적 페이지: {today_count(h)}회")
    last_block = next((r for r in reversed(h) if r.get("blocked_at")), None)
    if last_block:
        print(f"마지막 차단: {last_block['time'][:16]} · {last_block['interval']}초 간격 · {last_block['blocked_at']}번째 페이지")
    sg = suggestion(s, h)
    if sg:
        print(f"단축 제안: {s['interval']}초 → {sg}초 ({s['interval']}초로 {STREAK_RUNS}번 연속, 각 {STREAK_MIN_SEARCHES}회 이상 무차단)")
    else:
        print("단축 제안: 없음")


def cmd_log(a):
    s, h = load_state(), load_history()
    rec = {
        "time": now().isoformat(timespec="seconds"),
        "host": socket.gethostname(),
        "interval": s["interval"],
        "actual": a.actual,
        "searches": a.searches,
        "detail": a.detail,
        "today_before": today_count(h),
        "blocked_at": a.blocked_at,
        "elapsed_min": a.elapsed_min,
        "note": a.note,
    }
    append_history(rec)
    if a.blocked_at:
        new = round5(s["interval"] * BLOCK_FACTOR)
        print(f"차단 기록: {s['interval']}초 간격(실제 {a.actual}초), {a.blocked_at}번째 페이지,"
              f" 시작 후 {a.elapsed_min}분, 오늘 누적 {rec['today_before'] + a.searches}회")
        print(f"간격 상향: {s['interval']}초 → {new}초")
        s.update(interval=new, since=rec["time"])
        save_state(s)
    else:
        d = f" (상세 {a.detail})" if a.detail else ""
        print(f"무차단 기록: {s['interval']}초 간격(실제 {a.actual}초), 페이지 {a.searches}회{d}")
        sg = suggestion(s, h + [rec])
        if sg:
            print(f"단축 제안: {s['interval']}초 → {sg}초 (사용자 확인 후 set-interval {sg})")


def cmd_set(a):
    s = load_state()
    v = max(MIN_INTERVAL, a.seconds)
    print(f"간격 변경: {s['interval']}초 → {v}초")
    s.update(interval=v, since=now().isoformat(timespec="seconds"))
    save_state(s)


def cmd_history(a):
    for r in load_history()[-a.n:]:
        b = f"차단 {r['blocked_at']}번째" if r.get("blocked_at") else "무차단"
        d = f"(상세 {r['detail']})" if r.get("detail") else ""
        print(f"{r['time'][:16]}  {r['interval']}초(실제 {r.get('actual')})  {r['searches']}회{d}  {b}  {r.get('note') or ''}")


def main():
    # Windows 콘솔(cp949)에서도 한글·기호가 깨지거나 죽지 않게
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="쿠팡 페이지 간격 관리")
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("status").set_defaults(f=cmd_status)
    lg = sp.add_parser("log")
    lg.add_argument("--pages", "--searches", dest="searches", metavar="N", type=int, required=True,
                    help="이번 실행에서 실제로 연 페이지 수(검색 목록+상세, 차단된 것 포함)")
    lg.add_argument("--detail", type=int, help="그중 상세 페이지 수")
    lg.add_argument("--actual", type=float, help="Aside가 보고한 실제 대기(초)")
    lg.add_argument("--blocked-at", type=int, help="막힌 페이지의 순번(1부터). 무차단이면 생략")
    lg.add_argument("--elapsed-min", type=float, help="첫 페이지부터 막힐 때까지 경과(분)")
    lg.add_argument("--note", help="메모(주제, 목록/상세 구성 등)")
    lg.set_defaults(f=cmd_log)
    st = sp.add_parser("set-interval")
    st.add_argument("seconds", type=int)
    st.set_defaults(f=cmd_set)
    hs = sp.add_parser("history")
    hs.add_argument("-n", type=int, default=10)
    hs.set_defaults(f=cmd_history)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
