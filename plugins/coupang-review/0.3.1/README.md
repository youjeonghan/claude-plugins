# coupang-review

쿠팡 상품 링크 + 내 경험 + 사진을 주면, 붙여 넣을 **후기 텍스트만** 만들어 주는 스킬.
올리기는 사용자가 쿠팡 앱에서 직접 한다.

- 체험단은 신청제가 아니라 쿠팡이 초대한다.
  - 공식 기준: 와우 회원 + 활발한 상품평 활동 + 양질의 구매후기.
  - 상품평 랭킹과는 무관하다(공식).
  - 리뷰 개수·도움 수·글자 수 합격선은 공개되지 않았다.
- 스킬이 하는 일:
  - 링크의 상품 페이지를 한 번 읽어(coupang-search 간격 규칙) 다른 리뷰에서 많이 나온 포인트를 찾는다.
  - 내 경험에서 빠진 포인트만 짧게 되묻고, 답한 것만 쓴다.
  - 남의 경험·문장은 옮기지 않는다(허위 후기는 공식 불이익, 겹치는 문장은 복붙처럼 보임).
  - 내 말투를 살려 한줄 요약 + 상세리뷰 텍스트를 낸다.
  - 리뷰 활동과 체험단 주문·후기 마감일(초대일 포함 14일)을 기록한다.
- 조사 근거: `skills/coupang-review/references/selection-research.md`

## 설치

```bash
claude plugin marketplace add youjeonghan/claude-plugins
claude plugin install coupang-review@youjeonghan-claude-plugins
```

상품 페이지 읽기에는 `coupang-search` 플러그인과 Aside CLI가 있으면 좋다(없으면 간격 40초 기본값).

## 기록 명령

```bash
python3 scripts/review_log.py status                          # 최근 활동·진행 중 체험단 마감
python3 scripts/review_log.py add --product "…" --chars 420 --photos 4
python3 scripts/review_log.py invite --product "…" --date 2026-12-01
python3 scripts/review_log.py ordered --product "…"
python3 scripts/review_log.py history -n 20
```
