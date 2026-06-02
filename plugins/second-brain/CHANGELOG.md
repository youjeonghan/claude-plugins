# Changelog — second-brain

## 0.3.0 — 2026-06-02

### Breaking

- 볼트 구조: 3-레이어(knowledge/projects/archive) → **단일 통합 wiki**. 최상위 `sources/`·`wiki/`·`archive/` 각 1개, 영역은 하위폴더.
- brain-config `version` 2 → 3.
- frontmatter 간소화: `title`·`type` 필드 제거 — 종류는 폴더가, 제목은 파일명+H1이 표현.

### Changed

- `brain-ingest`/`brain-query`/`brain-lint`: 레이어 판단 → 영역(area) 판단, 경로 `wiki/<영역>`·`sources/<영역>` 통일, 단일 root `index.md`·`log.md`.
- `brain-setup`: 단일-wiki scaffolding(`sources/`·`wiki/`·`archive/`·`CLAUDE.md`), config v3. `_Standards.md` 생성 제거(CLAUDE.md 통합).

### Added

- `brain-lint` 아카이브 후보 검사 — 완료·중단 페이지를 `archive/` 이동 제안.

## 0.2.0 — 2026-04-22

### Breaking

- 볼트 구조 변경: `Projects/`, `Resources/`, `Archive/` → `knowledge/`, `projects/`, `archive/` 3-레이어
- 각 레이어 내부 `sources/` / `wiki/` 물리 분리
- frontmatter: `type` 값 4개 (`source|wiki|index|log`)로 축소, `domain` 및 `layer` 필드 제거, `updated` 필드 추가

### Added

- `brain-ingest` 스킬 — URL/파일/대화/이미지를 sources에 저장하고 관련 wiki 페이지 연쇄 갱신
- `brain-query` 스킬 — index.md description rollup grep + save-as-wiki 옵션
- `brain-lint` 스킬 — description·중복·orphan·stale·cross-ref 통합 헬스체크
- `project_workspaces` 매핑 — `~/.claude/brain-config.json`에서 외부 프로젝트 디렉토리 ↔ 프로젝트명 등록
- 루트 `index.md`, `log.md` 템플릿 자동 생성 (brain-setup)

### Changed

- `brain-write` → `brain-ingest` (흡수 + 연쇄 갱신)
- `brain-read` → `brain-query` (rollup + 저장 옵션)
- `brain-cleanse` → `brain-lint` (stale/orphan/cross-ref 검사 추가)
- `brain-setup` — config v2 스키마, LLM Wiki scaffolding

### Removed

- `domain` frontmatter 필드 (폴더 경로 + slug로 고유 키)
- `layer` frontmatter 필드 (폴더 경로로 표현)

### Migration

기존 0.1.0 사용자는 [마이그레이션 가이드](./0.2.0/README.md)를 참조.

## [0.1.0] - 2026-04-14
### Added
- `brain-read` 스킬 — Obsidian 볼트에서 description 인덱스를 grep해 관련 문서를 선별·참조
- `brain-write` 스킬 — 볼트에 새 문서 생성 또는 domain 기반 upsert로 기존 문서 업데이트
- `brain-cleanse` 스킬 — 중복 domain 문서 탐지·병합, description·domain 필드 일괄 추가
- `brain-setup` 커맨드 — 볼트 경로 설정, `~/.claude/brain-config.json` 생성/갱신, 볼트 폴더 구조 scaffolding (`Projects/`, `Resources/`, `README.md`)
