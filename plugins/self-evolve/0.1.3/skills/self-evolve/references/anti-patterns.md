# Tool Anti-Patterns 카탈로그

workflow-analyzer가 도구 사용 비효율을 식별할 때 참조하는 카탈로그.
각 안티패턴은 ID(AP-NNN), 검출 시그널, 권장 대안을 가진다.

---

## AP-001: Bash로 grep/rg 호출

**검출**: `Bash` 도구의 `command`가 `^(grep|rg)( |$)`로 시작
**문제**:
- Claude Code의 `Grep` 도구는 ripgrep 기반으로 권한 처리, 결과 포맷, 컨텍스트 옵션이 최적화됨
- 사용자가 도구 호출 의도를 더 정확히 검토할 수 있음

**권장**:
```
❌ Bash("grep -n 'foo' src/")
✅ Grep(pattern="foo", path="src/", output_mode="content", -n=true)
```

**예외**: `git grep`, 파이프라인 일부로 grep 사용(`cmd | grep ...`)은 OK

---

## AP-002: Bash로 cat/head/tail 호출

**검출**: `Bash`의 `command`가 `^(cat|head|tail)( |$)`로 시작
**문제**:
- `Read` 도구는 line number 형식, offset/limit, 이미지·PDF·노트북 처리 등 풍부한 기능 제공
- Bash로 cat하면 라인 번호가 없어 후속 Edit 위치 지정이 어려움

**권장**:
```
❌ Bash("cat /path/to/file.md")
❌ Bash("head -50 /path/to/file.md")
✅ Read(file_path="/path/to/file.md")
✅ Read(file_path="/path/to/file.md", limit=50)
```

**예외**: 파이프라인 (`cat foo.json | jq ...`)은 OK

---

## AP-003: Bash로 find/ls 호출

**검출**: `Bash`의 `command`가 `^(find|ls)( |$)`로 시작
**문제**:
- `Glob` 도구는 패턴 기반 파일 검색에 최적화, 결과를 mtime 정렬로 반환
- find의 복잡한 표현식보다 glob 패턴이 더 직관적이고 안전

**권장**:
```
❌ Bash("find . -name '*.md'")
❌ Bash("ls plugins/self-evolve/")
✅ Glob(pattern="**/*.md")
✅ Glob(pattern="plugins/self-evolve/*")
```

**예외**: `ls -la`로 권한·소유자 등 메타데이터 확인은 OK

---

## AP-004: Bash로 sed/awk 인플레이스 편집

**검출**: `Bash`의 `command`가 `sed -i`, `awk ... > tmp && mv` 등
**문제**:
- 파일 편집은 `Edit` 도구로 정확한 diff 확인 가능
- sed/awk 편집은 의도치 않은 다중 매치 위험

**권장**:
```
❌ Bash("sed -i 's/foo/bar/g' file.md")
✅ Edit(file_path="...", old_string="foo", new_string="bar", replace_all=true)
```

**예외**: 파이프라인 변환 (`grep ... | awk '{print $2}'`)은 OK (편집이 아님)

---

## AP-005: 단일-tool 메시지 반복 (병렬화 누락)

**검출**: `Session Tool Stats`의 `단일-tool 메시지 비율 ≥70%`
**문제**:
- 독립적인 도구 호출을 한 메시지에 묶지 않으면 round-trip이 N배로 늘어남
- 사용자 경험·토큰·시간 모두 손해

**권장**:
- 한 메시지 안에 독립 호출을 함께 발행
- 예: 여러 파일 동시 Read, 독립 Grep 동시 실행

**참고**: 의존성 있는 호출(앞 결과로 다음 호출 결정)은 순차여야 한다. 비율이 100%인 경우는 거의 없다는 점 감안.

---

## AP-006: 동일 파일 반복 Read

**검출**: `Session Tool Stats`의 `반복 Read (≥2회)` 항목
**문제**:
- 같은 파일을 여러 번 Read하면 토큰 낭비 + context 압박
- 캐시된 file state는 LLM이 활용해야 함

**권장**:
- 첫 Read 결과를 메모리에서 활용
- 파일이 정말 변경되었는지 확인 후에만 재Read
- 여러 파일을 검토할 거면 한 메시지에 모두 Read

---

## AP-007: 동일 패턴 반복 Grep

**검출**: `Session Tool Stats`의 `반복 Grep (≥2회)` 항목
**문제**:
- 같은 검색을 반복하는 건 보통 검색 범위가 너무 좁거나 결과를 다시 찾는 것
- 한 번에 더 넓은 범위로 검색하면 끝남

**권장**:
- 첫 Grep 결과를 활용
- 범위를 좁게 잡았다면 디렉토리 확장
- 결과를 잊었다면 메시지 위로 스크롤 (재호출 X)

---

## AP-008: 도구 실패 후 동일 도구 재시도

**검출**: `Session Tool Stats`의 `도구 실패` 항목 — `is_error=true` 직후 동일 `tool_use_id`의 도구 재호출
**문제**:
- 같은 접근법으로 실패 후 재시도는 사전 검증이 부족했다는 신호
- 대표 케이스: Edit이 file_path 미존재로 실패 → 같은 file_path에 Edit 재시도 (Read 먼저 했어야 함)
- 대표 케이스: Bash 명령이 syntax 오류로 실패 → 같은 명령에 살짝 변경 후 재시도 (이미 한 번 실패한 접근법 고집)

**권장**:
- Edit 실패 시: 항상 Read를 먼저 (Edit tool은 Read 후에만 동작 보장)
- Bash 실패 시: 에러 메시지를 정확히 읽고 근본 원인 진단, 같은 카테고리 명령 반복 금지
- 동일 파일에 N회 Edit 실패: file_path 자체를 의심 (오타? 경로 변경?)

**예외**: 의도적인 retry-with-different-args (예: 빌드 실패 → 다른 환경 변수로 재시도)는 OK

---

## (폐기) Hook 경고 카운트

> 초기 설계에서 PreToolUse hook reminder 발화 카운트를 시그널 #6으로 사용하려 했으나, **Claude Code transcript에 hook reminder가 영속화되지 않음**을 검증으로 확인. 런타임 system-reminder injection만 발생하고 jsonl에는 저장되지 않는다.
>
> 카운트하려면 사용자가 PostToolUse hook으로 별도 로그 파일(`~/.claude/self-evolve-hook-log.jsonl`)을 만들어야 한다. 이는 사전 설치가 필요하므로 self-evolve 기본 시그널에서 제외했다. 향후 옵트인 기능으로 추가 가능.

---

## 카탈로그 확장 가이드

새 안티패턴 추가 시:
1. AP-NNN ID 부여 (순차)
2. **검출** 섹션은 `Session Tool Stats`에서 자동 추출 가능한 형태로 작성
3. **권장** 섹션에 ❌ / ✅ 코드 블록 포함
4. **예외** 섹션으로 false positive 케이스 명시
5. workflow-analyzer 출력 표의 "카탈로그" 컬럼에서 ID 인용 가능하도록 함

> 카탈로그가 커지면 검색을 위해 ID/제목 색인을 상단에 추가한다.
