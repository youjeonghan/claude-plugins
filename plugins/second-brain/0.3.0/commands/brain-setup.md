---
name: brain-setup
description: 'Second Brain 볼트 경로 설정 — ~/.claude/brain-config.json v3 생성/갱신, 단일 통합 wiki 구조 scaffolding'
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

`~/.claude/brain-config.json`을 v3 스키마로 생성하거나 업데이트한다. 볼트 경로에 단일 통합 wiki 구조(`sources/`, `wiki/`, `archive/`)가 없으면 scaffolding한다.

## Step 1: 현재 설정 확인

`~/.claude/brain-config.json` 존재 여부를 Read로 확인.

**파일이 있고 `vault.version == 3`:** 현재 설정 요약을 표시하고 AskUserQuestion으로 변경 여부를 묻는다:

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

**파일이 없거나 v2 이하 (version < 3):** Step 2로 이동 (새로 작성 또는 마이그레이션). v2에서 마이그레이션이면 기존 `vault.path`를 유지하고 `version: 3`으로 올린 뒤 단일-wiki 구조를 안내한다.

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

## Step 3: 프로젝트 워크스페이스 매핑 (선택)

AskUserQuestion으로 외부 프로젝트 디렉토리를 등록할지 묻는다. 등록 시 `프로젝트명 ↔ 절대경로` 쌍을 반복 입력.

## Step 4: 설정 파일 쓰기

`~/.claude/brain-config.json`:

```json
{
  "vault": {
    "path": "{사용자_입력_절대경로}",
    "version": 3
  },
  "project_workspaces": {
    "{프로젝트명}": "{절대경로}"
  }
}
```

## Step 5: 볼트 구조 scaffolding

볼트 경로에 다음이 없으면 생성:

```
<vault>/
├── sources/assets/
├── wiki/
├── archive/
├── index.md
├── log.md
└── CLAUDE.md
```

폴더는 `Bash(mkdir -p)`. `index.md`·`log.md`·`CLAUDE.md`가 없으면 단일-wiki 템플릿으로 Write:
- `CLAUDE.md`: 볼트 운영 매뉴얼(철학·아키텍처·frontmatter·영역·라이프사이클·운영·포맷·사용자).
- `index.md`: 빈 카탈로그(영역 섹션은 ingest가 추가).
- `log.md`: frontmatter + `# Activity Log` + 포맷 안내.

## Step 6: 결과 출력

사용자에게 간단히 보고:
- config 경로와 주요 값
- scaffolding 결과 (새로 만든 폴더 목록)
- 다음 단계 제안 (`brain-ingest`로 첫 source 저장)
