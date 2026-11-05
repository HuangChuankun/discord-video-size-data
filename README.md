# Discord video size data

**Archived on Zenodo with a DOI — cite [10.5281/zenodo.23904987](https://doi.org/10.5281/zenodo.23904987) if you reuse these tables.**

Discord's per-file upload limits, the bitrate those limits leave you, and measured encodes to check the arithmetic against — as CSV, plus a small calculator.

Every number here traces back to a file in [`records/`](records/): either an official Discord page (URL and quoted text in the CSV) or an encode that was actually run, with input sha256, encoder settings, output byte count and elapsed time.

## What's in here

| File | What it answers |
|---|---|
| [`data/discord-file-size-limits.csv`](data/discord-file-size-limits.csv) | What each account tier can upload, in bytes, with the official page each figure comes from |
| [`data/bitrate-budget.csv`](data/bitrate-budget.csv) | For an 8, 10, 20 or 50 MB ceiling and a 15 s to 3 min clip, the video bitrate you can afford |
| [`data/measured-encodes.csv`](data/measured-encodes.csv) | Three encodes run through a browser ffmpeg.wasm build: what was asked for, what came out |
| [`data/quality-levers.csv`](data/quality-levers.csv) | What resolution, frame rate, x264 preset and audio bitrate each buy you, measured |
| [`tools/bitrate_budget.py`](tools/bitrate_budget.py) | The formula as a CLI: target size + duration in, video bitrate out |
| [`records/`](records/) | The raw JSON each CSV is generated from, including `ffprobe` output for each encode |

Rebuild every CSV from the records with:

```bash
python tools/build_tables.py
```

## Discord's limits, as of 2026-11-02

| Tier | Per file | Source |
|---|---|---|
| Free (non-Nitro) | 20 MB | File Attachments FAQ — "For non-Nitro subscribers, the maximum file upload is 20MB" |
| Nitro Basic | 50 MB | File Attachments FAQ and the Account Caps table agree |
| Nitro (full) | 500 MB | Account Caps table, "File Sharing Limit" row |
| Nitro (full) | up to 1 GB | File Attachments FAQ — "Nitro offers up to 1GB" |

The two official pages disagree above 50 MB. The FAQ also opens with "We're currently experimenting with various file upload size limits. Select users may have the ability to upload larger file sizes." The Account Caps table is the limit the tier actually enforces, so 500 MB is the figure to plan for; 1 GB is a bonus if your account has it. Both URLs are in the CSV, with the quoted sentence that produced each row.

## The arithmetic

File size is bitrate multiplied by duration, and nothing else. Once the size is fixed, the length of the clip fixes the bitrate:

```
target_bytes   = target_mb * 1024 * 1024
media_bytes    = target_bytes * (1 - 0.006)      # container reserve
total_kbps     = media_bytes * 8 / duration_s / 1000
video_kbps     = floor(total_kbps - audio_kbps)  # 64 kbps under 12 MB, 96 kbps above
```

The 0.006 reserve exists because an MP4 is not only media: it carries headers and a `moov` index of every frame, and those bytes come out of the budget whether you plan for them or not. Two earlier encodes, at a 3 MB and a 2.8 MB target, landed 0.43% and 0.44% over their target with no reserve in the formula; the same 3 MB run landed 0.22% under once the reserve was added. That is the whole reason the constant is in the formula.

```bash
$ python tools/bitrate_budget.py 20 30
target            20 MB = 20,971,520 bytes
media budget      20,845,690 bytes (after 0.600% container reserve)
total             5558.9 kbps over 30 s
audio             96 kbps
video             5462 kbps
projected output  20,842,500 bytes
```

## The measured encodes

| Input | Target | Passes | Output | Video asked → measured |
|---|---|---|---|---|
| 15,942,580 B, 1280x720 @ 30 fps, no audio track | 10 MB | 2 | 9,253,520 B | 8,274 kbps → overshot to 10,880,120 B, retry at 7,032 kbps → 7,399,220 bps |
| 5,407,489 B, 1920x1080 @ 60 fps, AAC stereo | 3 MB | 1 | 3,138,651 B | 2,437 kbps → 2,432,889 bps, audio 63,940 bps |
| 15,942,580 B, 1280x720 @ 30 fps, no audio track | 8 MB | 2 | 7,345,513 B | 6,606 kbps → overshot to 8,685,880 B, retry at 5,615 kbps → 5,872,840 bps |

All three finished at or under the target on the final pass. The 10 MB and 8 MB runs are the retry rule in action: x264 at a high bitrate can spend more than you asked for, and a single pass cannot promise a ceiling. The 8 MB run is the newest (2026-11-05); its raw record and matching `ffprobe` output are in [`records/`](records/).

## Coverage and limits

These three runs are a check on the arithmetic, not a validation suite. Every one uses a 10 s clip, and only two distinct source files appear (15,942,580 B without an audio track, and 5,407,489 B with one). There is no systematic set across durations, resolutions, frame rates, codecs or container conditions, and no independent reproduction by a third party. Consistent target-size performance across the range of supported media is therefore **not established by this data**. The CSV columns state what was measured; nothing here is an estimate.

## Licence

Code (`tools/`) is MIT. The CSV files and records are CC BY 4.0 — use them, just say where they came from.

The browser tool these numbers were measured on is at [compressmyclip.com](https://compressmyclip.com/) — same encoder, same reserve, nothing uploaded. The write-ups behind two of the targets are the [8 MB guide](https://compressmyclip.com/8mb-video-compressor) and the [10 MB guide](https://compressmyclip.com/10mb-video-compressor); each quotes the same run record published here.
