---
name: avalonia-data-templates
description: Use when defining DataTemplate, ItemTemplate, ContentTemplate, selecting templates by data type, using TreeDataTemplate for hierarchical data, implementing IDataTemplate selectors, or using FuncDataTemplate in Avalonia. Covers template scoping, app-level templates, and compiled bindings in templates (default in 12.0+, so `x:DataType` is required; `{ReflectionBinding}` as opt-out), including TableView/DataGrid column templates.
---

# Avalonia Data Templates

## Overview

DataTemplates define how a data object is rendered as UI. They apply to:
- `ItemsControl` and subclasses (`ListBox`, `TreeView`) via `ItemTemplate`
- `TableViewColumn.CellTemplate` (12.1+) and DataGrid template columns (see Column Templates below)
- `ContentControl` and subclasses via `ContentTemplate`
- Any `Content` property — Avalonia walks up the template tree to find a matching `DataTemplate`

Template matching is by the data object's **runtime type**. First matching template in scope wins.

---

## Inline DataTemplate

```xml
<ListBox ItemsSource="{Binding People}">
    <ListBox.ItemTemplate>
        <DataTemplate x:DataType="vm:PersonViewModel">
            <StackPanel Orientation="Horizontal" Spacing="8">
                <TextBlock Text="{Binding FirstName}"/>
                <TextBlock Text="{Binding LastName}"/>
            </StackPanel>
        </DataTemplate>
    </ListBox.ItemTemplate>
</ListBox>
```

`x:DataType` enables compiled bindings inside the template.

> **12.0+:** compiled bindings are the **default** (`AvaloniaUseCompiledBindingsByDefault` is on in new templates), so every `{Binding}` needs a known `x:DataType` or the build fails (AVLN2000). For genuinely dynamic data use `{ReflectionBinding Path}`. **11.x:** compiled bindings are opt-in (`x:CompileBindings="True"` / the MSBuild property); without it `{Binding}` is reflection-based. See `avalonia-versions`.

---

## ContentControl with DataTemplate

```xml
<ContentControl Content="{Binding CurrentPage}">
    <ContentControl.ContentTemplate>
        <DataTemplate x:DataType="vm:HomeViewModel">
            <views:HomeView/>
        </DataTemplate>
    </ContentControl.ContentTemplate>
</ContentControl>
```

For multi-page navigation, app-level templates (see below) are more practical than per-ContentControl templates.

---

## App-Level Templates (Global Auto-Selection)

In `App.axaml`, templates registered here apply everywhere in the application. Avalonia automatically uses the matching template when a ViewModel type appears as `Content` or as an item.

```xml
<Application.DataTemplates>
    <DataTemplate x:DataType="vm:HomeViewModel">
        <views:HomeView/>
    </DataTemplate>
    <DataTemplate x:DataType="vm:SettingsViewModel">
        <views:SettingsView/>
    </DataTemplate>
    <DataTemplate x:DataType="vm:PersonViewModel">
        <StackPanel>
            <TextBlock Text="{Binding FullName}" FontWeight="Bold"/>
            <TextBlock Text="{Binding Email}"/>
        </StackPanel>
    </DataTemplate>
</Application.DataTemplates>
```

With this setup, a `ContentControl` binding to a ViewModel just works:
```xml
<!-- Automatically renders the right view -->
<ContentControl Content="{Binding ActivePage}"/>
```

---

## Template Scope Resolution Order

Avalonia searches for a matching DataTemplate in this order:
1. `ContentControl.ContentTemplate` or `ItemsControl.ItemTemplate` (explicit, highest priority)
2. `Control.DataTemplates` on the control itself
3. `DataTemplates` in parent controls, walking up the logical tree
4. `Application.DataTemplates` (global fallback)

First match wins. Order within a collection matters — put more specific types before base types.

---

## DataTemplate Type Selector (IDataTemplate)

For conditional template selection based on runtime type or property values, implement `IDataTemplate`:

```csharp
public class AnimalTemplateSelector : IDataTemplate
{
    // Set these from XAML
    public IDataTemplate? DogTemplate { get; set; }
    public IDataTemplate? CatTemplate { get; set; }

    public Control? Build(object? param) => param switch
    {
        Dog d => DogTemplate?.Build(d),
        Cat c => CatTemplate?.Build(c),
        _ => new TextBlock { Text = $"Unknown: {param}" }
    };

    public bool Match(object? data) => data is Dog or Cat;
}
```

```xml
<Window.Resources>
    <local:AnimalTemplateSelector x:Key="AnimalSelector">
        <local:AnimalTemplateSelector.DogTemplate>
            <DataTemplate x:DataType="vm:Dog">
                <TextBlock Text="{Binding Breed}"/>
            </DataTemplate>
        </local:AnimalTemplateSelector.DogTemplate>
        <local:AnimalTemplateSelector.CatTemplate>
            <DataTemplate x:DataType="vm:Cat">
                <TextBlock Text="{Binding Color}"/>
            </DataTemplate>
        </local:AnimalTemplateSelector.CatTemplate>
    </local:AnimalTemplateSelector>
</Window.Resources>

<ItemsControl ItemsSource="{Binding Animals}"
              ItemTemplate="{StaticResource AnimalSelector}"/>
```

---

## FuncDataTemplate (Code-Only)

Useful in code-behind, custom controls, or when XAML is impractical:

```csharp
// Simple
var template = new FuncDataTemplate<PersonViewModel>((person, _) =>
    new TextBlock { Text = person.FullName });

// With bindings
var template = new FuncDataTemplate<PersonViewModel>((person, scope) =>
{
    var tb = new TextBlock();
    // 12.0+: compiled binding from a lambda (no reflection)
    tb.Bind(TextBlock.TextProperty,
        CompiledBinding.Create((PersonViewModel p) => p.FullName));
    // 11.x idiom / reflection fallback: new Binding(nameof(PersonViewModel.FullName))
    // 12: new ReflectionBinding(nameof(PersonViewModel.FullName))
    return tb;
});

myListBox.ItemTemplate = template;
```

---

## Column Templates (TableView 12.1+, DataGrid)

```xml
<!-- TableView (12.1+) -->
<TableView ItemsSource="{Binding People}">
    <TableView.Columns>
        <TableViewColumn Header="Name" Binding="{Binding Name}"/>
        <TableViewColumn Header="Status">
            <TableViewColumn.CellTemplate>
                <DataTemplate x:DataType="vm:PersonViewModel">
                    <TextBlock Text="{Binding Status}"/>
                </DataTemplate>
            </TableViewColumn.CellTemplate>
        </TableViewColumn>
    </TableView.Columns>
</TableView>
```

`CellTemplate` takes priority over `Binding`. DataGrid (`Avalonia.Controls.DataGrid`, maintenance-only) uses `DataGridTemplateColumn.CellTemplate` the same way. Column `Binding`s are compiled in 12: the row type is inferred from `ItemsSource` when possible; otherwise set it explicitly with `Binding="{Binding Name, DataType={x:Type vm:PersonViewModel}}"` or fall back to `{ReflectionBinding Name}`. See `avalonia-controls/data-display`.

---

## Reusable Templates as Resources

Define once, reference many times:

```xml
<Window.Resources>
    <DataTemplate x:Key="PersonCard" x:DataType="vm:PersonViewModel">
        <Border BorderThickness="1" CornerRadius="4" Padding="8">
            <StackPanel>
                <TextBlock Text="{Binding FullName}" FontWeight="Bold"/>
                <TextBlock Text="{Binding Email}" Foreground="Gray"/>
            </StackPanel>
        </Border>
    </DataTemplate>
</Window.Resources>

<!-- Use by key -->
<ListBox ItemsSource="{Binding People}"
         ItemTemplate="{StaticResource PersonCard}"/>

<ContentControl Content="{Binding SelectedPerson}"
                ContentTemplate="{StaticResource PersonCard}"/>
```

---

## TreeDataTemplate (Hierarchical / TreeView)

`TreeDataTemplate` extends `DataTemplate` with an `ItemsSource` binding for child nodes:

```xml
<TreeView ItemsSource="{Binding RootNodes}">
    <TreeView.ItemTemplate>
        <TreeDataTemplate x:DataType="vm:TreeNode"
                          ItemsSource="{Binding Children}">
            <StackPanel Orientation="Horizontal" Spacing="4">
                <Image Source="{Binding Icon}" Width="16" Height="16"/>
                <TextBlock Text="{Binding Name}"/>
            </StackPanel>
        </TreeDataTemplate>
    </TreeView.ItemTemplate>
</TreeView>
```

ViewModel:
```csharp
public class TreeNode
{
    public string Name { get; set; } = "";
    public IImage? Icon { get; set; }
    public ObservableCollection<TreeNode> Children { get; } = new();
}
```

Mixed types in a tree (files and folders):
```csharp
public class NodeTemplateSelector : IDataTemplate
{
    public Control? Build(object? param) => param switch
    {
        FolderNode => /* build folder template */,
        FileNode => /* build file template */,
        _ => null
    };
    public bool Match(object? data) => data is FolderNode or FileNode;
}
```

---

## ItemsControl Panel Customization

Change the layout panel used to arrange items:

```xml
<!-- Wrap panel for wrapping items -->
<ItemsControl ItemsSource="{Binding Tags}">
    <ItemsControl.ItemsPanel>
        <ItemsPanelTemplate>
            <WrapPanel Orientation="Horizontal"/>
        </ItemsPanelTemplate>
    </ItemsControl.ItemsPanel>
    <ItemsControl.ItemTemplate>
        <DataTemplate x:DataType="vm:TagViewModel">
            <Border Background="#E0E0E0" CornerRadius="12" Padding="8,4">
                <TextBlock Text="{Binding Label}"/>
            </Border>
        </DataTemplate>
    </ItemsControl.ItemTemplate>
</ItemsControl>

<!-- Uniform grid -->
<ItemsControl>
    <ItemsControl.ItemsPanel>
        <ItemsPanelTemplate>
            <UniformGrid Columns="3"/>
        </ItemsPanelTemplate>
    </ItemsControl.ItemsPanel>
</ItemsControl>
```

---

## Design-Time Data in Templates

```xml
<ListBox ItemsSource="{Binding People}">
    <Design.DataContext>
        <vm:MainViewModelDesign/>
    </Design.DataContext>
    <ListBox.ItemTemplate>
        <DataTemplate x:DataType="vm:PersonViewModel">
            <TextBlock Text="{Binding FullName}"/>
        </DataTemplate>
    </ListBox.ItemTemplate>
</ListBox>
```

---

## Common Mistakes

- **Missing `x:DataType` on DataTemplate** — in 12.0+ (compiled bindings default) the build fails (AVLN2000) without a type context; in 11.x with compiled bindings enabled it fails the same way. Every DataTemplate using `{Binding}` needs `x:DataType`, or use `{ReflectionBinding}`.
- **`new Binding(...)` in C# templates (12.0+)** — the 11.x idiom is gone from the compiled-by-default model; use `CompiledBinding.Create` or `ReflectionBinding`.
- **Binding plugins like `{Binding ^Stream}` (12.0+)** — plugins were removed; see `avalonia-versions` for replacements.
- **Wrong resource scope** — a DataTemplate in `Window.Resources` is not visible to templates inside a nested `UserControl`. Each `UserControl` has its own resource scope. Put shared templates in `Application.Resources` or `Application.DataTemplates`.
- **Using `DataTemplate` instead of `TreeDataTemplate` for tree data** — `DataTemplate` renders the node content but does not provide an `ItemsSource` binding for children; `TreeView` will not recurse into children.
- **Matching on interface type** — Avalonia's automatic type-based template selection matches on the **concrete runtime type**, not interfaces. `IDataTemplate.Match()` must explicitly check for the concrete type, or register templates against the concrete type.
- **Multiple templates for same type in same scope** — if two `DataTemplate`s in `Application.DataTemplates` have `x:DataType="vm:PersonViewModel"`, the first one always wins. Remove duplicates or use keyed resources for multiple representations.
- **Circular template reference** — a `DataTemplate` that creates a `ContentControl` whose `Content` binds back to the same ViewModel type causes infinite recursion. Use a keyed template or break the cycle with a wrapper ViewModel.
- **Setting both `ItemTemplate` and using auto-selection** — an explicit `ItemTemplate` always takes precedence over `Application.DataTemplates`. Remove `ItemTemplate` to rely on global auto-selection.
