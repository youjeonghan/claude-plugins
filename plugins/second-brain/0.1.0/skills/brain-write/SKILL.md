---
name: brain-write
description: Second Brain 볼트에 문서를 저장하거나 기존 도메인 문서를 업데이트한다. domain 필드 기반 upsert로 중복 문서 생성을 방지한다.
---

# Brain Write 스킬

볼트에 새 문서를 만들거나 기존 문서를 업데이트한다.

## Step 0: 볼트 경로 확인

`~/.claude/brain-config.json`을 Read해 `vault.path`를 가져온다.

## Step 1: 프로젝트/위치 판단

저장할 내용을 분석해 어느 폴더에 넣을지 결정:

| 내용 | 저장 위치 |
|------|----------|
| 특정 프로젝트 설계·계획 | `Projects/[프로젝트명]/` |
| 프로젝트 진행 일지 | `Projects/[프로젝트명]/Daily Progress/YYYY-MM-DD - 주제.md` |
| 공통 레퍼런스·학습 | `Resources/[카테고리]/` |

프로젝트 판단이 모호하면 사용자에게 확인: "어느 프로젝트에 해당하나요?"

## Step 2: 기존 domain 문서 검색 (설계 문서인 경우)

`type: design` 문서이면 domain 충돌 확인:

```
Grep(pattern="^domain:", path="{vault_path}/Projects/[프로젝트명]", glob="**/*.md", output_mode="content")
```

**같은 domain 문서가 이미 있으면 → Step 3a (Update)**
**없으면 → Step 3b (Create)**

## Step 3a: 기존 문서 업데이트

1. 기존 파일 Read
2. 변경 내용을 적절한 섹션에 병합 (덮어쓰기 아님, 내용 통합)
3. frontmatter의 `date`를 오늘 날짜로 갱신
4. Edit으로 저장

## Step 3b: 새 문서 생성

`_Standards.md`의 frontmatter 규칙에 따라 새 파일 생성.

파일명 규칙:
- 설계 문서: `[도메인명]_설계.md` (예: `아이템_시스템_설계.md`)
- 진행 일지: `YYYY-MM-DD - 주제.md`
- 레퍼런스: `Resource - 주제 - 출처.md`

### 설계 문서 frontmatter 템플릿

```yaml
---
title: 문서 제목
description: 이 문서가 다루는 내용 한 줄 요약
type: design
date: YYYY-MM-DD
tags: [프로젝트명, domain-tag]
project: "[[프로젝트명]]"
domain: domain-key
status: draft
version: "1.0"
---
```

### 레퍼런스 frontmatter 템플릿

```yaml
---
title: 제목
description: 핵심 내용 한 줄 요약
type: reference
date: YYYY-MM-DD
tags: [카테고리, topic]
source: "https://..."
category: game-dev | web-dev
key_concepts: []
---
```

## Step 4: git commit

파일 저장 후 즉시 커밋:
- 새 문서: `docs: [파일명] 추가`
- 업데이트: `docs: [파일명] 업데이트`

## 주의

- 내용 덮어쓰기 금지. 기존 내용 보존 + 새 내용 병합
- 저장 전 대상 폴더 존재 확인. 없으면 mkdir
- 한국어로 응답
