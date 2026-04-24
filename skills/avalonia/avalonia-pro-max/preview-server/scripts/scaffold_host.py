#!/usr/bin/env python3
"""
scaffold_host.py

Creates the .preview/AvaloniaPreviewHost/ scratch project used by render_variants.py
to render Avalonia variant XAML to PNG via Avalonia.Headless + Skia.

Idempotent — safe to re-run. Skips if the project already exists with a valid csproj.

Usage:
    python3 scaffold_host.py [--root <project_root>] [--avalonia-version 12.0.0] [--force]
"""
from __future__ import annotations

import argparse
import os
import sys
import textwrap
from pathlib import Path

DEFAULT_AVALONIA_VERSION = "12.0.0"

CSPROJ_TEMPLATE = """\
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <LangVersion>latest</LangVersion>
    <ApplicationManifest>app.manifest</ApplicationManifest>
    <AvaloniaUseCompiledBindingsByDefault>true</AvaloniaUseCompiledBindingsByDefault>
    <RootNamespace>AvaloniaPreviewHost</RootNamespace>
    <AssemblyName>AvaloniaPreviewHost</AssemblyName>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Avalonia" Version="{ver}" />
    <PackageReference Include="Avalonia.Themes.Fluent" Version="{ver}" />
    <PackageReference Include="Avalonia.Skia" Version="{ver}" />
    <PackageReference Include="Avalonia.Headless" Version="{ver}" />
    <PackageReference Include="Avalonia.Desktop" Version="{ver}" />
  </ItemGroup>

  <ItemGroup>
    <AvaloniaResource Include="Variant\\**" />
  </ItemGroup>

</Project>
"""

APP_AXAML = """\
<Application xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             x:Class="AvaloniaPreviewHost.App"
             RequestedThemeVariant="Default">

  <Application.Styles>
    <FluentTheme />
    <StyleInclude Source="avares://AvaloniaPreviewHost/Variant/Styles.axaml" />
  </Application.Styles>

  <Application.Resources>
    <ResourceDictionary>
      <ResourceDictionary.MergedDictionaries>
        <ResourceInclude Source="avares://AvaloniaPreviewHost/Variant/Resources.axaml" />
      </ResourceDictionary.MergedDictionaries>
    </ResourceDictionary>
  </Application.Resources>

</Application>
"""

APP_AXAML_CS = """\
using Avalonia;
using Avalonia.Markup.Xaml;

namespace AvaloniaPreviewHost;

public partial class App : Application
{
    public override void Initialize() => AvaloniaXamlLoader.Load(this);
}
"""

PROGRAM_CS = """\
// CLI: AvaloniaPreviewHost --variant <N> --viewport <wide|compact|phone|tablet> --theme <light|dark> --out <path>
using System;
using System.IO;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Markup.Xaml;
using Avalonia.Media.Imaging;
using Avalonia.Styling;
using Avalonia.Threading;

namespace AvaloniaPreviewHost;

public static class Program
{
    public static int Main(string[] args)
    {
        var opts = ParseArgs(args);
        if (opts is null) return 64;

        AppBuilder
            .Configure<App>()
            .UseHeadless(new AvaloniaHeadlessPlatformOptions { UseHeadlessDrawing = false })
            .UseSkia()
            .SetupWithoutStarting();

        return Dispatcher.UIThread.Invoke(() =>
        {
            try
            {
                Application.Current!.RequestedThemeVariant =
                    opts.Theme.Equals("dark", StringComparison.OrdinalIgnoreCase)
                        ? ThemeVariant.Dark
                        : ThemeVariant.Light;

                var content = (Control)AvaloniaXamlLoader.Load(
                    new Uri("avares://AvaloniaPreviewHost/Variant/PreviewScene.axaml"));

                var window = new Window
                {
                    Width = opts.Width,
                    Height = opts.Height,
                    SystemDecorations = SystemDecorations.None,
                    Content = content
                };
                window.Show();

                // Force two layout passes so transitions/initial state settle.
                window.Measure(new Avalonia.Size(opts.Width, opts.Height));
                window.Arrange(new Avalonia.Rect(0, 0, opts.Width, opts.Height));
                Dispatcher.UIThread.RunJobs();
                window.Measure(new Avalonia.Size(opts.Width, opts.Height));
                window.Arrange(new Avalonia.Rect(0, 0, opts.Width, opts.Height));
                Dispatcher.UIThread.RunJobs();

                var px = new PixelSize(opts.Width, opts.Height);
                using var bmp = new RenderTargetBitmap(px, new Vector(96, 96));
                bmp.Render(window);

                Directory.CreateDirectory(Path.GetDirectoryName(opts.Output)!);
                bmp.Save(opts.Output);

                Console.WriteLine($"Rendered {opts.Output}");
                return 0;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("Render failed: " + ex);
                return 1;
            }
        });
    }

    private record Options(int Variant, string Viewport, string Theme, int Width, int Height, string Output);

    private static Options? ParseArgs(string[] args)
    {
        int variant = 1;
        string viewport = "wide", theme = "light", output = "preview.png";
        for (int i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--variant":  variant  = int.Parse(args[++i]); break;
                case "--viewport": viewport = args[++i]; break;
                case "--theme":    theme    = args[++i]; break;
                case "--out":      output   = args[++i]; break;
                default:
                    Console.Error.WriteLine($"Unknown arg: {args[i]}");
                    return null;
            }
        }
        var (w, h) = viewport switch
        {
            "wide"    => (1280, 800),
            "compact" => (800,  600),
            "phone"   => (390,  844),
            "tablet"  => (1024, 1366),
            _         => (1280, 800)
        };
        return new Options(variant, viewport, theme, w, h, output);
    }
}
"""

APP_MANIFEST = """\
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity version="1.0.0.0" name="AvaloniaPreviewHost.app"/>
</assembly>
"""

PLACEHOLDER_RESOURCES = """\
<ResourceDictionary xmlns="https://github.com/avaloniaui"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"/>
"""

PLACEHOLDER_STYLES = """\
<Styles xmlns="https://github.com/avaloniaui"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"/>
"""

PLACEHOLDER_SCENE = """\
<UserControl xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             x:Class="AvaloniaPreviewHost.PlaceholderScene">
  <TextBlock Text="No variant loaded"
             HorizontalAlignment="Center"
             VerticalAlignment="Center"/>
</UserControl>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold the Avalonia preview host project.")
    parser.add_argument("--root", default=".", help="Project root (defaults to cwd)")
    parser.add_argument("--avalonia-version", default=DEFAULT_AVALONIA_VERSION)
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    host = root / ".preview" / "AvaloniaPreviewHost"
    csproj = host / "AvaloniaPreviewHost.csproj"

    if csproj.exists() and not args.force:
        print(f"Host already scaffolded at {host}. Use --force to overwrite.")
        _ensure_gitignore(root)
        return 0

    host.mkdir(parents=True, exist_ok=True)
    (host / "Variant").mkdir(exist_ok=True)

    files = {
        csproj:                       CSPROJ_TEMPLATE.format(ver=args.avalonia_version),
        host / "App.axaml":           APP_AXAML,
        host / "App.axaml.cs":        APP_AXAML_CS,
        host / "Program.cs":          PROGRAM_CS,
        host / "app.manifest":        APP_MANIFEST,
        host / "Variant" / "Resources.axaml":     PLACEHOLDER_RESOURCES,
        host / "Variant" / "Styles.axaml":        PLACEHOLDER_STYLES,
        host / "Variant" / "PreviewScene.axaml":  PLACEHOLDER_SCENE,
    }
    for path, content in files.items():
        path.write_text(content)
        print(f"  wrote {path.relative_to(root)}")

    _ensure_gitignore(root)
    print()
    print(f"Scaffolded host at {host}")
    print("Next: write your variants under .preview/variants/{1,2,3}/ and run render_variants.py")
    return 0


def _ensure_gitignore(root: Path) -> None:
    gi = root / ".gitignore"
    line = ".preview/"
    if gi.exists():
        existing = gi.read_text().splitlines()
        if line not in existing and ".preview" not in existing:
            with gi.open("a") as f:
                f.write(f"\n{line}\n")
            print(f"  appended {line} to .gitignore")
    else:
        gi.write_text(f"{line}\n")
        print("  created .gitignore with .preview/")


if __name__ == "__main__":
    sys.exit(main())
