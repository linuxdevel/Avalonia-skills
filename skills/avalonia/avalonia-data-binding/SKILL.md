---
name: avalonia-data-binding
description: Use when writing data bindings, compiled bindings, converters, MultiBinding, collection views, validation, or binding to commands in Avalonia. Covers binding modes, path syntax, DataContext, built-in and custom converters, FallbackValue, DataValidationException, and debugging techniques.
---

# Avalonia Data Binding

## Overview

Avalonia 12: compiled bindings are **on by default**. The root element implicitly has `x:CompileBindings="true"`. Compiled bindings are verified at build time, require `x:DataType`, and generate no reflection overhead. Reflection bindings remain available per-binding with `x:CompileBindings=False`.

---

## Binding Modes

| Mode | Direction | Updates |
|---|---|---|
| `OneWay` | Source → Target | On source change |
| `TwoWay` | Source ↔ Target | On either change |
| `OneTime` | Source → Target | Once at bind time |
| `OneWayToSource` | Target → Source | On target change |
| `Default` | Per-property default | Typically `TwoWay` for input controls, `OneWay` for display |

---

## Basic Binding Syntax

```xml
<!-- Compiled binding — requires x:DataType on scope root -->
<Window xmlns:vm="using:MyApp.ViewModels"
        x:DataType="vm:MainViewModel">
    <TextBox Text="{Binding Name}"/>
    <TextBlock Text="{Binding Name, Mode=OneWay}"/>
    <TextBlock Text="{Binding Name, StringFormat='Hello, {0}!'}"/>
</Window>

<!-- Opt out per-binding (reflection binding) -->
<TextBox Text="{Binding Name, x:CompileBindings=False}"/>

<!-- Explicit compiled binding syntax (same as default in Avalonia 12) -->
<TextBox Text="{CompiledBinding Name}"/>
```

---

## Binding Path Syntax

| Syntax | Meaning |
|---|---|
| `{Binding Name}` | Property on DataContext |
| `{Binding Address.Street}` | Nested property path |
| `{Binding [0]}` | Indexer |
| `{Binding [key]}` | Dictionary indexer |
| `{Binding .}` | DataContext itself |
| `{Binding #controlName.Property}` | Named control in same scope |
| `{Binding $parent.Property}` | Nearest parent control |
| `{Binding $parent[Window].Property}` | Nearest parent of type `Window` |
| `{Binding $parent[1].Property}` | Parent N levels up |
| `{Binding $self.Property}` | The control itself |
| `{Binding $root.Property}` | Root of logical tree |

---

## DataContext

Inherits down the logical tree. Child controls automatically receive the parent DataContext unless overridden.

```xml
<!-- Set in XAML -->
<Window DataContext="{x:Static vm:DesignData.Main}"
        x:DataType="vm:MainViewModel">

<!-- Design-time only data context -->
<Design.DataContext>
    <vm:MainViewModelDesign/>
</Design.DataContext>
```

```csharp
// Set in code-behind
public MainWindow()
{
    InitializeComponent();
    DataContext = new MainViewModel();
}
```

`x:DataType` informs the compiler what type the DataContext is. Required for every scope (Window, UserControl, DataTemplate) that uses compiled bindings.

---

## Converters

### Built-in (namespace `Avalonia.Data.Converters`)

| Converter | Usage |
|---|---|
| `BooleanToVisibilityConverter` | `bool` → `IsVisible` (rarely needed; bind `IsVisible` to `bool` directly) |
| `StringConverters.IsNullOrEmpty` | `string` → `bool` |
| `StringConverters.IsNotNullOrEmpty` | `string` → `bool` |
| `ObjectConverters.IsNull` | `object` → `bool` |
| `ObjectConverters.IsNotNull` | `object` → `bool` |
| `FuncValueConverter<TIn,TOut>` | Inline lambda converter |

```xml
<TextBlock IsVisible="{Binding Name, Converter={x:Static StringConverters.IsNotNullOrEmpty}}"/>
```

### FuncValueConverter (inline, no class needed)

```csharp
// In ViewModel or resource file
public static readonly FuncValueConverter<int, string> CountToLabel =
    new(count => count == 1 ? "item" : "items");
```

```xml
<TextBlock Text="{Binding Count, Converter={x:Static vm:Converters.CountToLabel}}"/>
```

### Custom IValueConverter

```csharp
public class InverseBoolConverter : IValueConverter
{
    public static readonly InverseBoolConverter Instance = new();

    public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        => value is bool b ? !b : BindingOperations.DoNothing;

    public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => Convert(value, targetType, parameter, culture);
}
```

```xml
<!-- Register as resource -->
<Window.Resources>
    <converters:InverseBoolConverter x:Key="InverseBool"/>
</Window.Resources>

<Button IsEnabled="{Binding IsBusy, Converter={StaticResource InverseBool}}"/>
```

### Converter with Parameter

```xml
<TextBlock Text="{Binding Price, Converter={StaticResource CurrencyConverter}, ConverterParameter=USD}"/>
```

---

## MultiBinding

```xml
<TextBlock>
    <TextBlock.Text>
        <MultiBinding StringFormat="{}{0} {1}">
            <Binding Path="FirstName"/>
            <Binding Path="LastName"/>
        </MultiBinding>
    </TextBlock.Text>
</TextBlock>
```

With a custom `IMultiValueConverter`:
```csharp
public class FullNameConverter : IMultiValueConverter
{
    public object? Convert(IList<object?> values, Type targetType, object? parameter, CultureInfo culture)
        => values is [string first, string last] ? $"{first} {last}" : null;
}
```

---

## FallbackValue and TargetNullValue

```xml
<!-- TargetNullValue: shown when binding value is null -->
<TextBlock Text="{Binding Description, TargetNullValue='No description'}"/>

<!-- FallbackValue: shown when binding fails entirely (path missing, exception) -->
<Image Source="{Binding AvatarUrl, FallbackValue={StaticResource DefaultAvatar}}"/>
```

---

## Binding to Collections

```xml
<ListBox ItemsSource="{Binding Items}"/>
<DataGrid ItemsSource="{Binding Items}"/>
```

For sorting and filtering, use `DataGridCollectionView`:
```csharp
var view = new DataGridCollectionView(myObservableList);
view.SortDescriptions.Add(new SortDescription("Name", ListSortDirection.Ascending));
view.Filter = item => ((MyItem)item).IsActive;
DataContext = new { Items = view };
```

For reactive filtering without `DataGridCollectionView`, use a computed `IEnumerable` property that re-exposes a filtered collection and raise `PropertyChanged` when the filter changes.

---

## Binding Validation

Throw `DataValidationException` from the property setter:
```csharp
private string _name = "";
public string Name
{
    get => _name;
    set
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new DataValidationException("Name cannot be empty.");
        SetAndRaise(NameProperty, ref _name, value); // AvaloniaObject
        // or for INPC:
        _name = value;
        OnPropertyChanged();
    }
}
```

For `AvaloniaObject` DirectProperty, enable validation explicitly:
```csharp
public static readonly DirectProperty<MyControl, string> NameProperty =
    AvaloniaProperty.RegisterDirect<MyControl, string>(
        nameof(Name), o => o.Name, (o, v) => o.Name = v,
        enableDataValidation: true);
```

Display validation errors with the built-in control:
```xml
<DataValidationErrors/>
```

Or access errors via the attached property `DataValidationErrors.GetErrors(control)`.

---

## Binding to Commands

```xml
<Button Command="{Binding SaveCommand}"/>
<Button Command="{Binding DeleteCommand}" CommandParameter="{Binding SelectedItem}"/>

<!-- Binding to a method directly (ReactiveUI / CommunityToolkit) -->
<Button Command="{Binding DoSomething}"/>
```

With `IRelayCommand` (CommunityToolkit.Mvvm):
```csharp
[RelayCommand]
private async Task SaveAsync()
{
    // ...
}
// Generates SaveCommand property automatically
```

With `ReactiveCommand` (ReactiveUI):
```csharp
public ICommand SaveCommand { get; }

SaveCommand = ReactiveCommand.CreateFromTask(SaveAsync, canSave);
```

---

## Binding in ItemTemplate (DataTemplate scope)

Each item in a collection gets its own DataContext. Declare `x:DataType` on the DataTemplate:
```xml
<ListBox ItemsSource="{Binding People}">
    <ListBox.ItemTemplate>
        <DataTemplate x:DataType="vm:PersonViewModel">
            <TextBlock Text="{Binding FullName}"/>
        </DataTemplate>
    </ListBox.ItemTemplate>
</ListBox>
```

---

## Binding Debugging

```xml
<!-- Enable trace output for a specific binding -->
<TextBlock Text="{Binding Name, diag:Binding.DebugMode=True}"
           xmlns:diag="clr-namespace:Avalonia.Diagnostics;assembly=Avalonia"/>
```

- **DevTools (F12 in Debug builds)**: Data Context panel shows current DataContext hierarchy and property values.
- **Output window**: Binding errors appear as warnings, e.g. `[Binding] Could not find a matching property accessor for 'Name'`.
- Check `TraceLevel` on bindings: `{Binding Name, TraceLevel=Verbose}`.

---

## Common Mistakes

- **Missing `x:DataType`** — compiled bindings fail at build time with a type-resolution error. Every scope (Window, UserControl, DataTemplate) that uses compiled bindings needs `x:DataType`.
- **Binding to non-public members** — compiled bindings require `public` properties. Internal or private members cause build errors.
- **Not implementing `INotifyPropertyChanged`** — binding updates are silently dropped. Use `ObservableObject` (CommunityToolkit), `ReactiveObject` (ReactiveUI), or `AvaloniaObject` with `SetAndRaise`.
- **Using `OneTime` expecting updates** — `OneTime` captures the value once at binding activation. Use `OneWay` for live updates.
- **Mixing `{Binding}` and `{CompiledBinding}` carelessly** — in Avalonia 12, `{Binding}` is compiled by default. Opt out explicitly with `x:CompileBindings=False` on the element, not by switching to `{CompiledBinding}` (they are the same thing).
- **Reflection binding path with compiled binding scope** — special paths like `$parent`, `$self`, `#name` work only in compiled bindings and require the target type to be resolvable.
- **Binding `Command` to a method name, not a property** — `Command` must bind to an `ICommand` property. Methods need to be wrapped in a command object.
