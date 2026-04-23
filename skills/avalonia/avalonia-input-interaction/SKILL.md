---
name: avalonia-input-interaction
description: Use when handling pointer events, keyboard input, gestures, focus, drag-and-drop, or hot keys in Avalonia. Covers PointerPressed/Released/Moved, KeyDown/KeyUp, TextInput, HotKeyManager, KeyGesture, focus management, TapGestureRecognizer, PinchGestureRecognizer, DragDrop.DoDragDrop, DataObject, and Cursor types.
---
# Avalonia Input & Interaction

## Overview
All input routes as routed events (bubbling by default, tunneling with "Preview" prefix). Pointer events are unified across mouse, touch, and stylus.

## Pointer Events

| Event | Fires when |
|---|---|
| `PointerPressed` | Button/finger down |
| `PointerReleased` | Button/finger up |
| `PointerMoved` | Pointer moves over control |
| `PointerEntered` | Pointer enters bounds |
| `PointerExited` | Pointer leaves bounds |
| `PointerCaptureLost` | Capture released |
| `Tapped` | Quick tap/click |
| `DoubleTapped` | Double tap/click |
| `RightTapped` | Right-click / long press |

```csharp
myControl.PointerPressed += (s, e) =>
{
    var point = e.GetPosition(myControl);
    var props = e.GetCurrentPoint(myControl).Properties;
    if (props.IsLeftButtonPressed) { /* left click */ }
    if (props.IsRightButtonPressed) { /* right click */ }
    if (props.IsMiddleButtonPressed) { /* middle click */ }
};
```

Capture pointer (receive events outside bounds):
```csharp
myControl.PointerPressed += (s, e) =>
{
    e.Pointer.Capture(myControl);
};
myControl.PointerReleased += (s, e) =>
{
    e.Pointer.Capture(null); // release
};
```

Check pointer type:
```csharp
myControl.PointerPressed += (s, e) =>
{
    if (e.Pointer.Type == PointerType.Touch) { /* touch */ }
    if (e.Pointer.Type == PointerType.Pen) { /* stylus */ }
};
```

## Keyboard Events

| Event | Fires when |
|---|---|
| `KeyDown` | Key pressed (repeats while held) |
| `KeyUp` | Key released |
| `TextInput` | Text character produced |

```csharp
myControl.KeyDown += (s, e) =>
{
    if (e.Key == Key.Enter && e.KeyModifiers == KeyModifiers.Control)
    {
        e.Handled = true; // stop bubbling + prevent default
        SubmitForm();
    }
};
```

```csharp
myTextBox.TextInput += (s, e) =>
{
    if (!char.IsDigit(e.Text![0]))
        e.Handled = true; // block non-digit input
};
```

`KeyModifiers` flags: `None`, `Alt`, `Control`, `Shift`, `Meta` (combinable with `|`)

```csharp
// Ctrl+Shift+Z
if (e.Key == Key.Z && e.KeyModifiers == (KeyModifiers.Control | KeyModifiers.Shift))
```

## Hot Keys

XAML registration:
```xml
<Button HotKey="Ctrl+S" Command="{Binding SaveCommand}" Content="Save"/>
<MenuItem HotKey="Ctrl+Z" Header="Undo" Command="{Binding UndoCommand}"/>
```

Code registration:
```csharp
HotKeyManager.RegisterHotKey(myControl, new KeyGesture(Key.S, KeyModifiers.Control));
HotKeyManager.SetHotKey(myButton, new KeyGesture(Key.F5));
```

Unregister:
```csharp
HotKeyManager.SetHotKey(myControl, null);
```

## Focus

```csharp
// Programmatic focus
myControl.Focus();

// Via FocusManager
var fm = TopLevel.GetTopLevel(this)?.FocusManager;
fm?.Focus(myControl, NavigationMethod.Tab);

// Get currently focused element
var focused = fm?.GetFocusedElement();
```

XAML focus control:
```xml
<TextBox IsTabStop="False"/>           <!-- exclude from tab order -->
<TextBox TabIndex="2"/>                <!-- explicit tab order -->
<TextBox AutoFocus="True"/>            <!-- focus on load (Avalonia 11.1+) -->
```

Pseudoclasses for styling:
```xml
<Style Selector="TextBox:focus">
    <Setter Property="BorderBrush" Value="Blue"/>
</Style>
<Style Selector="Button:focus-visible">
    <Setter Property="BorderThickness" Value="2"/>
</Style>
```

Focus scope (contains Tab navigation):
```xml
<Panel FocusManager.IsFocusScope="True">
    <!-- Tab cycles within this panel -->
</Panel>
```

## Gesture Recognizers

Add to any `InputElement.GestureRecognizers`:
```xml
<Border Background="LightBlue" Width="200" Height="200">
    <Border.GestureRecognizers>
        <TapGestureRecognizer Tapped="OnTapped"/>
        <PinchGestureRecognizer PinchUpdated="OnPinchUpdated"/>
    </Border.GestureRecognizers>
</Border>
```

```csharp
private void OnPinchUpdated(object? sender, PinchEventArgs e)
{
    _scale *= e.Scale;
    myBorder.RenderTransform = new ScaleTransform(_scale, _scale);
}
```

| Recognizer | Events |
|---|---|
| `TapGestureRecognizer` | `Tapped` |
| `DoubleTapGestureRecognizer` | `DoubleTapped` |
| `PinchGestureRecognizer` | `PinchUpdated`, `PinchEnded` |
| `PullGestureRecognizer` | `PullDelta`, `PullEnded` |
| `ScrollGestureRecognizer` | `ScrollGesture`, `ScrollGestureEnded`, `ScrollGestureInertiaStarting` |

## Drag and Drop

Source (initiates drag):
```csharp
private async void OnPointerPressed(object? sender, PointerPressedEventArgs e)
{
    var data = new DataObject();
    data.Set(DataFormats.Text, "dragged text");
    data.Set("custom/format", myObject);

    var result = await DragDrop.DoDragDrop(e, data,
        DragDropEffects.Copy | DragDropEffects.Move);
    // result: DragDropEffects indicating what happened
}
```

Target (receives drop):
```xml
<Border DragDrop.AllowDrop="True"
        Drop="OnDrop"
        DragOver="OnDragOver"
        DragEnter="OnDragEnter"
        DragLeave="OnDragLeave"/>
```

```csharp
private void OnDragOver(object? sender, DragEventArgs e)
{
    e.DragEffects = e.Data.Contains(DataFormats.Text)
        ? DragDropEffects.Copy
        : DragDropEffects.None;
    e.Handled = true;
}

private void OnDrop(object? sender, DragEventArgs e)
{
    if (e.Data.Contains(DataFormats.Text))
    {
        var text = e.Data.GetText();
        // use text
    }
    if (e.Data.Contains(DataFormats.Files))
    {
        var files = e.Data.GetFiles();
        // IEnumerable<IStorageItem>
    }
}
```

Built-in `DataFormats`: `Text`, `Files`, `FileNames`

## Cursor

```xml
<Border Cursor="Hand"/>
<TextBox Cursor="IBeam"/>
<Border Cursor="Wait"/>
```

Available cursors: `Default`, `Arrow`, `Cross`, `Hand`, `Help`, `IBeam`, `No`, `SizeAll`, `SizeNESW`, `SizeNS`, `SizeNWSE`, `SizeWE`, `TopSide`, `BottomSide`, `LeftSide`, `RightSide`, `Wait`, `None`

Custom cursor from bitmap:
```csharp
var cursor = new Cursor(myBitmap, new PixelPoint(hotspotX, hotspotY));
myControl.Cursor = cursor;
```

## Scroll Events

```csharp
myControl.PointerWheelChanged += (s, e) =>
{
    var delta = e.Delta; // Vector: X for horizontal, Y for vertical
    ScrollBy(-delta.Y * 30);
};
```

## Common Mistakes

- **Not setting `e.Handled = true`** on `KeyDown` — event bubbles to parent; `TextBox` will still consume keys
- **`DragDrop.DoDragDrop` must be called on pointer event** — calling after `await` loses the pointer event context
- **`Focus()` before control is attached to visual tree** — silently does nothing; call in `OnAttachedToVisualTree` or later
- **Gesture recognizers vs. events** — `Tapped`/`DoubleTapped` fire on `InputElement` directly; `TapGestureRecognizer` needed only for custom gesture behavior
- **`DragDrop.AllowDrop` is an attached property** — must be set on the drop target, not a parent
- **`PointerPressed` fires before `Tapped`** — don't handle both if one is sufficient
