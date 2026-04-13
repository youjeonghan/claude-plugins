---
name: brain-setup
description: 'Second Brain 볼트 경로 설정 — ~/.claude/brain-config.json 생성/갱신, 볼트 폴더 구조 scaffolding'
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash(ls *)
  - Bash(mkdir *)
  - AskUserQuestion
---

# Brain Setup

`~/.claude/brain-config.json`을 생성하거나 업데이트한다.
볼트 경로에 기본 폴더 구조(`Projects/`, `Resources/`)와 `README.md`가 없으면 생성한다.

## Step 1: 현재 설정 확인

`~/.claude/brain-config.json` 존재 여부를 Read로 확인한다.

**파일이 있으면:**

현재 `vault.path` 값을 읽어 표시한 뒤 AskUserQuestion으로 변경 여부를 묻는다:

AskUserQuestion(
    questions=[{
        "question": "현재 볼트 경로: {현재_경로}\n어떻게 할까요?",
        "header": "Brain Setup",
        "multiSelect": false,
        "options": [
            {"label": "현재 설정 유지", "description": "변경 없이 그대로 사용"},
            {"label": "경로 변경", "description": "새 볼트 경로를 입력합니다"}
        ]
    }]
)

"현재 설정 유지" 선택 시 → Step 3(폴더 구조 확인)으로 이동. 경로는 기존 값을 그대로 사용.

**파일이 없으면:** 바로 Step 2로 이동.

## Step 2: 볼트 경로 입력

AskUserQuestion으로 볼트 절대 경로를 입력받는다:

AskUserQuestion(
    questions=[{
        "question": "Obsidian 볼트의 절대 경로를 입력해주세요 (존재하지 않으면 새로 생성합니다)",
        "header": "볼트 경로 설정",
        "multiSelect": false,
        "options": [
            {"label": "직접 입력", "description": "예: /Users/yourname/second-brain"}
        ]
    }]
)

## Step 3: 폴더 구조 확인 및 scaffolding

### 3-1: 볼트 디렉토리 존재 확인

Bash로 확인:
```bash
ls {입력_경로}
```

존재하지 않으면 → AskUserQuestion으로 생성 여부 확인:

AskUserQuestion(
    questions=[{
        "question": "{입력_경로} 디렉토리가 존재하지 않습니다. 새로 생성할까요?",
        "header": "볼트 디렉토리 생성",
        "multiSelect": false,
        "options": [
            {"label": "생성", "description": "디렉토리와 기본 구조를 만들겠습니다"},
            {"label": "취소", "description": "경로를 다시 입력합니다"}
        ]
    }]
)

"취소" 선택 시 → Step 2로 돌아간다.

"생성" 선택 시 mkdir -p로 Projects/, Resources/ 생성.

### 3-2: Projects/ 폴더 확인

```bash
ls {입력_경로}/Projects
```

오류 발생(없음) 시: `mkdir -p {입력_경로}/Projects`

### 3-3: Resources/ 폴더 확인

```bash
ls {입력_경로}/Resources
```

오류 발생(없음) 시: `mkdir -p {입력_경로}/Resources`

### 3-4: README.md 확인 및 생성

```bash
ls {입력_경로}/README.md
```

존재하지 않으면 Write로 아래 내용 생성:

파일 경로: `{입력_경로}/README.md`

```
# Second Brain

Claude Code와 연동된 Obsidian 지식 베이스.

## 폴더 구조

| 폴더 | 용도 |
|------|------|
| `Projects/` | 프로젝트별 설계 문서, 진행 일지 |
| `Resources/` | 공통 레퍼런스, 학습 자료 |

## Claude Code 스킬 연동

- **brain-read** — 볼트에서 관련 문서 검색·참조
- **brain-write** — 새 문서 생성 또는 기존 문서 업데이트
- **brain-cleanse** — 중복 문서 탐지·정리, 메타데이터 일괄 추가

설정 파일: `~/.claude/brain-config.json`
```

## Step 4: brain-config.json 생성/업데이트

`~/.claude/brain-config.json`을 Write로 생성 또는 덮어쓴다:

```json
{
  "vault": {
    "path": "{입력_경로}"
  }
}
```

## Step 5: 완료 안내

생성/확인된 항목을 목록으로 표시:

```
## 설정 완료!

볼트 경로: {입력_경로}
설정 파일: ~/.claude/brain-config.json

### 볼트 구조
✓ Projects/
✓ Resources/
✓ README.md

이제 다음 스킬을 사용할 수 있습니다:
- brain-read  — 볼트에서 문서 검색·참조
- brain-write — 볼트에 문서 저장·업데이트
- brain-cleanse — 중복 문서 탐지·정리
```

이미 존재하던 항목은 ✓(기존), 새로 생성된 항목은 ✓(생성됨)으로 구분 표시.

## 주의사항

- 한국어로 대화
- 모든 사용자 입력은 AskUserQuestion으로 받는다
- 기존 파일은 덮어쓰지 않는다 (README.md 포함)
- 볼트 디렉토리 생성은 반드시 사용자 확인 후 진행
