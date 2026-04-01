---
name: self-evolve
description: "세션 분석 후 환경 자동 개선. 문서화, 프로젝트 컨텍스트, 설정, 스킬, 워크플로우 5개 영역을 병렬 분석하고 개선안을 제시. 트리거: self evolve, self-evolve, 자기개선, 환경 개선, 세션 개선, 세션 분석 개선, improve session, evolve"
argument-hint: "[setup | setting | help | --auto | --dry-run | --area doc,context,settings,skills,workflow | --scan quick|full]"
allowed-tools:
  - Bash(git *)
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# Self-Evolve: 세션 기반 환경 자동 개선

세션에서 수행한 작업을 메타 분석하여 문서화, 프로젝트 컨텍스트, 설정, 스킬, 워크플로우 5개 영역의 개선안을 제시하고 선택적으로 적용하는 스킬.

**범용성**: `~/.claude/skills/`(전역)에 설치되므로 어떤 프로젝트에서든 사용 가능. 현재 작업 디렉토리의 CLAUDE.md, AGENTS.md, .omc/, .claude/ 등을 자동 감지하여 분석.

## 실행 흐름

```
┌─────────────────────────────────────────────────────┐
│  1. 모드 판별 & 설정 로드                              │
├─────────────────────────────────────────────────────┤
│  2. 공통 컨텍스트 수집 (Context Bundle)                │
├─────────────────────────────────────────────────────┤
│  3. Phase 1: 분석 에이전트 (병렬)                      │
│     ┌──────────────┬──────────────┬──────────────┐  │
│     │ doc-analyzer │ context-     │ settings-    │  │
│     │              │ analyzer     │ analyzer     │  │
│     ├──────────────┼──────────────┼──────────────┤  │
│     │ skills-      │ workflow-    │ custom       │  │
│     │ analyzer     │ analyzer     │ analyzers    │  │
│     └──────────────┴──────────────┴──────────────┘  │
├─────────────────────────────────────────────────────┤
│  4. Phase 2: Consolidator (순차)                     │
│     ┌───────────────────────────────────┐           │
│     │  중복 제거 + 충돌 검증 + 우선순위 분류  │           │
│     └───────────────────────────────────┘           │
├─────────────────────────────────────────────────────┤
│  5. 결과 프레젠테이션 & 사용자 선택                     │
├─────────────────────────────────────────────────────┤
│  6. 선택 항목 실행 & 결과 보고                         │
└─────────────────────────────────────────────────────┘
```

## Step 1: 모드 판별 & 설정 로드

### 1-1. 인자 파싱

`$ARGUMENTS`를 파싱하여 모드를 결정한다:

| 인자 | 동작 |
|------|------|
| `setup` | `/self-evolve-setup` 커맨드로 위임 (초기 설정) |
| `setting` | `/self-evolve-setup` 커맨드로 위임 (설정 변경) |
| `--auto` | 전체 영역 자동 분석 + Quick Win 자동 적용 → 롤백 선택지 제시 |
| `--area X,Y` | 쉼표로 구분된 영역만 실행 (doc, context, settings, skills, workflow) |
| `--scan quick\|full` | 스킬 스캔 범위 (기본: quick) |
| `--dry-run` | 분석만 수행, 적용 안 함 (결과 확인용) |
| `help` | 도움말 표시. `/self-evolve-help` 커맨드로 위임 |
| 인자 없음 | 전체 영역 인터랙티브 분석 |

인자는 조합 가능: `--auto --area doc,skills --scan full`

**옵션 조합 우선순위**:
- `--dry-run` + `--auto` → `--dry-run`이 우선. 분석만 수행하고 자동 적용하지 않음.
- `--dry-run` + `--area X` → 선택 영역만 분석, 적용 안 함. 정상 조합.

### 1-2. 설정 로드

`~/.claude/self-evolve-config.json`을 읽는다. 파일이 없으면 아래 기본값을 사용:

```json
{
  "version": "1.0.0",
  "documentation": {
    "enabled": true,
    "targets": [],
    "customCommand": null
  },
  "projectContext": {
    "enabled": true,
    "files": ["CLAUDE.md", "AGENTS.md"],
    "projectMemory": true,
    "staleDays": 30
  },
  "globalSettings": {
    "enabled": true,
    "scope": ["permissions", "hooks", "env"]
  },
  "skills": {
    "enabled": true,
    "scanPaths": [".claude/skills", ".claude/commands"],
    "scanMode": "quick"
  },
  "workflow": {
    "enabled": true,
    "minRepetitionCount": 2
  },
  "analyzers": {
    "doc": { "enabled": true, "model": "sonnet" },
    "context": { "enabled": true, "model": "sonnet" },
    "settings": { "enabled": true, "model": "sonnet" },
    "skills": { "enabled": true, "model": "sonnet" },
    "workflow": { "enabled": true, "model": "sonnet" }
  },
  "customAnalyzers": [],
  "auto": {
    "enabled": false,
    "triggerEvents": ["Stop"],
    "minSessionDuration": 300,
    "minToolCalls": 5
  },
  "cache": {
    "enabled": true,
    "path": "~/.claude/self-evolve-cache.json",
    "ttlMinutes": 60,
    "targets": ["skills-metadata", "settings", "claude-md"]
  },
  "exclusions": {
    "paths": [],
    "areas": []
  },
  "output": {
    "verbose": false,
    "maxSuggestionsPerArea": 5,
    "showTokenUsage": true
  }
}
```

설정 파일을 로드한 뒤 `references/self-evolve-config.schema.json`의 스키마와 대조하여 검증한다:
- 스키마와 맞지 않는 필드 → 경고 출력 후 해당 필드는 기본값 사용
- config에 정의되지 않은 알 수 없는 필드 → 무시 (forward compatibility)

`--area` 인자가 있으면 해당 영역만 enabled로 처리. config의 `exclusions.areas`에 포함된 영역은 비활성.

## Step 2: 공통 컨텍스트 수집 (Context Bundle)

**모든 분석 에이전트가 공유하는 컨텍스트를 한 번만 수집한다.** 에이전트가 개별로 같은 파일을 Read하는 중복을 제거.

### 2-1. 파일 캐시 확인

`cache.enabled`가 true이면 `~/.claude/self-evolve-cache.json`을 먼저 확인한다.

**캐시 구조:**
```json
{
  "version": "1.0.0",
  "createdAt": "2026-03-17T18:00:00Z",
  "gitDiffStat": "3 files changed, 45 insertions(+), 12 deletions(-)",
  "sections": {
    "skills-metadata": {
      "updatedAt": "2026-03-17T18:00:00Z",
      "content": "..."
    },
    "settings": {
      "updatedAt": "2026-03-17T18:00:00Z",
      "content": "..."
    },
    "claude-md": {
      "updatedAt": "2026-03-17T18:00:00Z",
      "content": "..."
    }
  }
}
```

**캐시 갱신 룰:**

| 조건 | 동작 |
|------|------|
| 캐시 파일 없음 | 전체 수집 후 캐시 생성 |
| TTL 초과 (`cache.ttlMinutes`, 기본 60분) | 전체 갱신 |
| `git diff --stat` 출력이 캐시의 `gitDiffStat`과 다름 | 전체 갱신 (코드 변경 감지) |
| 특정 섹션만 원본 파일 mtime이 캐시 `updatedAt`보다 새로움 | 해당 섹션만 갱신 |
| `--scan full` 인자 사용 | 스킬 메타데이터 섹션을 본문 포함으로 갱신 |

**캐시 대상 (변경 빈도 낮은 항목만):**
- `skills-metadata`: 스킬 frontmatter (또는 full 시 본문)
- `settings`: `~/.claude/settings.json`, `settings.local.json`
- `claude-md`: 전역 + 프로젝트 CLAUDE.md, AGENTS.md

**캐시 비대상 (항상 실시간 수집):**
- Git 상태 (`git status`, `git diff --stat`, `git log`)
- 최근 수정 파일 목록
- 세션 대화 요약
- project-memory, .omc/ 상태 (있으면)

### 2-2. 실시간 수집 항목

캐시 여부와 무관하게 **항상 새로 수집**하는 항목:

**Git 상태:**
```bash
git status --short
git diff --stat
git log --oneline -10
```

**최근 수정 파일:**
```bash
git diff --name-only HEAD~5 2>/dev/null || git diff --name-only
```

**세션 대화 요약:**
- 현재까지의 세션 작업 내용을 3-5줄로 요약 생성

### 2-3. 선택적 수집 (있으면 활용, 없으면 무시)

아래 항목은 존재 여부를 먼저 확인하고, 있을 때만 bundle에 포함:

- `.omc/project-memory.json` — OMC 설치 환경에서만 존재
- `.omc/state/` — OMC 실행 상태 (OMC 없으면 생략)
- `./AGENTS.md` — 프로젝트에 따라 없을 수 있음
- `~/.claude/settings.local.json` — 없을 수 있음

> **독립성 원칙**: self-evolve는 OMC, Obsidian, 특정 프로젝트 구조에 의존하지 않는다. 이들은 "감지되면 추가 컨텍스트로 활용"할 뿐, 없어도 정상 동작한다.

### 2-4. Bundle 조합 & 캐시 저장

수집 완료 후:
1. 캐시 대상 항목을 `~/.claude/self-evolve-cache.json`에 저장 (cache.enabled일 때)
2. 실시간 + 캐시 + 선택적 항목을 합쳐 Context Bundle 문자열 생성

### Context Bundle 형식

```
=== CONTEXT BUNDLE ===

## Git Status
[git status output]

## Recent Changes
[git log + diff stat]

## Recently Modified Files
[file list]

## Global CLAUDE.md
[content or "없음"]

## Project CLAUDE.md
[content or "없음"]

## AGENTS.md
[content or "없음" — 파일 없으면 이 섹션 생략]

## Project Memory
[content or "없음" — .omc/ 없으면 이 섹션 생략]

## Settings
[settings.json content]

## Skills Metadata
[frontmatter list per skill]

## Session Summary
[session work summary]

=== END CONTEXT BUNDLE ===
```

**토큰 추정**: context bundle 크기를 다음 공식으로 추정하여 기록:
- 영문([a-zA-Z0-9]) 문자수 / 4 + 비영문 문자수 / 1.5

## Step 3: Phase 1 — 분석 에이전트 병렬 실행

config에서 enabled된 에이전트만 실행. **단일 메시지에서 모든 Agent 호출**을 병렬로 발행한다.

각 에이전트 프롬프트는 `references/analyzers/` 디렉토리의 해당 파일을 Read하여 구성한다:
- doc-analyzer → `references/analyzers/doc.md`
- context-analyzer → `references/analyzers/context.md`
- settings-analyzer → `references/analyzers/settings.md`
- skills-analyzer → `references/analyzers/skills.md`
- workflow-analyzer → `references/analyzers/workflow.md`

프롬프트 구조:

```
[Context Bundle 전체 내용]

---

[해당 에이전트 프롬프트 파일 내용]
```

### 에이전트 목록

| # | 에이전트 | model | 분석 영역 |
|---|---------|-------|----------|
| 1 | doc-analyzer | config.analyzers.doc.model | 문서화할 지식 식별, targets별 저장 제안 |
| 2 | context-analyzer | config.analyzers.context.model | CLAUDE.md/AGENTS.md/project-memory 업데이트/삭제 제안 |
| 3 | settings-analyzer | config.analyzers.settings.model | permissions, hooks, env 개선 제안 |
| 4 | skills-analyzer | config.analyzers.skills.model | 스킬 갭/개선/미사용 스킬 식별 |
| 5 | workflow-analyzer | config.analyzers.workflow.model | 반복 패턴, 비효율, 병렬화 가능 지점 |
| +α | custom analyzers | customAnalyzers[].model | 사용자 정의 분석 |

Agent 호출 형식:
```
Agent(
    subagent_type="general-purpose",
    model="{config에서 읽은 model}",
    description="{영역} 분석",
    prompt="[Context Bundle]\n---\n[해당 에이전트 프롬프트 파일 내용]"
)
```

### customAnalyzers 처리

config의 `customAnalyzers` 배열에 항목이 있으면 동일한 방식으로 추가 에이전트를 병렬 실행:

```json
{ "name": "security-check", "prompt": "보안 관련 개선점을 분석하세요", "model": "sonnet" }
```

custom analyzer도 동일한 context bundle을 프롬프트 앞에 주입받는다.

## Step 4: Phase 2 — Consolidator

Phase 1의 모든 결과를 수집한 후 **순차적으로** consolidator 에이전트를 실행한다.

```
Agent(
    subagent_type="general-purpose",
    model="sonnet",
    description="분석 결과 통합",
    prompt="[references/consolidation-template.md 읽기]\n\n[Phase 1 전체 결과]\n\n위 분석 결과를 통합하세요."
)
```

Consolidator의 역할:
1. **중복 제거** — 여러 에이전트가 같은 제안을 한 경우 병합
2. **충돌 검증** — 기존 파일 내용과 충돌하는 제안 식별
3. **우선순위 분류**:
   - **Quick Win**: 즉시 적용 가능, 위험 낮음 (permissions 추가, 오타 수정, frontmatter 보완 등)
   - **Standard**: 검토 후 적용 (CLAUDE.md 섹션 추가, 스킬 개선, 훅 등록 등)
   - **Major**: 신중한 검토 필요 (새 스킬 생성, 아키텍처 변경, 워크플로우 재구성 등)

## Step 5: 결과 프레젠테이션 & 사용자 선택

### dry-run 모드 (`--dry-run`)

`--dry-run`이면 Consolidator 결과를 표시한 뒤 **Step 6, 7을 건너뛰고 종료**한다. AskUserQuestion을 호출하지 않는다.

```markdown
## Self-Evolve 분석 결과 (dry-run)

[Consolidator 결과 동일 형식]

※ dry-run 모드: 적용 없이 분석 결과만 표시합니다.
```

### 인터랙티브 모드 (기본)

Consolidator 결과를 우선순위별로 표시한 뒤, **우선순위 등급별 1회씩** AskUserQuestion `multiSelect`로 일괄 선택받는다.

**절대 금지**: 항목마다 개별 AskUserQuestion을 순차 호출하지 않는다. 사용자를 기다리게 하는 왕복을 최소화한다.

**라벨 규칙**: `QW-1`, `ST-2` 같은 약어를 사용하지 않는다. label에 **변경 대상 파일: 변경 내용**을 직관적으로 표기한다 (예: `"Memory: PPU=48→32 업데이트"`, `"CLAUDE.md: Aseprite 임포트 순서 추가"`).

**흐름**: Quick Win → Standard → Major 순서로, 각 등급당 하나의 multiSelect 질문을 보낸다. 해당 등급에 항목이 없으면 건너뛴다. 선택된 항목은 즉시 적용하고 (또는 백그라운드 Agent에 위임하고) 다음 등급 질문으로 넘어간다.

```markdown
## Self-Evolve 분석 결과

### Quick Win (즉시 적용 가능)
- ☐ Memory: PPU=48→32 컨벤션 업데이트
- ☐ CLAUDE.md: sortingOrder 주의사항 추가

### Standard (검토 후 적용)
- ☐ CLAUDE.md: Aseprite 임포트 표준 순서 문서화
- ☐ CLAUDE.md: body/arm 렌더러 계층 구조 추가

### Major (신중한 검토 필요)
- ☐ 새 스킬: animator-setup (Animator 생성~클립 바인딩 원스톱)
```

**등급별 일괄 선택 (Quick Win 예시):**
```
AskUserQuestion(
    questions=[{
        "question": "Quick Win 항목 중 적용할 것을 선택하세요",
        "header": "Quick Win",
        "multiSelect": true,
        "options": [
            {"label": "Memory: PPU=48→32 컨벤션 업데이트", "description": "project_unity_conventions.md + MEMORY.md 인덱스 수정"},
            {"label": "CLAUDE.md: sortingOrder 주의사항 추가", "description": "스프라이트 규칙 섹션에 추가"},
            ...
        ]
    }]
)
```
→ 선택된 항목 즉시 적용 (또는 백그라운드 Agent로 위임하며 다음 등급 진행)
→ Standard, Major도 동일 패턴으로 각 1회 multiSelect 호출

### Auto 모드 (`--auto`)

1. Quick Win 항목을 **자동 적용**
2. 적용 완료 후 롤백 + 추가 적용 선택지 제시:

```
AskUserQuestion(
    questions=[{
        "question": "롤백할 항목 또는 추가 적용할 항목을 선택하세요",
        "header": "Self-Evolve 자동 개선 완료",
        "multiSelect": true,
        "options": [
            {"label": "↩ CLAUDE.md 변경 롤백", "description": "자동 적용됨"},
            {"label": "↩ permissions 변경 롤백", "description": "자동 적용됨"},
            {"label": "➕ 새 스킬 생성: notion-image-viewer", "description": "Standard"},
            {"label": "➕ 워크플로우 개선 적용", "description": "Major"}
        ]
    }]
)
```

3. `↩` 선택 시 → 해당 변경 되돌림 (Edit으로 원본 복원)
4. `➕` 선택 시 → 해당 항목 실행

## Step 6: 선택 항목 실행

사용자가 선택한 각 항목을 Write/Edit로 적용한다.

적용 유형별 처리:
- **permissions 추가**: `~/.claude/settings.json`의 `permissions.allow` 배열에 항목 추가
- **CLAUDE.md 수정**: 해당 파일을 Edit으로 섹션 추가/수정
- **project-memory 업데이트**: `.omc/project-memory.json` 수정
- **스킬 수정**: 해당 SKILL.md를 Edit
- **새 스킬 생성**: `/create-agent` 또는 직접 Write
- **훅 등록**: settings.json의 hooks 섹션 수정
- **커스텀 커맨드 호출**: config의 `documentation.customCommand` 실행 (예: `/brain-dump`)

## Step 7: 결과 보고

### 적용 요약

```markdown
## Self-Evolve 완료

### 적용됨
✓ permissions.allow에 Bash(npm:*) 추가
✓ CLAUDE.md에 CPL 상품코드 규칙 섹션 추가

### 스킵됨
- 새 스킬 생성: notion-image-viewer (사용자 선택 안 함)

### 롤백됨 (auto 모드 시)
↩ slack 스킬 변경 롤백
```

### 리소스 사용 추정 (`output.showTokenUsage: true`일 때)

```markdown
## 리소스 사용 추정
- context bundle: ~N tokens (에이전트 공유)
- 분석 에이전트: N개 실행
- 총 input 추정: ~N tokens

※ output 토큰은 추정 불가하여 생략합니다.
토큰 추정 공식: 영문 문자수 / 4 + 비영문 문자수 / 1.5
```

## 완수 보장

- 모든 에이전트가 결과를 반환할 때까지 대기
- 에이전트 실패 시 원인에 따라 전략 분기:
  - **timeout** → 동일 프롬프트로 재시도 (1회)
  - **error** (프롬프트 오류 등) → 에러 메시지를 프롬프트에 포함하여 재시도 (1회)
  - 재시도 후에도 실패 → "분석 실패" 보고 + 실패 원인 기록, 나머지 결과로 진행
- Stop 훅으로 중단된 경우, 미완료 분석 목록을 `~/.claude/self-evolve-pending.json`에 저장하여 다음 실행 시 이어서 수행

## 주의사항

- 한국어로 모든 출력 수행
- 기존 파일 수정 시 반드시 현재 내용을 Read한 뒤 Edit 사용
- permissions, hooks 등 민감한 설정 변경은 항상 구체적 변경 내용을 사용자에게 보여준 뒤 적용
- auto 모드에서도 Major 등급은 자동 적용하지 않음 (Quick Win만 자동)
- config 파일이 없어도 기본값으로 정상 동작해야 함
