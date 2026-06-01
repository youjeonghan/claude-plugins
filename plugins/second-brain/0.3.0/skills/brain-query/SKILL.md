---
name: brain-query
description: Second Brain 단일 통합 wiki에서 자연어 질문에 답한다. root index.md description rollup을 1차 grep해 관련 페이지를 선별·합성하며, 답변을 wiki로 환류하는 옵션을 제공한다.
---

# Brain Query

LLM Wiki의 **query** 오퍼레이션. 볼트 전체를 통짜로 읽지 않고, root `index.md` description rollup을 먼저 grep해서 후보를 좁힌 뒤 깊이 읽는다. 규약 원본은 볼트 `CLAUDE.md`.

## Step 0: 볼트 경로 확인

`~/.claude/brain-config.json` Read → `vault.path`. 없으면 `brain-setup` 안내.

## Step 1: 스코프 결정

인자 우선, 없으면 cwd로 추론:

- `--area <영역>` — 특정 영역(`wiki/<영역>`)만
- `--scope all` — wiki 전체 (기본값)
- `cwd`가 등록 workspace 하위면 해당 프로젝트 영역을 기본 추천(없으면 all).

## Step 2: index.md rollup grep

스코프 내 description을 Grep:

```
Grep(pattern="<질문 키워드>", path="index.md", output_mode="content")
Grep(pattern="^description:|^title:", path="wiki", glob="**/*.md", output_mode="content")
```

(영역 한정 시 둘째 path를 `wiki/<영역>`으로.) description 필드 우선, 매치된 페이지 목록을 후보로.

## Step 3: 후보 페이지 읽기

후보를 관련도 순으로 정렬 (키워드 매치 수, description 근접도). 상위 N개 Read. N은 질문 복잡도에 따라 3~10.

## Step 4: sources 보강 (필요 시)

wiki에 해답이 불충분하면 `source_refs`를 따라 `sources/` 원본을 Read. 특히 "원문에 정확히 뭐라고 쓰여 있냐"류 질문은 필수.

## Step 5: 합성 답변 생성

답변 구조:
- 핵심 답 (한 문단)
- 상세 (필요 시)
- **출처**: 모든 주장에 `[[wikilink]]` 형식 출처. sources 직접 참조면 `[[sources/<파일>]]`로.

## Step 6: (옵션) 답변을 wiki로 저장

인자 `--save-as-wiki <slug>` 있거나 사용자가 저장을 원하면:

- 답변 내용을 wiki 페이지로 포맷팅
- 영역 판단(cwd + 내용 기반) 후 `wiki/<영역>/<slug>.md`로 저장
- `brain-ingest` 내부 로직 재사용 가능 (또는 직접 Write)
- index 갱신 + log append

## Step 7: log.md append

루트 `log.md`에:

```
## [YYYY-MM-DD] query | <질문 요지> → <읽은 페이지 slug 목록>
```

## Step 8: 결과 보고

- 답변 본문
- 참조한 페이지 목록
- (선택) 저장된 wiki 페이지 경로
- log 엔트리

## 에러 처리

- 관련 페이지 없음 → "볼트에 해당 정보가 없습니다. ingest 필요" 안내. 외부 검색으로 우회하지 않음 (볼트 범위 내 답변이 원칙).
- 스코프 모호 → AskUserQuestion
