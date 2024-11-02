# py-cross-compile

[![Build](https://github.com/ai-mindset/py-cross-compile/actions/workflows/build.yml/badge.svg)](https://github.com/ai-mindset/py-cross-compile/actions/workflows/build.yml)

Cross-platform Python application builder that creates native executables for Windows (.msi), macOS (.dmg), and Linux (.deb) using BeeWare and GitHub Actions.

## Features
- Single codebase, multiple platforms
- Automated builds via GitHub Actions
- Native installers for each OS
- No need for Windows/macOS machines
- Proper desktop integration on all platforms

## Usage

1. Clone template:
```bash
git clone https://github.com/<my gh handle>/py-cross-compile
cd py-cross-compile
```

2. Update  `pyproject.toml`:  
```toml
[tool.briefcase]
project_name = "YourApp"
version = "0.1.0"
bundle = "com.yourdomain"

[tool.briefcase.app.yourapp]
formal_name = "Your App"
description = "Your app description"
sources = ["src/yourapp"]
requires = []
```

3. Add your code to `src/yourapp` 

4. Push to GitHub:  
```bash
git push origin main
```

5. Get your binaries from GitHub Actions artifacts

## Requirements
* Python 3.12+
* git
* GitHub Account
