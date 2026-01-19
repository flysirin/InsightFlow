<div align="center">

# InsightFlow 🧠

**Zero Friction Knowledge Ingestion**

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/flysirin/InsightFlow)
[![Python](https://img.shields.io/badge/python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![AI](https://img.shields.io/badge/AI-Gemini_2.0-8E75B2.svg?logo=google-gemini&logoColor=white)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**InsightFlow** is a local-first tool that turns your media consumption into structured knowledge. It automatically processes videos and audio files using Google Gemini AI to generate summaries, transcripts, and action items.

</div>

---

## ✨ Features
*   **Inbox-Centric:** Just drop files into your folder.
*   **Smart Analysis:** Uses Gemini 2.0 Flash for ultra-fast, cheap processing.
*   **Multi-Key Engine:** Automatically rotates between Free and Paid API keys to save costs.
*   **Hybrid Input:** Supports local files (MP3, MP4, MOV) and YouTube URLs.

## 🚀 Quick Start

### 1. Prerequisites
**InsightFlow** requires two tools to be installed on your system:

1.  **Python 3.11+**
2.  **FFmpeg** (Core engine for audio processing)
    *   **Windows:** Open Terminal and run: `winget install Gyan.FFmpeg`
    *   **macOS:** `brew install ffmpeg`
    *   **Linux:** `sudo apt install ffmpeg`
    *   *Manual:* Download from [ffmpeg.org](https://ffmpeg.org) and add to PATH.

    > **Verify Setup:** Open a terminal and run `ffmpeg -version`. If you see version info, you're good to go!

### 2. Installation

**Option A: Using UV (Recommended)**
```bash
# Clone the repository
git clone https://github.com/flysirin/InsightFlow.git
cd InsightFlow

# Install Python dependencies
uv sync
```

**Option B: Using Standard Pip**
```bash
# Clone the repository
git clone https://github.com/flysirin/InsightFlow.git
cd InsightFlow

# Create a virtual environment (Optional but recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy the template to create your environment file:
```bash
cp .env.example .env
```
Edit `.env` with your settings:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `GOOGLE_KEYS_FREE` | List of Free Tier API keys (comma-separated) | Required |
| `GOOGLE_KEYS_PAID` | List of Paid Tier API keys (comma-separated) | Optional |
| `GOOGLE_MODEL` | Gemini model to use (e.g., `gemini-2.0-flash`) | `gemini-2.0-flash-lite` |
| `INSIGHTFLOW_INBOX` | Folder to watch for new files | `~/Downloads/InsightFlowInbox` |
| `INSIGHTFLOW_AUDIO_BITRATE` | Audio quality for processing (e.g., `64k`, `128k`) | `64k` |
| `INSIGHTFLOW_AUDIO_CHANNELS` | Audio channels (1 for Mono, 2 for Stereo) | `1` |

> **Note:** For Windows users, ensure `INSIGHTFLOW_INBOX` uses a full path like `C:\Users\Name\Downloads\InsightFlowInbox`.

### 4. Usage

**Analyze Local Files:**
Drop files into `Downloads/InsightFlowInbox` (or configured path) and run:
```bash
uv run python -m insightflow.main inbox
```

**Analyze YouTube:**
```bash
uv run python -m insightflow.main url "https://youtu.be/..."
```

## 📂 Output
For every file processed (e.g., `interview.mp3`), you get:
1.  `[DONE] interview.mp3` (Renamed source)
2.  `interview.md` (Full Markdown report)

## 🔧 Customization
Edit `prompts.yaml` to change how the AI summarizes your content (Language, Detail level, Format).
