import numpy as np
import sounddevice as sd
import tkinter as tk
from scipy.signal import get_window

# ==========================
# PARAMETRELER
# ==========================

fs = 44100
duration = 0.04
samples_per_char = int(fs * duration)

amplitude_threshold = 0.01     # Mikrofon genlik eşiği
power_threshold = 800          # Frekans güç eşiği (gürültü filtresi)

alphabet = list("ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ ")
alphabet_size = len(alphabet)

low_freqs = np.linspace(400, 1000, 6)
high_freqs = np.linspace(1200, 2000, 5)

freq_map = {}
index = 0
for lf in low_freqs:
    for hf in high_freqs:
        if index < alphabet_size:
            freq_map[alphabet[index]] = (lf, hf)
            index += 1

# ==========================
# GOERTZEL
# ==========================

def goertzel(samples, freq):
    N = len(samples)
    k = int(0.5 + ((N * freq) / fs))
    w = (2 * np.pi / N) * k
    cosine = np.cos(w)
    coeff = 2 * cosine
    q0 = q1 = q2 = 0

    for sample in samples:
        q0 = coeff * q1 - q2 + sample
        q2 = q1
        q1 = q0

    power = q1**2 + q2**2 - coeff * q1 * q2
    return power

# ==========================
# TEK HARF SES
# ==========================

def play_character(char):
    char = char.upper()
    if char in freq_map:
        f1, f2 = freq_map[char]
        t = np.linspace(0, duration, samples_per_char, endpoint=False)
        tone = np.sin(2*np.pi*f1*t) + np.sin(2*np.pi*f2*t)
        sd.play(tone, fs)

# ==========================
# METNİ ÇAL (TÜMÜ)
# ==========================

def play_full_text():
    text = entry_text.get().upper()
    signal = np.array([])

    for char in text:
        if char in freq_map:
            f1, f2 = freq_map[char]
            t = np.linspace(0, duration, samples_per_char, endpoint=False)
            tone = np.sin(2*np.pi*f1*t) + np.sin(2*np.pi*f2*t)
            silence = np.zeros(int(fs * 0.01))  # 10 ms sessizlik
            signal = np.concatenate((signal, tone, silence))

    if len(signal) > 0:
        sd.play(signal, fs)

# ==========================
# KLAVYE ANLIK SES
# ==========================

def on_keypress(event):
    char = event.char
    if char and char.upper() in freq_map:
        play_character(char)

# ==========================
# GERÇEK ZAMANLI ÇÖZÜMLEME
# ==========================

decoded_text = ""
last_char = None
stream = None

def audio_callback(indata, frames, time, status):
    global decoded_text, last_char

    samples = indata[:, 0]

    # Genlik filtresi
    if np.max(np.abs(samples)) < amplitude_threshold:
        return

    windowed = samples * get_window("hamming", len(samples))

    best_char = None
    max_power = 0

    for char, (f1, f2) in freq_map.items():
        power1 = goertzel(windowed, f1)
        power2 = goertzel(windowed, f2)

        # İki frekans da güçlü olmalı
        if power1 < power_threshold or power2 < power_threshold:
            continue

        total_power = power1 + power2

        if total_power > max_power:
            max_power = total_power
            best_char = char
    min_detect_power = 300  # min eşik

    if max_power < min_detect_power:
        return
    if best_char and best_char != last_char:
        decoded_text += best_char
        result_label.config(text="Çözülen: " + decoded_text)
        last_char = best_char

def start_listening():
    global decoded_text, last_char, stream
    decoded_text = ""
    last_char = None
    result_label.config(text="Dinleniyor...")

    stream = sd.InputStream(callback=audio_callback,
                            channels=1,
                            samplerate=fs,
                            blocksize=samples_per_char)
    stream.start()

def stop_listening():
    global stream
    if stream:
        stream.stop()
        stream.close()
        result_label.config(text="Dinleme durduruldu.")

# ==========================
# GUI
# ==========================

root = tk.Tk()
root.title("DTMF Metin ↔ Gerçek Zamanlı Sistem")
root.geometry("650x450")
root.configure(bg="#1e1e1e")

title = tk.Label(root,
                 text="DTMF Metin - Ses Dönüşüm Sistemi (44.1 kHz)",
                 font=("Arial", 15, "bold"),
                 bg="#1e1e1e",
                 fg="white")
title.pack(pady=10)

entry_text = tk.Entry(root, width=55, font=("Arial", 14))
entry_text.pack(pady=10)

entry_text.bind("<KeyPress>", on_keypress)

play_button = tk.Button(root,
                        text="Metni Çal",
                        command=play_full_text,
                        bg="#4CAF50",
                        fg="white",
                        font=("Arial", 12))
play_button.pack(pady=5)

listen_button = tk.Button(root,
                          text="Mikrofondan Dinle",
                          command=start_listening,
                          bg="#2196F3",
                          fg="white",
                          font=("Arial", 12))
listen_button.pack(pady=5)

stop_button = tk.Button(root,
                        text="Durdur",
                        command=stop_listening,
                        bg="#f44336",
                        fg="white",
                        font=("Arial", 12))
stop_button.pack(pady=5)

result_label = tk.Label(root,
                        text="Çözülen: ",
                        font=("Arial", 14),
                        bg="#1e1e1e",
                        fg="white")
result_label.pack(pady=20)

root.mainloop()