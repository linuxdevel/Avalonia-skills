---
name: avalonia-pro-max/layout-patterns
description: Use when designing the page-level layout of an Avalonia app — responsive breakpoints, sidebar vs top-nav vs bottom-nav, dashboard grids, master-detail, settings page, mobile vs desktop adaptive layouts. Covers Grid, DockPanel, SplitView, NavigationView, ItemsRepeater layout strategies.
---

# Layout Patterns

## Breakpoints

Avalonia desktop windows have no fixed viewport, so define your own breakpoint conventions and react in code-behind or via `OnSizeChanged`. Recommended scale:

| Name | Width | Typical |
|---|---|---|
| `Compact` | < 640 px | Mobile, narrow sidebar collapsed window |
| `Medium` | 640 – 1024 px | Tablet, small desktop window |
| `Wide` | 1024 – 1440 px | Standard desktop |
| `XWide` | ≥ 1440 px | Large desktop, ultrawide |

```csharp
private void OnSizeChanged(object? sender, SizeChangedEventArgs e)
{
    var classes = (Window)this;
    classes.Classes.Set("compact", e.NewSize.Width <  640);
    classes.Classes.Set("medium",  e.NewSize.Width >= 640  && e.NewSize.Width < 1024);
    classes.Classes.Set("wide",    e.NewSize.Width >= 1024 && e.NewSize.Width < 1440);
    classes.Classes.Set("xwide",   e.NewSize.Width >= 1440);
}
```

Then style by class:
```xml
<Style Selector="Window.compact StackPanel.sidebar"><Setter Property="IsVisible" Value="False"/></Style>
```

For more granular containers, use `ContainerQuery` (see `avalonia-styling`).

---

## Layout Templates

### App Shell — Sidebar + Content + Right Panel

```xml
<Grid>
  <Grid.ColumnDefinitions>
    <ColumnDefinition Width="240"/>     <!-- Sidebar -->
    <ColumnDefinition Width="*"/>       <!-- Main -->
    <ColumnDefinition Width="320"/>     <!-- Right rail -->
  </Grid.ColumnDefinitions>

  <Border Grid.Column="0" Background="{DynamicResource SurfaceMutedBrush}">
    <!-- nav -->
  </Border>

  <ScrollViewer Grid.Column="1">
    <StackPanel Margin="32" Spacing="{StaticResource Space6}">
      <!-- main content -->
    </StackPanel>
  </ScrollViewer>

  <Border Grid.Column="2" Background="{DynamicResource SurfaceBrush}">
    <!-- detail / inspector -->
  </Border>
</Grid>
```

Hide the right rail on `compact`/`medium`:
```xml
<Style Selector="Window.compact Grid > Border:nth-child(3)">
  <Setter Property="IsVisible" Value="False"/>
</Style>
```

### Master-Detail with SplitView

```xml
<SplitView IsPaneOpen="True"
           DisplayMode="Inline"
           OpenPaneLength="320">
  <SplitView.Pane>
    <ListBox ItemsSource="{Binding Conversations}"
             SelectedItem="{Binding SelectedConversation}"/>
  </SplitView.Pane>
  <ContentControl Content="{Binding SelectedConversation}"/>
</SplitView>
```

For mobile-style adaptive: bind `DisplayMode` to a converter on window width — `Inline` on wide, `Overlay` on compact.

### Dashboard Grid (Cards)

```xml
<ScrollViewer>
  <ItemsControl ItemsSource="{Binding Widgets}" Margin="24">
    <ItemsControl.ItemsPanel>
      <ItemsPanelTemplate>
        <UniformGrid Columns="3"/>
      </ItemsPanelTemplate>
    </ItemsControl.ItemsPanel>
    <ItemsControl.ItemTemplate>
      <DataTemplate>
        <Border Classes="card" Margin="8">
          <ContentPresenter Content="{Binding}"/>
        </Border>
      </DataTemplate>
    </ItemsControl.ItemTemplate>
  </ItemsControl>
</ScrollViewer>
```

For responsive columns, swap to `WrapPanel` with min card widths:
```xml
<WrapPanel Orientation="Horizontal"/>
```
…and set `MinWidth="280" MaxWidth="360"` on the card.

For powerful auto-grid behavior, use `AvaloniaAutoGrid` or custom `Layout` with `ItemsRepeater`.

### Settings Page

```xml
<ScrollViewer>
  <StackPanel MaxWidth="720" Margin="24" Spacing="{StaticResource Space6}">
    <TextBlock Classes="h1" Text="Settings"/>
    <ui:SettingsExpander Header="Account" .../>
    <ui:SettingsExpander Header="Appearance" .../>
    <ui:SettingsExpander Header="Notifications" .../>
    <ui:SettingsExpander Header="Privacy" .../>
  </StackPanel>
</ScrollViewer>
```

`MaxWidth="720"` keeps reading length sane on ultrawide.

### Centered Single-Column (auth, onboarding)

```xml
<ScrollViewer>
  <StackPanel HorizontalAlignment="Center"
              MaxWidth="380"
              Margin="32"
              Spacing="{StaticResource Space4}">
    <Image Source="avares://MyApp/Assets/logo.svg" Height="40"/>
    <TextBlock Classes="h2" Text="Welcome back"/>
    <!-- form -->
  </StackPanel>
</ScrollViewer>
```

---

## Navigation Pattern Selection

| Pattern | Use when | Avalonia mechanism |
|---|---|---|
| **Sidebar nav (vertical)** | Desktop app, ≤8 top-level destinations | `SplitView` or FluentAvalonia `NavigationView PaneDisplayMode="Left"` |
| **Top tab nav** | ≤5 destinations, content-focused | `TabControl` |
| **Bottom nav** | Mobile, ≤5 destinations | FluentAvalonia `NavigationView PaneDisplayMode="LeftMinimal"` (mobile-styled) or custom `Grid` with `RadioButton`s |
| **Hamburger drawer** | Many destinations + secondary nav | `SplitView DisplayMode="Overlay"` with toggle |
| **Command palette** | Power users, search-driven | Custom modal with TextBox + filtered ListBox; bind `Ctrl+K` |
| **Breadcrumb** | Hierarchical content (file system, settings) | Custom `ItemsControl` with separator template |

Never mix sidebar + bottom nav at the same hierarchy level.

### Adaptive nav (single source of truth)

```csharp
NavigationView.PaneDisplayMode = window.Bounds.Width switch
{
    < 640  => NavigationViewPaneDisplayMode.LeftMinimal,
    < 1024 => NavigationViewPaneDisplayMode.LeftCompact,
    _      => NavigationViewPaneDisplayMode.Left
};
```

---

## Spacing Rhythm in Layouts

- Page padding: 24–32 px on desktop, 16 px on compact.
- Section spacing: `Space6` (24 px) between major sections, `Space4` (16 px) within.
- Card padding: `PaddingCard` (20 px).
- `StackPanel.Spacing` instead of per-child `Margin` (cleaner, less drift).

Avoid `Margin` and `Padding` collision — pick one.

---

## ScrollViewer Discipline

- Wrap **only** the scrollable region, not the whole window — let headers/footers stay fixed.
- One vertical scroll axis per view; nested scroll regions break wheel/trackpad UX.
- Set `HorizontalScrollBarVisibility="Disabled"` on vertical lists to prevent accidental horizontal scroll.
- For long lists, use a `VirtualizingStackPanel` (default in `ListBox`/`ItemsRepeater`) — never a regular `StackPanel` for 100+ items.

```xml
<ListBox ItemsSource="{Binding Items}">
  <ListBox.ItemsPanel>
    <ItemsPanelTemplate>
      <VirtualizingStackPanel Orientation="Vertical"/>
    </ItemsPanelTemplate>
  </ListBox.ItemsPanel>
</ListBox>
```

For grid virtualization, use `ItemsRepeater` with `StackLayout` or `UniformGridLayout`.

---

## Window Chrome

```xml
<Window ExtendClientAreaToDecorationsHint="True"
        ExtendClientAreaTitleBarHeightHint="-1"
        ExtendClientAreaChromeHints="PreferSystemChrome">
```

Hints:
- `PreferSystemChrome` — keep OS controls (recommended).
- `NoChrome` — fully custom (provide your own min/max/close buttons).
- `OSXThickTitleBar` — macOS thicker bar with traffic lights inset.

Reserve 40 px top safe area for the drag region. Add a `DragRegion` element with `IsHitTestVisible="True"` and listen for pointer drag if going chromeless.

---

## Mobile-Specific (Avalonia.Mobile)

- Use `SafeAreaPadding` from `TopLevel.InsetsManager`:
  ```csharp
  var insets = TopLevel.GetTopLevel(this)!.InsetsManager;
  insets.DisplayEdgeToEdge = true;
  ```
- Bottom nav must respect home-indicator inset.
- Touch targets ≥44×44 dp.
- One vertical scroll axis only.

---

## Common Mistakes

- **Fixed pixel widths on the whole layout** — breaks at small windows. Use `*` Grid columns.
- **`StackPanel` for a 500-item list** — laggy; use `ListBox`/`ItemsRepeater` (virtualized).
- **Two vertical scroll regions stacked** — wheel doesn't know which to scroll.
- **No `MaxWidth` on long-form text** — line length exceeds 90 chars and hurts readability.
- **Sidebar always visible at 800px window** — content gets cramped; collapse to overlay.
- **Putting nav in a `Window` and content in a `Window` separately** — single-window app should use `SplitView`/`NavigationView`.
- **Hardcoded margins like `12,8,15,4`** — break the spacing scale; use tokens.
- **Forgetting `RowDefinitions="Auto,*"`** — content expands wrongly.
- **Mixing `DockPanel` and `Grid` semantics in the same panel** — confusing layout. Pick one root layout per scope.
