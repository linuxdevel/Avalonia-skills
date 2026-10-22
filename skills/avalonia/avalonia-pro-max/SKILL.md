---
name: avalonia-pro-max
description: Use when designing or polishing the visual quality of an Avalonia app — choosing themes, building a design system, crafting beautiful screens, improving accessibility, motion, layout, or before shipping a UI. Routes to focused sub-skills for tokens, themes, components, motion, accessibility, layout patterns, icons, and pre-delivery review.
---

# Avalonia Pro Max — Beautiful Avalonia UIs

## Purpose

`avalonia` skills teach you the framework. `avalonia-pro-max` teaches you to make it **look and feel professional**: design tokens, theme selection, component recipes, motion, accessibility, responsive layout, icons, and final QA.

This skill is the desktop/cross-platform counterpart to `ui-ux-pro-max`. Same priorities, but every rule is mapped to Avalonia 12.x (XAML, FluentTheme, ControlThemes, pseudoclasses, AutomationProperties, etc.).

## Avalonia Versions

Supports Avalonia 11.3, 12.0 and 12.1 (latest 12.1.4). Detect the project's version first and use the `avalonia-versions` skill (version matrix, renamed APIs, label convention). In these sub-skills: **(12.0+)** / **(12.1+)** = needs that version or newer, **(11.x)** = 11.x only (removed/obsolete in 12), no label = works in 11.3, 12.0 and 12.1. Never mix 11.x and 12.x APIs. No project yet → 12.1.x on `net10.0`.

## When to Use

### Must use
- Building a new screen, window, or page
- Restyling an existing app or replacing the default look
- Choosing a theme library (FluentAvalonia, SukiUI, Semi, Material, ShadUI, Ursa…)
- Defining colors, typography, spacing, radius, elevation tokens
- Adding animations, transitions, hover/press states
- Implementing dark/light theme variants
- Reviewing UI before shipping or PR
- The user says "make this beautiful", "modernize", "polish", "looks bland"

### Recommended
- Migrating WPF visuals to Avalonia and wanting modern feel (combine with `avalonia-wpf-migration`)
- Cross-platform polish (desktop + mobile + web)
- Building a reusable component library

### Skip
- Pure data binding, MVVM plumbing, services, deployment — use base `avalonia` subskills

## Routing Table

| Task | Load sub-subskill |
|---|---|
| Design tokens, palettes, typography scale, spacing, theme variants, semantic color system | `avalonia-pro-max/design-system` |
| Picking and configuring a theme library (FluentAvalonia, SukiUI, Semi, Material, ShadUI, Ursa, Material.Avalonia) | `avalonia-pro-max/themes` |
| Production-ready XAML recipes: cards, dialogs, command bar, sidebar nav, settings page, forms, empty states | `avalonia-pro-max/components` |
| Transitions, keyframe animations, easing, hover/press feedback, page transitions, reduced-motion | `avalonia-pro-max/motion` |
| Contrast, focus rings, keyboard navigation, AutomationProperties, screen readers, dynamic font scaling | `avalonia-pro-max/accessibility` |
| Responsive design, breakpoints, AdaptiveLayout, NavigationView vs sidebar vs bottom nav, dashboards | `avalonia-pro-max/layout-patterns` |
| Icon libraries (Lucide, Material, FontAwesome, Heroicons), SVG (Svg.Skia), brand assets, image optimization | `avalonia-pro-max/icons-imagery` |
| Final QA before merge / release — checklist of every must-pass item | `avalonia-pro-max/review-checklist` |
| Show the user 2–3 design alternatives **as rendered Avalonia screens** in a browser gallery before implementation; user picks one in chat | `avalonia-pro-max/preview-server` |

## Workflow for "Build a beautiful Avalonia app/screen"

1. **Establish the design system** → `design-system`
   Choose palette (semantic tokens), typography scale, spacing rhythm, radius scale, elevation. Persist as `Resources/Tokens.axaml` + theme-variant dictionaries.

2. **Pick a theme base** → `themes`
   FluentTheme + community theme (or pure custom). The themes sub-skill has a recommendation matrix by app type.

3. **Build screens with recipes** → `components`
   Use the recipe library — never hand-roll a card / dialog / nav from zero when a vetted pattern exists.

4. **Apply motion** → `motion`
   Add `Transitions` to interactive controls, page transitions for navigation, respect `prefers-reduced-motion`.

5. **Verify accessibility** → `accessibility`
   AutomationProperties, focus order, contrast 4.5:1, keyboard parity.

6. **Check responsive behavior** → `layout-patterns`
   Test at 800/1280/1920 widths; mobile/tablet via Avalonia.Mobile.

7. **Run the review checklist** → `review-checklist`
   Pre-merge audit. If anything fails, loop back.

### Optional: Show the user options first

If the user wants to **see and pick** between alternatives before you commit to a direction (e.g., "show me a few options", "what would this look like"), insert this **before step 3**:

→ `preview-server` — generate 3 variant `.axaml` files, render each via `Avalonia.Headless` to PNG (light/dark × wide/compact), serve a side-by-side HTML gallery. The user reviews in their browser and tells you which to build.

## Priority of Concerns

Same global priority as `ui-ux-pro-max`, mapped to Avalonia:

| # | Category | Avalonia Mechanism | Sub-skill |
|---|---|---|---|
| 1 | Accessibility | `AutomationProperties.*`, focus pseudoclasses, contrast | `accessibility` |
| 2 | Touch & interaction | Min hit-target via `Padding`/`MinHeight`, `:pointerover` / `:pressed` styles | `components`, `motion` |
| 3 | Performance | `CompiledBinding` (default in 12.0+, opt-in in 11.x), virtualization (`VirtualizingStackPanel`), `RenderOptions.BitmapInterpolationMode` | `components`, `layout-patterns` |
| 4 | Style selection | Theme library + ControlTheme + Style classes | `themes`, `design-system` |
| 5 | Layout & responsive | Grid `*` / `Auto`, `AdaptiveLayout`, `NavigationView.PaneDisplayMode` | `layout-patterns` |
| 6 | Typography & color | Theme-variant dictionaries, `DynamicResource`, type ramp | `design-system` |
| 7 | Animation | `Transitions`, `Animation`, `KeyFrame`, `IterationCount` | `motion` |
| 8 | Forms & feedback | Validation (`DataAnnotations` / `INotifyDataErrorInfo`), `Flyout`, error pseudoclasses | `components` |
| 9 | Navigation | `TabControl`, `SplitView`, FluentAvalonia `NavigationView` | `layout-patterns`, `components` |
| 10 | Charts & data | LiveCharts2, ScottPlot, OxyPlot | `components` |

## Recommended Stack for "Beautiful by Default"

A pragmatic starter pack that yields a polished app with minimal effort:

```xml
<!-- App.axaml -->
<Application.Styles>
  <FluentTheme/>
  <StyleInclude Source="avares://MyApp/Resources/Tokens.axaml"/>
  <StyleInclude Source="avares://MyApp/Resources/ComponentStyles.axaml"/>
</Application.Styles>
```

NuGet:
- `Avalonia` 12.1.x (or the project's version)
- `Avalonia.Themes.Fluent` (or `SukiUI` / `Semi.Avalonia`)
- `FluentAvaloniaUI` (3.x for Avalonia 12, 2.5.x for 11.3) — NavigationView, InfoBar, TeachingTip
- `Lucide.Avalonia` or `Material.Icons.Avalonia` — icons
- `Svg.Skia` — vector assets
- `Avalonia.Xaml.Behaviors` — declarative event triggers

The `themes` sub-skill explains alternatives by product type.

## Anti-Patterns (See Each Sub-skill for Detail)

- Hard-coded hex colors scattered across views — use `DynamicResource` + theme dictionaries
- Emoji as icons — use a vector icon library
- Removing focus rings to look cleaner — breaks keyboard a11y
- Same `Margin="10"` everywhere — use a 4/8 spacing scale
- Animating `Width`/`Height` instead of `RenderTransform` Scale — janky
- `StaticResource` for theme-variant brushes — won't update on variant change
- Forgetting `AutomationProperties.Name` on icon-only buttons
- Mixing FluentTheme + Material.Avalonia in the same app — visual inconsistency
- Custom controls without `:pointerover` / `:pressed` / `:disabled` / `:focus` styles
- One giant `Window` with no `UserControl` decomposition
