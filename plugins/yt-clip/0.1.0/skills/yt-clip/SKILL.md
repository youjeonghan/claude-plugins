---
name: yt-clip
description: 유튜브 링크에서 원하는 구간(초·분:초)만 잘라 mp4 짤이나 mp3 소리로 저장한다. "이 영상 54초~57초 따줘", "유튜브 구간 잘라줘", "이거 소리만 따줘", "앞 1초 더 잘라줘" 같은 요청에 사용. 여러 구간을 한 번에, 전체(full)도 가능.
---

# yt-clip — 유튜브 구간 자르기

`scripts/yt_clip.py` 하나로 처리한다. yt-dlp는 uv가 자동 설치하고, ffmpeg만 PATH에 있으면 된다.

## 준비 확인

```bash
which ffmpeg uv   # Windows: where ffmpeg uv
```

- ffmpeg 없음 → macOS `brew install ffmpeg` / Windows `winget install ffmpeg`
- uv 없음 → https://docs.astral.sh/uv/ 설치 안내. uv 대신 `pip install yt-dlp` 후 `python yt_clip.py ...`도 된다.

## 실행

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/yt-clip/scripts/yt_clip.py" URL 구간... [옵션]
```

| 인자 | 뜻 |
|---|---|
| `구간` | `54-57`, `0:54-0:57`, `1:02:03-1:02:10`, 소수 허용(`2.5-4`), `full`=전체. 여러 개 나열 가능 |
| `--name` | 파일명 앞부분 (기본: 영상 제목). 묶음이면 영문 소문자-하이픈 권장 |
| `--out` | 저장 폴더 (기본 `~/Downloads/clips`) |
| `--audio` | mp3로 저장 |
| `--trim-start N` | 받은 뒤 앞에서 N초 더 자르기 (재인코딩) |

출력: 파일명 `{name}_{시작}-{끝}s.mp4`, 끝나면 `경로<TAB>길이`를 줄마다 출력한다.

## 진행

1. 사용자가 준 링크·구간을 그대로 인자로 옮긴다. "처음부터 2초"는 `0-2`.
2. 같은 주제 묶음이면 `--out ~/Downloads/<주제>`와 `--name`을 정해 준다.
3. 실행 후 출력된 길이가 요청 구간과 맞는지 보고한다(키프레임 강제 컷이라 보통 정확).
4. 미세 조정 요청("앞 1초 더")은 기존 파일에 ffmpeg로 직접 처리하거나 `--trim-start`로 다시 받는다.
5. 아이폰으로 보내기: macOS면 `open -R <파일>` 후 Finder에서 공유 → AirDrop 안내.

## 주의

- 저작권 있는 영상은 개인 편집·참고용으로만 쓴다.
- 로그인·연령 제한 영상은 실패할 수 있다(`--cookies-from-browser` 필요 — 스크립트 미지원, 필요하면 yt-dlp를 직접 호출).
