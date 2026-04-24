---
name: avalonia-pro-max/preview-server
description: Use when the user wants to see and choose between visual design alternatives for an Avalonia app before implementation — generates 3 design variants as real .axaml files, renders each to PNGs at multiple viewport sizes (compact/wide × light/dark) using Avalonia.Headless, and serves an HTML comparison gallery via a local web server. The user reviews in their browser and tells the agent which variant to build.
---

# Preview Server — Visual Variant Picker for Avalonia

## What this does

Lets the agent show the user 2–3 design alternatives **as actual rendered Avalonia screens** (not HTML mockups), in a browser-based side-by-side comparison gallery. The user picks one and the agent then builds the chosen design out into the real app.

Why "real Avalonia" matters: HTML mockups misrepresent how Avalonia's Skia renderer, FluentTheme, ControlThemes, acrylic, shadows and font rendering actually look. A user who approves an HTML mockup is often disappointed by the real app. Rendering the actual XAML guarantees fidelity.

## When to use

### Must use
- User says: "show me some options", "what would this look like", "give me a few designs", "preview", "mockup"
- Building a new screen/window where there are valid stylistic alternatives
- Choosing between theme libraries (Fluent vs Suki vs Semi vs Material)
- Big visual refactor before committing to one direction

### Skip
- User has already specified an exact design
- Tiny tweaks to existing UI (just edit it)
- Pure backend / non-visual changes

## High-level flow

```
1. Agent reads requirements        (uses brainstorming skill if unclear)
2. Agent generates 3 variant       .axaml files in .preview/variants/{1,2,3}/
3. Agent runs render script         renders each variant via Avalonia.Headless
                                    → .preview/output/{variant}/{viewport}-{theme}.png
                                    (e.g. 1/wide-light.png, 1/wide-dark.png,
                                          1/compact-light.png, 1/compact-dark.png)
4. Agent runs serve script          starts python http.server, builds index.html
                                    gallery, prints URL: http://localhost:PORT
5. User reviews in browser, replies "I like variant 2"
6. Agent stops the server, copies   .preview/variants/2/* into the real project
   the chosen variant into the
   actual app
```

The user never has to install anything beyond what's already needed for Avalonia development plus Python (already required by `ui-ux-pro-max`).

## Prerequisites

- .NET 8 / 9 SDK (Avalonia 12 target)
- Python 3.8+ (for the gallery server)
- A scratch project at `.preview/AvaloniaPreviewHost/` — the agent creates this on first use

The scratch project is a bare Avalonia console app referencing:
- `Avalonia` 12.x
- `Avalonia.Themes.Fluent`
- `Avalonia.Headless`
- `Avalonia.Skia` (transitively required by Headless for image output)

Optional packages added per variant if it uses them: `FluentAvalonia`, `SukiUI`, `Semi.Avalonia`, `Material.Avalonia`, `Lucide.Avalonia`, `Material.Icons.Avalonia`, `Svg.Skia`.

## Variant generation rules

Generate exactly **3 variants** that are **meaningfully different**, not three shades of the same idea. Use this matrix:

| Slot | Variant identity | Typical theme combo |
|---|---|---|
| **A — Conservative** | Safe, professional, native-feeling. Lowest risk pick. | `FluentTheme` + `FluentAvalonia` |
| **B — Modern Flat** | Opinionated, low-chrome, accent-driven. "Linear/Vercel" energy. | `SukiUI` or `Semi.Avalonia` + custom tokens |
| **C — Distinctive** | A bigger swing — bold accent, heavier type, denser layout, or a Material-spec take. | `Material.Avalonia` **or** `Semi.Avalonia` + bold accent **or** `SukiUI` dark with neon accent |

If the user has already constrained the choice ("we're using Material"), generate 3 variants **within** that theme that differ in palette, density, or layout instead.

Each variant must include:
- The same target screen/window (so comparison is apples-to-apples)
- A `Resources.axaml` with the variant's tokens
- A `Styles.axaml` with shared component styles
- The screen `.axaml` (e.g. `MainWindow.axaml` or `DashboardView.axaml`)
- A short `README.md` explaining the design intent in 3–5 bullets

Reference the `design-system`, `themes`, and `components` sub-skills for the actual XAML content.

## Workflow for the agent

### Step 1 — Confirm scope

Before generating variants, confirm with the user:

- Which screen(s) do you want previewed? (single window / specific page / whole shell)
- Target window size? (default: 1280×800)
- Any hard constraints? (must be dark, must be Fluent, etc.)
- Mobile/tablet preview needed? (default: no — just desktop compact 800×600 + wide 1280×800)

Skip if the user has already given enough detail.

### Step 2 — Scaffold the preview host (once per project)

```bash
python3 skills/avalonia/avalonia-pro-max/preview-server/scripts/scaffold_host.py
```

Creates `.preview/AvaloniaPreviewHost/` if missing. Idempotent.

### Step 3 — Write the 3 variants

Author the XAML files under `.preview/variants/{1,2,3}/`. The structure for each:

```
.preview/variants/1/
├── README.md              # 3-5 bullet design intent
├── Resources.axaml        # tokens (theme dictionaries)
├── Styles.axaml           # component styles
├── PreviewScene.axaml     # the screen to render
└── packages.txt           # optional: extra NuGet refs needed (one per line)
```

The render script will inject `Resources.axaml` + `Styles.axaml` into the host App and load `PreviewScene.axaml` as the window content.

### Step 4 — Render to PNG

```bash
python3 skills/avalonia/avalonia-pro-max/preview-server/scripts/render_variants.py
```

What it does:
1. For each `variants/{N}/`:
   - Reads `packages.txt` and adds any new NuGet refs to the host project
   - Copies the variant's `.axaml` files into `.preview/AvaloniaPreviewHost/Variant/`
   - Runs `dotnet run --project .preview/AvaloniaPreviewHost -- --variant N --viewport wide --theme light --out .preview/output/1/wide-light.png`
   - Repeats for: `wide-dark`, `compact-light`, `compact-dark`
2. Outputs total render time + path to gallery script

Default viewports:
- `wide`: 1280 × 800
- `compact`: 800 × 600

Mobile viewports if `--mobile` flag passed:
- `phone`: 390 × 844 (iPhone 14)
- `tablet`: 1024 × 1366 (iPad Pro)

### Step 5 — Serve the gallery

```bash
python3 skills/avalonia/avalonia-pro-max/preview-server/scripts/serve_gallery.py
```

What it does:
1. Generates `.preview/output/index.html` from the gallery template — side-by-side cards per variant, with theme toggle (light/dark) and viewport toggle (wide/compact).
2. Starts `python -m http.server` on a free port (default 8765, falls back if taken).
3. Prints:
   ```
   Preview gallery serving at:  http://localhost:8765
   Press Ctrl+C to stop.
   ```
4. Optionally opens the URL via `xdg-open` / `open` / `start` if `--open` flag passed.

The agent leaves the server running and tells the user:

> I've put 3 design options on http://localhost:8765 — have a look and tell me which one to build (or describe what you'd change about one of them).

### Step 6 — Apply the chosen variant

Once the user picks (e.g. "go with variant 2, but with a green accent instead of blue"):

1. Stop the preview server (`Ctrl+C` or kill the process the agent spawned).
2. Copy `.preview/variants/2/Resources.axaml`, `Styles.axaml`, and any necessary `.axaml` into the real project's `Resources/` and `Views/` folders.
3. Apply any tweaks the user asked for (accent swap, etc.).
4. Wire up via `App.axaml` (`StyleInclude` + `ResourceInclude`) — see `design-system`.
5. Optionally clean up `.preview/` or leave for next iteration.

### Step 7 — Iterate (optional)

If the user says "I like variant 2 but make it tighter", generate 3 new variants based on variant 2 and re-run from Step 4. Keep iterations cheap — the host project is already scaffolded.

## File layout summary

```
<project root>/
├── .preview/                                 # gitignored
│   ├── AvaloniaPreviewHost/                  # scratch .NET project (scaffolded once)
│   │   ├── AvaloniaPreviewHost.csproj
│   │   ├── Program.cs                        # CLI: --variant N --viewport X --theme T --out P
│   │   ├── App.axaml
│   │   └── Variant/                          # populated per render run
│   │       ├── Resources.axaml
│   │       ├── Styles.axaml
│   │       └── PreviewScene.axaml
│   ├── variants/
│   │   ├── 1/{Resources,Styles,PreviewScene}.axaml + README.md
│   │   ├── 2/...
│   │   └── 3/...
│   └── output/
│       ├── index.html                        # gallery
│       ├── 1/wide-light.png, wide-dark.png, compact-light.png, compact-dark.png
│       ├── 2/...
│       └── 3/...
└── .gitignore                                # ensure .preview/ is excluded
```

## Add to .gitignore

The agent should ensure `.gitignore` contains:
```
.preview/
```

## Limits and honest caveats

- **Custom title bars / acrylic / native chrome** render but won't show OS-specific behavior (window shadows, traffic lights). The screen content is accurate; the chrome may differ slightly per platform.
- **Animation can't be screenshotted.** Document motion intent in the variant `README.md` instead. For motion previews, escalate to the `Avalonia WASM live preview` approach (not in this sub-skill — see "Future work" below).
- **Fonts must be embedded** (`avares://`). System-installed-only fonts may render with fallback under headless Skia.
- **First render is slow** (~10–30s — restoring NuGet + JIT). Subsequent renders are ~1–3s per PNG.
- **Headless rendering uses software Skia** by default. Pixel output matches a real Avalonia window 99%+ for static UI; tiny anti-aliasing differences exist but are not user-visible at gallery scale.
- **`ExperimentalAcrylicBorder` works under headless** but the blur source is a flat color (no real desktop background to sample), so the effect is approximate.

## Future work (not in this sub-skill)

- **Live WASM preview** — compile each variant to `wasm` via `dotnet publish` and serve interactively. Higher fidelity (motion, hover, click) but +30–60s per variant build and requires `dotnet workload install wasm-tools`.
- **Diff overlay** — render two variants and produce a pixel diff highlighting changes.
- **Auto-screenshot on file change** — watch `variants/` and re-render on save for fast iteration.

## Common mistakes

- **Generating three near-identical variants.** Defeats the purpose. Use the A/B/C identity matrix above.
- **Different content per variant.** The variants must show the *same* screen so the user is judging style, not content.
- **Forgetting `packages.txt`.** If variant uses `SukiUI`, the host won't compile without the reference.
- **Not gitignoring `.preview/`.** Pollutes the repo with binary screenshots.
- **Telling the user "click the button to pick"** when the gallery is purely visual. The user replies in chat — re-read this skill: selection is chat-based, not click-based.
- **Leaving the server running after selection.** Stop it before continuing implementation.
- **Rendering at only one viewport/theme.** Always render all four (wide/compact × light/dark) by default — that's the point of the comparison.
