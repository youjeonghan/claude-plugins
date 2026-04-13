# second-brain 플러그인 설계

**날짜:** 2026-04-14  
**상태:** 승인됨

---

## 개요

기존에 로컬(`~/.claude/skills/`)에만 설치된 `brain-read`, `brain-write`, `brain-cleanse` 스킬 3개를 `claude-plugins` 레포에 `second-brain` 플러그인으로 패키징해 배포한다.

---

## 플러그인 구조

```
plugins/second-brain/0.1.0/
  .claude-plugin/plugin.json
  README.md
  commands/
    brain-setup.md
  skills/
    brain-read/SKILL.md
    brain-write/SKILL.md
    brain-cleanse/SKILL.md
```

### 스킬 목록

| 스킬 | 설명 |
|------|------|
| `brain-read` | Obsidian 볼트에서 description 인덱스를 우선 grep해 관련 문서를 선별·참조 |
| `brain-write` | 볼트에 새 문서를 생성하거나 domain 기반 upsert로 기존 문서를 업데이트 |
| `brain-cleanse` | 중복 domain 문서를 탐지하고 병합/분리, description·domain 필드 일괄 추가 |

### brain-setup 커맨드

볼트 경로를 물어보고 `~/.claude/brain-config.json`을 생성/갱신한다.

동작 흐름:
1. `~/.claude/brain-config.json` 존재 여부 확인
2. 있으면 현재 볼트 경로 표시 + 변경 여부 질문
3. 없으면 볼트 경로 입력 안내
4. 경로 유효성 확인 (디렉토리 존재 여부)
5. `brain-config.json` 생성/갱신

생성되는 파일 형식:
```json
{
  "vault": {
    "path": "/Users/youjeonghan/second-brain"
  }
}
```

---

## plugin.json

```json
{
  "name": "second-brain",
  "version": "0.1.0",
  "description": "Obsidian Second Brain 볼트를 Claude Code에서 읽고, 쓰고, 정리하는 스킬 모음",
  "author": {
    "name": "youjeonghan",
    "url": "https://github.com/youjeonghan"
  },
  "repository": "https://github.com/youjeonghan/claude-plugins",
  "license": "MIT",
  "skills": "./skills/",
  "commands": "./commands/"
}
```

---

## marketplace.json 변경

루트 `.claude-plugin/marketplace.json`의 `plugins` 배열에 추가:

```json
{
  "name": "second-brain",
  "description": "Obsidian Second Brain 볼트 읽기·쓰기·정리 스킬 모음",
  "version": "0.1.0",
  "source": "./plugins/second-brain/0.1.0",
  "category": "productivity",
  "tags": ["second-brain", "obsidian", "notes", "knowledge"]
}
```

---

## 전제 조건

- 스킬 설치 후 `/brain-setup`을 먼저 실행해 볼트 경로를 설정해야 한다.
- 세 스킬 모두 `~/.claude/brain-config.json`의 `vault.path`를 Step 0에서 읽는다.

---

## 구현 방식

**Approach A (선택): 단순 직접 포팅**

- 기존 `~/.claude/skills/brain-*/SKILL.md` 파일을 그대로 복사
- 공통 로직(Step 0) 중복이 있지만 스킬 3개 규모에서는 무시 가능
- 기존 스킬 이름(`brain-read` 등) 그대로 유지해 사용 패턴 보존

---

## 버전

`0.1.0` — 초기 배포
