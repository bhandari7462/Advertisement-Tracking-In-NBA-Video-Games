import os
import json
from datetime import datetime
from fpdf import FPDF
import pandas as pd

FPS = 1
IMAGE_EXTS = [".png", ".jpg", ".jpeg"]

COLORS = {
    'primary': (41, 128, 185),
    'secondary': (52, 73, 94),
    'accent': (231, 76, 60),
    'light_gray': (236, 240, 241),
    'white': (255, 255, 255),
    'text_dark': (44, 62, 80),
    'text_light': (127, 140, 141)
}

def frame_to_seconds(frame_name, fps=1):
    try:
        frame_number = int(frame_name.replace("frame_", "").replace("_result", ""))
        return round(frame_number / fps, 2)
    except Exception:
        return 0

def find_frame_image(frame_name, frames_dir):
    base = frame_name.replace("_result", "")
    for ext in IMAGE_EXTS:
        candidate = os.path.join(frames_dir, base + ext)
        if os.path.isfile(candidate):
            return candidate
    return None

def _load_frame_texts(path):
    out, current = {}, None
    if not os.path.isfile(path): return out
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("===") and line.endswith("==="):
                current = line.strip("= ").strip()
                out[current] = []
            elif line and current:
                out[current].append(line)
    return out

class EnhancedPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=False)

    def header(self):
        self.set_fill_color(*COLORS['primary'])
        self.rect(0, 0, 210, 25, 'F')
        self.set_font("Arial", "B", 16)
        self.set_text_color(255, 255, 255)
        self.set_y(8)
        self.cell(0, 10, "NBA BROADCAST BRAND VISIBILITY REPORT", 0, 1, "C")
        self.set_font("Arial", "", 10)
        self.set_text_color(200, 200, 200)
        self.cell(0, 6, f"Generated on {datetime.now().strftime('%B %d, %Y')}", 0, 1, "C")
        self.set_text_color(*COLORS['text_dark'])
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(*COLORS['text_light'])
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def check_page_break(self, height_needed):
        if self.get_y() + height_needed > 280:
            self.add_page()
            return True
        return False

    def create_section_header(self, title, color=None):
        if color is None:
            color = COLORS['secondary']
        self.check_page_break(15)
        self.ln(5)
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, f"  {title}", 0, 1, "L", 1)
        self.set_text_color(*COLORS['text_dark'])
        self.ln(3)

    def create_info_box(self, title, content, color=None):
        if color is None:
            color = COLORS['light_gray']
        lines = content.split('\n')
        needed_height = 8 + (len(lines) * 5) + 5
        self.check_page_break(needed_height)
        self.set_fill_color(*color)
        self.set_draw_color(*COLORS['secondary'])
        self.rect(self.get_x(), self.get_y(), 190, 8, 'FD')
        self.set_font("Arial", "B", 10)
        self.cell(190, 8, f"  {title}", 0, 1, "L")
        self.set_font("Arial", "", 9)
        self.set_x(self.get_x() + 5)
        self.multi_cell(180, 5, content.encode('latin-1', errors='ignore').decode('latin-1'))
        self.ln(2)

    def create_styled_table(self, headers, data, col_widths=None):
        if col_widths is None:
            col_widths = [190 // len(headers)] * len(headers)
        needed_height = 8 + (len(data) * 7) + 5
        self.check_page_break(needed_height)
        self.set_fill_color(*COLORS['secondary'])
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 10)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, "C", 1)
        self.ln()
        self.set_text_color(*COLORS['text_dark'])
        self.set_font("Arial", "", 9)
        for i, row in enumerate(data):
            self.set_fill_color(*COLORS['light_gray'] if i % 2 == 0 else COLORS['white'])
            for j, cell in enumerate(row):
                align = "R" if j > 0 else "L"
                clean = str(cell).encode('latin-1', errors='ignore').decode('latin-1')
                self.cell(col_widths[j], 7, clean, 1, 0, align, True)
            self.ln()
        self.ln(5)

    def add_key_metrics_summary(self, df_totals, tot_col):
        top = df_totals.iloc[0]
        metrics_text = f"""
Total Brands Analyzed: {len(df_totals)}
Top Performing Brand: {top['Brand']} (Score: {round(top[tot_col], 2)})
Average Visibility Score: {round(df_totals[tot_col].mean(), 2)}
Analysis Duration: 300 seconds (estimated)
        """.strip()
        self.create_info_box("KEY METRICS", metrics_text, COLORS['accent'])

    def add_methodology_section(self):
        self.create_info_box("METHODOLOGY", """This report uses PaddleOCR and fuzzy matching to analyze frame-level brand visibility in broadcast footage.
Frames are extracted at 1 FPS and processed with OCR, then matched against known brand variants.""")

    def add_brand_analysis_page(self, brand, frame_texts, max_frame, min_frame, max_count, min_count, frames_dir, match_log):
        self.add_page()
        self.create_section_header(f"{brand.upper()} - DETAILED ANALYSIS", COLORS['secondary'])

        self.create_styled_table(
            ["Metric", "Frame (Time)", "Detection Count"],
            [
                ["Peak Frame", f"{max_frame} ({frame_to_seconds(max_frame)}s)" if max_frame else "N/A", str(max_count)],
                ["Lowest Frame", f"{min_frame} ({frame_to_seconds(min_frame)}s)" if min_frame else "N/A", str(min_count)]
            ],
            [50, 90, 50]
        )

        for label, frame in [("PEAK VISIBILITY", max_frame), ("LOWEST VISIBILITY", min_frame)]:
            if not frame:
                continue
            if self.get_y() + 100 > 280:
                break
            self.ln(3)
            self.set_fill_color(*COLORS['light_gray'])
            self.set_font("Arial", "B", 10)
            self.cell(0, 8, f"  {label} FRAME ANALYSIS", 0, 1, "L", 1)
            self.ln(2)

            img = find_frame_image(frame, frames_dir)
            if img and os.path.exists(img):
                h = min(60, 280 - self.get_y() - 30)
                w = min(h * 1.5, 170)
                if self.get_y() + h < 270:
                    self.image(img, x=20, w=w, h=h)
                    self.ln(5)

            matches = [m["word"] for m in match_log.get(frame, []) if m["brand"] == brand]
            if matches and self.get_y() < 260:
                self.set_font("Arial", "B", 9)
                self.cell(0, 5, "Detected Text:", ln=1)
                self.set_font("Arial", "", 8)
                for word in matches[:2]:
                    self.cell(5, 4, "-", 0, 0)
                    self.cell(0, 4, word[:80], 0, 1)
                if len(matches) > 2:
                    self.set_font("Arial", "I", 8)
                    self.cell(0, 4, f"... and {len(matches) - 2} more", 0, 1)

# === Main Report Generator ===
def generate_enhanced_report(base_dir, brand_keywords=None):
    try:
        match_log_path = os.path.join(base_dir, "brand_match_log.json")
        with open(match_log_path, "r", encoding="utf-8") as f:
            match_log = json.load(f)

        frame_texts = _load_frame_texts(os.path.join(base_dir, "paddle_output", "merged_texts.txt"))
        df_totals = pd.read_csv(os.path.join(base_dir, "brand_totals.csv"))
        analysis_csv = os.path.join(base_dir, "brand_analysis.csv")
        df_analysis = pd.read_csv(analysis_csv)
        frames_dir = os.path.join(base_dir, "frames")
        plots_dir = os.path.join(base_dir, "plots")
        output_pdf = os.path.join(base_dir, "brand_report_enhanced.pdf")

        df_totals.columns = df_totals.columns.str.strip()
        tot_col = [c for c in df_totals.columns if "Total" in c][0]
        brands = [c for c in df_analysis.columns if c != "Frame"]
        df_totals = df_totals.sort_values(tot_col, ascending=False)

        pdf = EnhancedPDF()
        pdf.add_page()
        pdf.create_section_header("EXECUTIVE SUMMARY")
        top_brand = df_totals.iloc[0]["Brand"]
        top_score = round(df_totals.iloc[0][tot_col], 2)
        summary = f"This automated analysis covers broadcast footage.\nTop brand: {top_brand} (score: {top_score})."
        pdf.multi_cell(0, 6, summary.strip())
        pdf.ln(5)
        pdf.add_key_metrics_summary(df_totals, tot_col)
        pdf.add_methodology_section()

        pdf.add_page()
        pdf.create_section_header("BRAND VISIBILITY RESULTS")
        total_score = df_totals[tot_col].sum()
        table_data = []
        df_totals_sorted = df_totals.sort_values(tot_col, ascending=False).reset_index(drop=True)
        for i, row in df_totals_sorted.iterrows():
            pct = (row[tot_col] / total_score * 100) if total_score else 0
            table_data.append([
                row["Brand"],
                f"{round(row[tot_col], 3)}",
                f"#{i+1}",
                f"{round(pct, 1)}%"
            ])
        pdf.create_styled_table(["Brand", "Total", "Rank", "Share %"], table_data)

        # Enhanced plot integration with better descriptions and layout
        plot_configs = [
            {
                "file": "brand_timeline_overview.png",
                "title": "BRAND DETECTION TIMELINE",
                "description": "Timeline showing when each brand appears throughout the broadcast. Larger dots indicate stronger detections."
            },
            {
                "file": "brand_market_share.png", 
                "title": "BRAND VISIBILITY MARKET SHARE",
                "description": "Overall distribution of brand visibility across the entire broadcast period."
            },
            {
                "file": "brand_intensity_heatmap.png",
                "title": "DETECTION INTENSITY BY TIME WINDOWS", 
                "description": "Heatmap showing brand detection intensity across different time periods. Darker colors indicate higher activity."
            },
            {
                "file": "brand_frequency_analysis.png",
                "title": "BRAND DETECTION FREQUENCY ANALYSIS",
                "description": "Comparison of total brand detections (left) vs detection consistency across frames (right)."
            },
            {
                "file": "brand_peak_analysis.png",
                "title": "BRAND DETECTION PEAKS AND TRENDS",
                "description": "Timeline analysis showing peak detection moments (marked with stars) and overall trends for each brand."
            },
            {
                "file": "brand_competitive_landscape.png",
                "title": "COMPETITIVE LANDSCAPE - BRAND CO-OCCURRENCES",
                "description": "Analysis of moments when multiple brands appear simultaneously, indicating competitive advertising periods."
            }
        ]

        # Replace the existing plot loop in generate_enhanced_report() with:
        for plot_config in plot_configs:
            plot_path = os.path.join(plots_dir, plot_config["file"])
            if os.path.exists(plot_path):
                pdf.add_page()
                pdf.create_section_header(plot_config["title"])
                
                # Add description
                pdf.set_font("Arial", "", 10)
                pdf.multi_cell(0, 5, plot_config["description"])
                pdf.ln(5)
                
                # Add the plot
                # Calculate image dimensions to fit well on page
                img_width = 170
                img_height = min(180, 280 - pdf.get_y() - 20)  # Leave space for footer
                
                pdf.image(plot_path, x=20, w=img_width, h=img_height)
                pdf.ln(10)

        # Optional: Add a summary insights section
        def add_insights_section(pdf, df_analysis, brand_columns):
            """Add automated insights based on the data analysis"""
            pdf.add_page()
            pdf.create_section_header("KEY INSIGHTS", COLORS['accent'])
            
            insights = []
            
            # Peak detection timing
            for brand in brand_columns:
                brand_data = df_analysis[brand]
                if brand_data.max() > 0:
                    peak_frame = brand_data.idxmax()
                    peak_time = frame_to_seconds(peak_frame)
                    insights.append(f"• {brand} reached peak visibility at {peak_time}s")
            
            # Detection consistency
            for brand in brand_columns:
                detection_rate = (df_analysis[brand] > 0).mean() * 100
                if detection_rate > 0:
                    insights.append(f"• {brand} appears in {detection_rate:.1f}% of analyzed frames")
            
            # Co-occurrence analysis
            co_occur_count = 0
            for _, row in df_analysis.iterrows():
                active_brands = sum(1 for brand in brand_columns if row[brand] > 0)
                if active_brands > 1:
                    co_occur_count += 1
            
            if co_occur_count > 0:
                co_occur_rate = (co_occur_count / len(df_analysis)) * 100
                insights.append(f"• Multiple brands appear together in {co_occur_rate:.1f}% of frames")
            
            # Create insights text
            insights_text = "\n".join(insights) if insights else "No significant patterns detected in the current dataset."
            
            pdf.create_info_box("AUTOMATED INSIGHTS", insights_text)

        # Add this call before the individual brand analysis in generate_enhanced_report():
        # add_insights_section(pdf, df_analysis, brands)
        pdf.output(output_pdf)
        print(f"✅ PDF saved to: {output_pdf}")
    except Exception as e:
        print(f"❌ Failed to generate PDF: {e}")
