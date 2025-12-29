import os
from gtts import gTTS

def text_to_speech(text, filename="output.mp3"):
    
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None