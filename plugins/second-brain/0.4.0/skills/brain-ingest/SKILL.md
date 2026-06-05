---
name: brain-ingest
description: Second Brain 단일 통합 wiki에 새 source(URL/파일/대화/이미지)를 받아 정리한다 — sources에 원본 보존 + 관련 wiki 페이지 연쇄 갱신 + index/log 갱신. 절차·규약은 볼트 매뉴얼을 따른다.
---

# Brain Ingest

LLM Wiki **ingest** 오퍼레이션의 Claude Code 진입점.

실제 절차·규약의 단일 진실원본은 **볼트 매뉴얼**이다 — 여기에 복붙하지 않고, 매번 매뉴얼을 읽어 그대로 따른다.

## 절차

1. **볼트 경로 확인**
   `~/.claude/brain-config.json`을 Read → `vault.path`.
   없으면 진행하지 말고 `brain-setup`을 안내한다.

2. **매뉴얼 로드 (필수)**
   볼트 루트의 `CLAUDE.md`를 Read한다. 없으면 동일 내용인 `AGENTS.md`를 Read한다.
   거기서 "## 7. 운영 워크플로우 → ### Ingest" 절과 규약(§3 frontmatter · §4 파일명 · §8 포맷)을 확인한다.

3. **수행**
   매뉴얼의 Ingest 절차를 이번 입력(URL/파일/대화/이미지)에 그대로 적용한다.
   영역은 요청에 자연어로 지정할 수 있다(예: 'game-dev로 넣어줘').

4. **보고**
   저장한 source · 갱신/신규 wiki 페이지 · index/log 변경을 보고한다.

## ⚠️ 가드 — 매뉴얼 없이 추측 금지

`vault.path` 또는 매뉴얼(`CLAUDE.md`/`AGENTS.md`)을 찾거나 읽지 못하면 **작업을 진행하지 않는다.**

임의로 경로를 추측하거나 규약 없이 wiki를 건드리지 말고, **무엇이 없는지 사용자에게 경고하고 멈춘다** (예: "볼트 매뉴얼을 찾을 수 없습니다 — `brain-setup` 또는 `vault.path`를 확인하세요").

매뉴얼은 찾았지만 그 안에서 기대한 절(`### Ingest`)이 없으면, 임의로 진행하지 말고 **매뉴얼 구조가 바뀐 것 같다고 경고**한다 — 참조가 어긋났다는 신호다(이 결합은 의도된 것).

규약 원본이 매뉴얼이므로, 매뉴얼이 바뀌면 이 스킬은 자동으로 따라간다.
