import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import streamlit as st
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


st.set_page_config(
    page_title="yt-dlp + FFmpeg Converter",
    page_icon="🎬",
    layout="centered",
)

st.title("🎬 yt-dlp + FFmpeg MP4 / MP3 Converter")
st.write(
    "Paste a media URL, choose MP4 or MP3, and download the converted file. "
    "This app uses yt-dlp for downloading and FFmpeg for merging/conversion."
)

st.warning(
    "Use this only for videos/audio you own, have permission to download, "
    "or that are clearly allowed by the site and copyright owner."
)


def find_ffmpeg() -> str | None:
    """
    Return the FFmpeg executable path if installed and available in PATH.
    """
    return shutil.which("ffmpeg")


def get_ffmpeg_version(ffmpeg_path: str) -> str:
    """
    Return a short FFmpeg version label.
    """
    try:
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            text=True,
            check=False,
        )
        first_line = result.stdout.splitlines()[0] if result.stdout else "FFmpeg found"
        return first_line
    except Exception:
        return "FFmpeg found, but version could not be read."


def human_bytes(num: int | float | None) -> str:
    """
    Convert bytes to a readable label.
    """
    if not num:
        return "0 B"

    num = float(num)
    for unit in ["B", "KB", "MB", "GB"]:
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024

    return f"{num:.1f} TB"


def find_output_file(download_dir: str, preferred_ext: str) -> Path:
    """
    Find the final file created by yt-dlp/FFmpeg.
    """
    directory = Path(download_dir)
    files = [
        p for p in directory.iterdir()
        if p.is_file()
        and not p.name.endswith(".part")
        and not p.name.endswith(".ytdl")
        and not p.name.endswith(".temp")
    ]

    preferred = [p for p in files if p.suffix.lower() == f".{preferred_ext.lower()}"]
    candidates = preferred or files

    if not candidates:
        raise FileNotFoundError("No output file was created.")

    return max(candidates, key=lambda p: p.stat().st_mtime)


def build_ydl_options(
    download_dir: str,
    output_type: str,
    max_height: int,
    mp3_quality: str,
    ffmpeg_path: str,
    progress_hook,
) -> dict:
    """
    Build yt-dlp options.

    FFmpeg is used for:
    - merging separate video/audio streams into MP4
    - extracting/converting audio into MP3
    """
    base_options = {
        "outtmpl": os.path.join(download_dir, "%(title).80s-%(id)s.%(ext)s"),
        "restrictfilenames": True,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [progress_hook],

        # This explicitly tells yt-dlp where FFmpeg is.
        # If FFmpeg is in PATH, this is usually enough.
        "ffmpeg_location": ffmpeg_path,
    }

    if output_type == "MP3":
        base_options.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": mp3_quality,
                    }
                ],
            }
        )

    else:
        base_options.update(
            {
                # Prefer MP4/H.264/AAC-compatible formats first.
                # FFmpeg handles merging/remuxing into a final MP4.
                "format": (
                    f"bv*[height<={max_height}][ext=mp4]+ba[ext=m4a]/"
                    f"bv*[height<={max_height}]+ba/"
                    f"b[height<={max_height}][ext=mp4]/"
                    f"b"
                ),
                "merge_output_format": "mp4",
                "postprocessors": [
                    {
                        "key": "FFmpegVideoRemuxer",
                        "preferedformat": "mp4",
                    }
                ],
                "format_sort": [
                    "vcodec:h264",
                    "acodec:aac",
                    "ext:mp4:m4a",
                    "res",
                ],
            }
        )

    return base_options


def download_and_convert(
    url: str,
    output_type: str,
    max_height: int,
    mp3_quality: str,
    ffmpeg_path: str,
):
    """
    Download and convert one URL.
    Returns: filename, bytes, file_size_label
    """
    temp_dir = tempfile.mkdtemp(prefix="ytdlp_streamlit_")

    progress_bar = st.progress(0, text="Preparing download...")
    status_box = st.empty()

    def progress_hook(d):
        status = d.get("status")

        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate")

            if total:
                pct = min(downloaded / total, 1.0)
                progress_bar.progress(
                    pct,
                    text=(
                        f"Downloading... {pct:.0%} "
                        f"({human_bytes(downloaded)} / {human_bytes(total)})"
                    ),
                )
            else:
                progress_bar.progress(
                    0,
                    text=f"Downloading... {human_bytes(downloaded)}",
                )

        elif status == "finished":
            progress_bar.progress(
                0.90,
                text="Download finished. Processing with FFmpeg...",
            )

    try:
        ydl_opts = build_ydl_options(
            download_dir=temp_dir,
            output_type=output_type,
            max_height=max_height,
            mp3_quality=mp3_quality,
            ffmpeg_path=ffmpeg_path,
            progress_hook=progress_hook,
        )

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        final_ext = "mp3" if output_type == "MP3" else "mp4"
        output_file = find_output_file(temp_dir, final_ext)

        file_bytes = output_file.read_bytes()
        file_size = human_bytes(output_file.stat().st_size)

        title = info.get("title") if isinstance(info, dict) else output_file.stem

        progress_bar.progress(1.0, text="Done.")
        status_box.success(f"Ready: {title}")

        return output_file.name, file_bytes, file_size

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


ffmpeg_path = find_ffmpeg()

with st.sidebar:
    st.header("FFmpeg status")

    if ffmpeg_path:
        st.success("FFmpeg detected")
        st.code(ffmpeg_path, language="text")
        st.caption(get_ffmpeg_version(ffmpeg_path))
    else:
        st.error("FFmpeg not found")
        st.write(
            "Install FFmpeg locally, or deploy with `packages.txt` on Streamlit Cloud."
        )

    st.divider()
    st.write("FFmpeg is used for:")
    st.write("- MP4 video/audio merging")
    st.write("- MP3 audio extraction")
    st.write("- Remuxing compatible video into `.mp4`")

with st.form("converter_form"):
    url = st.text_input(
        "Media URL",
        placeholder="https://www.youtube.com/watch?v=...",
    )

    output_type = st.radio(
        "Output format",
        ["MP4", "MP3"],
        horizontal=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        max_height = st.selectbox(
            "Max video quality",
            [2160, 1440, 1080, 720, 480, 360],
            index=2,
            disabled=(output_type == "MP3"),
            help="Used only for MP4 downloads.",
        )

    with col2:
        mp3_quality = st.selectbox(
            "MP3 quality",
            ["320", "256", "192", "128"],
            index=2,
            disabled=(output_type == "MP4"),
            help="Used only for MP3 conversion.",
        )

    submitted = st.form_submit_button("Convert")

if submitted:
    if not url.strip():
        st.error("Please paste a URL first.")

    elif not ffmpeg_path:
        st.error("FFmpeg is required but was not found.")
        st.info(
            "For Streamlit Cloud, keep `packages.txt` in your repo with this line: `ffmpeg`."
        )

    else:
        try:
            with st.spinner("Working with yt-dlp and FFmpeg..."):
                filename, file_bytes, file_size = download_and_convert(
                    url=url.strip(),
                    output_type=output_type,
                    max_height=int(max_height),
                    mp3_quality=str(mp3_quality),
                    ffmpeg_path=ffmpeg_path,
                )

            mime_type = "audio/mpeg" if output_type == "MP3" else "video/mp4"

            st.download_button(
                label=f"Download {output_type} ({file_size})",
                data=file_bytes,
                file_name=filename,
                mime=mime_type,
            )

        except DownloadError as e:
            st.error("yt-dlp could not download this URL.")
            st.code(str(e), language="text")
            st.info(
                "Some websites block downloads, require login, or do not allow extraction. "
                "This app does not bypass DRM, paywalls, logins, or site restrictions."
            )

        except Exception as e:
            st.error("Something went wrong.")
            st.code(str(e), language="text")
