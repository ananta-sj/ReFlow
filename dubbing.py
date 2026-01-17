import torch
import os
import subprocess
import shutil
import gc
from pydub import AudioSegment
from pydub.silence import split_on_silence

# --- PYTORCH 2.6 PATCH ---
try:
    _original_load = torch.load
    def _safe_load(*args, **kwargs):
        if 'weights_only' not in kwargs: kwargs['weights_only'] = False
        return _original_load(*args, **kwargs)
    torch.load = _safe_load
except Exception: pass
# -------------------------

def get_duration(filename):
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
               "-of", "default=noprint_wrappers=1:nokey=1", filename]
        return float(subprocess.check_output(cmd).strip())
    except: return 0.0

def smart_squeeze_audio(file_path, target_duration):
    try:
        audio = AudioSegment.from_wav(file_path)
    except: return 1.0, False 

    current_dur = len(audio) / 1000.0
    
    # 1. Silence Removal
    if current_dur > target_duration:
        chunks = split_on_silence(audio, min_silence_len=300, silence_thresh=-40)
        if chunks:
            no_silence = chunks[0]
            for c in chunks[1:]: no_silence += c
            no_silence.export(file_path, format="wav")
            current_dur = len(no_silence) / 1000.0

    # 2. Gentle Speed Calculation
    if current_dur > target_duration:
        speed = current_dur / target_duration
        
        # LOWER CAP: 1.3x max (was 1.5x)
        # Anything higher than 1.3 sounds broken.
        final_speed = min(speed, 1.3)
        
        # If 1.3x isn't enough, we trim.
        return final_speed, True 
        
    return 1.0, False

# ... inside generate_dub_audio function ...
# When building the ffmpeg command, add the bitrate:

def extract_reference_audio(video_path, start, dur, out_path):
    subprocess.run(f'ffmpeg -y -v error -ss {start} -i "{video_path}" -t {dur} -vn -acodec pcm_s16le -ar 24000 "{out_path}"', shell=True)

def generate_dub_audio(segments, output_file, video_source_path, tts_model, mode="hindi"):
    print(f"--- XTTS ENGINE ({mode.upper()}) ---")
    tts = tts_model
    
    if os.path.exists("temp_chunks"): shutil.rmtree("temp_chunks")
    os.makedirs("temp_chunks")
    
    # --- PRE-PROCESS: Fix Overlapping Timestamps ---
    # Ensure Segment A ends before Segment B starts
    for i in range(len(segments) - 1):
        if segments[i]['end'] > segments[i+1]['start']:
            segments[i]['end'] = segments[i+1]['start']
    # -----------------------------------------------

    final_concat_list = "temp_chunks/final_list.txt"
    
    for i, seg in enumerate(segments):
        text = seg['text']
        # Enforce Minimum Duration (0.5s) to prevent FFmpeg errors
        start = seg['start']
        end = max(seg['end'], start + 0.5) 
        slot_duration = end - start
        
        ref_audio = f"temp_chunks/ref_{i}.wav"
        extract_reference_audio(video_source_path, start, slot_duration, ref_audio)
        
        raw_file = f"temp_chunks/raw_{i}.wav"
        try:
            target_lang = "hi" if mode in ["hindi", "hinglish"] else "en"
            tts.tts_to_file(text=text, speaker_wav=ref_audio, language=target_lang, file_path=raw_file)
        except:
            # Generate silence if TTS fails
            subprocess.run(f'ffmpeg -y -v error -f lavfi -i anullsrc=r=24000:cl=mono -t {slot_duration} "{raw_file}"', shell=True)

        # STRICT SYNC
        final_file = f"temp_chunks/final_{i}.wav"
        
        # Calculate Speed & Trim
        speed, needs_trim = smart_squeeze_audio(raw_file, slot_duration)
        
        cmd = f'ffmpeg -y -v error -i "{raw_file}" -filter:a "atempo={speed}" -ar 24000 '
        if needs_trim:
            # HARD CUT at exact slot duration
            cmd += f'-t {slot_duration} '
        cmd += f'"{final_file}"'
        
        subprocess.run(cmd, shell=True)

    # Master Merge
    last_end = 0.0
    with open(final_concat_list, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments):
            # Calculate Gap
            gap = seg['start'] - last_end
            
            # If gap is positive, add silence
            if gap > 0.01:
                silence_f = f"temp_chunks/sil_gap_{i}.wav"
                subprocess.run(f'ffmpeg -y -v error -f lavfi -i anullsrc=r=24000:cl=mono -t {gap} "{silence_f}"', shell=True)
                f.write(f"file 'sil_gap_{i}.wav'\n")
            
            # If gap is negative (Overlap), we effectively skip the overlap by not adding silence
            # The previous logic (clamping) prevents this, but this is a safety net.
            
            f.write(f"file 'final_{i}.wav'\n")
            last_end = seg['end']

    subprocess.run(f'ffmpeg -y -v error -f concat -safe 0 -i "{final_concat_list}" -ar 44100 -ac 2 "{output_file}"', shell=True)
    if os.path.exists("temp_chunks"): shutil.rmtree("temp_chunks")
    return output_file