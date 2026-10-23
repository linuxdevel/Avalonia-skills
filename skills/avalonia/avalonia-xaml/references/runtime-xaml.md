# Runtime XAML Loading Workflow

Use this for previewers, editors, and dynamic document hosts. Keep normal application views on compiled XAML via `InitializeComponent()` / `AvaloniaXamlLoader.Load(this)`.

## Version and Runtime Boundary

- Reference `Avalonia.Markup.Xaml.Loader` at the same version as core Avalonia. Initialize Avalonia before creating or loading controls, and load/update the UI on its dispatcher.
- The workflow below uses APIs available in **12.1 and 11.3**. It was validated against **12.1.4** and **11.3.22**.
- Set `RuntimeXamlLoaderConfiguration.UseCompiledBindingsByDefault` explicitly. The runtime-loader configuration defaults to `false`, including on 12.1; the project's build-time compiled-binding default does not configure it. With `true`, bindings in loaded XAML need an appropriate `x:DataType`.
- Runtime XAML compilation requires dynamic code and reflection. It is not the Native AOT loading path; use compiled XAML and compiled bindings for AOT applications. Do not treat trimmer roots as a replacement for runtime code generation.

## Load Related Documents Together

Give each in-memory document an absolute `BaseUri` and a diagnostic `Document` path. A relative `ResourceInclude` can then resolve another document in the same `LoadGroup` batch. `LocalAssembly` identifies the assembly for local type lookup; it does not replace each document's base URI.

This example loads a palette and a view into an existing, initially empty `UserControl`. Replace `App` with a type from the host assembly. The two documents have no bindings; add `x:DataType` when introducing compiled bindings.

```csharp
using System;
using System.Collections.Generic;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using Avalonia.Markup.Xaml.Diagnostics;

const string paletteXaml = """
<ResourceDictionary xmlns="https://github.com/avaloniaui"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <SolidColorBrush x:Key="PreviewAccent" Color="#2563EB" />
</ResourceDictionary>
""";

const string viewXaml = """
<UserControl xmlns="https://github.com/avaloniaui">
    <UserControl.Resources>
        <ResourceDictionary>
            <ResourceDictionary.MergedDictionaries>
                <ResourceInclude Source="Palette.axaml" />
            </ResourceDictionary.MergedDictionaries>
        </ResourceDictionary>
    </UserControl.Resources>
    <Border Background="{DynamicResource PreviewAccent}" Padding="16">
        <TextBlock Text="Runtime preview" Foreground="White" />
    </Border>
</UserControl>
""";

var assembly = typeof(App).Assembly;
var baseUri = new Uri($"avares://{assembly.GetName().Name}/Preview/");
var existing = new UserControl();
var diagnostics = new List<RuntimeXamlDiagnostic>();
var configuration = new RuntimeXamlLoaderConfiguration
{
    LocalAssembly = assembly,
    UseCompiledBindingsByDefault = true,
    CreateSourceInfo = true,
    DiagnosticHandler = diagnostic =>
    {
        diagnostics.Add(diagnostic);
        return diagnostic.Severity;
    }
};

var documents = new[]
{
    new RuntimeXamlLoaderDocument(new Uri(baseUri, "Palette.axaml"), paletteXaml)
    {
        Document = "Preview/Palette.axaml"
    },
    new RuntimeXamlLoaderDocument(new Uri(baseUri, "Scene.axaml"), existing, viewXaml)
    {
        Document = "Preview/Scene.axaml"
    }
};

UserControl view;
XamlSourceInfo? sourceInfo;
try
{
    var loaded = AvaloniaRuntimeXamlLoader.LoadGroup(documents, configuration);
    view = loaded[1] as UserControl ?? throw new InvalidOperationException("No preview view was loaded.");
    sourceInfo = XamlSourceInfo.GetXamlSourceInfo(view.Content!);
    // sourceInfo, when present, contains SourceUri, LineNumber, and LinePosition.
}
finally
{
    foreach (var document in documents)
        document.XamlStream.Dispose();
}
```

`RootInstance` populates the supplied object; it does not reset old children, resources, subscriptions, or application state for you. For replaceable previews, load into a fresh root and swap the displayed content only after success. Loading into an existing root is not a transactional hot-reload mechanism.

Dispose the documents' `XamlStream` values when finished, including on failure. The string constructors allocate streams too.

For a single independent document, use `AvaloniaRuntimeXamlLoader.Load(document, configuration)`; use `LoadGroup` when includes or type references span the in-memory batch. Recreate document streams for a subsequent load rather than reusing consumed streams.

## Diagnose Failures

- Retain both the loader exception and collected diagnostics. `DiagnosticHandler` receives diagnostic ID, severity, document, and optional line/column; it does not make every load failure recoverable.
- Returning a higher severity can promote a warning to an error. Severity cannot be lowered below the diagnostic's minimum; avoid suppressing load errors to publish a partial preview.
- Missing relative include: check the including document's `BaseUri` and the included document's matching absolute URI. A diagnostic `Document` path alone does not resolve includes.
- Missing local type: check the XML namespace and `LocalAssembly` before changing resources or bindings.
- Missing binding data type: check `x:DataType` and the explicit runtime compiled-binding setting, including inside templates.
- Missing source location: set `CreateSourceInfo = true` and a `Document` path before loading. `XamlSourceInfo` is optional; inspect a created child as well as an existing root, and handle `null`.

## Official Sources

- [Runtime loader API](https://docs.avaloniaui.net/api/avalonia/markup/xaml/avaloniaruntimexamlloader)
- [Runtime document API](https://docs.avaloniaui.net/api/avalonia/markup/xaml/runtimexamlloaderdocument)
- [Configuration API](https://docs.avaloniaui.net/api/avalonia/markup/xaml/runtimexamlloaderconfiguration)
- [12.1.4 runtime loader source and dynamic-code annotations](https://github.com/AvaloniaUI/Avalonia/blob/12.1.4/src/Markup/Avalonia.Markup.Xaml.Loader/AvaloniaRuntimeXamlLoader.cs)
- [12.1.4 configuration defaults and diagnostics](https://github.com/AvaloniaUI/Avalonia/blob/12.1.4/src/Markup/Avalonia.Markup.Xaml/RuntimeXamlLoaderConfiguration.cs)
- [Native AOT guidance](https://docs.avaloniaui.net/docs/deployment/native-aot)
