---
name: avalonia-controls-data-display
description: Use when working with Avalonia data display controls: TextBlock, Label, ItemsControl, ListBox, TableView (12.1+), DataGrid (maintenance mode), TreeDataGrid (commercial), TreeView, or Carousel. Includes a decision table for choosing a list/grid control, compiled-binding rules for DataGrid/TableView columns, touch/pen selection behavior, and Carousel swipe/wrap (12.0+). Note there is no built-in MarkdownViewer; use Markdown.Avalonia. Covers Avalonia 11.3, 12.0 and 12.1.
---

# Avalonia Data Display Controls

## Overview

Data display controls render read-only or selectable information. Pick by need:

| Need | Control | Availability |
|---|---|---|
| Simple repeated items, no selection | `ItemsControl` | all |
| Selectable list, custom item layout | `ListBox` | all |
| **Read-only table**: columns over a collection, no editing (virtualized, row/cell recycling) | `TableView` | **12.1+** (core `Avalonia` package) |
| Editable/sortable/grouped grid | `DataGrid` | `Avalonia.Controls.DataGrid` package, MIT. **Maintenance mode** (bug fixes only) since 12.1 — fine for existing apps and 11.x/12.0, don't pick for new read-only grids on 12.1+ |
| Tree + table, advanced editing, hierarchical grid | `TreeDataGrid` | `Avalonia.Controls.TreeDataGrid` package. **Commercial: requires an Avalonia Accelerate/Pro license** (since 11.2); versions independently (12.x line targets Avalonia 12) |
| Hierarchy, single column | `TreeView` | all |

> There is **no `MarkdownViewer` in Avalonia core**. Use the community `Markdown.Avalonia` package (or `LiveMarkdown.Avalonia`).

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

> **12.0+ behavior:** touch/pen selection happens on pointer **release** (swipe/scroll no longer selects). `ListBoxItem` and `TreeViewItem` handle selection themselves — to customize, override `ShouldTriggerSelection` / `UpdateSelectionFromEvent` rather than intercepting at the `ListBox`/`TreeView` level. `UpdateSelection` / `UpdateSelectionFromEventSource` are obsolete.

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

## TableView (12.1+)

Read-only tabular control (like WPF `GridView`) in the **core `Avalonia` package**, namespace `Avalonia.Controls` — no extra package or style include. Built on `ListBox` (selection, virtualization), recycles rows and cells. Not in 11.x or 12.0 → use `DataGrid` there. No editing, no sorting/grouping built in; for that use `DataGrid`/`TreeDataGrid`.

| `TableView` | Type | Notes |
|---|---|---|
| `ItemsSource` | `IEnumerable` | Rows (inherited from `ItemsControl`) |
| `Columns` | `AvaloniaList<TableViewColumn>` | Define in XAML |
| `CanUserResizeColumns` | `bool` | Drag header separators; per-column override via `CanUserResize` |

| `TableViewColumn` | Type | Notes |
|---|---|---|
| `Header` / `HeaderTemplate` | `object` / `IDataTemplate` | Header content |
| `Binding` | `BindingBase` | Cell value from row item, e.g. `{Binding Name}` |
| `CellTemplate` | `IDataTemplate` | Whole row item is the data context; **takes priority over `Binding`** |
| `Width` | `GridLength` | Pixel (`120`), star (`*`, `2*`), `Auto` |
| `HorizontalContentAlignment` | `HorizontalAlignment` | Cell content alignment |
| `CanUserResize` | `bool?` | `null` = follow `TableView.CanUserResizeColumns` |
| `IsVisible` | `bool` | Default `true` |
| `HeaderTheme` / `CellTheme` | `ControlTheme` | Must target `TableViewColumnHeader` / `TableViewCell` |
| `ActualWidth` | `double` | `NaN` until measured |

```xml
<TableView ItemsSource="{Binding Employees}"
           SelectedItem="{Binding SelectedEmployee}"
           CanUserResizeColumns="True">
    <TableView.Columns>
        <TableViewColumn Header="Name"   Binding="{Binding Name}"   Width="2*"/>
        <TableViewColumn Header="Dept"   Binding="{Binding Department}" Width="*"/>
        <TableViewColumn Header="Salary" Binding="{Binding Salary, StringFormat=C2}"
                         Width="100" HorizontalContentAlignment="Right"/>
        <TableViewColumn Header="Status" Width="Auto">
            <TableViewColumn.CellTemplate>
                <DataTemplate x:DataType="vm:EmployeeVm">
                    <TextBlock Text="{Binding Status}"/>
                </DataTemplate>
            </TableViewColumn.CellTemplate>
        </TableViewColumn>
    </TableView.Columns>
</TableView>
```

> Compiled bindings (default in 12): `Binding` on a column is compiled against the inferred data type. If the compiler infers the window/VM type instead of the row type, set it explicitly: `Binding="{Binding Name, DataType={x:Type vm:EmployeeVm}}"` (same applies to `DataGridTextColumn`). `x:DataType` inside a `CellTemplate` works because the row item is its data context.

---

## DataGrid

Requires separate NuGet package: `Avalonia.Controls.DataGrid` (MIT; own repo and version line — use the release matching your core version, e.g. 12.1.x needs Avalonia >= 12.1.0).

> **Maintenance mode (12.1+):** "deprecated and only receives bug fixes". For new **read-only** grids on 12.1+ prefer `TableView`; for advanced editing/hierarchical data, `TreeDataGrid` (commercial). Existing DataGrid code keeps working in 11.3 / 12.0 / 12.1.

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

> **Bindings in columns:** column `Binding` is **not** reflection-only. In **12.x** compiled bindings are the default, so `{Binding Name}` in a `DataGridTextColumn` is compiled against the type inferred from `ItemsSource` (when it's a `{Binding}` in the same XAML) — otherwise the compiler may pick the window/VM type and fail with `AVLN2000`. Fix: `Binding="{Binding Name, DataType={x:Type vm:EmployeeVm}}"` (or `x:DataType` on the column), or `{ReflectionBinding Name}` as a fallback. In **11.x** compiled bindings are opt-in; column bindings behave as reflection unless `x:CompileBindings`/`CompiledBinding` is used. `x:DataType` on the `DataTemplate` inside `DataGridTemplateColumn.CellTemplate` is fine (row item is the data context).

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
| `IsSwipeEnabled` | `bool` | Swipe between items **(12.0+)**; also accepts mouse input |
| `WrapSelection` | `bool` | Wrap from last to first and back **(12.0+)** |
| `ViewportFraction` | `double` | Fraction of viewport per item; `<1` shows neighbours **(12.0+)** |
| `Next()` / `Previous()` | methods | Programmatic navigation |
| `IsVirtualized` | `bool` | **(11.x)** only renders visible item — not listed in the 12 API reference |

**Built-in transitions:** `PageSlide`, `CrossFade`, `CompositePageTransition`

```xml
<Carousel ItemsSource="{Binding Slides}"
          SelectedIndex="{Binding CurrentIndex}"
          IsSwipeEnabled="True" WrapSelection="True">
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
| `DataGrid`/`TableView` column fails with `AVLN2000` (12.x) | Compiled binding inferred the wrong type — add `DataType={x:Type vm:RowVm}` inside the `Binding`, or use `{ReflectionBinding}` |
| New read-only grid built with `DataGrid` on 12.1+ | `DataGrid` is in maintenance mode — use `TableView` (12.1+) |
| `TableView` in 12.0/11.x project | Doesn't exist before 12.1 — use `DataGrid` |
| `<MarkdownViewer>` | Not an Avalonia control — add `Markdown.Avalonia` |
| `TreeDataGrid` added without license | Package requires an Avalonia Accelerate license — check before choosing it |
| Touch selection logic at `ListBox` level | 12.0+: `ListBoxItem`/`TreeViewItem` handle selection on pointer release; override `ShouldTriggerSelection` |
| `TreeView` using plain `DataTemplate` | Use `TreeDataTemplate` with `ItemsSource` pointing to children; plain `DataTemplate` won't expand |
| `ListBox.SelectedItems` always empty | Requires `SelectionMode="Multiple"` (or `Toggle`) to populate |
| `ItemsControl` inside `ScrollViewer` inside `StackPanel` | `StackPanel` gives infinite height — items render but `ScrollViewer` won't scroll. Use `Grid` row with `*` height |
| `Carousel` flickering on fast navigation | Use `CrossFade` instead of `PageSlide` (and `IsVirtualized="True"` in 11.x) |
| `Carousel` swipe/wrap not working | `IsSwipeEnabled` / `WrapSelection` are 12.0+; set them explicitly |
| `TextBlock` not trimming | `TextTrimming` requires a `MaxWidth` constraint or a parent that constrains width |
