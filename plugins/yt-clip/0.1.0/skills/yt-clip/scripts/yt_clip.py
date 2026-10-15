# /// script
# requires-python = ">=3.9"
# dependencies = ["yt-dlp"]
# ///
"""유튜브 영상에서 원하는 구간만 잘라 mp4(또는 mp3)로 저장한다.

사용 예:
  uv run yt_clip.py URL 0:54-0:57
  uv run yt_clip.py URL 2-7 9-10 --name usagi-ringtone --out ~/Downloads/chiikawa-sounds
  uv run yt_clip.py URL full --audio            # 전체를 mp3로
  uv run yt_clip.py URL 41-44 --trim-start 1    # 받은 뒤 앞 1초 더 자르기

구간 표기: 초(54) · 분:초(0:54) · 시:분:초(1:02:03), 소수 허용(2.5). 'full'이면 전체.
필요: ffmpeg가 PATH에 있어야 한다. yt-dlp는 uv가 자동 설치한다.
macOS·Windows·Linux 공통.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def to_seconds(t: str) -> float:
    parts = [float(p) for p in t.split(":")]
    sec = 0.0
    for p in parts:
        sec = sec * 60 + p
    return sec


def fmt(sec: float) -> str:
    s = f"{sec:g}"
    return s.replace(".", "_")


def safe(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "_", name).strip() or "clip"


def ffprobe_duration(path: Path) -> str:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)],
            capture_output=True, text=True, check=True).stdout.strip()
        return f"{float(out):.2f}s"
    except Exception:
        return "?"


def main() -> int:
    ap = argparse.ArgumentParser(description="유튜브 구간 자르기 (yt-dlp + ffmpeg)")
    ap.add_argument("url")
    ap.add_argument("ranges", nargs="+", help="구간들: 54-57, 0:54-0:57, full")
    ap.add_argument("--name", help="파일명 앞부분 (기본: 영상 제목)")
    ap.add_argument("--out", default=str(Path.home() / "Downloads" / "clips"),
                    help="저장 폴더 (기본 ~/Downloads/clips)")
    ap.add_argument("--audio", action="store_true", help="mp3로 저장 (소리만)")
    ap.add_argument("--trim-start", type=float, default=0.0,
                    help="받은 뒤 앞에서 더 자를 초")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        print("ffmpeg가 없습니다. macOS: brew install ffmpeg / Windows: winget install ffmpeg",
              file=sys.stderr)
        return 1

    import yt_dlp
    from yt_dlp.utils import download_range_func

    out_dir = Path(args.out).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    name = args.name
    if not name:
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as y:
            name = y.extract_info(args.url, download=False).get("title", "clip")
    name = safe(name)

    results = []
    for r in args.ranges:
        if r.lower() == "full":
            start = end = None
            stem = f"{name}_full"
        else:
            a, b = r.split("-", 1)
            start, end = to_seconds(a), to_seconds(b)
            stem = f"{name}_{fmt(start)}-{fmt(end)}s"

        tmp_stem = stem + ".part-dl"
        opts = {
            "quiet": True,
            "noprogress": True,
            "no_warnings": True,
            "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
            "merge_output_format": "mp4",
            "outtmpl": str(out_dir / f"{tmp_stem}.%(ext)s"),
        }
        if start is not None:
            opts["download_ranges"] = download_range_func(None, [(start, end)])
            opts["force_keyframes_at_cuts"] = True
        with yt_dlp.YoutubeDL(opts) as y:
            y.download([args.url])

        src = next(out_dir.glob(f"{tmp_stem}.*"))
        ext = "mp3" if args.audio else "mp4"
        if args.trim_start and start is not None:
            stem = f"{name}_{fmt(start + args.trim_start)}-{fmt(end)}s"
        dst = out_dir / f"{stem}.{ext}"

        cmd = ["ffmpeg", "-loglevel", "error", "-y"]
        if args.trim_start:
            cmd += ["-ss", str(args.trim_start)]
        cmd += ["-i", str(src)]
        if args.audio:
            cmd += ["-vn", "-c:a", "libmp3lame", "-q:a", "2"]
        elif args.trim_start:
            cmd += ["-c:v", "libx264", "-crf", "18", "-c:a", "aac"]
        else:
            cmd += ["-c", "copy"]
        cmd.append(str(dst))
        subprocess.run(cmd, check=True)
        src.unlink()
        results.append(dst)

    for p in results:
        print(f"{p}\t{ffprobe_duration(p)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
