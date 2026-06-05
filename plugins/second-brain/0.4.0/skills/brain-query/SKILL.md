---
name: brain-query
description: Second Brain 단일 통합 wiki에서 자연어 질문에 답한다 — index/description grep으로 후보를 좁혀 합성, [[wikilink]] 출처 표기. 절차·규약은 볼트 매뉴얼을 따른다.
---

# Brain Query

LLM Wiki **query** 오퍼레이션의 Claude Code 진입점.

절차·규약의 단일 진실원본은 **볼트 매뉴얼**이다 — 매번 읽어 그대로 따른다.

## 절차

1. **볼트 경로 확인**
   `~/.claude/brain-config.json`을 Read → `vault.path`.
   없으면 진행하지 말고 `brain-setup`을 안내한다.

2. **매뉴얼 로드 (필수)**
   볼트 루트의 `CLAUDE.md`를 Read한다(없으면 동일 내용 `AGENTS.md`).
   "## 7. 운영 워크플로우 → ### Query" 절을 확인한다.

3. **수행**
   그 Query 절차대로 진행한다 — `index.md`·`description` grep으로 후보 좁히기 → 상위 N개 정독(부족하면 `source_refs`로 원본) → `[[wikilink]]` 출처로 합성.
   범위는 요청에 자연어로 한정할 수 있다(예: 'game-dev만').

4. **보고**
   답변 본문 · 참조 페이지 · (선택) 환류 저장 경로 · log.

## ⚠️ 가드 — 매뉴얼 없이 추측 금지

`vault.path` 또는 매뉴얼(`CLAUDE.md`/`AGENTS.md`)을 찾거나 읽지 못하면 **진행하지 말고 사용자에게 경고하고 멈춘다** (임의 경로 추측·규약 없는 동작 금지). 매뉴얼에서 기대한 절(`### Query`)을 못 찾을 때도 같이 경고한다 — 참조 어긋남 신호.
