#!/usr/bin/env bash
# Export the slide decks (English and Spanish) to PDF and editable PowerPoint.
#
#   workshop/tools/export-slides.sh
#
# Output: workshop/exports/kubevirt-without-fear-slides-{en,es}.{pdf,pptx}
# Needs Google Chrome, Chromium or Microsoft Edge (PDF) and uv or python-pptx (PowerPoint).
# Put the lab sheet QR code at workshop/assets/qr/lab-sheet.png before the final export.
set -euo pipefail

WORKSHOP="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$WORKSHOP/exports"
QR="$WORKSHOP/assets/qr/lab-sheet.png"
mkdir -p "$OUT"

find_chrome() {
  if [[ -n "${CHROME:-}" ]]; then echo "$CHROME"; return; fi
  local c
  for c in \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Chromium.app/Contents/MacOS/Chromium" \
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
    google-chrome google-chrome-stable chromium chromium-browser microsoft-edge; do
    if [[ -x "$c" ]] || command -v "$c" >/dev/null 2>&1; then echo "$c"; return; fi
  done
  echo "No Chrome, Chromium or Edge found. Set CHROME=/path/to/browser." >&2
  exit 1
}

run_pptx() {
  if command -v uv >/dev/null 2>&1; then
    uv run --quiet --with "python-pptx==1.0.2" python "$WORKSHOP/tools/build_pptx.py" "$@"
  elif python3 -c "import pptx" >/dev/null 2>&1; then
    python3 "$WORKSHOP/tools/build_pptx.py" "$@"
  else
    echo "Install uv (https://docs.astral.sh/uv/) or run: python3 -m pip install python-pptx" >&2
    exit 1
  fi
}

if [[ ! -f "$QR" ]]; then
  echo "Note: $QR is missing; the Module 1 slide will show an empty QR box."
fi

CHROME_BIN="$(find_chrome)"
for lang in en es; do
  if [[ $lang == en ]]; then page=slides.html; data=slides.js; else page=slides.es.html; data=slides.es.js; fi
  name="kubevirt-without-fear-slides-$lang"

  "$CHROME_BIN" --headless=new --disable-gpu --hide-scrollbars --window-size=1280,720 \
    --no-pdf-header-footer --virtual-time-budget=5000 \
    --print-to-pdf="$OUT/$name.pdf" "file://$WORKSHOP/$page?print" >/dev/null 2>&1
  echo "$OUT/$name.pdf"

  run_pptx "$WORKSHOP/$data" "$OUT/$name.pptx"
done
