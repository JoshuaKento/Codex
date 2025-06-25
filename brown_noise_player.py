import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk

class BrownNoisePlayer:
    def __init__(self, sample_rate=44100, block_size=1024):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            channels=1,
            dtype='float32',
            callback=self.audio_callback
        )
        self.gain = 0.01
        self.running = False
        self.prev_sample = 0
        self.wave_type = 'Brown'
        self.phase = 0

    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(status)
        if self.running:
            if self.wave_type == 'Brown':
                white = np.random.normal(0, 0.1, frames)
                data = np.cumsum(white) + self.prev_sample
                self.prev_sample = data[-1]
            elif self.wave_type == 'White':
                data = np.random.normal(0, 0.1, frames)
            else:  # Sine
                t = (np.arange(frames) + self.phase) / self.sample_rate
                freq = 440
                data = np.sin(2 * np.pi * freq * t)
                self.phase += frames
            data = np.clip(data * self.gain, -1, 1)
            outdata[:, 0] = data.astype(np.float32)
        else:
            outdata.fill(0)

    def start(self):
        self.running = True
        if not self.stream.active:
            self.stream.start()

    def stop(self):
        self.running = False

    def close(self):
        self.stream.stop()
        self.stream.close()

    def set_wave_type(self, wave_type):
        self.wave_type = wave_type
        self.prev_sample = 0
        self.phase = 0

class BrownNoiseUI:
    def __init__(self):
        self.player = BrownNoisePlayer()
        self.root = tk.Tk()
        self.root.title("Noise Generator")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        self.volume_var = tk.DoubleVar(value=0.01)
        volume_scale = ttk.Scale(frame, from_=0, to=0.02, orient='horizontal',
                                 variable=self.volume_var, command=self.update_volume)
        volume_scale.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="Volume").pack()

        self.wave_var = tk.StringVar(value='Brown')
        wave_menu = ttk.OptionMenu(frame, self.wave_var, 'Brown', 'Brown', 'White', 'Sine', command=self.update_wave)
        wave_menu.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="Wave Type").pack()

        self.start_button = ttk.Button(frame, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(frame, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, padx=5)

    def update_volume(self, event=None):
        self.player.gain = self.volume_var.get()

    def update_wave(self, value=None):
        self.player.set_wave_type(self.wave_var.get())

    def start(self):
        self.player.start()

    def stop(self):
        self.player.stop()

    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.player.close()

if __name__ == "__main__":
    BrownNoiseUI().run()
