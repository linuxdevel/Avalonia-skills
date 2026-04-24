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

Customize the FluentTheme accent via well-known resource keys:

```xml
<Application.Resources>
  <ResourceDictionary>
    <ResourceDictionary.ThemeDictionaries>
      <ResourceDictionary x:Key="Light">
        <SolidColorBrush x:Key="SystemAccentColor"      Color="#2563EB"/>
        <SolidColorBrush x:Key="SystemAccentColorDark1" Color="#1D4ED8"/>
        <SolidColorBrush x:Key="SystemAccentColorLight1" Color="#3B82F6"/>
      </ResourceDictionary>
      <ResourceDictionary x:Key="Dark">
        <SolidColorBrush x:Key="SystemAccentColor"      Color="#3B82F6"/>
      </ResourceDictionary>
    </ResourceDictionary.ThemeDictionaries>
  </ResourceDictionary>
</Application.Resources>
```

---

## FluentAvalonia

WinUI3-style controls + accent system. Best companion to `FluentTheme`.

```sh
dotnet add package FluentAvalonia
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
dotnet add package SukiUI
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
dotnet add package Semi.Avalonia
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
dotnet add package Semi.Avalonia.Ursa
```

```xml
<Application.Styles>
  <semi:SemiTheme/>
  <ursa:UrsaTheme/>
  <ursa:SemiTheme/>   <!-- bridge styles -->
</Application.Styles>
```

---

## Material.Avalonia

True Material Design 3.

```sh
dotnet add package Material.Avalonia
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

shadcn/ui-inspired styling for Avalonia. Currently community-driven; check repo for latest install.

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
- `Semi.Avalonia` + `Ursa.Avalonia` (+ Semi.Avalonia.Ursa bridge)
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
