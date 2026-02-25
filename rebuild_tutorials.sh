#!/bin/bash

# Klotho Tutorials Rebuild Script
# Re-executes tutorial notebooks so saved outputs reflect current code.
# Automatically skips placeholder notebooks (no code cells) and
# widget-dependent notebooks (require a live kernel / Binder).

set -e

TUTORIALS_DIR="."

should_skip() {
    python3 -c "
import json, sys

with open(sys.argv[1]) as f:
    nb = json.load(f)

code_sources = [
    ''.join(c.get('source', []))
    for c in nb.get('cells', [])
    if c['cell_type'] == 'code'
]

if not code_sources:
    print('no-code')
    sys.exit(0)

combined = '\n'.join(code_sources)
widget_markers = ['ipywidgets', 'pn.widgets', 'panel.widgets', 'interact(', 'pn.Column', 'pn.Row']
if any(m in combined for m in widget_markers):
    print('widgets')
    sys.exit(0)

print('run')
" "$1"
}

echo "Collecting tutorial notebooks..."

NOTEBOOKS=()
SKIPPED=()
while IFS= read -r nb; do
    result=$(should_skip "$nb")
    if [ "$result" != "run" ]; then
        echo "  SKIP ($result): $(basename "$nb")"
        SKIPPED+=("$(basename "$nb")")
        continue
    fi
    NOTEBOOKS+=("$nb")
done < <(find "$TUTORIALS_DIR" -name "*.ipynb" -not -path "*/.ipynb_checkpoints/*" | sort)

if [ ${#NOTEBOOKS[@]} -eq 0 ]; then
    echo "No notebooks found to convert."
    exit 0
fi

echo ""
echo "Converting ${#NOTEBOOKS[@]} notebooks (${#SKIPPED[@]} skipped)..."
echo ""

FAILED=()
SUCCEEDED=()

for nb in "${NOTEBOOKS[@]}"; do
    name=$(basename "$nb")
    echo "--- $name ---"
    if jupyter nbconvert --to notebook --execute --inplace --allow-errors "$nb" 2>&1; then
        SUCCEEDED+=("$name")
    else
        echo "  FAILED: $name"
        FAILED+=("$name")
    fi
    echo ""
done

echo "=============================="
echo "  ${#SUCCEEDED[@]} succeeded"
echo "  ${#SKIPPED[@]} skipped"
if [ ${#FAILED[@]} -gt 0 ]; then
    echo "  ${#FAILED[@]} failed:"
    for f in "${FAILED[@]}"; do
        echo "    - $f"
    done
    echo ""
    echo "Review failures above, then commit and push."
    exit 1
else
    echo "  0 failed"
    echo ""
    echo "All notebooks converted. Ready to commit and push."
fi
