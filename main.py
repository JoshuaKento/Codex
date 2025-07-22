"""PyQt6 Pomodoro timer application."""
from __future__ import annotations

try:
    from PyQt6.QtCore import QFile
    from PyQt6.QtGui import QFontDatabase
    from PyQt6.QtWidgets import QApplication, QFrame, QHBoxLayout, QMainWindow, QVBoxLayout
except ModuleNotFoundError as exc:  # pragma: no cover - environment specific
    raise SystemExit(
        "PyQt6 is required to run this application. Install dependencies with './setup.sh'."
    ) from exc

import resources.resources  # noqa: F401

from schedule import ScheduleView
from timer import PomodoroTimer


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Pomodoro")
        self.resize(800, 480)

        central = QFrame(self)
        central.setObjectName("panel")
        self.setCentralWidget(central)

        outer = QVBoxLayout(central)
        outer.setContentsMargins(10, 10, 10, 10)

        main = QHBoxLayout()
        self.timer_widget = PomodoroTimer()
        self.schedule_view = ScheduleView()
        main.addWidget(self.timer_widget, 1)
        main.addWidget(self.schedule_view)
        outer.addLayout(main)

        self.load_style()

    def load_style(self) -> None:
        file = QFile("theme.qss")
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            self.setStyleSheet(str(file.readAll(), "utf-8"))
            file.close()


def main() -> None:
    app = QApplication([])
    QFontDatabase.addApplicationFont(":/fonts/Rubik-SemiBold.ttf")
    win = MainWindow()
    win.show()
    app.exec()


if __name__ == "__main__":
    main()

