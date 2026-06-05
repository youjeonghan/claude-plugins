---
name: brain-setup
description: 'Second Brain 볼트 경로 설정 — ~/.claude/brain-config.json v3 생성/갱신, 단일 통합 wiki 구조 scaffolding (CLAUDE.md 매뉴얼 + AGENTS.md 심볼릭)'
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash(ls *)
  - Bash(mkdir *)
  - Bash(touch *)
  - Bash(ln *)
  - AskUserQuestion
---

# Brain Setup

`~/.claude/brain-config.json`을 v3 스키마로 생성·갱신하고, 볼트에 단일 통합 wiki 구조(`sources/`·`wiki/`·`archive/`)가 없으면 scaffolding한다.

## Step 1 — 현재 설정 확인

`~/.claude/brain-config.json`을 Read한다.

**이미 있고 `vault.version == 3`이면** — 현재 설정을 요약해 보여주고, AskUserQuestion으로 다음 중 하나를 고르게 한다:

- **유지** — 변경 없이 종료
- **프로젝트 매핑 추가** — `project_workspaces` 엔트리 추가
- **볼트 경로 변경** — `vault.path` 재입력
- **폴더 재검증** — 누락된 구조를 채움

**없거나 `version < 3`이면** — Step 2로 이동.
(v2 마이그레이션이면 기존 `vault.path`는 유지하고 `version: 3`으로 올린 뒤 단일-wiki 구조를 안내한다.)

## Step 2 — 볼트 경로 입력

신규면 AskUserQuestion으로 볼트의 **절대 경로**를 입력받는다 (없으면 새로 생성).

## Step 3 — 프로젝트 워크스페이스 매핑 (선택)

외부 프로젝트를 등록할지 묻고, 등록 시 `프로젝트명 ↔ 절대경로` 쌍을 반복 입력받는다.

## Step 4 — 설정 파일 쓰기

`~/.claude/brain-config.json`:

```json
{
  "vault": {
    "path": "{입력한 절대경로}",
    "version": 3
  },
  "project_workspaces": {
    "{프로젝트명}": "{절대경로}"
  }
}
```

## Step 5 — 볼트 구조 scaffolding

볼트 루트에 다음이 없으면 만든다:

```
볼트 루트/
├── sources/assets/
├── wiki/
├── archive/
├── CLAUDE.md   # 운영 매뉴얼 (Claude Code·Codex 공용 단일 진실원본)
├── AGENTS.md   # → CLAUDE.md 심볼릭 링크 (Codex 진입점)
├── index.md
└── log.md
```

- 폴더는 `mkdir -p`로 생성.
- **`CLAUDE.md`** — second-brain 운영 매뉴얼. 섹션 골격:
  §1 철학 / §2 아키텍처(sources·wiki·archive 단일 그래프) / §3 frontmatter(`description`·`date`·`updated`·`tags`·`source_url`·`source_refs`) / §4 파일명·태그 / §5 영역 / §6 라이프사이클 / §7 운영 워크플로우(ingest·query·lint 절차) / §8 index·log 포맷 / 사용자.
  **기존 second-brain 볼트가 있으면 그 `CLAUDE.md`를 참고·복사**한다.
- **`AGENTS.md`** — `CLAUDE.md`로의 심볼릭 링크(`ln -s CLAUDE.md AGENTS.md`). Codex가 같은 매뉴얼을 읽도록.
- **`index.md`** — 빈 카탈로그(영역 섹션은 ingest가 추가).
- **`log.md`** — frontmatter + `# Activity Log` + §8 포맷 안내.

## Step 6 — 결과 보고

- config 경로와 주요 값
- 새로 만든 폴더·파일 목록
- 다음 단계: `brain-ingest`로 첫 source 저장
