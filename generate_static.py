#!/usr/bin/env python3
"""Generate static JS assets for the Klotho Jupyter Book site.

Copies shared JS libraries and generates klotho_boot.js from the
installed klotho package.  Called by rebuild_tutorials.sh.
"""
import shutil
from pathlib import Path

STATIC_DIR = Path(__file__).parent / "static"

def main():
    from klotho.utils.playback.supersonic.cdn import DRAW_JS_PATH
    from klotho.utils.playback.supersonic._js_fragments import (
        ss_init_js, draw_scheduler_js, scheduler_core_js, scheduler_score_js,
    )

    import klotho
    pkg_root = Path(klotho.__path__[0])
    ss_dir = pkg_root / "utils" / "playback" / "supersonic"
    BRIDGE_JS_PATH = pkg_root / "utils" / "playback" / "_animation_bridge.js"
    SCHED_CORE_PATH = ss_dir / "scheduler_core.js"
    SCHED_SCORE_PATH = ss_dir / "scheduler_score.js"

    STATIC_DIR.mkdir(exist_ok=True)

    shutil.copy2(SCHED_CORE_PATH, STATIC_DIR / "scheduler_core.js")
    shutil.copy2(SCHED_SCORE_PATH, STATIC_DIR / "scheduler_score.js")
    shutil.copy2(DRAW_JS_PATH, STATIC_DIR / "draw.js")
    shutil.copy2(BRIDGE_JS_PATH, STATIC_DIR / "animation_bridge.js")
    print(f"  Copied scheduler_core.js, scheduler_score.js, draw.js, animation_bridge.js")

    boot_js = f"""\
(function() {{
{ss_init_js()}
{draw_scheduler_js()}
{scheduler_core_js()}
}})();
"""
    (STATIC_DIR / "klotho_boot.js").write_text(boot_js)
    print(f"  Generated klotho_boot.js ({len(boot_js):,} bytes)")

if __name__ == "__main__":
    main()
