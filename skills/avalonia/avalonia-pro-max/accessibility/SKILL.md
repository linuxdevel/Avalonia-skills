---
name: avalonia-pro-max/accessibility
description: Use when adding or auditing accessibility in an Avalonia app — AutomationProperties, focus order, keyboard navigation, contrast, screen reader (Narrator/NVDA/VoiceOver/Orca) support, dynamic text scaling, reduced motion. Maps WCAG 2.2 AA to Avalonia APIs.
---

# Accessibility in Avalonia

Avalonia exposes accessibility through:

| API | Purpose |
|---|---|
| `AutomationProperties.*` attached props | Names, descriptions, roles, item status |
| `Focusable` / `IsTabStop` / `TabIndex` | Keyboard traversal |
| Focus pseudoclasses (`:focus`, `:focus-visible`, `:focus-within`) | Visible focus indication |
| `KeyBindings`, `HotKey`, `KeyGesture` | Shortcuts |
| `RequestedThemeVariant`, `PlatformSettings` | High-contrast / dark mode / reduced motion |
| `AccessKey` (`_File`) | Mnemonic underline shortcuts |
| `ToolTip.Tip` | Hover and screen-reader hints |

Targets: WCAG 2.2 AA, plus Windows UI Automation, macOS NSAccessibility, Linux AT-SPI.

---

## AutomationProperties (Required)

```xml
<Button Command="{Binding DeleteCommand}"
        AutomationProperties.Name="Delete project"
        AutomationProperties.HelpText="Permanently removes the current project and all its files">
  <PathIcon Data="{StaticResource TrashIconGeometry}"/>
</Button>
```

Common properties:

| Property | When | Example |
|---|---|---|
| `AutomationProperties.Name` | Always for icon-only / image-only / unlabeled controls | `"Search"` |
| `AutomationProperties.HelpText` | Long-form explanation | `"Searches across all projects"` |
| `AutomationProperties.AcceleratorKey` | Display the keyboard shortcut | `"Ctrl+K"` |
| `AutomationProperties.AccessibilityView` | `Content` / `Control` / `Raw` — control visibility to AT | `Raw` for purely decorative |
| `AutomationProperties.IsRequiredForForm` | Required form fields | `True` |
| `AutomationProperties.LabeledBy` | When a `TextBlock` labels another control | `{Binding ElementName=EmailLabel}` |
| `AutomationProperties.LiveSetting` | Polite/Assertive live regions | `Polite` for toasts |
| `AutomationProperties.ItemStatus` | Dynamic state (e.g., "Saving…") | `"3 of 5 selected"` |
| `AutomationProperties.AutomationId` | Stable test id (for UI tests, also used by AT) | `"login.submit"` |

### Hide decorative elements

```xml
<PathIcon Data="{StaticResource ChevronGeometry}"
          AutomationProperties.AccessibilityView="Raw"/>
```

### Label association

```xml
<TextBlock x:Name="EmailLabel" Text="Email"/>
<TextBox AutomationProperties.LabeledBy="{Binding ElementName=EmailLabel}"/>
```

---

## Focus Indication (Never Remove)

FluentTheme ships a focus ring. If you replace a ControlTheme, re-add it:

```xml
<Style Selector="Button:focus-visible /template/ ContentPresenter">
  <Setter Property="BorderBrush" Value="{DynamicResource AccentBrush}"/>
  <Setter Property="BorderThickness" Value="2"/>
</Style>
```

`:focus-visible` activates only when focus arrived from keyboard — preferred over `:focus` so mouse clicks don't show the ring. Always provide some visible cue on `:focus` too in case `:focus-visible` is not detected.

Minimum: 2px ring, contrast ≥3:1 against the surface.

---

## Keyboard Navigation

### Tab order
- Tab order follows logical tree by default.
- Override via `TabIndex="N"` (lower = earlier).
- `IsTabStop="False"` on labels and decorative containers.
- Group containers: set `KeyboardNavigation.TabNavigation="Local"` on a panel to scope Tab within it.

### Modes
```xml
<StackPanel KeyboardNavigation.TabNavigation="Cycle"
            KeyboardNavigation.DirectionalNavigation="Contained">
  …
</StackPanel>
```

| Mode | Effect |
|---|---|
| `Continue` (default) | Tab traverses normally |
| `Local` | Tab cycles within the container |
| `Cycle` | Cycles within and stops |
| `Once` | Container as a whole gets one tab stop |
| `None` | Skipped |

### Arrow-key navigation

Set `KeyboardNavigation.DirectionalNavigation` for Lists/grids to allow arrow keys.

### Mnemonics

```xml
<MenuItem Header="_File"/>   <!-- Alt+F -->
<Button Content="_Save" Command="{Binding SaveCommand}"/>
```

### Shortcuts

```xml
<Window>
  <Window.KeyBindings>
    <KeyBinding Gesture="Ctrl+S" Command="{Binding SaveCommand}"/>
    <KeyBinding Gesture="Ctrl+K" Command="{Binding OpenSearchCommand}"/>
    <KeyBinding Gesture="Cmd+S"  Command="{Binding SaveCommand}"/>  <!-- macOS -->
  </Window.KeyBindings>
</Window>
```

Also expose as `HotKey` on a Button:
```xml
<Button Content="Save" HotKey="Ctrl+S" Command="{Binding SaveCommand}"/>
```

---

## Color Contrast

| Element | Min ratio | Tool |
|---|---|---|
| Body text on background | 4.5 : 1 | WCAG AA |
| Large text (≥18px / ≥14px bold) | 3 : 1 | WCAG AA |
| UI components (icon, focus ring, border) | 3 : 1 | WCAG 2.2 |
| Disabled text | exempt (but make it clearly disabled) | — |

Validate every brush pair light **and** dark. Common pitfalls:
- `TextMutedBrush` over `SurfaceBrush` often fails — use Slate 600+ on light, Slate 400+ on dark.
- Accent text on white usually needs Blue 600+, not Blue 500.
- Disabled buttons at 50% opacity may fail 3:1 against accent.

---

## Don't Convey by Color Alone

**Bad:** Status as a single colored dot.
**Good:** Color + icon + text:

```xml
<StackPanel Orientation="Horizontal" Spacing="6">
  <Ellipse Width="8" Height="8"
           Fill="{DynamicResource SuccessBrush}"
           AutomationProperties.AccessibilityView="Raw"/>
  <PathIcon Data="{StaticResource CheckGeometry}" Width="14" Height="14"
            Foreground="{DynamicResource SuccessBrush}"
            AutomationProperties.AccessibilityView="Raw"/>
  <TextBlock Text="Active" Foreground="{DynamicResource TextPrimaryBrush}"/>
</StackPanel>
```

---

## Forms — Accessible Validation

```xml
<StackPanel Spacing="4">
  <TextBlock x:Name="LblEmail" Text="Email"/>
  <TextBox Text="{Binding Email}"
           AutomationProperties.LabeledBy="{Binding ElementName=LblEmail}"
           AutomationProperties.IsRequiredForForm="True"/>
  <TextBlock Text="{Binding EmailError}"
             IsVisible="{Binding HasEmailError}"
             Foreground="{DynamicResource DangerBrush}"
             AutomationProperties.LiveSetting="Polite"/>
</StackPanel>
```

Move focus to first invalid field on submit:
```csharp
if (!IsValid && firstInvalid is Control c) c.Focus(NavigationMethod.Tab);
```

---

## Screen Reader Live Regions (Toasts)

```xml
<TextBlock x:Name="StatusLine"
           Text="{Binding Status}"
           AutomationProperties.LiveSetting="Polite"
           AutomationProperties.Name="Status"/>
```

`Polite` waits until idle; `Assertive` interrupts. Use `Assertive` only for errors and important blocks.

---

## Dynamic Text Scaling

Avoid fixed `FontSize` literals in views — drive everything from your `FontSize*` resources. Bind a global scale factor when needed:

```xml
<TextBlock FontSize="{Binding FontSize, Source={x:Static app:UserPrefs.Instance},
                              Converter={StaticResource ScaleConverter}}"/>
```

Avoid:
- Fixed `Height` on text containers — text gets clipped at 200% scale.
- `MaxLines="1"` without `TextTrimming="CharacterEllipsis"` and a tooltip.

Test at 100%, 150%, 200% OS DPI scaling.

---

## High-Contrast Mode

Windows high-contrast: FluentTheme adapts most colors. For custom controls:

```xml
<Style Selector="Border.card">
  <Setter Property="BorderBrush" Value="{DynamicResource SystemControlForegroundBaseHighBrush}"/>
  <Setter Property="BorderThickness" Value="1"/>
</Style>
```

Or supply a third theme dictionary keyed `HighContrast` (Avalonia respects custom variants when registered).

---

## Touch Targets

Even on desktop, touch users exist (Surface, tablet, kiosk). Min visible size **or** padded hit-area: 36×36 px (desktop), 44×44 px (touch/mobile).

Expand hit area without enlarging visual:
```xml
<Button Padding="10" MinWidth="36" MinHeight="36">
  <PathIcon Data="…" Width="16" Height="16"/>
</Button>
```

Keep ≥8 px between adjacent tap targets.

---

## Reduced Motion

See `avalonia-pro-max/motion` — every animation must have a zero-duration fallback.

---

## Testing

- Tab through every screen — can you reach and operate every control?
- Activate Windows Narrator / macOS VoiceOver / Orca — read each major screen.
- Run the app at OS DPI 200%.
- Toggle high contrast.
- Use the Avalonia DevTools `Visual Tree` → look for unnamed actionable controls.
- For UI tests, set `AutomationProperties.AutomationId` on every control under test.

---

## Common Mistakes

- **Icon-only button without `AutomationProperties.Name`** — invisible to screen readers.
- **Removed focus ring "for cleanliness"** — keyboard users are blocked.
- **`TextBlock` used as a clickable header** — not focusable, no role; use `Button.ghost` instead.
- **Color-only error indication** — colorblind users miss it.
- **`MaxLines` truncation without tooltip** — text scaled to 200% gets clipped silently.
- **`KeyBinding` on `Window` only** — won't fire if focus is in a TextBox that swallows the key. Use `RoutedCommand` or also bind on the TextBox.
- **Different shortcuts on Win vs macOS not provided** — provide both `Ctrl+` and `Cmd+`.
- **`AutomationProperties.AccessibilityView="Raw"` on a meaningful control** — hides it entirely.
- **Missing `AutomationProperties.LabeledBy`** between visible label and input.
