---
name: kakao-food-card
description: 카카오맵 맛집(즐겨찾기 그룹·장소 링크·가게 이름 목록)을 역 도보 시간·카카오 평점·인기 맛집 태그·리뷰 요약·음식 대표사진·카카오맵 버튼이 있는 사진 카드 웹페이지(Artifact)로 만들어 친구에게 공유한다. "맛집 정리해서 웹으로", "카카오맵 즐겨찾기 정리", "맛집 카드 만들어줘", "친구한테 보여줄 맛집 페이지" 요청 시 사용.
---

# kakao-food-card

카카오맵 장소들을 **섹션별 사진 카드 페이지**로 정리해 Artifact로 게시한다. 결과물 예시: [신중동 맛집 후보](https://claude.ai/artifact/2qxiVhuR2LbSazVW6NEe3K) (육지/해산 2섹션, 8곳).

도구: `S="${CLAUDE_PLUGIN_ROOT}/skills/kakao-food-card/scripts/kfc.py"`, 작업 폴더 `W=<스크래치패드>/kfc-<슬러그>`. 카카오 비공식 API는 로그인 없이 curl로 된다(`search.map.kakao.com`, `place-api.map.kakao.com` + `Referer`·`pf: web` 헤더). 브라우저는 **즐겨찾기 목록 읽기**에만 Aside를 쓴다.

**macOS·Windows 공통** — 아래 명령은 Bash 도구(Windows는 Git Bash)에서 그대로 돈다.
- 파이썬: `PY=python3`(macOS) / `PY=python`(Windows — `python3`는 Microsoft Store 스텁일 수 있음). 처음에 `$PY --version`으로 3.8 이상인지 확인한다.
- `-I`(격리 모드)는 사용자 site-packages를 막는다. Pillow가 필요한 `sheet`·`pick`만 `-I` 없이 실행하고, 나머지는 `-I`를 붙인다.
- Pillow가 없으면 `$PY -m pip install --user pillow`. macOS는 Pillow가 없어도 `pick`이 `sips`로 대체된다(`sheet`는 Pillow 필수).
- 파일 입출력과 출력은 스크립트가 UTF-8로 고정하므로 `-X utf8`은 필요 없다.

## 1. 장소 목록 확보

- **가게 이름 목록**이면 바로 2단계.
- **장소 링크**(`map.kakao.com/?itemId=…`, `place.map.kakao.com/<id>`)가 하나뿐이면, 사용자가 원하는 건 대개 그 가게가 저장된 **즐겨찾기 그룹 전체**다. Aside로 확인한다:
  - `aside guide`·`aside guide repl`을 먼저 읽는다(aside-browser 스킬 규칙).
  - `aside repl`은 호출마다 세션이 끝나므로 **한 번의 호출 안에서** `openTab('https://map.kakao.com/')` → snapshot에서 `link "즐겨찾기"` 클릭 → 그룹 목록에서 대상 그룹 `link "<그룹명>"` 클릭 → snapshot으로 장소명·주소를 읽는다. ref는 정규식으로 snapshot tree에서 뽑는다.
  - 장소 링크(`action=addFavorite`)를 열면 나오는 그룹 선택 레이어의 "저장됨 <그룹명>"으로 소속 그룹을 알 수 있다. **그 레이어의 그룹 항목은 클릭하지 않는다**(즐겨찾기 토글됨).
  - 그룹이 모호하면 사용자에게 묻는다.

## 2. 데이터 수집

```bash
$PY -I $S fetch $W "가게1" "가게2" ... --region 부천   # 주소 필터용 지역명
```
- `raw/`에 패널·리뷰 원본, `data.json`에 카드 데이터가 생기고 리뷰 다이제스트가 출력된다(`digest`로 재출력).
- 결과의 주소가 1단계 주소와 같은지 확인한다(동명 가게 주의).
- 패널 필드: `find_way.subway`(가장 가까운 역·출구·도보 분·m), `kakaomap_review.score_set`, `trend_rank.display_text`("○○ 인기 맛집" 태그), `ai_mate`(카카오 AI 요약·블로그 키워드·가격대), `menu.menus.items`, `open_hours`.

## 3. 섹션 나누기·리뷰 요약 (Claude가 직접 작성)

`data.json`의 각 장소에 채운다:
- `section`: 사용자가 말한 분류의 key(예: 육지 `land` / 해산 `sea`). 분류 지시가 없으면 카테고리로 자연스럽게 2~3개.
- `sum`: 2~3문장. 마침표로 끝내야 문장별 줄바꿈된다. 칭찬만 옮기지 말고 **호불호·저평점 후기 패턴**을 반영한다.
- `pros` / `cons`: 짧은 구 2~3개씩.
- 의심 신호는 그대로 적는다: 리뷰 10건 미만(평점 신뢰 낮음), 5점 리뷰가 한 달에 몰림(이벤트 리뷰 가능성), 블로그의 "매장 이전" 언급 등.

`meta.json`을 쓴다:
```json
{"title": "신중동 맛집 후보", "subtitle": "부천 중동 먹자골목 근처 8곳. 사진 위 숫자는 가장 가까운 역 출구에서 걸어가는 시간이에요.",
 "note": "평점·리뷰 수·도보 시간·메뉴·영업시간은 카카오맵 기준(YYYY년 M월 D일 조회). 리뷰가 10건 미만이면 리뷰 수를 주황색으로 표시했어요. 인기 맛집 태그는 카카오맵이 붙인 것이고, 리뷰 요약은 카카오맵 리뷰와 블로그 후기를 읽고 정리한 내용이에요. 영업시간은 조회한 요일 기준이라 가기 전에 카카오맵에서 확인해 주세요.",
 "sections": [{"key": "land", "label": "육지", "sub": "곱창 · 막창 · 양꼬치", "tone": "warm"},
              {"key": "sea", "label": "해산", "sub": "회 · 해산물", "tone": "cool"}]}
```
`tone`은 `warm`(주황) / `cool`(파랑).

## 4. 대표 사진 (음식 위주, 반드시 눈으로 확인)

```bash
$PY -I $S photos $W --n 8                 # 카카오 '음식' 태그 사진 → cand-food/
$PY $S sheet $W --dir cand-food               # 컨택트시트 (Pillow 필요해서 -I 없이)
```
- 시트를 Read로 보고 **첫 장이 그 가게 대표 메뉴**(곱창집이면 곱창판, 횟집이면 회)가 되게 고른다. 음식 태그여도 찌개·볶음밥·사이드만 나오는 경우가 흔하다.
- 대표 메뉴가 없으면 `--src all`(가게 등록 사진 포함) 또는 `--src blog`(블로그 후기 사진)로 `--ids`를 좁혀 다시 받는다.
- 확정: `$PY $S pick $W <id> cand-food/<id>-3.jpg cand-blog/<id>-0.jpg ...` (4장 권장, 첫 장이 대표). Pillow로 변환하므로 `-I` 없이 실행한다.

## 5. 빌드·게시

```bash
$PY -I $S build $W     # site/index.html 생성, 게시할 img 파일 목록 JSON 출력
```
- section·imgs·sum이 빠진 장소가 있으면 빌드가 멈춘다.
- Artifact 게시: `file_path=$W/site/index.html`, `root=$W/site`, `files=`(build가 출력한 목록), 첫 게시 때 `icon: "food"`. 같은 file_path로 재게시하면 URL이 유지된다.
- 페이지에 들어 있는 것: 정렬 버튼(가까운 순/평점 순/리뷰 많은 순), 섹션 바로가기, 사진 썸네일 전환, 카카오맵처럼 생긴 인기 맛집 태그(순위 없이 문구만), 리뷰 요약, 대표 메뉴 가격, 오늘 영업시간, 노란 "카카오맵에서 보기" 버튼, 라이트/다크 테마.

## 6. 보고

- 섹션별 표: 가게 / 평점(리뷰 수) / 역·출구·도보 시간.
- 눈에 띄는 점(호불호, 리뷰 신뢰도, 사진을 다른 출처에서 가져온 가게).
- **공유**: 처음엔 비공개다. 페이지 오른쪽 위 Share에서 링크 공유를 켜야 친구가 열 수 있다(Claude는 공유 설정을 바꿀 수 없음). 페이지엔 공개 가게 정보만 있고 개인 즐겨찾기·계정 정보는 없다. 사진은 리뷰어 사진이라 지인 공유는 괜찮지만 공개 게시는 피하라고 안내한다.
