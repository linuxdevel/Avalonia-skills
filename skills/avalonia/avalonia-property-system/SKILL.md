---
name: avalonia-property-system
description: Use when working with Avalonia's property system: StyledProperty, DirectProperty, AttachedProperty, property inheritance, metadata override, coercion, value priority, or observing property changes via GetObservable or OnPropertyChanged.
---
# Avalonia Property System

## Overview
`AvaloniaProperty` is the foundation of Avalonia's data binding, styling, and animations. Three kinds:
- **StyledProperty** — full-featured; supports styling, animation, inheritance
- **DirectProperty** — lightweight, CLR-field-backed; no styling/animation support
- **AttachedProperty** — set on foreign controls (like `Grid.Row`)

## StyledProperty

```csharp
public static readonly StyledProperty<IBrush?> BackgroundProperty =
    AvaloniaProperty.Register<MyControl, IBrush?>(
        name: nameof(Background),
        defaultValue: null,
        inherits: false,
        defaultBindingMode: BindingMode.OneWay,
        validate: null,
        coerce: CoerceBackground);

public IBrush? Background
{
    get => GetValue(BackgroundProperty);
    set => SetValue(BackgroundProperty, value);
}

private static IBrush? CoerceBackground(AvaloniaObject instance, IBrush? value)
    => value ?? Brushes.Transparent;
```

Inherit/reuse from another class:
```csharp
// Re-register an existing property as owner
public static readonly StyledProperty<IBrush?> BackgroundProperty =
    Border.BackgroundProperty.AddOwner<MyPanel>();
```

## DirectProperty

Use for properties that back observable collections, streams, or are performance-sensitive:
```csharp
public static readonly DirectProperty<MyControl, string> TextProperty =
    AvaloniaProperty.RegisterDirect<MyControl, string>(
        name: nameof(Text),
        getter: o => o.Text,
        setter: (o, v) => o.Text = v,
        defaultBindingMode: BindingMode.TwoWay,
        enableDataValidation: true);

private string _text = "";
public string Text
{
    get => _text;
    set => SetAndRaise(TextProperty, ref _text, value);
}
```

`SetAndRaise` performs equality check, updates field, raises `PropertyChanged`.

## AttachedProperty

```csharp
public static class Grid
{
    public static readonly AttachedProperty<int> RowProperty =
        AvaloniaProperty.RegisterAttached<Grid, Control, int>(
            name: "Row",
            defaultValue: 0,
            inherits: false);

    public static int GetRow(Control element) => element.GetValue(RowProperty);
    public static void SetRow(Control element, int value) => element.SetValue(RowProperty, value);
}
```

XAML usage:
```xml
<TextBlock Grid.Row="1" Grid.Column="2"/>
```

## Property Value Priority (highest → lowest)

| Priority | Source |
|---|---|
| 1 | Animation |
| 2 | Local value (`SetValue` / binding at `LocalValue`) |
| 3 | Style trigger (active pseudoclass setter) |
| 4 | Template binding |
| 5 | Style setter (non-triggered) |
| 6 | Inherited value |
| 7 | Default value |

`SetCurrentValue` — sets without overriding bindings/styles (priority: LocalValue but clears on style change):
```csharp
// Doesn't break two-way binding
myControl.SetCurrentValue(IsCheckedProperty, true);
```

## Observing Property Changes

On a specific instance (reactive):
```csharp
myTextBox
    .GetObservable(TextBox.TextProperty)
    .Subscribe(text => Console.WriteLine($"Text: {text}"));

// With debounce (requires System.Reactive)
myTextBox
    .GetObservable(TextBox.TextProperty)
    .Throttle(TimeSpan.FromMilliseconds(300))
    .ObserveOn(RxApp.MainThreadScheduler)
    .Subscribe(HandleTextChanged);
```

In a control, override `OnPropertyChanged`:
```csharp
protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
{
    base.OnPropertyChanged(change);

    if (change.Property == ValueProperty)
    {
        var newValue = change.GetNewValue<int>();
        var oldValue = change.GetOldValue<int>();
        UpdateVisuals(newValue);
    }
}
```

Static class handler (fires for all instances):
```csharp
static MyControl()
{
    ValueProperty.Changed.AddClassHandler<MyControl>((control, e) =>
        control.OnValueChanged(e));

    // Or multiple properties
    AffectsRender<MyControl>(ForegroundProperty, BackgroundProperty, PaddingProperty);
    AffectsMeasure<MyControl>(WidthProperty, HeightProperty);
    AffectsArrange<MyControl>(AlignmentProperty);
}
```

`AffectsRender` / `AffectsMeasure` / `AffectsArrange` — declare layout/render dependencies efficiently.

## Inherited Properties

```csharp
public static readonly StyledProperty<FlowDirection> FlowDirectionProperty =
    AvaloniaProperty.Register<Control, FlowDirection>(
        nameof(FlowDirection),
        defaultValue: FlowDirection.LeftToRight,
        inherits: true);
```

Child controls inherit the value from their nearest ancestor that sets it explicitly.

## Metadata Override

Override default value or coerce function for a subclass:
```csharp
static MyControl()
{
    BackgroundProperty.OverrideMetadata<MyControl>(
        new StyledPropertyMetadata<IBrush?>(
            defaultValue: Brushes.White,
            defaultBindingMode: BindingMode.OneWay,
            coerce: MyCoerce));
}
```

## Data Validation

Enable on `DirectProperty` with `enableDataValidation: true`, then throw in setter or implement `INotifyDataErrorInfo`:
```csharp
private int _age;
public int Age
{
    get => _age;
    set
    {
        if (value < 0 || value > 150)
            throw new ArgumentOutOfRangeException(nameof(Age), "Age must be 0–150");
        SetAndRaise(AgeProperty, ref _age, value);
    }
}
```

## Common Mistakes

- **Field must end with `Property`** — convention: `FooProperty` for public property `Foo`; breaks tooling otherwise
- **`DirectProperty` for rarely-changed values** — incurs no overhead, but can't be used in styles or animations; use `StyledProperty` if styling needed
- **Forgetting `SetAndRaise` in `DirectProperty` setter** — plain field assignment won't notify bindings
- **Setting value in constructor via property setter** — creates a local value that blocks style/theme overrides; use `SetCurrentValue` or set field directly in constructor
- **`AddOwner` vs. `Register`** — `AddOwner` shares metadata and identity with source property (same `AvaloniaProperty` instance); bindings between types sharing a property work correctly
- **`change.GetNewValue<T>()`** — must match registered type exactly; mismatched cast throws `InvalidCastException`
