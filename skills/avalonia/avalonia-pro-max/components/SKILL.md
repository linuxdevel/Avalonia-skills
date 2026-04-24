---
name: avalonia-pro-max/components
description: Use when building production-quality Avalonia screens — copy-paste XAML recipes for cards, primary/secondary/icon buttons, dialogs, sidebar nav, command bar, settings page, forms with validation, empty states, toasts, badges, skeletons. All recipes use semantic tokens from the design-system sub-skill.
---

# Component Recipes

All recipes assume the design tokens from `avalonia-pro-max/design-system` are loaded (`SurfaceBrush`, `AccentBrush`, `TextPrimaryBrush`, `RadiusLg`, `Space*`, etc.).

---

## Buttons

### Reusable Button Styles

```xml
<!-- Styles/Buttons.axaml -->
<Styles xmlns="https://github.com/avaloniaui"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">

  <!-- Base: applies to all Button -->
  <Style Selector="Button">
    <Setter Property="MinHeight" Value="36"/>
    <Setter Property="Padding" Value="14,8"/>
    <Setter Property="CornerRadius" Value="{StaticResource RadiusMd}"/>
    <Setter Property="FontWeight" Value="Medium"/>
    <Setter Property="Cursor" Value="Hand"/>
    <Setter Property="Transitions">
      <Transitions>
        <BrushTransition Property="Background" Duration="0:0:0.15"/>
        <BrushTransition Property="Foreground" Duration="0:0:0.15"/>
        <TransformOperationsTransition Property="RenderTransform" Duration="0:0:0.10"/>
      </Transitions>
    </Setter>
    <Setter Property="RenderTransform" Value="none"/>
  </Style>

  <Style Selector="Button:pressed">
    <Setter Property="RenderTransform" Value="scale(0.98)"/>
  </Style>

  <!-- Primary -->
  <Style Selector="Button.primary">
    <Setter Property="Background" Value="{DynamicResource AccentBrush}"/>
    <Setter Property="Foreground" Value="{DynamicResource TextOnAccentBrush}"/>
  </Style>
  <Style Selector="Button.primary:pointerover /template/ ContentPresenter">
    <Setter Property="Background" Value="{DynamicResource AccentBrush}"/>
    <Setter Property="Opacity" Value="0.9"/>
  </Style>

  <!-- Secondary (outline) -->
  <Style Selector="Button.secondary">
    <Setter Property="Background" Value="Transparent"/>
    <Setter Property="Foreground" Value="{DynamicResource TextPrimaryBrush}"/>
    <Setter Property="BorderBrush" Value="{DynamicResource BorderBrush}"/>
    <Setter Property="BorderThickness" Value="1"/>
  </Style>
  <Style Selector="Button.secondary:pointerover /template/ ContentPresenter">
    <Setter Property="Background" Value="{DynamicResource SurfaceMutedBrush}"/>
  </Style>

  <!-- Ghost -->
  <Style Selector="Button.ghost">
    <Setter Property="Background" Value="Transparent"/>
    <Setter Property="Foreground" Value="{DynamicResource TextPrimaryBrush}"/>
  </Style>
  <Style Selector="Button.ghost:pointerover /template/ ContentPresenter">
    <Setter Property="Background" Value="{DynamicResource SurfaceMutedBrush}"/>
  </Style>

  <!-- Danger -->
  <Style Selector="Button.danger">
    <Setter Property="Background" Value="{DynamicResource DangerBrush}"/>
    <Setter Property="Foreground" Value="White"/>
  </Style>

  <!-- Icon-only (square) -->
  <Style Selector="Button.icon">
    <Setter Property="Padding" Value="8"/>
    <Setter Property="MinHeight" Value="36"/>
    <Setter Property="MinWidth" Value="36"/>
  </Style>

  <!-- Sizes -->
  <Style Selector="Button.sm">
    <Setter Property="MinHeight" Value="28"/>
    <Setter Property="Padding" Value="10,4"/>
    <Setter Property="FontSize" Value="13"/>
  </Style>
  <Style Selector="Button.lg">
    <Setter Property="MinHeight" Value="44"/>
    <Setter Property="Padding" Value="20,12"/>
    <Setter Property="FontSize" Value="15"/>
  </Style>

  <!-- Disabled override -->
  <Style Selector="Button:disabled">
    <Setter Property="Opacity" Value="0.5"/>
    <Setter Property="Cursor" Value="Arrow"/>
  </Style>
</Styles>
```

Usage:
```xml
<Button Classes="primary" Content="Save"/>
<Button Classes="secondary" Content="Cancel"/>
<Button Classes="ghost icon" ToolTip.Tip="Settings"
        AutomationProperties.Name="Settings">
  <PathIcon Data="{StaticResource SettingsIconGeometry}"/>
</Button>
<Button Classes="danger" Content="Delete account"/>
<Button Classes="primary lg" Content="Get started"/>
```

---

## Card

```xml
<Border Classes="card">
  <StackPanel Spacing="{StaticResource Space2}">
    <TextBlock Classes="h3" Text="Total revenue"/>
    <TextBlock FontSize="{StaticResource FontSize2xl}"
               FontWeight="SemiBold"
               Text="$48,294"/>
    <TextBlock Classes="muted" Text="+12.4% vs last month"/>
  </StackPanel>
</Border>
```

```xml
<Style Selector="Border.card">
  <Setter Property="Background" Value="{DynamicResource SurfaceElevatedBrush}"/>
  <Setter Property="BorderBrush" Value="{DynamicResource BorderBrush}"/>
  <Setter Property="BorderThickness" Value="1"/>
  <Setter Property="CornerRadius" Value="{StaticResource RadiusLg}"/>
  <Setter Property="Padding" Value="{StaticResource PaddingCard}"/>
  <Setter Property="BoxShadow" Value="{StaticResource ShadowSm}"/>
</Style>

<Style Selector="Border.card.interactive">
  <Setter Property="Cursor" Value="Hand"/>
  <Setter Property="Transitions">
    <Transitions>
      <BoxShadowsTransition Property="BoxShadow" Duration="0:0:0.15"/>
    </Transitions>
  </Setter>
</Style>
<Style Selector="Border.card.interactive:pointerover">
  <Setter Property="BoxShadow" Value="{StaticResource ShadowMd}"/>
</Style>
```

---

## Sidebar Navigation (FluentAvalonia NavigationView)

```xml
<ui:NavigationView xmlns:ui="using:FluentAvalonia.UI.Controls"
                   PaneDisplayMode="Left"
                   IsPaneToggleButtonVisible="True"
                   OpenPaneLength="240"
                   IsBackButtonVisible="False"
                   AlwaysShowHeader="False">
  <ui:NavigationView.MenuItems>
    <ui:NavigationViewItem Content="Dashboard" Tag="dashboard">
      <ui:NavigationViewItem.IconSource>
        <ui:SymbolIconSource Symbol="Home"/>
      </ui:NavigationViewItem.IconSource>
    </ui:NavigationViewItem>
    <ui:NavigationViewItem Content="Projects" Tag="projects">
      <ui:NavigationViewItem.IconSource>
        <ui:SymbolIconSource Symbol="Folder"/>
      </ui:NavigationViewItem.IconSource>
    </ui:NavigationViewItem>
    <ui:NavigationViewItemSeparator/>
    <ui:NavigationViewItem Content="Team" Tag="team">
      <ui:NavigationViewItem.IconSource>
        <ui:SymbolIconSource Symbol="People"/>
      </ui:NavigationViewItem.IconSource>
    </ui:NavigationViewItem>
  </ui:NavigationView.MenuItems>

  <ui:NavigationView.FooterMenuItems>
    <ui:NavigationViewItem Content="Settings" Tag="settings">
      <ui:NavigationViewItem.IconSource>
        <ui:SymbolIconSource Symbol="Setting"/>
      </ui:NavigationViewItem.IconSource>
    </ui:NavigationViewItem>
  </ui:NavigationView.FooterMenuItems>

  <ui:Frame x:Name="ContentFrame"/>
</ui:NavigationView>
```

For non-FluentAvalonia apps, build a sidebar with `SplitView`:

```xml
<SplitView IsPaneOpen="True"
           DisplayMode="CompactInline"
           OpenPaneLength="240"
           CompactPaneLength="56">
  <SplitView.Pane>
    <Border Background="{DynamicResource SurfaceMutedBrush}">
      <ListBox ItemsSource="{Binding NavItems}"
               SelectedItem="{Binding SelectedNav}"
               Background="Transparent">
        <ListBox.ItemTemplate>
          <DataTemplate>
            <StackPanel Orientation="Horizontal" Spacing="12">
              <PathIcon Data="{Binding IconGeometry}" Width="16" Height="16"/>
              <TextBlock Text="{Binding Label}" VerticalAlignment="Center"/>
            </StackPanel>
          </DataTemplate>
        </ListBox.ItemTemplate>
      </ListBox>
    </Border>
  </SplitView.Pane>
  <ContentControl Content="{Binding CurrentView}"/>
</SplitView>
```

---

## App Shell (Title bar + sidebar + content)

```xml
<Window xmlns="https://github.com/avaloniaui"
        ExtendClientAreaToDecorationsHint="True"
        ExtendClientAreaTitleBarHeightHint="40"
        TransparencyLevelHint="AcrylicBlur"
        Background="Transparent">
  <Panel>
    <ExperimentalAcrylicBorder IsHitTestVisible="False">
      <ExperimentalAcrylicBorder.Material>
        <ExperimentalAcrylicMaterial
          BackgroundSource="Digger"
          TintColor="{DynamicResource SurfaceBackgroundColor}"
          TintOpacity="1"
          MaterialOpacity="0.65"/>
      </ExperimentalAcrylicBorder.Material>
    </ExperimentalAcrylicBorder>

    <DockPanel>
      <!-- Custom title bar -->
      <Border DockPanel.Dock="Top" Height="40"
              IsHitTestVisible="False">
        <TextBlock Text="My App" Margin="16,0"
                   VerticalAlignment="Center"
                   Foreground="{DynamicResource TextSecondaryBrush}"/>
      </Border>

      <!-- Main content -->
      <ContentControl Content="{Binding CurrentView}"/>
    </DockPanel>
  </Panel>
</Window>
```

---

## Dialog (FluentAvalonia ContentDialog)

```csharp
var dialog = new ContentDialog
{
    Title = "Delete project?",
    Content = "This action cannot be undone. All files will be permanently deleted.",
    PrimaryButtonText = "Delete",
    CloseButtonText = "Cancel",
    DefaultButton = ContentDialogButton.Close
};
dialog.PrimaryButtonClick += (_, _) => viewModel.ConfirmDelete();
await dialog.ShowAsync();
```

For destructive actions, style the primary button with the danger class via `PrimaryButtonStyle`.

---

## Form with Inline Validation

```xml
<StackPanel Spacing="{StaticResource Space4}" MaxWidth="400">

  <StackPanel Spacing="{StaticResource Space1}">
    <TextBlock Text="Email" Classes="label"/>
    <TextBox Text="{Binding Email, Mode=TwoWay,
                            UpdateSourceTrigger=LostFocus}"
             Watermark="you@example.com"/>
    <TextBlock Text="{Binding EmailError}"
               IsVisible="{Binding HasEmailError}"
               Classes="error"/>
  </StackPanel>

  <StackPanel Spacing="{StaticResource Space1}">
    <TextBlock Text="Password" Classes="label"/>
    <TextBox PasswordChar="•"
             Text="{Binding Password, Mode=TwoWay}"/>
    <TextBlock Text="At least 12 characters" Classes="helper"/>
  </StackPanel>

  <Button Classes="primary lg"
          Content="Create account"
          Command="{Binding CreateAccountCommand}"
          IsEnabled="{Binding !IsBusy}"
          HorizontalAlignment="Stretch"/>
</StackPanel>
```

```xml
<Style Selector="TextBlock.label">
  <Setter Property="FontSize" Value="13"/>
  <Setter Property="FontWeight" Value="Medium"/>
  <Setter Property="Foreground" Value="{DynamicResource TextSecondaryBrush}"/>
</Style>
<Style Selector="TextBlock.helper">
  <Setter Property="FontSize" Value="12"/>
  <Setter Property="Foreground" Value="{DynamicResource TextMutedBrush}"/>
</Style>
<Style Selector="TextBlock.error">
  <Setter Property="FontSize" Value="12"/>
  <Setter Property="Foreground" Value="{DynamicResource DangerBrush}"/>
</Style>
<Style Selector="TextBox:error /template/ Border#PART_BorderElement">
  <Setter Property="BorderBrush" Value="{DynamicResource DangerBrush}"/>
</Style>
```

Use `INotifyDataErrorInfo` on the ViewModel; the `:error` pseudoclass auto-applies.

---

## Empty State

```xml
<Border Classes="card">
  <StackPanel Spacing="{StaticResource Space4}"
              HorizontalAlignment="Center"
              Margin="0,48">
    <PathIcon Data="{StaticResource InboxIconGeometry}"
              Width="48" Height="48"
              Foreground="{DynamicResource TextMutedBrush}"/>
    <TextBlock Classes="h3" Text="No projects yet"
               HorizontalAlignment="Center"/>
    <TextBlock Classes="muted"
               Text="Create your first project to get started"
               HorizontalAlignment="Center"
               TextAlignment="Center"
               MaxWidth="280"/>
    <Button Classes="primary"
            Content="New project"
            HorizontalAlignment="Center"
            Command="{Binding CreateProjectCommand}"/>
  </StackPanel>
</Border>
```

---

## Toast / Notification (Avalonia built-in)

```csharp
// In Window/UserControl
private WindowNotificationManager _notif;

protected override void OnLoaded(RoutedEventArgs e)
{
    base.OnLoaded(e);
    _notif = new WindowNotificationManager(TopLevel.GetTopLevel(this))
    {
        Position = NotificationPosition.BottomRight,
        MaxItems = 3
    };
}

_notif.Show(new Notification(
    "Project created",
    "‘Acme website redesign’ is ready.",
    NotificationType.Success));
```

---

## Badge

```xml
<Border CornerRadius="{StaticResource RadiusFull}"
        Background="{DynamicResource AccentBrush}"
        Padding="8,2"
        VerticalAlignment="Center">
  <TextBlock Text="{Binding Count}"
             FontSize="11"
             FontWeight="SemiBold"
             Foreground="White"/>
</Border>
```

Status variants: swap `Background` to `SuccessBrush`, `WarningBrush`, `DangerBrush`, or muted (`SurfaceMutedBrush` + `TextSecondaryBrush`).

---

## Skeleton (loading placeholder)

```xml
<Border Background="{DynamicResource SurfaceMutedBrush}"
        CornerRadius="{StaticResource RadiusSm}"
        Height="14" Width="180">
  <Border.Styles>
    <Style Selector="Border">
      <Style.Animations>
        <Animation Duration="0:0:1.4" IterationCount="Infinite">
          <KeyFrame Cue="0%"><Setter Property="Opacity" Value="0.4"/></KeyFrame>
          <KeyFrame Cue="50%"><Setter Property="Opacity" Value="0.8"/></KeyFrame>
          <KeyFrame Cue="100%"><Setter Property="Opacity" Value="0.4"/></KeyFrame>
        </Animation>
      </Style.Animations>
    </Style>
  </Border.Styles>
</Border>
```

Use Ursa.Avalonia's `Skeleton` control if you depend on Ursa.

---

## Settings Row (FluentAvalonia SettingsExpander pattern)

```xml
<StackPanel Spacing="{StaticResource Space3}">
  <ui:SettingsExpander Header="Appearance"
                       Description="Choose how the app looks">
    <ui:SettingsExpander.IconSource>
      <ui:SymbolIconSource Symbol="Color"/>
    </ui:SettingsExpander.IconSource>
    <ui:SettingsExpanderItem Content="Theme">
      <ui:SettingsExpanderItem.Footer>
        <ComboBox SelectedItem="{Binding SelectedTheme}"
                  ItemsSource="{Binding ThemeOptions}"
                  MinWidth="160"/>
      </ui:SettingsExpanderItem.Footer>
    </ui:SettingsExpanderItem>
    <ui:SettingsExpanderItem Content="Accent color">
      <ui:SettingsExpanderItem.Footer>
        <ColorPicker Color="{Binding AccentColor}"/>
      </ui:SettingsExpanderItem.Footer>
    </ui:SettingsExpanderItem>
  </ui:SettingsExpander>
</StackPanel>
```

---

## Common Mistakes

- **Hand-rolling button styles per view** — define once in `Styles/Buttons.axaml`, use `Classes="..."` everywhere.
- **`Padding="10"` on an icon-only button** — total target shrinks below 36px, fails 44pt accessibility on touch.
- **Forgetting `AutomationProperties.Name` on icon-only buttons** — screen readers announce nothing.
- **Validating with red-only feedback** — combine `:error` border with helper text.
- **Cards stacked at the same elevation** — use `ShadowSm` or 1px border, not `ShadowLg`, for in-page cards.
- **Using `ContentDialog` for non-blocking info** — use a toast/notification instead.
