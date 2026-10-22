---
name: avalonia-interop-rendering
description: Use when going beyond Render()/DrawingContext in Avalonia — Composition API (ElementComposition, CompositionCustomVisualHandler, implicit animations), ICustomDrawOperation with direct SkiaSharp access, OpenGlControlBase, WriteableBitmap/ILockedFramebuffer pixel work, NativeControlHost embedding native HWND/NSView, hosting Avalonia in WinForms/WinUI or EmbeddableControlRoot, text-shaping setup (UseSkia + UseHarfBuzz), or choosing/configuring rendering backends (Skia, Wayland, refresh rate).
---
# Avalonia Advanced Rendering & Native Interop

Basic `Render(DrawingContext)`, brushes, geometry and animations: see `avalonia-custom-controls` and `avalonia-graphics-animation`. Version labels: see `avalonia-versions`. This skill covers what sits below/beside them.

## Which Tool?

| Need | Use |
|---|---|
| Draw shapes/text in a control | `Render(DrawingContext)` (other skills) |
| Raw SkiaSharp calls (SKCanvas, shaders, SKPath effects) | `ICustomDrawOperation` + `ISkiaSharpApiLeaseFeature` |
| Animation/redraw loop on the render thread, independent of UI thread | Composition custom visual (`CompositionCustomVisualHandler`) |
| Animate offset/opacity/scale of an existing control on the compositor | Composition implicit/explicit animations |
| Own OpenGL scene | `OpenGlControlBase` |
| Per-pixel CPU image | `WriteableBitmap` + `Lock()` |
| Real native widget (HWND, NSView, X11 window) inside the tree | `NativeControlHost` |
| Avalonia inside another UI toolkit | WinForms host, `EmbeddableControlRoot`, `Avalonia.WinUI` (12.1+) |

## Composition API

Namespace `Avalonia.Rendering.Composition`. Compositor objects live on the render thread; UI-thread properties are copied across.

```csharp
// Entry point: the element's backing CompositionVisual (null until attached to a root)
var visual = ElementComposition.GetElementVisual(control);
var compositor = visual?.Compositor;
```

Use it from `OnAttachedToVisualTree` or later — never the constructor.

### Custom visual with its own render-thread loop

```csharp
sealed class SpinnerHandler : CompositionCustomVisualHandler
{
    public static readonly object Start = new(), Stop = new();
    bool _running; TimeSpan _last; double _angle;

    public override void OnMessage(object message)          // UI thread -> render thread
    {
        if (message == Start) { _running = true; _last = CompositionNow; RegisterForNextAnimationFrameUpdate(); }
        else if (message == Stop) _running = false;
    }

    public override void OnAnimationFrameUpdate()           // once per frame while registered
    {
        if (!_running) return;
        var now = CompositionNow;
        _angle = (_angle + (now - _last).TotalSeconds * 180) % 360;
        _last = now;
        Invalidate();                                       // or Invalidate(Rect) for precise dirty rects
        RegisterForNextAnimationFrameUpdate();              // must re-register every frame
    }

    public override void OnRender(ImmediateDrawingContext context)
    {
        // Draw from state computed in OnAnimationFrameUpdate (e.g. _angle -> position of a marker)
        var x = EffectiveSize.X / 2 + Math.Cos(_angle * Math.PI / 180) * 30;
        var y = EffectiveSize.Y / 2 + Math.Sin(_angle * Math.PI / 180) * 30;
        context.DrawEllipse(Brushes.DodgerBlue, null, new Point(x, y), 8, 8);   // as in ControlCatalog sample
    }
}

// In the control:
protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
{
    base.OnAttachedToVisualTree(e);
    var compositor = ElementComposition.GetElementVisual(this)?.Compositor;
    if (compositor is null) return;
    _custom = compositor.CreateCustomVisual(new SpinnerHandler());
    ElementComposition.SetElementChildVisual(this, _custom);
    _custom.Size = new Vector(Bounds.Width, Bounds.Height);   // keep in sync on size change
    _custom.SendHandlerMessage(SpinnerHandler.Start);
}
```

Handler members (all verified): `OnMessage`, `OnAnimationFrameUpdate`, `OnRender`, `GetRenderBounds`, `EffectiveSize`, `CompositionNow`, `Invalidate()`, `Invalidate(Rect)`, `RegisterForNextAnimationFrameUpdate()`, `RenderClipContains`, `RenderClipIntersectes` (sic).

### Implicit animations (animate when a property changes)

```csharp
var compositor = ElementComposition.GetElementVisual(this)!.Compositor;
var offset = compositor.CreateVector3KeyFrameAnimation();
offset.Target = "Offset";
offset.InsertExpressionKeyFrame(1.0f, "this.FinalValue");
offset.Duration = TimeSpan.FromMilliseconds(400);

var implicitAnims = compositor.CreateImplicitAnimationCollection();
implicitAnims["Offset"] = offset;                          // sample wraps animations in CreateAnimationGroup()
ElementComposition.GetElementVisual(childControl)!.ImplicitAnimations = implicitAnims;
```

Explicit: `visual.StartAnimation("Opacity", anim)`, `StopAnimation`, `StartAnimationGroup`. `CompositionVisual` properties: `Offset`, `Opacity`, `Scale` (`Vector3D`), `RotationAngle`, `CenterPoint`, `Size` (`Vector`), `Visible`, `ClipToBounds`, `OpacityMask`, `Orientation`. **(12.0+)** `Translation` (`Vector3D`) — offset applied on top of layout `Offset`, ideal for transient motion without fighting layout.

## ICustomDrawOperation + Skia

Draw with `context.Custom(op)` from `Render(DrawingContext)`. `ICustomDrawOperation : IDisposable, IEquatable<ICustomDrawOperation>` — members `Bounds`, `HitTest(Point)`, `Render(ImmediateDrawingContext)`.

```csharp
using Avalonia.Platform; using Avalonia.Rendering.SceneGraph; using Avalonia.Skia; using SkiaSharp;

public override void Render(DrawingContext context)
    => context.Custom(new SkOp(new Rect(Bounds.Size), _phase));

sealed class SkOp(Rect bounds, float phase) : ICustomDrawOperation
{
    public Rect Bounds { get; } = bounds;
    public bool HitTest(Point p) => Bounds.Contains(p);
    public bool Equals(ICustomDrawOperation? other) => other is SkOp o && o.Bounds == Bounds && o.phase == phase;
    public void Dispose() { }

    public void Render(ImmediateDrawingContext context)
    {
        var feature = context.TryGetFeature<ISkiaSharpApiLeaseFeature>();
        if (feature is null) return;                        // non-Skia backend: draw a fallback
        using var lease = feature.Lease();                  // always dispose
        var canvas = lease.SkCanvas;                        // also: GrContext, SkSurface, CurrentOpacity
        canvas.Save();
        using var paint = new SKPaint { Color = SKColors.OrangeRed, IsAntialias = true };
        canvas.DrawCircle((float)Bounds.Width / 2, (float)Bounds.Height / 2, 30 + phase, paint);
        canvas.Restore();
    }
}
```

- Types are `[Unstable]` — pin the Avalonia version and expect changes.
- The lease canvas inherits Avalonia's current transform/clip; `Save()/Restore()` around your work.
- `Equals` drives dirty-rect/scene diffing: return `false` (or compare real state) when content changed, else the op may be skipped.
- Operations run on the **render thread**: capture immutable data in the op; never touch controls or `AvaloniaProperty` values inside `Render`.
- `lease.TryLeasePlatformGraphicsApi()` gives access to the native GPU context for GL/Vulkan interop (advanced).
- Package: `Avalonia.Skia` (+ SkiaSharp via Avalonia's dependency; match its SkiaSharp version).

## OpenGL (`OpenGlControlBase`)

Namespace `Avalonia.OpenGL.Controls`.

```csharp
public class GlView : OpenGlControlBase
{
    protected override void OnOpenGlInit(GlInterface gl)    { /* create shaders, buffers */ }
    protected override void OnOpenGlDeinit(GlInterface gl)  { /* delete GL objects */ }
    protected override void OnOpenGlLost()                  { /* context lost: drop cached handles */ }
    protected override void OnOpenGlRender(GlInterface gl, int fb)
    {
        // fb = framebuffer to render into; issue GL calls through gl, then:
        RequestNextFrameRendering();                        // keep animating (InvalidateVisual is obsolete here)
    }
}
```

- `protected GlVersion GlVersion { get; }` reports the negotiated context.
- Rendering happens on the render/composition path, not necessarily the UI thread — no UI access in the overrides.
- For GL function loading, bindings like Silk.NET are commonly wired from `gl.GetProcAddress` (check the binding's Avalonia sample).
- **(12.1+)** X11 supports OpenGL *desktop* profiles when rendering through EGL, and the Wayland backend does too; stencil buffers on by default (more HW-accelerated clipping).
- Deeper GPU interop (external memory, shared textures) lives under `Avalonia.OpenGL`/`ISkiaSharpApiLease.TryLeasePlatformGraphicsApi()` — unstable; read the source samples.

## WriteableBitmap / ILockedFramebuffer

```csharp
var bmp = new WriteableBitmap(new PixelSize(256, 256), new Vector(96, 96),
                              PixelFormat.Bgra8888, AlphaFormat.Premul);
using (var fb = bmp.Lock())                                 // ILockedFramebuffer
{
    // fb.Address (IntPtr), fb.RowBytes (stride), fb.Size, fb.Format, fb.AlphaFormat, fb.Dpi
    unsafe { var p = (uint*)fb.Address; /* respect RowBytes, not Width*4 */ }
}
image.Source = bmp;                                         // re-Lock + write, then image.InvalidateVisual()
```

- From existing memory: `new WriteableBitmap(PixelFormat format, AlphaFormat alphaFormat, IntPtr data, PixelSize size, Vector dpi, int stride)` (data is copied).
- **(12.0+)** `ILockedFramebuffer.AlphaFormat` exists; custom `new LockedFramebuffer(...)` requires an `AlphaFormat` argument. `Bitmap.CopyPixels(...)` no longer takes an `AlphaFormat` parameter — the format comes from the source framebuffer.
- **(12.1+)** Creating bitmaps directly from pixel data is several times faster (no API change).
- `Format`/`AlphaFormat` of Skia-backed bitmaps is typically `Bgra8888`/`Premul` — write premultiplied alpha.

## NativeControlHost (embed native widgets)

`NativeControlHost : Control` — subclass and return an `IPlatformHandle` (`Handle` `IntPtr`, `HandleDescriptor` `string?`).

```csharp
public class NativeHost : NativeControlHost
{
    protected override IPlatformHandle CreateNativeControlCore(IPlatformHandle parent)
    {
        // Create the native widget parented to parent.Handle, then return an IPlatformHandle
        // wrapping it (Handle = HWND / NSView pointer / X11 window id, HandleDescriptor = its kind).
        // Implement IPlatformHandle yourself (or use PlatformHandle if present in your version).
        return base.CreateNativeControlCore(parent);        // placeholder: replace with your handle
    }
    protected override void DestroyNativeControlCore(IPlatformHandle control) { /* destroy native object */ }
}
```

- `TryUpdateNativeControlPosition()` forces re-layout of the native child if it drifts.
- Native widgets are **airspace-bound**: they paint above Avalonia content; Avalonia controls (popups, adorners) cannot overlap them. Use a separate top-level (e.g. a `Window`/overlay) for floating UI.
- Rendering of the hosted widget is the OS's job — no Avalonia clipping/transforms/opacity apply.
- Prefer `Avalonia.Controls.WebView` (`NativeWebView`) over hand-rolled web embedding (see `avalonia-versions`).

## Hosting Avalonia Elsewhere

| Host | How |
|---|---|
| WinForms | Package `Avalonia.Win32.Interoperability`; `WinFormsAvaloniaControlHost` (WinForms `Control`, property `Content` = Avalonia `Control`) |
| WinUI 3 **(12.1+)** | Package `Avalonia.WinUI` (net10.0-windows10.0.19041, depends on Windows App SDK) |
| Any custom host | `EmbeddableControlRoot` (`Avalonia.Controls.Embedding`) |

```csharp
// WinForms form: after Avalonia has been initialised once for the process
var host = new WinFormsAvaloniaControlHost { Content = new MyAvaloniaView(), Dock = DockStyle.Fill };
Controls.Add(host);
```

- **(12.0+)** `WinFormsAvaloniaMessageFilter` (`IMessageFilter`) routes keyboard messages WinForms would otherwise swallow to Avalonia windows; `WinFormsAvaloniaControlHost` also implements `IMessageFilter`. Register it via the standard WinForms `Application.AddMessageFilter` if keys/tab/shortcuts misbehave in hosted views.
- **(12.0+)** `EmbeddableControlRoot` owns rendering: `root.Prepare()`, `root.StartRendering()`, `root.StopRendering()`, `Dispose()`. `TopLevel.StartRendering/StopRendering` were removed in 12.
- In 12.x do not cast a visual root to `TopLevel`: use `TopLevel.GetTopLevel(visual)`, or `GetPresentationSource()` → `RootVisual` for non-TopLevel hosts (`VisualExtensions.GetVisualRoot` removed).
- WPF interop: no WPF host type is documented for 12.x in the API reference; verify against the package before promising it.

## Text Shaping & Rendering Backends

```csharp
// 12.x with explicit Skia: shaping is configured separately
AppBuilder.Configure<App>().UsePlatformDetect();            // handles Skia + HarfBuzz for you
// or
AppBuilder.Configure<App>().UseSkia().UseHarfBuzz();        // (12.0+) needs Avalonia.HarfBuzz package
```

- Missing `UseHarfBuzz()` → `InvalidOperationException: No text shaping system configured`.
- **(12.0+)** `AppBuilder.UseTextShapingSubsystem(Action initializer, string name)` registers a custom shaper; `UseHarfBuzz()` is the standard one.
- **Skia is the only renderer in 12.** `Avalonia.Direct2D1`/`UseDirect2D1()` is **(11.x)** only → `UseSkia()`.
- Custom backend authors (12): `IRenderTarget.CreateDrawingContext` takes `RenderTargetSceneInfo`; `ISkiaGpu` is internal; `IRenderTarget2`/`ISkiaGpuRenderTarget2` merged into their base interfaces.
- **(12.1+, experimental)** Native Wayland: package `Avalonia.Wayland`, `.UseWayland()` or `.UsePlatformDetect().UseWaylandWithFallback()` (keeps the prior backend when no compositor). Renders via EGL (optional dmabuf). `UsePlatformDetect()` alone does **not** pick Wayland. Options: register `WaylandPlatformOptions` in `AvaloniaLocator`.
- **(12.1+)** X11 and Windows (non-`WinUIComposition` modes; `WinUIComposition` remains Windows default) render at monitor refresh rate instead of 60 FPS. Time-based animation stays correct; per-frame work (custom handlers, GL) costs more — drive by `CompositionNow`/elapsed time, not frame counts.
- **(12.1+)** Multiple dirty-rect clipping off by default.

## Common Mistakes

- Calling `ElementComposition.GetElementVisual` before attach (returns `null`) or caching a visual across compositors/windows.
- Forgetting `RegisterForNextAnimationFrameUpdate()` every frame — the loop silently stops.
- Setting a custom visual's `Size` once and never updating it on resize (nothing draws / clips wrong).
- Touching UI-thread state from `CompositionCustomVisualHandler`/`ICustomDrawOperation.Render`/`OnOpenGlRender` — copy data in or use `SendHandlerMessage`.
- Not disposing the Skia lease, or assuming Skia is present (`TryGetFeature` can return `null`; headless/other backends).
- `ICustomDrawOperation.Equals` always `true` → stale frames; always `false` → needless redraws.
- Using `InvalidateVisual()` on `OpenGlControlBase` (obsolete) instead of `RequestNextFrameRendering()`.
- Writing pixels with `Width * 4` instead of `fb.RowBytes`; writing straight alpha into a premultiplied buffer.
- Overlapping Avalonia UI on a `NativeControlHost` and expecting z-order to work.
- Using `TopLevel.StartRendering` or `GetVisualRoot` in 12.x; `UseSkia()` without `UseHarfBuzz()`; `UseDirect2D1()` in 12.x.
- Assuming `UsePlatformDetect()` selects Wayland in 12.1.

## Sources
- API reference: https://docs.avaloniaui.net/api/ (e.g. `/api/avalonia/rendering/composition/compositionvisual.md`)
- Breaking changes: https://docs.avaloniaui.net/docs/avalonia12-breaking-changes
- 12.1 notes: https://avaloniaui.net/blog/release-12-1
- Source: https://github.com/AvaloniaUI/Avalonia (`src/Avalonia.Base/Rendering/Composition`, `src/Skia/Avalonia.Skia/ISkiaSharpApiLeaseFeature.cs`, `src/Avalonia.OpenGL/Controls/OpenGlControlBase.cs`, `samples/ControlCatalog/Pages/CompositionPage.axaml.cs`)
- Packages: https://www.nuget.org/packages/Avalonia.Win32.Interoperability · https://www.nuget.org/packages/Avalonia.WinUI
