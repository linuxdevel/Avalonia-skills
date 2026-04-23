---
name: avalonia-data-templates
description: Use when defining DataTemplate, ItemTemplate, ContentTemplate, selecting templates by data type, using TreeDataTemplate for hierarchical data, implementing IDataTemplate selectors, or using FuncDataTemplate in Avalonia. Covers template scoping, app-level templates, and compiled binding in templates.
---

# Avalonia Data Templates

## Overview

DataTemplates define how a data object is rendered as UI. They apply to:
- `ItemsControl` and subclasses (`ListBox`, `TreeView`, `DataGrid`) via `ItemTemplate`
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

`x:DataType` enables compiled bindings inside the template. Every DataTemplate that uses compiled bindings must declare it.

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
    tb.Bind(TextBlock.TextProperty, new Binding(nameof(PersonViewModel.FullName)));
    return tb;
});

myListBox.ItemTemplate = template;
```

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
public class AnimalTreeSelector : IDataTemplate
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

- **Missing `x:DataType` on DataTemplate** — compiled bindings inside the template have no type context and fail to build. Every DataTemplate using `{Binding}` needs `x:DataType`.
- **Wrong resource scope** — a DataTemplate in `Window.Resources` is not visible to templates inside a nested `UserControl`. Each `UserControl` has its own resource scope. Put shared templates in `Application.Resources` or `Application.DataTemplates`.
- **Using `DataTemplate` instead of `TreeDataTemplate` for tree data** — `DataTemplate` renders the node content but does not provide an `ItemsSource` binding for children; `TreeView` will not recurse into children.
- **Matching on interface type** — Avalonia's automatic type-based template selection matches on the **concrete runtime type**, not interfaces. `IDataTemplate.Match()` must explicitly check for the concrete type, or register templates against the concrete type.
- **Multiple templates for same type in same scope** — if two `DataTemplate`s in `Application.DataTemplates` have `x:DataType="vm:PersonViewModel"`, the first one always wins. Remove duplicates or use keyed resources for multiple representations.
- **Circular template reference** — a `DataTemplate` that creates a `ContentControl` whose `Content` binds back to the same ViewModel type causes infinite recursion. Use a keyed template or break the cycle with a wrapper ViewModel.
- **Setting both `ItemTemplate` and using auto-selection** — an explicit `ItemTemplate` always takes precedence over `Application.DataTemplates`. Remove `ItemTemplate` to rely on global auto-selection.
