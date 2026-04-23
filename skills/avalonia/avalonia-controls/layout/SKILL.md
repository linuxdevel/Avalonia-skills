---
name: avalonia-controls-layout
description: Use when working with Avalonia layout container controls: Border, ScrollViewer, SplitView, Expander, Viewbox, or Panel variants (Grid, StackPanel, WrapPanel, DockPanel, UniformGrid, Canvas). Covers container-specific API, properties, scroll configuration, and layout pitfalls in Avalonia 12.
---

# Avalonia Layout Controls

## Overview

Layout controls are containers that position and constrain child controls. See `avalonia-layout` for general sizing/alignment concepts. This skill covers the container control APIs.

---

## Border

Single-child container. Adds background, border, rounded corners, padding, and shadows.

| Property | Type | Notes |
|---|---|---|
| `Background` | `IBrush` | Fill color |
| `BorderBrush` | `IBrush` | Border color |
| `BorderThickness` | `Thickness` | `1` or `1,2,1,2` (L,T,R,B) |
| `CornerRadius` | `CornerRadius` | `8` or `8,0,8,0` (TL,TR,BR,BL) |
| `Padding` | `Thickness` | Inner spacing |
| `BoxShadow` | `BoxShadows` | Drop shadow(s) |
| `Child` | `Control` | **Single child only** |

```xml
<!-- Card style -->
<Border Background="White"
        CornerRadius="8"
        BorderBrush="#E0E0E0"
        BorderThickness="1"
        Padding="16"
        BoxShadow="0 2 8 0 #20000000">
    <StackPanel Spacing="8">
        <TextBlock Text="Card Title" FontWeight="SemiBold" FontSize="16"/>
        <TextBlock Text="Card body content goes here." TextWrapping="Wrap"/>
    </StackPanel>
</Border>

<!-- Divider line using Border -->
<Border Height="1" Background="#E0E0E0" Margin="0,8"/>

<!-- Multiple box shadows -->
<Border BoxShadow="0 1 3 0 #1A000000, 0 4 6 0 #0D000000" CornerRadius="6" Padding="12">
    <TextBlock Text="Elevated card"/>
</Border>
```

> **Important:** `Border` only accepts **one child**. Wrap multiple children in a `Panel`, `StackPanel`, or `Grid`.

---

## ScrollViewer

Adds scrollbars to content that overflows its bounds.

| Property | Type | Notes |
|---|---|---|
| `HorizontalScrollBarVisibility` | `ScrollBarVisibility` | `Auto`, `Visible`, `Hidden`, `Disabled` |
| `VerticalScrollBarVisibility` | `ScrollBarVisibility` | `Auto`, `Visible`, `Hidden`, `Disabled` |
| `Offset` | `Vector` | Programmatic scroll position |
| `Extent` | `Size` | Total content size |
| `Viewport` | `Size` | Visible area size |
| `AllowAutoHide` | `bool` | Hides scrollbar when not hovering |
| `HorizontalSnapPointsType` | `SnapPointsType` | Snap behavior |

**ScrollBarVisibility values:**

| Value | Behavior |
|---|---|
| `Auto` | Shows when content overflows |
| `Visible` | Always shown |
| `Hidden` | Never shown, but scrolling still works |
| `Disabled` | Disables scrolling in that direction |

```xml
<!-- Standard vertical scroll -->
<ScrollViewer VerticalScrollBarVisibility="Auto"
              HorizontalScrollBarVisibility="Disabled">
    <StackPanel>
        <!-- many items -->
    </StackPanel>
</ScrollViewer>

<!-- Horizontal scroll (e.g. wide table) -->
<ScrollViewer HorizontalScrollBarVisibility="Auto"
              VerticalScrollBarVisibility="Disabled">
    <Grid Width="1200"><!-- wide content --></Grid>
</ScrollViewer>
```

```csharp
// Programmatic scroll
scrollViewer.Offset = new Vector(0, 500);

// Scroll to end
scrollViewer.ScrollToEnd();

// Subscribe to scroll events
scrollViewer.ScrollChanged += (s, e) =>
{
    bool atBottom = scrollViewer.Offset.Y >= scrollViewer.ScrollBarMaximum.Y;
};
```

> **Pitfall:** `ScrollViewer` inside `StackPanel` never scrolls because `StackPanel` gives infinite height. Fix: use a `Grid` row with `Height="*"` or set an explicit `Height` on the `ScrollViewer`.

---

## SplitView

Two-region layout: a collapsible pane and main content area.

| Property | Type | Notes |
|---|---|---|
| `IsPaneOpen` | `bool` | TwoWay — controls pane visibility |
| `OpenPaneLength` | `double` | Width when expanded |
| `CompactPaneLength` | `double` | Width when compact (icon-only) |
| `DisplayMode` | `SplitViewDisplayMode` | See table below |
| `PanePlacement` | `SplitViewPanePlacement` | `Left` (default), `Right` |
| `Pane` | `object` | Pane content |
| `Content` | `object` | Main content area |

**DisplayMode values:**

| Mode | Behavior |
|---|---|
| `Overlay` | Pane overlaps content when open |
| `Inline` | Pane pushes content when open |
| `CompactOverlay` | Shows `CompactPaneLength` strip; expands over content |
| `CompactInline` | Shows `CompactPaneLength` strip; expands pushing content |

```xml
<SplitView IsPaneOpen="{Binding IsNavOpen}"
           DisplayMode="CompactInline"
           OpenPaneLength="220"
           CompactPaneLength="48">
    <SplitView.Pane>
        <StackPanel Spacing="4" Margin="4">
            <Button Command="{Binding NavHomeCommand}" HorizontalAlignment="Stretch">
                <StackPanel Orientation="Horizontal" Spacing="12">
                    <PathIcon Data="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" Width="20" Height="20"/>
                    <TextBlock Text="Home" VerticalAlignment="Center"/>
                </StackPanel>
            </Button>
            <Button Command="{Binding NavSettingsCommand}" HorizontalAlignment="Stretch">
                <StackPanel Orientation="Horizontal" Spacing="12">
                    <PathIcon Data="M19.14 12.94..." Width="20" Height="20"/>
                    <TextBlock Text="Settings" VerticalAlignment="Center"/>
                </StackPanel>
            </Button>
        </StackPanel>
    </SplitView.Pane>
    <ContentControl Content="{Binding CurrentPage}"/>
</SplitView>
```

> **Note:** `Pane` and `Content` are set via XAML property element syntax, not as items in a `Children` collection.

---

## Expander

Collapsible section with a header.

| Property | Type | Notes |
|---|---|---|
| `Header` | `object` | Always-visible header (string or XAML) |
| `IsExpanded` | `bool` | TwoWay — controls expand state |
| `ExpandDirection` | `ExpandDirection` | `Down` (default), `Up`, `Left`, `Right` |
| `ContentTransition` | `IPageTransition` | Animation for expand/collapse |

```xml
<!-- Basic -->
<Expander Header="Advanced Options" IsExpanded="False">
    <StackPanel Margin="16,8" Spacing="8">
        <CheckBox Content="Enable caching" IsChecked="{Binding UseCache}"/>
        <CheckBox Content="Verbose logging" IsChecked="{Binding VerboseLog}"/>
    </StackPanel>
</Expander>

<!-- Custom header -->
<Expander IsExpanded="{Binding IsExpanded}">
    <Expander.Header>
        <StackPanel Orientation="Horizontal" Spacing="8">
            <PathIcon Data="..." Width="16" Height="16"/>
            <TextBlock Text="Section Title" FontWeight="SemiBold"/>
            <TextBlock Text="{Binding ItemCount, StringFormat='({0} items)'}" Foreground="Gray"/>
        </StackPanel>
    </Expander.Header>
    <ItemsControl ItemsSource="{Binding Items}">
        <ItemsControl.ItemTemplate>
            <DataTemplate x:DataType="vm:ItemVm">
                <TextBlock Text="{Binding Name}" Margin="16,4"/>
            </DataTemplate>
        </ItemsControl.ItemTemplate>
    </ItemsControl>
</Expander>
```

---

## Viewbox

Scales a single child to fill available space while optionally preserving aspect ratio.

| Property | Type | Notes |
|---|---|---|
| `Stretch` | `Stretch` | See table below |
| `StretchDirection` | `StretchDirection` | `Both`, `UpOnly`, `DownOnly` |

**Stretch values:**

| Value | Behavior |
|---|---|
| `None` | No scaling |
| `Fill` | Stretches to fill, ignores aspect ratio |
| `Uniform` | Scales uniformly to fit (default) |
| `UniformToFill` | Scales uniformly to fill, may clip |

```xml
<!-- Scale icon to container -->
<Viewbox Width="48" Height="48" Stretch="Uniform">
    <Canvas Width="24" Height="24">
        <PathIcon Data="M12 2L2 7l10 5 10-5-10-5z" Width="24" Height="24"/>
    </Canvas>
</Viewbox>

<!-- Responsive logo -->
<Viewbox Stretch="Uniform" HorizontalAlignment="Left" Height="40">
    <StackPanel Orientation="Horizontal">
        <Ellipse Width="32" Height="32" Fill="#6200EE"/>
        <TextBlock Text="AppName" FontSize="24" FontWeight="Bold" VerticalAlignment="Center" Margin="8,0,0,0"/>
    </StackPanel>
</Viewbox>
```

---

## Panel Variants Reference

For full layout concepts see `avalonia-layout`. Quick API reference:

### Grid

```xml
<Grid RowDefinitions="Auto,*,Auto" ColumnDefinitions="200,*">
    <TextBlock Grid.Row="0" Grid.Column="0" Text="Label"/>
    <TextBox Grid.Row="0" Grid.Column="1" Text="{Binding Value}"/>
    <Button Grid.Row="2" Grid.Column="1" Content="OK" HorizontalAlignment="Right"/>
</Grid>
```

### StackPanel

| Property | Notes |
|---|---|
| `Orientation` | `Vertical` (default), `Horizontal` |
| `Spacing` | Uniform gap between items |

```xml
<StackPanel Orientation="Horizontal" Spacing="8">
    <Button Content="Cancel"/>
    <Button Content="OK"/>
</StackPanel>
```

### WrapPanel

```xml
<WrapPanel Orientation="Horizontal" ItemWidth="120" ItemHeight="80">
    <!-- items wrap to next row when out of space -->
</WrapPanel>
```

### DockPanel

```xml
<DockPanel LastChildFill="True">
    <Menu DockPanel.Dock="Top"/>
    <StatusBar DockPanel.Dock="Bottom"/>
    <TreeView DockPanel.Dock="Left" Width="200"/>
    <ContentControl/><!-- fills remaining space -->
</DockPanel>
```

### UniformGrid

```xml
<UniformGrid Rows="2" Columns="3">
    <!-- 6 equal cells -->
</UniformGrid>
```

### Canvas

```xml
<Canvas Width="400" Height="300">
    <Rectangle Canvas.Left="50" Canvas.Top="50" Width="100" Height="80" Fill="Blue"/>
    <Ellipse Canvas.Left="200" Canvas.Top="100" Width="60" Height="60" Fill="Red"/>
</Canvas>
```

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Multiple children inside `Border` | Wrap in `StackPanel` or `Grid` — `Border.Child` accepts exactly one element |
| `ScrollViewer` inside `StackPanel` not scrolling | `StackPanel` gives infinite height; use `Grid` with `Height="*"` row or set explicit height on `ScrollViewer` |
| `SplitView` Pane content not showing | Set via `<SplitView.Pane>` property element, not as a child item |
| `Expander` header cut off | Set `MinHeight` on `Expander` or ensure parent doesn't constrain height to 0 |
| `Viewbox` making content blurry | `Viewbox` uses bitmap scaling for raster content; use vector (`PathIcon`, `Canvas` paths) for crisp results |
| `Canvas` not respecting size in layout | `Canvas` reports desired size as 0×0 by default; set explicit `Width`/`Height` on the `Canvas` element |
| `Grid` items overlapping | Every child needs explicit `Grid.Row`/`Grid.Column`; without them all go to row 0, col 0 |
