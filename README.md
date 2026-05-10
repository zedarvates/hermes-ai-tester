# 🤖 AI Tester — Automated Video Bug Reports

**An AI agent that tests any software, records the screen, and produces a narrated video report.**

No complex setup. No GPU needed. Just clone, run, get a video.

```
┌─────────────────────────────────────────────┐
│         AI TESTER PIPELINE                   │
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
│  3️⃣  GENERATE VIDEO REPORT                   │
│     Stitch screenshots → HyperFrames video   │
│     Add TTS narration (English)              │
│     "What works / What doesn't"              │
│     Background music with ducking            │
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
- 🎬 **Video reports** — narrated bug reports with screen recording
- 🗣️ **TTS narration** — explains what works and what doesn't
- 🐛 **GitHub Issues** — auto-creates issues with video evidence
- 📦 **Zero GPU** — uses HyperFrames (HTML + GSAP), no rendering farm needed
- 🔌 **Works on anything** — web apps, desktop apps, CLI tools

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/zedarvates/ai-tester.git
cd ai-tester

# Install HyperFrames
npm install -g hyperframes

# Run a test
python3 scripts/test_app.py --url https://yourapp.com --duration 60
```

## 📂 Structure

```
ai-tester/
├── scripts/
│   ├── test_app.py          # Main test orchestrator
│   ├── capture_screen.py    # Screen capture (PyAutoGUI)
│   ├── generate_report.py   # Generate video report from captures
│   └── create_issue.py      # Submit GitHub issue with video
├── hyperframes-templates/
│   ├── report-template.html  # HyperFrames video template
│   └── narration-template.txt
├── reports/                  # Generated reports go here
├── config.yaml               # Test configuration
└── DESIGN.md                 # Visual identity
```

## 🧪 Example

```bash
# Test a web app
python3 scripts/test_app.py \
  --url https://storycore-engine-demo.vercel.app \
  --steps "login, create project, export video" \
  --narration "Testing the video export feature"
```

## 🛠️ Requirements

- Node.js ≥ 22
- Python 3.10+
- HyperFrames: `npm install -g hyperframes`
- Windows (for desktop app testing) or any OS (for web testing)

## 📄 License

MIT — free to use, modify, share. Go build better software.

---

*Built with ❤️ by [Sylvain Galliez](https://github.com/zedarvates)*
