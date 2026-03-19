# self-evolve

세션에서 수행한 작업을 메타 분석하여 환경을 자동 개선하는 플러그인.

## 기능

문서화, 프로젝트 컨텍스트, 설정, 스킬, 워크플로우 5개 영역을 병렬 분석하고 개선안을 제시합니다.

| 영역 | 분석 내용 |
|------|----------|
| 문서화 | 세션에서 문서화할 지식 식별, 저장 위치 제안 |
| 컨텍스트 | CLAUDE.md/AGENTS.md/project-memory 업데이트/삭제 제안 |
| 설정 | permissions, hooks, env 개선 제안 |
| 스킬 | 스킬 갭/개선/미사용 스킬 식별 |
| 워크플로우 | 반복 패턴, 비효율, 병렬화 가능 지점 |

## 퀵스타트

1. 설치: `ln -s ~/claude-plugins/plugins/self-evolve/0.1.0 ~/.claude/plugins/self-evolve`
2. 세션 재시작
3. `/self-evolve setup` (선택 — 설정 없이도 기본값으로 동작)
4. `/self-evolve` — 바로 사용!

## 사용법

```
/self-evolve                          # 전체 5영역 인터랙티브 분석
/self-evolve --auto                   # Quick Win 자동 적용 + 롤백 선택
/self-evolve --dry-run                # 변경사항 미리 보기 (실제 적용 없음)
/self-evolve --area doc,skills        # 선택 영역만 분석
/self-evolve --scan full              # 스킬 본문까지 상세 분석
/self-evolve setup                    # 초기 설정
/self-evolve setting                  # 설정 변경
/self-evolve help                     # 도움말 표시
```

## 특징

- **범용**: 어떤 프로젝트에서든 동작. 특정 도구에 비의존
- **파일 캐시**: `~/.claude/self-evolve-cache.json`에 변경 빈도 낮은 항목 캐시, TTL/변경감지로 갱신
- **토큰 리포트**: 분석 완료 후 에이전트별 토큰 소모량 테이블 표시
- **선택 적용**: Quick Win / Standard / Major 우선순위 분류 후 사용자가 선택
- **Dry-run 모드**: `--dry-run` 플래그로 실제 변경 없이 개선안 미리 확인

## 설정

`/self-evolve setup`으로 인터랙티브 설정. 설정 파일: `~/.claude/self-evolve-config.json`

설정 없이도 기본값으로 정상 동작합니다.
