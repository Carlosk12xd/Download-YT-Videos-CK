import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import streamlit as st
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


st.set_page_config(
    page_title="Carlos Knight Media Converter",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed",
)


CUSTOM_CSS = """
<style>
:root {
    --card-bg: rgba(255, 255, 255, 0.10);
    --card-border: rgba(255, 255, 255, 0.18);
}

.stApp {
    background:
        radial-gradient(circle at 10% 20%, rgba(255, 90, 120, 0.28), transparent 28%),
        radial-gradient(circle at 90% 10%, rgba(96, 165, 250, 0.30), transparent 30%),
        radial-gradient(circle at 50% 90%, rgba(168, 85, 247, 0.26), transparent 28%),
        linear-gradient(135deg, #0f172a 0%, #111827 45%, #020617 100%);
    color: #f8fafc;
}

.block-container {
    max-width: 900px;
    padding-top: 3rem;
    padding-bottom: 3rem;
}

.hero-card {
    padding: 2.2rem 2.4rem;
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(255,255,255,0.16), rgba(255,255,255,0.06));
    border: 1px solid rgba(255,255,255,0.22);
    box-shadow: 0 25px 70px rgba(0,0,0,0.35);
    backdrop-filter: blur(18px);
    margin-bottom: 1.2rem;
}

.brand-kicker {
    display: inline-flex;
    gap: 0.45rem;
    align-items: center;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    background: rgba(96, 165, 250, 0.16);
    border: 1px solid rgba(147, 197, 253, 0.32);
    color: #bfdbfe;
    font-weight: 700;
    font-size: 0.86rem;
    letter-spacing: 0.02em;
    margin-bottom: 0.9rem;
}

.hero-title {
    font-size: clamp(2.1rem, 5vw, 4.1rem);
    line-height: 0.98;
    font-weight: 900;
    margin: 0;
    letter-spacing: -0.06em;
}

.gradient-text {
    background: linear-gradient(90deg, #f9a8d4, #93c5fd, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    margin-top: 1rem;
    color: #cbd5e1;
    font-size: 1.05rem;
    line-height: 1.65;
}

.credit {
    margin-top: 1.25rem;
    color: #e2e8f0;
    font-weight: 700;
    font-size: 0.95rem;
}

.feature-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.8rem;
    margin: 1rem 0 1.4rem 0;
}

.feature-card {
    border-radius: 20px;
    padding: 1rem;
    background: rgba(15, 23, 42, 0.55);
    border: 1px solid rgba(255,255,255,0.12);
    color: #dbeafe;
}

.feature-card strong {
    color: #ffffff;
    display: block;
    margin-bottom: 0.25rem;
}

.converter-card {
    padding: 1.4rem;
    border-radius: 24px;
    background: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(255,255,255,0.16);
    box-shadow: 0 18px 45px rgba(0,0,0,0.28);
}

.footer-note {
    margin-top: 1.4rem;
    padding: 1rem 1.1rem;
    border-radius: 18px;
    background: rgba(2, 6, 23, 0.55);
    border: 1px solid rgba(255,255,255,0.10);
    color: #cbd5e1;
    font-size: 0.9rem;
}

div[data-testid="stForm"] {
    border: 0;
    padding: 0;
}

label, .stRadio label, .stSelectbox label, .stTextInput label {
    color: #e5e7eb !important;
    font-weight: 700 !important;
}

.stTextInput input {
    background: rgba(255,255,255,0.94) !important;
    color: #0f172a !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.94) !important;
    color: #0f172a !important;
    border-radius: 14px !important;
}

.stRadio [role="radiogroup"] {
    gap: 0.6rem;
}

.stButton > button,
.stDownloadButton > button,
button[kind="primaryFormSubmit"] {
    border-radius: 999px !important;
    border: 0 !important;
    padding: 0.75rem 1.4rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #ec4899, #8b5cf6, #3b82f6) !important;
    color: white !important;
    box-shadow: 0 12px 30px rgba(59, 130, 246, 0.30);
}

.stAlert {
    border-radius: 16px;
}

@media (max-width: 760px) {
    .feature-row {
        grid-template-columns: 1fr;
    }
    .hero-card {
        padding: 1.5rem;
    }
}
</style>
"""


st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero-card">
        <div class="brand-kicker">🎞️ Premiere-friendly exports</div>
        <h1 class="hero-title">
            Media Converter<br>
            <span class="gradient-text">MP4 + Audio Export</span>
        </h1>
        <p class="hero-subtitle">
            Paste a media link, choose your export type, and download a clean file
            designed to import smoothly into editing apps like Adobe Premiere Pro.
        </p>
        <div class="credit">By Carlos Knight</div>
    </div>

    <div class="feature-row">
        <div class="feature-card">
            <strong>MP4 Video</strong>
            H.264 video with AAC audio.
        </div>
        <div class="feature-card">
            <strong>Audio Export</strong>
            M4A file with AAC audio.
        </div>
        <div class="feature-card">
            <strong>Editor Ready</strong>
            Fast-start files for smoother importing.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


def find_converter_engine() -> str | None:
    """
    Find the local conversion engine.
    Kept out of the regular UI so non-technical users are not overwhelmed.
    """
    return shutil.which("ffmpeg")


def human_bytes(num: int | float | None) -> str:
    if not num:
        return "0 B"

    num = float(num)
    for unit in ["B", "KB", "MB", "GB"]:
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024

    return f"{num:.1f} TB"


def safe_filename(name: str, fallback: str = "export") -> str:
    cleaned = re.sub(r"[^\w\s.-]", "", name or fallback, flags=re.UNICODE)
    cleaned = re.sub(r"\s+", "_", cleaned).strip("._-")
    return cleaned[:90] or fallback


def find_newest_media_file(download_dir: str, exclude_names: set[str] | None = None) -> Path:
    exclude_names = exclude_names or set()
    directory = Path(download_dir)

    files = [
        p for p in directory.iterdir()
        if p.is_file()
        and p.name not in exclude_names
        and not p.name.endswith(".part")
        and not p.name.endswith(".ytdl")
        and not p.name.endswith(".temp")
    ]

    if not files:
        raise FileNotFoundError("No downloaded media file was created.")

    return max(files, key=lambda p: p.stat().st_mtime)


def run_command(command: list[str]) -> None:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        details = result.stderr.strip() or result.stdout.strip() or "Unknown conversion error."
        raise RuntimeError(details)


def get_yt_dlp_attempts(output_type: str, max_height: int) -> list[dict]:
    """
    Build multiple yt-dlp attempts.

    Why:
    Some hosts, especially YouTube, may reject one client profile or one format URL
    with HTTP 403 even when another format/client works. These attempts do not bypass
    DRM, paywalls, logins, or private content. They simply let yt-dlp try normal
    public client profiles and safer format fallbacks.

    The po_token + visitor_data (obtained via cookies) is the most reliable fix
    for 403s on YouTube from cloud servers as of 2024–2025.
    """
    if output_type == "video":
        format_attempts = [
            # Prefer a single combined mp4 stream — avoids the DASH 403 that
            # separate video+audio streams often trigger on cloud IPs.
            f"best[height<={max_height}][ext=mp4]/best[height<={max_height}]/best[ext=mp4]/best",
            f"b[height<={max_height}]/best",
        ]
    else:
        format_attempts = [
            "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
        ]

    # Most reliable clients for authenticated/cloud requests, ordered by success rate.
    client_attempts = [
        {"extractor_args": {"youtube": {"player_client": ["web"]}}},
        {"extractor_args": {"youtube": {"player_client": ["mweb"]}}},
        {"extractor_args": {"youtube": {"player_client": ["android"]}}},
        {"extractor_args": {"youtube": {"player_client": ["tv_embedded"]}}},
        {},  # yt-dlp default as final fallback
    ]

    attempts = []
    for format_selector in format_attempts:
        for client_options in client_attempts:
            attempt = {
                "format": format_selector,
                **client_options,
            }
            attempts.append(attempt)

    return attempts


def download_source_media(
    url: str,
    temp_dir: str,
    output_type: str,
    max_height: int,
    progress_hook,
    converter_path: str,
    cookies_file: str | None = None,
) -> tuple[dict, Path]:
    """
    Use yt-dlp to download the best available source.
    Then FFmpeg exports it into Premiere-friendly H.264/AAC MP4 or AAC M4A.

    cookies_file: path to a Netscape-format cookies.txt exported from your browser.
    Providing cookies from a logged-in YouTube session is the most reliable fix
    for HTTP 403 errors when running on a cloud server.
    """
    last_error: Exception | None = None
    attempts = get_yt_dlp_attempts(output_type, max_height)

    for attempt_number, attempt in enumerate(attempts, start=1):
        attempt_dir = Path(temp_dir) / f"attempt_{attempt_number}"
        attempt_dir.mkdir(parents=True, exist_ok=True)

        options = {
            "outtmpl": os.path.join(str(attempt_dir), "source.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [progress_hook],
            "ffmpeg_location": converter_path,
            "merge_output_format": "mkv" if output_type == "video" else None,
            "retries": 5,
            "fragment_retries": 5,
            "file_access_retries": 3,
            "extractor_retries": 3,
            "socket_timeout": 30,
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
            "cookiefile": cookies_file,
            **attempt,
        }

        # Remove None values to avoid passing unnecessary config.
        options = {key: value for key, value in options.items() if value is not None}

        try:
            with YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)

            source_file = find_newest_media_file(str(attempt_dir))
            return info, source_file

        except Exception as e:
            last_error = e
            shutil.rmtree(attempt_dir, ignore_errors=True)
            continue

    raise RuntimeError(
        "The site rejected the download request after multiple attempts. "
        "This often happens when the video host blocks cloud-server downloads, "
        "requires login/cookies, requires extra client validation, or restricts that video. "
        f"Last error: {last_error}"
    )


def export_premiere_mp4(source_file: Path, output_file: Path, converter_path: str, crf: int) -> None:
    """
    Export MP4 with Premiere-friendly codecs:
    - Video: H.264
    - Audio: AAC
    - Pixel format: yuv420p
    - Fast-start metadata
    """
    command = [
        converter_path,
        "-y",
        "-i",
        str(source_file),
        "-map",
        "0:v:0",
        "-map",
        "0:a:0?",
        "-c:v",
        "libx264",
        "-profile:v",
        "high",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "medium",
        "-crf",
        str(crf),
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(output_file),
    ]

    run_command(command)


def export_premiere_audio(source_file: Path, output_file: Path, converter_path: str, bitrate: str) -> None:
    """
    Export audio as M4A/AAC, which is friendly for Premiere Pro workflows.
    """
    command = [
        converter_path,
        "-y",
        "-i",
        str(source_file),
        "-map",
        "0:a:0",
        "-vn",
        "-c:a",
        "aac",
        "-b:a",
        bitrate,
        "-movflags",
        "+faststart",
        str(output_file),
    ]

    run_command(command)


def convert_url(
    url: str,
    output_choice: str,
    max_height: int,
    quality_label: str,
    audio_bitrate: str,
    converter_path: str,
    cookies_file: str | None = None,
):
    temp_dir = tempfile.mkdtemp(prefix="carlos_converter_")

    progress_bar = st.progress(0, text="Preparing your export...")
    status_box = st.empty()

    def progress_hook(d):
        status = d.get("status")

        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate")

            if total:
                pct = min(downloaded / total, 1.0)
                progress_bar.progress(
                    pct * 0.70,
                    text=f"Downloading source... {pct:.0%} ({human_bytes(downloaded)} / {human_bytes(total)})",
                )
            else:
                progress_bar.progress(
                    0.15,
                    text=f"Downloading source... {human_bytes(downloaded)}",
                )

        elif status == "finished":
            progress_bar.progress(0.72, text="Preparing editor-friendly export...")

    try:
        output_type = "video" if output_choice.startswith("MP4") else "audio"

        info, source_file = download_source_media(
            url=url,
            temp_dir=temp_dir,
            output_type=output_type,
            max_height=max_height,
            progress_hook=progress_hook,
            converter_path=converter_path,
            cookies_file=cookies_file,
        )

        title = info.get("title", "export") if isinstance(info, dict) else "export"
        base_name = safe_filename(title)

        progress_bar.progress(0.82, text="Finishing export...")

        if output_type == "video":
            crf_by_label = {
                "High quality": 18,
                "Balanced": 21,
                "Smaller file": 24,
            }
            crf = crf_by_label.get(quality_label, 21)
            output_file = Path(temp_dir) / f"{base_name}_H264_AAC.mp4"
            export_premiere_mp4(source_file, output_file, converter_path, crf)
            mime_type = "video/mp4"
            label = "Download MP4"

        else:
            output_file = Path(temp_dir) / f"{base_name}_AAC.m4a"
            export_premiere_audio(source_file, output_file, converter_path, audio_bitrate)
            mime_type = "audio/mp4"
            label = "Download M4A audio"

        file_bytes = output_file.read_bytes()
        file_size = human_bytes(output_file.stat().st_size)

        progress_bar.progress(1.0, text="Export ready.")
        status_box.success(f"Ready: {title}")

        return {
            "filename": output_file.name,
            "data": file_bytes,
            "size": file_size,
            "mime": mime_type,
            "label": label,
        }

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


converter_path = find_converter_engine()

st.markdown('<div class="converter-card">', unsafe_allow_html=True)

with st.form("converter_form"):
    url = st.text_input(
        "Paste your media link",
        placeholder="https://www.youtube.com/watch?v=...",
    )

    output_choice = st.radio(
        "Choose export type",
        [
            "MP4 video for Premiere Pro",
            "Audio export for Premiere Pro",
        ],
        horizontal=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        max_height = st.selectbox(
            "Video resolution",
            [2160, 1440, 1080, 720, 480, 360],
            index=2,
            disabled=not output_choice.startswith("MP4"),
        )

    with col2:
        quality_label = st.selectbox(
            "Video quality",
            ["High quality", "Balanced", "Smaller file"],
            index=1,
            disabled=not output_choice.startswith("MP4"),
        )

    audio_bitrate = st.selectbox(
        "Audio quality",
        ["320k", "256k", "192k", "128k"],
        index=2,
        disabled=output_choice.startswith("MP4"),
    )

    with st.expander("🍪 YouTube cookies (fixes 403 errors on cloud)"):
        st.markdown(
            "If you see **403 Forbidden** errors, upload a `cookies.txt` from your "
            "logged-in YouTube session. This lets the app download as you.\n\n"
            "**How to export cookies:** Install the "
            "[Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) "
            "Chrome extension, go to youtube.com while logged in, click the extension, and export."
        )
        cookies_upload = st.file_uploader(
            "Upload cookies.txt (optional)",
            type=["txt"],
            help="Netscape-format cookies file exported from your browser.",
        )

    submitted = st.form_submit_button("Create Export")

st.markdown("</div>", unsafe_allow_html=True)


if submitted:
    if not url.strip():
        st.error("Paste a link first.")

    elif not converter_path:
        st.error("The export engine is not available on this server.")
        st.info(
            "If you are deploying on Streamlit Cloud, make sure your repo includes `packages.txt`."
        )

    else:
        try:
            # Save uploaded cookies to a temp file if provided
            cookies_path: str | None = None
            if cookies_upload is not None:
                cookies_tmp = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".txt", prefix="yt_cookies_"
                )
                cookies_tmp.write(cookies_upload.getvalue())
                cookies_tmp.flush()
                cookies_tmp.close()
                cookies_path = cookies_tmp.name

            with st.spinner("Creating your editor-friendly file..."):
                result = convert_url(
                    url=url.strip(),
                    output_choice=output_choice,
                    max_height=int(max_height),
                    quality_label=quality_label,
                    audio_bitrate=audio_bitrate,
                    converter_path=converter_path,
                    cookies_file=cookies_path,
                )

            if cookies_path:
                try:
                    os.unlink(cookies_path)
                except OSError:
                    pass

            st.download_button(
                label=f"{result['label']} ({result['size']})",
                data=result["data"],
                file_name=result["filename"],
                mime=result["mime"],
            )

        except DownloadError as e:
            st.error("This link could not be downloaded.")
            with st.expander("Technical details"):
                st.code(str(e), language="text")
            st.info(
                "Some websites block downloads, require login, or do not allow extraction."
            )

        except Exception as e:
            error_text = str(e)
            st.error("The export could not be created.")

            if "403" in error_text or "Forbidden" in error_text or "rejected the download request" in error_text:
                st.info(
                    "This usually means the video host blocked the cloud-server request. "
                    "Try a different public link, a shorter clip, or run the app locally from your own computer. "
                    "The app does not bypass DRM, paywalls, login-only videos, or private/restricted content."
                )

            with st.expander("Technical details"):
                st.code(error_text, language="text")


st.markdown(
    """
    <div class="footer-note">
        Hola Vision Latina :). 
    </div>
    """,
    unsafe_allow_html=True,
)
