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
<Project Sdk="Microsoft.NET.Sdk.BlazorWebAssembly">
    <PropertyGroup>
        <TargetFramework>net9.0</TargetFramework>
    </PropertyGroup>
    <ItemGroup>
        <PackageReference Include="Avalonia.Browser" Version="12.x.x"/>
    </ItemGroup>
</Project>
```
Entry point uses `ISingleViewApplicationLifetime`.
```bash
dotnet publish -r browser-wasm -c Release
# Output is wwwroot/ — host on any static server
```

## Android
```xml
<Project Sdk="Microsoft.NET.Sdk">
    <PropertyGroup>
        <TargetFramework>net9.0-android</TargetFramework>
    </PropertyGroup>
    <ItemGroup>
        <PackageReference Include="Avalonia.Android" Version="12.x.x"/>
    </ItemGroup>
</Project>
```
```bash
dotnet publish -f net9.0-android -c Release
# Produces .apk
```

## iOS
```xml
<TargetFramework>net9.0-ios</TargetFramework>
<PackageReference Include="Avalonia.iOS" Version="12.x.x"/>
```
Requires macOS + Xcode. Produces `.ipa`.

## Trimming
Enable for smaller binaries — may break reflection-heavy code:
```xml
<PublishTrimmed>true</PublishTrimmed>
<TrimmerRootDescriptor>TrimmerRoots.xml</TrimmerRootDescriptor>
```
Avalonia 12 is trim-compatible. Watch for reflection in converters, ViewLocator.

## Common Mistakes
- macOS `.app` bundle missing `NSHighResolutionCapable` → blurry on Retina
- Publishing without `--self-contained` to machines without .NET installed
- WASM project must use `ISingleViewApplicationLifetime`, not `IClassicDesktopStyleApplicationLifetime`
- Trimming with ViewLocator using `Type.GetType()` by string → types trimmed away; add trim roots
