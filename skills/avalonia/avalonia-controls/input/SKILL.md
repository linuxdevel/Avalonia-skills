---
name: avalonia-controls-input
description: Use when working with Avalonia input controls: Button, ToggleButton, RadioButton, CheckBox, TextBox, ComboBox, Slider, Calendar, DatePicker, TimePicker, NumericUpDown, or VirtualKeyboard. Covers key properties, events, binding patterns, and common pitfalls for each control in Avalonia 12.
---

# Avalonia Input Controls

## Overview

Input controls capture user data or trigger actions. All support `IsEnabled`, `IsVisible`, and standard styling.

---

## Button

| Property | Type | Notes |
|---|---|---|
| `Content` | `object` | Any content, including XAML subtrees |
| `Command` | `ICommand` | Bound command; auto-manages `IsEnabled` |
| `CommandParameter` | `object` | Passed to command |
| `IsDefault` | `bool` | Triggers on Enter |
| `IsCancel` | `bool` | Triggers on Escape |
| `ClickMode` | `ClickMode` | `Release` (default), `Press`, `Hover` |

**Events:** `Click`

**Variants:** `RepeatButton` (fires `Click` repeatedly while held), `ToggleButton` (stateful press)

```xml
<!-- Simple command button -->
<Button Content="Save" Command="{Binding SaveCommand}" IsDefault="True"/>

<!-- Button with icon + text -->
<Button Click="OnClick">
    <StackPanel Orientation="Horizontal" Spacing="8">
        <PathIcon Data="M17 3H5c-1.1 0-2 .9-2 2v14l7-3 7 3V5c0-1.1-.9-2-2-2z" Width="16" Height="16"/>
        <TextBlock Text="Save" VerticalAlignment="Center"/>
    </StackPanel>
</Button>

<!-- RepeatButton -->
<RepeatButton Content="+" Command="{Binding IncrementCommand}" Delay="400" Interval="100"/>

<!-- ToggleButton -->
<ToggleButton Content="Bold" IsChecked="{Binding IsBold}"/>
```

---

## CheckBox

| Property | Type | Notes |
|---|---|---|
| `IsChecked` | `bool?` | `null` = indeterminate |
| `IsThreeState` | `bool` | Enables null/indeterminate state |
| `Content` | `object` | Label displayed next to box |

```xml
<!-- Basic binding -->
<CheckBox Content="Enable notifications" IsChecked="{Binding IsNotificationsEnabled}"/>

<!-- Three-state -->
<CheckBox Content="Select all" IsThreeState="True" IsChecked="{Binding AllSelected}"/>
```

```csharp
// Handle indeterminate in ViewModel
private bool? _allSelected;
public bool? AllSelected
{
    get => _allSelected;
    set => SetProperty(ref _allSelected, value);
}
```

---

## RadioButton

| Property | Type | Notes |
|---|---|---|
| `IsChecked` | `bool` | TwoWay by default |
| `GroupName` | `string` | Groups buttons across panels |
| `Content` | `object` | Label |

```xml
<!-- Grouped by GroupName -->
<StackPanel>
    <RadioButton Content="Small" GroupName="Size" IsChecked="{Binding IsSmall}"/>
    <RadioButton Content="Medium" GroupName="Size" IsChecked="{Binding IsMedium}"/>
    <RadioButton Content="Large" GroupName="Size" IsChecked="{Binding IsLarge}"/>
</StackPanel>

<!-- Grouped by parent panel (no GroupName needed) -->
<StackPanel>
    <RadioButton Content="Option A"/>
    <RadioButton Content="Option B"/>
</StackPanel>
```

> **Tip:** For enum-based selection, bind each `IsChecked` to a converter comparing the enum value, or use `ItemsControl` with `RadioButton` items.

---

## TextBox

| Property | Type | Notes |
|---|---|---|
| `Text` | `string` | TwoWay by default — do **not** add `Mode=TwoWay` |
| `Watermark` | `string` | Placeholder text |
| `MaxLength` | `int` | 0 = unlimited |
| `AcceptsReturn` | `bool` | Multiline input |
| `TextWrapping` | `TextWrapping` | `NoWrap`, `Wrap`, `WrapWithOverflow` |
| `IsReadOnly` | `bool` | Prevents editing |
| `PasswordChar` | `char` | Masks input (e.g. `•`) |
| `SelectionStart` | `int` | Caret/selection start |
| `SelectionLength` | `int` | Selection length |
| `InnerLeftContent` | `object` | Icon inside left edge |
| `InnerRightContent` | `object` | Icon inside right edge |

**Events:** `TextChanged`, `TextChanging`, `LostFocus`, `KeyDown`

```xml
<!-- Basic -->
<TextBox Watermark="Enter name..." Text="{Binding Name}" MaxLength="100"/>

<!-- Multiline -->
<TextBox AcceptsReturn="True" TextWrapping="Wrap" Height="120" Text="{Binding Notes}"/>

<!-- Password -->
<TextBox PasswordChar="•" Watermark="Password" Text="{Binding Password}"/>

<!-- With inner icon -->
<TextBox Watermark="Search...">
    <TextBox.InnerLeftContent>
        <PathIcon Data="M15.5 14h-.79l-.28-.27A6.471..." Width="16" Height="16" Margin="4,0"/>
    </TextBox.InnerLeftContent>
</TextBox>
```

---

## ComboBox

| Property | Type | Notes |
|---|---|---|
| `ItemsSource` | `IEnumerable` | Bound collection |
| `SelectedItem` | `object` | TwoWay by default |
| `SelectedIndex` | `int` | Zero-based |
| `SelectedValue` | `object` | Used with `SelectedValueBinding` |
| `IsEditable` | `bool` | Allows text entry |
| `PlaceholderText` | `string` | Shown when nothing selected |
| `MaxDropDownHeight` | `double` | Limits dropdown height |

```xml
<!-- Basic binding -->
<ComboBox ItemsSource="{Binding Options}"
          SelectedItem="{Binding SelectedOption}"
          PlaceholderText="Select..."/>

<!-- Custom item template -->
<ComboBox ItemsSource="{Binding Countries}" SelectedItem="{Binding SelectedCountry}">
    <ComboBox.ItemTemplate>
        <DataTemplate x:DataType="vm:CountryVm">
            <StackPanel Orientation="Horizontal" Spacing="8">
                <Image Source="{Binding FlagUri}" Width="20" Height="14"/>
                <TextBlock Text="{Binding Name}"/>
            </StackPanel>
        </DataTemplate>
    </ComboBox.ItemTemplate>
</ComboBox>

<!-- Editable ComboBox -->
<ComboBox IsEditable="True" ItemsSource="{Binding Suggestions}" Text="{Binding InputText}"/>
```

---

## Slider

| Property | Type | Notes |
|---|---|---|
| `Minimum` | `double` | Default: 0 |
| `Maximum` | `double` | Default: 100 |
| `Value` | `double` | TwoWay by default |
| `TickFrequency` | `double` | Interval between ticks |
| `IsSnapToTickEnabled` | `bool` | Snaps value to tick marks |
| `Orientation` | `Orientation` | `Horizontal` (default), `Vertical` |
| `IsDirectionReversed` | `bool` | Inverts direction |
| `TickPlacement` | `TickPlacement` | `None`, `TopLeft`, `BottomRight`, `Outside` |

```xml
<!-- Horizontal volume slider -->
<Slider Minimum="0" Maximum="100" Value="{Binding Volume}"
        TickFrequency="10" IsSnapToTickEnabled="True" TickPlacement="BottomRight"/>

<!-- Vertical slider -->
<Slider Orientation="Vertical" Minimum="0" Maximum="1"
        Value="{Binding Opacity}" Height="200"/>
```

---

## NumericUpDown

| Property | Type | Notes |
|---|---|---|
| `Value` | `decimal?` | TwoWay by default |
| `Minimum` | `decimal?` | Lower bound |
| `Maximum` | `decimal?` | Upper bound |
| `Increment` | `decimal` | Step per click |
| `FormatString` | `string` | e.g. `"F2"`, `"N0"`, `"C2"` |
| `AllowSpin` | `bool` | Show up/down buttons |
| `ShowButtonSpinner` | `bool` | Toggle spinner visibility |
| `NumberFormat` | `NumberFormatInfo` | Culture-specific formatting |

```xml
<!-- Integer quantity -->
<NumericUpDown Value="{Binding Quantity}" Minimum="1" Maximum="999" Increment="1" FormatString="N0"/>

<!-- Decimal with currency -->
<NumericUpDown Value="{Binding Price}" Minimum="0" Increment="0.01" FormatString="C2"/>

<!-- No spinner buttons -->
<NumericUpDown Value="{Binding Amount}" AllowSpin="False"/>
```

---

## Calendar

| Property | Type | Notes |
|---|---|---|
| `SelectedDate` | `DateTime?` | Selected date |
| `DisplayMode` | `CalendarMode` | `Month`, `Year`, `Decade` |
| `DisplayDate` | `DateTime` | Currently displayed month |
| `BlackoutDates` | `CalendarBlackoutDatesCollection` | Disabled dates |
| `IsTodayHighlighted` | `bool` | Highlights today |
| `SelectionMode` | `CalendarSelectionMode` | `SingleDate`, `SingleRange`, `MultipleRange`, `None` |

```xml
<Calendar SelectedDate="{Binding SelectedDate}"
          DisplayMode="Month"
          IsTodayHighlighted="True"/>

<!-- With blackout dates in code-behind -->
```

```csharp
calendar.BlackoutDates.Add(new CalendarDateRange(DateTime.Today.AddDays(1), DateTime.Today.AddDays(7)));
```

---

## DatePicker

| Property | Type | Notes |
|---|---|---|
| `SelectedDate` | `DateTimeOffset?` | Note: **not** `DateTime` |
| `DisplayDateStart` | `DateTimeOffset?` | Earliest selectable |
| `DisplayDateEnd` | `DateTimeOffset?` | Latest selectable |
| `Watermark` | `string` | Placeholder |
| `DayFormat` | `string` | Day display format |
| `MonthFormat` | `string` | Month display format |
| `YearFormat` | `string` | Year display format |

```xml
<DatePicker SelectedDate="{Binding BirthDate}" Watermark="Select date"/>

<!-- Restrict range -->
<DatePicker SelectedDate="{Binding AppointmentDate}"
            DisplayDateStart="{Binding TodayOffset}"
            DisplayDateEnd="{Binding MaxDateOffset}"/>
```

```csharp
// Convert DateTimeOffset? to DateTime for use
DateTime? date = picker.SelectedDate?.DateTime;
```

---

## TimePicker

| Property | Type | Notes |
|---|---|---|
| `SelectedTime` | `TimeSpan?` | Selected time value |
| `ClockIdentifier` | `string` | `"12HourClock"` or `"24HourClock"` |
| `MinuteIncrement` | `int` | Snap interval (1–59) |

```xml
<TimePicker SelectedTime="{Binding MeetingTime}" ClockIdentifier="24HourClock"/>

<TimePicker SelectedTime="{Binding AlarmTime}" ClockIdentifier="12HourClock" MinuteIncrement="15"/>
```

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| `TextBox Text="{Binding X, Mode=TwoWay}"` | Remove `Mode=TwoWay` — it's the default |
| `ComboBox` with value types, `SelectedItem` not working | Use `SelectedIndex` or ensure proper equality; value types match by value but boxed objects may not |
| All `RadioButton`s in same panel auto-group | Use `GroupName` to separate groups across panels or force cross-panel grouping |
| `DatePicker.SelectedDate` typed as `DateTime` | It's `DateTimeOffset?` — convert with `.DateTime` |
| `NumericUpDown.Value` typed as `double` | It's `decimal?` — use `decimal` in ViewModel |
| `TextBox` binding not updating on every keystroke | Default updates on `LostFocus`; use `UpdateSourceTrigger=PropertyChanged` if needed |
| `PasswordChar` with compiled bindings | No issue, but `Text` binding exposes password in ViewModel — consider `SecureString` patterns |
