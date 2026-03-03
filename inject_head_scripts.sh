#!/bin/bash
# Inject Klotho static JS loader into all built HTML pages.
# Run after `myst build --html` and after copying static/ into _build/html/.
#
# The loader detects the site's base URL from MyST's own CSS <link> tags,
# then loads the four static JS files (scheduler, draw, bridge, boot).

set -e

BUILD_HTML="${1:-_build/html}"

LOADER_FILE=$(mktemp)
cat > "$LOADER_FILE" << 'ENDOFLOADER'
<style>[data-name="outputs-container"]>div>.p-2\.5{display:none}article{animation:klothoFadeIn .3s ease-in}@keyframes klothoFadeIn{from{opacity:0}to{opacity:1}}</style><script>(function(){var b="/";try{var e=document.querySelector('link[href*="/build/"]');if(e)b=e.href.replace(/\/build\/.*$/,"/");}catch(x){}["static/scheduler.js","static/scheduler_score.js","static/draw.js","static/animation_bridge.js","static/klotho_boot.js"].forEach(function(f){var s=document.createElement("script");s.src=b+f;s.async=false;document.head.appendChild(s);});})();</script>
ENDOFLOADER
LOADER=$(cat "$LOADER_FILE" | tr -d '\n')
rm "$LOADER_FILE"

COUNT=0
while IFS= read -r htmlfile; do
    if grep -q 'klotho_boot' "$htmlfile" 2>/dev/null; then
        continue
    fi
    python3 -c "
import sys
tag = sys.argv[1]
path = sys.argv[2]
data = open(path).read()
data = data.replace('</head>', tag + '</head>', 1)
open(path, 'w').write(data)
" "$LOADER" "$htmlfile"
    COUNT=$((COUNT + 1))
done < <(find "$BUILD_HTML" -name "index.html")

echo "  Injected Klotho head scripts into $COUNT HTML files"
