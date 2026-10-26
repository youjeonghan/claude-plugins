# coupang-search

쿠팡에서 상품을 찾아 가격·리뷰 수·랭킹을 모으고 1~3순위를 추천하는 스킬.

- 상품 상세 페이지는 열지 않고 **검색 목록 페이지만**, 탭 하나로 **순차** 조회한다.
- 검색 간격은 `~/.claude/coupang-search/`에 기기별 히스토리로 관리한다.
  - 막히면: 막힌 시점의 간격·순번·경과를 보고하고 간격을 1.5배로 올린다.
  - 같은 간격으로 3번 연속(각 10회+) 안 막히면: 단축을 제안한다(최소 10초).
- 브라우저 작업은 [Aside](https://aside.com) CLI 기준.

## 설치

```bash
claude plugin marketplace add youjeonghan/claude-plugins
claude plugin install coupang-search@youjeonghan-claude-plugins
```

## 히스토리 명령

```bash
python3 scripts/pacing.py status            # 현재 간격·오늘 누적·단축 제안
python3 scripts/pacing.py history -n 20     # 최근 기록
python3 scripts/pacing.py set-interval 30   # 간격 수동 변경
```
