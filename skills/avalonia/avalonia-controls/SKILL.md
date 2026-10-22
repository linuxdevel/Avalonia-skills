---
name: avalonia-controls
description: Use when working with built-in Avalonia controls (11.3, 12.0, 12.1). Routes to the correct sub-subskill for input, data display (ItemsControl/ListBox/TableView/DataGrid/TreeView), layout (incl. GroupBox), navigation (incl. page-based Navigation/Drawer/TabbedPage, CommandBar, PipsPager) and media (Image, NativeWebView) controls.
---

# Avalonia Controls

## Overview

Avalonia ships 60+ built-in controls organized by category. Load the sub-subskill for the relevant control category. Labels like (12.0+), (12.1+), (11.x) follow the convention in `avalonia-versions`; unlabelled means all versions.

## Routing Table

| Controls | Load sub-subskill |
|---|---|
| Button, ToggleButton, RadioButton, CheckBox, TextBox (`PlaceholderText` 12.0+, was `Watermark`), AutoCompleteBox, ComboBox, Slider, Calendar, CalendarDatePicker, DatePicker, NumericUpDown | `avalonia-controls/input` |
| TextBlock, Label, ItemsControl, ListBox, TableView (12.1+), DataGrid (maintenance-only package), TreeView, TreeDataGrid (commercial), Carousel | `avalonia-controls/data-display` |
| Border, ScrollViewer, Grid, StackPanel, WrapPanel, DockPanel, UniformGrid, SplitView, Expander, GroupBox (12.0+) | `avalonia-controls/layout` |
| TabControl, Menu, ContextMenu, Flyout, NativeMenu, NativeDock.Menu (12.0+), TrayIcon, NavigationPage / DrawerPage / TabbedPage / ContentPage / CarouselPage / CommandBar (12.0+), PipsPager (12.0+) | `avalonia-controls/navigation` |
| Image, DrawingImage (`Viewbox` 12.0+), NativeWebView / NativeWebDialog (12.0+, `Avalonia.Controls.WebView`) | `avalonia-controls/media` |

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
| Markdown.Avalonia | `Markdown.Avalonia` | Markdown renderer control (no `MarkdownViewer` in core) |
| GMap.NET | `GMap.NET.Avalonia` | Maps (Google, OpenStreetMap, etc.) |
| CherylUI | GitHub: kikipoulet/CherylUI | Mobile-focused control library |
