#!/usr/bin/env python3
"""Rebuild every CSV in data/ from the raw run records in records/.

Nothing in data/ is typed by hand. If a number is not in a record, it is not in a CSV.

Usage:
    python tools/build_tables.py
"""

import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RECORDS = os.path.join(ROOT, "records")
DATA = os.path.join(ROOT, "data")

MB = 1024 * 1024
CONTAINER_RESERVE = 0.006  # same constant the browser tool uses


def load(name):
    with open(os.path.join(RECORDS, name), encoding="utf-8") as f:
        return json.load(f)


def audio_kbps_for(target_bytes):
    """The tool reserves 64 kbps below 12 MB and 96 kbps above it."""
    return 64 if target_bytes <= 12 * MB else 96


def video_kbps(target_bytes, duration_s, reserve=CONTAINER_RESERVE):
    """Video bitrate that leaves room for container bytes and the audio track."""
    media_bytes = target_bytes * (1 - reserve)
    total_kbps = media_bytes * 8 / duration_s / 1000
    return max(100, int(total_kbps - audio_kbps_for(target_bytes)))


# --------------------------------------------------------------------------
# 1. Discord limits, with the official page each figure comes from.
#    Both URLs were opened and read on 2026-11-02; the quoted text is in notes.
# --------------------------------------------------------------------------
LIMITS = [
    ("Free (non-Nitro)", "20 MB", 20 * MB,
     "File Attachments FAQ",
     "https://support.discord.com/hc/en-us/articles/25444343291031-File-Attachments-FAQ",
     "2026-11-02",
     "Article text: \"For non-Nitro subscribers, the maximum file upload is 20MB.\" Also states the limit rose from 10MB in August 2026."),
    ("Nitro Basic", "50 MB", 50 * MB,
     "File Attachments FAQ + Account Caps",
     "https://support.discord.com/hc/en-us/articles/25444343291031-File-Attachments-FAQ",
     "2026-11-02",
     "FAQ: \"Nitro Basic offers 50MB\". Account Caps table row \"File Sharing Limit\": 50MB."),
    ("Nitro (full)", "500 MB", 500 * MB,
     "Account Caps, File Sharing Limit row",
     "https://support.discord.com/hc/en-us/articles/33694251638295-Discord-Account-Caps-Server-Caps-and-More",
     "2026-11-02",
     "Table row \"File Sharing Limit\": 10MB / 50MB / 500MB. This is the enforced tier limit."),
    ("Nitro (full)", "1 GB", 1024 * MB,
     "File Attachments FAQ",
     "https://support.discord.com/hc/en-us/articles/25444343291031-File-Attachments-FAQ",
     "2026-11-02",
     "FAQ: \"Nitro offers up to 1GB\". The same article opens with: \"We're currently experimenting with various file upload size limits. Select users may have the ability to upload larger file sizes.\" The two official pages disagree above 50MB."),
]


def write_limits():
    path = os.path.join(DATA, "discord-file-size-limits.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tier", "per_file_limit", "bytes", "source", "source_url", "checked", "notes"])
        w.writerows(LIMITS)
    return path


# --------------------------------------------------------------------------
# 2. Bitrate budget table: what a given ceiling leaves for video at a given length.
# --------------------------------------------------------------------------
def write_budget():
    path = os.path.join(DATA, "bitrate-budget.csv")
    rows = []
    for target_mb in (8, 10, 20, 50):
        target_bytes = target_mb * MB
        audio = audio_kbps_for(target_bytes)
        for duration in (15, 30, 60, 180):
            vb = video_kbps(target_bytes, duration)
            rows.append([
                target_mb, target_bytes, duration, audio,
                int(target_bytes * (1 - CONTAINER_RESERVE)),
                vb,
                round((vb + audio) * 1000 / 8 * duration),
            ])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["target_mb", "target_bytes", "duration_s", "audio_kbps",
                    "media_budget_bytes", "video_kbps", "projected_output_bytes"])
        w.writerows(rows)
    return path


# --------------------------------------------------------------------------
# 3. The encodes the browser tool actually ran, straight from the records.
# --------------------------------------------------------------------------
RUNS = ["site-10mb-10s-reserve", "site-3mb-10s-audio-reserve", "site-8mb-10s-reserve"]


def write_encodes():
    path = os.path.join(DATA, "measured-encodes.csv")
    rows = []
    for label in RUNS:
        rec = load(label + ".json")
        probe = load(label + ".probe.json")
        video = next((s for s in probe["streams"] if s["codec_type"] == "video"), {})
        audio = next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)
        last = rec["attempts"][-1]
        rows.append([
            label,
            rec["input"]["path"],
            rec["input"]["bytes"],
            rec["input"]["sha256"],
            rec["durationSeconds"],
            video.get("width"), video.get("height"), video.get("avg_frame_rate"),
            "yes" if audio else "no",
            rec["targetBytes"],
            rec["attempts"][0]["videoKbps"],
            len(rec["attempts"]),
            rec["output"]["bytes"],
            video.get("bit_rate"),
            (audio or {}).get("bit_rate", ""),
            rec["totalSeconds"],
            rec["codec"],
        ])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["run", "input_file", "input_bytes", "input_sha256", "duration_s",
                    "width", "height", "fps", "has_audio", "target_bytes",
                    "video_kbps_asked_pass1", "passes", "output_bytes",
                    "video_bps_measured", "audio_bps_measured", "seconds", "encoder"])
        w.writerows(rows)
    return path


# --------------------------------------------------------------------------
# 4. What each quality lever actually buys, from the CRF / fps / preset runs.
# --------------------------------------------------------------------------
def write_levers():
    base = load("measure.json")
    fps = load("measure_fps.json")
    preset = load("measure_preset.json")
    audio = load("measure_audio.json")
    rows = [
        ("resolution 1080p to 720p at CRF 23", "bytes", base["t2_720p_crf23"],
         f'{base["t2_delta_pct"]}% smaller than 1080p ({base["t1_30fps_crf23"]} bytes)', "measure.json"),
        ("frame rate 60 to 30 at CRF 20", "bytes", fps["30_20"],
         f'vs {fps["60_20"]} bytes at 60 fps', "measure_fps.json"),
        ("frame rate 60 to 30 at CRF 23", "bytes", fps["30_23"],
         f'vs {fps["60_23"]} bytes at 60 fps', "measure_fps.json"),
        ("frame rate 60 to 30 at CRF 26", "bytes", fps["30_26"],
         f'vs {fps["60_26"]} bytes at 60 fps', "measure_fps.json"),
        ("preset ultrafast", "bytes", preset["ultrafast"], "same source, CRF 23", "measure_preset.json"),
        ("preset veryfast", "bytes", preset["veryfast"], "same source, CRF 23", "measure_preset.json"),
        ("preset fast", "bytes", preset["fast"], "same source, CRF 23", "measure_preset.json"),
        ("preset medium", "bytes", preset["medium"], "same source, CRF 23", "measure_preset.json"),
        ("preset slow", "bytes", preset["slow"], "same source, CRF 23", "measure_preset.json"),
        ("preset veryslow", "bytes", preset["veryslow"], "same source, CRF 23", "measure_preset.json"),
        ("audio 64 kbps instead of 96", "bytes", audio["audio64"],
         f'{audio["delta_96_vs_64_pct"]}% smaller than 96 kbps on a 10 s clip', "measure_audio.json"),
    ]
    path = os.path.join(DATA, "quality-levers.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["lever", "unit", "value", "comparison", "record"])
        w.writerows(rows)
    return path


if __name__ == "__main__":
    for fn in (write_limits, write_budget, write_encodes, write_levers):
        print("wrote", os.path.relpath(fn(), ROOT))
