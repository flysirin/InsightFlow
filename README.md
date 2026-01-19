# InsightFlow 🧠

**InsightFlow** is a local-first tool that turns your media consumption into structured knowledge. It automatically processes videos and audio files using Google Gemini AI to generate summaries, transcripts, and action items.

## ✨ Features
*   **Inbox-Centric:** Just drop files into your folder.
*   **Smart Analysis:** Uses Gemini 1.5/2.0 Flash for ultra-fast, cheap processing.
*   **Multi-Key Engine:** Automatically rotates between Free and Paid API keys to save costs.
*   **Hybrid Input:** Supports local files (MP3, MP4, MOV) and YouTube URLs.

## 🚀 Quick Start

### 1. Prerequisites
*   **Python 3.10+**
*   **FFmpeg**: Must be installed and available in your system PATH (required for audio processing).
    *   *Windows:* `winget install Gyan.FFmpeg` or download from [ffmpeg.org](https://ffmpeg.org).
    *   *Mac:* `brew install ffmpeg`
    *   *Linux:* `sudo apt install ffmpeg`

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your/repo/InsightFlow.git
cd InsightFlow

# Install Python dependencies
uv sync
```

### 3. Configuration
Create a `.env` file (copy from `.env.example`) and add your Google AI Studio keys:
```ini
GOOGLE_KEYS_FREE=key1,key2
GOOGLE_KEYS_PAID=paid_key
```

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
