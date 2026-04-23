---
name: avalonia-testing
description: Use when writing tests for Avalonia apps — headless UI testing, ViewModel unit tests, UI automation, or setting up the Avalonia test infrastructure.
---
# Avalonia Testing

## Overview
Two testing approaches: ViewModel unit tests (no Avalonia needed, plain xUnit/NUnit), and headless UI tests using `Avalonia.Headless` (renders without a display).

## ViewModel Unit Tests (No UI)
No special setup needed — ViewModels are plain C# classes:
```csharp
[Fact]
public void Name_Change_RaisesPropertyChanged()
{
    var vm = new MainViewModel();
    var raised = new List<string?>();
    vm.PropertyChanged += (_, e) => raised.Add(e.PropertyName);

    vm.Name = "Alice";

    Assert.Contains(nameof(vm.Name), raised);
    Assert.Equal("Alice", vm.Name);
}

[Fact]
public async Task SaveCommand_WhenNameEmpty_CannotExecute()
{
    var vm = new MainViewModel { Name = "" };
    Assert.False(vm.SaveCommand.CanExecute(null));
}
```

## Headless Testing Setup
NuGet packages:
- `Avalonia.Headless`
- `Avalonia.Headless.XUnit` (or `.NUnit`)

```csharp
// Assembly-level attribute (AssemblyInfo.cs or top of test file)
[assembly: AvaloniaTestApplication(typeof(TestAppBuilder))]

public class TestAppBuilder
{
    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UseHeadless(new AvaloniaHeadlessOptions { UseHeadlessDrawing = true });
}
```

## Writing Headless Tests (xUnit)
```csharp
public class MainWindowTests
{
    [AvaloniaFact]
    public void Button_Click_UpdatesViewModel()
    {
        var window = new MainWindow();
        var vm = new MainViewModel();
        window.DataContext = vm;
        window.Show();

        var button = window.FindControl<Button>("SaveButton")!;
        button.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));

        Assert.True(vm.SaveWasCalled);
    }

    [AvaloniaFact]
    public async Task TextBox_Input_UpdatesBinding()
    {
        var window = new MainWindow();
        window.DataContext = new MainViewModel();
        window.Show();

        var textBox = window.FindControl<TextBox>("NameBox")!;
        textBox.RaiseTextInput("Hello");

        await Task.Delay(50); // allow binding to propagate
        Assert.Equal("Hello", ((MainViewModel)window.DataContext!).Name);
    }
}
```

## Finding Controls
```csharp
// By name (x:Name)
var btn = window.FindControl<Button>("MyButton");

// By type (first match)
var textBox = window.FindDescendantOfType<TextBox>();

// All of type
var allButtons = window.GetVisualDescendants().OfType<Button>();
```

## Simulating Input
```csharp
// Keyboard
window.KeyPress(Key.Enter, KeyModifiers.None);
window.KeyTextInput("Hello");

// Mouse/Pointer
window.MouseDown(new Point(100, 50), MouseButton.Left);
window.MouseMove(new Point(150, 50));
window.MouseUp(new Point(150, 50), MouseButton.Left);
```

## Screenshot Testing
```csharp
[AvaloniaFact]
public void Window_RendersCorrectly()
{
    var window = new MainWindow();
    window.Show();

    // Capture frame as bitmap
    var bitmap = window.CaptureRenderedFrame()!;
    // Compare or save for regression
    bitmap.Save("snapshot.png");
}
```

## Testing with NUnit
```csharp
[TestFixture]
public class Tests
{
    [AvaloniaTest]  // instead of [Test]
    public void MyTest() { }
}
```

## Common Mistakes
- Missing `[assembly: AvaloniaTestApplication]` — headless renderer not initialized, NullReferenceException
- Using `[Fact]` instead of `[AvaloniaFact]` for UI tests — no Avalonia dispatcher, random failures
- Forgetting `window.Show()` before interacting — controls not attached to visual tree
- Testing bindings synchronously — bindings may be async, add small delay or use `Dispatcher.UIThread.RunJobs()`
