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


# ---------------------------------------------------------------------------
# PO Token (Proof-of-Origin) provider setup
# ---------------------------------------------------------------------------
# bgutil-ytdlp-pot-provider clones a small Node.js script at first startup,
# then generates fresh PO Tokens on every yt-dlp call. PO Tokens prove the
# request came from a real browser — no account, no cookies, no expiry.
#
# Node.js is installed via packages.txt. The one-time npm install + TypeScript
# compile runs automatically when the app starts for the first time on a new
# container. Subsequent calls hit the @st.cache_resource cache instantly.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Cookie strategy — two layers, applied in priority order:
#
# 1. ACCOUNT COOKIES (Streamlit secret: YOUTUBE_COOKIES_TXT)
#    Export from a LOGGED-IN YouTube session using the "Get cookies.txt
#    LOCALLY" Chrome extension. Required for age-restricted, members-only,
#    or any video that shows "Please sign in". Paste the full file contents
#    into Streamlit Cloud → Settings → Secrets as:
#      YOUTUBE_COOKIES_TXT = """..."""
#
# 2. ANONYMOUS COOKIES (baked in)
#    Exported from an incognito YouTube session. No account data. Used as
#    a browser-legitimacy signal for public videos when no account secret
#    is configured. Expires ~2027.
# ---------------------------------------------------------------------------

_ANON_COOKIES = """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	TRUE	1795623095	__Secure-YNID	18.YT=xhDdq_iwRMdcYKXazaIKAIm4yu-PoYOKWwga2oPTvpHat9gH95Wpq8KmKDweiyd9EyvijacSPxln2CTGfPOw_--eMDBGPvrakz13X0sADVXnFhXSbfXQUkO3Us980vpMMmGWCtM6OQkYu-wKTPfyzEsTZD61duip6v73EjNS51joVIPqf5kImH3XAdf77M0ne0VQ7WszaIoXJ1XJyKPG3FKyhihxG0Wpur1YnfBAMTBT9q96eyWWm_iffqkFIkpl73j4R_XqU53RXo9fgJVap_ZxqgKSLLnlygL2SJwMfwnOVsBIEKW62RxdbfCxDC2rb7iDU9FukhW7eBHrn5g0iQ
.youtube.com	TRUE	/	TRUE	1780072896	GPS	1
.youtube.com	TRUE	/	TRUE	0	YSC	--KZVBEDOnE
.youtube.com	TRUE	/	TRUE	1795623097	VISITOR_INFO1_LIVE	YtVh-_hI0PU
.youtube.com	TRUE	/	TRUE	1795623097	VISITOR_PRIVACY_METADATA	CgJVUxIEGgAgSA%3D%3D
.youtube.com	TRUE	/	TRUE	1814631097	PREF	f4=4000000&f6=40000000&tz=America.Denver
.youtube.com	TRUE	/	TRUE	1795623096	__Secure-ROLLOUT_TOKEN	CKHmiYLV7PSqyAEQhILNyvHelAMYhvCFy_HelAM%3D
"""


def _write_cookies_to_tempfile() -> str:
    """
    Write the best available cookies to a temp file and return its path.
    Prefers account cookies from Streamlit secrets; falls back to anonymous.
    """
    # Try account cookies from Streamlit secrets first.
    try:
        account_cookies = st.secrets.get("YOUTUBE_COOKIES_TXT", "").strip()
    except Exception:
        account_cookies = ""

    cookie_text = account_cookies if account_cookies else _ANON_COOKIES

    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".txt", prefix="yt_cookies_", mode="w"
    )
    tmp.write(cookie_text)
    tmp.flush()
    tmp.close()
    return tmp.name


@st.cache_resource(show_spinner=False)
def _setup_pot_provider() -> bool:
    """
    Clone bgutil-ytdlp-pot-provider and compile its TypeScript once per
    container lifetime. Returns True on success, False on failure (the app
    falls back to cookies-only mode automatically).

    Steps performed on first call:
      1. git clone Brainicism/bgutil-ytdlp-pot-provider -> ~/bgutil-ytdlp-pot-provider
      2. npm install  (in server/ subdirectory)
      3. npx tsc      (compiles TypeScript to build/*)
    Node.js is provided by packages.txt so npm/npx are always available.
    """
    home = Path.home()
    server_dir = home / "bgutil-ytdlp-pot-provider" / "server"
    sentinel = server_dir / "build" / "generate_once.js"

    if sentinel.exists():
        return True  # Already built on this container — nothing to do.

    try:
        clone_dir = home / "bgutil-ytdlp-pot-provider"
        if not clone_dir.exists():
            subprocess.run(
                [
                    "git", "clone", "--depth", "1",
                    "https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git",
                    str(clone_dir),
                ],
                check=True,
                capture_output=True,
                timeout=120,
            )

        subprocess.run(
            ["npm", "install", "--prefer-offline"],
            check=True,
            capture_output=True,
            cwd=str(server_dir),
            timeout=240,
        )

        subprocess.run(
            ["npx", "--yes", "tsc"],
            check=True,
            capture_output=True,
            cwd=str(server_dir),
            timeout=120,
        )

        return sentinel.exists()

    except Exception:
        return False


def _build_attempts(output_type: str, max_height: int) -> list[dict]:
    """
    Return download attempt configs ordered by cloud-server success rate.
    Format selection is intentionally permissive — yt-dlp just fetches the raw
    bits, and FFmpeg re-encodes everything into the final clean MP4 or M4A.
    """
    if output_type == "video":
        format_selectors = [
            # Single combined stream first — no DASH merge, fewer 403s.
            f"best[height<={max_height}]/best",
            "best",
        ]
    else:
        format_selectors = [
            "bestaudio/best",
        ]

    # Client profiles ordered by cloud-server success rate (2025/2026).
    #
    # ios/android: use mobile API paths that bypass YouTube's cloud-IP
    # bot detection even without PO tokens. These are the most reliable
    # clients for public videos from cloud servers.
    #
    # web_creator/mweb/web: web clients that need PO tokens on cloud IPs.
    #
    # The bgutil POT plugin hooks in automatically for all clients.
    client_profiles = [
        {"extractor_args": {"youtube": {"player_client": ["ios"]}}},
        {"extractor_args": {"youtube": {"player_client": ["android"]}}},
        {"extractor_args": {"youtube": {"player_client": ["web_creator"]}}},
        {"extractor_args": {"youtube": {"player_client": ["mweb"]}}},
        {"extractor_args": {"youtube": {"player_client": ["web"]}}},
        {"extractor_args": {"youtube": {"player_client": ["tv_embedded"]}}},
        {},  # yt-dlp default
    ]

    attempts = []
    for fmt in format_selectors:
        for client in client_profiles:
            attempts.append({"format": fmt, **client})
    return attempts


def _bgutil_server_home() -> str | None:
    """Return the bgutil server home path if the compiled scripts exist."""
    path = Path.home() / "bgutil-ytdlp-pot-provider"
    if (path / "server" / "build" / "generate_once.js").exists():
        return str(path)
    return None


def download_source_media(
    url: str,
    temp_dir: str,
    output_type: str,
    max_height: int,
    progress_hook,
    converter_path: str,
) -> tuple[dict, Path]:
    """
    Download the raw source with yt-dlp, then FFmpeg re-encodes everything.
    PO Tokens are provided automatically by the bgutil plugin (if set up).
    Anonymous cookies are always sent as a supplementary signal.
    """
    cookies_file = _write_cookies_to_tempfile()
    last_error: Exception | None = None
    attempts = _build_attempts(output_type, max_height)

    # If bgutil scripts are compiled, tell the plugin exactly where they are.
    bgutil_home = _bgutil_server_home()

    try:
        for attempt_number, attempt in enumerate(attempts, start=1):
            attempt_dir = Path(temp_dir) / f"attempt_{attempt_number}"
            attempt_dir.mkdir(parents=True, exist_ok=True)

            # Build extractor_args: merge bgutil server_home (if available)
            # with the per-attempt youtube player_client arg.
            extractor_args: dict = {}
            if bgutil_home:
                extractor_args["youtubepot-bgutilscript"] = {
                    "server_home": [bgutil_home]
                }
            attempt_ea = attempt.get("extractor_args", {})
            for k, v in attempt_ea.items():
                extractor_args[k] = v
            attempt_without_ea = {k: v for k, v in attempt.items()
                                   if k != "extractor_args"}

            options = {
                "outtmpl": os.path.join(str(attempt_dir), "source.%(ext)s"),
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "progress_hooks": [progress_hook],
                "ffmpeg_location": converter_path,
                # mkv container for merging — FFmpeg converts to clean MP4/M4A.
                "merge_output_format": "mkv",
                "retries": 5,
                "fragment_retries": 5,
                "file_access_retries": 3,
                "extractor_retries": 3,
                "socket_timeout": 30,
                "cookiefile": cookies_file,
                "extractor_args": extractor_args,
                "http_headers": {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/125.0.0.0 Safari/537.36"
                    ),
                    "Accept-Language": "en-US,en;q=0.9",
                },
                **attempt_without_ea,
            }

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
            "Could not download the video after multiple attempts. "
            "Common causes: the video host blocks cloud-server IPs, the video requires "
            "a login, is private/restricted, or is DRM-protected. "
            f"Last error: {last_error}"
        )
    finally:
        # Always delete the temp cookies file immediately after use.
        try:
            os.unlink(cookies_file)
        except OSError:
            pass


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


# Set up the PO Token provider once at startup (runs git clone + npm build
# the first time; subsequent container restarts use the cached result).
_setup_pot_provider()

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
            with st.spinner("Creating your editor-friendly file..."):
                result = convert_url(
                    url=url.strip(),
                    output_choice=output_choice,
                    max_height=int(max_height),
                    quality_label=quality_label,
                    audio_bitrate=audio_bitrate,
                    converter_path=converter_path,
                )

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

            sign_in_error = "sign in" in error_text.lower() or "please sign" in error_text.lower()
            forbidden_error = "403" in error_text or "Forbidden" in error_text or "rejected the download request" in error_text
            drm_error = "DRM" in error_text or "drm" in error_text.lower()

            if sign_in_error:
                st.warning(
                    "This video requires a signed-in YouTube account to download. "
                    "To fix this: export cookies from a **logged-in** YouTube session using the "
                    "[Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) "
                    "Chrome extension, then add them to Streamlit Cloud under **Settings → Secrets** as "
                    "`YOUTUBE_COOKIES_TXT` under Settings → Secrets."
                )
            elif drm_error:
                st.warning(
                    "This video is DRM-protected and cannot be downloaded by any tool. "
                    "DRM is a hard technical barrier that cannot be bypassed."
                )
            elif forbidden_error:
                st.info(
                    "The video host blocked the download request from this cloud server. "
                    "Try adding account cookies via Streamlit Secrets (see above), "
                    "or run the app locally on your own computer where IP blocks don't apply."
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
