---
name: self-evolve-setup
description: 'self-evolve 스킬 설정 초기화 및 변경'
argument-hint: '[setting]'
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash(find *)
  - Bash(ls *)
  - Bash(cat *)
  - Bash(grep *)
  - Glob
  - Grep
  - AskUserQuestion
---

# Self-Evolve 설정 도우미

사용자와 대화하며 `~/.claude/self-evolve-config.json` 설정 파일을 만들거나 수정하는 인터랙티브 워크플로우.

## 모드 판별

- `$ARGUMENTS`가 비어있거나 `setup` → **초기 설정 모드**
- `$ARGUMENTS`가 `setting` → **설정 변경 모드** (기존 config 로드 후 변경할 항목만 수정)

## 1단계: 환경 탐색

아래 3가지를 **병렬로** 탐색한다:

### 1-1. 기존 설정 확인
- `~/.claude/self-evolve-config.json` 존재 여부
- 존재하면 내용을 읽어서 현재 설정 표시 (setting 모드의 기반)

### 1-2. 문서화 환경 감지
- Obsidian 볼트 감지: `~/second-brain/` 등 `.obsidian/` 폴더가 있는 디렉토리
- 기존 문서화 스킬 감지: `brain-dump`, `brain-log`, `doc-writer` 등
- Notion 스킬 존재 여부: `notion`, `notion-spec`

### 1-3. 현재 설정 스캔
- `~/.claude/settings.json` hooks 섹션
- `~/.claude/settings.local.json` 존재 여부
- 기존 스킬 수 (전역 + 프로젝트)
- `.omc/` 디렉토리 존재 여부

### 탐색 결과 표시

```markdown
## 환경 탐색 결과

| 항목 | 상태 |
|------|------|
| 기존 설정 | ✓ 존재 (v1.0.0) / ✗ 없음 |
| Obsidian 볼트 | ✓ ~/second-brain/ |
| 문서화 스킬 | brain-dump, brain-log, doc-writer |
| Notion 스킬 | ✓ notion, notion-spec |
| 전역 스킬 수 | 27개 |
| OMC 설치 | ✓ / ✗ |
| 기존 훅 | N개 등록됨 |
```

## 2단계: 인터뷰

**모든 질문은 AskUserQuestion을 사용한다.** 답변에 따라 다음 질문을 조정한다.

### 라운드 1 — 문서화 대상 설정

환경 탐색 결과를 먼저 표시한 뒤, 감지된 환경에 맞는 추천 옵션을 AskUserQuestion으로 제시한다.

**감지된 환경별 옵션 구성:**

- Obsidian만 감지 → Obsidian 추천(Recommended) + 사용 안 함
- Notion만 감지 → Notion 추천(Recommended) + 사용 안 함
- 둘 다 감지 → Obsidian, Notion, 둘 다, 사용 안 함
- 둘 다 없음 → 로컬 파일 추천(Recommended) + 사용 안 함

예시 (Obsidian 감지 시):

```
AskUserQuestion(
    questions=[{
        "question": "세션에서 발견한 지식을 어디에 저장할까요?",
        "header": "문서화 대상",
        "multiSelect": false,
        "options": [
            {"label": "Obsidian (추천)", "description": "~/second-brain/ 볼트에 저장 + /brain 커맨드 연동"},
            {"label": "로컬 파일", "description": "프로젝트 디렉토리 내 적절한 위치에 저장"},
            {"label": "문서화 비활성화", "description": "문서화 분석을 사용하지 않음"}
        ]
    }]
)
```

문서화 스킬이 감지되었으면 description에 `+ /{스킬명} 커맨드 연동`을 포함한다.

### 라운드 2 — 분석 영역 & 옵션

5개 분석 영역과 옵션을 **한 화면에** 모두 보여준다. 선택된 항목이 ON, 선택 안 된 항목이 OFF이다. 기본값으로 ON인 항목을 명확히 표시한다.

```
AskUserQuestion(
    questions=[{
        "question": "활성화할 분석 영역과 옵션을 선택하세요 (선택 = ON, 미선택 = OFF)",
        "header": "분석 설정",
        "multiSelect": true,
        "options": [
            {"label": "문서화 분석 (doc)", "description": "세션에서 문서화할 지식 식별 [기본: ON]"},
            {"label": "컨텍스트 분석 (context)", "description": "CLAUDE.md/AGENTS.md 업데이트/삭제 제안 [기본: ON]"},
            {"label": "설정 분석 (settings)", "description": "permissions, hooks, env 개선 제안 [기본: ON]"},
            {"label": "스킬 분석 (skills)", "description": "스킬 갭/개선/미사용 스킬 식별 [기본: ON]"}
        ]
    },
    {
        "question": "추가 옵션을 선택하세요 (선택 = ON, 미선택 = OFF)",
        "header": "추가 옵션",
        "multiSelect": true,
        "options": [
            {"label": "워크플로우 분석 (workflow)", "description": "반복 패턴, 비효율, 병렬화 가능 지점 [기본: ON]"},
            {"label": "Auto 모드", "description": "세션 종료 시 자동 분석 실행 [기본: OFF]"},
            {"label": "Full 스캔", "description": "스킬 본문까지 상세 분석 (토큰 소모 증가) [기본: OFF, quick]"},
            {"label": "토큰 사용량 표시", "description": "결과에 리소스 추정 포함 [기본: ON]"}
        ]
    }]
)
```

**해석 규칙:**
- 선택된 분석 영역 → `analyzers.{area}.enabled = true`
- 선택 안 된 분석 영역 → `analyzers.{area}.enabled = false`
- "Auto 모드" 선택 → `auto.enabled = true`
- "Full 스캔" 선택 → `skills.scanMode = "full"`
- "토큰 사용량 표시" 선택 → `output.showTokenUsage = true`

### 라운드 3 — 모델 설정

AskUserQuestion으로 모델 조정 여부를 확인한다.

```
AskUserQuestion(
    questions=[{
        "question": "에이전트 모델을 조정할까요? (opus는 더 정밀하지만 느리고 비쌈)",
        "header": "모델 설정",
        "multiSelect": false,
        "options": [
            {"label": "전체 sonnet (추천)", "description": "모든 에이전트를 sonnet으로 실행 — 빠르고 균형 잡힌 성능"},
            {"label": "context만 opus", "description": "CLAUDE.md 분석 품질 향상, 나머지 sonnet"},
            {"label": "전체 opus", "description": "모든 에이전트를 opus로 — 최고 품질, 느리고 비쌈"}
        ]
    }]
)
```

사용자가 "Other"를 선택하면 개별 영역별 모델을 자유롭게 지정할 수 있다.

## 3단계: Config 파일 생성/업데이트

인터뷰 결과를 바탕으로 config를 생성한다.

### setting 모드

기존 config를 읽고 변경된 항목만 업데이트. 변경 전/후를 diff로 표시:

```markdown
## 설정 변경 사항

- analyzers.context.model: sonnet → opus
- auto.enabled: false → true
- skills.scanMode: quick → full
```

### 생성 후 검증

```markdown
## 설정 완료

설정 파일: `~/.claude/self-evolve-config.json`

### 활성 영역
✓ 문서화 분석 (sonnet)
✓ 컨텍스트 분석 (sonnet)
✓ 설정 분석 (sonnet)
✓ 스킬 분석 (sonnet)
✓ 워크플로우 분석 (sonnet)

### 문서화 대상
- Obsidian: ~/second-brain/
- 커스텀 커맨드: /brain-log

### 자동화
- Auto 모드: OFF
- 스캔 모드: quick
- 토큰 표시: ON
```

### 퀵스타트 안내

설정 완료 후 다음 메시지를 표시한다:

```markdown
## 설정 완료!

바로 사용할 수 있습니다:
- `/self-evolve` — 전체 분석 시작
- `/self-evolve --auto` — Quick Win 자동 적용
- `/self-evolve help` — 전체 사용법 보기
```

## 4단계: 훅 등록 (auto 모드 활성화 시)

auto 모드를 활성화한 경우, AskUserQuestion으로 훅 등록 여부를 확인:

```
AskUserQuestion(
    questions=[{
        "question": "세션 종료 시 자동 분석을 위한 Stop 훅을 등록할까요?",
        "header": "Auto 훅",
        "multiSelect": false,
        "options": [
            {"label": "등록 (추천)", "description": "settings.json에 Stop 훅 추가 — 세션 종료 시 /self-evolve --auto 자동 실행"},
            {"label": "건너뛰기", "description": "나중에 수동으로 등록 가능"}
        ]
    }]
)
```

등록 시 `~/.claude/settings.json`의 hooks에 추가:
```json
"Stop": [{ "matcher": "", "hooks": [{ "type": "command", "command": "echo '[MAGIC KEYWORD: self-evolve --auto]'" }] }]
```

## 주의사항

- 한국어로 대화
- **모든 사용자 입력은 AskUserQuestion으로 받는다** — 텍스트로 질문하지 않는다
- 추천값을 먼저 제시하고 사용자가 조정하게 한다
- 설정이 너무 복잡해지지 않도록 — 대부분 기본값이 적절
- setting 모드에서는 전체를 다시 묻지 않고 변경할 부분만 질문
