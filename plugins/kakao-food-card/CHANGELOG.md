# Changelog — kakao-food-card

## [0.1.1] - 2026-11-06
### Fixed
- macOS·Windows 공통으로 동작하게 정비
  - 모든 파일 입출력을 UTF-8로 고정(Windows 기본 cp949에서 한글·이모지 깨짐 방지)
  - 표준출력도 UTF-8로 맞춰 리뷰 다이제스트 출력 오류 방지
  - `pick`을 macOS 전용 `sips` 대신 Pillow로 변환(EXIF 회전 반영), Pillow가 없는 macOS에서만 `sips`로 대체
  - `sheet`도 EXIF 회전을 반영, Pillow가 없으면 설치 안내 후 종료
- 가격 미기재 메뉴(`price: -1`)가 카드에 '-1원'으로 보이던 문제 수정
### Changed
- SKILL.md: 파이썬 실행기를 `$PY`(macOS `python3` / Windows `python`)로 표기, `pick`은 `-I` 없이 실행

## [0.1.0] - 2026-11-06
### Added
- 최초 버전: 맥 전역 스킬(`~/.claude/skills/kakao-food-card`)을 플러그인으로 이전
  - `scripts/kfc.py`, `template.html` 포함
  - 스크립트 경로를 `${CLAUDE_PLUGIN_ROOT}` 기준으로 변경
