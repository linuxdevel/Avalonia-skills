---
name: avalonia-graphics-animation
description: Use when working with Avalonia brushes, transforms, geometry, clipping, animations, transitions, or bitmap effects. Covers SolidColorBrush, LinearGradientBrush, RadialGradientBrush, ConicGradientBrush, ImageBrush, VisualBrush, RenderTransform, shapes, Path geometry, clipping, BoxShadow, keyframe Animation class, property Transitions, and page transitions.
---
# Avalonia Graphics & Animation

## Overview
Avalonia renders via Skia (default) or Impeller. All visual effects are cross-platform. Animations use keyframe `Animation` class or property `Transitions`.

## Brushes

| Brush | XAML | Use |
|---|---|---|
| SolidColorBrush | `"#FF5722"` or `"Red"` | Solid fill/stroke |
| LinearGradientBrush | `<LinearGradientBrush>` | Linear gradient |
| RadialGradientBrush | `<RadialGradientBrush>` | Radial gradient |
| ConicGradientBrush | `<ConicGradientBrush>` | Conic gradient |
| ImageBrush | `<ImageBrush>` | Tiled/stretched image fill |
| VisualBrush | `<VisualBrush>` | Render control as brush |

```xml
<Rectangle Width="200" Height="100">
    <Rectangle.Fill>
        <LinearGradientBrush StartPoint="0%,0%" EndPoint="100%,100%">
            <GradientStop Color="#FF5722" Offset="0"/>
            <GradientStop Color="#9C27B0" Offset="1"/>
        </LinearGradientBrush>
    </Rectangle.Fill>
</Rectangle>
```

```xml
<Rectangle Width="200" Height="200">
    <Rectangle.Fill>
        <RadialGradientBrush GradientOrigin="50%,50%" Radius="50%">
            <GradientStop Color="Yellow" Offset="0"/>
            <GradientStop Color="Red" Offset="1"/>
        </RadialGradientBrush>
    </Rectangle.Fill>
</Rectangle>
```

Opacity shorthand: `Opacity="0.5"` on any control (applies to whole subtree).

## Transforms

```xml
<Rectangle RenderTransform="rotate(45)" Width="100" Height="100"/>
```

```xml
<Rectangle>
    <Rectangle.RenderTransform>
        <TransformGroup>
            <RotateTransform Angle="45"/>
            <ScaleTransform ScaleX="1.5" ScaleY="1.5"/>
            <TranslateTransform X="20" Y="10"/>
            <SkewTransform AngleX="10"/>
        </TransformGroup>
    </Rectangle.RenderTransform>
</Rectangle>
```

`RenderTransformOrigin="0.5,0.5"` — pivot point (0–1 relative to control bounds).

String shorthand syntax: `rotate(deg)`, `scale(x,y)`, `translate(x,y)`, `skew(x,y)`, `matrix(a,b,c,d,e,f)`.

## Geometry / Shapes

Shapes (draw themselves): `Rectangle`, `Ellipse`, `Line`, `Polyline`, `Polygon`, `Path`

```xml
<Path Fill="CornflowerBlue" Stroke="Navy" StrokeThickness="2"
      Data="M 50,0 L 100,100 L 0,100 Z"/>
<Ellipse Fill="Red" Width="80" Height="60"/>
<Line StartPoint="0,0" EndPoint="100,100" Stroke="Black" StrokeThickness="2"/>
```

Geometry (reusable shape data): `EllipseGeometry`, `RectangleGeometry`, `PathGeometry`, `CombinedGeometry`, `GeometryGroup`

```xml
<Path>
    <Path.Data>
        <CombinedGeometry GeometryCombineMode="Xor">
            <CombinedGeometry.Geometry1>
                <EllipseGeometry Center="50,50" RadiusX="50" RadiusY="50"/>
            </CombinedGeometry.Geometry1>
            <CombinedGeometry.Geometry2>
                <EllipseGeometry Center="80,50" RadiusX="50" RadiusY="50"/>
            </CombinedGeometry.Geometry2>
        </CombinedGeometry>
    </Path.Data>
</Path>
```

## Clipping

```xml
<Border ClipToBounds="True" CornerRadius="8">
    <Image Source="..." Stretch="UniformToFill"/>
</Border>
```

Custom clip geometry:
```xml
<Rectangle Width="100" Height="100" Fill="Red">
    <Rectangle.Clip>
        <EllipseGeometry Center="50,50" RadiusX="50" RadiusY="50"/>
    </Rectangle.Clip>
</Rectangle>
```

## Shadows

`BoxShadow` only on `Border`:
```xml
<Border BoxShadow="0 4 8 0 #40000000" CornerRadius="8" Background="White">
    <TextBlock Text="Shadowed"/>
</Border>
```

Multiple shadows:
```xml
<Border BoxShadow="0 2 4 0 #20000000, 0 8 16 0 #10000000" CornerRadius="8"/>
```

Format: `offsetX offsetY blur spread color [inset]`

## Animations (Keyframe)

```xml
<Window.Styles>
    <Style Selector="Button.spin">
        <Style.Animations>
            <Animation Duration="0:0:1" IterationCount="INFINITE" PlaybackDirection="Normal">
                <KeyFrame Cue="0%">
                    <Setter Property="RenderTransform" Value="rotate(0)"/>
                </KeyFrame>
                <KeyFrame Cue="100%">
                    <Setter Property="RenderTransform" Value="rotate(360)"/>
                </KeyFrame>
            </Animation>
        </Style.Animations>
    </Style>
</Window.Styles>
```

Animation with easing and delay:
```xml
<Animation Duration="0:0:0.5" Delay="0:0:0.1" FillMode="Forward" Easing="CubicEaseOut">
    <KeyFrame Cue="0%">
        <Setter Property="Opacity" Value="0"/>
        <Setter Property="RenderTransform" Value="translateY(-20px)"/>
    </KeyFrame>
    <KeyFrame Cue="100%">
        <Setter Property="Opacity" Value="1"/>
        <Setter Property="RenderTransform" Value="translateY(0)"/>
    </KeyFrame>
</Animation>
```

| Property | Values |
|---|---|
| `Duration` | `h:m:s` format |
| `Delay` | `h:m:s` format |
| `IterationCount` | number or `INFINITE` |
| `PlaybackDirection` | `Normal` / `Reverse` / `Alternate` / `AlternateReverse` |
| `FillMode` | `None` / `Forward` / `Backward` / `Both` |
| `Easing` | `LinearEasing`, `CubicEaseIn/Out/InOut`, `BounceEaseOut`, etc. |

Trigger animation from code:
```csharp
var animation = new Animation
{
    Duration = TimeSpan.FromSeconds(0.3),
    FillMode = FillMode.Forward,
    Children =
    {
        new KeyFrame { Cue = Cue.Parse("0%"), Setters = { new Setter(OpacityProperty, 0.0) } },
        new KeyFrame { Cue = Cue.Parse("100%"), Setters = { new Setter(OpacityProperty, 1.0) } }
    }
};
await animation.RunAsync(myControl);
```

## Transitions (Property Change)

Smooth property changes on value set:
```xml
<Border Background="Blue">
    <Border.Transitions>
        <Transitions>
            <BrushTransition Property="Background" Duration="0:0:0.3"/>
            <DoubleTransition Property="Opacity" Duration="0:0:0.2" Easing="CubicEaseOut"/>
            <TransformOperationsTransition Property="RenderTransform" Duration="0:0:0.3"/>
        </Transitions>
    </Border.Transitions>
</Border>
```

| Transition Type | Property Types |
|---|---|
| `BrushTransition` | `IBrush` |
| `ColorTransition` | `Color` |
| `DoubleTransition` | `double` |
| `FloatTransition` | `float` |
| `IntegerTransition` | `int` |
| `PointTransition` | `Point` |
| `SizeTransition` | `Size` |
| `ThicknessTransition` | `Thickness` |
| `TransformOperationsTransition` | `ITransform` / string transform |
| `VectorTransition` | `Vector` |

In styles (apply to all matching controls):
```xml
<Style Selector="Button">
    <Setter Property="Transitions">
        <Transitions>
            <DoubleTransition Property="Opacity" Duration="0:0:0.15"/>
        </Transitions>
    </Setter>
</Style>
```

## Page Transitions (Carousel/Navigation)

```xml
<Carousel.PageTransition>
    <PageSlide Duration="0:0:0.35" Orientation="Horizontal"/>
</Carousel.PageTransition>
```

```xml
<Carousel.PageTransition>
    <CrossFade Duration="0:0:0.25"/>
</Carousel.PageTransition>
```

Composite:
```xml
<Carousel.PageTransition>
    <CompositePageTransition>
        <PageSlide Duration="0:0:0.3" Orientation="Horizontal"/>
        <CrossFade Duration="0:0:0.3"/>
    </CompositePageTransition>
</Carousel.PageTransition>
```

## Common Mistakes

- **Transitions only fire on property changes** — not on initial value set; hardcoded initial value + Transition won't animate on load
- **`RenderTransform="rotate(45)"` string syntax** — no spaces inside parentheses; `rotate( 45 )` fails
- **`BoxShadow` only on `Border`** — not on arbitrary controls like `Grid` or `StackPanel`
- **Animation `Cue` must be percent string** — `"0%"` and `"100%"`, not `0` or `1.0`
- **`FillMode="None"` (default) reverts after animation** — use `FillMode="Forward"` to hold end state
- **`IterationCount="INFINITE"` is all caps** — `Infinite` or `infinite` won't parse
