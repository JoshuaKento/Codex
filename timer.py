from __future__ import annotations

from PyQt6.QtCore import (
    QPoint,
    QPointF,
    QEasingCurve,
    QPropertyAnimation,
    QTimer,
    Qt,
    pyqtProperty,
    QSize,
    QUrl,
)
from PyQt6.QtGui import (
    QColor,
    QConicalGradient,
    QFont,
    QFontDatabase,
    QPainter,
    QPen,
    QIcon,
)
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
)

try:
    import qtawesome as qta
except ModuleNotFoundError:  # pragma: no cover - optional
    qta = None

from theme import ACCENT_START, ACCENT_END, BREAK_COLOR, TEXT_PRIMARY


class RingWidget(QWidget):
    """Circular progress ring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._value = 1.0
        self._ring_width = 16
        self._anim = QPropertyAnimation(self, b"value", self)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.setDuration(1000)
        self._gradient = QConicalGradient(QPointF(0, 0), 0)
        self._gradient.setColorAt(0.0, QColor(ACCENT_START))
        self._gradient.setColorAt(1.0, QColor(ACCENT_END))
        self._break = False
        self._label = QLabel("00:00", self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setFont(QFont("Rubik SemiBold", 72))
        effect = QGraphicsDropShadowEffect(self._label)
        effect.setBlurRadius(8)
        effect.setColor(QColor(0, 0, 0, 180))
        self._label.setGraphicsEffect(effect)

    def resizeEvent(self, event) -> None:
        self._label.setGeometry(self.rect())

    def sizeHint(self) -> QSize:
        return QSize(260, 260)

    def paintEvent(self, _) -> None:  # noqa: D401
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(10, 10, -10, -10)
        pen = QPen()
        pen.setWidth(self._ring_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setColor(QColor("#2d2d2d"))
        painter.setPen(pen)
        painter.drawEllipse(rect)

        if self._break:
            pen.setColor(QColor(BREAK_COLOR))
        else:
            pen.setBrush(self._gradient)
        painter.setPen(pen)
        span = int(-360 * self._value)
        painter.drawArc(rect, 90 * 16, span * 16)

    @pyqtProperty(float)
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, val: float) -> None:
        self._value = val
        self.update()

    def set_progress(self, frac: float) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._value)
        self._anim.setEndValue(frac)
        self._anim.start()

    def set_time_text(self, text: str) -> None:
        self._label.setText(text)

    def set_break_mode(self, enabled: bool) -> None:
        self._break = enabled
        self.update()


class FabButton(QPushButton):
    """Floating action button with hover animation."""

    def __init__(self, icon: QIcon, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("fab")
        self.setIcon(icon)
        self.setIconSize(QSize(24, 24))
        self._base = QPoint(0, 0)
        self._anim = QPropertyAnimation(self, b"pos", self)
        self._anim.setDuration(120)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(20)
        effect.setOffset(0, 4)
        effect.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(effect)

    def set_base_pos(self, pos: QPoint) -> None:
        self._base = pos
        self.move(pos)

    def enterEvent(self, event) -> None:
        self._animate(self._base - QPoint(0, 4))
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._animate(self._base)
        super().leaveEvent(event)

    def _animate(self, pos: QPoint) -> None:
        self._anim.stop()
        self._anim.setStartValue(self.pos())
        self._anim.setEndValue(pos)
        self._anim.start()


class PomodoroTimer(QWidget):
    """Timer widget with ring and controls."""

    def __init__(self) -> None:
        super().__init__()
        self.duration = 25 * 60
        self.remaining = self.duration
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ring = RingWidget(self)
        layout.addWidget(self.ring)

        if qta:
            play_icon = qta.icon("fa.play", color=TEXT_PRIMARY)
            pause_icon = qta.icon("fa.pause", color=TEXT_PRIMARY)
            reset_icon = qta.icon("fa.redo", color=TEXT_PRIMARY)
        else:
            play_icon = pause_icon = reset_icon = QIcon()

        self.play_icon = play_icon
        self.pause_icon = pause_icon
        self.play_btn = FabButton(play_icon, self.ring)
        self.reset_btn = FabButton(reset_icon, self.ring)

        self.play_btn.clicked.connect(self.toggle_play)
        self.reset_btn.clicked.connect(self.reset)

        self.sound = QSoundEffect(self)
        self.sound.setSource(QUrl("qrc:/audio/ding.mp3"))

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        r = self.ring.geometry()
        pb = self.play_btn.size()
        rb = self.reset_btn.size()
        self.play_btn.set_base_pos(QPoint(r.center().x() - pb.width() // 2, r.bottom() - pb.height() // 2))
        self.reset_btn.set_base_pos(QPoint(r.right() - rb.width(), r.bottom() - rb.height()))

    def start(self) -> None:
        self.timer.start(1000)

    def pause(self) -> None:
        self.timer.stop()

    def toggle_play(self) -> None:
        if self.timer.isActive():
            self.pause()
            self.play_btn.setIcon(self.play_icon)
        else:
            self.start()
            self.play_btn.setIcon(self.pause_icon)

    def reset(self) -> None:
        self.timer.stop()
        self.remaining = self.duration
        self.ring.set_progress(1.0)
        self.update_display()
        self.play_btn.setIcon(self.play_icon)
        self.ring.set_break_mode(False)

    def tick(self) -> None:
        if self.remaining > 0:
            self.remaining -= 1
            self.update_display()
            self.ring.set_progress(self.remaining / self.duration)
            if self.remaining <= 300:
                self.ring.set_break_mode(True)
        else:
            self.timer.stop()
            self.sound.play()
            self.play_btn.setIcon(self.play_icon)

    def update_display(self) -> None:
        minutes = self.remaining // 60
        secs = self.remaining % 60
        self.ring.set_time_text(f"{minutes:02d}:{secs:02d}")


def run_app() -> None:
    app = QApplication([])
    QFontDatabase.addApplicationFont(":/fonts/Rubik-SemiBold.ttf")
    timer = PomodoroTimer()
    timer.show()
    app.exec()


if __name__ == "__main__":
    run_app()
