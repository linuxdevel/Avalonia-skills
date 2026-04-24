```
    _            _             _        ____  _    _ _ _
   / \__   ____ _| | ___  _ __ (_) __ _ / ___|| | _(_) | |___
  / _ \ \ / / _` | |/ _ \| '_ \| |/ _` |\___ \| |/ / | | / __|
 / ___ \ V / (_| | | (_) | | | | | (_| | ___) |   <| | | \__ \
/_/   \_\_/ \__,_|_|\___/|_| |_|_|\__,_||____/|_|\_\_|_|_|___/
```
> AI agent skills for building Avalonia cross-platform .NET apps

---

A collection of dense reference skills that help AI coding agents (OpenCode, Claude Code, and others) write correct, idiomatic [Avalonia UI](https://avaloniaui.net/) code. Covers Avalonia 12 — the full framework from XAML to deployment.

Each skill is a focused reference document: real code patterns, key APIs, and the common mistakes that trip up even experienced developers. A master router skill automatically routes AI to the right subskill for any task.

## Install

```sh
curl -LsSf https://raw.githubusercontent.com/linuxdevel/Avalonia-skills/main/install.sh | bash
```

The installer:
- Downloads skills to `~/.local/share/avalonia-skills/`
- Creates symlinks in all detected agent directories (`~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/`)
- Is idempotent — safe to re-run to update

### Custom target directory

Pass `--target` with a **real** directory you want the skills symlinked into (e.g. an agent skills dir the installer doesn't auto-detect):

```sh
curl -LsSf https://raw.githubusercontent.com/linuxdevel/Avalonia-skills/main/install.sh | bash -s -- --target ~/my-agent/skills
```

> The installer refuses obvious placeholder paths like `/path/to/skills`.

## Skills

| Skill | Description |
|---|---|
| `avalonia` | Master router — identifies task and loads the correct subskill |
| `avalonia-xaml` | XAML markup, .axaml files, namespaces, code-behind, markup extensions |
| `avalonia-layout` | Panels (Grid, StackPanel, DockPanel, Canvas, WrapPanel), alignment, margins |
| `avalonia-styling` | Styles, ControlThemes, style selectors, pseudoclasses, theme variants |
| `avalonia-data-binding` | Compiled bindings, converters, MultiBinding, validation, collection views |
| `avalonia-data-templates` | DataTemplate, ItemTemplate, template selection, TreeDataTemplate |
| `avalonia-mvvm` | MVVM pattern, CommunityToolkit.Mvvm, ReactiveUI, ViewLocator, navigation |
| `avalonia-controls` | Router to control sub-skills |
| `avalonia-controls/input` | Button, TextBox, ComboBox, Slider, CheckBox, DatePicker, etc. |
| `avalonia-controls/data-display` | TextBlock, ListBox, DataGrid, TreeView, Carousel |
| `avalonia-controls/layout` | Border, ScrollViewer, SplitView, Expander, Viewbox |
| `avalonia-controls/navigation` | TabControl, Menu, ContextMenu, TrayIcon |
| `avalonia-controls/media` | Image, PathIcon, MediaPlayer, WebView |
| `avalonia-custom-controls` | UserControl, TemplatedControl, StyledProperty, custom drawing |
| `avalonia-graphics-animation` | Brushes, transforms, keyframe animations, transitions |
| `avalonia-input-interaction` | Pointer, keyboard, gestures, drag-and-drop, focus |
| `avalonia-property-system` | StyledProperty, DirectProperty, AttachedProperty, value priority |
| `avalonia-events` | Routed events, bubbling, tunneling, OnApplyTemplate |
| `avalonia-services` | Clipboard, file dialogs, notifications, StorageProvider |
| `avalonia-app-development` | App structure, lifetimes, resource dictionaries, assets |
| `avalonia-testing` | Headless UI tests, ViewModel unit tests, Avalonia.Headless |
| `avalonia-deployment` | Windows, macOS, Linux, WASM, Android, iOS packaging |
| `avalonia-wpf-migration` | WPF → Avalonia mapping, API differences, migration patterns |
| `avalonia-pro-max` | Router for visual design / UI polish — beautiful Avalonia UIs |
| `avalonia-pro-max/design-system` | Semantic tokens, palettes, typography, spacing, theme variants |
| `avalonia-pro-max/themes` | FluentAvalonia, SukiUI, Semi, Material, ShadUI, Ursa selection matrix |
| `avalonia-pro-max/components` | Production XAML recipes: buttons, cards, nav, dialogs, forms |
| `avalonia-pro-max/motion` | Transitions, animations, easings, reduced-motion |
| `avalonia-pro-max/accessibility` | AutomationProperties, contrast, keyboard nav, screen readers |
| `avalonia-pro-max/layout-patterns` | Responsive, breakpoints, sidebar/nav, dashboards |
| `avalonia-pro-max/icons-imagery` | Icon libraries, SVG, brand assets, image optimization |
| `avalonia-pro-max/review-checklist` | Pre-merge / pre-release UI audit checklist |
| `avalonia-pro-max/preview-server` | Generate 3 design variants, render each via Avalonia.Headless, serve an HTML gallery for the user to pick |

## How it works

When you start working on an Avalonia project, the AI agent loads the `avalonia` master skill. The master skill identifies what you're doing and routes to the appropriate subskill for accurate, dense reference.

Examples:
- Writing data bindings → loads `avalonia-data-binding`
- Styling a control → loads `avalonia-styling`
- Migrating from WPF → loads `avalonia-wpf-migration`
- Adding a Button or DataGrid → loads `avalonia-controls/input` or `avalonia-controls/data-display`

## Requirements

- `git` or `curl` (for the installer)
- A compatible AI agent: [OpenCode](https://opencode.ai), Claude Code, or any agent that supports the skills directory convention

## License

MIT
