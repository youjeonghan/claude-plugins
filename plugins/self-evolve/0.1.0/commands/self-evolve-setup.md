---
name: self-evolve-setup
description: 'self-evolve 스킬 설정 초기화 및 변경'
argument-hint: '[setting]'
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

**한 번에 모든 질문을 하지 않는다.** 답변에 따라 다음 질문을 조정한다.

### 라운드 1 — 문서화 대상 설정

탐색 결과를 기반으로 추천값을 제시:

> **Q1. 문서화 대상을 설정해주세요.**
>
> 세션에서 발견한 지식을 어디에 저장할지 설정합니다.
>
> 감지된 환경:
> - Obsidian 볼트: `~/second-brain/`
> - 문서화 스킬: `brain-dump`, `brain-log`
>
> 추천 설정:
> ```json
> "documentation": {
>   "enabled": true,
>   "targets": [
>     { "type": "obsidian", "path": "~/second-brain/" }
>   ],
>   "customCommand": "/brain-log"
> }
> ```
>
> 이 설정을 사용할까요? 수정이 필요하면 알려주세요.

사용자가 수락하거나 수정 사항을 알려주면 반영.

### 라운드 2 — 자동화 & 분석 설정

모든 항목을 추천값과 함께 한 번에 제시:

```
AskUserQuestion(
    questions=[{
        "question": "분석 설정을 확인해주세요",
        "header": "Self-Evolve 분석 설정",
        "multiSelect": true,
        "options": [
            {"label": "문서화 분석 (doc)", "description": "세션에서 문서화할 지식 식별 [기본: ON]"},
            {"label": "컨텍스트 분석 (context)", "description": "CLAUDE.md/AGENTS.md 업데이트 [기본: ON]"},
            {"label": "설정 분석 (settings)", "description": "permissions, hooks 개선 [기본: ON]"},
            {"label": "스킬 분석 (skills)", "description": "스킬 갭/개선 식별 [기본: ON]"},
            {"label": "워크플로우 분석 (workflow)", "description": "반복 패턴, 비효율 감지 [기본: ON]"},
            {"label": "Auto 모드 활성화", "description": "세션 종료 시 자동 실행 [기본: OFF]"},
            {"label": "Full 스캔 모드", "description": "스킬 본문까지 상세 분석 [기본: quick]"},
            {"label": "Dry-run 모드", "description": "분석만 수행, 적용 안 함 [기본: OFF]"},
            {"label": "토큰 사용량 표시", "description": "결과에 토큰 소모량 포함 [기본: ON]"}
        ]
    }]
)
```

기본값은 모든 분석 ON, auto OFF, quick 스캔, 토큰 표시 ON.
사용자가 선택을 변경하면 반영.

### 라운드 3 — 모델 설정 (선택)

> **Q. 에이전트별 모델을 조정할까요?**
>
> 기본값: 모든 에이전트 sonnet
> - 정밀 분석이 필요한 영역은 opus로 올릴 수 있습니다
> - 예: context-analyzer를 opus로 → CLAUDE.md 분석 품질 향상
>
> 기본값을 사용할까요, 아니면 특정 에이전트의 모델을 변경할까요?

대부분의 사용자는 기본값을 수락할 것이므로 간단히 확인만 받는다.

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

auto 모드를 활성화한 경우:

> **Q. 세션 종료 시 자동 실행을 위한 Stop 훅을 등록할까요?**
>
> `~/.claude/settings.json`에 다음 훅이 추가됩니다:
> ```json
> "Stop": [{ "matcher": "", "hooks": [{ "type": "command", "command": "echo '[MAGIC KEYWORD: self-evolve --auto]'" }] }]
> ```
>
> 등록할까요?

사용자 확인 후 settings.json에 훅 추가.

## 주의사항

- 한국어로 대화
- 추천값을 먼저 제시하고 사용자가 조정하게 한다
- 설정이 너무 복잡해지지 않도록 — 대부분 기본값이 적절
- setting 모드에서는 전체를 다시 묻지 않고 변경할 부분만 질문
