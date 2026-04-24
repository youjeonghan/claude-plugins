---
name: brain-lint
description: Second Brain 볼트의 헬스체크 — description 누락/빈약, 중복 wiki, orphan 페이지, stale 페이지, 누락 cross-reference 등을 탐지하고 승인형 자동 수정을 제공한다.
---

# Brain Lint

LLM Wiki의 **lint** 오퍼레이션. 주기적으로 볼트 품질을 점검한다. 원문 패턴의 "Lint" 역할.

## Step 0: 볼트 경로 확인

`~/.claude/brain-config.json` Read → `vault.path`. 없으면 `brain-setup` 안내.

## Step 1: 스코프 결정

- `--scope all` — 볼트 전체 (기본)
- `--scope knowledge` / `knowledge:<도메인>` / `project:<프로젝트>` — 범위 제한

## Step 2: 검사 항목

### (a) description 누락/빈약

```
Grep(pattern="^description:\\s*$|^description:\\s*\\.\\.\\.", path="<scope>", glob="**/*.md", output_mode="content")
```

빈 description 또는 10자 미만인 경우 flag.

### (b) 중복·근접 wiki 페이지

같은 레이어/폴더 내 description·title 유사도 검사. 아래 휴리스틱:
- title이 서로 70% 이상 공통 단어
- description이 같은 명사 3개 이상 공유

예: PixelLab 3개 파일(`pixellab-summary`, `pixellab-animation`, `pixellab-full-features`) → 통합 후보 제안.

### (c) orphan 페이지 (인바운드 wikilink 0)

각 wiki 페이지에 대해 `Grep(pattern="\\[\\[<slug>\\]\\]|\\[\\[<slug>\\|", path="<vault>")`로 인바운드 카운트. 0이면 flag.

### (d) stale 페이지

`updated` 필드가 매우 오래되었거나, 참조된 `source_refs` 중 더 최신 source 페이지가 있으면 "재검토 필요" flag.

### (e) 누락 cross-reference

wiki 페이지 본문에서 다른 wiki 페이지의 title/slug가 plain text로 등장하는데 `[[wikilink]]`로 감싸지 않은 케이스 탐지. 치환 후보 제안.

### (f) frontmatter 규격 위반

- `type` 필드 없음 또는 허용값(`source|wiki|index|log`) 외 값
- `date`, `updated` 형식 오류
- `domain` / `layer` 필드 잔존 (v2에서 제거됨)

### (g) 파일명 컨벤션 위반

- 언더스코어 포함
- 대문자 (영문 제목)
- 공백 포함

## Step 3: 리포트 출력

카테고리별로 그룹화:

```
## description 빈약 (3건)
- projects/눕/wiki/밸런스-시트.md — "밸런스 시트"
- ...

## 중복 후보 (1건)
- knowledge/게임개발/wiki/pixellab-{summary,animation,full-features}.md → 통합 제안

## orphan (2건)
- ...

## stale (0건)

## 누락 cross-reference (5건)
- projects/눕/wiki/전투-시스템-설계.md 에서 "무기 스탯" 언급 → [[무기-스탯-체계-설계]] 링크화 제안

## frontmatter 위반 (0건)

## 파일명 위반 (0건)
```

## Step 4: 승인형 자동 수정

카테고리별로 AskUserQuestion으로 일괄·개별 수정 승인:

```
AskUserQuestion({
  "question": "description 빈약 3건, 자동 생성할까요?",
  "options": [
    {"label": "전부 자동", "description": "본문에서 요약 추출"},
    {"label": "개별 선택", "description": "파일마다 확인"},
    {"label": "건너뛰기", "description": "지금은 수정하지 않음"}
  ]
})
```

승인된 항목만 Edit으로 적용.

## Step 5: log.md append

```
## [YYYY-MM-DD] lint | <scope> — <수정 건수 카테고리별 요약>
```

## Step 6: 결과 보고

- 검사 요약 (카테고리별 건수)
- 적용된 수정
- 남은 미해결 항목 (다음 lint 대상)

## 에러 처리

- 스킬 사용자가 수정 승인 거부 → 리포트만 출력하고 종료
- 수정 실패(파일 충돌 등) → 해당 항목만 스킵하고 나머지 진행
