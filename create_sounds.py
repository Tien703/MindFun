import os
import wave
import struct
import math

def generate_beep(filepath, frequency=440.0, duration=0.2, volume=0.5):
    sample_rate = 44100.0
    num_samples = int(duration * sample_rate)
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            # Fade out
            fade = 1.0 - (i / num_samples)
            value = int(volume * fade * 32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'sounds')
checklist_dir = os.path.join(base_dir, 'checklist_sounds')
notif_dir = os.path.join(base_dir, 'notification_sounds')

os.makedirs(checklist_dir, exist_ok=True)
os.makedirs(notif_dir, exist_ok=True)

# Generate 5 checklist sounds
freqs = [600, 700, 800, 900, 1000]
for i, f in enumerate(freqs):
    generate_beep(os.path.join(checklist_dir, f'check_{i+1}.wav'), frequency=f, duration=0.15)

# Generate 5 notification sounds
freqs_notif = [440, 523.25, 659.25, 783.99, 880]
for i, f in enumerate(freqs_notif):
    generate_beep(os.path.join(notif_dir, f'notif_{i+1}.wav'), frequency=f, duration=0.4)

print("Sounds generated successfully.")
