# Consolidation Template

Consolidator 에이전트가 Phase 1 결과를 통합할 때 사용하는 템플릿.

## Consolidator 지시

당신은 5개(+α) 분석 에이전트의 결과를 **통합하고 검증**하는 역할입니다.

### 작업 순서

1. **중복 제거** — 여러 에이전트가 같은 파일/설정에 대해 유사한 제안을 한 경우 병합
   - 완전 중복: 하나만 남기고 출처를 병기
   - 부분 중복: 더 구체적인 제안을 채택하고 나머지는 참고로 병기

2. **충돌 검증** — 제안 간 모순이 있는 경우 식별
   - 예: context-analyzer가 섹션 삭제를 제안하는데 doc-analyzer가 같은 섹션에 추가를 제안
   - 충돌 발견 시 양쪽 근거를 비교하여 권장안 제시

3. **기존 상태 대조** — Context Bundle의 현재 파일 내용과 제안을 대조
   - 이미 존재하는 내용과 동일한 제안은 "이미 반영됨"으로 표시
   - 기존 내용과 충돌하는 제안은 명시적으로 표시

4. **우선순위 분류** — 각 제안을 아래 기준으로 재분류
   - 분석 결과가 없는 우선순위 등급은 섹션을 생략한다
   - 활성화된 영역만 리소스 추정에 포함한다
   - customAnalyzer 결과도 동일한 우선순위 분류에 통합한다

### 우선순위 기준

| 등급 | 기준 | 예시 |
|------|------|------|
| **Quick Win** | 즉시 적용 가능, 위험 낮음, 되돌리기 쉬움 | permissions 추가, 오타 수정, frontmatter 보완 |
| **Standard** | 검토 후 적용, 중간 영향도 | CLAUDE.md 섹션 추가, 스킬 description 수정, 훅 등록 |
| **Major** | 신중한 검토 필요, 높은 영향도 | 새 스킬 생성, 워크플로우 재구성, 아키텍처 변경 |

Context Bundle 크기는 입력으로 전달받은 문자수로 추정:
```
영문 문자수 / 4 + 비영문 문자수 / 1.5
```

## 출력 형식

```markdown
## Self-Evolve 통합 분석 결과

### Quick Win (즉시 적용 가능)

| # | 영역 | 제안 | 대상 | 출처 |
|---|------|------|------|------|
| 1 | settings | permissions.allow에 `Bash(npm:*)` 추가 | settings.json | settings-analyzer |
| 2 | skills | slack 스킬 description에 `with:` 추가 | slack/SKILL.md | skills-analyzer |

#### 상세

**1. permissions.allow에 Bash(npm:*) 추가**
- 대상: `~/.claude/settings.json` > `permissions.allow`
- 변경:
  ```json
  "Bash(npm:*)"
  ```
- 근거: 세션 중 5회 수동 승인

---

### Standard (검토 후 적용)

| # | 영역 | 제안 | 대상 | 출처 |
|---|------|------|------|------|
| 3 | context | CLAUDE.md에 상품코드 규칙 추가 | ./CLAUDE.md | context-analyzer |

#### 상세

**3. CLAUDE.md에 상품코드 규칙 추가**
- 대상: `./CLAUDE.md` > CPL 섹션
- 변경:
  ```markdown
  ### 상품코드 규칙
  [내용]
  ```
- 근거: 세션에서 상품코드 구조를 조사하고 정리함

---

### Major (신중한 검토 필요)

| # | 영역 | 제안 | 대상 | 출처 |
|---|------|------|------|------|
| 5 | skills | 새 스킬 생성: notion-image-viewer | ~/.claude/skills/ | skills-analyzer |

#### 상세

**5. 새 스킬 생성: notion-image-viewer**
- 설명: [상세]
- 예상 구조: [파일 목록]
- 근거: [반복 패턴 설명]

---

### 충돌/중복 사항

| 제안 A | 제안 B | 유형 | 해결 |
|--------|--------|------|------|
| (없으면 이 섹션 생략) | | | |

---

### 리소스 사용 추정
- context bundle: ~N tokens (에이전트 공유)
- 분석 에이전트: N개 실행
- 총 input 추정: ~N tokens

※ output 토큰은 추정 불가하여 생략합니다.
```
