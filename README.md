# demo

A cross-platform application built with PyApp.

## Development

```bash
# Build and run
pyapp build windows
pyapp run windows

# Update source code and run
pyapp run windows -u

# Rebuild dependencies and run
pyapp run windows -ur
```

## Release

```bash
# Build → (optional) compile → package
pyapp build windows
pyapp compile windows    # optional, requires Nuitka
pyapp package windows

# Cross-platform
pyapp build linux --arch aarch64
pyapp build android --arch arm64-v8a
```

## Project Structure

```
demo/
├── pyproject.toml          # Project configuration
├── src/demo/      # Python source code
│   ├── __init__.py
│   ├── __main__.py         # Entry point
│   ├── app.py              # FastAPI application
│   └── resources/          # Static resources
├── frontend/               # Frontend project (optional)
├── .github/workflows/      # CI scripts (auto-generated)
├── scripts/                # Termux compile script (auto-generated)
└── bundles/                # Platform build output
```
