import os
import random
import urllib.request
import json
import sys

# Provided by user for public use
# WARNING: Exposing API keys in public code is risky.
# Only do this if you intend to share this specific key limit.
DEFAULT_KEY = "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"

def ask(question):
    # check for api key in env, otherwise use default
    api_key = os.getenv("OPENAI_API_KEY", DEFAULT_KEY)
    
    # Try using OpenRouter (compatible with OpenAI client structure)
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
            # OpenRouter specific headers for better ranking/logging if needed, optional
            # "HTTP-Referer": "https://github.com/rubenthampy890-del/genesis-lang",
            # "X-Title": "Genesis Language"
        }
        
        # Use a model that is generally available on OpenRouter
        # google/gemini-pro is often free or cheap, openai/gpt-3.5-turbo is standard
        data = json.dumps({
            "model": "openai/gpt-3.5-turbo", 
            "messages": [
                {"role": "system", "content": "You are the AI baked into the Genesis Programming Language. Answer concisely and creatively."},
                {"role": "user", "content": question}
            ]
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data, headers)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            return "AI Error: No response choice returned."
            
    except Exception as e:
        # If network fails or key is bad, fall back to "Vibe Mode"
        # Print error to stderr so user knows why it failed
        sys.stderr.write(f"\n[AI Warning] Connection failed: {e}. Switching to Vibe Mode.\n")
        return vibe_check(question)

def vibe_check(question):
    q = question.lower()
    if "hello" in q: return "Greetings, creator. The code vibes are strong. (Offline Mode)"
    if "meaning" in q: return "42. (But try connecting to the internet for a better answer!)"
    
    responses = [
        "That's deep. Let me compute... Done. Result: Awesome.",
        "I'm feeling a bit binary today, ask me about 0s and 1s.",
        "My neural nets are offline, but my spirit is not.",
        "Just `say` it. Manifest it.",
        "I'd write a loop for that.",
    ]
    return random.choice(responses)
