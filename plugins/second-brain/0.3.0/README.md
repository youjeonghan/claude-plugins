# second-brain 0.3.0

카파시 LLM Wiki 패턴 기반 Obsidian Second Brain 볼트 운영 스킬.

## 구조 전제

볼트는 단일 통합 wiki 구조를 가정한다:

```
<vault>/
├── sources/<영역>/   # 외부 원본 (immutable)
├── wiki/<영역>/      # LLM 합성·유지 페이지 (단일 그래프)
├── archive/          # 완료·중단 보관
├── index.md          # 영역별 description rollup
└── log.md            # 활동 로그 (append-only)
```

- `sources/`: 외부에서 가져온 원본 (immutable)
- `wiki/`: LLM이 합성·유지하는 페이지 (mutable), 영역은 하위폴더지만 단일 그래프
- `index.md`: 콘텐츠 카탈로그 (description rollup)
- `log.md`: 활동 로그 (append-only)

## 스킬

- `brain-ingest` — URL/파일/대화/이미지를 sources/<영역>에 저장하고 관련 wiki 페이지를 연쇄 갱신
- `brain-query` — 자연어 질문 → index rollup grep → wiki 합성 답변
- `brain-lint` — description 누락, 중복, orphan, stale, 아카이브 후보 등 헬스체크 및 승인형 자동 수정
- `brain-setup` (command) — `~/.claude/brain-config.json` 초기 설정 및 볼트 scaffolding

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
- `project_workspaces`: 외부 프로젝트 디렉토리 ↔ 프로젝트명 매핑. 스킬이 `cwd`로 현재 프로젝트(영역) 추론 시 사용.

## 0.2.0에서 변경

- 볼트 구조: knowledge/projects/archive 3-레이어 → **단일 통합 wiki** (최상위 sources/wiki/archive 각 1개, 영역은 하위폴더)
- 스킬: 레이어 판단 → 영역(area) 판단, 경로를 wiki/<영역>·sources/<영역>로 통일, 단일 root index·log
- brain-lint: 아카이브 후보 검사 추가
- brain-config: v2 → v3
