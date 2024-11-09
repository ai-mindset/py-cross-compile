# PDF to Markdown Converter

[![Code Quality](https://github.com/ai-mindset/py-cross-compile/actions/workflows/code-quality.yml/badge.svg)](https://github.com/ai-mindset/py-cross-compile/actions/workflows/code-quality.yml)
[![Unix Build](https://github.com/ai-mindset/py-cross-compile/actions/workflows/unix-build.yml/badge.svg)](https://github.com/ai-mindset/py-cross-compile/actions/workflows/unix-build.yml)
[![Windows Build](https://github.com/ai-mindset/py-cross-compile/actions/workflows/build-win.yml/badge.svg)](https://github.com/ai-mindset/py-cross-compile/actions/workflows/build-win.yml)
[![Tests](https://github.com/ai-mindset/py-cross-compile/actions/workflows/tests.yml/badge.svg)](https://github.com/ai-mindset/py-cross-compile/actions/workflows/tests.yml)
[![Release](https://github.com/ai-mindset/py-cross-compile/actions/workflows/release.yml/badge.svg)](https://github.com/ai-mindset/py-cross-compile/actions/workflows/release.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)


A GUI application for converting PDF documents to Markdown using pypdf. This project primarily serves as an experiment in cross-compilation using GitHub Actions, demonstrating how to build Python applications for multiple platforms from a single Linux environment.

## Project Goals

1. **Cross-Compilation Experimentation**
   - Build from Linux for Windows, macOS, and Linux targets
   - Support both x86_64 and ARM64 architectures
   - Create self-contained executables without target OS access
   - Handle dependencies and resources across platforms
   - Automate the release process

2. **Technical Implementation**
   - Modern Python practices (3.11+)
   - Type-safe code with comprehensive testing
   - Memory-efficient PDF processing
   - User-friendly GUI interface

## Features

- Cross-platform PDF to Markdown conversion
- Table extraction in fast and accurate modes
- Memory-efficient processing
- Simple, native-looking GUI
- Self-contained executables

## Requirements

- Python 3.11 or newer
- Operating System: Windows, macOS, or Linux

## Installation

### End Users

Download the appropriate executable for your system from the [Releases](https://github.com/ai-mindset/pdf_converter/releases) page:

- Windows: `docling-converter-windows-x86_64.exe`
- macOS:
  - Intel: `docling-converter-macos-x86_64`
  - Apple Silicon: `docling-converter-macos-arm64`
- Linux:
  - x86_64: `docling-converter-linux-x86_64`
  - ARM64: `docling-converter-linux-aarch64`

### Developers

1. Clone the repository:
```bash
git clone https://github.com/ai-mindset/pdf_converter.git
cd pdf_converter
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

## Development

### Code Quality
```bash
# Format and lint code
ruff check .
ruff format .

# Type checking
mypy src
```

### Testing
```bash
pytest
```

### Creating a Release

1. Update version in `src/pdf_converter/__about__.py`
2. Update CHANGELOG.md
3. Create and push a new tag:
```bash
git tag v1.0.0
git push origin v1.0.0
```

The GitHub Action will automatically:
- Run tests
- Build executables for all platforms
- Create a new release with the binaries

## Project Structure
```
pdf_converter/
├── src/
│   └── pdf_converter/
│       ├── __init__.py
│       ├── __about__.py
│       ├── app.py
│       └── resources/
│           └── .gitkeep
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_app.py
│   └── data/
│       └── test.pdf
├── .github/
│   └── workflows/
│       ├── code-quality.yml
│       ├── tests.yml
│       └── build-release.yml
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
└── README.md
```

## Cross-Compilation Details

### Build Process
- Uses GitHub Actions with Ubuntu runners
- Leverages QEMU for ARM64 builds
- PyInstaller for executable creation
- Automated resource bundling

### Supported Platforms
- Windows (x86_64)
- macOS (x86_64, ARM64)
- Linux (x86_64, ARM64)

### CI/CD Pipeline
1. **Code Quality** (`code-quality.yml`)
   - Ruff (linting and formatting)
   - MyPy (type checking)
   - Security checks

2. **Tests** (`tests.yml`)
   - Multiple Python versions
   - Multiple operating systems
   - Coverage reporting

3. **Build & Release** (`build-release.yml`)
   - Cross-platform builds
   - Automatic releases on tags
   - Asset uploading

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run quality checks:
```bash
ruff check . && ruff format . && mypy src && pytest
```
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Create a Pull Request

## License

MIT License - see [`LICENSE`](LICENSE) for details.
