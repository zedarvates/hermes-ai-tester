# 🤖 AI Tester — Automated Video Bug Reports

**An AI agent that tests any software, records the screen, and produces a narrated video report using HyperFrames.**

No complex setup. No GPU needed. Just clone, run, get a video.

```
┌─────────────────────────────────────────────┐
│         AI TESTER PIPELINE v2               │
├─────────────────────────────────────────────┤
│                                              │
│  1️⃣  AGENT EXPLORE                         │
│     Navigate the app like a human            │
│     Click, type, test features               │
│     Detect bugs & crashes                    │
│                                              │
│  2️⃣  CAPTURE                                 │
│     Screenshots every 0.3s                   │
│     Record each step with timestamp          │
│     Capture error logs                       │
│                                              │
│  3️⃣  GENERATE (HyperFrames v0.6+)           │
│     TTS narration (LocalAI or cloud)         │
│     HTML template with GSAP animations       │
│     Lint → Render → MP4                     │
│     Deterministic output                     │
│                                              │
│  4️⃣  SUBMIT                                   │
│     Create GitHub Issue with video           │
│     Or email report to developers            │
│     Or save as local file                    │
│                                              │
└─────────────────────────────────────────────┘
```

## ✨ Features

- 🧪 **Autonomous testing** — agent navigates & tests your app
- 🎬 **Video reports** — narrated bug reports with screen recording via HyperFrames
- 🗣️ **TTS narration** — LocalAI (EUREKAI, GPU) or HyperFrames cloud TTS
- 🎨 **GSAP animations** — smooth fade transitions between frames
- ✅ **Deterministic** — same input = same MP4 (CI/CD ready)
- 🔍 **Linting** — automatic HTML validation before render
- 🖥️ **Works on any software** — web apps, desktop apps, mobile via ADB

## 🚀 Quick Start

```bash
# 1. Test an app
python scripts/test_app.py --app https://example.com --duration 60

# 2. Generate video report (with LocalAI TTS on EUREKAI)
python scripts/generate_report.py \
  --captures ./screenshots \
  --narration "Test report: all features working" \
  --output report.mp4 \
  --localai

# 3. Create GitHub Issue
python scripts/create_issue.py --repo owner/repo --video report.mp4
```

### Pipeline Steps

```bash
# Full pipeline in one shot
python scripts/generate_report.py \
  --captures ./captures \
  --narration ./transcript.txt \
  --voice af_nova \
  --fps 3 \
  --output ./reports/test-run-001.mp4 \
  --localai
```

### Without LocalAI (cloud TTS)

```bash
python scripts/generate_report.py \
  --captures ./captures \
  --narration "Everything works" \
  --output report.mp4
```

## 📋 Requirements

- **Node.js ≥ 22** (for HyperFrames CLI)
- **FFmpeg** (in PATH)
- **Python 3.11+**
- LocalAI on EUREKAI (192.168.1.47:8080) for local TTS — or cloud TTS

## 🏗️ Architecture

```
test_app.py → captures screenshots
  ↓
generate_report.py
  ├── Step 1: npx hyperframes init (creates project)
  ├── Step 2: TTS generation (LocalAI or cloud)
  ├── Step 3: HTML template generation (frame images + GSAP)
  ├── Step 4: npm run check (linting)
  ├── Step 5: npm run render (→ MP4)
  └── Output: report.mp4
  ↓
create_issue.py → GitHub issue with video attachment
```

## 🎨 Template

Le template HTML utilise les conventions HyperFrames v0.6+ :
- `class="clip"` sur tous les éléments temporisés
- `data-composition-id`, `data-start`, `data-duration`, `data-track-index`
- GSAP timeline avec `paused: true` enregistrée sur `window.__timelines`
- Déterministe — pas de `Date.now()` / `Math.random()`

Voir `hyperframes-templates/report-template.html`.

## 🗣️ TTS Voices

| Voice | Gender | Source |
|-------|--------|--------|
| `af_nova` | Female (American) | HyperFrames / Piper |
| `am_michael` | Male (American) | HyperFrames / Piper |
| `nova` | Female (neutral) | LocalAI (OpenAI-compatible) |
| `onyx` | Male (neutral) | LocalAI (OpenAI-compatible) |
| `alloy` | Neutral | LocalAI (OpenAI-compatible) |

## 🔧 Configuration

Voir `config.yaml` :
```yaml
app: "https://github.com/user/repo"
duration: 60
interval: 0.3
voice: "af_nova"
output: "./reports"
```

## 📁 Structure

```
├── scripts/
│   ├── test_app.py          # Agent exploration & screenshot capture
│   ├── generate_report.py   # HyperFrames video generation (v2, full pipeline)
│   └── create_issue.py      # GitHub issue creation
├── hyperframes-templates/
│   └── report-template.html # GSAP-animated report template
├── avatars/                 # AI avatar assets (optional)
├── config.yaml              # Configuration
└── README.md
```

## 🔗 Related

- [HyperFrames](https://hyperframes.heygen.com) — HTML-to-Video framework
- [Hermes Agent](https://github.com/zedarvates/hermes-agent) — AI orchestrator
- [StoryCore Engine](https://github.com/zedarvates/StoryCore-Engine) — Video story engine
- [Hnoss Vtuber](https://github.com/zedarvates/hnoss-vtuber) — AI avatar pipeline


---

[![Donate](https://img.shields.io/badge/☕%20Soutenir-BTC%20%7C%20ETH-orange)](DONATE.md)