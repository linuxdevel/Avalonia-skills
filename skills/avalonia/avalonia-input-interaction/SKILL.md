---
name: avalonia-input-interaction
description: Use when handling pointer events, keyboard input, gestures, focus, drag-and-drop, or hot keys in Avalonia 11.3/12.x. Covers PointerPressed/Released/Moved, KeyDown/KeyUp, TextInput, HotKeyManager, KeyGesture, focus management and Focus Traversal (12.0+), gesture events and recognizers, drag-and-drop (DragDrop.DoDragDropAsync, DataTransfer, DataFormat; 11.x DataObject), and Cursor types.
---
# Avalonia Input & Interaction

Version labels: see `avalonia-versions`. **(12.0+)** = 12.x only, **(11.x)** = 11.x only, unlabeled = all.

## Overview
All input routes as routed events (bubbling by default, tunneling with "Preview" prefix). Pointer events are unified across mouse, touch, and stylus.

**(12.0+) Touch/pen select and focus on pointer release**, not press (mouse unchanged). `ListBoxItem`/`TreeViewItem` handle selection themselves. Access keys (`_Save`) match the symbol printed on the key (accents, digits); `AccessText.AccessKey` is `string?`.

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
myControl.Focus(NavigationMethod.Tab);

// Via FocusManager
var fm = TopLevel.GetTopLevel(this)?.FocusManager;
fm?.Focus(myControl, NavigationMethod.Tab);
var focused = fm?.GetFocusedElement();
```

XAML focus control:
```xml
<TextBox IsTabStop="False"/>           <!-- exclude from tab order -->
<TextBox TabIndex="2"/>                <!-- explicit tab order -->
```
There is no `AutoFocus` property; call `Focus()` after attach (e.g. in `Loaded`/`OnAttachedToVisualTree`) or use `FocusManager`.

**(12.0+) Focus Traversal API** — `IFocusManager` is public and manages all focus:
```csharp
fm.TryMoveFocus(NavigationDirection.Next);                       // bool
var next = fm.FindNextElement(NavigationDirection.Next);         // IInputElement? (options: FindNextElementOptions)
var first = fm.FindFirstFocusableElement();
var last  = fm.FindLastFocusableElement();
```
(11.x) `KeyboardNavigationHandler.GetNext` — removed in 12.

**(12.0+) Cancellable focus** — `GettingFocus` / `LosingFocus` use `FocusChangingEventArgs`:
```csharp
myBox.LosingFocus += (s, e) =>
{
    if (!IsValid()) e.TryCancel();            // or e.TrySetNewFocusedElement(otherControl)
};
```
`GotFocus` / `LostFocus` use **(12.0+)** `FocusChangedEventArgs` (`OldFocusedElement`, `NewFocusedElement`, `NavigationMethod`, `KeyModifiers`); **(11.x)** `GotFocusEventArgs`.

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

## Gestures

`Tapped`, `RightTapped`, `DoubleTapped`, `Holding` are events on `InputElement`. Touch gestures are raised by recognizers added to `GestureRecognizers` (e.g. `PinchGestureRecognizer`, `ScrollGestureRecognizer`, `PullGestureRecognizer`) and handled as routed events on the element:
```xml
<!-- (12.0+) events directly on InputElement -->
<Border Pinch="OnPinch" PinchEnded="OnPinchEnded">
    <Border.GestureRecognizers>
        <PinchGestureRecognizer/>
    </Border.GestureRecognizers>
</Border>
<!-- (11.x) Gestures.Pinch="OnPinch" Gestures.PinchEnded="OnPinchEnded" -->
```

```csharp
private void OnPinch(object? sender, PinchEventArgs e)
{
    _scale *= e.Scale;
    myBorder.RenderTransform = new ScaleTransform(_scale, _scale);
}
```

| Event (on `InputElement`) | Args |
|---|---|
| `Pinch`, `PinchEnded` | `PinchEventArgs`, `PinchEndedEventArgs` |
| `PullGesture`, `PullGestureEnded` | `PullGestureEventArgs`, `PullGestureEndedEventArgs` |
| `ScrollGesture`, `ScrollGestureInertiaStarting`, `ScrollGestureEnded` | `ScrollGesture*EventArgs` |
| `SwipeGesture`, `SwipeGestureEnded` | `SwipeGestureEventArgs`, `SwipeGestureEndedEventArgs` |
| `PointerTouchPadGestureMagnify/Rotate/Swipe` | `PointerDeltaEventArgs` |

## Drag and Drop

**(12.0+)** Source (initiates drag):
```csharp
private async void OnPointerPressed(object? sender, PointerPressedEventArgs e)
{
    var item = DataTransferItem.CreateText("dragged text");
    var myFormat = DataFormat.CreateInProcessFormat<MyType>("myapp/mytype");
    item.Set(myFormat, myObject);                 // extra in-process format on same item

    var data = new DataTransfer();
    data.Add(item);

    var result = await DragDrop.DoDragDropAsync(e, data,
        DragDropEffects.Copy | DragDropEffects.Move);
}
```

Target (receives drop):
```xml
<Border DragDrop.AllowDrop="True"
        DragDrop.Drop="OnDrop" DragDrop.DragOver="OnDragOver"
        DragDrop.DragEnter="OnDragEnter" DragDrop.DragLeave="OnDragLeave"/>
```

```csharp
// (12.0+)
private void OnDragOver(object? sender, DragEventArgs e)
{
    e.DragEffects = e.DataTransfer.Contains(DataFormat.Text)
        ? DragDropEffects.Copy
        : DragDropEffects.None;
    e.Handled = true;
}

private void OnDrop(object? sender, DragEventArgs e)
{
    var text = e.DataTransfer.TryGetText();               // string?
    var files = e.DataTransfer.TryGetFiles();             // IStorageItem[]?
    var mine = e.DataTransfer.TryGetValue(myFormat);      // DataFormat<T> where T : class
}
```
Built-in `DataFormat`: `Text`, `Bitmap`, `File`. Custom: `DataFormat.CreateStringApplicationFormat(id)`, `CreateBytesApplicationFormat(id)`, `CreateInProcessFormat<T>(id)`.

**(11.x)** equivalent — do not use in 12:
```csharp
var data = new DataObject();
data.Set(DataFormats.Text, "dragged text");
var result = await DragDrop.DoDragDrop(e, data, DragDropEffects.Copy);
// target: e.Data.Contains(DataFormats.Text), e.Data.GetText(), e.Data.GetFiles()
// DataFormats: Text, Files, FileNames
```

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
- **`DragDrop.DoDragDropAsync` (11.x: `DoDragDrop`) must be called from the pointer event handler** — calling after `await` loses the pointer event context
- **`Focus()` before control is attached to visual tree** — silently does nothing; call in `OnAttachedToVisualTree` or later
- **Gesture recognizers vs. events** — `Tapped`/`DoubleTapped` fire on `InputElement` directly, no recognizer needed; touch gestures (`Pinch`, `ScrollGesture`) need the matching recognizer in `GestureRecognizers`
- **(12.0+) `Gestures.Pinch` prefix** — removed; use `Pinch="..."` directly. `Gestures` is no longer public
- **(12.0+) Using `DataObject`/`DataFormats`/`e.Data`** — gone; use `DataTransfer`/`DataFormat`/`e.DataTransfer`
- **(12.0+) Selection on touch fires on release** — don't rely on `PointerPressed` to select for touch/pen
- **`DragDrop.AllowDrop` is an attached property** — must be set on the drop target, not a parent
- **`PointerPressed` fires before `Tapped`** — don't handle both if one is sufficient
