from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re
import gc

# --- CONFIG ---
MODEL_CHECKPOINT = "facebook/nllb-200-distilled-600M"
device = "cuda" if torch.cuda.is_available() else "cpu"

# --- Hinglish Protection List ---
DEFAULT_TECH_TERMS = [
    "Settings", "Update", "Install", "Download", "Upload", "Click", "Tap",
    "Login", "Password", "Account", "Profile", "Edit", "Save", "Delete",
    "Search", "Connect", "Play", "Pause", "Open", "Close", "Select",
    "Phone", "Mobile", "Computer", "Device", "Camera", "Mic", "Battery",
    "Screen", "Keyboard", "Memory", "Storage", "Processor",
    "Internet", "Wi-Fi", "Bluetooth", "Network", "Data", "Online", "App",
    "Video", "Audio", "Photo", "File", "Folder", "timeline", "Render"
]

class NLLBTranslator:
    def __init__(self):
        print(f"--- Loading NLLB Model on {device.upper()} ---")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_CHECKPOINT)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_CHECKPOINT).to(device)
        # NLLB requires specific language codes:
        # Hindi = hin_Deva, English = eng_Latn
        self.lang_code_map = {
            'hindi': 'hin_Deva',
            'english': 'eng_Latn'
        }

    def translate(self, text, target_lang='hindi'):
        flores_code = self.lang_code_map.get(target_lang, 'hin_Deva')
        
        inputs = self.tokenizer(text, return_tensors="pt").to(device)
        
        # --- FIX: Updated command for newer Transformers versions ---
        # Old: self.tokenizer.lang_code_to_id[flores_code] (Deprecated)
        # New: self.tokenizer.convert_tokens_to_ids(flores_code)
        
        forced_bos_id = self.tokenizer.convert_tokens_to_ids(flores_code)
        
        translated_tokens = self.model.generate(
            **inputs, 
            forced_bos_token_id=forced_bos_id, 
            max_length=128
        )
        return self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]

    def unload(self):
        """Free up VRAM for the next model (XTTS)"""
        del self.model
        del self.tokenizer
        gc.collect()
        torch.cuda.empty_cache()

# --- Helper Functions ---
def mask_text(text, terms):
    mask_map = {}
    masked_text = text
    sorted_terms = sorted(terms, key=len, reverse=True)
    
    for i, term in enumerate(sorted_terms):
        pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
        if pattern.search(masked_text):
            placeholder = f"__ID_{i}__"
            masked_text = pattern.sub(placeholder, masked_text)
            mask_map[placeholder] = term
    return masked_text, mask_map

def unmask_text(text, mask_map):
    for placeholder, term in mask_map.items():
        text = text.replace(placeholder, term)
        text = text.replace(placeholder.replace("_", " "), term)
    return text

def translate_segments(segments, target_mode='hindi', tech_terms=None):
    if tech_terms is None: tech_terms = DEFAULT_TECH_TERMS
    
    # Init Model
    translator = NLLBTranslator()
    
    print(f"--- NLLB Translating {len(segments)} lines. Mode: {target_mode.upper()} ---")
    
    translated_segments = []
    for seg in segments:
        try:
            new_seg = seg.copy()
            original_text = seg['text']
            
            if target_mode == 'hinglish':
                masked, mask_map = mask_text(original_text, tech_terms)
                trans_text = translator.translate(masked, target_lang='hindi')
                final_text = unmask_text(trans_text, mask_map)
                new_seg['text'] = final_text
            else:
                target = 'english' if target_mode == 'english' else 'hindi'
                new_seg['text'] = translator.translate(original_text, target_lang=target)
                
            translated_segments.append(new_seg)
        except Exception as e:
            print(f"NLLB Error: {e}")
            translated_segments.append(seg)
    
    # Unload to save GPU for Dubbing
    translator.unload()
    return translated_segments