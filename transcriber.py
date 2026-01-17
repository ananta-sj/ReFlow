import whisper
import torch
import warnings

# Suppress annoying warnings
warnings.filterwarnings("ignore")

def load_model():
    print("--- Loading Whisper Model (Base) ---")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Note: If you have 8GB VRAM, "small" or "medium" is much smarter than "base"
    model = whisper.load_model("base", device=device)
    return model

def transcribe_video(model, video_path, keywords=None):
    """
    Transcribes video with 'Priming' to fix specific jargon errors.
    keywords: A string of comma-separated words (e.g., "Numberphile, Python, RAM")
    """
    print(f"--- Transcribing: {video_path} ---")
    
    # 1. Build the Prompt (The Priming)
    # We combine a standard intro with user keywords
    initial_prompt = "This is a technical video about technology, coding, and tutorials."
    if keywords:
        initial_prompt += f" It includes terms like: {keywords}."

    print(f"   > Context Prompt: {initial_prompt}")

    # 2. Run Inference with Context
    result = model.transcribe(
        video_path,
        fp16=False,
        language='en',
        initial_prompt=initial_prompt, # <--- THIS IS THE MAGIC FIX
        temperature=0.2 # Low temp = More factual, less creative guessing
    )
    
    # 3. Format Output
    segments = []
    for seg in result['segments']:
        segments.append({
            'start': seg['start'],
            'end': seg['end'],
            'text': seg['text'].strip(),
            'original': seg['text'].strip(),
            'voice_label': 'Male' # Default
        })
        
    return segments