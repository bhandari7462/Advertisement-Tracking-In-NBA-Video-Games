import os
from paddleocr import PaddleOCR
import json
import time

def run_ocr_on_frames(frames_dir, output_dir, model):
    """
    Run OCR on all frames in a directory and save JSON+image results.
    """
    start_time = time.time()

    print(f"Initializing PaddleOCR with model: {model}")
    if model == "epoch50":
        ocr = PaddleOCR(
            det_model_dir="C:/Users/faiza/OneDrive/Desktop/New Pipeline/backend/tasks/inference/epoch50",
            rec_model_dir=None,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False
        )
    else:
        ocr = PaddleOCR(
            text_detection_model_name=model + "_det",
            text_recognition_model_name=model + "_rec",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False
        )

    os.makedirs(output_dir, exist_ok=True)

    image_extensions = ('.jpg', '.jpeg', '.png')
    image_files = [f for f in os.listdir(frames_dir) if f.lower().endswith(image_extensions)]
    image_files.sort()
    max_files = 50
    image_files = image_files[:max_files]

    for idx, img_file in enumerate(image_files):
        output_prefix = os.path.splitext(img_file)[0]
        result_folder = os.path.join(output_dir, f"{output_prefix}_result")
        result_json = os.path.join(result_folder, f"{output_prefix}_res.json")

        # if os.path.isfile(result_json):
        #     print(f"[{idx+1}/{len(image_files)}] Skipping (cached): {img_file}")
        #     continue

        img_path = os.path.join(frames_dir, img_file)
        print(f"[{idx+1}/{len(image_files)}] OCRing: {img_file}")

        result = ocr.predict(img_path)

        for i, res in enumerate(result):
            res.save_to_img(os.path.join(output_dir, f"{output_prefix}_result"))
            res.save_to_json(os.path.join(output_dir, f"{output_prefix}_result"))


    # === Merge JSONs into a single text file ===
    merged_output_file = os.path.join(output_dir, "merged_texts.txt")
    result_folders = [
        f for f in os.listdir(output_dir)
        if os.path.isdir(os.path.join(output_dir, f)) and f.endswith('_result')
    ]
    result_folders.sort()

    with open(merged_output_file, "w", encoding="utf-8") as f_out:
        for folder in result_folders:
            folder_path = os.path.join(output_dir, folder)
            json_filename = folder.replace('_result', '_res.json')
            json_path = os.path.join(folder_path, json_filename)

            if not os.path.isfile(json_path):
                print(f"Skipping missing JSON: {json_path}")
                continue

            with open(json_path, "r", encoding="utf-8") as jf:
                data = json.load(jf)
            rec_texts = data.get("rec_texts", [])

            f_out.write(f"=== {folder} ===\n")
            for text in rec_texts:
                f_out.write(text + "\n")
            f_out.write("\n")

    print(f"✅ Merged OCR texts written to {merged_output_file}")
    print(f"🕒 OCR completed in {round(time.time() - start_time, 2)} seconds.")
