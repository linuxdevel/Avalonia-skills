---
name: avalonia-controls-data-display
description: Use when working with Avalonia data display controls: TextBlock, Label, ListBox, DataGrid, TreeView, ItemsControl, Carousel, or MarkdownViewer. Covers binding patterns, templates, virtualization, selection modes, and column configuration for Avalonia 12.
---

# Avalonia Data Display Controls

## Overview

Data display controls render read-only or selectable information. Prefer `ItemsControl` for simple lists, `ListBox` when selection is needed, `DataGrid` for tabular data, and `TreeView` for hierarchical data.

---

## TextBlock

| Property | Type | Notes |
|---|---|---|
| `Text` | `string` | Plain text content |
| `FontSize` | `double` | In device-independent pixels |
| `FontWeight` | `FontWeight` | `Normal`, `Bold`, `SemiBold`, etc. |
| `FontStyle` | `FontStyle` | `Normal`, `Italic`, `Oblique` |
| `TextWrapping` | `TextWrapping` | `NoWrap`, `Wrap`, `WrapWithOverflow` |
| `TextTrimming` | `TextTrimming` | `None`, `CharacterEllipsis`, `WordEllipsis` |
| `TextDecorations` | `TextDecorationCollection` | `Underline`, `Strikethrough` |
| `LineHeight` | `double` | Line spacing |
| `MaxLines` | `int` | Clamps number of displayed lines |
| `Inlines` | `InlineCollection` | Mixed-format inline content |

```xml
<!-- Basic -->
<TextBlock Text="{Binding Title}" FontSize="18" FontWeight="SemiBold"/>

<!-- Trimming with ellipsis -->
<TextBlock Text="{Binding Description}" TextTrimming="CharacterEllipsis" MaxWidth="300"/>

<!-- Inline formatting -->
<TextBlock>
    <Run FontWeight="Bold">Important:</Run>
    <Run> This is </Run>
    <Run Foreground="Red" FontStyle="Italic">critical</Run>
    <LineBreak/>
    <Run Text="{Binding Detail}"/>
</TextBlock>

<!-- Underline + strikethrough -->
<TextBlock Text="Strike me" TextDecorations="Strikethrough"/>
<TextBlock Text="Link-style" TextDecorations="Underline" Cursor="Hand"/>
```

---

## Label

| Property | Type | Notes |
|---|---|---|
| `Content` | `object` | Text or XAML content |
| `Target` | `IInputElement` | Associates access key with target control |

Use `_` prefix in content to define an access key (Alt+key focuses `Target`).

```xml
<Label Content="_Username" Target="{Binding #usernameBox}"/>
<TextBox x:Name="usernameBox" Text="{Binding Username}"/>

<Label Content="_Password" Target="{Binding #passwordBox}"/>
<TextBox x:Name="passwordBox" PasswordChar="•" Text="{Binding Password}"/>
```

> **Note:** `Label` adds padding and is a `ContentControl`. For pure display, prefer `TextBlock`.

---

## ItemsControl

Base class for all list controls. Use directly when no selection is needed.

| Property | Type | Notes |
|---|---|---|
| `ItemsSource` | `IEnumerable` | Bound collection |
| `ItemTemplate` | `DataTemplate` | Template for each item |
| `ItemsPanel` | `ItemsPanelTemplate` | Layout panel (default: `StackPanel`) |
| `ItemContainerTheme` | `ControlTheme` | Style for each container |

```xml
<!-- Simple read-only list -->
<ItemsControl ItemsSource="{Binding Tags}">
    <ItemsControl.ItemTemplate>
        <DataTemplate x:DataType="vm:TagVm">
            <Border Background="#E3F2FD" CornerRadius="4" Padding="8,4" Margin="0,0,4,4">
                <TextBlock Text="{Binding Name}" FontSize="12"/>
            </Border>
        </DataTemplate>
    </ItemsControl.ItemTemplate>
    <!-- Horizontal wrapping layout -->
    <ItemsControl.ItemsPanel>
        <ItemsPanelTemplate>
            <WrapPanel Orientation="Horizontal"/>
        </ItemsPanelTemplate>
    </ItemsControl.ItemsPanel>
</ItemsControl>
```

---

## ListBox

Extends `ItemsControl` with selection. Virtualizes items by default.

| Property | Type | Notes |
|---|---|---|
| `SelectedItem` | `object` | TwoWay by default |
| `SelectedItems` | `IList` | Multiple selection (requires `SelectionMode` flag) |
| `SelectedIndex` | `int` | Zero-based index |
| `SelectionMode` | `SelectionMode` | `Single`, `Multiple`, `Toggle`, `AlwaysSelected` |
| `Scroll` | `ScrollViewer` | Access the internal scroll viewer |

```xml
<ListBox ItemsSource="{Binding People}"
         SelectedItem="{Binding SelectedPerson}"
         SelectionMode="Single">
    <ListBox.ItemTemplate>
        <DataTemplate x:DataType="vm:PersonVm">
            <StackPanel Margin="4">
                <TextBlock Text="{Binding FullName}" FontWeight="SemiBold"/>
                <TextBlock Text="{Binding Email}" FontSize="12" Foreground="Gray"/>
            </StackPanel>
        </DataTemplate>
    </ListBox.ItemTemplate>
</ListBox>

<!-- Multi-select -->
<ListBox ItemsSource="{Binding Files}"
         SelectionMode="Multiple,Toggle"
         SelectedItems="{Binding SelectedFiles}">
    <ListBox.ItemTemplate>
        <DataTemplate x:DataType="vm:FileVm">
            <TextBlock Text="{Binding Name}"/>
        </DataTemplate>
    </ListBox.ItemTemplate>
</ListBox>
```

---

## DataGrid

Requires separate NuGet package: `Avalonia.Controls.DataGrid`

Add to `App.axaml` styles:
```xml
<StyleInclude Source="avares://Avalonia.Controls.DataGrid/Themes/Fluent.xaml"/>
```

Namespace: `xmlns:dg="using:Avalonia.Controls"`

| Property | Type | Notes |
|---|---|---|
| `ItemsSource` | `IEnumerable` | Bound collection |
| `AutoGenerateColumns` | `bool` | False for manual columns |
| `CanUserSortColumns` | `bool` | Click-to-sort |
| `CanUserResizeColumns` | `bool` | Drag column edges |
| `CanUserReorderColumns` | `bool` | Drag column headers |
| `GridLinesVisibility` | `DataGridGridLinesVisibility` | `All`, `Horizontal`, `Vertical`, `None` |
| `FrozenColumnCount` | `int` | Columns that don't scroll |
| `RowBackground` | `IBrush` | Row fill |
| `AlternatingRowBackground` | `IBrush` | Alternating fill |
| `SelectedItem` | `object` | TwoWay |
| `SelectionMode` | `DataGridSelectionMode` | `Single`, `Extended` |

**Column types:**

| Type | Use for |
|---|---|
| `DataGridTextColumn` | String/primitive display |
| `DataGridCheckBoxColumn` | Boolean values |
| `DataGridTemplateColumn` | Custom cell content |

```xml
<DataGrid ItemsSource="{Binding Employees}"
          AutoGenerateColumns="False"
          CanUserSortColumns="True"
          CanUserResizeColumns="True"
          GridLinesVisibility="Horizontal"
          AlternatingRowBackground="#F5F5F5"
          SelectedItem="{Binding SelectedEmployee}">
    <DataGrid.Columns>
        <DataGridTextColumn Header="Name" Binding="{Binding Name}" Width="*"/>
        <DataGridTextColumn Header="Department" Binding="{Binding Department}" Width="Auto"/>
        <DataGridTextColumn Header="Salary" Binding="{Binding Salary, StringFormat=C2}" Width="100"/>
        <DataGridCheckBoxColumn Header="Active" Binding="{Binding IsActive}" Width="60"/>
        <DataGridTemplateColumn Header="Actions" Width="80">
            <DataGridTemplateColumn.CellTemplate>
                <DataTemplate>
                    <Button Content="Edit"
                            Command="{Binding $parent[DataGrid].DataContext.EditCommand}"
                            CommandParameter="{Binding}"
                            Padding="8,4"/>
                </DataTemplate>
            </DataGridTemplateColumn.CellTemplate>
        </DataGridTemplateColumn>
    </DataGrid.Columns>
</DataGrid>
```

> **Note:** DataGrid column `Binding` always uses reflection bindings (`{Binding ...}`), even when the page uses compiled bindings. `x:DataType` on `DataTemplate` inside columns is not supported.

---

## TreeView

| Property | Type | Notes |
|---|---|---|
| `ItemsSource` | `IEnumerable` | Root nodes |
| `ItemTemplate` | `TreeDataTemplate` | **Must** use `TreeDataTemplate` for hierarchy |
| `SelectedItem` | `object` | TwoWay |
| `AutoScrollToSelectedItem` | `bool` | Scrolls to selection |

`TreeDataTemplate` has an `ItemsSource` property that points to each node's children collection.

```xml
<TreeView ItemsSource="{Binding RootNodes}"
          SelectedItem="{Binding SelectedNode}"
          AutoScrollToSelectedItem="True">
    <TreeView.ItemTemplate>
        <TreeDataTemplate x:DataType="vm:TreeNodeVm" ItemsSource="{Binding Children}">
            <StackPanel Orientation="Horizontal" Spacing="6">
                <PathIcon Data="{Binding IconData}" Width="14" Height="14"/>
                <TextBlock Text="{Binding Name}"/>
            </StackPanel>
        </TreeDataTemplate>
    </TreeView.ItemTemplate>
</TreeView>
```

```csharp
public class TreeNodeVm
{
    public string Name { get; set; } = "";
    public string IconData { get; set; } = "";
    public ObservableCollection<TreeNodeVm> Children { get; } = new();
}
```

---

## Carousel

Displays one item at a time with animated transitions. Useful for image galleries, onboarding flows, or wizard steps.

| Property | Type | Notes |
|---|---|---|
| `ItemsSource` | `IEnumerable` | Bound collection |
| `SelectedIndex` | `int` | TwoWay |
| `SelectedItem` | `object` | TwoWay |
| `PageTransition` | `IPageTransition` | Animation between items |
| `IsVirtualized` | `bool` | Only renders visible item |

**Built-in transitions:** `PageSlide`, `CrossFade`, `CompositePageTransition`

```xml
<Carousel ItemsSource="{Binding Slides}"
          SelectedIndex="{Binding CurrentIndex}"
          IsVirtualized="True">
    <Carousel.PageTransition>
        <PageSlide Duration="0:0:0.4" Orientation="Horizontal"/>
    </Carousel.PageTransition>
    <Carousel.ItemTemplate>
        <DataTemplate x:DataType="vm:SlideVm">
            <Border Background="{Binding BackgroundColor}">
                <TextBlock Text="{Binding Title}" HorizontalAlignment="Center"
                           VerticalAlignment="Center" FontSize="24"/>
            </Border>
        </DataTemplate>
    </Carousel.ItemTemplate>
</Carousel>

<!-- Navigation buttons -->
<StackPanel Orientation="Horizontal" HorizontalAlignment="Center">
    <Button Content="◀" Command="{Binding PreviousCommand}"/>
    <TextBlock Text="{Binding CurrentIndex}" VerticalAlignment="Center" Margin="16,0"/>
    <Button Content="▶" Command="{Binding NextCommand}"/>
</StackPanel>
```

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| `DataGrid` not styled / missing | Add `Avalonia.Controls.DataGrid` NuGet and include `Fluent.xaml` style |
| `DataGrid` column `Binding` with `x:DataType` | Not supported in columns — use reflection `{Binding}`, not compiled |
| `TreeView` using plain `DataTemplate` | Use `TreeDataTemplate` with `ItemsSource` pointing to children; plain `DataTemplate` won't expand |
| `ListBox.SelectedItems` always empty | Requires `SelectionMode="Multiple"` (or `Toggle`) to populate |
| `ItemsControl` inside `ScrollViewer` inside `StackPanel` | `StackPanel` gives infinite height — items render but `ScrollViewer` won't scroll. Use `Grid` row with `*` height |
| `Carousel` flickering on fast navigation | Set `IsVirtualized="True"` and use `CrossFade` instead of `PageSlide` for smoother transitions |
| `TextBlock` not trimming | `TextTrimming` requires a `MaxWidth` constraint or a parent that constrains width |
