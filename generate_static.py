#!/usr/bin/env python3
"""Generate static JS assets for the Klotho Jupyter Book site.

Copies shared JS libraries and generates klotho_boot.js from the
installed klotho package.  Called by rebuild_tutorials.sh.
"""
import base64
import json
import shutil
from pathlib import Path

STATIC_DIR = Path(__file__).parent / "static"

def main():
    from klotho.utils.playback.supersonic.cdn import (
        SUPERSONIC_CDN,
        SUPERSONIC_CORE_CDN,
        SUPERSONIC_SYNTHDEFS_CDN,
        SUPERSONIC_SAMPLES_CDN,
        SCHEDULER_JS_PATH,
        DRAW_JS_PATH,
    )
    import klotho
    pkg_root = Path(klotho.__path__[0])
    ss_dir = pkg_root / "utils" / "playback" / "supersonic"
    BRIDGE_JS_PATH = pkg_root / "utils" / "playback" / "_animation_bridge.js"
    SCHED_SCORE_PATH = ss_dir / "scheduler_score.js"
    SYNTHDEFS_DIR = ss_dir / "assets" / "synthdefs"

    STATIC_DIR.mkdir(exist_ok=True)

    shutil.copy2(SCHEDULER_JS_PATH, STATIC_DIR / "scheduler.js")
    shutil.copy2(DRAW_JS_PATH, STATIC_DIR / "draw.js")
    shutil.copy2(BRIDGE_JS_PATH, STATIC_DIR / "animation_bridge.js")
    shutil.copy2(SCHED_SCORE_PATH, STATIC_DIR / "scheduler_score.js")
    print(f"  Copied scheduler.js, draw.js, animation_bridge.js, scheduler_score.js")

    needed = {
        'kl_tri', 'kl_kicktone', 'kl_sine', 'kl_saw', 'kl_sqr', 'kl_noisebpf',
        '__busRouter', '__busRouterMonitor', '__chainLimiter', '__klEnvCtrl',
    }
    assets = {}
    if SYNTHDEFS_DIR.exists():
        for p in SYNTHDEFS_DIR.glob("*.scsyndef"):
            assets[p.stem] = base64.b64encode(p.read_bytes()).decode("ascii")
    if "default" not in assets and "kl_tri" in assets:
        assets["default"] = assets["kl_tri"]
    filtered = {k: v for k, v in assets.items() if k in needed or k == "default"}
    synthdef_json = json.dumps(filtered)

    config_json = json.dumps({
        "baseURL": f"{SUPERSONIC_CDN}/dist/",
        "coreBaseURL": SUPERSONIC_CORE_CDN,
        "synthdefBaseURL": SUPERSONIC_SYNTHDEFS_CDN,
        "sampleBaseURL": SUPERSONIC_SAMPLES_CDN,
    })

    boot_js = f"""\
(function() {{
  if (globalThis.__klothoSonic) return;

  var config = {config_json};
  var synthdefAssets = {synthdef_json};

  globalThis.__klothoSonic = {{ instance: null, promise: null, loadedDefs: new Set() }};
  globalThis.__klothoSonic.promise = (async function() {{
    try {{
      var mod = await import("{SUPERSONIC_CDN}");
      globalThis.SuperSonic = mod.SuperSonic;
      var sonic = new mod.SuperSonic(config);
      await sonic.init();
      globalThis.__klothoSonic.instance = sonic;

      var loaded = globalThis.__klothoSonic.loadedDefs;
      for (var name in synthdefAssets) {{
        if (!synthdefAssets.hasOwnProperty(name)) continue;
        if (loaded.has(name)) continue;
        var b64 = synthdefAssets[name];
        var bytes = Uint8Array.from(atob(b64), function(c) {{ return c.charCodeAt(0); }});
        try {{ await sonic.loadSynthDef(bytes); loaded.add(name); }} catch(e) {{}}
      }}
      return sonic;
    }} catch(e) {{
      console.warn("[Klotho] SuperSonic site boot failed:", e);
      globalThis.__klothoSonic.promise = null;
      return null;
    }}
  }})();

  if (!globalThis.__ensureSuperSonic) {{
    globalThis.__ensureSuperSonic = function() {{
      var state = globalThis.__klothoSonic;
      if (!state) {{
        state = {{ instance: null, promise: null, loadedDefs: new Set() }};
        globalThis.__klothoSonic = state;
      }}
      if (state.instance) return Promise.resolve(state.instance);
      if (state.promise) return state.promise;
      return Promise.resolve(null);
    }};
  }}
}})();
"""
    (STATIC_DIR / "klotho_boot.js").write_text(boot_js)
    print(f"  Generated klotho_boot.js ({len(boot_js):,} bytes)")

if __name__ == "__main__":
    main()
