---
name: avalonia-xaml
description: Use when writing or reviewing Avalonia XAML markup, .axaml files, XML namespaces, code-behind, markup extensions, runtime XAML loading, or building UI without XAML in code.
---

# Avalonia XAML

## Overview
Avalonia uses `.axaml` extension (not `.xaml`) to avoid Visual Studio WPF tooling conflicts. XAML is optional; full code-only UI is supported. **(12.0+)** compiled bindings are ON by default (`AvaloniaUseCompiledBindingsByDefault=true`): `{Binding}` maps to `CompiledBinding`, so `x:DataType` is required wherever bindings are used. In 11.x compiled bindings are opt-in (`{CompiledBinding}` / `x:CompileBindings="True"`). Escape hatch: `{ReflectionBinding Path}` or `x:CompileBindings="False"`.

## File Structure

Every `.axaml` file requires the Avalonia root namespace and language namespace:

```xml
<Window xmlns="https://github.com/avaloniaui"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:vm="using:MyApp.ViewModels"
        x:Class="MyApp.MainWindow"
        x:DataType="vm:MainWindowViewModel"
        Title="My App"
        Width="800" Height="450">

    <TextBlock Text="{Binding Greeting}" />

</Window>
```

Corresponding code-behind:

```csharp
// MainWindow.axaml.cs
using Avalonia.Controls;

namespace MyApp;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }
}
```

## XML Namespaces

### Namespace Syntax

| Syntax | Use case | Example |
|---|---|---|
| `using:` | Same solution assemblies (preferred) | `xmlns:vm="using:MyApp.ViewModels"` |
| `clr-namespace:` | External assemblies (requires `;assembly=`) | `xmlns:ctrl="clr-namespace:MyLib.Controls;assembly=MyLib"` |
| URI | Framework namespaces | `xmlns="https://github.com/avaloniaui"` |

### Common Namespaces

| Prefix | URI / Syntax | Purpose |
|---|---|---|
| *(default)* | `https://github.com/avaloniaui` | All Avalonia controls |
| `x:` | `http://schemas.microsoft.com/winfx/2006/xaml` | XAML language features |
| `vm:` | `using:MyApp.ViewModels` | ViewModel types |
| `conv:` | `using:MyApp.Converters` | Converter classes |
| `sys:` | `using:System` | System types (Math, String, etc.) |

## Markup Extensions

| Extension | Purpose | Example |
|---|---|---|
| `{Binding}` | Compiled binding in 12.0+ (needs `x:DataType`); reflection binding in 11.x | `Text="{Binding Name}"` |
| `{CompiledBinding}` | Explicit compile-time checked binding (all versions) | `Text="{CompiledBinding Name}"` |
| `{ReflectionBinding}` | Runtime reflection binding; opt-out when no `x:DataType` (12.0+; 11.x: use `{Binding}`) | `Text="{ReflectionBinding Name}"` |
| `{StaticResource}` | One-time resource lookup | `Fill="{StaticResource AccentBrush}"` |
| `{DynamicResource}` | Live resource lookup (updates on change) | `Background="{DynamicResource SystemControlBackground}"` |
| `{x:Static}` | Static field/property | `Value="{x:Static sys:Math.PI}"` |
| `{x:Type}` | Type reference | `TargetType="{x:Type Button}"` |
| `{x:Null}` | Null literal | `Tag="{x:Null}"` |
| `{OnPlatform}` | Per-platform value | `FontSize="{OnPlatform 12, macOS=14}"` |
| `{OnFormFactor}` | Per-form-factor value | `Width="{OnFormFactor 200, Mobile=100}"` |

## x: Attributes

| Attribute | Purpose | Notes |
|---|---|---|
| `x:Class` | Links AXAML to code-behind partial class | Must match namespace + class name exactly |
| `x:Name` | Names control for code-behind access | Generates a typed field in partial class |
| `x:Key` | Resource dictionary key | Required for resources in `<ResourceDictionary>` |
| `x:DataType` | Compiled binding root type | Required on root or `DataTemplate` when using compiled bindings |
| `x:CompileBindings` | Enable/disable compiled bindings per scope | `x:CompileBindings="False"` to opt out |
| `ExperimentalAttribute` **(12.0+)** | XAML honors `[Experimental]` on types/members: using them needs the diagnostic suppressed (`<NoWarn>`) | |

## Code-Behind Pattern

```csharp
// MyView.axaml.cs
using Avalonia.Controls;

namespace MyApp.Views;

public partial class MyView : UserControl
{
    public MyView()
    {
        InitializeComponent();
    }

    // Access named controls via generated fields
    private void OnButtonClick(object sender, RoutedEventArgs e)
    {
        // myButton is generated from x:Name="myButton" in AXAML
        myButton.IsEnabled = false;
    }
}
```

```xml
<!-- MyView.axaml -->
<UserControl xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             x:Class="MyApp.Views.MyView">
    <Button x:Name="myButton"
            Content="Click Me"
            Click="OnButtonClick" />
</UserControl>
```

## Code-Only UI (No XAML)

Preferred for: dynamic control creation, headless testing, generated UIs.

```csharp
using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;

var window = new Window
{
    Title = "Code Only",
    Width = 400,
    Height = 300,
    Content = new StackPanel
    {
        Spacing = 8,
        Margin = new Thickness(16),
        Children =
        {
            new TextBlock { Text = "Hello, Avalonia!" },
            new Button
            {
                Content = "Click Me",
                HorizontalAlignment = HorizontalAlignment.Left
            }
        }
    }
};
```

Bindings in code:

```csharp
var textBox = new TextBox { DataContext = viewModel };
// (12.0+) explicit types; `new Binding(...)` is a compat alias of ReflectionBinding
textBox.Bind(TextBox.TextProperty, new ReflectionBinding(nameof(MainViewModel.Name)));
textBox.Bind(TextBox.TextProperty, CompiledBinding.Create((MainViewModel vm) => vm.Name)); // (12.0+) AOT/trim safe
// (11.x)
textBox.Bind(TextBox.TextProperty, new Binding("Name"));
```

## Gesture Events (12.0+)

Gesture attached events live directly on `InputElement` — drop the `Gestures.` prefix (`Gestures` is no longer public):

```xml
<Border Pinch="OnPinch" ScrollGesture="OnScroll" Tapped="OnTapped" />
<!-- (11.x) <Border Gestures.Pinch="OnPinch" Gestures.ScrollGesture="OnScroll" /> -->
```

## Resource Dictionaries

```xml
<Application.Resources>
    <ResourceDictionary>
        <ResourceDictionary.MergedDictionaries>
            <ResourceInclude Source="avares://MyApp/Assets/Colors.axaml"/>
        </ResourceDictionary.MergedDictionaries>
        <SolidColorBrush x:Key="BrandBrush" Color="#5B4FCF"/>
    </ResourceDictionary>
</Application.Resources>
```

```xml
<!-- Colors.axaml -->
<ResourceDictionary xmlns="https://github.com/avaloniaui"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <Color x:Key="BrandColor">#5B4FCF</Color>
</ResourceDictionary>
```

## Runtime XAML for Previewers and Editors

For runtime-loaded documents, relative includes, existing root instances, diagnostics, and source locations, read [references/runtime-xaml.md](references/runtime-xaml.md). It covers Avalonia 12.1 and 11.3; normal application views should keep the compiled `InitializeComponent()` path.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Using `.xaml` extension | Rename to `.axaml` |
| Missing `xmlns="https://github.com/avaloniaui"` | Add as first attribute on root element |
| `clr-namespace:` without `;assembly=` for external lib | `xmlns:x="clr-namespace:MyLib;assembly=MyLib"` |
| Compiled binding error: "Cannot resolve symbol" / `{Binding}` fails to compile after moving to 12 | Add `x:DataType="vm:MyViewModel"` to root or DataTemplate, or use `{ReflectionBinding}` |
| `Gestures.Pinch="..."` in 12.x | `Pinch="..."` (12.0+) |
| `x:Name` field not accessible in code-behind | Ensure file is `.axaml` and `InitializeComponent()` is called |
| `{StaticResource}` not found at runtime | Resource must be defined before use in document order |
| `{DynamicResource}` for performance-sensitive paths | Use `{StaticResource}` when resource never changes |
