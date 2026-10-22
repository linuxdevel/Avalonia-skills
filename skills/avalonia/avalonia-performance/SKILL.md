---
name: avalonia-performance
description: Use when diagnosing or improving Avalonia performance — slow scrolling or large lists (virtualization, TableView), FPS/layout/render profiling with DevTools and RendererDiagnostics overlays, compiled vs reflection bindings, image decode size, visual-tree depth, startup time and size (ReadyToRun, trimming, NativeAOT), and memory leaks (event handlers, DataContext, images).
---
# Avalonia Performance & Diagnostics

Version labels follow `avalonia-versions`: **(12.0+)**, **(12.1+)**, **(11.x)**, no label = 11.3/12.0/12.1. For publish steps (RIDs, single file, installers) see `avalonia-deployment`; this skill covers only the performance-relevant flags.

## Workflow

1. **Measure first**: overlay FPS/layout/render graphs, then DevTools visual tree, then `dotnet-counters`/`dotnet-trace`.
2. Fix the biggest cost: usually (a) non-virtualized big list, (b) reflection bindings, (c) full-size image decode, (d) deep/huge visual tree, (e) work on the UI thread.
3. Re-measure in **Release** (`dotnet run -c Release`); Debug builds and an attached debugger distort results.

## Diagnosing

### DevTools

| | Package | Call |
|---|---|---|
| **(12.0+)** | `AvaloniaUI.DiagnosticsSupport` (+ `AvaloniaUI.DeveloperTools` global tool `avdt`, Avalonia Plus tooling) | `this.AttachDeveloperTools();` in `Application.Initialize()` |
| **(11.x)** | `Avalonia.Diagnostics` | `this.AttachDevTools();` (or `window.AttachDevTools()`) |

```csharp
public override void Initialize()
{
    AvaloniaXamlLoader.Load(this);
#if DEBUG
    this.AttachDeveloperTools();   // (12.0+) — AppBuilder equivalent: .WithDeveloperTools()
#endif
}
```

`Avalonia.Diagnostics` has no 12.x release; never reference both. Options (`DeveloperToolsOptions`): `ConnectOnStartup`, `Runner`, `Protocol` (HTTP default port 29414, or named pipes), `AutoConnectFromDesignMode`, `DiagnosticLogger`. Docs: https://docs.avaloniaui.net/tools/developer-tools/installation

### Renderer overlays (all versions)

`TopLevel.RendererDiagnostics.DebugOverlays` is a `[Flags]` enum `RendererDebugOverlays` (namespace `Avalonia.Rendering`):

| Flag | Shows |
|---|---|
| `Fps` | frames per second |
| `DirtyRects` | invalidated rectangles per frame |
| `LayoutTimeGraph` | recent layout pass times |
| `RenderTimeGraph` | recent render times |

```csharp
var top = TopLevel.GetTopLevel(this)!;
top.RendererDiagnostics.DebugOverlays =
    RendererDebugOverlays.Fps | RendererDebugOverlays.LayoutTimeGraph | RendererDebugOverlays.RenderTimeGraph;
// toggle off: RendererDebugOverlays.None
```

How to read: large dirty rects every frame on a static screen means something is animating or invalidating continuously; tall layout graph means layout thrash (see below); tall render graph means heavy drawing (shadows, big images, effects).

### .NET tooling (run against the app process)

```sh
dotnet-counters monitor --process-id <pid> System.Runtime        # GC heap, alloc rate, gen0/1/2 counts, threadpool
dotnet-trace collect --process-id <pid> --profile cpu-sampling   # open .nettrace in PerfView / VS / Speedscope
dotnet-gcdump collect --process-id <pid>                         # heap snapshot to find leaked controls/VMs
```

Install these tools yourself from nuget.org (`dotnet tool install --global dotnet-counters`); verify package ids before installing. Rising gen2 heap after closing windows/views means a leak (see Memory).

## UI Performance

### Virtualization

| Control | Virtualizes by default? |
|---|---|
| `ListBox`, `ComboBox` dropdown, `TreeView`-style items hosts | Yes (`VirtualizingStackPanel`) |
| `ItemsControl` | **No**; `ItemsPanel` defaults to `StackPanel` |
| `TableView` **(12.1+)** | Yes, recycles rows **and** cells |
| `DataGrid` | Yes (rows); maintenance mode in 12.1, prefer `TableView`/`TreeDataGrid` |
| `ItemsRepeater` | **Retired**, not supported as of 12. Migrate to `ItemsControl`/`ListBox` |

```xml
<!-- ItemsControl with virtualization -->
<ScrollViewer>
  <ItemsControl ItemsSource="{Binding Items}">
    <ItemsControl.ItemsPanel>
      <ItemsPanelTemplate><VirtualizingStackPanel/></ItemsPanelTemplate>
    </ItemsControl.ItemsPanel>
  </ItemsControl>
</ScrollViewer>
<!-- Simpler: use ListBox; style it if you do not want selection visuals -->
```

`VirtualizingStackPanel` members: `Orientation`, `CacheLength` (extra space realized above/below viewport; raising it trades memory for smoother scrolling), `FirstRealizedIndex` / `LastRealizedIndex` (-1 when nothing realized; handy in a diagnostic to confirm virtualization is active).

What breaks virtualization (the panel gets unlimited space, realizes every item):
- Putting the list inside an **unconstrained-height parent**: `StackPanel`, `ScrollViewer` with `VerticalScrollBarVisibility="Auto"` wrapping a `ListBox`, or `Grid` row with `Height="Auto"`. Give the list a bounded height (`*` row, `DockPanel` fill) and let the list own its scrolling.
- Nesting a `ListBox` inside a `ScrollViewer` just to "scroll the page".
- Replacing `ItemsPanel` with a non-virtualizing panel (`StackPanel`, `WrapPanel`, `UniformGrid`).
- Variable-size, very heavy `ItemTemplate`s (virtualization works, but each realization is expensive; flatten the template).
- Realizing everything in code (`ItemsPanelRoot.Children` loops, `ContainerFromIndex` over the whole range).

Also: bind `ItemsSource` to an `ObservableCollection<T>` and mutate incrementally; replacing the whole collection reference rebuilds every container. For bulk loads, build the list then assign once.

### Bindings

| | Cost |
|---|---|
| Compiled (`x:DataType` set) | fastest, build-time checked, trim/AOT safe. **Default in 12.0+** |
| `{ReflectionBinding}` / (11.x) default `{Binding}` | reflection at runtime, slower, trimmer-unsafe |

- **(12.0+)** `{Binding}` without `x:DataType` fails to compile; set `x:DataType` on the view root and on `DataTemplate`s.
- **(11.x)** Opt in project-wide: `<AvaloniaUseCompiledBindingsByDefault>true</AvaloniaUseCompiledBindingsByDefault>`, or per-file `x:CompileBindings="True"`.
- C# **(12.0+)**: `CompiledBinding.Create((Item i) => i.Value)` instead of `new Binding(...)`.
- Avoid converters that allocate per update; cache results. Prefer `MultiBinding` only when necessary.
- Do not raise `PropertyChanged` in tight loops; batch updates then notify once, and never update bound VM properties from background threads without `Dispatcher.UIThread.Post`.

### Visual tree, layout, rendering

- **Fewer elements**: replace nested `Border > Grid > StackPanel` chains with a single `Grid`/`Border`; use `TextBlock` instead of `Label`/`ContentControl` for plain text; avoid wrapper `ContentControl`s in item templates.
- **Layout invalidation**: changing `Width/Height/Margin/Text` of a control invalidates measure/arrange up the tree. Animate `RenderTransform`/`Opacity` instead of size/margin. Fix sizes where possible so a change does not propagate; avoid `Auto` sizing cycles in `Grid` (`SharedSizeGroup` across many items is costly).
- **Hidden controls**: `IsVisible="False"` removes a subtree from layout/render; `Opacity="0"` does not. **(12.0+)** style-triggered animations on hidden controls pause (override with `Animation.PlaybackBehavior="Always"`).
- **Expensive effects**: `BoxShadow` (especially large blur on many items), `OpacityMask`, `Effect` (blur/drop-shadow) and clipping are costly per frame. Use sparingly on list items; prefer a flat border or one shadow on the container. Verify with the `RenderTimeGraph` overlay.
- **Cache immutable resources**: share one `SolidColorBrush`/`Geometry`/`Pen` (static field or `StaticResource`) rather than allocating in `Render`/converters. Freeze via `ToImmutable()` for `IBrush` created in code.
- **Custom controls**: draw in `Render(DrawingContext)`, call `InvalidateVisual()` only when state changes, and use `AffectsRender<T>(...)`/`AffectsMeasure<T>(...)` for styled properties instead of manual invalidation.
- **Heavy work off the UI thread**: `await Task.Run(...)` then marshal the result with `Dispatcher.UIThread.InvokeAsync`.

### Images

Decode at display size, not source size:

```csharp
await using var s = await file.OpenReadAsync();
var thumb = Bitmap.DecodeToWidth(s, 160, BitmapInterpolationMode.MediumQuality); // keeps aspect ratio
// Bitmap.DecodeToHeight(stream, height, mode) also exists
```

- A 4000x3000 photo shown in a 160px thumbnail costs ~48 MB decoded vs ~1 MB at thumbnail size. Decode thumbnails on a background thread.
- Dispose `Bitmap`s you own (`IDisposable`) when views go away; cache with a bounded LRU keyed by path+size, not an unbounded dictionary.
- `Image.Stretch`/`RenderOptions.BitmapInterpolationMode` set on the control control downscaling quality (lower quality is cheaper).
- **(12.1+)** creating a bitmap directly from pixels is several times faster.

## 12.x Rendering Facts (no code change needed)

| Version | Change |
|---|---|
| **12.0** | Large FPS improvements on complex scenes; Skia is the only desktop renderer (`Direct2D1` removed; it lacked parity) |
| **12.1** | Hit-testing reworked for containers with many visuals (up to several hundredfold in extreme cases) |
| **12.1** | Compositor render-data serialization rewritten: far fewer allocations, fewer GC pauses |
| **12.1** | Stencil buffers on by default (more HW-accelerated clipping); multiple dirty-rect clipping **off** by default (helps discrete GPUs) |
| **12.1** | X11 and Windows (render modes other than `WinUIComposition`) render at monitor refresh rate (>60 FPS); GPU/CPU use may rise vs 12.0 |
| **12.1** | Windows GPU surface creation changed when transparency not needed: lower GPU use on integrated graphics |

Source: https://avaloniaui.net/blog/release-12-1. If 12.1 regresses a specific GPU/driver, file an issue with the overlays enabled and a repro rather than pinning workarounds.

## Startup & Size

```xml
<PropertyGroup>
  <!-- Startup: precompiled native code next to IL; needs a RID; assemblies grow 2-3x -->
  <PublishReadyToRun>true</PublishReadyToRun>
  <RuntimeIdentifier>win-x64</RuntimeIdentifier>
  <SelfContained>true</SelfContained>

  <!-- Size: trimming (self-contained publish) -->
  <PublishTrimmed>true</PublishTrimmed>
</PropertyGroup>
```

| Technique | Notes |
|---|---|
| **ReadyToRun** | `-p:PublishReadyToRun=true` with `-r <RID>`. Cuts JIT time at startup and first use; tiered compilation later re-JITs hot methods. Exclude assemblies with `<PublishReadyToRunExclude Include="X.dll"/>`. Small apps see little gain |
| **Trimming** | Needs compiled bindings; reflection bindings, runtime XAML loading, `Activator`/`Type.GetType` and reflection-based serializers/DI get trimmed away. Fix trim warnings, do not suppress them |
| **Libraries** | `<IsAotCompatible>true</IsAotCompatible>` implies `IsTrimmable` + trim/AOT analyzers (net8.0+ target needed for analysis) |
| **Reflection-based library breaks** | Root it: `<TrimmerRootAssembly Include="YourAssembly" />` next to its `ProjectReference` |
| **NativeAOT** | `PublishAot` in the **executable project only**; `IsAotCompatible` in all libraries. Avalonia documents desktop NativeAOT (Windows/Linux/macOS) |

NativeAOT per Avalonia docs (https://docs.avaloniaui.net/docs/deployment/native-aot):

```xml
<PropertyGroup>
  <PublishAot>true</PublishAot>            <!-- main exe project only -->
  <IsAotCompatible>true</IsAotCompatible>  <!-- every project/library -->
  <!-- Only needed before Avalonia 12.0 (accessibility APIs): -->
  <BuiltInComInteropSupport>false</BuiltInComInteropSupport>
</PropertyGroup>
```
`dotnet publish -r win-x64 -c Release`

Caveats (Avalonia + .NET docs): no runtime loading of XAML or `Assembly.LoadFile`, no `Reflection.Emit`; dynamically created controls need trimmer settings; some third-party controls are not AOT-compatible; design-time preview is limited; `System.Linq.Expressions` run interpreted; Linux binaries only run on same-or-newer distro; all generic struct instantiations are pre-generated (size). Prefer `x:CompileBindings`/default compiled bindings, `AvaloniaResource` assets, compile-time DI registration (no reflection service location). Official `NativeWebView` **(12.0+, `Avalonia.Controls.WebView`)** is intended to be AOT-friendly; test your publish to confirm.

Trade-off: NativeAOT gives fastest startup and no JIT, but ReadyToRun + trimming is the lower-risk path for apps that use reflection-heavy libraries (reactive frameworks, serializers, plugin loading).

## Memory

- **Event handlers**: `source.Event += handler` keeps the subscriber alive for the source's lifetime. Unsubscribe in `OnDetachedFromVisualTree`/`Unloaded`, or when the VM is disposed. Static/long-lived sources (singletons, services, `Application`, `INotifyCollectionChanged` collections) are the usual culprits.
- **Lambdas and anonymous handlers** cannot be unsubscribed unless stored; use named methods or keep the delegate.
- **Weak subscriptions**: for a long-lived publisher and short-lived subscriber, use a weak-event pattern (`WeakReference` handler wrapper, or a messenger with weak references such as CommunityToolkit.Mvvm `WeakReferenceMessenger`). Verify the library API before use.
- **DataContext leaks**: a VM that holds references to views (or to `Window`) and is cached by a service keeps whole visual trees alive. Keep VMs view-agnostic; dispose/clear a view's `DataContext` when its VM is replaced; unsubscribe VMs from services in `IDisposable.Dispose`.
- **Observable subscriptions** (`Observable.Subscribe`, `GetObservable(...)`): keep the `IDisposable`, dispose when the owner goes away (`CompositeDisposable`).
- **Images/streams**: dispose bitmaps and streams; bound caches (see Images).
- **Find leaks**: `dotnet-gcdump`, take snapshot after opening/closing a view 10 times; instance count of the view/VM type should not grow.
- **Timers**: `DispatcherTimer` and `Task.Delay` loops must be stopped when the control detaches; **(12.0+)** create timers on the UI thread (they use the current dispatcher).

## Common Mistakes

- **Measuring in Debug** or with a debugger attached, then optimizing noise.
- **`ListBox`/`ItemsControl` inside `ScrollViewer` or `StackPanel`**: virtualization silently off; thousands of containers realized.
- **Using `ItemsControl` for a large list without a virtualizing `ItemsPanel`**; or still using `ItemsRepeater` in a 12.x project (retired).
- **Reflection `{Binding}` in an 11.x project** that could use compiled bindings; **(12.0+)** using `{ReflectionBinding}` everywhere "to make it compile" instead of adding `x:DataType`.
- **Loading full-resolution images for thumbnails**; not disposing bitmaps.
- **`BoxShadow`/blur on every list item**, large `OpacityMask`s, `Opacity="0"` instead of `IsVisible="False"`.
- **Animating `Width`/`Height`/`Margin`** (layout every frame) instead of `RenderTransform`/`Opacity`.
- **Calling `AttachDevTools()` in a 12.x project** or referencing `Avalonia.Diagnostics` (no 12.x package); leaving DevTools enabled in Release (guard with `#if DEBUG`).
- **Enabling `PublishTrimmed`/`PublishAot` and ignoring trim warnings**; runtime crashes appear only after publish. Test the published binary, not `dotnet run`.
- **Event subscriptions to singletons never removed**; VMs holding view references.
- **Assuming 60 FPS pacing** in 12.1 on X11/Windows: animation must be time-based; CPU/GPU use can rise on high-refresh monitors.

## Sources
- Native AOT: https://docs.avaloniaui.net/docs/deployment/native-aot
- Developer tools: https://docs.avaloniaui.net/tools/developer-tools/installation
- 12.1 rendering notes: https://avaloniaui.net/blog/release-12-1
- Breaking changes (compiled bindings, diagnostics): https://docs.avaloniaui.net/docs/avalonia12-breaking-changes
- ReadyToRun: https://learn.microsoft.com/en-us/dotnet/core/deploying/ready-to-run
- Native AOT (.NET): https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/
- `RendererDiagnostics`, `VirtualizingStackPanel`: https://github.com/AvaloniaUI/Avalonia (`src/Avalonia.Base/Rendering`, `src/Avalonia.Controls`)
