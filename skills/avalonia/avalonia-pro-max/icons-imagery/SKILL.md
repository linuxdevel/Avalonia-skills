---
name: avalonia-pro-max/icons-imagery
description: Use when picking an icon library, drawing custom icons, embedding SVG, or handling images and brand assets in an Avalonia app. Covers Lucide, Material.Icons, Projektanker.Icons, MahApps.IconPacks, FluentSystemIcons, Heroicons, Svg.Skia, PathIcon, and asset performance.
---

# Icons & Imagery

## Icon Library Selection

| Library | NuGet | Style | Notes |
|---|---|---|---|
| **Lucide.Avalonia** | `Lucide.Avalonia` | Modern stroke (Feather-derived) | First pick for modern UIs. Single visual language. |
| **Material.Icons.Avalonia** | `Material.Icons.Avalonia` | Material Design (filled + outline) | 6,000+ icons. Pair with Material.Avalonia. |
| **Projektanker.Icons.Avalonia** | `Projektanker.Icons.Avalonia` + provider pkg | Multi-provider (FontAwesome, MDI) | Use when you need FontAwesome specifically. |
| **MahApps.Metro.IconPacks.Avalonia** | `MahApps.Metro.IconPacks.Avalonia` | 21,000+ across 9 packs | Largest selection; heavier dependency. |
| **FluentSystemIcons** | `FluentIcons.Avalonia` | Microsoft Fluent | Best with FluentAvalonia / Windows-feel apps. |
| **HeroIcons.Avalonia** | community (russkyc/heroicons-avalonia) | Tailwind Heroicons | Great with shadcn-style designs. |

**Rule:** Pick **one** icon family per app. Mixing stroke widths and corner styles is the fastest way to look amateur.

---

## Lucide.Avalonia (recommended default)

```sh
dotnet add package Lucide.Avalonia
```

```xml
<Window xmlns="https://github.com/avaloniaui"
        xmlns:lucide="using:Lucide.Avalonia">
  <lucide:Lucide Icon="Home" Width="20" Height="20"
                 StrokeBrush="{DynamicResource TextPrimaryBrush}"
                 StrokeThickness="1.75"/>
</Window>
```

Set app-wide defaults via Style:
```xml
<Style Selector="lucide|Lucide">
  <Setter Property="Width" Value="18"/>
  <Setter Property="Height" Value="18"/>
  <Setter Property="StrokeThickness" Value="1.75"/>
  <Setter Property="StrokeBrush" Value="{DynamicResource TextPrimaryBrush}"/>
</Style>
```

---

## Material.Icons.Avalonia

```xml
<Window xmlns:mi="using:Material.Icons.Avalonia">
  <mi:MaterialIcon Kind="Home" Width="20" Height="20"
                   Foreground="{DynamicResource TextPrimaryBrush}"/>
</Window>
```

`Kind` is an enum with all 6,000+ MDI icons. IDE auto-complete works.

---

## Projektanker.Icons.Avalonia

```sh
dotnet add package Projektanker.Icons.Avalonia
dotnet add package Projektanker.Icons.Avalonia.FontAwesome
```

`Program.cs`:
```csharp
public static AppBuilder BuildAvaloniaApp() => AppBuilder.Configure<App>()
    .UsePlatformDetect()
    .WithIcons(c => c.Register<FontAwesomeIconProvider>());
```

```xml
<i:Icon xmlns:i="using:Projektanker.Icons.Avalonia"
        Value="fa-solid fa-house" FontSize="20"/>
```

---

## Built-in PathIcon (no external dependency)

```xml
<PathIcon Width="16" Height="16"
          Foreground="{DynamicResource TextPrimaryBrush}"
          Data="M12 2L2 22h20L12 2z"/>
```

Store geometries in resources for reuse:
```xml
<StreamGeometry x:Key="HomeIconGeometry">M3 12L12 4l9 8v8h-6v-6h-6v6H3z</StreamGeometry>

<PathIcon Data="{StaticResource HomeIconGeometry}"/>
```

This is fine for a handful of icons; for >10, use a library.

---

## SVG Files (Svg.Skia)

```sh
dotnet add package Svg.Skia
dotnet add package Svg.Controls.Skia.Avalonia
```

```xml
<Window xmlns:svg="using:Avalonia.Svg.Skia">
  <svg:Svg Path="avares://MyApp/Assets/logo.svg" Width="120" Height="40"/>
</Window>
```

Pros: pixel-perfect at any size, theme-aware fills if SVG uses `currentColor`.
Cons: extra dependency, larger binary than `PathIcon`.

For a brand logo, SVG is usually the right call. For UI glyphs, prefer the icon library.

---

## Icon Sizing Discipline

Define a token scale and stick to it:

```xml
<sys:Double x:Key="IconSizeXs">12</sys:Double>
<sys:Double x:Key="IconSizeSm">14</sys:Double>
<sys:Double x:Key="IconSizeMd">16</sys:Double>   <!-- inline with body text -->
<sys:Double x:Key="IconSizeLg">20</sys:Double>   <!-- toolbar button -->
<sys:Double x:Key="IconSizeXl">24</sys:Double>   <!-- nav item -->
<sys:Double x:Key="IconSize2xl">32</sys:Double>  <!-- empty state hero -->
```

`Width` and `Height` together (square). Never set just one.

Stroke widths: 1.5 or 1.75 for stroke icons. Filled icons need no stroke setting.

---

## Coloring Icons

Use `Foreground` (PathIcon, MaterialIcon) or `StrokeBrush` (Lucide) bound to semantic tokens — never hardcode:

```xml
<lucide:Lucide Icon="Trash" StrokeBrush="{DynamicResource DangerBrush}"/>
```

For buttons that swap icon color on hover:
```xml
<Style Selector="Button.icon:pointerover lucide|Lucide">
  <Setter Property="StrokeBrush" Value="{DynamicResource AccentBrush}"/>
</Style>
```

---

## Images

### Static asset
```xml
<Image Source="avares://MyApp/Assets/avatar.png"
       Width="40" Height="40"
       Stretch="UniformToFill"/>
```

### Bound URL
```xml
<Image Source="{Binding AvatarUrl, Converter={StaticResource AsyncImageConverter}}"/>
```

For network images, use `AsyncImageLoader` (`AsyncImageLoader.Avalonia`) — handles cache + placeholder.

### Rounded image (avatar)
```xml
<Border CornerRadius="9999" ClipToBounds="True"
        Width="40" Height="40">
  <Image Source="{Binding AvatarUrl}" Stretch="UniformToFill"/>
</Border>
```

### Bitmap performance
```xml
<Image Source="..."
       RenderOptions.BitmapInterpolationMode="HighQuality"/>
```

For thumbnails, prefer `LowQuality` to save GPU. For hero photos, `HighQuality`.

---

## Asset Pipeline

1. Source assets (SVG, PNG, fonts) live under `Assets/`.
2. Set Build Action = **AvaloniaResource** (not `Content`, not `Resource`).
3. Reference via `avares://AssemblyName/Assets/file.ext`.

In `csproj`:
```xml
<ItemGroup>
  <AvaloniaResource Include="Assets/**"/>
</ItemGroup>
```

---

## Brand Assets

- Use the **official** logo file from the brand kit; never recreate or recolor.
- Maintain clear-space margin around the mark (typically equal to the cap-height of the wordmark).
- Provide a light-mode and dark-mode variant if the logo has color or contrast issues.
- Ship as SVG for crispness; supply a 2× / 3× PNG fallback for platforms where SVG isn't ideal.

---

## Image Optimization

- Compress PNGs (`pngquant`, `zopflipng`) before adding to repo.
- Use WebP for photos >50 KB (Avalonia supports WebP via SkiaSharp).
- Keep app icon set complete: provide ICO (Windows), ICNS (macOS), and PNGs at 16/32/48/64/128/256/512 px.
- Lazy-load large galleries via virtualization rather than loading all at once.

---

## Common Mistakes

- **Mixing two icon families** in one app — different stroke widths and corner styles look broken.
- **Using emoji as icons** (🏠 ⚙️ 🔔) — font/OS dependent, not themable.
- **Hardcoded icon size on every usage** — drifts. Use the size token scale.
- **Setting only `Width`** — non-square icons look squashed.
- **Hardcoded icon color** — won't switch with theme variant.
- **PNG icons at 1× resolution** — blurry on high-DPI; ship 2×/3× or use SVG/PathIcon.
- **Build Action `Resource` instead of `AvaloniaResource`** — file isn't found at runtime.
- **No `AutomationProperties.Name` on icon-only buttons** — see accessibility sub-skill.
- **Loading network images on UI thread** — janky scroll. Use `AsyncImageLoader.Avalonia`.
