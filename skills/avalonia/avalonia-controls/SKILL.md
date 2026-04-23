---
name: avalonia-controls
description: Use when working with built-in Avalonia controls. Routes to the correct sub-subskill for the control category needed.
---

# Avalonia Controls

## Overview

Avalonia ships 60+ built-in controls organized by category. Load the sub-subskill for the relevant control category.

## Routing Table

| Controls | Load sub-subskill |
|---|---|
| Button, ToggleButton, RadioButton, CheckBox, TextBox, ComboBox, Slider, Calendar, DatePicker, NumericUpDown | `avalonia-controls/input` |
| TextBlock, Label, ListBox, DataGrid, TreeView, Carousel, MarkdownViewer | `avalonia-controls/data-display` |
| Border, ScrollViewer, Grid, StackPanel, WrapPanel, DockPanel, UniformGrid, SplitView, Expander | `avalonia-controls/layout` |
| TabControl, Menu, ContextMenu, CommandBar, TrayIcon | `avalonia-controls/navigation` |
| Image, DrawingImage, MediaPlayerControl, WebView | `avalonia-controls/media` |

## Community Control Libraries

For controls beyond the built-ins, these libraries are widely used:

| Library | NuGet | Highlights |
|---|---|---|
| FluentAvalonia | `FluentAvalonia` | WinUI3-style controls (NavigationView, InfoBar, TeachingTip, etc.) |
| Ursa.Avalonia | `Irihi.Ursa` | Full-featured cross-platform UI control set |
| SukiUI | `SukiUI` | Flat-design controls and dialogs |
| AvaloniaEdit | `AvaloniaEdit` | Code editor with syntax highlighting (port of AvalonEdit) |
| DialogHost.Avalonia | `DialogHost.Avalonia` | Managed async overlay dialogs |
| MessageBox.Avalonia | `MsgBox.Avalonia` | Simple message box dialogs |
| AvaloniaColorPicker | `AvaloniaColorPicker` | RGB/HSB/CIELAB color picker |
| PanAndZoom | `PanAndZoom` | Pan and zoom container control |
| AvaloniaHex | `AvaloniaHex` | Hex editor control |
| RangeSlider | `Avalonia.RangeSlider` | Dual-handle range slider |
| Tabalonia | `Tabalonia` | Draggable tab control |
| AvaloniaAutoGrid | `AvaloniaAutoGrid` | Auto-sizing Grid replacement |
| AvaloniaProgressRing | `AvaloniaProgressRing` | Circular progress ring |
| Paginator.Avalonia | `AvaloniaUtils.Paginator` | Pagination control |
| NodifyAvalonia | GitHub: BAndysc/nodify-avalonia | Node-based editor controls |
| Dock | `Dock.Avalonia` | VS-style docking layout |
| LiveCharts2 | `LiveChartsCore.SkiaSharpView.Avalonia` | Interactive charts and gauges |
| OxyPlot | `OxyPlot.Avalonia` | Scientific/engineering plots |
| ScottPlot | `ScottPlot.Avalonia` | Fast interactive data plots |
| Markdown.Avalonia | `Markdown.Avalonia` | Markdown renderer control |
| GMap.NET | `GMap.NET.Avalonia` | Maps (Google, OpenStreetMap, etc.) |
| CherylUI | GitHub: kikipoulet/CherylUI | Mobile-focused control library |
