import numpy as np
from scipy.io import wavfile

fs = 44100
duration = 0.05
window_size = int(fs * duration)

low_freqs = [600, 700, 800, 900, 1000]
high_freqs = [1200, 1300, 1400, 1500, 1600, 1700]

characters = [
    "A", "B", "C", "Ç", "D", "E", "F", "G", "Ğ", "H", "I", "İ",
    "J", "K", "L", "M", "N", "O", "Ö", "P", "R", "S", "Ş", "T",
    "U", "Ü", "V", "Y", "Z", " "
]

reverse_map = {}
index = 0
for lf in low_freqs:
    for hf in high_freqs:
        if index < len(characters):
            reverse_map[(lf, hf)] = characters[index]
            index += 1

def goertzel(samples, freq, fs):
    N = len(samples)
    k = round(N * freq / fs)
    omega = (2 * np.pi / N) * k
    coeff = 2 * np.cos(omega)
    s_prev, s_prev2 = 0, 0

    for sample in samples:
        s = sample + coeff * s_prev - s_prev2
        s_prev2, s_prev = s_prev, s

    return s_prev2 ** 2 + s_prev ** 2 - coeff * s_prev * s_prev2

fs_read, data = wavfile.read("encoded_output.wav")

if len(data.shape) > 1:
    data = data[:, 0]

decoded_text = ""
last_char = None

for i in range(0, len(data), window_size):
    segment = data[i:i + window_size]
    if len(segment) < window_size:
        continue

    segment = segment * np.hanning(len(segment))

    max_p = -1
    detected = None

    for lf in low_freqs:
        for hf in high_freqs:
            p = goertzel(segment, lf, fs) + goertzel(segment, hf, fs)
            if p > max_p:
                max_p = p
                detected = (lf, hf)

    if detected in reverse_map:
        char = reverse_map[detected]
        if char != last_char:
            decoded_text += char
            last_char = char

print("Çözülen Metin:", decoded_text)