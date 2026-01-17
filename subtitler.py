import os
import subprocess

def format_timestamp(seconds):
    """Converts seconds (12.5) to SRT format (00:00:12,500)"""
    millis = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    minutes = seconds // 60
    hours = minutes // 60
    
    minutes %= 60
    seconds %= 60
    
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

def generate_srt(segments, output_path):
    """Saves the current text segments to a .srt file."""
    print(f"--- Generating Subtitles: {output_path} ---")
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments):
            start = format_timestamp(seg['start'])
            end = format_timestamp(seg['end'])
            text = seg['text'].replace("[BEEP]", "*BEEP*") # Clean up for display
            
            f.write(f"{i+1}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")
    return output_path

def burn_subtitles(video_path, srt_path, output_path):
    """Uses FFmpeg to burn the subtitles permanently into the video."""
    print(f"--- Burning Subtitles into Video ---")
    # Note: FFmpeg requires forward slashes or escaped backslashes for the subtitles filter
    srt_clean = srt_path.replace("\\", "/").replace(":", "\\:")
    
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", video_path,
        "-vf", f"subtitles='{srt_clean}':force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1,Shadow=0'",
        "-c:a", "copy",
        output_path
    ]
    subprocess.run(cmd)