---
name: avalonia-versions
description: Use FIRST when the Avalonia version matters — detecting which Avalonia version a project uses, checking whether a feature/API exists in 11.3, 12.0 or 12.1, migrating 11.x → 12.x, or upgrading 12.0 → 12.1. Contains the version/feature matrix, renamed/removed API tables, and the version-label conventions used by all other Avalonia skills.
---
# Avalonia Versions & Feature Matrix

## Supported Versions

| Line | Latest patch | Released | .NET | Status |
|---|---|---|---|---|
| **12.1** | 12.1.4 | 12.1.0: Jul 2026 | net8.0+ (net10.0 recommended; **required** for Android/iOS) | Current stable — default for new projects |
| **12.0** | 12.0.5 | 12.0.0: Apr 2026 | same as 12.1 | Supported — drop-in upgrade to 12.1 |
| **11.3** | 11.3.22 | — | netstandard2.0 / net6.0+ / .NET Framework | Legacy — maintenance only; plan migration |

Versions older than 11.3 are out of scope; treat them like 11.3 but expect missing APIs.

## Step 1 — Detect the Project's Version

Before writing code, find the version. Search in this order:

1. `Directory.Packages.props` → `<PackageVersion Include="Avalonia" Version="..."/>`
2. `*.csproj` → `<PackageReference Include="Avalonia" Version="..."/>`
3. `Directory.Build.props` → an `AvaloniaVersion` property or similar
4. `dotnet list package | grep -i avalonia`

```sh
grep -rhoE 'Include="Avalonia(\.Desktop)?" Version="[^"]+"' --include='*.csproj' --include='*.props' .
```

- No project yet → use **12.1.x** (latest patch), `net10.0`.
- Mixed versions across `Avalonia.*` packages → bug. All core `Avalonia.*` packages must share one version (third-party themes/controls have their own versioning).
- `ReactiveUI.Avalonia`, `Avalonia.Controls.WebView`, `Avalonia.Controls.DataGrid`, `Avalonia.Controls.TreeDataGrid` version on their own schedule; check NuGet for the release that matches the core version.

## Version Label Convention (used across all skills)

| Label | Meaning |
|---|---|
| **(12.0+)** | Exists from 12.0.0 onward. Not in 11.x |
| **(12.1+)** | Exists from 12.1.0 onward. Not in 12.0 or 11.x |
| **(11.x)** | 11.x API — removed/obsolete in 12. Only use in 11.x projects |
| no label | Works in 11.3, 12.0 and 12.1 |

When a skill shows a 12.x API and an `(11.x)` alternative side by side, pick the one that matches the project's version. **Never mix** — e.g. don't use `DataObject` in a 12.x project.

## Feature Matrix

✅ available · ❌ not available · ⚠️ obsolete (works, warns) · 🧪 experimental

### Platform & runtime

| Feature | 11.3 | 12.0 | 12.1 |
|---|---|---|---|
| .NET Framework / netstandard2.0 targets | ✅ | ❌ | ❌ |
| net8.0 minimum, net10.0 recommended | — | ✅ | ✅ |
| Android/iOS on net10.0 (required) | ❌ | ✅ | ✅ |
| Mac Catalyst (via `Avalonia.iOS`) | ❌ | ✅ | ✅ |
| iOS scene delegate | ❌ | ✅ | ✅ |
| Rebuilt Android backend, multiple activities, `IActivityApplicationLifetime` | ❌ | ✅ | ✅ |
| Android system-theme change detection | ❌ | ❌ | ✅ |
| Linux AT-SPI2 accessibility | ❌ | ✅ | ✅ |
| Native Wayland backend (`Avalonia.Wayland` + `.UseWayland()`) | ❌ | ❌ | 🧪 (not picked by `UsePlatformDetect()`) |
| X11 drag-and-drop between processes (XDND) | ❌ | ❌ | ✅ |
| X11/Windows render at monitor refresh rate (>60 FPS) | ❌ | ❌ | ✅ |
| Embed Avalonia in WinUI 3 (`Avalonia.WinUI`) | ❌ | ❌ | ✅ |
| Windows 11 window corner rounding control | ❌ | ❌ | ✅ |
| `Avalonia.Direct2D1` backend | ✅ | ❌ (use Skia) | ❌ |
| `Avalonia.Browser.Blazor`, `Avalonia.Tizen` | ✅ | ❌ | ❌ |
| SBOM shipped with packages | ❌ | ❌ | ✅ |

### Controls

| Control / feature | 11.3 | 12.0 | 12.1 |
|---|---|---|---|
| `GroupBox` | ❌ | ✅ | ✅ |
| `PipsPager` | ❌ | ✅ | ✅ |
| Page-based navigation (`Page`, `ContentPage`, `NavigationPage`, `TabbedPage`, `DrawerPage`, `CarouselPage`, `CommandBar`) | ❌ | ✅ | ✅ |
| `TableView` (read-only tabular, virtualized) | ❌ | ❌ | ✅ |
| `NativeWebView` / `NativeWebDialog` open source (`Avalonia.Controls.WebView`) — Windows, macOS, Linux, iOS; Android experimental; **not browser/WASM** | ❌ (commercial) | ✅ | ✅ |
| `DataGrid` (`Avalonia.Controls.DataGrid`) | ✅ | ✅ | ✅ maintenance mode — prefer `TableView`/`TreeDataGrid` for new read-only grids |
| `TreeDataGrid` (`Avalonia.Controls.TreeDataGrid`) — needs Avalonia Accelerate licence since 11.2.0; 12.x packages need Avalonia ≥ 12.0.1 | ✅ (11.x pkg) | ✅ | ✅ |
| `TextBox.PlaceholderText` / `UseFloatingPlaceholder` | ❌ | ✅ | ✅ |
| `TextBox.Watermark` / `UseFloatingWatermark` | ✅ | ⚠️ | ⚠️ |
| `PlaceholderForeground` (TextBox, AutoCompleteBox, CalendarDatePicker, NumericUpDown) | ❌ | ✅ | ✅ |
| `TabItem.IconTemplate` | ❌ | ✅ | ✅ |
| `FlyoutBase.IsOpen` styled property | ❌ | ✅ | ✅ |
| Carousel gestures + `WrapSelection` | ❌ | ✅ | ✅ |
| `DrawingImage.Viewbox` | ❌ | ✅ | ✅ |
| `NativeDock.Menu` (macOS dock menu) | ❌ | ✅ | ✅ |
| `WindowDrawnDecorations` (themeable client-side decorations) | ❌ | ✅ | ✅ |
| `Window.WindowDecorations` | ❌ | ✅ | ✅ |
| `Window.SystemDecorations` / `ExtendClientAreaChromeHints` | ✅ | ⚠️ / ❌ | ⚠️ / ❌ |

### Bindings, text, input, threading

| Feature | 11.3 | 12.0 | 12.1 |
|---|---|---|---|
| Compiled bindings **on by default** (`AvaloniaUseCompiledBindingsByDefault` defaults `true`) | ❌ (opt-in) | ✅ | ✅ |
| `CompiledBinding.Create(...)` from LINQ expressions | ❌ | ✅ | ✅ |
| Binding plugins (`BindingPlugins`) configurable | ✅ | ❌ removed | ❌ |
| Data-annotations validation on by default | ✅ | ❌ (opt-in) | ❌ |
| `TextOptions` (`TextRenderingMode` etc.) | ❌ | ✅ | ✅ |
| `TextElement.LetterSpacing` (inherited) | ❌ (`TextBlock.LetterSpacing`) | ✅ | ✅ |
| `UseHarfBuzz()` required with explicit `UseSkia()` | ❌ | ✅ | ✅ |
| Access keys match printed symbol (accents, digits) | ❌ | ✅ | ✅ |
| Focus Traversal API (`IFocusManager.FindNextElement`/`TryMoveFocus`), cancellable focus, `FocusChangedEventArgs` | ❌ | ✅ | ✅ |
| Gesture events directly on `InputElement` (no `Gestures.` prefix) | ❌ | ✅ | ✅ |
| Touch/pen select on **release** (not press) | ❌ | ✅ | ✅ |
| `Dispatcher.CurrentDispatcher`, `Dispatcher.FromThread`, `AvaloniaObject.Dispatcher`, `Dispatcher.Yield` | ❌ | ✅ | ✅ |
| Async clipboard/drag-drop (`IAsyncDataTransfer`, `DataTransfer`) | ❌ | ✅ | ✅ |
| `PlatformFeedback` (haptics/sound, Android/iOS) | ❌ | ❌ | ✅ |
| Hidden controls stop style animations (`PlaybackBehavior="Always"` to override) | ❌ | ✅ | ✅ |

## 11.x → 12.0 Migration: Renamed / Replaced APIs

| 11.x | 12.x |
|---|---|
| `IDataObject` / `DataObject` | `IAsyncDataTransfer` / `DataTransfer` + `DataTransferItem` |
| `DataFormats.Text` etc. | `DataFormat.Text` etc. |
| `DragDrop.DoDragDrop(...)` | `await DragDrop.DoDragDropAsync(...)` |
| `DragEventArgs.Data` | `DragEventArgs.DataTransfer` |
| `IClipboard.GetTextAsync` / `SetTextAsync` | `TryGetTextAsync` / `SetTextAsync` (extension methods, `ClipboardExtensions`) |
| `IClipboard.SetDataObjectAsync` / `GetDataAsync` / `GetFormatsAsync` | `SetDataAsync` / `TryGetDataAsync` / `GetDataFormatsAsync` |
| `IBinding` / `InstancedBinding` | `BindingBase` / `BindingExpressionBase` |
| `new Binding(...)` in C# | `ReflectionBinding` or `CompiledBinding` |
| `GotFocusEventArgs` | `FocusChangedEventArgs` |
| `KeyboardNavigationHandler.GetNext` | `IFocusManager.FindNextElement(...)` / `TryMoveFocus(...)` |
| `Gestures.Pinch="..."` etc. in XAML | `Pinch="..."` |
| `TopLevel.PlatformSettings` | `visual.GetPlatformSettings()` |
| `VisualExtensions.GetVisualRoot` | `GetPresentationSource()` → `.RootVisual` |
| `(TopLevel)visual.GetVisualRoot()` | `TopLevel.GetTopLevel(visual)` |
| `SystemDecorations` / `ExtendClientAreaChromeHints` | `WindowDecorations` |
| `Chrome.TitleBar`, `CaptionButtons`, `ChromeOverlayLayer` | `WindowDrawnDecorations` |
| `VisualLayerManager.AdornerLayer` / `OverlayLayer` | `AdornerLayer.GetAdornerLayer(v)` / `OverlayLayer.GetOverlayLayer(v)` |
| `TextBox.Watermark` / `UseFloatingWatermark` | `PlaceholderText` / `UseFloatingPlaceholder` |
| `RenderOptions.TextRenderingMode` | `TextOptions.TextRenderingMode` |
| `TextBlock.LetterSpacing` | `TextElement.LetterSpacing` |
| `AccessText.AccessKey` (`char`) | `string?` |
| `NativeMenuItemToggleType` | `MenuItemToggleType` |
| `AvaloniaMainActivity<TApp>` | `AvaloniaMainActivity` + `[Application] class App : AvaloniaAndroidApplication<TApp>` |
| `ISingleViewApplicationLifetime` (Android) | `IActivityApplicationLifetime` with `MainViewFactory` (iOS/Browser still use `ISingleViewApplicationLifetime`) |
| `Avalonia.Diagnostics` + `AttachDevTools()` | `AvaloniaUI.DiagnosticsSupport` + `AttachDeveloperTools()` |
| `Avalonia.ReactiveUI` package (deprecated on NuGet, last 11.3.8) | `ReactiveUI.Avalonia` package (maintained by ReactiveUI team) |
| `Avalonia.Direct2D1` / `UseDirect2D1()` | `UseSkia()` |
| xUnit v2 / NUnit 3 (with `Avalonia.Headless.*`) | xUnit v3 / NUnit 4 |
| `FuncMultiValueConverter` lambda `IEnumerable<TIn>` | `IReadOnlyList<TIn>` |
| `ResourcesChangedEventArgs.Empty` / `new(...)` | `ResourcesChangedEventArgs.Create(...)` (now a struct) |

### Removed in 12 (were obsolete in 11)

`OpenFileDialog`/`SaveFileDialog`/`OpenFolderDialog`/`SystemDialog` → `IStorageProvider` · `ToggleButton.Checked/Unchecked/Indeterminate` events → `IsCheckedChanged` · `Popup.PlacementMode`/`ContextMenu.PlacementMode` → `Placement` · `CubicBezierEasing` → `SplineEasing` · `CustomAnimatorBase` → `InterpolatingAnimator<T>` · `ItemContainerGenerator.ContainerFromIndex` → `ItemsControl.ContainerFromIndex` · `BindingPriority.TemplatedParent` → `Template` · `DrawingContext.PushPreTransform/PushPostTransform` → `PushTransform` · `RadialGradientBrush.Radius` → `RadiusX`/`RadiusY` · `Screen.PixelDensity` → `Scaling` · `Screen.Primary` → `IsPrimary` · `IStyleable` → `StyledElement` · `IActivatableApplicationLifetime` → `TryGetFeature<IActivatableLifetime>()` · `IInsetsManager.DisplayEdgeToEdge` → `DisplayEdgeToEdgePreference` · `TopLevel.PointerOverElement` (no replacement) · `TextInputMethodClient.ShowInputPanel` → `InputPaneActivationRequested` event · Type 1 fonts · `BinaryFormatter` clipboard on Windows.

### Behavior changes in 12 (no compile error — silent!)

- Compiled bindings on by default: `{Binding}` without `x:DataType` now fails to compile. Add `x:DataType`, or use `{ReflectionBinding}`, or set `<AvaloniaUseCompiledBindingsByDefault>false</...>`.
- Data-annotation validation off by default. Properties registered with `enableDataValidation: true` report errors automatically.
- Touch/pen: selection/focus on pointer **release**. `ListBoxItem`/`TreeViewItem` handle selection themselves (no bubbling to `ItemsControl`).
- `Window.WindowState` is a direct property — **cannot be set from a style**.
- Style-triggered animations pause on invisible controls — set `Animation.PlaybackBehavior="Always"` to keep ticking.
- `Dispatcher.InvokeAsync` captures `ExecutionContext` (AsyncLocal, culture flow).
- `DispatcherTimer` / `AvaloniaSynchronizationContext` use the **current** dispatcher, not always the UI thread — create timers on the UI thread.
- Explicit `UseSkia()` without `UseHarfBuzz()` → `InvalidOperationException: No text shaping system configured`. (`UsePlatformDetect()` handles this.)
- Windows `ExtendClientAreaToDecorationsHint` fixed — remove old margin workarounds.

## 12.0 → 12.1 Upgrade

Drop-in: bump all `Avalonia.*` to `12.1.x`. No API breaks. Notes:
- Multiple dirty-rect clipping now off by default; stencil buffers on by default (more HW-accelerated clipping).
- Apps now render at monitor refresh rate on X11 (and Windows with non-default render modes) — animations that assumed 60 FPS ticks still work (time-based), but CPU/GPU use may rise.
- Wayland is opt-in and experimental: `AppBuilder.Configure<App>().UseWayland()` with `Avalonia.Wayland`; keep `UsePlatformDetect()` as default.

## Common Mistakes

- Writing 12.x API (`DataTransfer`, `PlaceholderText`, `GroupBox`) into an 11.x project, or 11.x API into 12.x — check version first.
- Upgrading `Avalonia` but not `Avalonia.Desktop`/`Avalonia.Themes.Fluent`/`Avalonia.Headless.*` — all must match.
- Keeping `Avalonia.ReactiveUI` / `Avalonia.Diagnostics` after moving to 12 — they don't exist for 12.
- Forgetting `net10.0` on Android/iOS heads in 12.x.
- Assuming `UsePlatformDetect()` picks Wayland in 12.1 — it doesn't.

## Sources
- Breaking changes: https://docs.avaloniaui.net/docs/avalonia12-breaking-changes
- 12.0.0 release notes: https://github.com/AvaloniaUI/Avalonia/discussions/21091
- What's new in 12.1: https://avaloniaui.net/blog/release-12-1
- Package versions: https://www.nuget.org/packages/Avalonia
