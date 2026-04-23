---
name: avalonia-layout
description: Use when arranging controls in Avalonia using panels, Grid, StackPanel, DockPanel, Canvas, alignment, margins, padding, or responsive layouts.
---

# Avalonia Layout

## Overview
Avalonia layout uses a two-pass measure/arrange system. Every control has `Margin` (space outside the control), `Padding` (space inside), `HorizontalAlignment`, and `VerticalAlignment`. Layout is done with `Panel` subclasses — choose the panel that matches the arrangement model.

## Panel Quick Reference

| Panel | Arranges children | Use when |
|---|---|---|
| `Grid` | In defined rows/columns | Complex layouts, forms, dashboards |
| `StackPanel` | Linearly (H or V) | Toolbars, lists, vertical forms |
| `WrapPanel` | Linearly, wraps to next row/col | Tag clouds, icon grids, badge lists |
| `DockPanel` | Docked to edges + fill center | App shell, menu+content+statusbar |
| `Canvas` | Absolute x/y positions | Drawing surfaces, overlays, diagrams |
| `UniformGrid` | Equal-size cells, auto rows/cols | Grids of same-size items |
| `RelativePanel` | Relative to siblings or panel | Adaptive layouts, dynamic alignment |

## Grid

### Sizing Modes

| Syntax | Meaning |
|---|---|
| `*` | Proportional — takes remaining space |
| `2*` | Takes 2× the share of `*` |
| `Auto` | Sized to content |
| `200` | Fixed pixel size |

### Basic Grid

```xml
<Grid RowDefinitions="Auto,*,Auto"
      ColumnDefinitions="200,*">

    <!-- Header spans full width -->
    <Border Grid.Row="0" Grid.ColumnSpan="2" Background="Navy" Height="50"/>

    <!-- Sidebar -->
    <ListBox Grid.Row="1" Grid.Column="0"/>

    <!-- Main content -->
    <ScrollViewer Grid.Row="1" Grid.Column="1">
        <StackPanel Margin="16" Spacing="8"/>
    </ScrollViewer>

    <!-- Footer spans full width -->
    <StatusBar Grid.Row="2" Grid.ColumnSpan="2"/>

</Grid>
```

### Login Form Example

```xml
<Grid RowDefinitions="Auto,Auto,Auto,Auto"
      ColumnDefinitions="120,*"
      Width="320"
      HorizontalAlignment="Center"
      VerticalAlignment="Center">

    <TextBlock Grid.Row="0" Grid.Column="0"
               Text="Username:"
               VerticalAlignment="Center"
               Margin="0,0,8,8"/>
    <TextBox Grid.Row="0" Grid.Column="1"
             Margin="0,0,0,8"/>

    <TextBlock Grid.Row="1" Grid.Column="0"
               Text="Password:"
               VerticalAlignment="Center"
               Margin="0,0,8,8"/>
    <TextBox Grid.Row="1" Grid.Column="1"
             PasswordChar="●"
             Margin="0,0,0,16"/>

    <Button Grid.Row="2" Grid.Column="0" Grid.ColumnSpan="2"
            Content="Sign In"
            HorizontalAlignment="Right"/>

</Grid>
```

### SharedSizeGroup

Keeps columns at equal widths across separate Grids:

```xml
<StackPanel Grid.IsSharedSizeScope="True">
    <Grid ColumnDefinitions="Auto,*">
        <TextBlock Grid.Column="0"
                   Text="First Name:"
                   SharedSizeGroup="Labels"/>
        <TextBox Grid.Column="1"/>
    </Grid>
    <Grid ColumnDefinitions="Auto,*">
        <TextBlock Grid.Column="0"
                   Text="Email Address:"
                   SharedSizeGroup="Labels"/>
        <TextBox Grid.Column="1"/>
    </Grid>
</StackPanel>
```

## StackPanel

```xml
<!-- Vertical (default) with spacing -->
<StackPanel Spacing="8" Margin="16">
    <Button Content="First"/>
    <Button Content="Second"/>
    <Button Content="Third"/>
</StackPanel>

<!-- Horizontal toolbar -->
<StackPanel Orientation="Horizontal" Spacing="4">
    <Button Content="New"/>
    <Button Content="Open"/>
    <Separator/>
    <Button Content="Save"/>
</StackPanel>
```

`Spacing` was added in Avalonia 11. Do not use `Margin` on each child for spacing — use `Spacing` on the panel.

## DockPanel

```xml
<DockPanel LastChildFill="True">

    <!-- Top menu bar -->
    <Menu DockPanel.Dock="Top">
        <MenuItem Header="File"/>
    </Menu>

    <!-- Bottom status bar -->
    <StatusBar DockPanel.Dock="Bottom">
        <TextBlock Text="Ready"/>
    </StatusBar>

    <!-- Left sidebar -->
    <TreeView DockPanel.Dock="Left" Width="200"/>

    <!-- Center fills remaining space (LastChildFill) -->
    <TextEditor/>

</DockPanel>
```

Dock order matters: elements are docked in the order they appear. The last child fills remaining space when `LastChildFill="True"` (default).

## Canvas

```xml
<Canvas Width="400" Height="300">
    <!-- Positioned absolutely -->
    <Rectangle Canvas.Left="50" Canvas.Top="30"
               Width="100" Height="60"
               Fill="CornflowerBlue"/>

    <Ellipse Canvas.Left="200" Canvas.Top="100"
             Width="80" Height="80"
             Fill="Tomato"
             ZIndex="1"/>

    <TextBlock Canvas.Right="10" Canvas.Bottom="10"
               Text="Bottom-right anchor"/>
</Canvas>
```

`Canvas.Left`/`Top`/`Right`/`Bottom` are attached properties. Use `ZIndex` to control paint order.

## Alignment & Spacing Reference

### HorizontalAlignment / VerticalAlignment

| Value | Behavior |
|---|---|
| `Stretch` (default) | Fills available space |
| `Left` / `Top` | Aligns to start edge |
| `Center` | Centers in available space |
| `Right` / `Bottom` | Aligns to end edge |

### Margin / Padding Syntax

| Syntax | Meaning |
|---|---|
| `"8"` | All four sides = 8 |
| `"8,4"` | Left+Right=8, Top+Bottom=4 |
| `"8,4,8,4"` | Left=8, Top=4, Right=8, Bottom=4 |

```xml
<!-- Uniform -->
<Button Margin="8" Content="A"/>

<!-- Horizontal, Vertical -->
<Button Margin="16,8" Content="B"/>

<!-- Left, Top, Right, Bottom -->
<Button Margin="16,8,0,8" Content="C"/>
```

### Size Constraints

```xml
<TextBox Width="200"
         MinWidth="100"
         MaxWidth="400"
         Height="32"/>
```

Avoid setting both `Width` and `HorizontalAlignment="Stretch"` — they conflict. Use one or the other.

## Responsive Layouts

### Proportional Grid (Most Common)

```xml
<!-- Two-column layout: sidebar + content -->
<Grid ColumnDefinitions="250,*">
    <NavigationPane Grid.Column="0"/>
    <ContentArea Grid.Column="1"/>
</Grid>
```

### Adaptive Layout with ContainerQuery (Avalonia 12)

```xml
<Grid>
    <Grid.Styles>
        <Style Selector="Grid">
            <Style.Resources>
                <ControlTheme x:Key="AdaptiveLayout" TargetType="Grid">
                    <!-- Wide: two columns -->
                    <Setter Property="ColumnDefinitions" Value="*,*"/>
                </ControlTheme>
            </Style.Resources>
        </Style>
    </Grid.Styles>
</Grid>
```

For truly responsive behavior, use code-behind or reactive bindings that respond to `Bounds` changes:

```csharp
// In code-behind
this.GetObservable(BoundsProperty)
    .Subscribe(bounds =>
    {
        if (bounds.Width < 600)
        {
            mainGrid.ColumnDefinitions = new ColumnDefinitions("*");
            // move items to single column
        }
        else
        {
            mainGrid.ColumnDefinitions = new ColumnDefinitions("*,*");
        }
    });
```

### ScrollViewer for Overflow

```xml
<ScrollViewer HorizontalScrollBarVisibility="Disabled"
              VerticalScrollBarVisibility="Auto">
    <StackPanel Spacing="8" Margin="16">
        <!-- content taller than viewport -->
    </StackPanel>
</ScrollViewer>
```

## Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| `Canvas` inside `StackPanel` with no explicit size | Canvas children invisible (zero height/width) | Set explicit `Width`/`Height` on the `Canvas` |
| `*` sizing inside `StackPanel` | Star column/row collapses | `StackPanel` gives infinite space — `*` has no bound. Use `Grid` instead. |
| Forgetting `LastChildFill="False"` in `DockPanel` | Last element stretches unexpectedly | Add `LastChildFill="False"` and size last child explicitly |
| `Margin` on root element of `UserControl` | Outer margin bleeds outside control bounds | Use `Padding` on the `UserControl` root, not `Margin` |
| `HorizontalAlignment="Stretch"` with explicit `Width` | Width is ignored or conflicted | Remove explicit `Width` or change alignment to `Left`/`Right` |
| Dock order mistakes in `DockPanel` | Elements appear in wrong positions | Dock elements in correct top→bottom order; last undocked child fills |
| Setting `Height="Auto"` on `StackPanel` | No effect — `StackPanel` is always `Auto` height by default | Remove redundant property; set explicit height on parent if constraint needed |
| Nested `ScrollViewer` without fixed outer height | Inner scroll never activates | Ensure outer container has a bounded height (`Height`, `MaxHeight`, or star row in `Grid`) |
