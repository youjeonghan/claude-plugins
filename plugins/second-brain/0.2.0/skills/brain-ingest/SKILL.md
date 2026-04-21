---
name: brain-ingest
description: Second Brain 볼트에 새 source(URL/파일/대화/이미지)를 저장하고, 영향받는 wiki 페이지를 연쇄 갱신한다. sources/wiki 물리 분리와 index·log 자동 갱신을 보장한다.
---

# Brain Ingest

LLM Wiki의 **ingest** 오퍼레이션. 원본을 보존(`sources/`)하고, 그 내용을 소화해 기존 wiki(`wiki/`)에 반영하거나 새 wiki 페이지를 만든다.

## Step 0: 볼트 경로 확인

`~/.claude/brain-config.json` Read → `vault.path` 획득. 없으면 사용자에게 `brain-setup` 선행을 안내.

## Step 1: 레이어 판단 (knowledge vs project)

현재 `cwd`를 Bash로 조회한 후 `project_workspaces`와 매칭:

- `cwd`가 등록된 프로젝트 workspace 하위 → `projects/<프로젝트명>/`
- 그 외 + 입력이 "제너럴 지식" 성격 → `knowledge/<도메인>/` (도메인은 `ls knowledge/` 후 AskUserQuestion으로 선택; 새 도메인이면 확장)
- 입력이 특정 프로젝트 맥락이면 AskUserQuestion으로 프로젝트 선택

사용자가 명시적 스코프를 인자로 주면(`--scope project:눕` 등) 그 값을 우선 사용.

## Step 2: 입력 분류 → source 저장 여부 결정

| 입력 유형 | sources/ 저장 | 비고 |
|----------|---------------|------|
| URL (웹 클립 가능) | ✅ | Firecrawl/WebFetch 요약본 저장. `source_url` 필드 기록 |
| 파일 경로 (PDF, 이미지 등) | ✅ | 파일 복사 또는 이동, 텍스트면 그대로 |
| 대화 스니펫 | 선택 | 단발성은 스킵, 참조 가치 있으면 저장 |
| 직접 입력된 분석·아이디어 | ❌ | source 아님. 바로 wiki로 |

sources 저장 시 파일명은 slug 형식 (`소문자-하이픈.md`), frontmatter는 `type: source`, `source_url` 필수.

## Step 3: 핵심 정보 추출

입력 내용에서 다음 정보 식별:
- 핵심 주제 / 엔티티
- 주요 주장·사실·수치
- 기존 wiki에서 다룰 만한 키워드

## Step 4: 영향 wiki 페이지 식별

`<layer_path>/index.md`를 Read → 페이지 목록 확인. 관련 wiki 페이지 후보:

- 같은 엔티티/주제 페이지가 있으면 업데이트
- 주제가 걸친 페이지 여러 개면 전체 업데이트
- 없으면 새 wiki 페이지 생성

Grep으로 키워드 검색 보조: `Grep(pattern="<키워드>", path="<layer_path>/wiki", output_mode="files_with_matches")`.

## Step 5: wiki 페이지 업데이트 / 생성

### 업데이트

기존 wiki 페이지 Read → 관련 섹션에 병합 (덮어쓰기 아님). frontmatter `updated` 갱신. `source_refs`에 이번 source 경로 추가.

### 생성

새 wiki 페이지 Write. frontmatter:

```yaml
---
title: <제목>
description: <한 줄 요약>
type: wiki
date: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
tags: [wiki, <도메인 태그>, ...]
source_refs:
  - sources/<새로 저장된 source 파일>
---
```

본문은 구조화: 개요 → 주요 내용 → 인용 / 출처 wikilink.

## Step 6: index.md rollup 갱신

해당 `<layer_path>/index.md`를 Read → 새 페이지(또는 변경된 description) 엔트리를 Wiki 또는 Sources 섹션에 삽입/업데이트.

포맷: `- [[wiki/<slug>]] — <description>`

## Step 7: log.md append

루트 `log.md`를 Edit로 append:

```
## [YYYY-MM-DD] ingest | <title> → <대상 경로>
```

프로젝트 스코프 ingest면 `projects/<프로젝트>/log.md`에도 추가 가능 (선택).

## Step 8: 결과 보고

사용자에게:
- 저장된 source 경로
- 갱신·생성된 wiki 페이지 목록
- index.md 변경 항목
- log 엔트리

## 에러 처리

- 볼트 경로 누락 → `brain-setup` 안내
- 도메인/프로젝트 모호 → AskUserQuestion
- source_url 누락(URL인데 접근 실패) → 사용자에게 보고하고 저장 continue
