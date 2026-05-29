# Carlos Knight Media Converter

A professional Streamlit app powered by `yt-dlp` and FFmpeg.

## User-facing exports

The app gives users two clean export choices:

1. **MP4 video for Premiere Pro**
   - Container: `.mp4`
   - Video codec: H.264
   - Audio codec: AAC
   - Pixel format: yuv420p
   - Fast-start enabled

2. **Audio export for Premiere Pro**
   - Container: `.m4a`
   - Audio codec: AAC

This is more Premiere Pro friendly than generic video/audio downloads.

## Files

- `app.py`
- `requirements.txt`
- `packages.txt`

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

You also need FFmpeg installed locally.

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

## Streamlit Cloud deployment

Upload these files to GitHub:

```text
app.py
requirements.txt
packages.txt
```

The `packages.txt` file must contain:

```text
ffmpeg
```

Streamlit Cloud uses this to install FFmpeg as a system dependency.