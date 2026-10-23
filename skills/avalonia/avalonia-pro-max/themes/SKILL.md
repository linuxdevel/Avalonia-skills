---
name: avalonia-pro-max/themes
description: Use when choosing or configuring a theme library for an Avalonia app (FluentTheme, FluentAvalonia, SukiUI, Semi.Avalonia, Material.Avalonia, ShadUI, Ursa.Avalonia, Citrus, Classic). Provides a recommendation matrix by product type, install snippets, and combination rules.
---

# Avalonia Theme Libraries

## TL;DR Defaults

| You want | Use |
|---|---|
| Modern Microsoft / Windows-native feel | `FluentTheme` + `FluentAvalonia` |
| Modern, opinionated flat (Linear-like) | `SukiUI` |
| Clean Chinese-design-system look | `Semi.Avalonia` |
| Material Design 3 | `Material.Avalonia` |
| shadcn/ui-inspired developer aesthetic | `ShadUI` |
| Rich enterprise control set | `Ursa.Avalonia` |
| Just a slight upgrade over built-ins | `Citrus.Avalonia` |
| Retro Windows 9x | `Classic.Avalonia` |
| Fallout Pip-Boy / themed novelty | `Pipboy.Avalonia` |
| Pure custom (no library) | `FluentTheme` only + your own ControlThemes |

---

## Avalonia Version Compatibility (verified on nuget.org, 2026-10-22)

Third-party themes version independently of Avalonia. Pick the package line that matches the project's Avalonia version (see `avalonia-versions`). "Min Avalonia" is the lowest Avalonia the package's nuspec declares (a NuGet minimum, not an exact pin). Do not mix a 11.x-line theme with a 12.x app or the reverse.

| Package (NuGet id) | Avalonia 11.3 | Avalonia 12.0 / 12.1 |
|---|---|---|
| `FluentAvaloniaUI` | 2.5.1 (min Avalonia 11.3.12) | 3.0.0 (min 12.0.0) · 3.1.0 (min 12.1.0) |
| `SukiUI` | 6.1.1 (min 11.3.14) | 7.0.1 (min 12.0.3). Stable 7.x on nuget is 7.0.1; later 7.0.2 builds are nightly only |
| `Semi.Avalonia` | 11.3.22 (min 11.3.22) | 12.0.0 / 12.0.1 / 12.0.3 / 12.1.0 / 12.1.0.1 (12.1.0.1: min 12.1.0) |
| `Irihi.Ursa` | 1.15.1 (min 11.3.7) | 2.0.0 to 2.2.0 published (2.2.0: min 12.0.2; earlier 2.x minimums not checked) |
| `Irihi.Ursa.Themes.Semi` (Ursa + Semi bridge) | not checked | 2.2.0 (needs Irihi.Ursa 2.2.0, Semi.Avalonia 12.0.1+, Avalonia 12.0.2+) |
| `Material.Avalonia` | up to 3.14.2 (min Avalonia 11.1.0) | 3.15.0 / 3.15.1 / 3.18.0 / 3.19.0 (min 12.0.0; intermediate versions not checked) · 3.20.0 / 3.21.0 (min 12.1.1) |
| `ShadUI` | none (0.x line starts at Avalonia 12) | 0.2.0 (min 12.0.2) · 0.2.4 (min 12.1.0, net10.0/net9.0 targets) |

Notes:
- Target frameworks seen in nuspecs: FluentAvaloniaUI 2.5.1/3.x `net10.0` only; SukiUI 6.1.1/7.0.1 and Material.Avalonia 3.20/3.21 `net8.0` only; Semi.Avalonia 12.1.0.1 and Irihi.Ursa 2.2.0 `net8.0` + `net10.0`. Check your app's TargetFramework against the package.
- ShadUI 0.2.4 lists `net10.0` and `net9.0` targets only; ShadUI 0.2.0 lists `net8.0`/`net9.0`/`net10.0`.
- Not verified: runtime behavior of each theme on Avalonia 12 (only package metadata was checked). Read the project's release notes for breaking visual/API changes between major versions (e.g. FluentAvaloniaUI 2.x to 3.x, SukiUI 6.x to 7.x, Ursa 1.x to 2.x).

---

## Recommendation Matrix by Product Type

| Product | Best fit | Why |
|---|---|---|
| Internal tools / admin / dashboards | FluentAvalonia + FluentTheme | NavigationView, InfoBar, TeachingTip ready; matches Windows desktop expectation |
| Cross-platform consumer app | SukiUI **or** Semi.Avalonia | Look identical on Win/macOS/Linux, modern flat |
| Mobile-first cross-platform | Semi.Avalonia + custom tokens | Lightweight, works well at small sizes |
| Developer tool (IDE, terminal, db client) | SukiUI **or** ShadUI | Dark-first, low-chrome, accent-driven |
| Material-spec product | Material.Avalonia | True MD3 compliance |
| Enterprise B2B with many forms / data | Ursa.Avalonia | Pre-built form, tag, badge, drawer, time picker, etc. |
| Game launcher / creative app | SukiUI + custom palette | High-contrast, flexible |
| Migration from WPF (minimum visual change) | FluentTheme only | Closest to legacy Windows look without Material weirdness |

---

## FluentTheme (built-in baseline)

Always start here unless you have a strong reason. Ships with Avalonia, no extra NuGet.

```xml
<Application.Styles>
  <FluentTheme/>
</Application.Styles>
```

Pair with `RequestedThemeVariant="Default"` to follow OS.

Customize the FluentTheme accent through its palettes (Avalonia 11.3 and 12.x):

```xml
<FluentTheme>
  <FluentTheme.Palettes>
    <ColorPaletteResources x:Key="Light" Accent="#2563EB"/>
    <ColorPaletteResources x:Key="Dark" Accent="#3B82F6"/>
  </FluentTheme.Palettes>
</FluentTheme>
```

`Accent` generates the related light/dark accent shades and can change at runtime. Other palette properties are read once at startup. The `SystemAccentColor*` resource keys hold `Color` values, not brushes. See [custom color palettes](https://docs.avaloniaui.net/docs/styling/themes#creating-custom-color-palettes).

---

## FluentAvalonia

WinUI3-style controls + accent system. Best companion to `FluentTheme`.

```sh
dotnet add package FluentAvaloniaUI   # 3.x for Avalonia 12, 2.5.x for Avalonia 11.3
```

```xml
<Application xmlns="https://github.com/avaloniaui"
             xmlns:ui="using:FluentAvalonia.UI.Controls"
             xmlns:fav="using:FluentAvalonia.Styling">
  <Application.Styles>
    <fav:FluentAvaloniaTheme PreferUserAccentColor="True"/>
  </Application.Styles>
</Application>
```

Key controls: `NavigationView`, `Frame`, `InfoBar`, `TeachingTip`, `CommandBar`, `Expander` (rich), `ContentDialog`, `FAComboBox`, `NumberBox`, `TabView`, `SettingsExpander`.

Use **instead of** `FluentTheme` (FluentAvaloniaTheme already includes Fluent base).

---

## SukiUI

Opinionated flat dark-friendly theme, modern look. Includes own controls and dialog system.

```sh
dotnet add package SukiUI   # 7.x for Avalonia 12, 6.x for Avalonia 11.3
```

```xml
<Application xmlns="https://github.com/avaloniaui"
             xmlns:suki="clr-namespace:SukiUI;assembly=SukiUI">
  <Application.Styles>
    <suki:SukiTheme ThemeColor="Blue"/>
  </Application.Styles>
</Application>
```

Wrap windows in `SukiWindow` for the chromeless title bar:

```xml
<suki:SukiWindow xmlns:suki="clr-namespace:SukiUI.Controls;assembly=SukiUI"
                 Title="My App">
  <!-- content -->
</suki:SukiWindow>
```

Dialogs: `ISukiDialogManager` injected into ViewModel.

---

## Semi.Avalonia

Port of Semi Design (ByteDance). Clean, dense, great for forms.

```sh
dotnet add package Semi.Avalonia   # version line follows Avalonia (11.3.x / 12.x)
```

```xml
<Application xmlns="https://github.com/avaloniaui"
             xmlns:semi="https://irihi.tech/semi">
  <Application.Styles>
    <semi:SemiTheme Locale="en-US"/>
  </Application.Styles>
</Application>
```

Often paired with **Ursa.Avalonia** (same author) for extra controls (TagInput, IconButton, Drawer, TimelineItem, Toast).

```sh
dotnet add package Irihi.Ursa
dotnet add package Irihi.Ursa.Themes.Semi
```

```xml
<Application.Styles>
  <semi:SemiTheme Locale="en-US"/>
  <semi:UrsaSemiTheme Locale="en-US"/>   <!-- Ursa bridge styles -->
</Application.Styles>
```

---

## Material.Avalonia

True Material Design 3.

```sh
dotnet add package Material.Avalonia   # 3.15+ needs Avalonia 12; 3.14.x for Avalonia 11
dotnet add package Material.Avalonia.DataGrid    <!-- optional -->
dotnet add package Material.Icons.Avalonia
```

```xml
<Application xmlns="https://github.com/avaloniaui"
             xmlns:material="clr-namespace:Material.Styles.Themes;assembly=Material.Avalonia">
  <Application.Styles>
    <material:MaterialTheme BaseTheme="Inherit" PrimaryColor="Blue" SecondaryColor="Pink"/>
  </Application.Styles>
</Application>
```

Use `Material.Icons.Avalonia` for the icon set:
```xml
<materialIcons:MaterialIcon Kind="Home"/>
```

---

## ShadUI

shadcn/ui-inspired styling for Avalonia. Currently community-driven; check repo for latest install. NuGet id `ShadUI`; every published version (0.2.x) targets Avalonia 12 (no Avalonia 11 line).

Aesthetic: minimal, neutral grays, single accent, subtle shadows, generous radius. Ideal for developer-facing tools.

---

## Ursa.Avalonia

Stand-alone full UI library (also bridges with Semi). Adds: `Form`, `Tag`, `IconButton`, `Drawer`, `Skeleton`, `Toast`, `Banner`, `Pagination`, `KeyGestures`, color picker, time picker, calendar, date picker, etc.

```sh
dotnet add package Irihi.Ursa
```

```xml
<Application.Styles>
  <FluentTheme/>           <!-- Ursa needs a base theme -->
  <ursa:UrsaTheme/>
</Application.Styles>
```

Use Ursa 2.x with Avalonia 12 and Ursa 1.x with Avalonia 11.3 (see compatibility table). The `ursa:UrsaTheme` snippet above is from earlier docs; confirm it against the project's README for the installed major version.

---

## Citrus.Avalonia

Light styling pack — keeps native controls but modernizes their visuals. Good for "tweak the defaults" projects.

```sh
dotnet add package Citrus.Avalonia
```

```xml
<Application.Styles>
  <StyleInclude Source="avares://Citrus.Avalonia/Citrus.xaml"/>
</Application.Styles>
```

---

## Classic.Avalonia / Pipboy.Avalonia / Neumorphism.Avalonia / WPFDarkTheme

Niche aesthetics — ship as primary theme only when the app's identity demands it. Don't combine with Fluent/Material.

---

## Combination Rules

**Allowed** (tested combinations):
- `FluentTheme` + `FluentAvalonia` → use FluentAvaloniaTheme (it includes Fluent base)
- `FluentTheme` + `Ursa.Avalonia`
- `Semi.Avalonia` + `Ursa.Avalonia` (+ Irihi.Ursa.Themes.Semi bridge)
- Any theme + `Citrus.Avalonia` for table/scroll polish
- Any theme + an icon library (`Lucide.Avalonia`, `Material.Icons.Avalonia`, `Projektanker.Icons.Avalonia`)

**Forbidden** (visual chaos):
- `Material.Avalonia` + `FluentAvaloniaTheme` (different design systems)
- `SukiUI` + `Material.Avalonia`
- More than one base theme of the same kind
- Mixing two icon families in the same view (pick one per app)

---

## Theme Selection Workflow

1. Identify product type → pick from matrix above.
2. Install minimum NuGets (1 base theme, optional 1 control library, 1 icon library).
3. Set `RequestedThemeVariant="Default"` so OS preference wins by default.
4. Override only the **accent color** + neutral surface colors via theme dictionaries.
5. Build app-specific Styles in `avares://MyApp/Styles/` — never modify the theme NuGet.
6. Test light **and** dark variant before committing.

---

## Common Mistakes

- **Importing two base themes** — `<FluentTheme/>` after `<FluentAvaloniaTheme/>` causes brush conflicts.
- **Hardcoding theme NuGet brushes** in views — they may be renamed in next version. Wrap them in your own semantic tokens.
- **Forgetting `RequestedThemeVariant="Default"`** — app stays in light mode regardless of OS setting.
- **Restyling default controls in App.axaml when using SukiUI/Semi** — overrides their styles and breaks intended look. Use Style classes instead.
- **Copy-pasting theme brush keys without checking version** — keys like `SystemAccentColor` exist in FluentTheme but not all alternatives.
- **Wrapping a normal `Window` in `SukiTheme` without `SukiWindow`** — content gets styled but the title bar stays native.
