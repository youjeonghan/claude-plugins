# second-brain 0.4.0

카파시 LLM Wiki 패턴 기반 Obsidian Second Brain 볼트 운영 스킬. **Claude Code·Codex 공용.**

## 단일 진실원본: 볼트 매뉴얼

볼트의 운영 매뉴얼은 `CLAUDE.md`다(정본). `AGENTS.md`는 그 심볼릭 링크라 Codex가 같은 내용을 읽는다. **규약(frontmatter·파일명·포맷)과 운영 절차(ingest/query/lint)가 모두 이 매뉴얼에 있고**, 스킬은 그걸 읽고 따르는 얇은 진입점이다.

## 구조 전제

```
<vault>/
├── sources/<영역>/   # 외부 원본 (immutable)
├── wiki/<영역>/      # LLM 합성·유지 페이지 (단일 그래프)
├── archive/          # 완료·중단 보관
├── CLAUDE.md         # 운영 매뉴얼 (단일 진실원본)
├── AGENTS.md         # → CLAUDE.md 심볼릭 링크 (Codex 진입점)
├── index.md          # 영역별 description rollup
└── log.md            # 활동 로그 (append-only)
```

## 스킬 (Claude Code 진입점)

- `brain-ingest` — URL/파일/대화/이미지를 흡수 → 매뉴얼 §7 Ingest 수행
- `brain-query` — 자연어 질문 → 매뉴얼 §7 Query 수행
- `brain-lint` — 헬스체크·수정 → 매뉴얼 §7 Lint 수행
- `brain-setup` (command) — `~/.claude/brain-config.json` 설정 + 볼트 scaffolding(CLAUDE.md 매뉴얼 + AGENTS.md 심볼릭 포함)

> Codex 등 스킬이 없는 환경에선 `CLAUDE.md`(= 심볼릭 `AGENTS.md`)의 §7을 직접 따르면 동일하게 동작한다.

## 설정

`~/.claude/brain-config.json`:

```json
{
  "vault": {
    "path": "/absolute/path/to/vault",
    "version": 3
  },
  "project_workspaces": {
    "프로젝트명": "/absolute/path/to/project/repo"
  }
}
```

- `vault.path`: 볼트 경로 (필수)
- `project_workspaces`: 외부 프로젝트 디렉토리 ↔ 프로젝트명 매핑. 스킬이 `cwd`로 현재 영역 추론 시 사용.

## 0.3.0에서 변경

- **스킬 슬림화**: brain-ingest/query/lint가 절차·규약을 복붙하지 않고 볼트 매뉴얼 §7을 읽고 따르는 얇은 진입점으로. 규약 출처가 1곳(매뉴얼)이라 드리프트가 사라짐.
- **Codex 호환**: 매뉴얼을 `CLAUDE.md`(단일 진실원본)로 두고 `AGENTS.md`는 그 심볼릭 링크. 운영 워크플로우가 매뉴얼 §7에 수록돼 스킬 없는 Codex도 동작.
- **brain-setup**: scaffolding이 `CLAUDE.md`(매뉴얼)+`AGENTS.md`(심볼릭)를 생성.
