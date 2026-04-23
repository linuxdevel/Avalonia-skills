---
name: avalonia
description: Use when working with Avalonia UI framework — building, styling, binding, animating, or deploying Avalonia apps with .NET.
---

# Avalonia UI

## Overview
Avalonia is a cross-platform .NET UI framework using XAML (`.axaml`), with its own rendering engine (Skia/Impeller), supporting Windows, macOS, Linux, iOS, Android, and WASM. Avalonia 12 is the current stable version; compiled bindings are enabled by default.

**Rule:** Always load the matching subskill before writing or reviewing Avalonia code.

## Routing Table

| Task | Load subskill |
|---|---|
| XAML markup, .axaml files, namespaces, code-behind | `avalonia-xaml` |
| Panels, Grid, StackPanel, alignment, margins | `avalonia-layout` |
| Styles, control themes, selectors, pseudoclasses, themes | `avalonia-styling` |
| `{Binding}`, compiled bindings, converters, validation | `avalonia-data-binding` |
| DataTemplate, ItemTemplate, template selection | `avalonia-data-templates` |
| MVVM pattern, INotifyPropertyChanged, ICommand, CommunityToolkit | `avalonia-mvvm` |
| Built-in controls (Button, TextBox, DataGrid, etc.) | `avalonia-controls` |
| Custom UserControl, TemplatedControl, drawing controls | `avalonia-custom-controls` |
| Brushes, transforms, animations, transitions | `avalonia-graphics-animation` |
| Pointer, keyboard, gestures, drag-and-drop | `avalonia-input-interaction` |
| StyledProperty, DirectProperty, AttachedProperty | `avalonia-property-system` |
| Routed events, bubbling, tunneling | `avalonia-events` |
| Clipboard, file dialogs, notifications, storage | `avalonia-services` |
| App structure, resource dictionaries, app lifetime | `avalonia-app-development` |
| Headless testing, UI automation | `avalonia-testing` |
| Packaging for macOS/Windows/Linux/WASM | `avalonia-deployment` |
| Migrating from WPF | `avalonia-wpf-migration` |

## Notable Community Packages

A curated short-list of the most commonly needed community packages:

| Need | Package |
|---|---|
| Message box dialogs | `MsgBox.Avalonia` |
| Hot reload during dev | `HotAvalonia` |
| SVG images | `Svg.Skia` |
| Animated GIFs | `AvaloniaGif` |
| Charts | `LiveChartsCore.SkiaSharpView.Avalonia` or `ScottPlot.Avalonia` |
| Code editor control | `AvaloniaEdit` |
| Docking layout | `Dock.Avalonia` |
| Behaviors (DataTrigger replacement) | `Avalonia.Xaml.Behaviors` |
| Node editor | `NodifyAvalonia` (GitHub: BAndysc) |
| Material theme | `Material.Avalonia` |
| Fluent/WinUI controls | `FluentAvalonia` |
| Rich dialog service | `HanumanInstitute.MvvmDialogs.Avalonia` |
| VLC media player | `LibVLCSharp.Avalonia` |
| PDF viewer | `MuPDFCore` |
| Deployment packaging | PupNet Deploy (GitHub: kuiperzone/PupNet-Deploy) |

Full community list: https://github.com/AvaloniaCommunity/awesome-avalonia
