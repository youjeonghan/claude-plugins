# coupang-review

쿠팡 구매후기를 **사용자의 실제 사용 경험으로** 쓰는 스킬.
쿠팡 체험단 초대를 노리고 리뷰 품질을 올리고 싶을 때 쓴다.

- 체험단은 신청제가 아니라 쿠팡이 초대한다.
  - 공식 기준: 와우 회원 + 활발한 상품평 활동 + 양질의 구매후기.
  - 상품평 랭킹과는 무관하다(공식).
  - 리뷰 개수·도움 수·글자 수 합격선은 공개되지 않았다.
- 스킬이 하는 일:
  - 경험을 질문으로 받아 상세리뷰·한줄 요약·별점 근거·사진 촬영 목록을 만든다.
  - 안 써 본 내용은 지어내지 않는다(허위·과장은 공식 불이익 사유).
  - 리뷰 활동과 체험단 주문·후기 마감일(초대일 포함 14일)을 기록한다.
- 쿠팡에 직접 올리지는 않는다. 사용자가 복사해서 올린다.
- 조사 근거: `skills/coupang-review/references/selection-research.md`

## 설치

```bash
claude plugin marketplace add youjeonghan/claude-plugins
claude plugin install coupang-review@youjeonghan-claude-plugins
```

## 기록 명령

```bash
python3 scripts/review_log.py status                          # 최근 활동·진행 중 체험단 마감
python3 scripts/review_log.py add --product "…" --chars 420 --photos 4
python3 scripts/review_log.py invite --product "…" --date 2026-12-01
python3 scripts/review_log.py ordered --product "…"
python3 scripts/review_log.py history -n 20
```
