#!/usr/bin/env python3
"""
render_variants.py

Renders each variant under .preview/variants/{1,2,3,...}/ to PNG screenshots
across the chosen viewports and themes, using the AvaloniaPreviewHost project.

For each variant, this script:
  1. Reads variants/<N>/packages.txt (one NuGet ref per line, e.g. "SukiUI:6.0.0")
  2. dotnet adds any missing packages to the host
  3. Copies the variant's Resources.axaml, Styles.axaml, PreviewScene.axaml
     into AvaloniaPreviewHost/Variant/
  4. Runs the host CLI for each (viewport, theme) combination
  5. Writes PNGs to .preview/output/<N>/<viewport>-<theme>.png

Usage:
    python3 render_variants.py [--root .] [--variants 1,2,3] [--mobile] [--viewports wide,compact]
                               [--themes light,dark]
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_VIEWPORTS = ["wide", "compact"]
MOBILE_VIEWPORTS  = ["phone", "tablet"]
DEFAULT_THEMES    = ["light", "dark"]
REQUIRED_FILES    = ["Resources.axaml", "Styles.axaml", "PreviewScene.axaml"]


def main() -> int:
    p = argparse.ArgumentParser(description="Render Avalonia variants to PNG.")
    p.add_argument("--root", default=".")
    p.add_argument("--variants", default="", help="Comma-separated variant ids (default: all)")
    p.add_argument("--viewports", default=",".join(DEFAULT_VIEWPORTS))
    p.add_argument("--themes", default=",".join(DEFAULT_THEMES))
    p.add_argument("--mobile", action="store_true", help="Add phone+tablet viewports")
    p.add_argument("--no-restore", action="store_true",
                   help="Skip dotnet restore (use if already restored this session)")
    args = p.parse_args()

    root = Path(args.root).resolve()
    host = root / ".preview" / "AvaloniaPreviewHost"
    variants_dir = root / ".preview" / "variants"
    out_dir = root / ".preview" / "output"

    if not host.exists():
        print(f"ERROR: Host not scaffolded. Run scaffold_host.py first.", file=sys.stderr)
        return 1
    if not variants_dir.exists() or not any(variants_dir.iterdir()):
        print(f"ERROR: No variants found under {variants_dir}.", file=sys.stderr)
        return 1

    variant_ids = _resolve_variants(variants_dir, args.variants)
    viewports = [v.strip() for v in args.viewports.split(",") if v.strip()]
    if args.mobile:
        viewports.extend(v for v in MOBILE_VIEWPORTS if v not in viewports)
    themes = [t.strip() for t in args.themes.split(",") if t.strip()]

    print(f"Rendering variants: {', '.join(variant_ids)}")
    print(f"  viewports: {', '.join(viewports)}")
    print(f"  themes:    {', '.join(themes)}")
    print()

    overall_start = time.time()

    # One restore if any packages.txt exists with content
    if not args.no_restore:
        _ensure_packages(host, variants_dir, variant_ids)
        print("Running dotnet restore...")
        rc = subprocess.run(["dotnet", "restore", str(host)], cwd=root).returncode
        if rc != 0:
            print("ERROR: dotnet restore failed.", file=sys.stderr)
            return rc

    for vid in variant_ids:
        v_src = variants_dir / vid
        if not _validate_variant(v_src):
            print(f"  ✗ variant {vid} skipped (missing required files)")
            continue

        # Copy variant files into host
        host_variant = host / "Variant"
        for fname in REQUIRED_FILES:
            shutil.copy2(v_src / fname, host_variant / fname)

        v_out = out_dir / vid
        v_out.mkdir(parents=True, exist_ok=True)

        print(f"Variant {vid}:")
        for viewport in viewports:
            for theme in themes:
                png = v_out / f"{viewport}-{theme}.png"
                t0 = time.time()
                cmd = [
                    "dotnet", "run", "--project", str(host),
                    "--no-restore",
                    "--",
                    "--variant", vid,
                    "--viewport", viewport,
                    "--theme", theme,
                    "--out", str(png),
                ]
                rc = subprocess.run(cmd, cwd=root).returncode
                dt = time.time() - t0
                if rc != 0:
                    print(f"  ✗ {viewport}-{theme} (failed in {dt:.1f}s)")
                else:
                    print(f"  ✓ {viewport}-{theme} ({dt:.1f}s) → {png.relative_to(root)}")

    total = time.time() - overall_start
    print()
    print(f"Done in {total:.1f}s. Now run:")
    print(f"  python3 {Path(__file__).parent / 'serve_gallery.py'}")
    return 0


def _resolve_variants(variants_dir: Path, csv: str) -> list[str]:
    if csv:
        return [v.strip() for v in csv.split(",") if v.strip()]
    return sorted(
        d.name for d in variants_dir.iterdir()
        if d.is_dir() and (d / "PreviewScene.axaml").exists()
    )


def _validate_variant(v_src: Path) -> bool:
    return all((v_src / f).exists() for f in REQUIRED_FILES)


def _ensure_packages(host: Path, variants_dir: Path, variant_ids: list[str]) -> None:
    """Read packages.txt from each variant and `dotnet add` any new ones."""
    csproj = host / "AvaloniaPreviewHost.csproj"
    existing = csproj.read_text()
    seen: set[str] = set()
    for vid in variant_ids:
        pkg_file = variants_dir / vid / "packages.txt"
        if not pkg_file.exists():
            continue
        for raw in pkg_file.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            # Accept "Name" or "Name:Version"
            name, _, version = line.partition(":")
            name, version = name.strip(), version.strip()
            key = name.lower()
            if key in seen or f'Include="{name}"' in existing:
                continue
            seen.add(key)
            cmd = ["dotnet", "add", str(csproj), "package", name]
            if version:
                cmd += ["--version", version]
            print(f"  + adding NuGet ref: {name}{(' ' + version) if version else ''}")
            subprocess.run(cmd, check=False)


if __name__ == "__main__":
    sys.exit(main())
