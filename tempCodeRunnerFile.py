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