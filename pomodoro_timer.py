import tkinter as tk
from tkinter import filedialog
import math
from datetime import datetime, timedelta


"""A simple Tkinter Pomodoro timer with a continuous 60 minute ring.

Click the ring to choose a number of minutes. The selected portion glows
red while the remaining time is tracked in real time using the system clock.
"""

class PomodoroTimer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pomodoro Timer")
        self.end_time = None

        # layout frames
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # timer ring settings
        self.canvas_size = 200
        self.radius_margin = 20
        self.ring_width = 12
        self.ring_radius = (self.canvas_size - 2 * self.radius_margin) / 2
        self.background_ring = None
        self.progress_arc = None

        # timer widgets
        self.time_label = tk.Label(self.left_frame, font=("Helvetica", 16))
        self.time_label.pack(pady=5)

        self.canvas = tk.Canvas(
            self.left_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="white",
            highlightthickness=0,
        )
        self.canvas.pack()
        self.draw_ring()
        self.canvas.bind("<Button-1>", self.on_click)

        self.timer_label = tk.Label(self.left_frame, text="00:00", font=("Helvetica", 24))
        self.timer_label.pack(pady=5)

        # schedule area
        self.schedule_container = tk.Frame(self.right_frame)
        self.schedule_container.pack(fill=tk.BOTH, expand=True)

        self.schedule_text = tk.Text(self.schedule_container, width=20, height=30)
        self.schedule_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.schedule_scroll = tk.Scrollbar(self.schedule_container, command=self.schedule_text.yview)
        self.schedule_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.schedule_text.config(yscrollcommand=self.schedule_scroll.set)

        self.button_frame = tk.Frame(self.right_frame)
        self.button_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Button(self.button_frame, text="Import", command=self.import_schedule).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Export", command=self.export_schedule).pack(side=tk.LEFT)
        self.populate_schedule()

        self.update_clock()

    def draw_ring(self):
        box = (
            self.canvas_size / 2 - self.ring_radius,
            self.canvas_size / 2 - self.ring_radius,
            self.canvas_size / 2 + self.ring_radius,
            self.canvas_size / 2 + self.ring_radius,
        )
        self.background_ring = self.canvas.create_oval(
            *box,
            outline="lightgray",
            width=self.ring_width,
        )
        self.progress_arc = self.canvas.create_arc(
            *box,
            start=90,
            extent=0,
            style=tk.ARC,
            width=self.ring_width,
            outline="red",
        )

    def on_click(self, event):
        # Convert click coordinates to polar angle relative to the centre
        cx = cy = self.canvas_size / 2
        dx = event.x - cx
        dy = event.y - cy
        r = math.hypot(dx, dy)
        inner = self.ring_radius - self.ring_width / 2
        outer = self.ring_radius + self.ring_width / 2
        if not (inner <= r <= outer):
            return
        # Calculate a clockwise angle from the top of the ring
        angle = (math.degrees(math.atan2(dy, dx)) + 90) % 360
        minutes = int(round(angle / 6))
        minutes = max(0, min(60, minutes))
        self.set_timer(minutes)

    def set_timer(self, minutes):
        if minutes <= 0:
            self.end_time = None
            self.timer_label.config(text="00:00")
            self.highlight_minutes(0)
            return
        self.end_time = datetime.now() + timedelta(minutes=minutes)
        self.highlight_minutes(minutes)
        self.update_timer()

    def highlight_minutes(self, minutes):
        """Draw a continuous arc highlighting the selected minutes."""
        extent = -minutes * 6
        self.canvas.itemconfig(self.progress_arc, extent=extent)

    def populate_schedule(self):
        """Fill the schedule text box with 15 minute slots."""
        self.schedule_text.delete("1.0", tk.END)
        for hour in range(24):
            for quarter in range(4):
                mins = quarter * 15
                self.schedule_text.insert(tk.END, f"{hour:02d}:{mins:02d} \n")
        self.schedule_text.tag_configure("current", background="lightyellow")

    def highlight_schedule(self):
        now = datetime.now()
        total_minutes = now.hour * 60 + now.minute
        index = total_minutes // 15 + 1
        self.schedule_text.tag_remove("current", "1.0", tk.END)
        line_start = f"{index}.0"
        self.schedule_text.tag_add("current", line_start, f"{index}.end")
        self.schedule_text.see(line_start)

    def import_schedule(self):
        """Load schedule text from a file into the text widget."""
        filename = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filename:
            with open(filename, "r", encoding="utf-8") as f:
                self.schedule_text.delete("1.0", tk.END)
                self.schedule_text.insert(tk.END, f.read())

    def export_schedule(self):
        """Save the current schedule text to a file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.schedule_text.get("1.0", tk.END))

    def update_timer(self):
        if not self.end_time:
            return
        remaining = int((self.end_time - datetime.now()).total_seconds())
        if remaining < 0:
            remaining = 0
        mins, secs = divmod(remaining, 60)
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
        self.highlight_minutes((remaining + 59) // 60)
        if remaining > 0:
            self.root.after(1000, self.update_timer)

    def update_clock(self):
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.highlight_schedule()
        self.root.after(1000, self.update_clock)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    PomodoroTimer().run()
