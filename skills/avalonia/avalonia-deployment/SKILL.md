---
name: avalonia-deployment
description: Use when packaging or deploying Avalonia apps for Windows, macOS, Linux, WebAssembly, Android, or iOS.
---
# Avalonia Deployment

## Overview
Avalonia apps are .NET apps — standard `dotnet publish` with `-r <RID>` produces executables. Platform-specific packaging tools handle OS-native bundles.

## Runtime Identifiers (RIDs)
| Platform | RID |
|---|---|
| Windows x64 | `win-x64` |
| Windows ARM64 | `win-arm64` |
| macOS x64 (Intel) | `osx-x64` |
| macOS ARM64 (Apple Silicon) | `osx-arm64` |
| Linux x64 | `linux-x64` |
| Linux ARM64 | `linux-arm64` |

## Target Frameworks
| | 11.3 | 12.0 / 12.1 |
|---|---|---|
| Desktop / shared | `net6.0`+, `netstandard2.0`, .NET Framework | `net8.0` min, `net10.0` recommended (no netstandard/.NET Framework) |
| Android / iOS / Mac Catalyst | `net8.0-android` / `net8.0-ios` etc. | **`net10.0-android` / `net10.0-ios` / `net10.0-maccatalyst`** (required) |
| Browser | `net8.0-browser`+ | `net8.0-browser`+ (`net10.0-browser` recommended) |

Removed in 12: `Avalonia.Browser.Blazor`, `Avalonia.Tizen`, `Avalonia.Direct2D1` (use Skia).

## Basic Publish
```bash
# Self-contained single file (Windows)
dotnet publish -r win-x64 -c Release --self-contained true -p:PublishSingleFile=true

# Framework-dependent (requires .NET installed)
dotnet publish -r win-x64 -c Release --self-contained false
```

## Windows
Options:
1. **MSIX** — Use Visual Studio packaging project or `msix-packaging-tool`
2. **Installer (Inno Setup / WiX)** — point at publish output
3. **Single EXE** — `PublishSingleFile=true` + self-contained

```xml
<!-- .csproj for Windows -->
<PropertyGroup>
    <PublishSingleFile>true</PublishSingleFile>
    <SelfContained>true</SelfContained>
    <RuntimeIdentifier>win-x64</RuntimeIdentifier>
    <IncludeNativeLibrariesForSelfExtract>true</IncludeNativeLibrariesForSelfExtract>
</PropertyGroup>
```

## macOS
```bash
# Publish
dotnet publish -r osx-arm64 -c Release --self-contained true

# Bundle as .app using dotnet-bundle tool:
dotnet tool install --global Dotnet.Bundle
dotnet msbundle -r osx-arm64 /p:CFBundleVersion=1.0.0
```
`Info.plist` properties in `.csproj`:
```xml
<PropertyGroup>
    <CFBundleName>MyApp</CFBundleName>
    <CFBundleIdentifier>com.mycompany.myapp</CFBundleIdentifier>
    <CFBundleVersion>1.0.0</CFBundleVersion>
    <NSHighResolutionCapable>true</NSHighResolutionCapable>
</PropertyGroup>
```
Notarization requires Apple Developer account + `xcrun notarytool`.

## Linux
```bash
# AppImage
dotnet publish -r linux-x64 -c Release --self-contained true
# Then use appimagetool to wrap the publish output

# Debian package (.deb)
dotnet publish -r linux-x64 -c Release
# Use dpkg-deb or dotnet-deb NuGet tool
dotnet tool install --global dotnet-deb
dotnet deb -r linux-x64 -c Release
```

## WebAssembly (WASM)
Separate project (`MyApp.Browser.csproj`):
```xml
<Project Sdk="Microsoft.NET.Sdk.WebAssembly">
    <PropertyGroup>
        <TargetFramework>net10.0-browser</TargetFramework>
        <AllowUnsafeBlocks>true</AllowUnsafeBlocks>
    </PropertyGroup>
    <ItemGroup>
        <PackageReference Include="Avalonia.Browser" Version="12.1.4"/>
    </ItemGroup>
</Project>
```
(11.x) templates used `Microsoft.NET.Sdk.BlazorWebAssembly` / `net8.0`; `Avalonia.Browser.Blazor` is removed in 12. Entry point uses `StartBrowserAppAsync("out")`; App uses `ISingleViewApplicationLifetime` (unchanged in 12).
```bash
dotnet publish -c Release
# Output is static files (wwwroot/) — host on any static server
```

## Android
```xml
<Project Sdk="Microsoft.NET.Sdk">
    <PropertyGroup>
        <TargetFramework>net10.0-android</TargetFramework>  <!-- (11.x) net8.0-android / net9.0-android -->
    </PropertyGroup>
    <ItemGroup>
        <PackageReference Include="Avalonia.Android" Version="12.1.4"/>
    </ItemGroup>
</Project>
```
```bash
dotnet publish -f net10.0-android -c Release
# Produces .apk / .aab (AndroidPackageFormats)
```
Entry (12.0+): `MainActivity : AvaloniaMainActivity` + `[Application] AndroidApp : AvaloniaAndroidApplication<App>`; `App` sets `IActivityApplicationLifetime.MainViewFactory` (see avalonia-app-development). (11.x) `AvaloniaMainActivity<App>` + `ISingleViewApplicationLifetime`.

## iOS / Mac Catalyst
```xml
<TargetFramework>net10.0-ios</TargetFramework>  <!-- (11.x) net8.0-ios / net9.0-ios -->
<PackageReference Include="Avalonia.iOS" Version="12.1.4"/>
```
Requires macOS + Xcode. Produces `.ipa`. iOS uses `ISingleViewApplicationLifetime` and the scene delegate lifecycle (12.0+; `AvaloniaAppDelegate.Window` is null after startup).

**Mac Catalyst (12.0+)** — same `Avalonia.iOS` project, add a target; needs `dotnet workload install maccatalyst`:
```xml
<TargetFrameworks>net10.0-ios;net10.0-maccatalyst</TargetFrameworks>
```
```bash
dotnet build -f net10.0-maccatalyst
```
Prefer the default AppKit macOS backend for new desktop apps; Catalyst is for UIKit-heavy / MAUI-hybrid scenarios.

## Linux Wayland (12.1+, experimental)
Opt-in: add `Avalonia.Wayland` and call `.UseWayland()` on the AppBuilder. `UsePlatformDetect()` does **not** select it; X11 remains default.

## SBOM (12.1+)
Avalonia 12.1.0+ packages ship a Software Bill of Materials listing the framework's NuGet packages (supports CRA/compliance work).

## Trimming
Enable for smaller binaries — may break reflection-heavy code:
```xml
<PublishTrimmed>true</PublishTrimmed>
<TrimmerRootDescriptor>TrimmerRoots.xml</TrimmerRootDescriptor>
```
Watch for reflection in converters, ViewLocator. Compiled bindings (default ON in 12, opt-in in 11) avoid binding reflection and are trim-friendly; reflection bindings (`ReflectionBinding`) are not.

## Community Deployment Tools

| Tool | NuGet / Repo | Purpose |
|---|---|---|
| PupNet Deploy | GitHub: kuiperzone/PupNet-Deploy | Cross-platform deployment: AppImage, Flatpak, deb, rpm, MSIX, zip |
| dotnet-deb | `dotnet-deb` tool | Generate Debian `.deb` packages |
| Dotnet.Bundle | `Dotnet.Bundle` tool | macOS `.app` bundle + DMG creation |
| macOS.SparkleUpdater.Avalonia | GitHub: Deadpikle/macOS.SparkleUpdater.Avalonia | Sparkle auto-update integration for macOS |

### PupNet Quick Start
```bash
dotnet tool install --global KuiperZone.PupNet
pupnet --help

# Build AppImage for Linux
pupnet -r linux-x64 -k AppImage

# Build MSIX for Windows
pupnet -r win-x64 -k Msix

# Build Setup.exe (Inno)
pupnet -r win-x64 -k Setup
```
PupNet reads a `pupnet.conf` in your project root. Handles icon conversion, desktop entries, version injection automatically.

## Common Mistakes
- macOS `.app` bundle missing `NSHighResolutionCapable` → blurry on Retina
- Publishing without `--self-contained` to machines without .NET installed
- WASM project must use `ISingleViewApplicationLifetime`, not `IClassicDesktopStyleApplicationLifetime`
- Android/iOS heads left on `net9.0-*` with Avalonia 12 — needs `net10.0-*`
- Referencing removed packages in 12 (`Avalonia.Browser.Blazor`, `Avalonia.Tizen`, `Avalonia.Direct2D1`)
- Expecting `UsePlatformDetect()` to pick Wayland in 12.1 — requires `Avalonia.Wayland` + `UseWayland()`
- Trimming with ViewLocator using `Type.GetType()` by string → types trimmed away; add trim roots
