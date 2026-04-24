# second-brain 0.2.0

LLM Wiki 패턴 기반 Obsidian Second Brain 볼트 운영 스킬.

## 구조 전제

볼트는 다음 구조를 가정한다:

```
<vault>/
├── knowledge/<도메인>/{sources,wiki,index.md}
├── projects/<프로젝트>/{sources,wiki,index.md,log.md}
└── archive/<연도>/
```

- `sources/`: 외부에서 가져온 원본 (immutable)
- `wiki/`: LLM이 합성·유지하는 페이지 (mutable)
- `index.md`: 폴더 카탈로그 (description rollup)
- `log.md`: 활동 로그 (append-only)

## 스킬

- `brain-ingest` — URL/파일/대화/이미지를 sources에 저장하고 관련 wiki 페이지를 연쇄 갱신
- `brain-query` — 자연어 질문 → index rollup grep → wiki 합성 답변
- `brain-lint` — description 누락, 중복, orphan, stale 등 헬스체크 및 승인형 자동 수정
- `brain-setup` (command) — `~/.claude/brain-config.json` 초기 설정 및 볼트 scaffolding

## 설정

`~/.claude/brain-config.json`:

```json
{
  "vault": {
    "path": "/absolute/path/to/vault",
    "version": 2
  },
  "project_workspaces": {
    "프로젝트명": "/absolute/path/to/project/repo"
  }
}
```

- `vault.path`: 볼트 경로 (필수)
- `project_workspaces`: 외부 프로젝트 디렉토리 ↔ 프로젝트명 매핑. 스킬이 `cwd`로 현재 프로젝트 추론 시 사용.

## 0.1.0에서 변경

- `brain-write` → `brain-ingest` (연쇄 wiki 갱신 추가)
- `brain-read` → `brain-query` (index rollup + save-as-wiki 옵션)
- `brain-cleanse` → `brain-lint` (stale·orphan·cross-ref 검사 추가)
- 볼트 구조: Projects/Resources/Archive → knowledge/projects/archive 3-레이어, sources/wiki 물리 분리
- frontmatter: type 4개(source/wiki/index/log), domain/layer 필드 제거
