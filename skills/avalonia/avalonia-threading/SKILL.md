---
name: avalonia-threading
description: Use when code touches Avalonia threading — updating UI from background threads, Dispatcher.UIThread Post/InvokeAsync/Invoke, CheckAccess/VerifyAccess ("Call from invalid thread"), DispatcherPriority, async/await in ViewModels, ConfigureAwait, DispatcherTimer, progress reporting, cancellation, ObservableCollection updates off the UI thread, AvaloniaSynchronizationContext, or the Avalonia 12 multi-dispatcher changes (Dispatcher.CurrentDispatcher, Dispatcher.Yield).
---
# Avalonia Threading

Version labels per `avalonia-versions`: **(12.0+)**, **(11.x)**, no label = 11.3/12.0/12.1.

## Core Rules

1. `AvaloniaObject`s (controls, styled properties) may only be touched from the thread that owns them — normally the **UI thread**. Violations throw `InvalidOperationException: Call from invalid thread`.
2. Avalonia installs an `AvaloniaSynchronizationContext` on the UI thread, so `await` in UI-thread code resumes on the UI thread automatically.
3. Do CPU/IO work off-thread (`Task.Run`, async IO); marshal only the *result* back.
4. Never block the UI thread (`.Result`, `.Wait()`, `.GetAwaiter().GetResult()`) — deadlocks and frozen UI.
5. Multiple UI threads are **not** supported, even in 12. One dispatcher per thread exists, but apps use one UI thread.

## Dispatcher.UIThread

```csharp
using Avalonia.Threading;

// Fire-and-forget (non-blocking, from any thread)
Dispatcher.UIThread.Post(() => StatusText.Text = "Done");
Dispatcher.UIThread.Post(() => StatusText.Text = "Idle", DispatcherPriority.Background);

// Await completion / get a value back
await Dispatcher.UIThread.InvokeAsync(() => StatusText.Text = "Done");
var text = await Dispatcher.UIThread.InvokeAsync(() => SearchBox.Text);

// Async callback overload (returns Task, awaits inner work)
await Dispatcher.UIThread.InvokeAsync(async () => { await LoadAsync(); });

// Blocking — avoid from UI-bound flows; fine for rare sync handoffs from a worker
Dispatcher.UIThread.Invoke(() => StatusText.Text = "Done");

// Access checks
if (Dispatcher.UIThread.CheckAccess()) { /* on UI thread */ }
Dispatcher.UIThread.VerifyAccess();      // throws if not on UI thread
```

| Member | Returns | Default priority | Use when |
|---|---|---|---|
| `Post(Action, priority = default)` | `void` | `Default` | Fire-and-forget; safest, cannot deadlock |
| `Post(SendOrPostCallback, object? arg, priority = default)` | `void` | `Default` | Avoid closure allocation |
| `InvokeAsync(Action [, priority [, ct]])` | `DispatcherOperation` | `Default` | Need to await / abort / cancel |
| `InvokeAsync<T>(Func<T> [, priority [, ct]])` | `DispatcherOperation<T>` | `Default` | Read a value from UI thread |
| `InvokeAsync(Func<Task> [, priority])` | `Task` | `Default` | Async lambda on UI thread |
| `InvokeAsync<T>(Func<Task<T>> [, priority])` | `Task<T>` | `Default` | Async lambda with result |
| `Invoke(Action)` / `Invoke<T>(Func<T>)` (+ priority, ct, timeout overloads) | `void` / `T` | `Send` | Synchronous; blocks caller |
| `CheckAccess()` | `bool` | — | Branch on current thread |
| `VerifyAccess()` | `void` | — | Assert in debug paths |
| `ToTaskScheduler()` / `ToTaskScheduler(priority)` | `TaskScheduler` | — | Run TPL tasks on the dispatcher |

`DispatcherOperation` members: `Status`, `Priority` (settable), `Abort()`, `Wait()`, `Wait(TimeSpan)`, `GetTask()`, `GetAwaiter()`, events `Aborted` / `Completed`; `DispatcherOperation<T>` adds `Result`.

`Dispatcher.UIThread.Post` is the default choice from background code. `InvokeAsync`/`Invoke` take the same priorities; `Invoke` on the UI thread itself runs inline.

### DispatcherPriority (low to high)

`SystemIdle (-5)` < `ApplicationIdle (-4)` < `ContextIdle (-3)` < `Background (-2)` < `Input (-1)` < `Default (0)` < `Loaded (1)` < `UiThreadRender (2)` < `Render (4)` < `BeforeRender (5)` < `AsyncRenderTargetResize (6)` < `Normal (8)` < `Send (9)`. Also public: `Inactive`, `Invalid`, `MaxValue`; `DataBind` is obsolete.

| Need | Priority |
|---|---|
| Normal UI update from worker | `Default` (omit) |
| Bulk/low-importance updates that must not starve input/render | `Background` |
| Run after layout/render settle | `Loaded` or `Background` |
| Idle housekeeping | `ApplicationIdle` / `SystemIdle` |

Posting thousands of `Normal`+ items starves input and rendering — batch, or use `Background`.

## async/await in ViewModels

ViewModel commands start on the UI thread; the continuation after `await` resumes there too.

```csharp
public partial class SearchViewModel : ObservableObject   // CommunityToolkit.Mvvm
{
    private CancellationTokenSource? _cts;

    [ObservableProperty] private bool _isBusy;
    [ObservableProperty] private string? _error;

    [RelayCommand]
    private async Task SearchAsync(string query)
    {
        _cts?.Cancel();
        _cts?.Dispose();
        _cts = new CancellationTokenSource();
        var ct = _cts.Token;

        IsBusy = true; Error = null;                  // UI thread
        try
        {
            var results = await Task.Run(() => _service.Search(query, ct), ct); // worker
            Results.Clear();                           // back on UI thread
            foreach (var r in results) Results.Add(r);
        }
        catch (OperationCanceledException) { /* superseded */ }
        catch (Exception ex) { Error = ex.Message; }
        finally { IsBusy = false; }
    }

    public ObservableCollection<ResultItem> Results { get; } = new();
}
```

Patterns:

- Prefer truly async APIs (`HttpClient`, `Stream.ReadAsync`) over `Task.Run` wrappers.
- `Task.Run` only for CPU-bound work. Inside the lambda do **not** touch controls or bound properties.
- `async void` only for event handlers; wrap the body in `try/catch` — unhandled exceptions crash the app. Prefer async commands.
- Fire-and-forget from sync code: `_ = DoAsync();` with exceptions handled *inside* `DoAsync`.
- Property changes raised on a background thread propagate to bindings on that thread and will throw — set bound properties only on the UI thread.

### ConfigureAwait

| Where | Guidance |
|---|---|
| ViewModel / View / code-behind touching UI state | Do **not** use `ConfigureAwait(false)` — you need the UI-thread continuation |
| Library / service / repository code with no UI access | `ConfigureAwait(false)` on every await is fine and avoids UI-thread hops |
| After `ConfigureAwait(false)` in a mixed method | Continuation is on a pool thread — marshal with `Dispatcher.UIThread.Post/InvokeAsync` before UI work |

## Background Work + Progress

```csharp
// Progress<T> captures SynchronizationContext.Current at construction.
// Construct it on the UI thread so Report() callbacks run on the UI thread.
var progress = new Progress<int>(p => ProgressValue = p);

await Task.Run(async () =>
{
    for (var i = 0; i <= 100; i++)
    {
        ct.ThrowIfCancellationRequested();
        await DoStepAsync(i, ct);
        ((IProgress<int>)progress).Report(i);
    }
}, ct);
```

Alternative without `Progress<T>`: `Dispatcher.UIThread.Post(() => ProgressValue = p)`. Throttle high-frequency reporting (e.g. report every N ms or only when the value changes) — each report is one dispatcher item.

`IProgress<T>` is easy to test; `Progress<T>` created off the UI thread invokes callbacks on the thread pool.

## ObservableCollection from Background Threads

`ObservableCollection<T>` is not thread-safe, and `CollectionChanged` is raised on the mutating thread; bindings then touch controls from that thread and throw.

```csharp
// WRONG — worker mutates bound collection
await Task.Run(() => { foreach (var x in LoadItems()) Items.Add(x); });

// RIGHT — compute off-thread, mutate on UI thread
var loaded = await Task.Run(() => LoadItems().ToList());
foreach (var x in loaded) Items.Add(x);                       // after await = UI thread

// RIGHT — mutate from a worker via the dispatcher
Dispatcher.UIThread.Post(() => Items.Add(item));

// Large batches — chunk to keep UI responsive
foreach (var chunk in loaded.Chunk(200))
{
    foreach (var x in chunk) Items.Add(x);
    await Dispatcher.UIThread.InvokeAsync(() => { }, DispatcherPriority.Background); // let input/render run
}
```

For large replacements, prefer swapping the whole collection property (one change notification) over thousands of `Add` calls. `DynamicData` (`SourceCache`/`SourceList` + `ObserveOn(...)` to the UI thread) is a common alternative for streaming data; Rx `ObserveOn` needs a scheduler that targets the UI dispatcher; `ReactiveUI.Avalonia` configures `RxApp.MainThreadScheduler` for this (verify against the package version).

## DispatcherTimer

```csharp
private readonly DispatcherTimer _timer = new() { Interval = TimeSpan.FromSeconds(1) };

public Clock()
{
    _timer.Tick += (_, _) => Now = DateTime.Now;   // Tick runs on the timer's dispatcher
    _timer.Start();
}

protected override void OnDetachedFromVisualTree(VisualTreeAttachmentEventArgs e)
{
    base.OnDetachedFromVisualTree(e);
    _timer.Stop();                                  // always stop — a running timer keeps handlers alive
}

// One-shot / loop helpers (return IDisposable; dispose to cancel)
DispatcherTimer.RunOnce(() => Hint.IsVisible = false, TimeSpan.FromSeconds(3));
using var loop = DispatcherTimer.Run(() => { Poll(); return true; }, TimeSpan.FromSeconds(5)); // return false to stop
```

Constructors: `()`, `(DispatcherPriority)`, `(DispatcherPriority, Dispatcher)`, `(TimeSpan, DispatcherPriority, EventHandler)`, `(TimeSpan, DispatcherPriority, Dispatcher)`, `(TimeSpan, DispatcherPriority, Dispatcher, EventHandler)`. Members: `Interval`, `IsEnabled`, `Tag`, `Dispatcher` (get-only), `Start()`, `Stop()`, `Tick`.

- Tick handlers run on the UI thread, so long work in `Tick` freezes the UI; for slow work start a `Task` and marshal results.
- `Tick` is not reentrant-safe for async work: `async void` tick handlers can overlap if work exceeds `Interval` — guard with a flag.
- For non-UI periodic work use `PeriodicTimer` or `System.Threading.Timer` and marshal results with `Post`.
- **(12.0+)** `DispatcherTimer()` binds to `Dispatcher.CurrentDispatcher` — create it **on the UI thread**, or pass `Dispatcher.UIThread` explicitly. **(11.x)** always the UI thread.

## Cancellation

- One `CancellationTokenSource` per operation; cancel the previous one before starting a new (search-as-you-type).
- Pass the token to the async API **and** `Task.Run(..., ct)`; call `ct.ThrowIfCancellationRequested()` in loops.
- Catch `OperationCanceledException` separately — it is not an error.
- Dispose the CTS when replaced; cancel it on view/ViewModel teardown (`Unloaded`/`DetachedFromVisualTree`/`IDisposable`).
- `Dispatcher.InvokeAsync(Action, DispatcherPriority, CancellationToken)` cancels a *queued* operation; it does not interrupt a running delegate. `DispatcherOperation.Abort()` likewise only works before it starts.

## AvaloniaSynchronizationContext

Installed automatically on the UI thread (`AvaloniaSynchronizationContext.AutoInstall` is `true` by default; `InstallIfNeeded()` is called for you). `Post` queues to the dispatcher without blocking; `Send` runs synchronously (inline when already on the dispatcher thread). This is why `await` resumes on the UI thread and `Progress<T>` works.

- Pool threads have no context, so `await` after `Task.Run` inner code resumes on the pool; only the *outer* `await` in a UI method resumes on the UI thread.
- **(12.0+)** `new AvaloniaSynchronizationContext()` uses `Dispatcher.CurrentDispatcher` (the calling thread's dispatcher), not `Dispatcher.UIThread`. Overloads: `(DispatcherPriority)` and `(Dispatcher, DispatcherPriority)` are public. Do not construct one on a worker thread expecting UI-thread behavior.

## Avalonia 12 Threading Changes

| Change | Detail |
|---|---|
| **(12.0+)** Multiple dispatchers | One `Dispatcher` per thread. `Dispatcher.CurrentDispatcher` (static, current thread), `Dispatcher.FromThread(Thread)` (returns `Dispatcher?`), `AvaloniaObject.Dispatcher` (get-only; the dispatcher of the thread that created the object) |
| `Dispatcher.UIThread` | Still valid and recommended for application code. Library/control authors should prefer `AvaloniaObject.Dispatcher` / `Dispatcher.CurrentDispatcher` |
| `AvaloniaObject.CheckAccess()` / `VerifyAccess()` | Delegate to that object's `Dispatcher` — works on any `AvaloniaObject` |
| `DispatcherTimer`, `AvaloniaSynchronizationContext` | Default to the **current** dispatcher, not the UI thread. Create on the right thread or pass the dispatcher explicitly |
| `InvokeAsync` captures `ExecutionContext` | `AsyncLocal<T>`, culture, impersonation flow from caller to the callback. Do not rely on callbacks seeing the UI thread's ambient context |
| `Dispatcher.Yield()` / `Yield(priority)` (static), `Dispatcher.Resume()` / `Resume(priority)` | Awaitables returning to the dispatcher at a priority (default `Background`); `Yield` uses the current dispatcher |
| Android dispatcher | Implemented over Android `Looper`/`MessageQueue` (rebuilt Android backend) — no code change needed |
| Managed dispatcher | Gained explicit background-processing support; internal, no app-level API change |

```csharp
// (12.0+) let input/render run in the middle of a long UI-thread loop
foreach (var item in items)
{
    Process(item);
    await Dispatcher.Yield();                       // continuation at Background priority
}

// (12.0+) library code: use the control's own dispatcher
void SafeUpdate(AvaloniaObject target, Action a)
{
    if (target.CheckAccess()) a();
    else target.Dispatcher.Post(a);
}
```

`Dispatcher.Yield()` is for UI-thread loops. Truly heavy work still belongs in `Task.Run`.

## Testing

Headless tests run the Avalonia dispatcher on the test's UI thread; await dispatcher work rather than using `Thread.Sleep`. See the `avalonia-testing` skill for the headless test attributes, session setup and pumping queued jobs. Keep ViewModel async logic injectable (`TimeProvider`, services returning `Task`) so most tests need no dispatcher.

## Common Mistakes

- **Updating a control/bound property from `Task.Run` or a `System.Threading.Timer` callback** — throws "Call from invalid thread". Use `Dispatcher.UIThread.Post(...)`.
- **`.Result` / `.Wait()` / `GetAwaiter().GetResult()` on the UI thread** — deadlock when the awaited task needs the UI thread. Make the call chain async.
- **`ConfigureAwait(false)` in ViewModel code, then setting properties** — continuation is on a pool thread. Remove it, or marshal explicitly.
- **`Dispatcher.UIThread.Invoke` from a worker while the UI thread waits on the worker** — deadlock. Prefer `Post`/`InvokeAsync`.
- **Mutating `ObservableCollection` in `Task.Run`** — see above; build a list off-thread, add on UI thread.
- **Posting per-item at high priority in a tight loop** — starves input/render. Batch, or use `DispatcherPriority.Background`.
- **`async void` outside event handlers** — exceptions crash the process and cannot be awaited/tested.
- **Not stopping `DispatcherTimer`** on view teardown — leaks the view and keeps ticking.
- **Creating `DispatcherTimer` / `AvaloniaSynchronizationContext` on a worker thread in 12** — binds to that thread's dispatcher; ticks never fire on the UI. Create on the UI thread or pass `Dispatcher.UIThread`.
- **Assuming `InvokeAsync` callbacks see no ambient context in 12** — `ExecutionContext` now flows; `AsyncLocal` values from the caller are visible.
- **`Progress<T>` constructed on a worker thread** — callbacks run on the pool. Construct on the UI thread.
- **Forgetting cancellation of superseded work** — stale results overwrite newer ones; cancel the old CTS and ignore `OperationCanceledException`.
- **Expecting multiple UI threads to work in 12** — multiple dispatchers exist, multi-threaded UI is unsupported.

## Sources
- UI thread guide: https://docs.avaloniaui.net/docs/guides/development-guides/accessing-the-ui-thread
- Breaking changes (multiple dispatchers, ExecutionContext): https://docs.avaloniaui.net/docs/avalonia12-breaking-changes
- Dispatcher source: https://github.com/AvaloniaUI/Avalonia/tree/master/src/Avalonia.Base/Threading
- 12.0.0 release notes (PRs #18686, #18975, #19163, #19370, #20957, #21025): https://github.com/AvaloniaUI/Avalonia/discussions/21091
