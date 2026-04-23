---
name: avalonia-styling
description: Use when applying styles, control themes, pseudoclasses, style selectors, theme variants, or custom fonts in Avalonia. Covers Style vs ControlTheme distinction, selector syntax, nested styles, light/dark theme variants, style sharing via avares://, StyleKeyOverride, and style precedence rules.
---

# Avalonia Styling

## Overview

Three mechanisms for visual styling in Avalonia:

| Mechanism | Analogous to | Use for |
|---|---|---|
| `Style` | CSS | App-specific visual rules, typography, spacing, state |
| `ControlTheme` | WPF Style + ControlTemplate | Restyling entire control appearance (lookless) |
| `ContainerQuery` | CSS container queries | Responsive styles based on container size |

Styles cascade up the logical tree. ControlThemes live in `Resources`, not `Styles`.

---

## Writing Styles

Selector + Setters. Place in `Window.Styles`, `UserControl.Styles`, or `App.axaml` for global.

```xml
<Window.Styles>
    <Style Selector="TextBlock.h1">
        <Setter Property="FontSize" Value="24"/>
        <Setter Property="FontWeight" Value="Bold"/>
        <!-- Nested: ^ refers to parent selector (TextBlock.h1) -->
        <Style Selector="^:pointerover">
            <Setter Property="Foreground" Value="Red"/>
        </Style>
    </Style>
</Window.Styles>
```

Multiple setters, one selector:
```xml
<Style Selector="Button.primary">
    <Setter Property="Background" Value="#0078D4"/>
    <Setter Property="Foreground" Value="White"/>
    <Setter Property="Padding" Value="16,8"/>
</Style>
```

---

## Style Selector Syntax

| Selector | Syntax | Matches |
|---|---|---|
| Type | `Button` | All Buttons |
| Class | `.myClass` | Controls with that style class |
| Type + Class | `Button.primary` | Buttons with class `primary` |
| Name | `#myName` | Control with `x:Name="myName"` |
| Direct child | `StackPanel > Button` | Button as direct child of StackPanel |
| Descendant | `StackPanel Button` | Any Button inside StackPanel |
| Pseudoclass | `:pointerover` | State-based match |
| Property value | `[IsChecked=True]` | Property equals value |
| Template part | `/template/ ContentPresenter` | Element inside ControlTemplate |
| Nesting | `^` | Parent selector (nested styles only) |
| Or | `Button, TextBlock` | Either type |
| Not | `:not(.primary)` | Negation |
| Is (type check) | `:is(Button)` | Includes subtypes |

---

## Pseudoclasses

Built-in: `:pointerover`, `:pressed`, `:disabled`, `:focus`, `:focus-within`, `:focus-visible`, `:checked`, `:unchecked`, `:indeterminate`, `:selected`, `:expanded`, `:collapsed`, `:empty`, `:nth-child(n)`, `:nth-last-child(n)`, `:first-child`, `:last-child`

Custom pseudoclass in code-behind or ViewModel:
```csharp
// In a custom control
PseudoClasses.Set(":loading", isLoading);
```

Then target in XAML:
```xml
<Style Selector="local|MyControl:loading">
    <Setter Property="Opacity" Value="0.5"/>
</Style>
```

---

## Style Classes

Declare on control:
```xml
<Button Classes="primary large">Click</Button>
```

Add/remove in code:
```csharp
myButton.Classes.Add("active");
myButton.Classes.Remove("active");
myButton.Classes.Set("active", condition); // toggle
```

Conditional class binding:
```xml
<Button Classes.active="{Binding IsActive}"/>
```

Multiple classes:
```xml
<Button Classes.primary="{Binding IsPrimary}" Classes.large="{Binding IsLarge}"/>
```

---

## Control Themes

ControlThemes replace the entire visual tree of a control. Must go in `Resources`, not `Styles`.

```xml
<Application.Resources>
    <ControlTheme x:Key="{x:Type Button}" TargetType="Button">
        <Setter Property="Background" Value="#E0E0E0"/>
        <Setter Property="Template">
            <ControlTemplate>
                <Border Background="{TemplateBinding Background}"
                        CornerRadius="4"
                        Padding="{TemplateBinding Padding}">
                    <ContentPresenter Content="{TemplateBinding Content}"/>
                </Border>
            </ControlTemplate>
        </Setter>
        <!-- State styles inside ControlTheme -->
        <Style Selector="^:pointerover /template/ Border">
            <Setter Property="Background" Value="#C0C0C0"/>
        </Style>
        <Style Selector="^:pressed /template/ Border">
            <Setter Property="Background" Value="#A0A0A0"/>
        </Style>
    </ControlTheme>
</Application.Resources>
```

Extend existing theme with `BasedOn`:
```xml
<ControlTheme x:Key="OutlineButton" TargetType="Button"
              BasedOn="{StaticResource {x:Type Button}}">
    <Setter Property="BorderThickness" Value="2"/>
    <Setter Property="Background" Value="Transparent"/>
</ControlTheme>
```

Apply a named ControlTheme:
```xml
<Button Theme="{StaticResource OutlineButton}">Outlined</Button>
```

---

## Theme Variants (Light / Dark)

Set on Window or Application:
```xml
<Window RequestedThemeVariant="Dark">
```

```csharp
Application.Current!.RequestedThemeVariant = ThemeVariant.Dark;
```

Theme-variant resources:
```xml
<ResourceDictionary>
    <ResourceDictionary.ThemeDictionaries>
        <ResourceDictionary x:Key="Light">
            <SolidColorBrush x:Key="SurfaceBrush" Color="#FFFFFF"/>
        </ResourceDictionary>
        <ResourceDictionary x:Key="Dark">
            <SolidColorBrush x:Key="SurfaceBrush" Color="#1E1E1E"/>
        </ResourceDictionary>
    </ResourceDictionary.ThemeDictionaries>
</ResourceDictionary>
```

Consume with `DynamicResource` (not `StaticResource`):
```xml
<Border Background="{DynamicResource SurfaceBrush}"/>
```

---

## Built-in Themes

```xml
<!-- App.axaml -->
<Application.Styles>
    <FluentTheme/>
    <!-- or -->
    <SimpleTheme/>
</Application.Styles>
```

NuGet packages:
- `Avalonia.Themes.Fluent` — Microsoft Fluent design
- `Avalonia.Themes.Simple` — minimal, no external dependencies

---

## Sharing Styles

Include an external `.axaml` file:
```xml
<Window.Styles>
    <StyleInclude Source="avares://MyApp/Styles/Buttons.axaml"/>
</Window.Styles>
```

Or at app level:
```xml
<Application.Styles>
    <FluentTheme/>
    <StyleInclude Source="avares://MyApp/Styles/Global.axaml"/>
</Application.Styles>
```

Merge ResourceDictionary:
```xml
<Application.Resources>
    <ResourceDictionary>
        <ResourceDictionary.MergedDictionaries>
            <ResourceInclude Source="avares://MyApp/Resources/Colors.axaml"/>
        </ResourceDictionary.MergedDictionaries>
    </ResourceDictionary>
</Application.Resources>
```

`avares://` URI scheme references embedded resources from the assembly. The format is `avares://AssemblyName/Path/To/File.axaml`.

---

## StyleKeyOverride

Causes a custom control subclass to pick up styles targeting its base type:
```csharp
public class MyButton : Button
{
    // This control will be styled as Button, not MyButton
    protected override Type StyleKeyOverride => typeof(Button);
}
```

Useful when subclassing a control only for behavior changes, not visual identity.

---

## ContainerQuery (Responsive Styles)

```xml
<Style Selector="local|MyPanel">
    <Style Selector="^ /template/ TextBlock">
        <ContainerQuery MinWidth="400">
            <Setter Property="FontSize" Value="18"/>
        </ContainerQuery>
        <ContainerQuery MaxWidth="399">
            <Setter Property="FontSize" Value="12"/>
        </ContainerQuery>
    </Style>
</Style>
```

---

## Style Precedence (Highest to Lowest)

1. Inline property set (e.g., `<Button Background="Red"/>`)
2. Animations
3. Template bindings (`{TemplateBinding}`)
4. Local style (closest scope — Window or UserControl)
5. Inherited styles (further up logical tree — App.axaml)

---

## Common Mistakes

- **Using WPF `Triggers`** — does not exist in Avalonia. Use pseudoclasses + nested styles instead.
- **Forgetting `^` in nested selectors** — `<Style Selector=":pointerover">` inside another Style does not scope to the parent; must be `<Style Selector="^:pointerover">`.
- **Putting ControlTheme in `Window.Styles`** — ControlThemes must go in `Window.Resources` or `Application.Resources`, not `Styles`.
- **Using `StaticResource` for theme-variant resources** — theme variant resources must be referenced with `DynamicResource` to react to variant changes at runtime.
- **Confusing Styles and ControlThemes** — Styles add/override individual property values; ControlThemes replace the entire visual template. If you only need color or font changes, use a Style.
- **`/template/` selector outside ControlTheme** — the `/template/` segment only works when targeting elements inside a ControlTemplate, typically from within a ControlTheme state style.
