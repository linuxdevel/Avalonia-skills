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
// using ReactiveUI.Avalonia;  // (12.0+) ReactiveUI.Avalonia package — only if using ReactiveUI
// using Avalonia.ReactiveUI;  // (11.x) Avalonia.ReactiveUI package, last release 11.3.x

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
            // .UseReactiveUI(_ => { }).RegisterReactiveUIViewsFromEntryAssembly() // (12.0+) ReactiveUI.Avalonia
            // .UseReactiveUI() // (11.x) Avalonia.ReactiveUI
}
```
`UsePlatformDetect()` configures Skia + HarfBuzz. With explicit `.UseSkia()` in 12, also call `.UseHarfBuzz()` (`Avalonia.HarfBuzz` package) or startup throws `No text shaping system configured`. (12.0+)

Dev tools: `Avalonia.Diagnostics` + `AttachDevTools()` (11.x) → `AvaloniaUI.DiagnosticsSupport` package + `AttachDeveloperTools()` in `App.OnFrameworkInitializationCompleted` (12.0+).

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
        else if (ApplicationLifetime is IActivityApplicationLifetime activity) // (12.0+) Android
        {
            activity.MainViewFactory = () => new MainView { DataContext = new MainViewModel() };
        }
        else if (ApplicationLifetime is ISingleViewApplicationLifetime singleView) // iOS, Browser (and Android in 11.x)
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
Check `IActivityApplicationLifetime` **before** `ISingleViewApplicationLifetime`. In 11.x omit the activity branch (`IActivityApplicationLifetime` does not exist).

### Android entry (12.0+)
```csharp
[Activity(Label = "MyApp", Theme = "@style/MyTheme.NoActionBar", MainLauncher = true,
    ConfigurationChanges = ConfigChanges.Orientation | ConfigChanges.ScreenSize | ConfigChanges.UiMode)]
public class MainActivity : AvaloniaMainActivity { }

[Application]
public class AndroidApp : AvaloniaAndroidApplication<App>
{
    protected AndroidApp(IntPtr javaReference, JniHandleOwnership transfer)
        : base(javaReference, transfer) { }
    // builder customization (e.g. AndroidPlatformOptions): override CustomizeAppBuilder here
}
```
(11.x) `public class MainActivity : AvaloniaMainActivity<App>` with `CustomizeAppBuilder(AppBuilder)` override in the activity; no `[Application]` class. `CreateAppBuilder`/`CustomizeAppBuilder` on `AvaloniaMainActivity` are removed in 12 — move logic to the `AvaloniaAndroidApplication<TApp>` subclass or `App`.

## Application Lifetimes
| Lifetime | Interface | Platforms |
|---|---|---|
| Classic Desktop | `IClassicDesktopStyleApplicationLifetime` | Windows, macOS, Linux |
| Activity | `IActivityApplicationLifetime` (`MainViewFactory`) (12.0+) | Android |
| Single View | `ISingleViewApplicationLifetime` | iOS, WASM (also Android in 11.x) |
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

## Community Libraries & Tooling

### Dependency Injection / Hosting
| Library | NuGet | Purpose |
|---|---|---|
| Lemon.Hosting.Avaloniaui | `Lemon.Hosting.Avaloniaui` | .NET Generic Host integration for Avalonia |
| Prism.Avalonia | `Prism.Avalonia` | IoC, modules, regions, navigation |
| AvaloniaInside.Shell | GitHub: AvaloniaInside/Shell | Shell navigation + side menu for mobile/desktop |

### Hot Reload / Dev Tools
| Tool | NuGet / Repo | Purpose |
|---|---|---|
| HotAvalonia | `HotAvalonia` | Hot reload for AXAML without restart |
| Live.Avalonia | GitHub: worldbeater/Live.Avalonia | Live reloading for development |
| Avant Garde | GitHub: kuiperzone/AvantGarde | Standalone cross-platform XAML previewer |
| DevTools for Avalonia | devtools.nlnet.net | Enhanced runtime inspector and debugger |

### Localization
| Library | NuGet | Purpose |
|---|---|---|
| Echoes | GitHub: Voyonic-Systems/Echoes | Simple type-safe translations/i18n |

### Misc
- **ShowMeTheXaml.Avalonia** — display corresponding XAML at runtime for demos/docs (`ShowMeTheXaml.Avalonia`)
- **Verify.Avalonia** — extends Verify for Avalonia headless UI snapshot testing (`Verify.Avalonia`)
- **Sortable.Avalonia** — animated drag-drop sort behavior attachments (`sortable-avalonia`)
- **AsyncImageLoader.Avalonia** — async image loading from web for Image controls (`AsyncImageLoader.Avalonia`)

## Common Mistakes
- Using `StartWithClassicDesktopLifetime` for mobile/WASM (use `IActivityApplicationLifetime` on Android 12+, `ISingleViewApplicationLifetime` on iOS/Browser)
- Android 12+: still using `AvaloniaMainActivity<App>` / `CustomizeAppBuilder` on the activity / `singleView.MainView` — silently no main view or build errors
- Keeping `Avalonia.ReactiveUI` or `Avalonia.Diagnostics` after upgrading to 12 — packages end at 11.3.x; use `ReactiveUI.Avalonia` / `AvaloniaUI.DiagnosticsSupport`
- Explicit `UseSkia()` without `UseHarfBuzz()` in 12 — startup exception
- `new DispatcherTimer()` created off the UI thread in 12 — binds to the current thread's dispatcher; create on UI thread or pass the dispatcher
- `AvaloniaXamlLoader.Load(this)` missing in `Initialize()` — styles and resources not loaded
- Using `StaticResource` for `ThemeVariant`-sensitive resources — dark mode won't update
- Asset path casing mismatch on Linux (`Assets/Logo.png` vs `assets/logo.png`)
