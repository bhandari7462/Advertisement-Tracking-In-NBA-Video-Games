import os
import json
import pandas as pd
from rapidfuzz import fuzz

def count_brands(merged_texts_path, base_output_dir, brand_keywords, threshold=80):
    """
    Count brand keyword occurrences in OCR output using fuzzy matching.
    Always generates CSVs, even with zero results.
    """
    def load_frame_texts(path):
        frame_texts = {}
        current_frame = None
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("===") and line.endswith("==="):
                    current_frame = line.strip("= ").strip()
                    frame_texts[current_frame] = []
                elif line and current_frame:
                    frame_texts[current_frame].append(line)
        return frame_texts

    frame_texts = load_frame_texts(merged_texts_path)
    valid_frames = {k: v for k, v in frame_texts.items() if v and any(line.strip() for line in v)}

    if not valid_frames:
        print("⚠️ No valid OCR text found in any frame. Generating empty CSVs.")
        # Fake one row with zeros for all brands
        df_analysis = pd.DataFrame([{"Frame": "no_valid_frames", **{brand: 0 for brand in brand_keywords}}])
    else:
        print(f"📊 Counting brands in {len(valid_frames)} frames...")

        def score_brands():
            results = []
            match_log = {}  # New: to store matches per frame

            for frame, lines in frame_texts.items():
                row = {"Frame": frame}
                match_log[frame] = []  # Initialize frame's match list

                for brand, variants in brand_keywords.items():
                    count = 0
                    for line in lines:
                        words = line.lower().split()
                        for word in words:
                            for variant in variants:
                                score = fuzz.ratio(variant, word)
                                if score >= threshold:
                                    count += 1
                                    match_log[frame].append({
                                        "brand": brand,
                                        "word": word,
                                        "matched_variant": variant,
                                        "score": score
                                    })
                                    break
                    row[brand] = count
                results.append(row)


                # === Step 5: Save detailed match log ===
            match_log_path = os.path.join(base_output_dir, "brand_match_log.json")
            with open(match_log_path, "w", encoding="utf-8") as f:
                json.dump(match_log, f, indent=2, ensure_ascii=False)

            print(f"📄 Saved match log to: {match_log_path}")
            return pd.DataFrame(results)

        df_analysis = score_brands()

    # Save analysis CSV
    analysis_csv = os.path.join(base_output_dir, "brand_analysis.csv")
    df_analysis.to_csv(analysis_csv, index=False)

    # Save totals CSV
    brand_cols = [c for c in df_analysis.columns if c != "Frame"]
    df_totals = df_analysis[brand_cols].sum().reset_index()
    df_totals.columns = ["Brand", "Total Score"]
    totals_csv = os.path.join(base_output_dir, "brand_totals.csv")
    df_totals.to_csv(totals_csv, index=False)
    

    print(f"✅ Saved brand_analysis.csv to: {analysis_csv}")
    print(f"✅ Saved brand_totals.csv to: {totals_csv}")
