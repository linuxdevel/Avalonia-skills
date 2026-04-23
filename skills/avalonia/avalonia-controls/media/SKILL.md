---
name: avalonia-controls-media
description: Use when working with Avalonia media controls: Image, DrawingImage, PathIcon, MediaPlayerControl, or WebView/NativeWebView. Covers asset loading URIs, stretch modes, vector icons, video playback setup, and browser embedding for Avalonia 12.
---

# Avalonia Media Controls

## Overview

Media controls display images, vector graphics, and embedded web or video content. Image sources use `avares://` URIs for app assets. Vector content (PathIcon, DrawingImage) scales without pixelation.

---

## Image

Displays raster (PNG, JPEG, BMP, WebP) or vector images.

| Property | Type | Notes |
|---|---|---|
| `Source` | `IImage` | `Bitmap`, `DrawingImage`, bound `IImage` |
| `Stretch` | `Stretch` | `None`, `Fill`, `Uniform` (default), `UniformToFill` |
| `Width` / `Height` | `double` | Explicit size; required if parent gives infinite space |
| `RenderOptions.BitmapInterpolationMode` | `BitmapInterpolationMode` | `Default`, `LowQuality`, `MediumQuality`, `HighQuality`, `None` |

**Stretch modes:**

| Value | Behavior |
|---|---|
| `None` | Original pixel size |
| `Fill` | Stretches to fill, distorts aspect ratio |
| `Uniform` | Letterboxed to fit, preserves aspect ratio |
| `UniformToFill` | Fills area, may clip, preserves aspect ratio |

**Loading from app assets (AXAML):**

```xml
<!-- Bundled asset — requires Build Action: AvaloniaResource -->
<Image Source="avares://MyApp/Assets/logo.png" Width="120" Height="40" Stretch="Uniform"/>

<!-- Relative path from project root (works at design time, runtime needs avares://) -->
<Image Source="/Assets/banner.jpg" Stretch="UniformToFill"/>
```

**Loading in code:**

```csharp
using Avalonia.Platform;
using Avalonia.Media.Imaging;

// From app assets
var uri = new Uri("avares://MyApp/Assets/logo.png");
var bitmap = new Bitmap(AssetLoader.Open(uri));
myImage.Source = bitmap;

// From file system
var bitmap = new Bitmap("/home/user/photo.png");
myImage.Source = bitmap;

// From stream
using var stream = File.OpenRead(path);
var bitmap = new Bitmap(stream);
```

**Binding to ViewModel:**

```csharp
// In ViewModel
private Bitmap? _photo;
public Bitmap? Photo
{
    get => _photo;
    set => SetProperty(ref _photo, value);
}

// Load async
public async Task LoadPhotoAsync(string path)
{
    await using var stream = File.OpenRead(path);
    Photo = await Task.Run(() => new Bitmap(stream));
}
```

```xml
<Image Source="{Binding Photo}" Width="200" Height="200" Stretch="UniformToFill"/>
```

**Dispose Bitmaps** when no longer needed to release native memory:

```csharp
_photo?.Dispose();
```

---

## DrawingImage

Vector image source built from geometry. Use for scalable icons embedded as image sources.

| Class | Use |
|---|---|
| `DrawingGroup` | Combines multiple drawings |
| `GeometryDrawing` | Fills/strokes a geometry path |
| `ImageDrawing` | Embeds a bitmap in a drawing |

```xml
<Image Width="64" Height="64">
    <Image.Source>
        <DrawingImage>
            <DrawingImage.Drawing>
                <DrawingGroup>
                    <!-- Background circle -->
                    <GeometryDrawing Brush="#6200EE"
                                     Geometry="M 32,32 m -32,0 a 32,32 0 1,0 64,0 a 32,32 0 1,0 -64,0"/>
                    <!-- Foreground path -->
                    <GeometryDrawing Brush="White"
                                     Geometry="M 20,20 L 44,32 L 20,44 Z"/>
                </DrawingGroup>
            </DrawingImage.Drawing>
        </DrawingImage>
    </Image.Source>
</Image>
```

> Prefer `PathIcon` for simple icons. Use `DrawingImage` when you need composite layered vector drawings or need to embed as `Image.Source`.

---

## PathIcon

SVG-path-based scalable icon. Preferred for UI icons. Color controlled by `Foreground`.

| Property | Type | Notes |
|---|---|---|
| `Data` | `Geometry` | SVG path string |
| `Foreground` | `IBrush` | Icon color (inherits from parent) |
| `Width` / `Height` | `double` | Display size |

```xml
<!-- Basic icon -->
<PathIcon Data="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
          Width="24" Height="24" Foreground="{DynamicResource TextFillColorPrimaryBrush}"/>

<!-- Icon button -->
<Button>
    <PathIcon Data="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12z" Width="20" Height="20"/>
</Button>

<!-- Colored icon -->
<PathIcon Data="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"
          Width="32" Height="32" Foreground="#4CAF50"/>

<!-- Inside a style/template, inheriting parent foreground -->
<PathIcon Data="..." Width="16" Height="16"/>
```

**Dynamic path from ViewModel:**

```xml
<PathIcon Data="{Binding IconPathData}" Width="24" Height="24"/>
```

```csharp
// In ViewModel
public string IconPathData => IsPlaying
    ? "M6 19h4V5H6v14zm8-14v14h4V5h-4z"   // pause icon
    : "M8 5v14l11-7z";                       // play icon
```

---

## MediaPlayerControl (LibVLCSharp)

Avalonia does not include built-in video playback. Use `LibVLCSharp.Avalonia`.

**NuGet packages:**
```
LibVLCSharp
LibVLCSharp.Avalonia
VideoLAN.LibVLC.Windows  (or .Mac / .Linux)
```

**Namespace:** `xmlns:vlc="using:LibVLCSharp.Avalonia"`

```xml
<vlc:VideoView x:Name="VideoView" MediaPlayer="{Binding MediaPlayer}">
    <!-- Overlay controls rendered on top of video -->
    <Grid VerticalAlignment="Bottom" Background="#80000000">
        <StackPanel Orientation="Horizontal" Margin="8">
            <Button Content="⏮" Command="{Binding StopCommand}"/>
            <Button Content="{Binding PlayPauseLabel}" Command="{Binding PlayPauseCommand}"/>
            <Slider Value="{Binding Position}" Maximum="1" Width="200"/>
        </StackPanel>
    </Grid>
</vlc:VideoView>
```

```csharp
using LibVLCSharp.Shared;

public class MediaViewModel : ObservableObject, IDisposable
{
    private readonly LibVLC _libVlc;
    public MediaPlayer MediaPlayer { get; }

    public MediaViewModel()
    {
        Core.Initialize(); // required before first use
        _libVlc = new LibVLC();
        MediaPlayer = new MediaPlayer(_libVlc);
    }

    public void Play(string url)
    {
        var media = new Media(_libVlc, url, FromType.FromLocation);
        MediaPlayer.Play(media);
    }

    public void Dispose()
    {
        MediaPlayer.Dispose();
        _libVlc.Dispose();
    }
}
```

---

## WebView / NativeWebView

Embeds a native browser engine. Requires `Avalonia.WebView` NuGet package.

**Supported engines:**
- Windows: WebView2 (requires WebView2 Runtime)
- macOS: WKWebView
- Linux: WebKitGtk

**NuGet:**
```
Avalonia.WebView
Avalonia.WebView.Desktop   (for desktop platforms)
```

**Registration in `Program.cs`:**

```csharp
AppBuilder.Configure<App>()
    .UsePlatformDetect()
    .UseAvaloniaNative()
    .UseSkia()
    .UseWebView()           // add this
    .StartWithClassicDesktopLifetime(args);
```

**AXAML usage:**

```xml
xmlns:wv="using:Avalonia.WebView"

<!-- Navigate to URL -->
<wv:WebView x:Name="Browser"
            Url="https://example.com"
            Width="800" Height="600"/>

<!-- Bind URL -->
<wv:WebView Url="{Binding CurrentUrl}"
            NavigationCompleted="OnNavigationCompleted"/>
```

**Code-behind:**

```csharp
// Navigate programmatically
Browser.Url = new Uri("https://example.com");

// Load local HTML
Browser.Url = new Uri("data:text/html,<h1>Hello from Avalonia</h1>");

// Load local file
Browser.Url = new Uri("file:///home/user/page.html");

// Handle navigation events
private void OnNavigationCompleted(object? sender, WebViewNavigationCompletedEventArgs e)
{
    if (!e.IsSuccess)
        Console.WriteLine($"Navigation failed: {e.WebErrorStatus}");
}
```

**Execute JavaScript:**

```csharp
var result = await Browser.ExecuteScriptAsync("document.title");
```

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| `avares://` URI not finding asset | Check exact casing — case-sensitive on Linux. Verify `Build Action = AvaloniaResource` in project |
| `Image` renders blank with no explicit size | Parent may give infinite space (e.g., `StackPanel`). Set `Width`/`Height` or `MaxWidth`/`MaxHeight` |
| `Image` leaking memory | `Bitmap` is `IDisposable` — call `.Dispose()` when image is replaced or view is closed |
| `PathIcon` color not changing | Use `Foreground` property, **not** `Fill`. `Fill` has no effect on `PathIcon` |
| `PathIcon` appears clipped | The `Data` geometry may have values outside `[0,0,width,height]`. Set `Width`/`Height` to match geometry bounds |
| `WebView` blank on Windows | WebView2 Runtime not installed. Distribute or check for runtime in installer |
| `WebView` crashes on non-desktop | Only works on `IClassicDesktopStyleApplicationLifetime`; guard before instantiation |
| `LibVLCSharp` video not showing | Must call `Core.Initialize()` before any LibVLC operation; missing platform NuGet package |
| `DrawingImage` GeometryDrawing invisible | Check that `Brush` is set — unfilled geometry with no stroke is invisible |
