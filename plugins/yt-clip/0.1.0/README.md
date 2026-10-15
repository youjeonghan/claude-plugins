# yt-clip

유튜브 영상에서 원하는 구간만 잘라 mp4(또는 mp3)로 저장한다. macOS·Windows·Linux 공통.

## 설치

```bash
/plugin marketplace add youjeonghan/claude-plugins
/plugin install yt-clip@youjeonghan-claude-plugins
```

필요: `ffmpeg`, `uv` (yt-dlp는 uv가 자동 설치).

## Claude 없이 직접 쓰기

```bash
uv run skills/yt-clip/scripts/yt_clip.py "https://youtu.be/SD2kY5JmkpA" 2-7 9-10 --name usagi-ringtone
uv run skills/yt-clip/scripts/yt_clip.py "https://youtu.be/JB2CXmL-ASk" full --audio
uv run skills/yt-clip/scripts/yt_clip.py "https://youtu.be/jgYVHsjXrIA" 41-44 --trim-start 1
```

기본 저장 위치는 `~/Downloads/clips`(`--out`으로 변경).
