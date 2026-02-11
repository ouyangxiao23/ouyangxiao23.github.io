# Xiao Ouyang - Academic Homepage

Personal academic homepage for Xiao Ouyang (欧阳霄), 3rd year CS undergraduate at Tsinghua University.

Site URL: https://ouyangxiao23.github.io/

## Project Structure

```
├── content.yaml   # All site content (edit this to update)
├── build.py       # Generates index.html from content.yaml
├── index.html     # Generated output (do not edit directly)
├── style.css      # Styles
├── main.js        # Nav interactions & language toggle
└── assets/        # Images, PDFs, and other static files
```

## Quick Start

### Prerequisites

- Python 3.6+
- PyYAML (`pip install pyyaml`)

### Edit Content

All site content lives in `content.yaml`. Edit that file, then regenerate:

```bash
python build.py
```

The script reads `content.yaml` and outputs a fresh `index.html`.

### Start from Scratch

To generate a blank `content.yaml` template with all available fields:

```bash
python build.py --init
```

This overwrites `content.yaml` with a commented template. Fill in your details and run `python build.py` to build.

## Assets

Add the following files to the `assets/` directory:

| File | Description |
|------|-------------|
| `profile.jpg` | Headshot photo |
| `rdt2-thumb.jpg` | Paper thumbnail image |
| `Xiao_Ouyang_CV.pdf` | CV |
| `Xiao_Ouyang_Transcript.pdf` | Academic transcript |
| `wechat-qr.jpg` | WeChat QR code |

## Features

- **Bilingual** — EN/中文 toggle with localStorage persistence
- **Responsive** — Mobile-friendly with hamburger menu
- **No frameworks** — Plain HTML, CSS, and vanilla JS
- **YAML-driven** — Edit content without touching HTML

## Deployment

1. Create a GitHub repo named `ouyangxiao23.github.io`
2. Push all files to the `main` branch
3. Go to Settings → Pages → Deploy from `main`
