#!/usr/bin/env bash
# Download the Texas Linux Fest 2026 logos from a pinned commit of
# github.com/TXLF/2026website and prepare them for the demo.
# Requires: curl, ImageMagick 7 (`magick`).
set -euo pipefail

TXLF_SHA="${TXLF_SHA:-8f5c478b37fa52d12763284f228af2583b09c91f}"
BASE="https://raw.githubusercontent.com/TXLF/2026website/${TXLF_SHA}/static/images"
DEST="$(cd "$(dirname "$0")/.." && pwd)/files/branding"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$DEST"
for f in logo.png footer-logo.png about-logo.png favicon.png; do
  curl -fsSL -o "$TMP/$f" "$BASE/$f"
done

cp "$TMP/logo.png" "$TMP/about-logo.png" "$TMP/favicon.png" "$DEST/"

# footer-logo.png is 3279x749 and white: resize to 280px wide for the dark masthead.
magick "$TMP/footer-logo.png" -resize 280x -strip \
  -define png:compression-level=9 -define png:compression-filter=5 \
  "$DEST/footer-logo-280.png"

# about-logo.png (800x800) is only shown at ~200px; shrink it to keep ConfigMaps/Secrets small.
magick "$TMP/about-logo.png" -resize 400x400 -strip \
  -define png:compression-level=9 "$DEST/about-logo.png"

cat > "$DEST/SOURCE.md" <<MD
# Branding source

All files come from https://github.com/TXLF/2026website at commit \`${TXLF_SHA}\`.

| File | Upstream path | Changes |
|---|---|---|
| logo.png | static/images/logo.png | none |
| footer-logo-280.png | static/images/footer-logo.png | resized to 280px wide, stripped |
| about-logo.png | static/images/about-logo.png | resized to 400x400, stripped |
| favicon.png | static/images/favicon.png | none |

See ../../NOTICE for usage terms.
MD

ls -l "$DEST"
