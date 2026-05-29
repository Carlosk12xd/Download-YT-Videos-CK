# Carlos Knight Media Converter

A Stacher-style Streamlit interface for `yt-dlp` and FFmpeg.

## What changed

This version moves the app closer to how Stacher works:

- Uses the yt-dlp command-line runner instead of only the Python API
- Supports local browser cookies with `--cookies-from-browser`
- Supports cookies.txt upload for cloud/sign-in cases
- Supports saving directly to a local folder when run locally
- Still supports browser download button for cloud deployment
- Exports Premiere-friendly files:
  - MP4: H.264 video + AAC audio + yuv420p + faststart
  - M4A: AAC audio

## Important difference from Stacher

Stacher is a desktop GUI for yt-dlp. It runs downloads on your own computer. A Streamlit Cloud app runs downloads from a cloud server, which YouTube may block with 403/sign-in errors.

For the most Stacher-like behavior, run this app locally.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Install FFmpeg first.

### macOS

```bash
brew install ffmpeg
```

### Windows

Install FFmpeg and add it to PATH.

### Linux

```bash
sudo apt update
sudo apt install ffmpeg
```

## Streamlit Cloud

Upload:

```text
app.py
requirements.txt
packages.txt
README.md
.streamlit/config.toml
```

Cloud mode may work for many links, but YouTube may block cloud server IPs. For YouTube 403/sign-in errors, use local mode or upload a valid cookies.txt file for videos you own or have permission to access.

## Legal / usage note

Use only for media you own, have permission to use, or can legitimately access. This app does not bypass DRM, paywalls, private videos, or platform restrictions.

## Streamlit Cloud + YouTube cookies

This version supports YouTube cookies from Streamlit Secrets.

In Streamlit Cloud:

1. Open your app.
2. Go to **Settings**.
3. Open **Secrets**.
4. Paste your cookies using this format:

```toml
YOUTUBE_COOKIES_TXT = """
# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	1795628587	VISITOR_INFO1_LIVE	replace_with_your_value
.youtube.com	TRUE	/	TRUE	1814632710	__Secure-3PSID	replace_with_your_value
"""
```

Do **not** commit real cookies to GitHub.

The app reads `YOUTUBE_COOKIES_TXT` with `st.secrets`, writes it to a temporary file only during conversion, passes it to yt-dlp with `--cookies`, and then deletes the temp file.

### Important

Cookies can help with YouTube sign-in / 403 / bot-check issues, but they do not guarantee success if YouTube blocks Streamlit Cloud's server IP or if the video is private, deleted, truly DRM-protected, or unavailable to that account.
