import numpy as np
from scipy.io.wavfile import write

fs = 44100
duration = 0.05  # 50 ms

low_freqs = [600, 700, 800, 900, 1000]
high_freqs = [1200, 1300, 1400, 1500, 1600, 1700]

characters = [
    "A", "B", "C", "Ç", "D", "E", "F", "G", "Ğ", "H", "I", "İ",
    "J", "K", "L", "M", "N", "O", "Ö", "P", "R", "S", "Ş", "T",
    "U", "Ü", "V", "Y", "Z", " "
]

char_map = {}
index = 0
for lf in low_freqs:
    for hf in high_freqs:
        if index < len(characters):
            char_map[characters[index]] = (lf, hf)
            index += 1

def generate_tone(f1, f2, duration, fs):
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    tone = np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t)
    return tone * 0.5  # ses patlamasını önler

def text_to_audio(text, fs, duration):
    audio = np.array([], dtype=np.float32)
    for char in text:
        char = char.upper()
        if char in char_map:
            f1, f2 = char_map[char]
            tone = generate_tone(f1, f2, duration, fs)
            audio = np.concatenate((audio, tone))
    return audio

input_text = input("Metin giriniz: ")
audio_data = text_to_audio(input_text, fs, duration)

write("encoded_output.wav", fs, audio_data.astype(np.float32))
print("Ses dosyası oluşturuldu.")