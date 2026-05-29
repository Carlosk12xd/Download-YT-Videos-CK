# yt-dlp + FFmpeg Streamlit MP4 / MP3 Converter

This Streamlit app uses:

- `yt-dlp` to download media
- `FFmpeg` to merge MP4 video/audio streams
- `FFmpeg` to extract and convert audio to MP3

## Important

Use this only for media you own, have permission to download, or that the copyright owner/site clearly allows you to download. This app does not bypass DRM, paywalls, logins, or platform restrictions.

## Files

- `app.py` - Main Streamlit app
- `requirements.txt` - Python dependencies
- `packages.txt` - System dependency for Streamlit Cloud

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

You need FFmpeg installed on your computer.

### macOS

```bash
brew install ffmpeg
```

### Windows

Install FFmpeg and add it to your PATH.

### Linux

```bash
sudo apt update
sudo apt install ffmpeg
```

## Deploy to Streamlit Cloud

Add these files to your GitHub repo:

```text
app.py
requirements.txt
packages.txt
```

The `packages.txt` file contains:

```text
ffmpeg
```

Streamlit Cloud uses this file to install FFmpeg as a system package.

## What changed in this version?

This version explicitly uses FFmpeg by:

1. Detecting FFmpeg with `shutil.which("ffmpeg")`
2. Showing the FFmpeg path/version in the sidebar
3. Blocking conversion if FFmpeg is missing
4. Passing the FFmpeg path into yt-dlp with:

```python
"ffmpeg_location": ffmpeg_path
```

5. Using FFmpeg postprocessors for:
   - MP3 extraction
   - MP4 remuxing/merging
