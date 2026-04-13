---
name: brain-cleanse
description: Second Brain 볼트의 중복·분산된 도메인 문서를 탐지하고 병합 또는 분리한다. description/domain 프론트매터 일괄 추가 기능도 포함.
---

# Brain Cleanse 스킬

볼트 문서의 중복·불일치를 정리한다. 두 가지 모드로 동작.

## Step 0: 볼트 경로 확인

`~/.claude/brain-config.json`을 Read해 `vault.path`를 가져온다.

---

## Mode A: 중복 도메인 병합/분리

사용자가 "정리해줘", "중복 있어?", "cleanse" 등을 요청할 때.

### A-1: domain 필드 인덱스 수집

```
Grep(pattern="^domain:", path="{vault_path}", glob="**/*.md", output_mode="content")
```

결과를 domain 값 기준으로 그룹핑:

```
item-system:
  - Projects/눕/아이템_시스템_설계.md
  - Projects/눕/아이템_드롭_설계.md   ← 같은 domain, 중복 의심

map-system:
  - Projects/눕/맵_시스템_설계.md     ← 단독, 문제 없음
```

### A-2: 중복 도메인 분석

같은 domain을 가진 파일이 2개 이상이면:

1. 각 파일 Read
2. 내용 비교:
   - **내용이 중복** → 병합 제안
   - **내용이 다른 측면** → 도메인 세분화 제안 (예: `item-system` → `item-system/drop` + `item-system/equipment`)

### A-3: 사용자에게 선택지 제시

```
[아이템 시스템 관련 문서 2개 발견]

1. 아이템_시스템_설계.md — 아이템 등급, 강화 시스템
2. 아이템_드롭_설계.md — 드롭률, 드롭 테이블

→ 내용이 서로 다른 측면을 다루고 있습니다.

선택:
A. 병합 (아이템_시스템_설계.md로 통합)
B. 도메인 세분화 유지 (domain을 item-system/equipment, item-system/drop으로 분리)
C. 현재 유지
```

### A-4: 실행

**병합 선택 시:**
1. 두 파일 내용을 섹션별로 통합
2. 대표 파일에 Write
3. 나머지 파일 삭제 (삭제 전 사용자 최종 확인)

**도메인 세분화 선택 시:**
1. 각 파일의 frontmatter `domain` 필드 업데이트
2. 파일명도 도메인에 맞게 변경 제안

---

## Mode B: description/domain 필드 일괄 추가

사용자가 "description 추가해줘", "프론트매터 업데이트" 등을 요청할 때.

### B-1: 대상 파일 수집

frontmatter에 `description` 또는 `domain`이 없는 파일 탐지:

```
Grep(pattern="^description:", path="{vault_path}", glob="**/*.md", output_mode="files_with_matches")
```

→ 결과에 없는 파일 = description 없는 파일

### B-2: 파일별 처리

각 파일을 Read하고:
- `description`: 내용을 분석해 한 줄 요약 자동 생성
- `domain`: `type: design` 문서이면 내용 기반으로 도메인 키 추론 (예: 아이템 관련 → `item-system`)

### B-3: frontmatter 업데이트

Edit으로 기존 frontmatter에 필드 추가. 기존 내용 변경 금지.

---

## 공통 주의사항

- 파일 삭제 전 반드시 사용자 확인
- 병합 시 내용 손실 없이 통합
- 모든 변경 후 git commit (`docs: brain cleanse - [변경 내용]`)
- 한국어로 응답
