# second-brain 플러그인 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `brain-read`, `brain-write`, `brain-cleanse` 스킬 3개와 `brain-setup` 커맨드를 `second-brain` 플러그인으로 패키징해 마켓플레이스에 배포한다.

**Architecture:** 기존 로컬 스킬(`~/.claude/skills/brain-*/SKILL.md`)을 플러그인 구조로 그대로 복사한다. `self-evolve` 플러그인과 동일한 파일 레이아웃을 따른다. `brain-setup` 커맨드는 `~/.claude/brain-config.json`을 생성·갱신하는 인터랙티브 워크플로우다.

**Tech Stack:** Markdown (스킬/커맨드 파일), JSON (plugin.json, marketplace.json)

---

## 파일 맵

| 작업 | 파일 |
|------|------|
| Create | `plugins/second-brain/0.1.0/.claude-plugin/plugin.json` |
| Create | `plugins/second-brain/0.1.0/README.md` |
| Create | `plugins/second-brain/0.1.0/commands/brain-setup.md` |
| Create | `plugins/second-brain/0.1.0/skills/brain-read/SKILL.md` |
| Create | `plugins/second-brain/0.1.0/skills/brain-write/SKILL.md` |
| Create | `plugins/second-brain/0.1.0/skills/brain-cleanse/SKILL.md` |
| Modify | `.claude-plugin/marketplace.json` |

---

### Task 1: plugin.json 생성

**Files:**
- Create: `plugins/second-brain/0.1.0/.claude-plugin/plugin.json`

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p plugins/second-brain/0.1.0/.claude-plugin
mkdir -p plugins/second-brain/0.1.0/commands
mkdir -p plugins/second-brain/0.1.0/skills/brain-read
mkdir -p plugins/second-brain/0.1.0/skills/brain-write
mkdir -p plugins/second-brain/0.1.0/skills/brain-cleanse
```

- [ ] **Step 2: plugin.json 작성**

`plugins/second-brain/0.1.0/.claude-plugin/plugin.json`:

```json
{
  "name": "second-brain",
  "version": "0.1.0",
  "description": "Obsidian Second Brain 볼트를 Claude Code에서 읽고, 쓰고, 정리하는 스킬 모음",
  "author": {
    "name": "youjeonghan",
    "url": "https://github.com/youjeonghan"
  },
  "repository": "https://github.com/youjeonghan/claude-plugins",
  "license": "MIT",
  "skills": "./skills/",
  "commands": "./commands/"
}
```

- [ ] **Step 3: JSON 유효성 확인**

```bash
python3 -m json.tool plugins/second-brain/0.1.0/.claude-plugin/plugin.json
```

Expected: JSON 내용 그대로 출력됨 (오류 없음)

- [ ] **Step 4: 커밋**

```bash
git add plugins/second-brain/0.1.0/.claude-plugin/plugin.json
git commit -m "feat: second-brain 플러그인 scaffold — plugin.json 추가"
```

---

### Task 2: brain-setup 커맨드 작성

**Files:**
- Create: `plugins/second-brain/0.1.0/commands/brain-setup.md`

- [ ] **Step 1: brain-setup.md 작성**

`plugins/second-brain/0.1.0/commands/brain-setup.md`:

```markdown
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

```
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
```

"현재 설정 유지" 선택 시 → Step 3(폴더 구조 확인)으로 이동. 경로는 기존 값을 그대로 사용.

**파일이 없으면:** 바로 Step 2로 이동.

## Step 2: 볼트 경로 입력

AskUserQuestion으로 볼트 절대 경로를 입력받는다:

```
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
```

## Step 3: 폴더 구조 확인 및 scaffolding

### 3-1: 볼트 디렉토리 존재 확인

```bash
ls {입력_경로}
```

존재하지 않으면 → AskUserQuestion으로 생성 여부 확인:

```
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
```

"취소" 선택 시 → Step 2로 돌아간다.

"생성" 선택 시:

```bash
mkdir -p {입력_경로}/Projects
mkdir -p {입력_경로}/Resources
```

### 3-2: Projects/ 폴더 확인

```bash
ls {입력_경로}/Projects
```

오류 발생(없음) 시:

```bash
mkdir -p {입력_경로}/Projects
```

### 3-3: Resources/ 폴더 확인

```bash
ls {입력_경로}/Resources
```

오류 발생(없음) 시:

```bash
mkdir -p {입력_경로}/Resources
```

### 3-4: README.md 확인 및 생성

```bash
ls {입력_경로}/README.md
```

존재하지 않으면 Write로 생성:

파일 경로: `{입력_경로}/README.md`

내용:
- 제목: `# Second Brain`
- 볼트 구조 설명 (Projects/, Resources/ 역할)
- brain-read / brain-write / brain-cleanse 사용법 안내

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
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/second-brain/0.1.0/commands/brain-setup.md
git commit -m "feat: brain-setup 커맨드 추가 — 볼트 경로 설정 + 폴더 구조 scaffolding"
```

---

### Task 3: brain-read 스킬 복사

**Files:**
- Create: `plugins/second-brain/0.1.0/skills/brain-read/SKILL.md`
- Source: `~/.claude/skills/brain-read/SKILL.md`

- [ ] **Step 1: 소스 파일 확인**

```bash
cat ~/.claude/skills/brain-read/SKILL.md
```

Expected: SKILL.md 내용 출력됨

- [ ] **Step 2: 파일 복사**

```bash
cp ~/.claude/skills/brain-read/SKILL.md plugins/second-brain/0.1.0/skills/brain-read/SKILL.md
```

- [ ] **Step 3: 복사 확인**

```bash
diff ~/.claude/skills/brain-read/SKILL.md plugins/second-brain/0.1.0/skills/brain-read/SKILL.md
```

Expected: 출력 없음 (동일)

- [ ] **Step 4: 커밋**

```bash
git add plugins/second-brain/0.1.0/skills/brain-read/SKILL.md
git commit -m "feat: brain-read 스킬 추가"
```

---

### Task 4: brain-write 스킬 복사

**Files:**
- Create: `plugins/second-brain/0.1.0/skills/brain-write/SKILL.md`
- Source: `~/.claude/skills/brain-write/SKILL.md`

- [ ] **Step 1: 파일 복사**

```bash
cp ~/.claude/skills/brain-write/SKILL.md plugins/second-brain/0.1.0/skills/brain-write/SKILL.md
```

- [ ] **Step 2: 복사 확인**

```bash
diff ~/.claude/skills/brain-write/SKILL.md plugins/second-brain/0.1.0/skills/brain-write/SKILL.md
```

Expected: 출력 없음 (동일)

- [ ] **Step 3: 커밋**

```bash
git add plugins/second-brain/0.1.0/skills/brain-write/SKILL.md
git commit -m "feat: brain-write 스킬 추가"
```

---

### Task 5: brain-cleanse 스킬 복사

**Files:**
- Create: `plugins/second-brain/0.1.0/skills/brain-cleanse/SKILL.md`
- Source: `~/.claude/skills/brain-cleanse/SKILL.md`

- [ ] **Step 1: 파일 복사**

```bash
cp ~/.claude/skills/brain-cleanse/SKILL.md plugins/second-brain/0.1.0/skills/brain-cleanse/SKILL.md
```

- [ ] **Step 2: 복사 확인**

```bash
diff ~/.claude/skills/brain-cleanse/SKILL.md plugins/second-brain/0.1.0/skills/brain-cleanse/SKILL.md
```

Expected: 출력 없음 (동일)

- [ ] **Step 3: 커밋**

```bash
git add plugins/second-brain/0.1.0/skills/brain-cleanse/SKILL.md
git commit -m "feat: brain-cleanse 스킬 추가"
```

---

### Task 6: README.md 작성

**Files:**
- Create: `plugins/second-brain/0.1.0/README.md`

- [ ] **Step 1: README.md 작성**

`plugins/second-brain/0.1.0/README.md`를 Write 도구로 생성한다. 내용은 아래 구조를 따른다:

**섹션 구성:**

1. `# second-brain` 제목과 한 줄 설명
2. `## 스킬` — brain-read / brain-write / brain-cleanse 표
3. `## 설치` — 마켓플레이스 설치 커맨드, 수동 설치 방법
4. `## 초기 설정` — `/brain-setup` 실행 안내, `~/.claude/brain-config.json` 생성됨 설명
5. `## 사용법` — 스킬 3개 한 줄 설명

설치 커맨드 예시 (README에 들어갈 내용):

```
/plugin marketplace add youjeonghan/claude-plugins
/plugin install second-brain@youjeonghan-claude-plugins
```

수동 설치 예시:

```
git clone https://github.com/youjeonghan/claude-plugins.git ~/claude-plugins
ln -s ~/claude-plugins/plugins/second-brain/0.1.0 ~/.claude/plugins/second-brain
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/second-brain/0.1.0/README.md
git commit -m "docs: second-brain README 추가"
```

---

### Task 7: marketplace.json 등록

**Files:**
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: 현재 파일 확인**

```bash
cat .claude-plugin/marketplace.json
```

- [ ] **Step 2: plugins 배열에 second-brain 항목 추가**

`.claude-plugin/marketplace.json`의 `plugins` 배열 끝에 추가:

```json
{
  "name": "second-brain",
  "description": "Obsidian Second Brain 볼트 읽기·쓰기·정리 스킬 모음",
  "version": "0.1.0",
  "source": "./plugins/second-brain/0.1.0",
  "category": "productivity",
  "tags": ["second-brain", "obsidian", "notes", "knowledge"]
}
```

결과 전체 파일:

```json
{
  "name": "youjeonghan-claude-plugins",
  "description": "youjeonghan의 Claude Code 플러그인 모음",
  "owner": {
    "name": "youjeonghan",
    "url": "https://github.com/youjeonghan"
  },
  "plugins": [
    {
      "name": "self-evolve",
      "description": "세션 분석 후 환경 자동 개선 — 5개 영역 병렬 분석 + 선택적 적용",
      "version": "0.1.3",
      "source": "./plugins/self-evolve/0.1.3",
      "category": "productivity",
      "tags": ["self-evolve", "session", "improvement", "analysis"]
    },
    {
      "name": "second-brain",
      "description": "Obsidian Second Brain 볼트 읽기·쓰기·정리 스킬 모음",
      "version": "0.1.0",
      "source": "./plugins/second-brain/0.1.0",
      "category": "productivity",
      "tags": ["second-brain", "obsidian", "notes", "knowledge"]
    }
  ]
}
```

- [ ] **Step 3: JSON 유효성 확인**

```bash
python3 -m json.tool .claude-plugin/marketplace.json
```

Expected: JSON 내용 그대로 출력됨 (오류 없음)

- [ ] **Step 4: 커밋**

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat: marketplace에 second-brain 플러그인 등록"
```
