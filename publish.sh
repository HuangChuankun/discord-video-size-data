#!/usr/bin/env bash
# Publishes this folder as a public GitHub repo, then prints the URL.
# Needs a GitHub login first:  gh auth login
set -euo pipefail
cd "$(dirname "$0")"
REPO="${1:-discord-video-size-data}"

gh auth status >/dev/null 2>&1 || { echo "Not signed in to GitHub. Run: gh auth login"; exit 1; }

git init -q 2>/dev/null || true
git add -A
git -c user.name="$(gh api user -q .login)" \
    -c user.email="$(gh api user -q .login)@users.noreply.github.com" \
    commit -qm "Discord file size limits, bitrate budgets, and measured encodes" || true

gh repo create "$REPO" --public --source=. --remote=origin --push \
  --description "Discord per-file upload limits, the bitrate those limits leave, and measured ffmpeg.wasm encodes behind the numbers." 

gh api "repos/{owner}/$REPO" -q .html_url
