---
name: avalonia-pro-max/review-checklist
description: Use before merging a PR or shipping a release of an Avalonia app — exhaustive pre-delivery checklist covering visual quality, interaction, light/dark, layout, accessibility, performance, motion, and platform parity. Run end-to-end; fix everything before sign-off.
---

# Avalonia UI Pre-Delivery Checklist

Run this before merging UI work or cutting a release. Each item maps back to a sub-skill if it fails.

## How to Use

1. Open every screen at default window size and at compact (640 px wide) and wide (1600+ px).
2. Toggle `RequestedThemeVariant` between Light and Dark.
3. Tab through every screen with the keyboard only.
4. Run a screen reader on the main flows (Narrator on Win, VoiceOver on macOS).
5. Profile a session with Avalonia DevTools (`F12`) for layout/render issues.
6. Tick each box. If anything fails → fix → re-run from the top.

---

## Design Tokens & Theming → `design-system`

- [ ] No hard-coded color hex values in any view (all via `DynamicResource`)
- [ ] No magic spacing numbers — every `Margin`/`Padding` references the spacing scale
- [ ] No magic font sizes — every `FontSize` references the type scale
- [ ] Both `Light` and `Dark` theme dictionaries provided for every semantic brush
- [ ] App responds correctly when OS theme changes at runtime
- [ ] One accent color, used consistently
- [ ] Text/background pairs verified ≥4.5:1 in both themes
- [ ] Disabled states use a token, not arbitrary opacity

## Theme Library → `themes`

- [ ] Exactly one base theme imported (no Fluent + Material conflict)
- [ ] Theme NuGets at supported version for the Avalonia version in use
- [ ] No app code depends on internal theme NuGet brush keys (only via own semantic tokens)
- [ ] Custom title bar / SukiWindow / chrome behaves on Win, macOS, Linux

## Component Quality → `components`

- [ ] All buttons use shared classes (`primary` / `secondary` / `ghost` / `danger` / `icon`)
- [ ] Icon-only buttons have ≥36×36 hit area (desktop) or 44×44 (touch)
- [ ] Cards use the shared `Border.card` style — no per-view ad-hoc cards
- [ ] Forms have visible labels (not placeholder-only)
- [ ] Form errors render inline, not only in a top banner
- [ ] Destructive actions confirmed via dialog or use `danger` class
- [ ] Empty states show icon + headline + description + CTA
- [ ] Loading states use skeleton or progress indicator (not spinner alone for >1s)
- [ ] Toasts auto-dismiss in 3–5s and are not focus-stealing
- [ ] No "click here" — link/button labels describe their action

## Motion → `motion`

- [ ] Hover/press feedback ≤150 ms
- [ ] Page transitions 200–300 ms with easing
- [ ] No `Width` / `Height` / `Margin` animation
- [ ] All `Transitions` declarations have explicit `Easing`
- [ ] Exit animations ~70% of enter duration
- [ ] At most 2–3 concurrent animations per visible screen
- [ ] Reduced-motion path tested (durations → zero)
- [ ] Looping animations used sparingly and only on small elements

## Accessibility → `accessibility`

- [ ] Every icon-only button has `AutomationProperties.Name`
- [ ] Every form input is associated with a `LabeledBy` or visible `<TextBlock>` label
- [ ] Required fields marked with `AutomationProperties.IsRequiredForForm`
- [ ] Tab order matches visual reading order
- [ ] Focus ring visible (not removed) on every interactive element
- [ ] No information conveyed by color alone (icon/text always paired)
- [ ] Live regions (`AutomationProperties.LiveSetting`) on toast / status updates
- [ ] Screen reader reads each main screen meaningfully
- [ ] Verified at OS DPI 100/150/200%
- [ ] Verified in Windows High Contrast (or platform equivalent)
- [ ] All keyboard shortcuts present on macOS as `Cmd` and Windows as `Ctrl`
- [ ] No `MaxLines` truncation without tooltip access to full text

## Layout & Responsive → `layout-patterns`

- [ ] No fixed-pixel layout that breaks at 800-px window width
- [ ] Long-form text capped with `MaxWidth` (~720 px reading width)
- [ ] Long lists use `VirtualizingStackPanel` / `ItemsRepeater`
- [ ] Single vertical scroll per view (no nested scroll regions)
- [ ] `MinWidth`/`MinHeight` on `Window` set to a reasonable floor (e.g., 800×600)
- [ ] Sidebar collapses or overlays on compact widths
- [ ] Right panel hidden on compact widths
- [ ] Page padding scales (24+ desktop / 16 compact)
- [ ] Cards reflow (UniformGrid columns / WrapPanel) at narrow widths

## Icons & Imagery → `icons-imagery`

- [ ] Single icon family across the app
- [ ] Icon sizes from the size scale token, never magic numbers
- [ ] Icons square (`Width == Height`)
- [ ] Icon `Foreground`/`StrokeBrush` bound to a semantic token
- [ ] No emoji used as a structural icon
- [ ] Brand logo is the official asset, correct proportions
- [ ] App icons supplied at all required sizes (Win ICO, macOS ICNS, Linux PNG set)
- [ ] PNG raster images compressed
- [ ] Network images loaded asynchronously with placeholder

## Performance

- [ ] `CompiledBindings` enabled (default in Avalonia 11+)
- [ ] No `INotifyPropertyChanged` storms — verify with Avalonia DevTools
- [ ] No allocation in `Render()` overrides
- [ ] Lists ≥100 items virtualized
- [ ] Images >256 px load via async loader and dispose properly
- [ ] Scroll stays at 60 fps on a mid-tier machine
- [ ] First-window-shown < 1s after launch (cold start)
- [ ] No console warnings (`avalonia: WARN ...`) in release build

## Platform Parity

- [ ] Built and tested on Windows
- [ ] Built and tested on macOS
- [ ] Built and tested on Linux (X11 and Wayland if applicable)
- [ ] Tested on Avalonia.Mobile (Android/iOS) if app targets mobile
- [ ] Tested on WASM (browser) if app targets web
- [ ] Title bar/menu behavior correct per platform (macOS app-menu, Windows custom chrome)
- [ ] File dialogs use `IStorageProvider` (cross-platform) — not WinForms `OpenFileDialog`
- [ ] Fonts render correctly on all platforms (variable fonts work; fallbacks provided)
- [ ] Keyboard shortcuts match platform conventions (`Cmd` on macOS)

## Final Polish

- [ ] No XAML warnings in build output
- [ ] `App.axaml` Styles ordered: theme → tokens → app styles
- [ ] Unused styles / resources removed
- [ ] All `x:Name` declarations are intentional and used
- [ ] Localization-ready: no English strings hard-coded if app is multi-language (use `Resx`/`Avalonia.Localization`)
- [ ] Designer-mode preview works (`d:DesignWidth`/`d:DesignHeight` valid)
- [ ] No `MessageBox.Show` left in production code (use `IDialogService` / FluentAvalonia ContentDialog)

---

## Sign-off Template

```
✅ Visual Quality (tokens, themes, theme-variant tested both modes)
✅ Component Quality (shared styles, no ad-hoc)
✅ Motion (timing, easing, reduced-motion path)
✅ Accessibility (a11y props, keyboard, contrast, screen reader)
✅ Layout & Responsive (compact / wide tested)
✅ Icons & Imagery (single family, semantic colors)
✅ Performance (60 fps scroll, virtualized lists)
✅ Platform Parity (Win/macOS/Linux at minimum)
✅ Final Polish (no warnings, no leftover strings)

Reviewer: ____________  Date: ____________
```

If any item is `❌`, link the relevant sub-skill in the PR review and request changes.
