---
name: avalonia-controls-navigation
description: Use when working with Avalonia navigation controls: TabControl, Menu, ContextMenu, MenuItem, NativeMenu, or TrayIcon. Covers tab binding, menu command wiring, access keys, context menu DataContext resolution, and tray icon setup for Avalonia 12 desktop apps.
---

# Avalonia Navigation Controls

## Overview

Navigation controls let users move between views or trigger application commands. All menu controls support `Command` binding and keyboard shortcuts via `InputGesture`.

---

## TabControl

Displays content in tabbed panels. Tabs can be static (inline `TabItem`) or dynamic (bound `ItemsSource`).

| Property | Type | Notes |
|---|---|---|
| `SelectedIndex` | `int` | TwoWay |
| `SelectedItem` | `object` | TwoWay |
| `TabStripPlacement` | `Dock` | `Top` (default), `Bottom`, `Left`, `Right` |
| `ItemsSource` | `IEnumerable` | For dynamic tabs |
| `ItemTemplate` | `DataTemplate` | Header template for dynamic tabs |
| `ContentTemplate` | `DataTemplate` | Body template for dynamic tabs |

**TabItem properties:**

| Property | Notes |
|---|---|
| `Header` | Tab label (string or XAML) |
| `Content` | Tab body |
| `IsEnabled` | Disables individual tab |
| `IsSelected` | Set programmatically |

```xml
<!-- Static tabs -->
<TabControl SelectedIndex="{Binding ActiveTabIndex}" TabStripPlacement="Top">
    <TabItem Header="Dashboard">
        <views:DashboardView/>
    </TabItem>
    <TabItem Header="Reports">
        <views:ReportsView/>
    </TabItem>
    <TabItem Header="Settings" IsEnabled="{Binding IsAdmin}">
        <views:SettingsView/>
    </TabItem>
</TabControl>

<!-- Custom tab header with icon -->
<TabControl>
    <TabItem>
        <TabItem.Header>
            <StackPanel Orientation="Horizontal" Spacing="6">
                <PathIcon Data="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"
                          Width="14" Height="14"/>
                <TextBlock Text="Dashboard" VerticalAlignment="Center"/>
            </StackPanel>
        </TabItem.Header>
        <views:DashboardView/>
    </TabItem>
</TabControl>
```

**Dynamic tabs (ViewModel-driven):**

```xml
<TabControl ItemsSource="{Binding Tabs}"
            SelectedItem="{Binding ActiveTab}">
    <TabControl.ItemTemplate>
        <!-- Header template -->
        <DataTemplate x:DataType="vm:TabVm">
            <StackPanel Orientation="Horizontal" Spacing="6">
                <TextBlock Text="{Binding Title}" VerticalAlignment="Center"/>
                <Button Content="✕"
                        Command="{Binding $parent[TabControl].DataContext.CloseTabCommand}"
                        CommandParameter="{Binding}"
                        Padding="4,0" FontSize="10"/>
            </StackPanel>
        </DataTemplate>
    </TabControl.ItemTemplate>
    <TabControl.ContentTemplate>
        <!-- Body template -->
        <DataTemplate x:DataType="vm:TabVm">
            <ContentControl Content="{Binding Content}"/>
        </DataTemplate>
    </TabControl.ContentTemplate>
</TabControl>
```

```csharp
public class TabVm
{
    public string Title { get; set; } = "";
    public object? Content { get; set; }
}
```

---

## Menu

Top-level application menu bar. Contains `MenuItem` hierarchy.

| Property | Notes |
|---|---|
| `Header` | Text label; prefix with `_` for access key |
| `Command` | Bound command |
| `CommandParameter` | Passed to command |
| `Icon` | Left-side icon (usually `Image` or `PathIcon`) |
| `InputGesture` | Keyboard shortcut (display only for top-level; functional for items) |
| `Items` | Sub-menu items |
| `IsEnabled` | Disables item |

```xml
<Menu>
    <MenuItem Header="_File">
        <MenuItem Header="_New"
                  Command="{Binding NewCommand}"
                  InputGesture="Ctrl+N">
            <MenuItem.Icon>
                <PathIcon Data="M14 2H6c-1.1 0-2 .9-2 2v16..." Width="16" Height="16"/>
            </MenuItem.Icon>
        </MenuItem>
        <MenuItem Header="_Open..."
                  Command="{Binding OpenCommand}"
                  InputGesture="Ctrl+O"/>
        <Separator/>
        <MenuItem Header="Recent Files" Items="{Binding RecentFiles}">
            <MenuItem.ItemTemplate>
                <DataTemplate x:DataType="vm:RecentFileVm">
                    <MenuItem Header="{Binding DisplayName}"
                              Command="{Binding $parent[MenuItem].DataContext.OpenRecentCommand}"
                              CommandParameter="{Binding Path}"/>
                </DataTemplate>
            </MenuItem.ItemTemplate>
        </MenuItem>
        <Separator/>
        <MenuItem Header="E_xit" Command="{Binding ExitCommand}" InputGesture="Alt+F4"/>
    </MenuItem>

    <MenuItem Header="_Edit">
        <MenuItem Header="Cu_t"   Command="ApplicationCommands.Cut"   InputGesture="Ctrl+X"/>
        <MenuItem Header="_Copy"  Command="ApplicationCommands.Copy"  InputGesture="Ctrl+C"/>
        <MenuItem Header="_Paste" Command="ApplicationCommands.Paste" InputGesture="Ctrl+V"/>
    </MenuItem>

    <MenuItem Header="_Help">
        <MenuItem Header="_About" Command="{Binding AboutCommand}"/>
    </MenuItem>
</Menu>
```

---

## ContextMenu

Attached to any control. Shown on right-click.

| Property | Notes |
|---|---|
| `Items` | `MenuItem` list |
| `IsOpen` | Programmatic open/close |

```xml
<ListBox ItemsSource="{Binding Files}" SelectedItem="{Binding SelectedFile}">
    <ListBox.ContextMenu>
        <ContextMenu>
            <MenuItem Header="Open"
                      Command="{Binding $parent[Window].DataContext.OpenFileCommand}"
                      CommandParameter="{Binding SelectedFile}"/>
            <MenuItem Header="Rename..."
                      Command="{Binding $parent[Window].DataContext.RenameCommand}"
                      CommandParameter="{Binding SelectedFile}"/>
            <Separator/>
            <MenuItem Header="Delete"
                      Command="{Binding $parent[Window].DataContext.DeleteCommand}"
                      CommandParameter="{Binding SelectedFile}"/>
        </ContextMenu>
    </ListBox.ContextMenu>
    <ListBox.ItemTemplate>
        <DataTemplate x:DataType="vm:FileVm">
            <TextBlock Text="{Binding Name}"/>
        </DataTemplate>
    </ListBox.ItemTemplate>
</ListBox>
```

> **DataContext pitfall:** `ContextMenu` is not in the visual tree of its host control. Its `DataContext` is the **control's DataContext** by default, but ancestor binding (`$parent[Window]`) must be used to reach the Window's ViewModel. Alternatively, set `DataContext` explicitly in code.

```csharp
// Set ContextMenu DataContext explicitly in code-behind
myControl.ContextMenu!.DataContext = this.DataContext;
```

---

## NativeMenu

Platform-native menus. Used for macOS app menus and TrayIcon menus.

```xml
<!-- In App.axaml, for macOS native app menu -->
<Application.ApplicationLifetime>
    <!-- ... -->
</Application.ApplicationLifetime>
<NativeMenu.Menu>
    <NativeMenu>
        <NativeMenuItem Header="About MyApp" Command="{Binding AboutCommand}"/>
        <NativeMenuItemSeparator/>
        <NativeMenuItem Header="Quit" Command="{Binding QuitCommand}" Gesture="Cmd+Q"/>
    </NativeMenu>
</NativeMenu.Menu>
```

---

## TrayIcon

System tray icon for desktop apps. **Desktop lifetime only.**

In `App.axaml`:

```xml
<Application xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             x:Class="MyApp.App">
    <TrayIcon.Icons>
        <TrayIcons>
            <TrayIcon Icon="/Assets/tray-icon.ico"
                      ToolTipText="MyApp is running">
                <TrayIcon.Menu>
                    <NativeMenu>
                        <NativeMenuItem Header="Show Window"
                                        Command="{Binding ShowWindowCommand}"/>
                        <NativeMenuItem Header="Settings"
                                        Command="{Binding SettingsCommand}"/>
                        <NativeMenuItemSeparator/>
                        <NativeMenuItem Header="Quit"
                                        Command="{Binding QuitCommand}"/>
                    </NativeMenu>
                </TrayIcon.Menu>
            </TrayIcon>
        </TrayIcons>
    </TrayIcon.Icons>
</Application>
```

```csharp
// In App.axaml.cs — wire DataContext for TrayIcon commands
public override void OnFrameworkInitializationCompleted()
{
    if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
    {
        var vm = new MainWindowViewModel();
        desktop.MainWindow = new MainWindow { DataContext = vm };

        // TrayIcon DataContext
        if (TrayIcon.GetIcons(this) is { } icons)
            foreach (var icon in icons)
                icon.DataContext = vm;  // or a dedicated TrayIconVm
    }
    base.OnFrameworkInitializationCompleted();
}
```

**Icon formats:** `.ico` recommended for Windows; `.png` works on Linux/macOS.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Access key not working in `MenuItem.Header` | Use `_` prefix: `Header="_File"` (Alt+F). Without `_`, no access key is registered |
| `ContextMenu` command binding fails | `ContextMenu` is not in visual tree; use `$parent[Window].DataContext.Cmd` or set `DataContext` in code |
| `TrayIcon` crashes on non-desktop lifetime | Guard: `if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime)` before using TrayIcon |
| `TabControl` dynamic tabs show blank content | Provide both `ItemTemplate` (header) and `ContentTemplate` (body), or use `ContentControl` in body template |
| `MenuItem.InputGesture` not firing | `InputGesture` on `MenuItem` only shows the hint; actual shortcut requires `KeyBinding` at the window level |
| Dynamic submenu bound `Items` not showing | Use `Items="{Binding ...}"` with an `ItemTemplate` on the parent `MenuItem`, not `ItemsSource` |
