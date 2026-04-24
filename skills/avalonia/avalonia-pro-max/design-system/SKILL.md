---
name: avalonia-pro-max/design-system
description: Use when establishing or refactoring an Avalonia app's design system — semantic color tokens, theme-variant dictionaries (light/dark), typography scale, spacing rhythm, radius and elevation tokens. Produces production-ready Resources/Tokens.axaml.
---

# Design System for Avalonia

## Goal

A design system in Avalonia is a set of **named resources** (colors, brushes, fonts, doubles, thicknesses) that:

1. Live in `ResourceDictionary` files merged into `App.axaml`.
2. Are referenced via `{DynamicResource Name}` in views — never hard-coded hex/numbers.
3. Are split by **theme variant** (Light/Dark) so the entire UI re-themes instantly.
4. Follow a 3-layer naming model: **primitive → semantic → component**.

---

## 3-Layer Token Model

### Layer 1 — Primitives (raw values, never used in views)

```xml
<!-- Resources/Primitives.axaml -->
<ResourceDictionary xmlns="https://github.com/avaloniaui"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <!-- Color ramp: 50..950 like Tailwind -->
  <Color x:Key="Slate50">#F8FAFC</Color>
  <Color x:Key="Slate100">#F1F5F9</Color>
  <Color x:Key="Slate200">#E2E8F0</Color>
  <Color x:Key="Slate500">#64748B</Color>
  <Color x:Key="Slate700">#334155</Color>
  <Color x:Key="Slate900">#0F172A</Color>
  <Color x:Key="Slate950">#020617</Color>

  <Color x:Key="Blue500">#3B82F6</Color>
  <Color x:Key="Blue600">#2563EB</Color>
  <Color x:Key="Blue700">#1D4ED8</Color>

  <Color x:Key="Red500">#EF4444</Color>
  <Color x:Key="Green500">#22C55E</Color>
  <Color x:Key="Amber500">#F59E0B</Color>
</ResourceDictionary>
```

### Layer 2 — Semantic tokens (theme-variant aware)

```xml
<!-- Resources/Semantic.axaml -->
<ResourceDictionary xmlns="https://github.com/avaloniaui"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <ResourceDictionary.MergedDictionaries>
    <ResourceInclude Source="avares://MyApp/Resources/Primitives.axaml"/>
  </ResourceDictionary.MergedDictionaries>

  <ResourceDictionary.ThemeDictionaries>

    <ResourceDictionary x:Key="Light">
      <!-- Surfaces -->
      <SolidColorBrush x:Key="SurfaceBackgroundBrush" Color="{StaticResource Slate50}"/>
      <SolidColorBrush x:Key="SurfaceBrush"           Color="#FFFFFF"/>
      <SolidColorBrush x:Key="SurfaceElevatedBrush"   Color="#FFFFFF"/>
      <SolidColorBrush x:Key="SurfaceMutedBrush"      Color="{StaticResource Slate100}"/>

      <!-- Text -->
      <SolidColorBrush x:Key="TextPrimaryBrush"   Color="{StaticResource Slate900}"/>
      <SolidColorBrush x:Key="TextSecondaryBrush" Color="{StaticResource Slate700}"/>
      <SolidColorBrush x:Key="TextMutedBrush"     Color="{StaticResource Slate500}"/>
      <SolidColorBrush x:Key="TextOnAccentBrush"  Color="#FFFFFF"/>

      <!-- Borders / dividers -->
      <SolidColorBrush x:Key="BorderBrush"         Color="{StaticResource Slate200}"/>
      <SolidColorBrush x:Key="BorderStrongBrush"   Color="{StaticResource Slate500}"/>

      <!-- Brand / status -->
      <SolidColorBrush x:Key="AccentBrush"  Color="{StaticResource Blue600}"/>
      <SolidColorBrush x:Key="DangerBrush"  Color="{StaticResource Red500}"/>
      <SolidColorBrush x:Key="SuccessBrush" Color="{StaticResource Green500}"/>
      <SolidColorBrush x:Key="WarningBrush" Color="{StaticResource Amber500}"/>
    </ResourceDictionary>

    <ResourceDictionary x:Key="Dark">
      <SolidColorBrush x:Key="SurfaceBackgroundBrush" Color="{StaticResource Slate950}"/>
      <SolidColorBrush x:Key="SurfaceBrush"           Color="{StaticResource Slate900}"/>
      <SolidColorBrush x:Key="SurfaceElevatedBrush"   Color="#1E293B"/>
      <SolidColorBrush x:Key="SurfaceMutedBrush"      Color="#1E293B"/>

      <SolidColorBrush x:Key="TextPrimaryBrush"   Color="{StaticResource Slate50}"/>
      <SolidColorBrush x:Key="TextSecondaryBrush" Color="{StaticResource Slate200}"/>
      <SolidColorBrush x:Key="TextMutedBrush"     Color="{StaticResource Slate500}"/>
      <SolidColorBrush x:Key="TextOnAccentBrush"  Color="#FFFFFF"/>

      <SolidColorBrush x:Key="BorderBrush"       Color="#1E293B"/>
      <SolidColorBrush x:Key="BorderStrongBrush" Color="{StaticResource Slate700}"/>

      <SolidColorBrush x:Key="AccentBrush"  Color="{StaticResource Blue500}"/>
      <SolidColorBrush x:Key="DangerBrush"  Color="#F87171"/>
      <SolidColorBrush x:Key="SuccessBrush" Color="#4ADE80"/>
      <SolidColorBrush x:Key="WarningBrush" Color="#FBBF24"/>
    </ResourceDictionary>

  </ResourceDictionary.ThemeDictionaries>
</ResourceDictionary>
```

### Layer 3 — Component-specific (optional)

```xml
<SolidColorBrush x:Key="ButtonPrimaryBackgroundBrush" Color="{DynamicResource AccentBrush}"/>
<SolidColorBrush x:Key="CardBackgroundBrush"          Color="{DynamicResource SurfaceElevatedBrush}"/>
```

**Rule:** Views use Layer 2/3 only. Never reference `Slate900` directly from a view.

---

## Typography Scale

Choose ONE scale and stick to it. Modular scale 1.25 (Major Third) is a safe default.

```xml
<!-- Resources/Typography.axaml -->
<ResourceDictionary xmlns="https://github.com/avaloniaui"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                    xmlns:sys="using:System">

  <!-- Font families -->
  <FontFamily x:Key="FontSans">avares://MyApp/Assets/Fonts/Inter-Variable.ttf#Inter</FontFamily>
  <FontFamily x:Key="FontMono">avares://MyApp/Assets/Fonts/JetBrainsMono-Variable.ttf#JetBrains Mono</FontFamily>

  <!-- Sizes (modular scale 1.25) -->
  <sys:Double x:Key="FontSizeXs">12</sys:Double>
  <sys:Double x:Key="FontSizeSm">13</sys:Double>
  <sys:Double x:Key="FontSizeBase">14</sys:Double>   <!-- desktop body -->
  <sys:Double x:Key="FontSizeMd">16</sys:Double>
  <sys:Double x:Key="FontSizeLg">18</sys:Double>
  <sys:Double x:Key="FontSizeXl">22</sys:Double>
  <sys:Double x:Key="FontSize2xl">28</sys:Double>
  <sys:Double x:Key="FontSize3xl">36</sys:Double>
  <sys:Double x:Key="FontSize4xl">48</sys:Double>

  <!-- Line heights (multipliers) -->
  <sys:Double x:Key="LineHeightTight">1.2</sys:Double>
  <sys:Double x:Key="LineHeightNormal">1.5</sys:Double>
  <sys:Double x:Key="LineHeightRelaxed">1.65</sys:Double>
</ResourceDictionary>
```

Type ramp Styles:

```xml
<Style Selector="TextBlock.h1">
  <Setter Property="FontFamily" Value="{StaticResource FontSans}"/>
  <Setter Property="FontSize"   Value="{StaticResource FontSize3xl}"/>
  <Setter Property="FontWeight" Value="SemiBold"/>
  <Setter Property="LineHeight" Value="44"/>
  <Setter Property="Foreground" Value="{DynamicResource TextPrimaryBrush}"/>
</Style>

<Style Selector="TextBlock.body">
  <Setter Property="FontSize"   Value="{StaticResource FontSizeBase}"/>
  <Setter Property="LineHeight" Value="21"/>
  <Setter Property="Foreground" Value="{DynamicResource TextPrimaryBrush}"/>
</Style>

<Style Selector="TextBlock.muted">
  <Setter Property="Foreground" Value="{DynamicResource TextMutedBrush}"/>
</Style>
```

Usage: `<TextBlock Classes="h1">Dashboard</TextBlock>`

### Variable fonts

Avalonia 11+ supports variable fonts (`.ttf`/`.otf` with axes). Inter and JetBrains Mono variable versions cover most needs at one file each.

---

## Spacing Scale (4 / 8 rhythm)

```xml
<sys:Double x:Key="Space0">0</sys:Double>
<sys:Double x:Key="Space1">4</sys:Double>
<sys:Double x:Key="Space2">8</sys:Double>
<sys:Double x:Key="Space3">12</sys:Double>
<sys:Double x:Key="Space4">16</sys:Double>
<sys:Double x:Key="Space5">20</sys:Double>
<sys:Double x:Key="Space6">24</sys:Double>
<sys:Double x:Key="Space8">32</sys:Double>
<sys:Double x:Key="Space10">40</sys:Double>
<sys:Double x:Key="Space12">48</sys:Double>
<sys:Double x:Key="Space16">64</sys:Double>
```

For `Margin`/`Padding` use `Thickness`:

```xml
<Thickness x:Key="PaddingCard">20</Thickness>
<Thickness x:Key="PaddingCardCompact">12</Thickness>
<Thickness x:Key="PaddingPage">24,16</Thickness>
```

`Padding="{StaticResource PaddingCard}"`.

---

## Radius & Elevation

```xml
<CornerRadius x:Key="RadiusSm">4</CornerRadius>
<CornerRadius x:Key="RadiusMd">8</CornerRadius>
<CornerRadius x:Key="RadiusLg">12</CornerRadius>
<CornerRadius x:Key="RadiusXl">16</CornerRadius>
<CornerRadius x:Key="RadiusFull">9999</CornerRadius>

<!-- Elevation via BoxShadow -->
<BoxShadows x:Key="ShadowSm">0 1 2 0 #19000000</BoxShadows>
<BoxShadows x:Key="ShadowMd">0 4 8 -2 #26000000, 0 2 4 -2 #1A000000</BoxShadows>
<BoxShadows x:Key="ShadowLg">0 12 24 -8 #33000000, 0 4 8 -4 #1F000000</BoxShadows>
```

Apply to `Border`:
```xml
<Border Background="{DynamicResource SurfaceBrush}"
        CornerRadius="{StaticResource RadiusLg}"
        BoxShadow="{StaticResource ShadowMd}"
        Padding="{StaticResource PaddingCard}">
  <!-- card content -->
</Border>
```

For dark mode, halve shadow opacity in the dark theme dictionary (or use a subtle 1px border instead).

---

## Wire Everything Up

```xml
<!-- App.axaml -->
<Application xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             x:Class="MyApp.App"
             RequestedThemeVariant="Default">

  <Application.Resources>
    <ResourceDictionary>
      <ResourceDictionary.MergedDictionaries>
        <ResourceInclude Source="avares://MyApp/Resources/Primitives.axaml"/>
        <ResourceInclude Source="avares://MyApp/Resources/Semantic.axaml"/>
        <ResourceInclude Source="avares://MyApp/Resources/Typography.axaml"/>
        <ResourceInclude Source="avares://MyApp/Resources/Spacing.axaml"/>
        <ResourceInclude Source="avares://MyApp/Resources/Radius.axaml"/>
      </ResourceDictionary.MergedDictionaries>
    </ResourceDictionary>
  </Application.Resources>

  <Application.Styles>
    <FluentTheme/>
    <StyleInclude Source="avares://MyApp/Styles/Typography.axaml"/>
    <StyleInclude Source="avares://MyApp/Styles/Components.axaml"/>
  </Application.Styles>
</Application>
```

---

## Theme Switching at Runtime

```csharp
Application.Current!.RequestedThemeVariant =
    Application.Current.ActualThemeVariant == ThemeVariant.Dark
        ? ThemeVariant.Light
        : ThemeVariant.Dark;
```

Persist to settings; restore on launch in `OnFrameworkInitializationCompleted`.

---

## Palette Selection by Product Type

| Product type | Accent suggestion | Tone |
|---|---|---|
| Productivity / SaaS dashboard | Blue 600 / Indigo 600 | Cool, professional |
| Developer tool / IDE | Slate + accent (Cyan 500 or Violet 500) | Neutral, dark-mode first |
| Finance / banking | Green 600 or Navy 800 | Trust, conservative |
| Health / wellness | Teal 500 / Emerald 500 | Calm, fresh |
| Creative / media | Bold gradient or Magenta 500 | Vibrant |
| Gaming / entertainment | Purple 600 + Neon accent | Energetic |
| Enterprise B2B | Slate + Brand color from logo | Restrained |
| Education / kids | Saturated multi-color (Amber/Sky/Pink) | Friendly |

Always validate accent on white **and** the dark surface for ≥4.5:1 contrast on text overlays.

---

## Common Mistakes

- **Hex literals in views** — kills theming. Always `DynamicResource`.
- **Missing dark-mode variant** — app looks broken if user's OS is dark.
- **Using `StaticResource` for theme-variant brushes** — won't switch at runtime.
- **More than ~3 accent colors** — visual noise; pick one accent + one optional secondary.
- **Inventing one-off spacing values** (`Margin="13,7"`) — breaks rhythm.
- **Body text below 13px on desktop** — readability suffers.
- **Pure black `#000` text on pure white** — too harsh; use Slate 900 / Slate 50.
- **Same shadow opacity in dark mode** — looks muddy. Reduce or replace with a 1px border.
