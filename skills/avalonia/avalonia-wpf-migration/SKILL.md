---
name: avalonia-wpf-migration
description: Use when migrating a WPF application to Avalonia, mapping WPF concepts to Avalonia equivalents, or understanding differences between WPF and Avalonia APIs.
---
# Avalonia WPF Migration

## Overview
Target: **Avalonia 12.x** (12.1.x recommended); 11.x notes are labeled `(11.x)`; see avalonia-versions. Avalonia 12 requires net8.0+ (net10.0 recommended) — **.NET Framework and netstandard2.0 targets are not supported**, so retarget WPF apps on .NET Framework to modern .NET first (Avalonia 11.3 is the last line supporting them).

Avalonia's API is intentionally WPF-like. Most XAML, binding, and MVVM patterns transfer directly. Key differences: styling system, ControlTemplates → ControlThemes, no Triggers, `.axaml` extension, namespace differences.

## Quick Mapping Table
| WPF | Avalonia | Notes |
|---|---|---|
| `.xaml` | `.axaml` | Extension differs |
| `xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"` | `xmlns="https://github.com/avaloniaui"` | Root namespace |
| `DependencyProperty` | `StyledProperty` / `DirectProperty` | See property system |
| `FrameworkElement` | `Control` | Base for custom controls |
| `UserControl` (base) | `UserControl` | Same name, similar API |
| `Control` (for lookless) | `TemplatedControl` | Different base class |
| `Style` with `TargetType` | `ControlTheme` with `TargetType` | Styling lookless controls |
| `Style` with `Triggers` | `Style` with nested styles + pseudoclasses | No Triggers in Avalonia |
| `DataTrigger` | Binding + pseudoclass / `Classes` binding | Pattern change |
| `ResourceDictionary` `Source=` | `ResourceInclude Source="avares://..."` | URI scheme differs |
| `pack://application:,,,/` | `avares://AssemblyName/` | Asset URI scheme |
| `Window.ShowDialog()` | `window.ShowDialog(owner)` | Requires owner parameter |
| `MessageBox.Show()` | No built-in — use dialog or notification | API removed |
| `Dispatcher.Invoke()` | `Dispatcher.UIThread.InvokeAsync()` | Async-first |
| `BindingOperations.ClearBinding()` | `control.ClearValue(prop)` | Slightly different |
| `x:Static` | `x:Static` | Same |
| `TemplateBinding` | `TemplateBinding` | Same |
| `RelativeSource Self` | `{Binding $self.Property}` | Different syntax |
| `RelativeSource AncestorType` | `{Binding $parent[TypeName].Property}` | Different syntax |
| `EventTrigger` + `Storyboard` | `Animation` in styles | Different animation system |
| `BitmapImage` + `Uri` | `Bitmap` + `AssetLoader` | Different image loading |
| `IValueConverter` | `IValueConverter` | Same interface |
| `IMultiValueConverter` | `IMultiValueConverter` | Same interface |
| `ObservableCollection<T>` | `ObservableCollection<T>` | Same |
| `ICommand` | `ICommand` | Same |
| `CollectionViewSource` | No equivalent — sort/filter/group in the ViewModel (e.g. DynamicData, LINQ); `DataGridCollectionView` (`Avalonia.Controls.DataGrid`) only for DataGrid | No `ICollectionView` infrastructure |
| `GroupBox` | `GroupBox` (12.0+) | 11.x: `HeaderedContentControl` + styling |
| `ListView` + `GridView` (read-only columns) | `TableView` (12.1+) | 12.0/11.x: `DataGrid` (`Avalonia.Controls.DataGrid`) or `TreeDataGrid`; `DataGrid` is maintenance-mode |
| `DataGrid` (editable) | `DataGrid` (`Avalonia.Controls.DataGrid`, separate package) | Not in core |
| `TextBox` watermark (e.g. `Watermark` in toolkits) | `TextBox.PlaceholderText` (12.0+) | 11.x: `Watermark` (obsolete in 12) |
| `DataObject` / `IDataObject` (clipboard, drag-drop) | `DataTransfer` + `DataTransferItem` (12.0+) | 11.x: `DataObject`; use `DragDrop.DoDragDropAsync`, `DragEventArgs.DataTransfer` |
| `DragDrop.DoDragDrop` | `await DragDrop.DoDragDropAsync(...)` (12.0+) | |
| `Clipboard.SetText/GetText` | `clipboard.SetTextAsync` / `TryGetTextAsync` | Async |
| `Frame` + `NavigationService` | ContentControl + ViewModel swap | MVVM pattern preferred |

## Styles: No Triggers
WPF:
```xml
<!-- WPF - DOES NOT WORK in Avalonia -->
<Style TargetType="Button">
    <Style.Triggers>
        <Trigger Property="IsMouseOver" Value="True">
            <Setter Property="Background" Value="Red"/>
        </Trigger>
    </Style.Triggers>
</Style>
```
Avalonia:
```xml
<Style Selector="Button:pointerover">
    <Setter Property="Background" Value="Red"/>
</Style>
```

## ControlTemplate → ControlTheme
WPF:
```xml
<Style TargetType="Button">
    <Setter Property="Template">
        <Setter.Value>
            <ControlTemplate TargetType="Button">
                ...
            </ControlTemplate>
        </Setter.Value>
    </Setter>
</Style>
```
Avalonia:
```xml
<ControlTheme TargetType="Button" x:Key="{x:Type Button}">
    <Setter Property="Template">
        <ControlTemplate>
            ...
        </ControlTemplate>
    </Setter>
</ControlTheme>
```

## RelativeSource Binding
```xml
<!-- WPF -->
<TextBlock Text="{Binding RelativeSource={RelativeSource AncestorType=Window}, Path=Title}"/>

<!-- Avalonia -->
<TextBlock Text="{Binding $parent[Window].Title}"/>
<TextBlock Text="{Binding $self.Tag}"/>
<TextBlock Text="{Binding $parent.Tag}"/>
```

## Asset URIs
```xml
<!-- WPF -->
<Image Source="pack://application:,,,/Assets/logo.png"/>

<!-- Avalonia -->
<Image Source="avares://MyApp/Assets/logo.png"/>
```

## Dialogs
```csharp
// WPF
MessageBox.Show("Hello");
var dialog = new OpenFileDialog();
dialog.ShowDialog();

// Avalonia
// Use StorageProvider for file dialogs (see avalonia-services skill)
// Use WindowNotificationManager for notifications
// For message dialogs: use a community library like MessageBox.Avalonia
// or implement a simple dialog Window
var result = await new ConfirmDialog("Are you sure?").ShowDialog<bool>(owner);
```

## Dispatcher
```csharp
// WPF
Dispatcher.Invoke(() => { /* UI update */ });

// Avalonia
await Dispatcher.UIThread.InvokeAsync(() => { /* UI update */ });
// or
Dispatcher.UIThread.Post(() => { /* fire-and-forget */ });
```

## Bindings (12.0+)
Compiled bindings are the default: WPF-style `{Binding Name}` needs `x:DataType` on the root/`DataTemplate`, otherwise it fails to compile. Quick path for ported XAML: add `x:DataType`, or use `{ReflectionBinding Name}`, or set `<AvaloniaUseCompiledBindingsByDefault>false</AvaloniaUseCompiledBindingsByDefault>`. Data-annotation validation is opt-in.

## MVVM Frameworks
- ReactiveUI: package `ReactiveUI.Avalonia` (12.x); `Avalonia.ReactiveUI` does not exist for 12.
- CommunityToolkit.Mvvm: unchanged.
- WPF `SystemDecorations`/`WindowStyle`-like tweaks → `Window.WindowDecorations` (12.0+).

## What Works Without Changes
- `INotifyPropertyChanged` implementations
- `ICommand` implementations
- `ObservableCollection<T>` usage
- `IValueConverter` implementations
- Data binding patterns (with namespace/syntax adjustments)
- Most MVVM framework code (ReactiveUI, CommunityToolkit.Mvvm)
- `ItemsControl`, `ListBox` (similar APIs); `DataGrid` needs the `Avalonia.Controls.DataGrid` package
- Grid, StackPanel, DockPanel layouts (same attached properties)

## Common Mistakes
- Using WPF Trigger syntax — silently ignored or compile error
- Using `pack://` URIs — assets not found
- Calling `MessageBox.Show()` — doesn't exist
- Targeting `net48` / `netstandard2.0` with Avalonia 12 — unsupported
- `{Binding}` without `x:DataType` in 12 — compile error
- Using `FrameworkElement` as base class — use `Control`
- `Style TargetType` without `x:Key` for ControlThemes — template not applied
