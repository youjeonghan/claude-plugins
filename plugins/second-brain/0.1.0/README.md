# second-brain

Claude Code와 연동된 Obsidian 지식 베이스를 관리하는 플러그인.

## 스킬

| 스킬 | 설명 |
|------|------|
| brain-read | 볼트에서 관련 문서를 검색·참조한다. description 프론트매터 인덱스를 우선 grep해 관련 파일만 선별적으로 읽어 응답 효율을 높인다. |
| brain-write | 볼트에 새 문서를 저장하거나 기존 도메인 문서를 업데이트한다. domain 필드 기반 upsert로 중복 문서 생성을 방지한다. |
| brain-cleanse | 볼트의 중복·분산된 도메인 문서를 탐지하고 병합 또는 분리한다. description/domain 프론트매터 일괄 추가 기능도 포함. |

## 설치

### 마켓플레이스로 설치 (권장)

Claude Code에서:

```bash
# 1. 마켓플레이스 등록 (최초 1회)
/plugin marketplace add youjeonghan/claude-plugins

# 2. 플러그인 설치
/plugin install second-brain@youjeonghan-claude-plugins
```

### 업데이트

```bash
/plugin marketplace update
```

### 수동 설치 (대안)

```bash
git clone https://github.com/youjeonghan/claude-plugins.git ~/claude-plugins
mkdir -p ~/.claude/plugins
ln -s ~/claude-plugins/plugins/second-brain/0.1.0 ~/.claude/plugins/second-brain
```

설치 후:

1. 세션 재시작
2. `/brain-setup` — Obsidian 볼트 경로 설정 및 폴더 구조 자동 생성

## 초기 설정

설치 후 `/brain-setup`을 실행하여 다음을 수행합니다:

- Obsidian 볼트 절대 경로 입력 (없으면 새로 생성)
- 기본 폴더 구조 (`Projects/`, `Resources/`) 자동 생성
- 설정 파일 `~/.claude/brain-config.json` 생성

설정이 완료되면 brain-read, brain-write, brain-cleanse를 바로 사용할 수 있습니다.

## 사용법

- **brain-read** — "프로젝트 설계 검색", "캐시 구현 방법 찾아줘" 등 쿼리로 볼트에서 관련 문서 검색
- **brain-write** — "설계 문서 저장", "학습 자료 추가" 등으로 새 문서 생성 또는 기존 문서 업데이트
- **brain-cleanse** — "문서 정리", "description 추가해줘" 등으로 중복 탐지 및 메타데이터 일괄 관리
