---
name: avalonia-custom-controls
description: Use when creating custom UserControls, TemplatedControls, basic drawing controls, custom panels, control libraries, attached properties, or custom flyouts in Avalonia.
---

# Avalonia Custom Controls

## Overview

Three control types: UserControl (XAML composition, app-specific), TemplatedControl (lookless, restyled per theme), Control (custom drawing with Render override). Choose by reusability needs.

## Choosing a Control Type

| Type | Inherit from | Use when |
|---|---|---|
| UserControl | `UserControl` | App-specific view/page, composed of existing controls |
| TemplatedControl | `TemplatedControl` | Reusable, restyled control for libraries/themes |
| Basic control | `Control` | Custom drawing (charts, gauges, games) |
| Panel | `Panel` | Custom layout algorithm |

## UserControl

```xml
<!-- MyCard.axaml -->
<UserControl xmlns="https://github.com/avaloniaui"
             x:Class="MyApp.Controls.MyCard">
    <Border CornerRadius="8" Padding="16">
        <ContentPresenter Content="{Binding}"/>
    </Border>
</UserControl>
```

```csharp
// MyCard.axaml.cs
public partial class MyCard : UserControl
{
    public MyCard() => InitializeComponent();
}
```

## TemplatedControl

```csharp
public class RatingControl : TemplatedControl
{
    public static readonly StyledProperty<int> ValueProperty =
        AvaloniaProperty.Register<RatingControl, int>(nameof(Value), defaultValue: 0);

    public int Value
    {
        get => GetValue(ValueProperty);
        set => SetValue(ValueProperty, value);
    }
}
```

Default template in `Themes/Generic.axaml`:

```xml
<ControlTheme x:Key="{x:Type local:RatingControl}" TargetType="local:RatingControl">
    <Setter Property="Template">
        <ControlTemplate>
            <StackPanel Orientation="Horizontal">
                <!-- template content -->
            </StackPanel>
        </ControlTemplate>
    </Setter>
</ControlTheme>
```

## StyledProperty vs DirectProperty

| | StyledProperty | DirectProperty |
|---|---|---|
| Styling support | Yes | No |
| Binding | All priorities | LocalValue only |
| Value inheritance | Yes | No |
| Per-instance storage | Prioritized list | Field |
| Use when | Needs styling, most cases | High-perf, won't be styled |

```csharp
// StyledProperty
public static readonly StyledProperty<IBrush?> FillProperty =
    AvaloniaProperty.Register<MyControl, IBrush?>(nameof(Fill));

// DirectProperty
public static readonly DirectProperty<MyControl, int> CountProperty =
    AvaloniaProperty.RegisterDirect<MyControl, int>(
        nameof(Count), o => o.Count, (o, v) => o.Count = v);
private int _count;
public int Count
{
    get => _count;
    set => SetAndRaise(CountProperty, ref _count, value);
}
```

## AttachedProperty

```csharp
public static readonly AttachedProperty<bool> IsHighlightedProperty =
    AvaloniaProperty.RegisterAttached<MyHelper, Control, bool>("IsHighlighted");

public static bool GetIsHighlighted(Control element) => element.GetValue(IsHighlightedProperty);
public static void SetIsHighlighted(Control element, bool value) => element.SetValue(IsHighlightedProperty, value);
```

Usage: `<Button local:MyHelper.IsHighlighted="True"/>`

## Custom Drawing (Render Override)

```csharp
public class CircleControl : Control
{
    public override void Render(DrawingContext context)
    {
        var brush = new SolidColorBrush(Colors.CornflowerBlue);
        var pen = new Pen(Brushes.Navy, 2);
        context.DrawEllipse(brush, pen,
            new Point(Bounds.Width / 2, Bounds.Height / 2),
            Bounds.Width / 2 - 2, Bounds.Height / 2 - 2);
    }

    protected override Size MeasureOverride(Size availableSize)
        => new Size(100, 100); // desired size
}
```

Invalidate drawing: `InvalidateVisual()`

## Custom Panel

```csharp
public class CircularPanel : Panel
{
    protected override Size MeasureOverride(Size availableSize)
    {
        foreach (var child in Children)
            child.Measure(availableSize);
        return availableSize;
    }

    protected override Size ArrangeOverride(Size finalSize)
    {
        double angle = 0, step = 2 * Math.PI / Children.Count;
        double cx = finalSize.Width / 2, cy = finalSize.Height / 2;
        double r = Math.Min(cx, cy) * 0.8;
        foreach (var child in Children)
        {
            var x = cx + r * Math.Cos(angle) - child.DesiredSize.Width / 2;
            var y = cy + r * Math.Sin(angle) - child.DesiredSize.Height / 2;
            child.Arrange(new Rect(x, y, child.DesiredSize.Width, child.DesiredSize.Height));
            angle += step;
        }
        return finalSize;
    }
}
```

## StyleKeyOverride

```csharp
// Make MyButton style as base Button (picks up Button's ControlTheme)
protected override Type StyleKeyOverride => typeof(Button);
```

## Control Library Project

- Separate class library project
- Reference `Avalonia` NuGet (not `Avalonia.Desktop`)
- Include `Generic.axaml` as embedded resource: `avares://MyLib/Themes/Generic.axaml`
- Register in consuming app: `<StyleInclude Source="avares://MyLib/Themes/Generic.axaml"/>`

## Common Mistakes

- Inheriting from `Control` (WPF habit) instead of `TemplatedControl` for lookless controls
- Not calling `InitializeComponent()` in UserControl constructor
- Forgetting `partial` keyword on UserControl class
- Using `StyledProperty` for high-frequency properties that don't need styling (perf issue)
- Not providing `x:Key="{x:Type local:MyControl}"` in Generic.axaml ControlTheme
