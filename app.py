import os
import re
import sys
import shutil
import subprocess
import tempfile
import platform
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="Carlos Knight Media Converter",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed",
)


CUSTOM_CSS = """
<style>
.stApp {
    background:
        radial-gradient(circle at 10% 20%, rgba(255, 90, 120, 0.25), transparent 28%),
        radial-gradient(circle at 90% 10%, rgba(96, 165, 250, 0.28), transparent 30%),
        radial-gradient(circle at 50% 90%, rgba(168, 85, 247, 0.24), transparent 28%),
        linear-gradient(135deg, #0f172a 0%, #111827 45%, #020617 100%);
    color: #f8fafc;
}

.block-container {
    max-width: 930px;
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

.local-note {
    margin: 1rem 0 1.3rem 0;
    padding: 1rem 1.1rem;
    border-radius: 18px;
    background: rgba(34, 197, 94, 0.12);
    border: 1px solid rgba(74, 222, 128, 0.22);
    color: #dcfce7;
    font-size: 0.95rem;
}

.cloud-note {
    margin: 1rem 0 1.3rem 0;
    padding: 1rem 1.1rem;
    border-radius: 18px;
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(251, 191, 36, 0.25);
    color: #fef3c7;
    font-size: 0.95rem;
}

div[data-testid="stForm"] {
    border: 0;
    padding: 0;
}

label, .stRadio label, .stSelectbox label, .stTextInput label, .stCheckbox label {
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
        <div class="brand-kicker">🎞️ Stacher-style yt-dlp interface</div>
        <h1 class="hero-title">
            Media Converter<br>
            <span class="gradient-text">MP4 + Audio Export</span>
        </h1>
        <p class="hero-subtitle">
            Paste a link, choose your export, and download a clean file designed to import smoothly into editing apps like Adobe Premiere Pro.
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
            <strong>Local Friendly</strong>
            Can use your own browser session.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


def is_streamlit_cloud() -> bool:
    """
    Best-effort Streamlit Cloud detection.
    Cloud paths typically run under /mount/src and cannot access a user's browser cookies.
    """
    cwd = str(Path.cwd())
    return cwd.startswith("/mount/src") or os.getenv("STREAMLIT_RUNTIME_ENV") == "cloud"


def find_exe(name: str) -> str | None:
    return shutil.which(name)


def default_download_dir() -> str:
    home = Path.home()
    downloads = home / "Downloads"
    if downloads.exists():
        return str(downloads)
    return str(home)


def safe_filename(name: str, fallback: str = "export") -> str:
    cleaned = re.sub(r"[^\w\s.-]", "", name or fallback, flags=re.UNICODE)
    cleaned = re.sub(r"\s+", "_", cleaned).strip("._-")
    return cleaned[:90] or fallback


def human_bytes(num: int | float | None) -> str:
    if not num:
        return "0 B"
    num = float(num)
    for unit in ["B", "KB", "MB", "GB"]:
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} TB"


def newest_file(folder: str | Path, preferred_ext: str | None = None) -> Path:
    folder = Path(folder)
    files = [
        p for p in folder.iterdir()
        if p.is_file()
        and not p.name.endswith(".part")
        and not p.name.endswith(".ytdl")
        and not p.name.endswith(".temp")
    ]
    if preferred_ext:
        preferred = [p for p in files if p.suffix.lower() == f".{preferred_ext.lower()}"]
        if preferred:
            files = preferred
    if not files:
        raise FileNotFoundError("No output file was created.")
    return max(files, key=lambda p: p.stat().st_mtime)


def read_uploaded_cookies(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    try:
        return uploaded_file.getvalue().decode("utf-8", errors="ignore").strip()
    except Exception:
        return ""


def read_secret_cookies() -> str:
    """
    Read YouTube cookies from Streamlit Secrets.

    In Streamlit Cloud, set a secret named YOUTUBE_COOKIES_TXT and paste the
    full Netscape cookies.txt content as a TOML multiline string.

    Do not commit real cookies to GitHub.
    """
    try:
        value = st.secrets.get("YOUTUBE_COOKIES_TXT", "")
        if value is None:
            return ""
        return str(value).strip()
    except Exception:
        return ""


def secret_cookies_available() -> bool:
    return valid_cookie_text(read_secret_cookies())



def valid_cookie_text(cookie_text: str) -> bool:
    if not cookie_text:
        return False
    lower = cookie_text.lower()
    return ("youtube.com" in lower or ".youtube.com" in lower) and "\t" in cookie_text


def write_temp_cookies(cookie_text: str) -> str | None:
    if not valid_cookie_text(cookie_text):
        return None

    tmp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".txt",
        prefix="yt_cookies_",
        mode="w",
        encoding="utf-8",
    )
    tmp.write(cookie_text)
    tmp.flush()
    tmp.close()
    return tmp.name


def run_process(command: list[str], progress_bar=None, status_box=None) -> str:
    """
    Run a subprocess and stream logs into Streamlit.
    """
    log_lines: list[str] = []

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    percent_re = re.compile(r"(\d{1,3}(?:\.\d+)?)%")

    if process.stdout:
        for line in process.stdout:
            clean = line.rstrip()
            if clean:
                log_lines.append(clean)

            match = percent_re.search(clean)
            if progress_bar and match:
                try:
                    pct = float(match.group(1))
                    progress_bar.progress(min(max(pct / 100, 0), 0.95), text=clean[:120])
                except Exception:
                    pass

            if status_box and clean:
                status_box.caption(clean[:180])

    return_code = process.wait()
    full_log = "\n".join(log_lines)

    if return_code != 0:
        raise RuntimeError(full_log or f"Command failed with exit code {return_code}")

    return full_log


def build_ytdlp_command(
    url: str,
    temp_dir: str,
    output_type: str,
    max_height: int,
    cookies_file: str | None,
    browser_cookie_source: str,
    use_browser_cookies: bool,
    advanced_args: str,
) -> list[str]:
    if output_type == "video":
        # Stacher-like default. Download best available source first.
        fmt = f"bestvideo*[height<={max_height}]+bestaudio/best[height<={max_height}]/best"
        merge_format = "mkv"
    else:
        fmt = "bestaudio[ext=m4a]/bestaudio/best"
        merge_format = "mka"

    command = [
        sys.executable,
        "-m",
        "yt_dlp",
        url,
        "--no-playlist",
        "--newline",
        "--progress",
        "--force-ipv4",
        "--retries",
        "5",
        "--fragment-retries",
        "5",
        "--socket-timeout",
        "30",
        "--format",
        fmt,
        "--merge-output-format",
        merge_format,
        "--paths",
        temp_dir,
        "--output",
        "source.%(ext)s",
    ]

    ffmpeg = find_exe("ffmpeg")
    if ffmpeg:
        command += ["--ffmpeg-location", ffmpeg]

    if cookies_file:
        command += ["--cookies", cookies_file]
    elif use_browser_cookies and browser_cookie_source != "None":
        # This is the key Stacher-like behavior.
        # It only works when the Streamlit app runs locally on the user's own computer.
        command += ["--cookies-from-browser", browser_cookie_source.lower()]

    if advanced_args.strip():
        # Basic advanced mode for users who already know yt-dlp args.
        # shlex handles quoted values correctly on Unix and Windows.
        import shlex
        command += shlex.split(advanced_args.strip())

    return command


def ffmpeg_export_mp4(source_file: Path, output_file: Path, quality: str) -> None:
    ffmpeg = find_exe("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg was not found.")

    crf_map = {
        "High quality": "18",
        "Balanced": "21",
        "Smaller file": "24",
    }
    crf = crf_map.get(quality, "21")

    command = [
        ffmpeg,
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
        crf,
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(output_file),
    ]
    run_process(command)


def ffmpeg_export_m4a(source_file: Path, output_file: Path, bitrate: str) -> None:
    ffmpeg = find_exe("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg was not found.")

    command = [
        ffmpeg,
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
    run_process(command)


def explain_download_error(error_text: str, cloud_mode: bool, used_browser_cookies: bool, used_cookie_file: bool) -> str:
    lower = error_text.lower()

    if "sign in" in lower or "confirm you're not a bot" in lower or "confirm you’re not a bot" in lower:
        if cloud_mode:
            return (
                "YouTube is asking the cloud server to sign in. Stacher avoids this more often because it runs on your own computer. "
                "Add fresh cookies to Streamlit Secrets, upload cookies.txt in Advanced, or run this app locally and enable browser cookies."
            )
        return (
            "YouTube is asking for a signed-in browser session. Enable browser cookies, close your browser if cookie extraction fails, "
            "or upload a fresh cookies.txt file exported from a session that can play the video."
        )

    if "http error 403" in lower or "forbidden" in lower:
        if cloud_mode:
            return (
                "YouTube blocked the Streamlit Cloud server. This is the main difference from Stacher: Stacher downloads from your local computer, "
                "not from a public datacenter IP. Add fresh cookies to Streamlit Secrets, upload cookies.txt in Advanced, or run the app locally for the Stacher-like behavior."
            )
        return (
            "YouTube returned 403 from this machine. Try browser cookies, a fresh cookies.txt file, updating yt-dlp, or a different public link."
        )

    if "drm" in lower:
        return (
            "yt-dlp reported DRM-protected media. This app cannot bypass DRM. If you think that report is wrong, run locally with fresh browser cookies."
        )

    if "requested format is not available" in lower:
        return (
            "The requested format was not exposed to yt-dlp. Try a lower resolution, audio export, browser cookies, or a different public link."
        )

    return "The export could not be created. Try running locally, updating yt-dlp, or using a different public link."


cloud = is_streamlit_cloud()

if cloud:
    st.markdown(
        """
        <div class="cloud-note">
        <strong>Cloud mode detected.</strong> Streamlit Cloud downloads from a public server IP, so YouTube may block some videos with 403 or sign-in errors.
        This version can use YouTube cookies stored in Streamlit Secrets as <code>YOUTUBE_COOKIES_TXT</code>.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="local-note">
        <strong>Local mode detected.</strong> This is closest to Stacher: downloads run from your computer and can use your browser session.
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown('<div class="converter-card">', unsafe_allow_html=True)

with st.form("converter_form"):
    url = st.text_input("Paste your media link", placeholder="https://www.youtube.com/watch?v=...")

    output_choice = st.radio(
        "Choose export type",
        ["MP4 video for Premiere Pro", "Audio export for Premiere Pro"],
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

    save_mode = st.radio(
        "Save method",
        [
            "Download button in browser",
            "Save directly to local folder",
        ],
        index=0 if cloud else 1,
        help=(
            "Browser download works on cloud but loads the finished file into Streamlit memory. "
            "Local folder save is closest to Stacher and works best when running this app locally."
        ),
    )

    output_folder = st.text_input(
        "Local output folder",
        value=default_download_dir(),
        disabled=save_mode != "Save directly to local folder",
    )

    with st.expander("Advanced: YouTube sign-in / 403 fixes"):
        st.caption(
            "Stacher works well because it runs locally. On Streamlit Cloud, the best available option is using YouTube cookies stored in Streamlit Secrets."
        )

        if secret_cookies_available():
            st.success("YouTube cookies are configured in Streamlit Secrets.")
        else:
            st.warning(
                "No valid YouTube cookies found in Streamlit Secrets. "
                "Add YOUTUBE_COOKIES_TXT in Streamlit Cloud Settings → Secrets."
            )

        use_secret_cookies = st.checkbox(
            "Use YouTube cookies from Streamlit Secrets",
            value=secret_cookies_available(),
            disabled=not secret_cookies_available(),
            help="Recommended for Streamlit Cloud. Cookies are read from st.secrets and written to a temporary file only during conversion.",
        )

        use_browser_cookies = st.checkbox(
            "Use cookies from my local browser",
            value=not cloud,
            disabled=cloud,
            help="Only works when this Streamlit app is running locally on your computer.",
        )

        browser_cookie_source = st.selectbox(
            "Browser",
            ["Chrome", "Edge", "Firefox", "Brave", "Safari", "None"],
            index=0,
            disabled=(cloud or not use_browser_cookies),
        )

        cookies_upload = st.file_uploader(
            "Or upload cookies.txt",
            type=["txt"],
            accept_multiple_files=False,
            help="Use only for videos you own, have permission to use, or can legitimately access.",
        )

        advanced_args = st.text_input(
            "Extra yt-dlp arguments",
            value="",
            placeholder="Example: --verbose",
            help="Optional. For advanced users who already know yt-dlp flags.",
        )

    submitted = st.form_submit_button("Create Export")

st.markdown("</div>", unsafe_allow_html=True)


if submitted:
    if not url.strip():
        st.error("Paste a link first.")
        st.stop()

    if not find_exe("ffmpeg"):
        st.error("FFmpeg was not found. Install FFmpeg first.")
        st.stop()

    progress = st.progress(0, text="Preparing your export...")
    status = st.empty()

    uploaded_cookie_text = read_uploaded_cookies(cookies_upload)
    secret_cookie_text = read_secret_cookies() if "use_secret_cookies" in locals() and use_secret_cookies else ""

    # Priority:
    # 1. uploaded cookies.txt for this one conversion
    # 2. YOUTUBE_COOKIES_TXT from Streamlit Secrets
    # 3. local browser cookies, only when running locally
    cookie_text = uploaded_cookie_text or secret_cookie_text

    cookies_file = None
    temp_dir = tempfile.mkdtemp(prefix="carlos_ytdlp_")

    try:
        if cookie_text:
            cookies_file = write_temp_cookies(cookie_text)
            if not cookies_file:
                st.warning("The uploaded cookies.txt file did not look valid, so it was ignored.")

        output_type = "video" if output_choice.startswith("MP4") else "audio"

        command = build_ytdlp_command(
            url=url.strip(),
            temp_dir=temp_dir,
            output_type=output_type,
            max_height=int(max_height),
            cookies_file=cookies_file,
            browser_cookie_source=browser_cookie_source,
            use_browser_cookies=use_browser_cookies,
            advanced_args=advanced_args,
        )

        status.caption("Downloading source with yt-dlp...")
        run_process(command, progress_bar=progress, status_box=status)

        source_file = newest_file(temp_dir)

        title_base = safe_filename(source_file.stem.replace("source", "export"))
        if output_type == "video":
            final_name = f"{title_base}_H264_AAC.mp4"
            final_temp = Path(temp_dir) / final_name
            progress.progress(0.96, text="Converting to Premiere-friendly MP4...")
            ffmpeg_export_mp4(source_file, final_temp, quality_label)
            mime = "video/mp4"
            button_label = "Download MP4"
        else:
            final_name = f"{title_base}_AAC.m4a"
            final_temp = Path(temp_dir) / final_name
            progress.progress(0.96, text="Converting to Premiere-friendly M4A...")
            ffmpeg_export_m4a(source_file, final_temp, audio_bitrate)
            mime = "audio/mp4"
            button_label = "Download M4A"

        progress.progress(1.0, text="Export ready.")

        if save_mode == "Save directly to local folder":
            folder = Path(output_folder).expanduser()
            folder.mkdir(parents=True, exist_ok=True)
            final_path = folder / final_name
            shutil.copy2(final_temp, final_path)
            st.success(f"Saved to: {final_path}")
            st.caption("This local-save mode is closest to Stacher.")

        else:
            data = final_temp.read_bytes()
            st.download_button(
                label=f"{button_label} ({human_bytes(len(data))})",
                data=data,
                file_name=final_name,
                mime=mime,
            )

    except Exception as e:
        error_text = str(e)
        st.error("The export could not be created.")
        st.info(
            explain_download_error(
                error_text=error_text,
                cloud_mode=cloud,
                used_browser_cookies=use_browser_cookies and not cloud,
                used_cookie_file=bool(cookies_file),
            )
        )

        with st.expander("Technical details"):
            st.code(error_text, language="text")

    finally:
        if cookies_file:
            try:
                os.unlink(cookies_file)
            except OSError:
                pass
        shutil.rmtree(temp_dir, ignore_errors=True)


st.markdown(
    """
    <div class="footer-note">
        Hola Vision Latina :). Use only for media you own, have permission to use, or can legitimately access.
        This app does not bypass DRM, paywalls, private videos, or platform restrictions.
    </div>
    """,
    unsafe_allow_html=True,
)
