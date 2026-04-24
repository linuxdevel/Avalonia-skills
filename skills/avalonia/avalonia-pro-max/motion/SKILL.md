---
name: avalonia-pro-max/motion
description: Use when adding animation, hover/press feedback, page transitions, list-item entrance, or honoring reduced-motion in an Avalonia app. Covers Transitions, Animation, KeyFrame, easing, IterationCount, and shared-element patterns.
---

# Motion in Avalonia

Two complementary systems:

| System | Purpose | When |
|---|---|---|
| `Transitions` | Animate property changes automatically when value changes | Hover/press, layout, color, size |
| `Animation` (`Style.Animations`) | Time-based keyframed animation | Skeleton shimmer, indeterminate spinner, attention pulse |
| `PageTransition` (FluentAvalonia / TabControl) | Whole-view transitions | Frame navigation, tab swap |

Target durations:

| Type | Duration | Easing |
|---|---|---|
| Micro (hover, press) | 100–150 ms | `LinearEasing` or `QuadraticEaseOut` |
| Standard (panel slide, fade) | 200–300 ms | `CubicEaseOut` |
| Large (page transition) | 300–400 ms | `ExponentialEaseOut` |
| Exit | ~70% of enter | Same family |

---

## Transitions on a Style

```xml
<Style Selector="Border.card">
  <Setter Property="Background" Value="{DynamicResource SurfaceElevatedBrush}"/>
  <Setter Property="Transitions">
    <Transitions>
      <BrushTransition Property="Background" Duration="0:0:0.2"/>
      <DoubleTransition Property="Opacity" Duration="0:0:0.2"/>
      <TransformOperationsTransition Property="RenderTransform"
                                     Duration="0:0:0.15"
                                     Easing="CubicEaseOut"/>
      <BoxShadowsTransition Property="BoxShadow" Duration="0:0:0.2"/>
    </Transitions>
  </Setter>
  <Setter Property="RenderTransform" Value="none"/>
</Style>

<Style Selector="Border.card:pointerover">
  <Setter Property="BoxShadow" Value="{StaticResource ShadowMd}"/>
  <Setter Property="RenderTransform" Value="translateY(-2px)"/>
</Style>
```

Available `*Transition` types: `DoubleTransition`, `BrushTransition`, `ColorTransition`, `ThicknessTransition`, `CornerRadiusTransition`, `TransformOperationsTransition`, `BoxShadowsTransition`, `IntegerTransition`, `SizeTransition`, `PointTransition`, `VectorTransition`.

**Rule:** Animate only `Opacity`, `RenderTransform`, `Background`/`Foreground`/`BorderBrush`, and `BoxShadow`. Avoid `Width`/`Height`/`Margin` — these trigger layout passes and jank.

---

## Built-in Easings

`LinearEasing`, `BackEaseIn/Out/InOut`, `BounceEaseIn/Out/InOut`, `CircularEaseIn/Out/InOut`, `CubicEaseIn/Out/InOut`, `ElasticEaseIn/Out/InOut`, `ExponentialEaseIn/Out/InOut`, `QuadraticEaseIn/Out/InOut`, `QuarticEaseIn/Out/InOut`, `QuinticEaseIn/Out/InOut`, `SineEaseIn/Out/InOut`.

Defaults if unspecified: linear. Always set an easing for UI feel.

Recommended:
- Enter / appear → `CubicEaseOut` or `ExponentialEaseOut`
- Exit / disappear → `CubicEaseIn`
- Spring-y emphasis → `BackEaseOut` (subtle, ≤300 ms)

---

## Press Feedback (Scale-on-Press)

```xml
<Style Selector="Button">
  <Setter Property="RenderTransform" Value="none"/>
  <Setter Property="Transitions">
    <Transitions>
      <TransformOperationsTransition Property="RenderTransform"
                                     Duration="0:0:0.08"
                                     Easing="QuadraticEaseOut"/>
    </Transitions>
  </Setter>
</Style>
<Style Selector="Button:pressed">
  <Setter Property="RenderTransform" Value="scale(0.97)"/>
</Style>
```

`RenderTransformOrigin="0.5,0.5"` is the default — leave it.

---

## Keyframe Animation

```xml
<Style Selector="Border.pulse">
  <Style.Animations>
    <Animation Duration="0:0:1.6" IterationCount="Infinite">
      <KeyFrame Cue="0%">
        <Setter Property="Opacity" Value="1"/>
        <Setter Property="RenderTransform" Value="scale(1)"/>
      </KeyFrame>
      <KeyFrame Cue="50%">
        <Setter Property="Opacity" Value="0.6"/>
        <Setter Property="RenderTransform" Value="scale(1.06)"/>
      </KeyFrame>
      <KeyFrame Cue="100%">
        <Setter Property="Opacity" Value="1"/>
        <Setter Property="RenderTransform" Value="scale(1)"/>
      </KeyFrame>
    </Animation>
  </Style.Animations>
</Style>
```

Spinner:
```xml
<Style Selector="PathIcon.spin">
  <Style.Animations>
    <Animation Duration="0:0:1" IterationCount="Infinite" Easing="LinearEasing">
      <KeyFrame Cue="0%"><Setter Property="RenderTransform" Value="rotate(0deg)"/></KeyFrame>
      <KeyFrame Cue="100%"><Setter Property="RenderTransform" Value="rotate(360deg)"/></KeyFrame>
    </Animation>
  </Style.Animations>
</Style>
```

---

## Page / View Transitions

### TabControl

```xml
<TabControl>
  <TabControl.PageTransition>
    <CrossFade Duration="0:0:0.2"/>
  </TabControl.PageTransition>
  <TabItem Header="Tab 1">…</TabItem>
</TabControl>
```

Built-in transitions: `CrossFade`, `PageSlide` (with `Direction` and `Orientation`), `CompositePageTransition`.

```xml
<PageSlide Duration="0:0:0.3" Orientation="Horizontal" SlideOutEasing="CubicEaseIn" SlideInEasing="CubicEaseOut"/>
```

### TransitioningContentControl (for `ContentControl`-based view-switching)

```xml
<TransitioningContentControl Content="{Binding CurrentView}">
  <TransitioningContentControl.PageTransition>
    <CompositePageTransition>
      <CrossFade Duration="0:0:0.2"/>
      <PageSlide Duration="0:0:0.2" Orientation="Vertical"/>
    </CompositePageTransition>
  </TransitioningContentControl.PageTransition>
</TransitioningContentControl>
```

### FluentAvalonia Frame

```csharp
ContentFrame.Navigate(typeof(DashboardPage),
    null,
    new SlideNavigationTransitionInfo
    {
        Effect = SlideNavigationTransitionEffect.FromRight
    });
```

---

## List Item Entrance (Stagger)

Avalonia doesn't have built-in list-item stagger. Two approaches:

**1. Animate on `ItemContainer` load**
```xml
<ListBox ItemsSource="{Binding Items}">
  <ListBox.ItemContainerTheme>
    <ControlTheme TargetType="ListBoxItem"
                  BasedOn="{StaticResource {x:Type ListBoxItem}}">
      <Style.Animations>
        <Animation Duration="0:0:0.3" Easing="CubicEaseOut">
          <KeyFrame Cue="0%">
            <Setter Property="Opacity" Value="0"/>
            <Setter Property="RenderTransform" Value="translateY(8px)"/>
          </KeyFrame>
          <KeyFrame Cue="100%">
            <Setter Property="Opacity" Value="1"/>
            <Setter Property="RenderTransform" Value="none"/>
          </KeyFrame>
        </Animation>
      </Style.Animations>
    </ControlTheme>
  </ListBox.ItemContainerTheme>
</ListBox>
```

**2. Manual stagger** — drive `Animation.Delay` per item from the ViewModel using indexed offsets.

---

## Reduced Motion

Avalonia exposes the OS preference via `RendererDiagnostics`-ish APIs and platform-specific settings. Pragmatic approach: expose a `ReducedMotion` setting in your app and bind transition durations to it.

```csharp
public class MotionSettings : INotifyPropertyChanged
{
    public bool ReducedMotion { get; set; }
    public TimeSpan Standard => ReducedMotion ? TimeSpan.Zero : TimeSpan.FromMilliseconds(200);
    public TimeSpan Fast     => ReducedMotion ? TimeSpan.Zero : TimeSpan.FromMilliseconds(100);
}
```

Bind in XAML:
```xml
<DoubleTransition Property="Opacity"
                  Duration="{Binding Source={x:Static app:MotionSettings.Instance}, Path=Standard}"/>
```

Or, in code-behind, swap the `Transitions` collection at app start when reduced-motion is enabled.

Detect Windows preference:
```csharp
SystemParameters.ClientAreaAnimation == false  // (P/Invoke; check Avalonia API for Linux/macOS)
```

---

## Modal / Sheet Motion

Sheets should slide+fade in from their trigger direction:

```xml
<Style Selector="Border.sheet">
  <Setter Property="Opacity" Value="0"/>
  <Setter Property="RenderTransform" Value="translateY(20px)"/>
  <Setter Property="Transitions">
    <Transitions>
      <DoubleTransition Property="Opacity" Duration="0:0:0.25" Easing="CubicEaseOut"/>
      <TransformOperationsTransition Property="RenderTransform"
                                     Duration="0:0:0.25"
                                     Easing="CubicEaseOut"/>
    </Transitions>
  </Setter>
</Style>
<Style Selector="Border.sheet.open">
  <Setter Property="Opacity" Value="1"/>
  <Setter Property="RenderTransform" Value="none"/>
</Style>
```

Toggle `Classes.open="{Binding IsOpen}"`.

---

## Shared Element-Style Transitions

True shared-element transitions are not built-in. Use:

1. `RenderTransform` interpolation on both source and destination — animate scale/translation between known positions.
2. `LayoutTransformControl` for size-based transitions without re-layout cost.
3. For "magic move" lists, consider `ItemsRepeater` + custom container animation.

---

## Performance Rules

- Animate **transform + opacity + brush** only.
- Never animate `Width`, `Height`, `Margin`, `Padding`, `Grid.Column*`.
- Cap concurrent animations per view: 2–3 max for most screens.
- For 60fps, total animation cost per frame < 16 ms. Profile with `--renderer skia --fps`.
- `IterationCount="Infinite"` only on small elements (spinner, badge dot).
- Disable expensive transitions on battery (Mobile / WASM).

---

## Common Mistakes

- **Animating `Width`/`Height` for "smooth resize"** — use `LayoutTransformControl` + `ScaleTransform` instead.
- **No easing** (defaults to linear) — UI feels mechanical.
- **300 ms fade for press feedback** — too slow; press should react ≤100 ms.
- **Same enter and exit duration** — exit should be ~70%.
- **Forgetting `RenderTransform="none"` initial value** — first transition snaps from null.
- **Looping decorative animation that pulls eye from content** — limits cognition.
- **No reduced-motion path** — accessibility regression for vestibular-disorder users.
- **Animating during virtualization scroll** — every recycled container re-runs entrance animation. Disable on virtualized lists or mark as one-shot.
