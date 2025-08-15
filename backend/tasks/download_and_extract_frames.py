import os
import re
import cv2
import yt_dlp
from datetime import datetime

def log(message, log_file=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    if log_file:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

def sanitize_filename(name):
    """Sanitize filename for filesystem compatibility."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def download_video(url):
    """
    Download a YouTube video via yt_dlp.
    Returns (path_to_mp4, run_directory).
    """
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = sanitize_filename(info.get("title", "downloaded_video"))

    run_dir = os.path.abspath(title)
    os.makedirs(run_dir, exist_ok=True)
    output_template = os.path.join(run_dir, "video.%(ext)s")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "merge_output_format": "mp4",
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for file in os.listdir(run_dir):
        if file.endswith(".mp4"):
            return os.path.join(run_dir, file), run_dir

    raise RuntimeError("No MP4 file found after download.")

def extract_frames(video_path, output_dir, fps=1):
    """
    Extract frames from a video at the given FPS.
    Returns the directory where frames were saved.
    """
    print("Extracting frames.")
    os.makedirs(output_dir, exist_ok=True)
    vidcap = cv2.VideoCapture(video_path)
    video_fps = vidcap.get(cv2.CAP_PROP_FPS)

    if not video_fps or video_fps <= 0:
        raise ValueError("Unable to read FPS from video.")

    interval = max(int(video_fps / fps), 1)
    frame_count, frame_id = 0, 0

    while True:
        success, frame = vidcap.read()
        if not success:
            break
        if frame_count % interval == 0:
            cv2.imwrite(os.path.join(output_dir, f"frame_{frame_id:04d}.jpg"), frame)
            frame_id += 1
        frame_count += 1

    vidcap.release()
    print("Frames extracted succefully")
    return output_dir

import os
import re
import cv2
import yt_dlp
from datetime import datetime

def log(message, log_file=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    if log_file:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

def sanitize_filename(name):
    """Sanitize filename for filesystem compatibility."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def download_video(url):
    """
    Download a YouTube video via yt_dlp.
    Returns (path_to_mp4, run_directory).
    """
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = sanitize_filename(info.get("title", "downloaded_video"))

    run_dir = os.path.abspath(title)
    os.makedirs(run_dir, exist_ok=True)
    output_template = os.path.join(run_dir, "video.%(ext)s")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "merge_output_format": "mp4",
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for file in os.listdir(run_dir):
        if file.endswith(".mp4"):
            return os.path.join(run_dir, file), run_dir

    raise RuntimeError("No MP4 file found after download.")

def extract_frames(video_path, output_dir, fps=1):
    """
    Extract frames from a video at the given FPS.
    Returns the directory where frames were saved.
    """
    print("Extracting frames.")
    os.makedirs(output_dir, exist_ok=True)
    vidcap = cv2.VideoCapture(video_path)
    video_fps = vidcap.get(cv2.CAP_PROP_FPS)

    if not video_fps or video_fps <= 0:
        raise ValueError("Unable to read FPS from video.")

    interval = max(int(video_fps / fps), 1)
    frame_count, frame_id = 0, 0

    while True:
        success, frame = vidcap.read()
        if not success:
            break
        if frame_count % interval == 0:
            cv2.imwrite(os.path.join(output_dir, f"frame_{frame_id:04d}.jpg"), frame)
            frame_id += 1
        frame_count += 1

    vidcap.release()
    print("Frames extracted succefully")
    return output_dir

def download_and_extract_frames(youtube_url, fps=1, output_dir=None, log_file=None):
    """
    Combined function: Downloads video and extracts frames.
    Returns absolute path to the frame output directory.
    """
    if log_file:
        log("Downloading YouTube video and extracting frames...", log_file)

    # Download video
    video_path, run_dir = download_video(youtube_url)

    # Decide frame output location
    frames_dir = output_dir if output_dir else os.path.join(run_dir, "frames")

    # Extract frames
    extract_frames(video_path, frames_dir, fps=fps)

    return frames_dir
