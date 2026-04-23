---
name: avalonia-services
description: Use when accessing Avalonia platform services via TopLevel: clipboard read/write, file/folder/save dialogs via StorageProvider, URI/file launching via Launcher, screen and window info, focus manager, in-app notifications via WindowNotificationManager, or IME input method access.
---
# Avalonia Platform Services

## Overview
Platform services are accessed via the `TopLevel` class (root of visual tree — typically `Window` or `PopupRoot`).

```csharp
var topLevel = TopLevel.GetTopLevel(this); // 'this' = any attached control
```

Returns `null` if control is not yet attached to visual tree. Call in `OnAttachedToVisualTree` or later.

## Clipboard

```csharp
var clipboard = TopLevel.GetTopLevel(this)?.Clipboard;

// Write text
await clipboard!.SetTextAsync("Hello, world");

// Write custom data object
var data = new DataObject();
data.Set("application/x-myformat", myObject);
data.Set(DataFormats.Text, "fallback text");
await clipboard.SetDataObjectAsync(data);

// Read text
var text = await clipboard!.GetTextAsync(); // null if no text on clipboard

// Read custom format
var formats = await clipboard!.GetFormatsAsync(); // string[]
var raw = await clipboard!.GetDataAsync("application/x-myformat");

// Clear
await clipboard!.ClearAsync();
```

## File Dialogs (StorageProvider)

```csharp
var storage = TopLevel.GetTopLevel(this)?.StorageProvider;
```

**Open file(s):**
```csharp
var files = await storage!.OpenFilePickerAsync(new FilePickerOpenOptions
{
    Title = "Open File",
    AllowMultiple = false,
    FileTypeFilter = new[]
    {
        new FilePickerFileType("Images")
        {
            Patterns = new[] { "*.png", "*.jpg", "*.jpeg", "*.webp" },
            MimeTypes = new[] { "image/png", "image/jpeg" }
        },
        new FilePickerFileType("All Files") { Patterns = new[] { "*" } }
    },
    SuggestedStartLocation = await storage.TryGetWellKnownFolderAsync(WellKnownFolder.Pictures)
});

if (files.Count > 0)
{
    await using var stream = await files[0].OpenReadAsync();
    var bitmap = new Bitmap(stream);
}
```

Built-in `FilePickerFileTypes`: `All`, `TextPlain`, `Pdf`, `Images`

**Save file:**
```csharp
var file = await storage!.SaveFilePickerAsync(new FilePickerSaveOptions
{
    Title = "Save As",
    DefaultExtension = "txt",
    SuggestedFileName = "untitled",
    FileTypeChoices = new[]
    {
        new FilePickerFileType("Text Files") { Patterns = new[] { "*.txt" } },
        new FilePickerFileType("All Files") { Patterns = new[] { "*" } }
    }
});

if (file is not null)
{
    await using var stream = await file.OpenWriteAsync();
    await using var writer = new StreamWriter(stream);
    await writer.WriteAsync(content);
}
```

**Open folder:**
```csharp
var folders = await storage!.OpenFolderPickerAsync(new FolderPickerOpenOptions
{
    Title = "Select Folder",
    AllowMultiple = false,
    SuggestedStartLocation = await storage.TryGetWellKnownFolderAsync(WellKnownFolder.Documents)
});

if (folders.Count > 0)
{
    var path = folders[0].Path.LocalPath; // platform file path string
}
```

**Well-known folders:**
`Desktop`, `Documents`, `Downloads`, `Music`, `Pictures`, `Videos`

**Navigate to path:**
```csharp
var folder = await storage.TryGetFolderFromPathAsync("/home/user/projects");
var file = await storage.TryGetFileFromPathAsync("/home/user/file.txt");
```

## Launcher (Open URLs / Files)

```csharp
var launcher = TopLevel.GetTopLevel(this)?.Launcher;

// Open URL in default browser
await launcher!.LaunchUriAsync(new Uri("https://avaloniaui.net"));

// Open file with default app
await launcher!.LaunchFileAsync(myStorageFile); // IStorageFile
```

## Screen Information

```csharp
var screens = TopLevel.GetTopLevel(this)?.Screens;

var primary = screens?.Primary;       // IScreen
var all = screens?.All;               // IReadOnlyList<IScreen>
var count = screens?.ScreenCount;     // int

// IScreen properties
var bounds = primary?.Bounds;         // PixelRect — full screen area
var workArea = primary?.WorkingArea;  // PixelRect — area excluding taskbar
var scaling = primary?.Scaling;       // double — DPI scaling factor (1.0 = 96dpi)
var isPrimary = primary?.IsPrimary;   // bool
```

Window position relative to screen:
```csharp
if (this is Window window)
{
    var position = window.Position;     // PixelPoint
    var size = window.ClientSize;       // Size (in DIPs)
    window.WindowState = WindowState.Maximized;
}
```

## Focus Manager

```csharp
var fm = TopLevel.GetTopLevel(this)?.FocusManager;

// Get focused element
var focused = fm?.GetFocusedElement(); // IInputElement?

// Focus a control
fm?.Focus(myControl, NavigationMethod.Pointer);
// NavigationMethod: Unspecified, Tab, Pointer, Directional

// Or directly
myControl.Focus(NavigationMethod.Tab);
```

## In-App Notifications

Requires NuGet: `Avalonia.Controls.Notifications`

```csharp
using Avalonia.Controls.Notifications;

// Create once, store as field
private WindowNotificationManager? _notifications;

protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
{
    base.OnAttachedToVisualTree(e);
    _notifications = new WindowNotificationManager(TopLevel.GetTopLevel(this))
    {
        Position = NotificationPosition.TopRight,
        MaxItems = 3,
        Margin = new Thickness(0, 0, 15, 40)
    };
}

// Show notification
_notifications?.Show(new Notification(
    title: "Success",
    message: "File saved successfully.",
    type: NotificationType.Success,
    expiration: TimeSpan.FromSeconds(4),
    onClick: () => Console.WriteLine("Clicked"),
    onClose: () => Console.WriteLine("Dismissed")));
```

`NotificationType`: `Information`, `Success`, `Warning`, `Error`
`NotificationPosition`: `TopLeft`, `TopCenter`, `TopRight`, `BottomLeft`, `BottomCenter`, `BottomRight`

## Input Method (IME)

```csharp
var inputMethod = TopLevel.GetTopLevel(this)?.InputMethod;
inputMethod?.SetCursorRect(new Rect(x, y, 0, lineHeight));
```

## Insider Info: TopLevel Properties Summary

| Property | Type | Purpose |
|---|---|---|
| `Clipboard` | `IClipboard?` | Read/write clipboard |
| `StorageProvider` | `IStorageProvider?` | File/folder dialogs |
| `Launcher` | `ILauncher?` | Open URIs and files |
| `Screens` | `IScreens?` | Screen geometry/DPI |
| `FocusManager` | `IFocusManager?` | Focus control |
| `InputMethod` | `IInputMethod?` | IME cursor position |
| `PlatformSettings` | `IPlatformSettings?` | OS theme, animation prefs |
| `RendererDiagnostics` | `RendererDiagnostics` | FPS overlay, dirty rects |

Platform settings (dark mode, animations):
```csharp
var settings = TopLevel.GetTopLevel(this)?.PlatformSettings;
var isDark = settings?.GetColorValues().ThemeVariant == PlatformThemeVariant.Dark;
var reduceMotion = settings?.GetColorValues().ContrastPreference == ColorContrastPreference.High;
```

## Common Mistakes

- **`TopLevel.GetTopLevel(this)` returns `null` before attachment** — never call in constructor; use `OnAttachedToVisualTree` or control-loaded events
- **`IStorageFile` is not a file path** — must use `OpenReadAsync()`/`OpenWriteAsync()` streams; `file.Path.LocalPath` may fail on sandboxed platforms (iOS/Android/browser)
- **Clipboard operations must be awaited** — fire-and-forget silently fails or throws on some platforms
- **`WindowNotificationManager` created per-notification** — creates multiple overlapping managers; create once and store as field
- **`WindowNotificationManager` must be created on UI thread** — don't create from background tasks
- **`LaunchUriAsync` for file:// URIs** — use `LaunchFileAsync` with `IStorageFile` instead for local files
