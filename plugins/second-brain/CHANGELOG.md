# Changelog — second-brain

## [0.1.0] - 2026-04-14
### Added
- `brain-read` 스킬 — Obsidian 볼트에서 description 인덱스를 grep해 관련 문서를 선별·참조
- `brain-write` 스킬 — 볼트에 새 문서 생성 또는 domain 기반 upsert로 기존 문서 업데이트
- `brain-cleanse` 스킬 — 중복 domain 문서 탐지·병합, description·domain 필드 일괄 추가
- `brain-setup` 커맨드 — 볼트 경로 설정, `~/.claude/brain-config.json` 생성/갱신, 볼트 폴더 구조 scaffolding (`Projects/`, `Resources/`, `README.md`)
