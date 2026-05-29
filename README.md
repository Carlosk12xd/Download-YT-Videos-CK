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

## 403 / Forbidden fix notes

This version includes extra reliability improvements for public cloud hosting:

- Adds `nodejs` in `packages.txt` so yt-dlp has a JavaScript runtime available for modern YouTube extraction.
- Keeps `ffmpeg` in `packages.txt`.
- Uses yt-dlp retry settings.
- Tries multiple normal yt-dlp YouTube client profiles.
- Falls back to safer combined MP4 formats when separate video/audio streams are blocked.
- Shows a user-friendly message if the host blocks the cloud-server request.

A 403 can still happen on some links because hosts may block Streamlit Cloud/server IPs, require login/cookies, restrict a video, or require validation that public apps should not bypass.

## Default dark mode

This version includes:

```text
.streamlit/config.toml
```

with Streamlit dark mode enabled by default.

## Latest fix: YouTube sign-in / 403 reliability

This version fixes the main issues from the Streamlit logs:

- Corrects the bgutil `server_home` path to point to `~/bgutil-ytdlp-pot-provider/server`
- Clones the matching bgutil provider version `1.3.1`
- Uses `npm ci` for a deterministic provider build
- Removes baked-in anonymous cookies
- Adds an Advanced cookies.txt uploader for per-conversion YouTube sign-in / 403 cases
- Uses cookies only temporarily, then deletes the temp file
- Avoids client profiles that can produce misleading DRM errors
- Aggregates yt-dlp attempt errors into a clearer message

Some YouTube videos may still fail on Streamlit Cloud because YouTube may reject datacenter/cloud IP addresses. In that case, running the app locally with fresh cookies from the same browser session is the reliable path.
