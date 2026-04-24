---
name: brain-setup
description: 'Second Brain 볼트 경로 설정 — ~/.claude/brain-config.json v2 생성/갱신, 볼트 LLM Wiki 구조 scaffolding'
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash(ls *)
  - Bash(mkdir *)
  - Bash(touch *)
  - AskUserQuestion
---

# Brain Setup

`~/.claude/brain-config.json`을 v2 스키마로 생성하거나 업데이트한다. 볼트 경로에 LLM Wiki 3-레이어 구조(`knowledge/`, `projects/`, `archive/`)가 없으면 scaffolding한다.

## Step 1: 현재 설정 확인

`~/.claude/brain-config.json` 존재 여부를 Read로 확인.

**파일이 있고 `vault.version == 2`:** 현재 설정 요약을 표시하고 AskUserQuestion으로 변경 여부를 묻는다:

AskUserQuestion(
    questions=[{
        "question": "현재 볼트 경로: {vault.path}\n등록된 프로젝트: {project_workspaces 키 목록}\n어떻게 할까요?",
        "header": "Brain Setup",
        "multiSelect": false,
        "options": [
            {"label": "유지", "description": "변경 없이 종료"},
            {"label": "프로젝트 매핑 추가", "description": "project_workspaces 엔트리를 추가한다"},
            {"label": "볼트 경로 변경", "description": "vault.path를 다시 입력"},
            {"label": "폴더 scaffolding 재검증", "description": "볼트에 누락된 구조가 있는지 확인하고 채운다"}
        ]
    }]
)

**파일이 없거나 v1 (version 필드 없음):** Step 2로 이동 (새로 작성 또는 마이그레이션).

## Step 2: 볼트 경로 입력 / 마이그레이션

신규 생성이면 AskUserQuestion으로 볼트 절대 경로를 입력받는다:

AskUserQuestion(
    questions=[{
        "question": "Second Brain 볼트의 절대 경로를 입력해주세요 (없으면 새로 생성됩니다).",
        "header": "볼트 경로",
        "multiSelect": false,
        "options": []
    }]
)

v1에서 마이그레이션이면 기존 `vault.path`를 그대로 사용하고 `version: 2` 필드 추가.

## Step 3: 프로젝트 워크스페이스 매핑 (선택)

AskUserQuestion으로 외부 프로젝트 디렉토리를 등록할지 묻는다. 등록 시 `프로젝트명 ↔ 절대경로` 쌍을 반복 입력.

## Step 4: 설정 파일 쓰기

`~/.claude/brain-config.json`:

```json
{
  "vault": {
    "path": "{사용자_입력_절대경로}",
    "version": 2
  },
  "project_workspaces": {
    "{프로젝트명}": "{절대경로}"
  }
}
```

## Step 5: 볼트 구조 scaffolding

볼트 경로에 다음이 없으면 생성한다:

```
<vault>/
├── knowledge/
├── projects/
├── archive/
├── index.md
├── log.md
└── _Standards.md
```

각 폴더 생성에 Bash(mkdir -p) 사용. `index.md`, `log.md`, `_Standards.md`가 없으면 템플릿으로 Write.

- `index.md` 템플릿: LLM Wiki 루트 카탈로그
- `log.md` 템플릿: 빈 활동 로그 (frontmatter + `# Activity Log` 제목)
- `_Standards.md` 템플릿: frontmatter 스펙 요약 (볼트 스펙 참조)

## Step 6: 결과 출력

사용자에게 간단히 보고:
- config 경로와 주요 값
- scaffolding 결과 (새로 만든 폴더 목록)
- 다음 단계 제안 (`brain-ingest`로 첫 source 저장)
