import os
import re

SENSITIVE_WORDS_FILE = os.path.join(os.path.dirname(__file__), 'sensitive_words.txt')

def load_sensitive_words():
    if not os.path.exists(SENSITIVE_WORDS_FILE):
        return []
    with open(SENSITIVE_WORDS_FILE, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def check_sensitive_words(text):
    words = load_sensitive_words()
    for word in words:
        if re.search(re.escape(word), text, re.IGNORECASE):
            return word
    return None 