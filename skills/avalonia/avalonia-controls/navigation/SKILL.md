---
name: avalonia-controls-navigation
description: Use when working with Avalonia navigation controls: TabControl (TabItem.IconTemplate 12.0+), Menu, ContextMenu, Flyout (FlyoutBase.IsOpen 12.0+), NativeMenu/NativeDock.Menu, TrayIcon, and the page-based navigation set added in 12.0 (Page, ContentPage, NavigationPage, TabbedPage, DrawerPage, CarouselPage, CommandBar). Covers tab binding, menu command wiring, access keys, context menu DataContext, tray icons, and mobile-style page stacks. HamburgerMenu does not exist in core.
---

# Avalonia Navigation Controls

## Overview

Navigation controls let users move between views or trigger application commands. All menu controls support `Command` binding and keyboard shortcuts via `InputGesture`.

| Need | Use | Availability |
|---|---|---|
| Desktop tabs | `TabControl` | all |
| Touch-first page stack, drawer, bottom tabs (mobile style) | `NavigationPage` / `DrawerPage` / `TabbedPage` / `ContentPage` / `CarouselPage` | **12.0+** (core `Avalonia` package) |
| Toolbar with overflow | `CommandBar` | **12.0+** |
| Side nav on 11.x / desktop shell | `SplitView` + `ListBox`, or FluentAvalonia `NavigationView` | all |
| `HamburgerMenu` | **not in Avalonia core** — use `DrawerPage` (12.0+), `SplitView`, or a community lib | — |

> **12.0+ touch/pen:** `TabControl`/`ListBox`/`TreeView` select on pointer **release**; `TabItem`/`ListBoxItem`/`TreeViewItem` handle selection themselves.

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
| `Icon` / `IconTemplate` | Icon next to the header; `IconTemplate` (`IDataTemplate`) is **12.0+** |
| `IndicatorTemplate` | Selection indicator template |

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

**Icon template (12.0+):**

```xml
<TabControl ItemsSource="{Binding Tabs}">
    <TabControl.Styles>
        <Style Selector="TabItem">
            <Setter Property="Header" Value="{Binding Title}"/>
            <Setter Property="Icon" Value="{Binding IconData}"/>
            <Setter Property="IconTemplate">
                <Setter.Value>
                    <DataTemplate x:DataType="x:String">
                        <PathIcon Data="{Binding}" Width="14" Height="14"/>
                    </DataTemplate>
                </Setter.Value>
            </Setter>
        </Style>
    </TabControl.Styles>
</TabControl>
```
(11.x: put the icon inside a custom `Header` as shown above.)

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

## Page-based Navigation (12.0+)

Touch-first, MAUI-style navigation in the **core `Avalonia` package** (namespace `Avalonia.Controls`, default xmlns). Not available in 11.x. Hierarchy: `Page` → `ContentPage` (single content), `MultiPage` → `NavigationPage`, `SelectingMultiPage` → `TabbedPage`/`CarouselPage`; `DrawerPage` derives from `Page`. **`ContentPage.Content` cannot be a `Page`** (throws `InvalidOperationException`) — host pages in `NavigationPage`/`TabbedPage`/`DrawerPage`/`CarouselPage`.

**`Page` members:** `Header`/`HeaderTemplate`, `Icon`/`IconTemplate`, `CurrentPage`, `Navigation` (`INavigation` of parent `NavigationPage`), `IsInNavigationPage`, `SafeAreaPadding`; events `Navigating` (`NavigatingFromEventArgs`, set `Cancel`), `NavigatedFrom`, `NavigatedTo`; overrides `OnNavigatingFrom/OnNavigatedFrom/OnNavigatedTo` (call `base`). `NavigatedTo` fires every time the page becomes active (unlike `Loaded`).

| Control | Purpose | Key members |
|---|---|---|
| `ContentPage` | One piece of content | `Content`, `ContentTemplate`, `TopCommandBar`, `BottomCommandBar`, `H/VerticalContentAlignment`, `AutomaticallyApplySafeAreaPadding` |
| `NavigationPage` | Push/pop stack with nav bar + back button | `PushAsync`, `PopAsync`, `PopToRootAsync`, `PopToPageAsync`, `ReplaceAsync` (each with `IPageTransition` overload), `InsertPage`, `RemovePage`, modal: `PushModalAsync`/`PopModalAsync`/`PopAllModalsAsync`; props `NavigationStack`, `ModalStack`, `StackDepth`, `CanGoBack`, `IsNavigating`, `PageTransition`, `ModalTransition`, `IsGestureEnabled`, `HasShadow`, `BarHeight`; events `Pushed`, `Popped`, `PoppedToRoot`, `PageInserted`, `PageRemoved`, `ModalPushed`, `ModalPopped` |
| `TabbedPage` | Tab strip over child pages | `Pages` or `ItemsSource`+`PageTemplate`, `SelectedIndex`, `SelectedPage`, `TabPlacement` (`Auto`/`Top`/`Bottom`/`Left`/`Right`; `Auto` = Bottom on iOS/Android), `IsGestureEnabled` (default false), `IsKeyboardNavigationEnabled`, `PageTransition`, `IndicatorTemplate`; attached `TabbedPage.IsTabEnabled`; event `SelectionChanged` |
| `DrawerPage` | Slide-out drawer (built on `SplitView`) | below |
| `CarouselPage` | Swipe between pages | `Pages`/`ItemsSource`, `SelectedIndex`, `IsGestureEnabled`, `IsKeyboardNavigationEnabled`, `PageTransition`, `ItemsPanel` |

**`NavigationPage` attached properties** (set on a child page): `HasNavigationBar`, `HasBackButton`, `IsBackButtonEnabled`, `BackButtonContent`, `TopCommandBar`, `BottomCommandBar`, `BarLayoutBehavior` (`Inset` default / `Overlay`), `BarHeightOverride`. Only the first page set as `Content` is the root; most navigation calls are ignored while `IsNavigating` is true; cancelling in `Navigating` aborts silently (also cancels system back on Android/browser).

```xml
<NavigationPage>
    <ContentPage Header="Home">
        <StackPanel Margin="16" Spacing="8">
            <TextBlock Text="Home" FontSize="24"/>
            <Button Content="Details" Click="OnDetails"/>
        </StackPanel>
    </ContentPage>
</NavigationPage>
```

```csharp
private async void OnDetails(object? s, RoutedEventArgs e)
{
    if (this.FindAncestorOfType<ContentPage>()?.Navigation is { } nav)   // or Page.Navigation on the page itself
        await nav.PushAsync(new ContentPage { Header = "Details", Content = new TextBlock { Text = "..." } });
}

// Page code-behind (ContentPage subclass): cancel navigation with unsaved edits
protected override void OnNavigatingFrom(NavigatingFromEventArgs args)
{
    base.OnNavigatingFrom(args);
    if (_hasPendingEdits) args.Cancel = true;
}
```

**TabbedPage**

```xml
<TabbedPage TabPlacement="Bottom">
    <ContentPage Header="Home">
        <ContentPage.Icon><PathIcon Data="M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z"/></ContentPage.Icon>
        <TextBlock Text="Home" Margin="16"/>
    </ContentPage>
    <NavigationPage Header="Settings">           <!-- independent stack per tab -->
        <ContentPage Header="Settings"><TextBlock Text="..." Margin="16"/></ContentPage>
    </NavigationPage>
    <ContentPage Header="Locked" TabbedPage.IsTabEnabled="False"/>
</TabbedPage>

<!-- Data-driven -->
<TabbedPage ItemsSource="{Binding Tabs}">
    <TabbedPage.PageTemplate>
        <DataTemplate x:DataType="vm:TabVm">
            <ContentPage Header="{Binding Title}"><TextBlock Text="{Binding Body}" Margin="16"/></ContentPage>
        </DataTemplate>
    </TabbedPage.PageTemplate>
</TabbedPage>
```

**DrawerPage** — props (defaults): `Drawer`/`DrawerTemplate`, `Content`/`ContentTemplate`, `IsOpen` (false), `DrawerLength` (320), `CompactDrawerLength` (48), `DrawerBreakpointLength` (0 = off; width below which it switches to overlay), `IsGestureEnabled` (true), `DrawerBehavior` (`Auto`/`Flyout`/`Locked`/`Disabled`), `DrawerLayoutBehavior` (`Overlay`/`Split`/`CompactOverlay`/`CompactInline`), `DrawerPlacement` (`Left`/`Right`/`Top`/`Bottom`), `DrawerHeader`/`DrawerHeaderTemplate`/`DrawerHeaderBackground`/`DrawerHeaderForeground`, `DrawerFooter`/`DrawerFooterTemplate`/`DrawerFooterBackground`/`DrawerFooterForeground`, `DrawerIcon`/`DrawerIconTemplate`, `DrawerBackground`, `BackdropBrush`, `DisplayMode`. Events `Opened`, `Closing` (`DrawerClosingEventArgs.Cancel`), `Closed`. `Closing` is not raised when `DrawerBehavior` forces it closed; `IsOpen` is coerced when `Disabled`/`Locked`.

```xml
<DrawerPage Header="My App" DrawerLength="280" IsOpen="{Binding IsDrawerOpen}">
    <DrawerPage.DrawerHeader>
        <Border Background="#1E3A5F" Padding="16">
            <TextBlock Text="My App" Foreground="White" FontSize="20"/>
        </Border>
    </DrawerPage.DrawerHeader>
    <DrawerPage.Drawer>
        <StackPanel Spacing="4" Margin="8">
            <Button Content="Home" Command="{Binding GoHomeCommand}"/>
            <Button Content="Settings" Command="{Binding GoSettingsCommand}"/>
        </StackPanel>
    </DrawerPage.Drawer>
    <DrawerPage.DrawerFooter>
        <Border Padding="12"><Button Content="Sign Out" HorizontalAlignment="Stretch"/></Border>
    </DrawerPage.DrawerFooter>
    <NavigationPage>
        <ContentPage Header="Home"><TextBlock Text="Home" Margin="16"/></ContentPage>
    </NavigationPage>
</DrawerPage>
```

Wide-screen sidebar: `DrawerLayoutBehavior="Split" DrawerBehavior="Locked"`, or `DrawerBreakpointLength="800"`. Compact rail: `DrawerLayoutBehavior="CompactInline"`.

**CommandBar (12.0+)** — primary commands inline, secondary in an overflow menu. Elements implement `ICommandBarElement`: `CommandBarButton` (`Label`, `Icon`, `IsCompact`, `DynamicOverflowOrder`, plus `Button.Command`), `CommandBarToggleButton`, `CommandBarSeparator`. Props: `PrimaryCommands`, `SecondaryCommands`, `DefaultLabelPosition`, `IsDynamicOverflowEnabled`, `OverflowButtonVisibility`, `IsSticky`, `IsOpen`, `Content`; events `Opening/Opened/Closing/Closed`. Use standalone or via `ContentPage.TopCommandBar`/`BottomCommandBar`.

```xml
<CommandBar>
    <CommandBar.PrimaryCommands>
        <CommandBarButton Label="New" Command="{Binding NewCommand}">
            <CommandBarButton.Icon><PathIcon Data="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z"/></CommandBarButton.Icon>
        </CommandBarButton>
        <CommandBarSeparator/>
    </CommandBar.PrimaryCommands>
    <CommandBar.SecondaryCommands>
        <CommandBarButton Label="Export" Command="{Binding ExportCommand}"/>
    </CommandBar.SecondaryCommands>
</CommandBar>
```

> **Carousel vs CarouselPage:** `Carousel` (items control, `avalonia-controls/data-display`) shows data items; `CarouselPage` swipes between `Page`s.

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
| `Items` / `ItemsSource` | Sub-menu items (static) / bound collection |
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
        <MenuItem Header="Recent Files" ItemsSource="{Binding RecentFiles}">
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
| `Placement` | Popup placement (12+; `PlacementMode` was removed — 11.x name) |

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

## Flyout

`Flyout`/`MenuFlyout` attach via `Button.Flyout` or `FlyoutBase.AttachedFlyout`.

| `FlyoutBase` member | Notes |
|---|---|
| `IsOpen` | `StyledProperty<bool>` **(12.0+)** — bindable/settable. Setting `true` shows at the last placement target; no effect if `ShowAt` was never called |
| `ShowAt(Control)`, `Hide()`, `Target` | All versions |
| `Opened`, `Closed` | Events |

```xml
<Button Content="Options">
    <Button.Flyout>
        <Flyout IsOpen="{Binding IsOptionsOpen, Mode=TwoWay}">  <!-- 12.0+ binding -->
            <TextBlock Text="Hello"/>
        </Flyout>
    </Button.Flyout>
</Button>
```

---

## PipsPager (12.0+)

Dot-style page indicator/pager (WinUI-like). Pair with `Carousel`/`CarouselPage` or any paged view.

| Member | Type | Notes |
|---|---|---|
| `NumberOfPages` | `int` | total pages |
| `SelectedPageIndex` | `int` | two-way bind to the pager's owner |
| `MaxVisiblePips` | `int` | pips shown before scrolling |
| `Orientation` | `Orientation` | horizontal / vertical |
| `IsPreviousButtonVisible` / `IsNextButtonVisible` | `bool` | arrow buttons |
| `PreviousButtonTheme` / `NextButtonTheme` | `ControlTheme` | restyle arrows |
| `SelectedIndexChanged` | routed event (`PipsPagerSelectedIndexChangedEventArgs`) | |

```xml
<StackPanel Spacing="8">
    <Carousel x:Name="Slides" ItemsSource="{Binding Slides}"
              SelectedIndex="{Binding #Pager.SelectedPageIndex}"/>
    <PipsPager x:Name="Pager" HorizontalAlignment="Center"
               NumberOfPages="{Binding Slides.Count}" MaxVisiblePips="7"
               IsPreviousButtonVisible="True" IsNextButtonVisible="True"/>
</StackPanel>
```

Not in 11.x — there, use a `ListBox` of dots bound to the `Carousel.SelectedIndex`.

---

## NativeMenu

Platform-native menus. Used for macOS app menus and TrayIcon menus.

```xml
<!-- On a Window (macOS menu bar while that window is active; ignored where unsupported) -->
<NativeMenu.Menu>
    <NativeMenu>
        <NativeMenuItem Header="About MyApp" Command="{Binding AboutCommand}"/>
        <NativeMenuItemSeparator/>
        <NativeMenuItem Header="Quit" Command="{Binding QuitCommand}" Gesture="Cmd+Q"/>
    </NativeMenu>
</NativeMenu.Menu>
```

**macOS Dock menu — `NativeDock.Menu` (12.0+):** attached property `NativeDock.Menu` (`NativeMenu`); `NativeDock.GetMenu/SetMenu`. Supported where a `NativeMenu` can attach to the dock (macOS).

```xml
<!-- App.axaml -->
<NativeDock.Menu>
    <NativeMenu>
        <NativeMenuItem Header="New Window" Command="{Binding NewWindowCommand}"/>
    </NativeMenu>
</NativeDock.Menu>
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
| Dynamic submenu bound items not showing | Bind `ItemsSource="{Binding ...}"` (+ `ItemTemplate`) on the parent `MenuItem`; `Items` is the static collection and isn't bindable in 11+ |
| `NavigationPage`/`DrawerPage`/`TabbedPage` in an 11.x project | 12.0+ only — use `TabControl`, `SplitView`, `Frame`-less ViewModel navigation (`ContentControl` + DataTemplates) |
| `ContentPage` with another `Page` as `Content` | Throws — nest pages inside `NavigationPage`/`TabbedPage`/`DrawerPage`/`CarouselPage` |
| `HamburgerMenu` control not found | Doesn't exist in core; use `DrawerPage` (12.0+) or `SplitView` |
| `ContextMenu.PlacementMode` / `Popup.PlacementMode` in 12 | Removed — use `Placement` |
| `FlyoutBase.IsOpen` binding in 11.x | Styled property only since 12.0; use `ShowAt`/`Hide` in 11.x |
| Page navigation call ignored | `NavigationPage` ignores calls while `IsNavigating`; await each call |
