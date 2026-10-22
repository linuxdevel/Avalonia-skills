---
name: avalonia-controls-media
description: Use when working with Avalonia media controls: Image, DrawingImage (incl. Viewbox 12.0+), PathIcon, MediaPlayerControl (LibVLCSharp), or NativeWebView/NativeWebDialog (Avalonia.Controls.WebView, open source in 12.0+, commercial in 11.x). Covers asset loading URIs, stretch modes, vector icons, video playback setup, and web content embedding.
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

**`DrawingImage.Viewbox` (12.0+)** — `Rect?` in DIPs: which region of the `Drawing` to render. Crops the drawing or adds empty space around it. `null` (default) = the drawing's own bounds. Not in 11.x.

```xml
<DrawingImage Viewbox="0,0,64,64" Drawing="{StaticResource IconDrawing}"/>
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

## NativeWebView / NativeWebDialog (12.0+)

Official native browser control, open source (MIT) since 12.0, package **`Avalonia.Controls.WebView`** (versioned separately from core — pick the release matching your Avalonia version). Namespace `Avalonia.Controls` = default xmlns, **no prefix needed**. In **11.x** this control was a commercial add-on (Avalonia Accelerate), not part of the free packages; the old `Avalonia.WebView` / `wv:WebView` / `.UseWebView()` / `ExecuteScriptAsync` / `Url` API does not exist in the official control.

```sh
dotnet add package Avalonia.Controls.WebView
```

**No `AppBuilder` call is required** — the docs show only the package reference and the control. (`UsePlatformDetect()` as usual.)

| Platform | `NativeWebView` backend |
|---|---|
| Windows | WebView2 (preinstalled on Win 11; Win 10 may need the Evergreen runtime) |
| macOS / iOS | WKWebView |
| Linux | WPE WebKit (preferred if installed) or WebKitGTK 4.1 (GTK 3, libsoup 3; WebKitGTK 6.0 unsupported; needs X11 GDK backend / XWayland) |
| Android | Android WebView (API 21+) |
| Browser (WASM) | **Not supported** for `NativeWebView`/`NativeWebDialog` (only `WebAuthenticationBroker` works) |

`NativeWebDialog` (separate window hosting web content): Windows, macOS, Linux only.

```xml
<!-- default xmlns, no prefix -->
<NativeWebView x:Name="Browser"
               Source="https://example.com"
               NavigationCompleted="OnNavigationCompleted"
               WebMessageReceived="OnWebMessage"/>

<!-- Bind Source (type Uri) -->
<NativeWebView Source="{Binding CurrentUri}"/>
```

| `NativeWebView` member | Notes |
|---|---|
| `Source` (`Uri`) | Styled property; set to navigate |
| `Navigate(Uri)`, `NavigateToString(string html, Uri? baseUri = null)` | Programmatic navigation / inline HTML |
| `GoBack()`, `GoForward()`, `Refresh()`, `Stop()` → `bool`; `CanGoBack`, `CanGoForward` | History |
| `InvokeScript(string)` → `Task<string?>` | Run JS, returns result string. Faulted task (`InvalidOperationException`) if native adapter not created yet |
| Events | `NavigationStarted`, `NavigationCompleted` (`WebViewNavigationCompletedEventArgs.IsSuccess`), `WebMessageReceived` (`.Body`), `NewWindowRequested`, `WebResourceRequested`, `EnvironmentRequested`, `AdapterCreated`, `AdapterDestroyed` |
| Other | `UserAgent`, `Background`, `AdapterPreference`, `AdapterInfo`, `ShowPrintUI()`, `PrintToPdfStreamAsync()`, `TryGetCookieManager()`, `TryGetCommandManager()`, `TryGetPlatformHandle()`, `BeginReparenting()` |

```csharp
// Code-behind
Browser.Source = new Uri("https://example.com");
Browser.NavigateToString("<h1>Hello from Avalonia</h1>");

private void OnNavigationCompleted(object? sender, WebViewNavigationCompletedEventArgs e)
{
    if (!e.IsSuccess) Debug.WriteLine("Navigation failed");
}

// C# -> JS (wait until the adapter exists, e.g. after NavigationCompleted)
string? title = await Browser.InvokeScript("document.title");

// JS -> C#: page calls the helper `invokeCSharpAction(payload)`; C# receives it here
private void OnWebMessage(object? sender, WebMessageReceivedEventArgs e)
{
    var body = e.Body;
}
```

**NativeWebDialog** — dedicated window, not a control; `IDisposable`:

```csharp
var dialog = new NativeWebDialog
{
    Title = "Sign in",
    CanUserResize = true,
    Source = new Uri("https://example.com/login")
};
dialog.NavigationCompleted += (_, e) => { /* e.IsSuccess */ };
dialog.Show();            // or dialog.Show(owner) with a TopLevel
// dialog.Close(); dialog.Dispose();
```

**OAuth:** `WebAuthenticationBroker.AuthenticateAsync(window, new WebAuthenticatorOptions { RequestUri = ..., RedirectUri = ... })` → result `.CallbackUri` carries the response (all platforms incl. browser; Android experimental; browser needs CORS on the redirect page and .NET 10).

> Linux packages: WebKitGTK 4.1 + libsoup 3 (baseline); WPE WebKit optional (Debian 13+/Fedora/Arch, not packaged on Ubuntu).

---

## Community Media Libraries

| Library | NuGet / Source | Purpose |
|---|---|---|
| LibVLCSharp.Avalonia | `LibVLCSharp.Avalonia` | Full VLC media engine — video, audio, streams |
| AvaloniaGif | `AvaloniaGif` | Animated GIF playback control |
| FFME.Avalonia | GitHub: WangsYi/ffme.avalonia | FFmpeg-based MediaElement |
| Mpv.Avalonia | GitHub: saverinonrails/Mpv.Avalonia | MPV + OpenGL media control |
| MediaPlayerUI.NET | `MediaPlayerUI.NET` | Reusable media player UI shell |
| CefGlue | `Xilium.CefGlue.Avalonia` | Chromium Embedded Framework WebView (bundled Chromium; alternative to the native `NativeWebView`) |
| OutSystems WebView | GitHub: OutSystems/WebView | Full-featured Avalonia WebView |
| MuPDFCore | `MuPDFCore` | PDF/XPS/ePub rendering via MuPDF |
| Markdown.Avalonia | `Markdown.Avalonia` | Markdown renderer control |
| LiveMarkdown.Avalonia | GitHub: DearVa/LiveMarkdown.Avalonia | High-performance real-time markdown |

### LibVLCSharp Full Example
```csharp
// NuGet: LibVLCSharp.Avalonia + VideoLAN.LibVLC.Windows (or .Linux, .Mac)
using LibVLCSharp.Shared;
using LibVLCSharp.Avalonia;

var libVlc = new LibVLC();
var mediaPlayer = new MediaPlayer(libVlc);

// In XAML:
// <vlc:VideoView MediaPlayer="{Binding MediaPlayer}" HorizontalAlignment="Stretch"/>

mediaPlayer.Play(new Media(libVlc, new Uri("https://example.com/stream.mp4")));
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| `avares://` URI not finding asset | Check exact casing — case-sensitive on Linux. Verify `Build Action = AvaloniaResource` in project |
| `Image` renders blank with no explicit size | Parent may give infinite space (e.g., `StackPanel`). Set `Width`/`Height` or `MaxWidth`/`MaxHeight` |
| `Image` leaking memory | `Bitmap` is `IDisposable` — call `.Dispose()` when image is replaced or view is closed |
| `PathIcon` color not changing | Use `Foreground` property, **not** `Fill`. `Fill` has no effect on `PathIcon` |
| `PathIcon` appears clipped | The `Data` geometry may have values outside `[0,0,width,height]`. Set `Width`/`Height` to match geometry bounds |
| `NativeWebView` blank on Windows | WebView2 Runtime missing (Win 10) — install/distribute the Evergreen runtime |
| `NativeWebView` / `.UseWebView()` / `Avalonia.WebView` copied from old samples | Wrong for 12: use package `Avalonia.Controls.WebView`, `<NativeWebView Source="..."/>`, no AppBuilder call, no `wv:` prefix |
| `NativeWebView` on Browser (WASM) target | Not supported there — guard with a platform check. Only `WebAuthenticationBroker` works in browser |
| `InvokeScript` throws `InvalidOperationException` | Native adapter not created yet — call after `AdapterCreated` / `NavigationCompleted` |
| `NativeWebView` blank on Linux | Install WebKitGTK 4.1 (+ libsoup 3) or WPE WebKit; WebKitGTK 6.0 is unsupported; GTK backend needs X11/XWayland |
| Using `NativeWebView` in an 11.x project | Commercial add-on in 11.x; free from 12.0 — upgrade or use CefGlue / community control |
| `LibVLCSharp` video not showing | Must call `Core.Initialize()` before any LibVLC operation; missing platform NuGet package |
| `DrawingImage` GeometryDrawing invisible | Check that `Brush` is set — unfilled geometry with no stroke is invisible |
