---
name: avalonia-wpf-migration
description: Use when migrating a WPF application to Avalonia, mapping WPF concepts to Avalonia equivalents, or understanding differences between WPF and Avalonia APIs.
---
# Avalonia WPF Migration

## Overview
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
| `CollectionViewSource` | `DataGridCollectionView` | Different class |
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

## What Works Without Changes
- `INotifyPropertyChanged` implementations
- `ICommand` implementations
- `ObservableCollection<T>` usage
- `IValueConverter` implementations
- Data binding patterns (with namespace/syntax adjustments)
- Most MVVM framework code (ReactiveUI, CommunityToolkit.Mvvm)
- `ItemsControl`, `ListBox`, `DataGrid` (similar APIs)
- Grid, StackPanel, DockPanel layouts (same attached properties)

## Common Mistakes
- Using WPF Trigger syntax — silently ignored or compile error
- Using `pack://` URIs — assets not found
- Calling `MessageBox.Show()` — doesn't exist
- Using `FrameworkElement` as base class — use `Control`
- `Style TargetType` without `x:Key` for ControlThemes — template not applied
