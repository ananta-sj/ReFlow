from better_profanity import profanity

# Custom bad words (You can add Hindi bad words here later!)
CUSTOM_BAD_WORDS = ['badword1', 'badword2'] 
profanity.add_censor_words(CUSTOM_BAD_WORDS)

def check_profanity(text):
    """Returns True if text contains bad words."""
    return profanity.contains_profanity(text)

def censor_text(text):
    """Replaces bad words with ****"""
    return profanity.censor(text)

def get_bad_words_in_text(text):
    """Returns a list of bad words found in the text (for highlighting)."""
    # This is a bit of a hack since better_profanity doesn't give a list directly
    words = text.split()
    found = []
    for word in words:
        if profanity.contains_profanity(word):
            found.append(word)
    return found