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
