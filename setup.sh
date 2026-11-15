#!/usr/bin/env bash
# Installs MAGI-UI: fetches TomaszRewak/MAGI at a pinned commit, swaps in ai.py,
# applies main.py.patch, creates a virtualenv, and copies the sample results.
# The upstream graphics (components/, assets/) are not modified.
set -euo pipefail

UPSTREAM_URL="https://github.com/TomaszRewak/MAGI.git"
UPSTREAM_SHA="98a4d0184b1b0013e2216689c770127b6aff2efc"   # 2023-10-11, verified with this adapter

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-$HERE/MAGI}"

if [ -e "$TARGET" ]; then
  echo "Already exists: $TARGET (pass another path as the first argument)" >&2
  exit 1
fi

git clone -q "$UPSTREAM_URL" "$TARGET"
git -C "$TARGET" checkout -q "$UPSTREAM_SHA"

cp "$HERE/ai.py" "$TARGET/ai.py"
git -C "$TARGET" apply "$HERE/main.py.patch"

python3 -m venv "$TARGET/.venv"
"$TARGET/.venv/bin/pip" install -q -r "$HERE/requirements.lock"

mkdir -p "$TARGET/results"
cp "$HERE"/samples/0*.json "$TARGET/results/"   # 99_invalid.json stays in samples/
touch "$TARGET/results/01_passed.json"   # so "latest" opens a passed sample first

cat <<EOF

Installed: $TARGET
Run:
  cd "$TARGET"
  MAGI_RESULTS_DIR=results .venv/bin/python main.py
Open http://127.0.0.1:8050, type a file name (e.g. 02_passed_2of3.json) or latest
in the question field, and press Enter. Set MAGI_UI_LANG=ko for Korean labels.
EOF
