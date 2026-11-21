import math
import wave
import struct
import random

sample_rate = 22050
duration = 60
output = "Assets/Backgrounds/fantasy_music.wav"

random.seed(10)

notes = [130.81, 164.81, 196.00, 261.63, 329.63, 392.00]

with wave.open(output, "w") as audio:
    audio.setnchannels(2)
    audio.setsampwidth(2)
    audio.setframerate(sample_rate)

    for i in range(sample_rate * duration):
        t = i / sample_rate

        pad = sum(
            math.sin(2 * math.pi * f * t) * 0.045
            for f in notes[:4]
        )

        melody = 0
        beat = int(t / 2) % len(notes)

        if int(t * 2) % 4 == 0:
            melody = math.sin(
                2 * math.pi * notes[beat] * t
            ) * 0.10

        bell = (
            math.sin(2 * math.pi * 523.25 * t) *
            max(0, math.sin(t * 0.8)) * 0.025
        )

        atmosphere = math.sin(2 * math.pi * 55 * t) * 0.035

        fade = min(1, t / 3, (duration - t) / 3)

        left = (pad + melody + bell + atmosphere) * fade
        right = (pad + melody * 0.8 + bell + atmosphere) * fade

        left = max(-1, min(1, left))
        right = max(-1, min(1, right))

        audio.writeframesraw(
            struct.pack("<hh", int(left * 32767), int(right * 32767))
        )

print("Fantasy Adventure Music Created!")
print(output)
