---
name: avalonia-mobile
description: Use when building or fixing the Android or iOS (and Mac Catalyst) app side of an Avalonia app — project heads and startup per version (AvaloniaAndroidApplication, AvaloniaMainActivity, AvaloniaAppDelegate, IActivityApplicationLifetime vs ISingleViewApplicationLifetime), safe areas/edge-to-edge (IInsetsManager), soft keyboard (IInputPane), back button, orientation, app activation/background, haptics (PlatformFeedback), touch behavior, and mobile storage/launcher. For packaging/signing see avalonia-deployment.
---
# Avalonia Mobile (Android & iOS)

App-level concerns only. Packaging, signing, APK/IPA publishing: see `avalonia-deployment`. Version labels: see `avalonia-versions`.

## Requirements

| | 11.x | 12.0 / 12.1 |
|---|---|---|
| TFM | `net*-android` / `net*-ios` (pre-net10) | **`net10.0-android` / `net10.0-ios`** (net10.0 required) |
| Mac Catalyst | no | (12.0+) `net10.0-maccatalyst` via `Avalonia.iOS` package |
| Packages | `Avalonia.Android` / `Avalonia.iOS` | same, version must match core `Avalonia` |

Standard solution layout (from `avalonia-dotnet-templates` xplat template): shared `App` project + `*.Android` head + `*.iOS` head (+ Desktop/Browser). Template defaults: Android `SupportedOSPlatformVersion` 23, iOS 13.0, AndroidX SplashScreen package referenced.

## Android startup

### (12.0+) Application class + activity

```csharp
// Application.cs — initialization moved here from the activity
[Application]
public class AndroidApp : AvaloniaAndroidApplication<App>
{
    public AndroidApp(IntPtr javaReference, JniHandleOwnership transfer)
        : base(javaReference, transfer) { }

    protected override AppBuilder CustomizeAppBuilder(AppBuilder builder)
        => base.CustomizeAppBuilder(builder).WithInterFont();
}

// MainActivity.cs — non-generic
[Activity(
    Label = "MyApp",
    Theme = "@style/MyTheme.NoActionBar",
    Icon = "@drawable/icon",
    MainLauncher = true,
    ConfigurationChanges = ConfigChanges.Orientation | ConfigChanges.ScreenSize | ConfigChanges.UiMode)]
public class MainActivity : AvaloniaMainActivity { }
```

`CreateAppBuilder()` / `CustomizeAppBuilder()` were **removed from `AvaloniaMainActivity`** — put builder customization in the `AvaloniaAndroidApplication<TApp>` subclass or `App`. (The `IntPtr, JniHandleOwnership` constructor is the standard .NET-Android requirement for `Application` subclasses; the template may omit/inline it — copy from the generated head.)

Type chain: `AppCompatActivity` -> `AvaloniaActivity` -> `AvaloniaMainActivity`.

### (12.0+) App.axaml.cs — set the main view

```csharp
public override void OnFrameworkInitializationCompleted()
{
    switch (ApplicationLifetime)
    {
        case IClassicDesktopStyleApplicationLifetime desktop:
            desktop.MainWindow = new MainWindow();
            break;
        case IActivityApplicationLifetime activity:        // Android (12.0+)
            activity.MainViewFactory = () => new MainView();  // Func<Control>
            break;
        case ISingleViewApplicationLifetime single:        // iOS, Browser, embedded Linux
            single.MainView = new MainView();
            break;
    }
    base.OnFrameworkInitializationCompleted();
}
```

Android no longer uses `ISingleViewApplicationLifetime`; keep that branch for iOS/Browser. Use a **factory** (a new view per activity instance), not a shared instance.

### (11.x) Generic activity + single view

```csharp
[Activity(Label = "MyApp", MainLauncher = true, Theme = "@style/MyTheme.NoActionBar",
    ConfigurationChanges = ConfigChanges.Orientation | ConfigChanges.ScreenSize | ConfigChanges.UiMode)]
public class MainActivity : AvaloniaMainActivity<App>
{
    protected override AppBuilder CustomizeAppBuilder(AppBuilder builder)
        => base.CustomizeAppBuilder(builder).WithInterFont();
}
// App: case ISingleViewApplicationLifetime single: single.MainView = new MainView();
```

### Multiple activities (12.0+)

Android may create several instances of the main activity in one process (notification tap, return from another app), and 12.0 lets later activities use your project's `Application` class. `IActivityApplicationLifetime.MainViewFactory` (`Func<Control>`) is called **once per new activity instance**, so each gets a fresh view with its own state. Never set `ISingleViewApplicationLifetime.MainView` on Android 12 — the Android lifetime implements both interfaces and wraps `MainView` in a factory returning the *same* instance, so a second activity shows a blank screen. The lifetime holds only the factory; keep your own reference if you need the current view. Extra (non-main) activities subclass `AvaloniaActivity` (`AppCompatActivity` -> `AvaloniaActivity`) and set its `Content` property. `AvaloniaActivity` also has `ActivityResult`, `RequestPermissionsResult` (both `Action<...>`), event `BackRequested`, and `OnBackPressed()` / `OnBackInvoked()`.

### Rendering mode

```csharp
// in AvaloniaAndroidApplication<TApp>.CustomizeAppBuilder
.With(new AndroidPlatformOptions
{
    RenderingMode = new[] { AndroidRenderingMode.Egl, AndroidRenderingMode.Software }
})
```
`AndroidRenderingMode`: `Egl` (default GPU), `Vulkan`, `Software`. First mode that initializes wins; empty list or all failing throws `InvalidOperationException` — keep `Software` as fallback.

## iOS / Mac Catalyst startup

```csharp
[Register("AppDelegate")]
public partial class AppDelegate : AvaloniaAppDelegate<App>
{
    protected override AppBuilder CustomizeAppBuilder(AppBuilder builder)
        => base.CustomizeAppBuilder(builder)
            .WithInterFont()
            .With(new iOSPlatformOptions
            {
                RenderingMode = new[] { iOSRenderingMode.Metal, iOSRenderingMode.OpenGl },
                EnableHighRefreshRate = false   // opt out of high refresh rate
            });
}
```

- iOS uses `ISingleViewApplicationLifetime` (`MainView`) in all versions.
- (12.0+) **Scene-based lifecycle**: a scene delegate is managed internally; most apps need no changes. `AvaloniaAppDelegate.Window` stays `null` after startup — to reach the `UIWindow`, override `AvaloniaView.MovedToWindow`.
- (12.0+) Mac Catalyst: `<TargetFrameworks>net10.0-ios;net10.0-maccatalyst</TargetFrameworks>`; `dotnet workload install maccatalyst`, `dotnet run -f net10.0-maccatalyst`.
- Embedding: `Avalonia.iOS.AvaloniaView` (UIKit view hosting Avalonia content), `Avalonia.Android.AvaloniaView` on Android.

## Safe areas & edge-to-edge — `IInsetsManager`

```csharp
var insets = TopLevel.GetTopLevel(this)?.InsetsManager;   // IInsetsManager?
if (insets is not null)
{
    insets.DisplayEdgeToEdgePreference = true;      // draw behind system bars
    insets.IsSystemBarVisible = true;               // bool?
    insets.SystemBarColor = Colors.Black;           // Color?
    Thickness pad = insets.SafeAreaPadding;         // notches, bars, (keyboard excluded)
    insets.SafeAreaChanged += (_, e) => Padding = e.SafeAreaPadding;   // SafeAreaChangedArgs
}
```

| Member | Notes |
|---|---|
| `DisplayEdgeToEdgePreference` (bool) | Request edge-to-edge. **Replaces `DisplayEdgeToEdge` (removed in 12)** |
| `DisplaysEdgeToEdge` | Actual current state |
| `SafeAreaPadding` (`Thickness`) / `SafeAreaChanged` | Current safe-area insets / change event |
| `IsSystemBarVisible` (`bool?`), `SystemBarColor` (`Color?`) | System bar control |

Also on `TopLevel`: attached `SystemBarColor` (`TopLevel.SetSystemBarColor(control, SolidColorBrush?)` / `GetSystemBarColor`) and `TopLevel.GetAutoSafeAreaPadding` / `SetAutoSafeAreaPadding` (whether the TopLevel auto-pads for the safe area). `SystemBarTheme` enum: `Light` (light bar background, dark foreground) / `Dark`.

When drawing edge-to-edge, apply `SafeAreaPadding` to your root layout (or rely on auto safe-area padding) so content isn't under notches/home indicator.

## Soft keyboard — `IInputPane`

```csharp
var pane = TopLevel.GetTopLevel(this)?.InputPane;   // IInputPane?
pane!.StateChanged += (_, e) =>
{
    // e.NewState: InputPaneState.Open / Closed
    // e.EndRect: final keyboard bounds; e.StartRect (Rect?); e.AnimationDuration; e.Easing
    BottomSpacer.Height = e.NewState == InputPaneState.Open ? e.EndRect.Height : 0;
};
var occluded = pane.OccludedRect;   // current keyboard bounds
```

- `Closed` also means "keyboard floating / overlay and not part of insets".
- To request showing the keyboard: `TextInputMethodClient.ShowInputPanel` was **removed in 12**; the client now raises `InputPaneActivationRequested` (`EventHandler`) and the platform decides. Don't call a show method yourself — focus a `TextBox`.

## Back button

```csharp
var top = TopLevel.GetTopLevel(this)!;
top.BackRequested += (_, e) =>      // EventHandler<RoutedEventArgs>, "physical Back Button pressed or back navigation requested"
{
    if (Nav.CanGoBack) { Nav.GoBack(); e.Handled = true; }
};
```

Android-specific (12.0+, per `AvaloniaActivity`): event `BackRequested` of `EventHandler<AndroidBackRequestedEventArgs>` (has `bool Handled`), plus `OnBackPressed()` / `OnBackInvoked()`. Set `Handled = true` to stop the default (finishing the activity); do not leave it unhandled when you consumed the back action.

## Orientation

- Lock in the Android activity: `[Activity(..., ScreenOrientation = ScreenOrientation.Portrait)]` (Android attribute). Keep `ConfigurationChanges = Orientation | ScreenSize | UiMode` so rotation doesn't recreate the activity.
- iOS: set supported orientations in `Info.plist` (`UISupportedInterfaceOrientations`).
- Read at runtime: `TopLevel.Screens?.Primary?.CurrentOrientation` -> `Avalonia.Platform.ScreenOrientation` (`None`, `Landscape`, `LandscapeFlipped`, `Portrait`, `PortraitFlipped`). React to size changes via layout size changes rather than polling.

## App lifecycle — `IActivatableLifetime`

```csharp
if (Application.Current?.TryGetFeature<IActivatableLifetime>() is { } life)
{
    life.Activated   += (_, e) => { /* e.Kind: ActivationKind.Background / File / OpenUri / Reopen */ };
    life.Deactivated += (_, e) => { if (e.Kind == ActivationKind.Background) SaveState(); };
}
```

- `ActivatedEventArgs.Kind` is an `ActivationKind`: `Background` (enter/leave background), `File` (`FileActivatedEventArgs.Files`), `OpenUri` (`ProtocolActivatedEventArgs.Uri`), `Reopen` (macOS).
- Replaces `IActivatableApplicationLifetime` / `IApplicationPlatformEvents` (removed in 12). In 11.x use `(ApplicationLifetime as IActivatableApplicationLifetime)`.
- Android: `IAvaloniaActivity.Activated/Deactivated` per activity; file/URI intents arrive as `FileActivatedEventArgs` / `ProtocolActivatedEventArgs`. Register intent filters on the activity (`[IntentFilter(...)]`) — see Avalonia docs "Register your app to open files".
- iOS: protocol/universal links are delivered as `ProtocolActivatedEventArgs` with `Kind == ActivationKind.OpenUri`.
- Save state on `Deactivated` (background) — mobile OSes may kill the process without further notice.

## Haptics & sound — `PlatformFeedback` (12.1+)

```csharp
// Opt a control in (default is FeedbackType.None for custom controls)
PlatformFeedback.SetFeedbackType(this, FeedbackType.Auto);   // None, Auto, Sound, Haptic
this.PerformFeedback(FeedbackAction.Click);                  // extension on InputElement; also FeedbackAction.Hold
```
```xml
<Button PlatformFeedback.FeedbackType="Auto" />
```
Namespace `Avalonia.Controls`. Implemented on Android and iOS. `FeedbackAction` cannot be constructed by apps (internal constructor). Not available in 12.0/11.x.

## System theme (12.1+ on Android)

12.1 detects Android system theme (dark/light) **changes at runtime**; earlier versions only read it at startup. Keep `RequestedThemeVariant` = `Default` (don't hard-set Light/Dark) to follow the OS, and handle `ConfigChanges.UiMode` on the activity. Read with `TopLevel.PlatformSettings?.GetColorValues().ThemeVariant` (11.x) or `visual.GetPlatformSettings()` (12.x).

## Touch input

- (12.0+) Touch/pen **select and focus on pointer release**, not press; `ListBoxItem`/`TreeViewItem` handle their own selection. 11.x selects on press — don't write 12 code that depends on press-selection from touch.
- (12.0+) Gesture events (e.g. `Pinch`) are directly on `InputElement`, no `Gestures.` prefix in XAML.
- Hover (`:pointerover`) styling is meaningless on touch; use `:pressed`.
- Make hit targets at least ~44x44 dp (`MinHeight`/`MinWidth`).

## Storage, permissions, launcher

```csharp
var top = TopLevel.GetTopLevel(this)!;
var files = await top.StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions { AllowMultiple = false });
await using var s = await files[0].OpenReadAsync();          // use streams, not paths
await top.Launcher.LaunchUriAsync(new Uri("https://avaloniaui.net"));
```
- Android pickers go through the system document picker (content URIs); iOS through the document picker. `file.Path.LocalPath` is unreliable — always use `OpenReadAsync/OpenWriteAsync`. Details: `avalonia-services`.
- Android runtime permissions: declare in `AndroidManifest.xml` (`<uses-permission>`), request via Android APIs from the activity; `AvaloniaActivity.RequestPermissionsResult` / `ActivityResult` callbacks (`Action<...>` properties) can receive results; `IActivityResultHandler` exists for this.
- iOS: add usage descriptions (`NSCameraUsageDescription`, etc.) to `Info.plist`.

## Page-based navigation (12.0+)

12.0 adds `Page`, `ContentPage`, `DrawerPage`, `CarouselPage` and related page types for mobile-style navigation (page lifecycle events fire after transitions complete). Not in 11.x — there use a `ContentControl` + ViewModel navigation. See `avalonia-controls` / `avalonia-mvvm` and the Avalonia docs for the page API; the dotnet template can scaffold a page-hosted main view. Wire `TopLevel.BackRequested` to the page stack.

## Common Mistakes

- **Android 12.x with `AvaloniaMainActivity<TApp>` or `ISingleViewApplicationLifetime`** — use non-generic `AvaloniaMainActivity` + `[Application] AvaloniaAndroidApplication<TApp>` + `IActivityApplicationLifetime.MainViewFactory`.
- **Overriding `CustomizeAppBuilder` on the activity (12.x)** — removed; put it on the Application class.
- **Missing `[Application]` attribute** on the `AvaloniaAndroidApplication<TApp>` subclass — app never initializes.
- **Wrong TFM** — 12.x mobile heads need `net10.0-android`/`net10.0-ios`.
- **`DisplayEdgeToEdge` / `ShowInputPanel` / `IActivatableApplicationLifetime`** — removed in 12; use `DisplayEdgeToEdgePreference`, `InputPaneActivationRequested`, `TryGetFeature<IActivatableLifetime>()`.
- **Content under notch/status bar** after enabling edge-to-edge — apply `SafeAreaPadding` (and re-apply on `SafeAreaChanged`).
- **Keyboard covers inputs** — listen to `InputPane.StateChanged`, pad/scroll by `EndRect.Height`.
- **Accessing `TopLevel.InsetsManager`/`InputPane` too early** — null before attachment; use `Loaded`/`OnAttachedToVisualTree`.
- **Forgetting `e.Handled = true`** on back handling — app exits instead of navigating back.
- **Using `PlatformFeedback` on 12.0** — 12.1+ only; custom controls default to `FeedbackType.None`.
- **Assuming selection on press for touch** — 12.x selects on release.
- **Using file paths from pickers** on mobile — use stream APIs.
- **Removing `ConfigChanges.UiMode/Orientation/ScreenSize`** — activity restarts on rotate/theme change and view state is lost.
- **Reading `AvaloniaAppDelegate.Window` on iOS 12** — null; scene delegate owns the window.

## Sources
- Android: https://docs.avaloniaui.net/docs/platform-specific-guides/android ; iOS: https://docs.avaloniaui.net/docs/platform-specific-guides/ios
- Breaking changes: https://docs.avaloniaui.net/docs/avalonia12-breaking-changes
- API: https://docs.avaloniaui.net/api/avalonia/android , /api/avalonia/controls/platform , /api/avalonia/controls/applicationlifetimes
- Templates: https://github.com/AvaloniaUI/avalonia-dotnet-templates (templates/csharp/xplat)
- PlatformFeedback: https://github.com/AvaloniaUI/Avalonia/pull/21189
