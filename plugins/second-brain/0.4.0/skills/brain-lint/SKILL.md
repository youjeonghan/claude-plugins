---
name: brain-lint
description: Second Brain 단일 통합 wiki 헬스체크 — description 누락·중복·orphan·stale·끊긴 링크·frontmatter/파일명 위반·아카이브 후보 탐지 후 승인형 수정. 검사 항목·규약은 볼트 매뉴얼을 따른다.
---

# Brain Lint

LLM Wiki **lint** 오퍼레이션의 Claude Code 진입점.

검사 항목·규약의 단일 진실원본은 **볼트 매뉴얼**이다 — 매번 읽어 그대로 따른다.

## 절차

1. **볼트 경로 확인**
   `~/.claude/brain-config.json`을 Read → `vault.path`.
   없으면 진행하지 말고 `brain-setup`을 안내한다.

2. **매뉴얼 로드 (필수)**
   볼트 루트의 `CLAUDE.md`를 Read한다(없으면 동일 내용 `AGENTS.md`).
   "## 7. 운영 워크플로우 → ### Lint"의 검사 ⓐ~ⓗ를 확인한다.

3. **수행**
   검사 ⓐ~ⓗ → 카테고리별 리포트 → 사용자 승인(일괄/개별/스킵) → 승인분만 수정 → `log` 엔트리.
   범위는 요청에 자연어로 한정할 수 있다(예: 'game-dev만').

4. **보고**
   카테고리별 건수 · 적용한 수정 · 남은 미해결 항목.

## ⚠️ 가드 — 매뉴얼 없이 추측 금지

`vault.path` 또는 매뉴얼(`CLAUDE.md`/`AGENTS.md`)을 찾거나 읽지 못하면 **진행하지 말고 사용자에게 경고하고 멈춘다** (임의 경로 추측·규약 없는 동작 금지). 매뉴얼에서 기대한 절(`### Lint`)을 못 찾을 때도 같이 경고한다 — 참조 어긋남 신호.
