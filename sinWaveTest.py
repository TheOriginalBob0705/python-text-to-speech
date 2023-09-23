import numpy as np
import sounddevice as sd

duration = 4
sample_rate = 44100
frequency = 440

time_array = np.linspace(0, duration, int(sample_rate * duration), endpoint = False)
sine_wave = 0.5 * np.sin(2 * np.pi * frequency * time_array)

sd.play(sine_wave, sample_rate)
sd.wait()
