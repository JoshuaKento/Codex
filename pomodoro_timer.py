import tkinter as tk
import math
from datetime import datetime

class PomodoroTimer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pomodoro Timer")
        self.timer_seconds = 0
        self.canvas_size = 200
        self.radius_margin = 20
        self.segments = []

        self.time_label = tk.Label(self.root, font=("Helvetica", 16))
        self.time_label.pack(pady=5)

        self.canvas = tk.Canvas(self.root, width=self.canvas_size,
                                height=self.canvas_size, bg="white", highlightthickness=0)
        self.canvas.pack()
        self.draw_segments()
        self.canvas.bind("<Button-1>", self.on_click)

        self.timer_label = tk.Label(self.root, text="00:00", font=("Helvetica", 24))
        self.timer_label.pack(pady=5)

        self.update_clock()

    def draw_segments(self):
        for i in range(60):
            start = i * 6 - 90
            arc = self.canvas.create_arc(self.radius_margin, self.radius_margin,
                                         self.canvas_size - self.radius_margin,
                                         self.canvas_size - self.radius_margin,
                                         start=start, extent=6, style=tk.ARC,
                                         width=8, outline="lightgray")
            self.segments.append(arc)

    def on_click(self, event):
        cx = cy = self.canvas_size / 2
        dx = event.x - cx
        dy = event.y - cy
        r = math.hypot(dx, dy)
        if r < self.canvas_size / 2 - self.radius_margin/2 or r > self.canvas_size / 2 + self.radius_margin/2:
            return
        angle = (math.degrees(math.atan2(-dy, dx)) + 360) % 360
        minutes = int(angle // 6)
        self.set_timer(minutes)

    def set_timer(self, minutes):
        self.timer_seconds = minutes * 60
        self.update_timer()

    def highlight_segments(self, minutes):
        for i, arc in enumerate(self.segments):
            color = "dodgerblue" if i < minutes else "lightgray"
            self.canvas.itemconfig(arc, outline=color)

    def update_timer(self):
        mins = self.timer_seconds // 60
        secs = self.timer_seconds % 60
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
        self.highlight_segments((self.timer_seconds + 59) // 60)
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.root.after(1000, self.update_timer)

    def update_clock(self):
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_clock)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    PomodoroTimer().run()
