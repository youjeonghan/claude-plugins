# Hook Integration Guide

self-evolve 스킬을 자동으로 트리거하는 두 가지 훅 연동 방식.

## 1. OMC UserPromptSubmit 키워드 감지 (자연어 트리거)

사용자가 "self-evolve", "자기개선", "환경 개선" 등의 키워드를 입력하면 스킬이 자동 로드되는 방식.

이미 SKILL.md의 description에 트리거 키워드가 포함되어 있어 별도 설정 없이 동작:
```
트리거: self evolve, self-evolve, 자기개선, 환경 개선, 세션 개선, 세션 분석 개선, improve session, evolve
```

## 2. settings.json Stop 훅 등록 (자동 트리거)

세션 종료 시 자동으로 self-evolve를 실행하려면 Stop 훅을 등록한다.

### 설정 방법

`~/.claude/settings.json`의 `hooks` 섹션에 추가:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo '[MAGIC KEYWORD: self-evolve --auto]'"
          }
        ]
      }
    ]
  }
}
```

### 주의사항

- `auto.enabled`가 `true`인 경우에만 자동 트리거가 의미 있음
- `auto.minSessionDuration` (기본 300초) 미만 세션에서는 트리거 안 됨
- `auto.minToolCalls` (기본 5회) 미만이면 트리거 안 됨
- 짧은 세션에서 불필요한 분석을 방지하는 가드

### auto 모드 동작 조건

Stop 훅에서 `--auto`로 트리거된 경우:
1. 세션 길이/복잡도 체크 (minSessionDuration, minToolCalls)
2. 조건 불충족 시 "세션이 짧아 분석을 건너뜁니다" 메시지만 출력
3. 조건 충족 시 전체 자동 분석 실행

## 3. /ralph 연동으로 분석 완수 보장

분석 에이전트가 타임아웃이나 기타 이유로 실패할 수 있다. 완수를 보장하려면:

### 기본 재시도 (SKILL.md 내장)

- 에이전트 실패 시 1회 자동 재시도
- 재시도 후에도 실패하면 해당 영역은 "분석 실패"로 보고하고 나머지 결과로 진행

### 미완료 추적

Stop 훅으로 중단된 경우:
1. 미완료 에이전트 목록을 `~/.claude/self-evolve-pending.json`에 저장
2. 다음 self-evolve 실행 시 pending 파일 확인
3. 미완료 영역만 재실행하여 이전 결과와 합산

```json
// ~/.claude/self-evolve-pending.json
{
  "timestamp": "2026-03-17T18:00:00Z",
  "pending": ["skills", "workflow"],
  "completed": {
    "doc": { "result": "..." },
    "context": { "result": "..." },
    "settings": { "result": "..." }
  }
}
```

## setup 시 훅 등록 안내

`/self-evolve setup`에서 `auto.enabled = true`로 설정하면:

1. settings.json에 Stop 훅 추가를 제안
2. 사용자 확인 후 `/update-config` 스킬로 훅 등록
3. 등록 완료 후 동작 방식 안내
