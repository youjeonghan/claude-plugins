---
name: brain-ingest
description: Second Brain 단일 통합 wiki에 새 source(URL/파일/대화/이미지)를 sources/<영역>/에 저장하고, 영향받는 wiki/<영역>/ 페이지를 연쇄 갱신한다. root index·log 자동 갱신과 sources/wiki 분리를 보장한다.
---

# Brain Ingest

LLM Wiki의 **ingest** 오퍼레이션. 원본을 보존(`sources/`)하고, 그 내용을 소화해 기존 wiki(`wiki/`)에 반영하거나 새 wiki 페이지를 만든다. 규약 원본은 볼트 `CLAUDE.md`.

## Step 0: 볼트 경로 확인

`~/.claude/brain-config.json` Read → `vault.path` 획득. 없으면 사용자에게 `brain-setup` 선행을 안내.

## Step 1: 영역(area) 판단

저장할 영역(`wiki/`·`sources/` 하위폴더)을 정한다:

- 사용자가 `--area <이름>`을 주면 그 값 우선.
- 현재 `cwd`(Bash로 조회)가 `project_workspaces`에 등록된 프로젝트 하위 → 영역 = 그 프로젝트명.
- 그 외: `ls wiki/`로 기존 영역 확인 후, 입력 내용에 맞는 영역을 고르거나 새로 만든다. 모호하면 AskUserQuestion으로 사용자에게 선택받는다(기존 영역 목록 + "새 영역" 옵션).
- 영역 폴더가 없으면 이번 저장 시 생성(`sources/<영역>/`, `wiki/<영역>/`).

## Step 2: 입력 분류 → source 저장 여부 결정

| 입력 유형 | sources/ 저장 | 비고 |
|----------|---------------|------|
| URL (웹 클립 가능) | ✅ | WebFetch 요약본 저장. `source_url` 필드 기록 |
| 파일 경로 (PDF, 이미지 등) | ✅ | 파일 복사 또는 이동, 텍스트면 그대로 |
| 대화 스니펫 | 선택 | 단발성은 스킵, 참조 가치 있으면 저장 |
| 직접 입력된 분석·아이디어 | ❌ | source 아님. 바로 wiki로 |

sources 저장 시 파일은 `sources/<영역>/<slug>.md` (slug = 소문자-하이픈), frontmatter `type: source`, URL이면 `source_url` 필수.

## Step 3: 핵심 정보 추출

입력 내용에서 다음 정보 식별:
- 핵심 주제 / 엔티티
- 주요 주장·사실·수치
- 기존 wiki에서 다룰 만한 키워드

## Step 4: 영향 wiki 페이지 식별

root `index.md`를 Read → 해당 영역 섹션의 페이지 목록 확인. 관련 wiki 페이지 후보:

- 같은 엔티티/주제 페이지가 있으면 업데이트
- 주제가 여러 페이지에 걸치면 전부 업데이트
- 없으면 새 wiki 페이지 생성

Grep 보조: `Grep(pattern="<키워드>", path="wiki", output_mode="files_with_matches")` (영역 한정 시 `path="wiki/<영역>"`).

## Step 5: wiki 페이지 업데이트 / 생성

### 업데이트

기존 wiki 페이지 Read → 관련 섹션에 병합 (덮어쓰기 아님). frontmatter `updated` 갱신. `source_refs`에 이번 source 경로 추가.

### 생성

새 wiki 페이지를 `wiki/<영역>/<slug>.md`로 Write. frontmatter:

```yaml
---
title: <제목>
description: <한 줄 요약>
type: wiki
date: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
tags: [wiki, <영역 태그>, ...]
source_refs:
  - sources/<영역>/<새 source 파일>
---
```

본문은 구조화: 개요 → 주요 내용 → 인용 / 출처 wikilink.

## Step 6: index.md rollup 갱신

root `index.md`를 Read → 해당 영역 섹션에 새 페이지(또는 변경된 description) 엔트리를 삽입/갱신. 영역 섹션이 없으면 새로 만든다(`## <영역>`).

포맷: `- [[wiki/<영역>/<slug>]] — <description>`

## Step 7: log.md append

루트 `log.md`를 Edit로 append:

```
## [YYYY-MM-DD] ingest | <title> → wiki/<영역>/<slug>
```

## Step 8: 결과 보고

사용자에게:
- 저장된 source 경로
- 갱신·생성된 wiki 페이지 목록
- index.md 변경 항목
- log 엔트리

## 에러 처리

- 볼트 경로 누락 → `brain-setup` 안내
- 영역 모호 → AskUserQuestion
- source_url 누락(URL인데 접근 실패) → 사용자에게 보고하고 저장 continue
