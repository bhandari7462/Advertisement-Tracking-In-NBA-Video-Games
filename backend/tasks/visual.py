import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # MUST be before importing pyplot
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Rectangle

def generate_visuals(analysis_csv, base_dir):
    """
    Generate meaningful brand visualizations for the report
    """
    df = pd.read_csv(analysis_csv)
    df["FrameIndex"] = df.index
    df["TimeSeconds"] = df["FrameIndex"]  # Assuming 1 FPS
    brand_columns = [col for col in df.columns if col not in ["Frame", "FrameIndex", "TimeSeconds"]]

    # Create plots directory
    plots_dir = os.path.join(base_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    # Set consistent style for all plots
    plt.style.use('default')
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#593E2B', '#6A994E']
    
    # --- 1. TIMELINE OVERVIEW: Brand visibility over time ---
    plt.figure(figsize=(16, 8))
    for i, brand in enumerate(brand_columns):
        color = colors[i % len(colors)]
        # Plot actual detections as scatter points
        detections = df[df[brand] > 0]
        if not detections.empty:
            plt.scatter(detections["TimeSeconds"], [i] * len(detections), 
                       s=detections[brand] * 30, c=color, alpha=0.7, label=brand)
    
    plt.title("Brand Detection Timeline", fontsize=16, fontweight='bold', pad=20)
    plt.xlabel("Time (seconds)", fontsize=12)
    plt.ylabel("Brands", fontsize=12)
    plt.yticks(range(len(brand_columns)), brand_columns)
    plt.grid(True, alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "brand_timeline_overview.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # --- 2. BRAND DOMINANCE: Market share pie chart ---
    brand_totals = df[brand_columns].sum()
    brand_totals = brand_totals[brand_totals > 0]  # Only show brands with detections
    
    if not brand_totals.empty:
        plt.figure(figsize=(10, 8))
        wedges, texts, autotexts = plt.pie(brand_totals.values, labels=brand_totals.index, 
                                          autopct='%1.1f%%', startangle=90, colors=colors)
        
        # Enhance text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.title("Brand Visibility Share", fontsize=16, fontweight='bold', pad=20)
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, "brand_market_share.png"), dpi=300, bbox_inches='tight')
        plt.close()

    # --- 3. DETECTION INTENSITY HEATMAP ---
    # Create time windows (e.g., 30-second intervals)
    window_size = 30
    max_time = df["TimeSeconds"].max()
    time_windows = range(0, int(max_time) + window_size, window_size)
    
    heatmap_data = []
    window_labels = []
    
    for i in range(len(time_windows) - 1):
        start_time = time_windows[i]
        end_time = time_windows[i + 1]
        window_data = df[(df["TimeSeconds"] >= start_time) & (df["TimeSeconds"] < end_time)]
        
        if not window_data.empty:
            window_totals = window_data[brand_columns].sum()
            heatmap_data.append(window_totals.values)
            window_labels.append(f"{start_time}-{end_time}s")
    
    if heatmap_data:
        heatmap_df = pd.DataFrame(heatmap_data, columns=brand_columns, index=window_labels)
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_df.T, annot=True, fmt='.0f', cmap='YlOrRd', 
                   cbar_kws={'label': 'Detection Count'})
        plt.title("Brand Detection Intensity by Time Window", fontsize=16, fontweight='bold', pad=20)
        plt.xlabel("Time Windows", fontsize=12)
        plt.ylabel("Brands", fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, "brand_intensity_heatmap.png"), dpi=300, bbox_inches='tight')
        plt.close()

    # --- 4. DETECTION FREQUENCY ANALYSIS ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Total detections bar chart
    brand_totals_sorted = brand_totals.sort_values(ascending=True)
    bars = ax1.barh(brand_totals_sorted.index, brand_totals_sorted.values, color=colors[:len(brand_totals_sorted)])
    ax1.set_title("Total Brand Detections", fontweight='bold')
    ax1.set_xlabel("Total Detection Score")
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{width:.0f}', ha='left', va='center', fontweight='bold')
    
    # Detection consistency (frames with detections)
    detection_frames = {}
    for brand in brand_columns:
        detection_frames[brand] = (df[brand] > 0).sum()
    
    detection_frames_sorted = dict(sorted(detection_frames.items(), key=lambda x: x[1]))
    bars2 = ax2.barh(list(detection_frames_sorted.keys()), list(detection_frames_sorted.values()), 
                     color=colors[:len(detection_frames_sorted)])
    ax2.set_title("Detection Consistency (Frames with Brand Present)", fontweight='bold')
    ax2.set_xlabel("Number of Frames")
    
    # Add value labels
    for i, bar in enumerate(bars2):
        width = bar.get_width()
        ax2.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "brand_frequency_analysis.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # --- 5. PEAK DETECTION ANALYSIS ---
    plt.figure(figsize=(14, 8))
    
    for i, brand in enumerate(brand_columns):
        brand_data = df[brand]
        if brand_data.max() > 0:
            # Find peaks (local maxima)
            from scipy.signal import find_peaks
            peaks, _ = find_peaks(brand_data, height=0.5, distance=5)
            
            # Plot the brand timeline
            plt.plot(df["TimeSeconds"], brand_data, label=brand, linewidth=2, 
                    color=colors[i % len(colors)], alpha=0.8)
            
            # Mark peaks
            if len(peaks) > 0:
                plt.scatter(df["TimeSeconds"].iloc[peaks], brand_data.iloc[peaks], 
                           color=colors[i % len(colors)], s=100, marker='*', 
                           edgecolors='black', linewidth=1, zorder=5)
    
    plt.title("Brand Detection Peaks and Trends", fontsize=16, fontweight='bold', pad=20)
    plt.xlabel("Time (seconds)", fontsize=12)
    plt.ylabel("Detection Score", fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "brand_peak_analysis.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # --- 6. COMPETITIVE LANDSCAPE ---
    # Show when multiple brands appear together
    plt.figure(figsize=(14, 6))
    
    # Calculate co-occurrence
    co_occurrence_frames = []
    for idx, row in df.iterrows():
        active_brands = [brand for brand in brand_columns if row[brand] > 0]
        if len(active_brands) > 1:
            co_occurrence_frames.append({
                'time': row['TimeSeconds'], 
                'brands': ', '.join(active_brands),
                'count': len(active_brands)
            })
    
    if co_occurrence_frames:
        co_df = pd.DataFrame(co_occurrence_frames)
        
        # Plot timeline of co-occurrences
        for i, row in co_df.iterrows():
            plt.scatter(row['time'], row['count'], s=100, alpha=0.7, 
                       c=colors[row['count'] % len(colors)])
        
        plt.title("Brand Co-occurrence Timeline", fontsize=16, fontweight='bold', pad=20)
        plt.xlabel("Time (seconds)", fontsize=12)
        plt.ylabel("Number of Brands Present", fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Add annotations for high co-occurrence moments
        max_cooccur = co_df['count'].max() if not co_df.empty else 0
        if max_cooccur > 1:
            peak_moments = co_df[co_df['count'] == max_cooccur]
            for _, moment in peak_moments.iterrows():
                plt.annotate(f"{moment['brands']}", 
                           xy=(moment['time'], moment['count']),
                           xytext=(10, 10), textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                           fontsize=8)
    else:
        plt.text(0.5, 0.5, "No brand co-occurrences detected", 
                transform=plt.gca().transAxes, ha='center', va='center', 
                fontsize=14, style='italic')
        plt.title("Brand Co-occurrence Timeline", fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "brand_competitive_landscape.png"), dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ Enhanced plots saved to: {plots_dir}")
    print("📊 Generated visualizations:")
    print("  • Brand Timeline Overview - Shows when each brand appears")
    print("  • Brand Market Share - Pie chart of visibility distribution") 
    print("  • Detection Intensity Heatmap - Brand presence across time windows")
    print("  • Frequency Analysis - Total detections vs consistency")
    print("  • Peak Detection Analysis - Identifies high-visibility moments")
    print("  • Competitive Landscape - Shows brand co-occurrences")

# analysis_csv = "../#4 NUGGETS at #1 THUNDER _ FULL GAME 2 HIGHLIGHTS _ May 7, 2025/brand_analysis.csv"
# base_dir = "../#4 NUGGETS at #1 THUNDER _ FULL GAME 2 HIGHLIGHTS _ May 7, 2025"
# generate_visuals(analysis_csv=analysis_csv, base_dir=base_dir)