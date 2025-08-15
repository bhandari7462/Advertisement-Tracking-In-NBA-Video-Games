import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from tasks.download_and_extract_frames import download_and_extract_frames
from tasks.ocr import run_ocr_on_frames
from tasks.count import count_brands
from tasks.visual import generate_visuals
from tasks.report import generate_enhanced_report
from utils.emailer import send_report_email

def log(message, log_file=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    if log_file:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

def get_video_id(youtube_url):
    query = parse_qs(urlparse(youtube_url).query)
    return query.get("v", [None])[0]

brand_keywords = {
    "YouTube TV": ["youtube", "tube"],
    "Coinbase": ["coin", "base", "coinbas", "coir", "coinb"],
    "StateFarm": ["state","statefarm", "astatefarm"],
    "Michelob Ultra": ["michel", "ultra", "michelao", "michelab", "michewb"],
    "Google": ["google", "gogl", "gogle", "googl", "gooogle"],
    "Tissot": ["tissot", "tiss", "tisso", "tissol", "tissst"],
    "ESPN": ["espn", "esn", "esp", "espm", "espnn"],
    "Kia": ["kia", "kv"]
}

def run_full_pipeline(youtube_url, brands, model, email, timestamp=None):
    try:
        # === Extract video ID ===
        video_id = get_video_id(youtube_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL — unable to extract video ID.")

        # === Define base directory for caching ===
        base_dir = os.path.join("downloads", model, video_id)
        os.makedirs(base_dir, exist_ok=True)
        log_file = os.path.join(base_dir, "pipeline.log")

        log("[0/6] Task received. Checking cache...", log_file)

        # === Prepare brand keywords ===
        selected_brand_keywords = {
            brand: brand_keywords[brand]
            for brand in brands
            if brand in brand_keywords
        }

        # === OCR output check ===
        ocr_output_dir = os.path.join(base_dir, "paddle_output")
        merged_texts_path = os.path.join(ocr_output_dir, "merged_texts.txt")
        frames_dir = os.path.join(base_dir, "frames")

        if not os.path.exists(merged_texts_path):
            # === 1. Download & extract frames ===
            log(f"[1/6] Downloading and extracting frames from URL: {youtube_url}", log_file)
            download_and_extract_frames(youtube_url, fps=1, output_dir=frames_dir)

            # === 2. Run OCR ===
            log("[2/6] Running OCR on frames...", log_file)
            run_ocr_on_frames(frames_dir, ocr_output_dir, model=model)
        else:
            log("🔁 Cached OCR results found. Skipping download and OCR.", log_file)

        # === 3. Count selected brand keywords ===
        log("[3/6] Counting brand keywords...", log_file)
        count_brands(
            merged_texts_path=merged_texts_path,
            base_output_dir=base_dir,
            brand_keywords=selected_brand_keywords
        )

        # === 4. Generate visualizations ===
        log("[4/6] Generating visualizations...", log_file)
        analysis_csv = os.path.join(base_dir, "brand_analysis.csv")
        generate_visuals(analysis_csv, base_dir=base_dir)

        # === 5. Generate PDF report ===
        log("[5/6] Generating PDF report...", log_file)
        generate_enhanced_report(base_dir, selected_brand_keywords)
        pdf_path = os.path.join(base_dir, "brand_report_enhanced.pdf")

        # === 6. Email report ===
        log("[6/6] Sending report via email...", log_file)
        send_report_email(email, pdf_path, subject="Your NBA Brand Visibility Report")

        log("✅ Pipeline completed successfully.", log_file)
        return {"status": "success", "report": pdf_path}

    except Exception as e:
        log(f"❌ Pipeline failed: {e}", log_file if 'log_file' in locals() else None)
        return {"status": "error", "message": str(e)}
