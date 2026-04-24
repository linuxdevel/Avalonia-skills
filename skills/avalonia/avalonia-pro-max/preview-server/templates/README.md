# Variant Template

Copy this folder to `.preview/variants/<N>/` and edit the four files. The render script picks up everything automatically.

## Files

- **`README.md`** — design intent. First `# Heading` line becomes the variant title in the gallery; the rest becomes the description card. Keep it to 3–5 lines.
- **`Resources.axaml`** — token dictionary (semantic colors, spacing, radius). MUST be a `<ResourceDictionary>` root with optional `<ResourceDictionary.ThemeDictionaries>` for Light/Dark.
- **`Styles.axaml`** — component styles (Button classes, Card class, etc.). MUST be a `<Styles>` root.
- **`PreviewScene.axaml`** — the actual screen to render. MUST be a `<UserControl>` (or any `Control` root). The host wraps it in a `<Window>` of the requested viewport size.
- **`packages.txt`** *(optional)* — extra NuGet refs needed by this variant, one per line, format `Name` or `Name:Version`. Lines starting with `#` are ignored. Examples:
  ```
  FluentAvalonia:2.1.0
  Lucide.Avalonia
  # SukiUI:6.0.0
  ```

## Hard rules

1. **Do not put `<Application>` or `<Window>` at the root** of `PreviewScene.axaml` — the host owns those.
2. **`x:Class` is not allowed** anywhere (no code-behind in variants — pure XAML only).
3. **All assets must be `avares://AvaloniaPreviewHost/...`** if referenced. Easier: skip images, use `PathIcon` with inline geometry.
4. **Use only namespaces from packages declared in `packages.txt`** (or the default Avalonia ones).
5. **Theme-variant brushes must use `DynamicResource`**, not `StaticResource`, so the renderer's theme switch works.

## Default available namespaces

```
xmlns="https://github.com/avaloniaui"
xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
```

Add more (with `packages.txt` entries) as needed:
```
xmlns:ui="using:FluentAvalonia.UI.Controls"        <!-- needs FluentAvalonia -->
xmlns:lucide="using:Lucide.Avalonia"               <!-- needs Lucide.Avalonia -->
xmlns:semi="https://irihi.tech/semi"               <!-- needs Semi.Avalonia -->
xmlns:suki="clr-namespace:SukiUI.Controls;assembly=SukiUI"  <!-- needs SukiUI -->
```
