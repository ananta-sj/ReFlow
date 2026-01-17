from transformers import pipeline
from PIL import Image
import cv2
import os
import subprocess
import torch

# --- GLOBAL LOADER ---
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        print("   > Loading Vision Transformer (HuggingFace)...")
        device = 0 if torch.cuda.is_available() else -1
        try:
            _classifier = pipeline("image-classification", model="Falconsai/nsfw_image_detection", device=device)
        except Exception as e:
            print(f"   > Error loading model: {e}")
            return None
    return _classifier

def scan_video_for_content(video_path):
    print(f"--- Scanning with Continuity Logic: {video_path} ---")
    classifier = get_classifier()
    if not classifier: return []

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0: fps = 24.0
    
    # SCAN FASTER: Check every 6th frame (~0.25 seconds)
    frame_interval = 6 
    timestamps = []
    
    count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        if count % frame_interval == 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            try:
                results = classifier(pil_image)
                nsfw_score = 0
                for r in results:
                    if r['label'] == 'nsfw':
                        nsfw_score = r['score']
                        break
                
                # LOWER THRESHOLD: 0.60 (Catch the "Flickering" frames)
                if nsfw_score > 0.60:
                    time_sec = count / fps
                    timestamps.append(time_sec)
                    # print(f"   > [UNSAFE] Confidence: {nsfw_score:.2f} at {time_sec:.2f}s")
                    
            except Exception as e:
                pass

        count += 1
        
    cap.release()
    return merge_timestamps_with_gap_filling(timestamps)

def merge_timestamps_with_gap_filling(timestamps):
    if not timestamps: return []
    
    # 1. SORT
    timestamps.sort()
    
    # 2. GAP FILLING ALGORITHM
    # If two detections are less than 4 seconds apart, merge them.
    # This covers the "25s to 45s" scenario perfectly.
    
    GAP_LIMIT = 4.0  # Seconds
    
    merged_intervals = []
    if not timestamps: return []

    # Start the first block
    current_start = max(0, timestamps[0] - 1.0)
    current_end = timestamps[0] + 1.0
    
    for i in range(1, len(timestamps)):
        t = timestamps[i]
        
        # Calculate distance from previous detection's end (without buffer)
        prev_raw_t = timestamps[i-1]
        
        if (t - prev_raw_t) < GAP_LIMIT:
            # EXTEND current block
            # If we saw nude at 25s, and now at 28s, extend the blur to cover 28s
            current_end = t + 1.0
        else:
            # CLOSE current block and start new one
            merged_intervals.append([current_start, current_end])
            current_start = max(0, t - 1.0)
            current_end = t + 1.0
            
    # Append the last block
    merged_intervals.append([current_start, current_end])
        
    print(f"   > Final Plan: Blurring {len(merged_intervals)} continuous scenes.")
    return merged_intervals

def apply_blur_to_video(input_path, output_path, intervals):
    print(f"--- Applying HEAVY Blur Filters ---")
    if not intervals: return

    filters = []
    for start, end in intervals:
        # CHANGED: Increased from 20:1 to 50:5
        # This makes it impossible to see shapes or movement details.
        filters.append(f"boxblur=50:5:enable='between(t,{start:.2f},{end:.2f})'")
    
    if len(filters) > 50:
        print("   > Too many zones. Applying continuous heavy blur.")
        filters = ["boxblur=50:5"]

    filter_str = ",".join(filters)
    cmd = (
        f'ffmpeg -y -v error -i "{input_path}" '
        f'-vf "{filter_str}" '
        f'-c:a copy -c:v libx264 '
        f'"{output_path}"'
    )
    subprocess.run(cmd, shell=True)