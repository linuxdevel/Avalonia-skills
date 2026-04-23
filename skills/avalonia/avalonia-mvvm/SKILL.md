---
name: avalonia-mvvm
description: Use when implementing the MVVM pattern in Avalonia, including ViewModels, INotifyPropertyChanged, ICommand, ReactiveUI, CommunityToolkit.Mvvm, or ViewModel-first navigation.
---

# Avalonia MVVM

## Overview

MVVM: Model (data/business), View (.axaml), ViewModel (presentation logic, bindable state). ViewModel knows nothing about View. Views bind to ViewModel properties and commands.

## INotifyPropertyChanged (Manual)

```csharp
public class PersonViewModel : INotifyPropertyChanged
{
    private string _name = "";
    public string Name
    {
        get => _name;
        set { _name = value; PropertyChanged?.Invoke(this, new(nameof(Name))); }
    }
    public event PropertyChangedEventHandler? PropertyChanged;
}
```

## CommunityToolkit.Mvvm (Recommended)

Source-generator based, no reflection, clean code.

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

public partial class MainViewModel : ObservableObject
{
    [ObservableProperty]
    private string _name = "";

    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(SaveCommand))]
    private bool _isDirty;

    [RelayCommand(CanExecute = nameof(CanSave))]
    private async Task SaveAsync()
    {
        // save logic
    }

    private bool CanSave() => IsDirty && !string.IsNullOrEmpty(Name);
}
```

NuGet: `CommunityToolkit.Mvvm`

Generated: `Name` property with change notification, `NameChanged` partial method hook, `SaveCommand` as `AsyncRelayCommand`.

## ReactiveUI (Alternative)

```csharp
using ReactiveUI;

public class MainViewModel : ReactiveObject
{
    private string _name = "";
    public string Name
    {
        get => _name;
        set => this.RaiseAndSetIfChanged(ref _name, value);
    }

    public ReactiveCommand<Unit, Unit> SaveCommand { get; }

    public MainViewModel()
    {
        var canSave = this.WhenAnyValue(x => x.Name, n => !string.IsNullOrEmpty(n));
        SaveCommand = ReactiveCommand.CreateFromTask(SaveAsync, canSave);
    }

    private async Task SaveAsync() { /* ... */ }
}
```

NuGet: `Avalonia.ReactiveUI`  
App setup: `.UseReactiveUI()` in Program.cs

## ICommand (Manual)

```csharp
public class RelayCommand : ICommand
{
    private readonly Action _execute;
    private readonly Func<bool>? _canExecute;

    public RelayCommand(Action execute, Func<bool>? canExecute = null)
    { _execute = execute; _canExecute = canExecute; }

    public event EventHandler? CanExecuteChanged;
    public bool CanExecute(object? p) => _canExecute?.Invoke() ?? true;
    public void Execute(object? p) => _execute();
    public void RaiseCanExecuteChanged() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}
```

## ViewLocator Pattern

Auto-maps ViewModels → Views by naming convention (`FooViewModel` → `FooView`):

```csharp
public class ViewLocator : IDataTemplate
{
    public Control? Build(object? data)
    {
        if (data is null) return null;
        var name = data.GetType().FullName!.Replace("ViewModel", "View");
        var type = Type.GetType(name);
        return type != null
            ? (Control)Activator.CreateInstance(type)!
            : new TextBlock { Text = $"Not Found: {name}" };
    }
    public bool Match(object? data) => data is ViewModelBase;
}
```

Register in App.axaml:

```xml
<Application.DataTemplates>
    <local:ViewLocator/>
</Application.DataTemplates>
```

## ViewModel-First Navigation

Pattern: Router/NavigationViewModel holds current page ViewModel, ContentControl displays it:

```xml
<ContentControl Content="{Binding CurrentPage}"/>
```

```csharp
public partial class MainViewModel : ObservableObject
{
    [ObservableProperty]
    private ViewModelBase _currentPage = new HomeViewModel();

    public void NavigateTo(ViewModelBase page) => CurrentPage = page;
}
```

## Design-Time DataContext

```xml
<Window xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
        d:DataContext="{d:DesignInstance vm:MainViewModel, IsDesignTimeCreatable=True}">
```

## ObservableCollection for Lists

```csharp
public ObservableCollection<PersonViewModel> People { get; } = new();
```

Use `ObservableCollection<T>` (not `List<T>`) so UI updates on add/remove.

## Common Mistakes

- Using `List<T>` instead of `ObservableCollection<T>` — list changes not reflected in UI
- Not calling `PropertyChanged` with exact property name — use `nameof()`
- Doing UI work in ViewModel (creating controls, accessing `DataContext`)
- Async command without `AsyncRelayCommand` — exceptions swallowed, UI blocks
- Forgetting `partial` keyword on CommunityToolkit ViewModel class — source gen fails silently
