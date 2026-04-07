# claude-plugins

개인용 Claude Code 플러그인 모음.

## 플러그인 목록

| 이름 | 버전 | 설명 |
|------|------|------|
| self-evolve | 0.1.3 | 세션 분석 후 환경 자동 개선 — 5개 영역 병렬 분석 + 선택적 적용 |

## 설치

### 마켓플레이스로 설치 (권장)

Claude Code에서 아래 명령어 실행:

```bash
# 1. 마켓플레이스 등록 (최초 1회)
/plugin marketplace add youjeonghan/claude-plugins

# 2. 플러그인 설치
/plugin install self-evolve@youjeonghan-claude-plugins
```

### 업데이트

```bash
/plugin marketplace update
```

### 수동 설치 (대안)

```bash
git clone https://github.com/youjeonghan/claude-plugins.git ~/claude-plugins
mkdir -p ~/.claude/plugins
ln -s ~/claude-plugins/plugins/self-evolve/0.1.3 ~/.claude/plugins/self-evolve
```

수동 업데이트:

```bash
cd ~/claude-plugins && git pull
```
