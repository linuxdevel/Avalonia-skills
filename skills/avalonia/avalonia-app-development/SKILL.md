---
name: avalonia-app-development
description: Use when setting up Avalonia app structure, resource dictionaries, application lifetimes, startup configuration, cross-platform project setup, or App.axaml configuration.
---
# Avalonia App Development

## Overview
Avalonia app entry: `Program.cs` builds and runs an `AppBuilder`. `App.axaml` + `App.axaml.cs` is the root. Platform lifetime determines how the app runs (Desktop vs Single-view for mobile/WASM).

## Program.cs
```csharp
using Avalonia;
using Avalonia.ReactiveUI; // or remove if not using ReactiveUI

class Program
{
    [STAThread]
    public static void Main(string[] args) => BuildAvaloniaApp()
        .StartWithClassicDesktopLifetime(args);

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .WithInterFont()
            .LogToTrace();
            // .UseReactiveUI() // add if using ReactiveUI
}
```

## App.axaml
```xml
<Application xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             x:Class="MyApp.App"
             RequestedThemeVariant="Default">
    <Application.DataTemplates>
        <local:ViewLocator/>
    </Application.DataTemplates>
    <Application.Styles>
        <FluentTheme/>
    </Application.Styles>
    <Application.Resources>
        <ResourceDictionary>
            <ResourceDictionary.MergedDictionaries>
                <ResourceInclude Source="avares://MyApp/Assets/Colors.axaml"/>
            </ResourceDictionary.MergedDictionaries>
            <SolidColorBrush x:Key="AccentBrush" Color="#FF5722"/>
        </ResourceDictionary>
    </Application.Resources>
</Application>
```

## App.axaml.cs
```csharp
public partial class App : Application
{
    public override void Initialize() => AvaloniaXamlLoader.Load(this);

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            desktop.MainWindow = new MainWindow
            {
                DataContext = new MainViewModel()
            };
        }
        else if (ApplicationLifetime is ISingleViewApplicationLifetime singleView)
        {
            singleView.MainView = new MainView
            {
                DataContext = new MainViewModel()
            };
        }
        base.OnFrameworkInitializationCompleted();
    }
}
```

## Application Lifetimes
| Lifetime | Interface | Platforms |
|---|---|---|
| Classic Desktop | `IClassicDesktopStyleApplicationLifetime` | Windows, macOS, Linux |
| Single View | `ISingleViewApplicationLifetime` | iOS, Android, WASM |
| Lifetime-less | None | Headless testing |

## Resource Dictionaries
```xml
<!-- Colors.axaml (standalone resource dictionary) -->
<ResourceDictionary xmlns="https://github.com/avaloniaui"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <Color x:Key="PrimaryColor">#FF5722</Color>
    <SolidColorBrush x:Key="PrimaryBrush" Color="{StaticResource PrimaryColor}"/>
    <sys:Double x:Key="DefaultCornerRadius" xmlns:sys="clr-namespace:System;assembly=mscorlib">8</sys:Double>
</ResourceDictionary>
```
Include with:
```xml
<ResourceInclude Source="avares://MyApp/Assets/Colors.axaml"/>
```

## StaticResource vs DynamicResource
| | StaticResource | DynamicResource |
|---|---|---|
| Resolved | Once at load time | On every access |
| Runtime changes | No | Yes |
| Theme variants | No | Yes (required) |
| Performance | Faster | Slightly slower |

Use `DynamicResource` for anything theme-variant-aware. Use `StaticResource` for constants that never change.

## Assets
```xml
<!-- In .csproj -->
<ItemGroup>
    <AvaloniaResource Include="Assets/**"/>
</ItemGroup>
```
Access: `avares://MyApp/Assets/logo.png`

## Cross-Platform Project Structure
```
MyApp/
  MyApp.csproj           — Desktop (Windows/macOS/Linux)
  Program.cs
  App.axaml + .cs
  Views/
  ViewModels/
  Assets/
MyApp.Mobile/            — Optional: iOS/Android
  MyApp.Mobile.csproj
MyApp.Browser/           — Optional: WASM
  MyApp.Browser.csproj
MyApp.Core/              — Shared ViewModels/Models
  MyApp.Core.csproj
```

## Common Mistakes
- Using `StartWithClassicDesktopLifetime` for mobile/WASM (must use `ISingleViewApplicationLifetime`)
- `AvaloniaXamlLoader.Load(this)` missing in `Initialize()` — styles and resources not loaded
- Using `StaticResource` for `ThemeVariant`-sensitive resources — dark mode won't update
- Asset path casing mismatch on Linux (`Assets/Logo.png` vs `assets/logo.png`)
