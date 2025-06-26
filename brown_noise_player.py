import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk
import threading

class BrownNoisePlayer:
    def __init__(self, sample_rate=44100, block_size=1024, device=None):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.device = device
        self.gain = 0.01
        self.running = False
        self.prev_sample = 0
        self.wave_type = 'Brown'
        self.phase = 0
        self._stop_event = threading.Event()
        self._start_stream()

    def _create_stream(self):
        return sd.OutputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            channels=1,
            dtype='float32',
            device=self.device,
            callback=self.audio_callback
        )

    def _start_stream(self):
        self.stream = self._create_stream()
        self._thread = threading.Thread(target=self._run_stream, daemon=True)
        self._thread.start()

    def _stop_stream(self):
        self._stop_event.set()
        if hasattr(self, '_thread') and self._thread.is_alive():
            self._thread.join()
        if hasattr(self, 'stream'):
            self.stream.close()
        self._stop_event.clear()

    def _run_stream(self):
        with self.stream:
            while not self._stop_event.is_set():
                sd.sleep(100)

    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(status)
        if self.running:
            if self.wave_type == 'Brown':
                white = np.random.normal(0, 1, frames)
                data = np.empty(frames)
                for i, w in enumerate(white):
                    self.prev_sample = (self.prev_sample + 0.02 * w) / 1.02
                    data[i] = self.prev_sample * 3.5
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

    def stop(self):
        self.running = False

    def close(self):
        self._stop_stream()

    def set_wave_type(self, wave_type):
        self.wave_type = wave_type
        self.prev_sample = 0
        self.phase = 0

    def set_device(self, device):
        """Switch to a different output device."""
        self._stop_stream()
        self.device = device
        self._start_stream()

class BrownNoiseUI:
    def __init__(self):
        self.player = BrownNoisePlayer()
        self.root = tk.Tk()
        self.root.title("Noise Generator")
        self.create_widgets()

    def _get_output_devices(self):
        devices = []
        for idx, dev in enumerate(sd.query_devices()):
            if dev['max_output_channels'] > 0:
                devices.append((idx, dev['name']))
        return devices

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        devices = self._get_output_devices()
        self.device_map = {name: idx for idx, name in devices}
        self.device_var = tk.StringVar()
        default_index = sd.default.device[1]
        default_name = next((name for name, idx in self.device_map.items()
                             if idx == default_index), None)
        if default_name is None and devices:
            default_name = devices[0][1]
        self.device_var.set(default_name)
        device_menu = ttk.OptionMenu(frame, self.device_var, default_name,
                                     *[name for _, name in devices],
                                     command=self.update_device)
        device_menu.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="Output Device").pack()

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

    def update_device(self, value=None):
        name = self.device_var.get()
        device = self.device_map.get(name)
        if device is not None:
            self.player.set_device(device)

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
