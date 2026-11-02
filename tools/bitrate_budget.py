#!/usr/bin/env python3
"""Work out the video bitrate that fits a target file size.

The container and the audio track are not free: an MP4 carries headers plus a moov
index of every frame, and the audio stream takes its bitrate before the video gets
anything. This module subtracts both, so the number it returns is what the video
stream can actually spend.

    python tools/bitrate_budget.py 20 30          # 20 MB target, 30 second clip
    python tools/bitrate_budget.py 20 30 --audio 96

Formula, with every input spelled out:

    target_bytes   = target_mb * 1024 * 1024
    media_bytes    = target_bytes * (1 - 0.006)      # container reserve
    total_kbps     = media_bytes * 8 / duration_s / 1000
    video_kbps     = total_kbps - audio_kbps         # floored, minimum 100
    projected_size = (video_kbps + audio_kbps) * 1000 / 8 * duration_s

The 0.006 reserve is measured, not guessed: two encodes through the browser tool
landed 0.43% and 0.44% over their target before the reserve existed, and under it
afterwards. See records/ and data/measured-encodes.csv.
"""

import argparse

MB = 1024 * 1024
CONTAINER_RESERVE = 0.006


def audio_kbps_for(target_bytes):
    """64 kbps up to a 12 MB target, 96 kbps above it."""
    return 64 if target_bytes <= 12 * MB else 96


def budget(target_mb, duration_s, audio_kbps=None, reserve=CONTAINER_RESERVE):
    """Return a dict of every intermediate value, so nothing is hidden."""
    target_bytes = int(round(target_mb * MB))
    if audio_kbps is None:
        audio_kbps = audio_kbps_for(target_bytes)
    media_bytes = target_bytes * (1 - reserve)
    total_kbps = media_bytes * 8 / duration_s / 1000
    video_kbps = max(100, int(total_kbps - audio_kbps))
    projected = (video_kbps + audio_kbps) * 1000 / 8 * duration_s
    return {
        "target_bytes": target_bytes,
        "media_budget_bytes": int(media_bytes),
        "total_kbps": round(total_kbps, 1),
        "audio_kbps": audio_kbps,
        "video_kbps": video_kbps,
        "projected_output_bytes": int(round(projected)),
    }


def main():
    ap = argparse.ArgumentParser(description="Video bitrate that fits a target file size.")
    ap.add_argument("target_mb", type=float)
    ap.add_argument("duration_s", type=float)
    ap.add_argument("--audio", type=int, default=None, help="audio kbps (default 64, or 96 above 12 MB)")
    ap.add_argument("--reserve", type=float, default=CONTAINER_RESERVE)
    a = ap.parse_args()

    b = budget(a.target_mb, a.duration_s, a.audio, a.reserve)
    print(f"target            {a.target_mb:g} MB = {b['target_bytes']:,} bytes")
    print(f"media budget      {b['media_budget_bytes']:,} bytes (after {a.reserve:.3%} container reserve)")
    print(f"total             {b['total_kbps']} kbps over {a.duration_s:g} s")
    print(f"audio             {b['audio_kbps']} kbps")
    print(f"video             {b['video_kbps']} kbps")
    print(f"projected output  {b['projected_output_bytes']:,} bytes")


if __name__ == "__main__":
    main()
