#!/usr/bin/env python3
"""
serve_gallery.py

Generates .preview/output/index.html (a side-by-side comparison gallery for
the rendered variant PNGs) and serves the .preview/output/ directory over HTTP.

Usage:
    python3 serve_gallery.py [--root .] [--port 8765] [--open]
"""
from __future__ import annotations

import argparse
import http.server
import json
import socket
import socketserver
import sys
import threading
import webbrowser
from functools import partial
from pathlib import Path

DEFAULT_PORT = 8765


def main() -> int:
    p = argparse.ArgumentParser(description="Build and serve the variant comparison gallery.")
    p.add_argument("--root", default=".")
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument("--open", action="store_true", help="Open browser automatically")
    args = p.parse_args()

    root = Path(args.root).resolve()
    out_dir = root / ".preview" / "output"
    if not out_dir.exists():
        print(f"ERROR: No output dir at {out_dir}. Run render_variants.py first.", file=sys.stderr)
        return 1

    catalog = _scan_catalog(out_dir)
    if not catalog["variants"]:
        print("ERROR: No PNGs found under .preview/output/. Run render_variants.py first.",
              file=sys.stderr)
        return 1

    index_html = _render_index(catalog)
    (out_dir / "index.html").write_text(index_html)
    print(f"Wrote {out_dir / 'index.html'}")
    print(f"  variants:  {', '.join(catalog['variants'])}")
    print(f"  viewports: {', '.join(catalog['viewports'])}")
    print(f"  themes:    {', '.join(catalog['themes'])}")
    print()

    port = _find_free_port(args.port)
    handler = partial(_QuietHandler, directory=str(out_dir))
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"Preview gallery serving at:  {url}")
        print("Press Ctrl+C to stop.")
        if args.open:
            threading.Timer(0.5, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
    return 0


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002
        pass  # suppress per-request logs


def _scan_catalog(out_dir: Path) -> dict:
    variants: list[str] = []
    viewports: set[str] = set()
    themes: set[str] = set()
    images: dict[str, dict[str, dict[str, str]]] = {}  # variant -> viewport -> theme -> filename

    for v_dir in sorted(out_dir.iterdir()):
        if not v_dir.is_dir():
            continue
        vid = v_dir.name
        readme = v_dir.parent.parent / "variants" / vid / "README.md"
        intent = readme.read_text() if readme.exists() else ""

        v_images: dict[str, dict[str, str]] = {}
        for png in sorted(v_dir.glob("*.png")):
            stem = png.stem  # e.g. "wide-light"
            if "-" not in stem:
                continue
            viewport, theme = stem.rsplit("-", 1)
            viewports.add(viewport)
            themes.add(theme)
            v_images.setdefault(viewport, {})[theme] = f"{vid}/{png.name}"
        if v_images:
            variants.append(vid)
            images[vid] = v_images
            (out_dir / vid / "_intent.txt").write_text(intent)
    return {
        "variants":  variants,
        "viewports": sorted(viewports, key=_viewport_sort_key),
        "themes":    sorted(themes, key=lambda t: 0 if t == "light" else 1),
        "images":    images,
    }


def _viewport_sort_key(v: str) -> int:
    order = {"wide": 0, "compact": 1, "tablet": 2, "phone": 3}
    return order.get(v, 99)


def _find_free_port(preferred: int) -> int:
    for candidate in [preferred] + list(range(preferred + 1, preferred + 50)):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", candidate))
                return candidate
            except OSError:
                continue
    raise SystemExit(f"No free port near {preferred}")


def _render_index(catalog: dict) -> str:
    data_json = json.dumps(catalog, indent=2)
    return _TEMPLATE.replace("/*__DATA__*/", data_json)


_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Avalonia Design Variants</title>
<style>
  :root {
    --bg: #0b1020;
    --surface: #131a31;
    --surface-2: #1a2240;
    --border: #232c4d;
    --text: #e6e8f2;
    --muted: #8b93b3;
    --accent: #6aa3ff;
  }
  @media (prefers-color-scheme: light) {
    :root {
      --bg: #f6f7fb; --surface: #ffffff; --surface-2: #f1f3f9;
      --border: #e3e6ef; --text: #0f1330; --muted: #5b6280; --accent: #2563eb;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, system-ui, sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.5;
  }
  header {
    padding: 24px 32px; border-bottom: 1px solid var(--border);
    display: flex; flex-wrap: wrap; gap: 16px; align-items: center; justify-content: space-between;
    position: sticky; top: 0; background: var(--bg); z-index: 10;
  }
  header h1 { margin: 0; font-size: 18px; font-weight: 600; }
  header .meta { color: var(--muted); font-size: 13px; }
  .controls { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
  .group { display: flex; gap: 4px; background: var(--surface-2); border-radius: 8px; padding: 4px; }
  .group button {
    background: transparent; border: 0; color: var(--muted); padding: 6px 12px;
    border-radius: 6px; font-size: 13px; cursor: pointer; font-weight: 500;
  }
  .group button.active { background: var(--surface); color: var(--text); box-shadow: 0 1px 2px #00000019; }
  .group button:hover:not(.active) { color: var(--text); }
  main { padding: 24px 32px; }
  .grid {
    display: grid; gap: 24px;
    grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
  }
  .card {
    background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
    overflow: hidden; display: flex; flex-direction: column;
  }
  .card-header { padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; align-items: baseline; gap: 12px; }
  .card-header h2 { margin: 0; font-size: 15px; font-weight: 600; }
  .card-header .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; }
  .img-wrap {
    background: repeating-conic-gradient(#0000000a 0% 25%, transparent 0% 50%) 50% / 16px 16px,
                var(--surface-2);
    display: flex; align-items: center; justify-content: center; min-height: 280px;
  }
  .img-wrap img { display: block; max-width: 100%; height: auto; }
  .intent { padding: 14px 20px; color: var(--muted); font-size: 13px; white-space: pre-wrap; border-top: 1px solid var(--border); }
  footer { padding: 24px 32px; color: var(--muted); font-size: 12px; text-align: center; }
  .empty { padding: 40px; text-align: center; color: var(--muted); }
  kbd {
    background: var(--surface-2); border: 1px solid var(--border); border-radius: 4px;
    padding: 2px 6px; font-size: 11px; font-family: ui-monospace, SFMono-Regular, monospace;
  }
</style>
</head>
<body>
<header>
  <div>
    <h1>Avalonia Design Variants</h1>
    <div class="meta" id="meta"></div>
  </div>
  <div class="controls">
    <div class="group" id="theme-group" role="tablist" aria-label="Theme"></div>
    <div class="group" id="viewport-group" role="tablist" aria-label="Viewport"></div>
  </div>
</header>
<main>
  <div class="grid" id="grid"></div>
</main>
<footer>
  Tell the agent which variant you'd like — e.g. <em>"go with variant 2, but use a green accent"</em>.
  Stop the server with <kbd>Ctrl</kbd>+<kbd>C</kbd> in the terminal when done.
</footer>

<script>
  const data = /*__DATA__*/;
  const state = {
    theme:    data.themes.includes("dark") ? "dark" : data.themes[0],
    viewport: data.viewports.includes("wide") ? "wide" : data.viewports[0],
  };

  function buildGroup(id, items, key) {
    const el = document.getElementById(id);
    el.innerHTML = "";
    items.forEach(item => {
      const btn = document.createElement("button");
      btn.textContent = item;
      btn.dataset.value = item;
      btn.addEventListener("click", () => { state[key] = item; render(); });
      el.appendChild(btn);
    });
  }

  function render() {
    document.getElementById("meta").textContent =
      `${data.variants.length} variants · ${state.viewport} · ${state.theme}`;

    document.querySelectorAll("#theme-group button").forEach(b =>
      b.classList.toggle("active", b.dataset.value === state.theme));
    document.querySelectorAll("#viewport-group button").forEach(b =>
      b.classList.toggle("active", b.dataset.value === state.viewport));

    const grid = document.getElementById("grid");
    grid.innerHTML = "";

    if (!data.variants.length) {
      grid.innerHTML = '<div class="empty">No variants rendered yet.</div>';
      return;
    }

    data.variants.forEach(vid => {
      const card = document.createElement("article");
      card.className = "card";

      const header = document.createElement("div");
      header.className = "card-header";
      header.innerHTML = `
        <span class="label">Variant ${vid}</span>
        <h2 id="title-${vid}">Loading…</h2>
      `;
      card.appendChild(header);

      const img = data.images[vid]?.[state.viewport]?.[state.theme];
      const wrap = document.createElement("div");
      wrap.className = "img-wrap";
      if (img) {
        const i = document.createElement("img");
        i.src = img + "?t=" + Date.now();
        i.alt = `Variant ${vid} — ${state.viewport} ${state.theme}`;
        i.loading = "lazy";
        wrap.appendChild(i);
      } else {
        wrap.innerHTML = '<div class="empty">No render for this combo.</div>';
      }
      card.appendChild(wrap);

      // Intent (README first line as title, rest as body)
      fetch(`${vid}/_intent.txt?t=${Date.now()}`).then(r => r.text()).then(txt => {
        const lines = txt.trim().split(/\r?\n/);
        const titleLine = (lines.find(l => l.startsWith("# ")) || `# Variant ${vid}`).replace(/^#\s*/, "");
        document.getElementById(`title-${vid}`).textContent = titleLine;
        const body = lines.filter(l => !l.startsWith("# ")).join("\n").trim();
        if (body) {
          const intentEl = document.createElement("div");
          intentEl.className = "intent";
          intentEl.textContent = body;
          card.appendChild(intentEl);
        }
      }).catch(() => { document.getElementById(`title-${vid}`).textContent = `Variant ${vid}`; });

      grid.appendChild(card);
    });
  }

  buildGroup("theme-group", data.themes, "theme");
  buildGroup("viewport-group", data.viewports, "viewport");
  render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(main())
