---
name: self-evolve-help
description: 'self-evolve 스킬 사용법 안내'
---

# Self-Evolve 도움말

사용자에게 아래 내용을 그대로 표시한다.

## self-evolve 사용법

### 기본 명령어

| 명령어 | 설명 |
|--------|------|
| `/self-evolve` | 전체 5영역 인터랙티브 분석 |
| `/self-evolve --auto` | Quick Win 자동 적용 + 롤백 선택 |
| `/self-evolve --area X,Y` | 선택 영역만 분석 (doc,context,settings,skills,workflow) |
| `/self-evolve --scan quick\|full` | 스킬 스캔 범위 (기본: quick) |
| `/self-evolve --dry-run` | 분석만 수행, 적용하지 않음 |
| `/self-evolve help` | 이 도움말 표시 |
| `/self-evolve setup` | 초기 설정 (인터랙티브) |
| `/self-evolve setting` | 설정 변경 |

### 옵션 조합

```
/self-evolve --auto --area doc,skills --scan full
/self-evolve --dry-run --area settings
```

### 분석 영역

| 영역 | 설명 |
|------|------|
| doc | 세션에서 문서화할 지식 식별, 저장 위치 제안 |
| context | CLAUDE.md/AGENTS.md/project-memory 업데이트/삭제 제안 |
| settings | permissions, hooks, env 개선 제안 |
| skills | 스킬 갭/개선/미사용 스킬 식별 |
| workflow | 반복 패턴, 비효율, 병렬화 가능 지점 |

### 우선순위

| 등급 | 의미 |
|------|------|
| Quick Win | 즉시 적용 가능, 위험 낮음 |
| Standard | 검토 후 적용 권장 |
| Major | 신중한 검토 필요 |

### 설정

- 설정 파일: `~/.claude/self-evolve-config.json`
- `/self-evolve setup`으로 인터랙티브 설정 가능
- 설정 없이도 기본값으로 정상 동작

### 퀵스타트

1. 설치: `ln -s ~/claude-plugins/plugins/self-evolve/0.1.0 ~/.claude/plugins/self-evolve`
2. 세션 재시작
3. `/self-evolve setup` (선택 — 기본값으로도 동작)
4. `/self-evolve` — 바로 사용!
