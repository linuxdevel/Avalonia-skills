---
name: avalonia-events
description: Use when working with Avalonia routed events — defining custom RoutedEvent, handling bubbling or tunneling events, attaching handlers with AddHandler, RoutingStrategies, the OnApplyTemplate/PART_ pattern, or class-level static handlers via AddClassHandler.
---
# Avalonia Routed Events

## Overview
Avalonia uses routed events that travel the logical tree. Three strategies:
- **Bubble** — source → root (default for most input events)
- **Tunnel** — root → source (`Preview` prefix by convention)
- **Direct** — only raised on source element

All input events (`PointerPressed`, `KeyDown`, etc.) are routed.

## Handling Events

XAML:
```xml
<Button Click="Button_Click"/>
<StackPanel PointerPressed="Panel_PointerPressed"/>
```

Code-behind (direct `+=`):
```csharp
myButton.Click += Button_Click;
private void Button_Click(object? sender, RoutedEventArgs e) { }
```

`AddHandler` — explicit routing strategy, required for tunneling:
```csharp
// Catch bubbled clicks from any child Button
myPanel.AddHandler(Button.ClickEvent, OnAnyButtonClick, RoutingStrategies.Bubble);

// Intercept before children see it (tunneling)
myPanel.AddHandler(InputElement.PointerPressedEvent, OnPreviewPointerPressed,
    RoutingStrategies.Tunnel);

private void OnAnyButtonClick(object? sender, RoutedEventArgs e)
{
    Console.WriteLine($"Clicked: {e.Source}");
}
```

Remove handler:
```csharp
myPanel.RemoveHandler(Button.ClickEvent, OnAnyButtonClick);
```

## Stopping Propagation

```csharp
private void OnKeyDown(object? sender, KeyEventArgs e)
{
    if (e.Key == Key.Escape)
    {
        e.Handled = true; // stops further bubbling/tunneling
    }
}
```

`e.Handled = true` prevents subsequent handlers in the route from firing.

## Defining Custom Routed Events

```csharp
public class MyControl : Control
{
    // Event registration
    public static readonly RoutedEvent<RoutedEventArgs> ActivatedEvent =
        RoutedEvent.Register<MyControl, RoutedEventArgs>(
            name: "Activated",
            routingStrategy: RoutingStrategies.Bubble);

    // CLR event wrapper
    public event EventHandler<RoutedEventArgs> Activated
    {
        add => AddHandler(ActivatedEvent, value);
        remove => RemoveHandler(ActivatedEvent, value);
    }

    // Raise it
    protected void RaiseActivated()
        => RaiseEvent(new RoutedEventArgs(ActivatedEvent, this));
}
```

Custom event args:
```csharp
public class ValueChangedEventArgs : RoutedEventArgs
{
    public double OldValue { get; }
    public double NewValue { get; }

    public ValueChangedEventArgs(RoutedEvent routedEvent, object source,
        double oldValue, double newValue)
        : base(routedEvent, source)
    {
        OldValue = oldValue;
        NewValue = newValue;
    }
}

public static readonly RoutedEvent<ValueChangedEventArgs> ValueChangedEvent =
    RoutedEvent.Register<MyControl, ValueChangedEventArgs>(
        "ValueChanged", RoutingStrategies.Bubble);
```

## Tunneling Events (Preview)

Convention: tunneling events prefixed with `Preview`.

```csharp
public static readonly RoutedEvent<PointerPressedEventArgs> PreviewPointerPressedEvent =
    RoutedEvent.Register<InputElement, PointerPressedEventArgs>(
        "PreviewPointerPressed",
        RoutingStrategies.Tunnel);
```

Use pattern:
```csharp
// Parent intercepts before child
myParent.AddHandler(InputElement.PointerPressedEvent, Handler, RoutingStrategies.Tunnel);
```

## RoutingStrategies Enum

| Value | Meaning |
|---|---|
| `Direct` | Only raised on source element |
| `Bubble` | Source → root |
| `Tunnel` | Root → source |
| `All` | Both tunnel and bubble (fire twice) |

## OnApplyTemplate Pattern

Called when `ControlTemplate` is applied. Use to wire up named template parts:
```csharp
protected override void OnApplyTemplate(TemplateAppliedEventArgs e)
{
    base.OnApplyTemplate(e);

    // Get required part (throws if missing)
    _button = e.NameScope.Get<Button>("PART_Button");
    _button.Click += OnPartButtonClick;

    // Get optional part (returns null if missing)
    _indicator = e.NameScope.Find<Border>("PART_Indicator");
}

// Clean up old subscriptions if template changes
private Button? _button;
private Border? _indicator;
```

Template XAML:
```xml
<ControlTemplate TargetType="local:MyControl">
    <StackPanel>
        <Border Name="PART_Indicator" Background="Gray"/>
        <Button Name="PART_Button" Content="Click"/>
    </StackPanel>
</ControlTemplate>
```

Convention: template part names prefixed with `PART_`.

Declare expected parts (documentation + tooling):
```csharp
[TemplatePart("PART_Button", typeof(Button))]
[TemplatePart("PART_Indicator", typeof(Border))]
public class MyControl : TemplatedControl { }
```

## Class Handlers (Static, All Instances)

```csharp
static MyControl()
{
    // Fires for every instance when a child Button is clicked
    Button.ClickEvent.AddClassHandler<MyControl>((instance, e) =>
        instance.OnChildButtonClicked(e));

    // Intercept tunneling on all instances
    InputElement.PointerPressedEvent.AddClassHandler<MyControl>(
        (instance, e) => instance.OnPreviewPointerPressed(e),
        RoutingStrategies.Tunnel);
}

private void OnChildButtonClicked(RoutedEventArgs e)
{
    Console.WriteLine($"Button clicked in {this}");
}
```

## Interaction Events (Non-Routed) vs Routed

`Control.AttachedToVisualTree` / `DetachedFromVisualTree` — not routed, fires on control directly:
```csharp
protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
{
    base.OnAttachedToVisualTree(e);
    // Safe to access TopLevel, start subscriptions
}

protected override void OnDetachedFromVisualTree(VisualTreeAttachmentEventArgs e)
{
    base.OnDetachedFromVisualTree(e);
    // Clean up subscriptions
}
```

## Common Mistakes

- **`+=` vs `AddHandler` routing strategies** — `myPanel.PointerPressed += Handler` only catches `Bubble` by default; use `AddHandler` with `RoutingStrategies.Tunnel` for preview intercept
- **Tunnel events won't fire with default `Bubble` strategy** — must explicitly pass `RoutingStrategies.Tunnel` to `AddHandler`
- **`new RoutedEventArgs(MyEvent)` missing source** — always pass `this` as source: `new RoutedEventArgs(MyEvent, this)`
- **Forgetting `e.Handled = true`** in a handler that should consume the event — other handlers in the route still fire
- **`OnApplyTemplate` without cleaning up previous subscriptions** — template can be re-applied; detach old handlers before attaching new ones
- **`e.NameScope.Get<T>` throws if part missing** — use `Find<T>` for optional parts to avoid `KeyNotFoundException`
