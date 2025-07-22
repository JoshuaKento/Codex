# coding: utf-8
"""PyQt6 Pomodoro timer with animated ring and schedule list."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

# design constants
BG_DARK = "#1b1b1b"
BG_PANEL = "rgba(255,255,255,0.06)"
ACCENT_START = "#00d2ff"
ACCENT_END = "#3a7bd5"
BREAK_START = "#ff4b2b"
BREAK_END = "#ff416c"
TEXT_PRIMARY = "#F5F8FB"

try:
    from PyQt6.QtCore import (
        QSize,
        QUrl,
        QEasingCurve,
        QPointF,
        QPropertyAnimation,
        Qt,
        QTimer,
        pyqtProperty,
    )
    from PyQt6.QtGui import (
        QAction,
        QColor,
        QConicalGradient,
        QFont,
        QFontDatabase,
        QPainter,
        QPalette,
        QPen,

    )
    from PyQt6.QtMultimedia import QSoundEffect
    from PyQt6.QtWidgets import (
        QApplication,
        QCheckBox,
        QGraphicsDropShadowEffect,
        QGraphicsColorizeEffect,
        QListView,
        QMainWindow,
        QPushButton,
        QStyledItemDelegate,
        QStyleOptionViewItem,
        QStyle,
        QWidget,
        QHBoxLayout,
        QVBoxLayout,
        QLabel,
        QLineEdit,
        QColorDialog,
        QFrame,
    )
    from PyQt6.QtCore import QAbstractListModel, QModelIndex, QVariant, QSettings
except ModuleNotFoundError as exc:  # pragma: no cover - environment specific
    raise SystemExit(
        "PyQt6 is required to run this application. "
        "Install dependencies with './setup.sh'."
    ) from exc

import resources.resources

try:
    import qtawesome as qta
except ModuleNotFoundError:  # pragma: no cover - optional
    qta = None


class RingWidget(QWidget):
    """Circular progress ring with gradient and animated value."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._value = 0.0
        self._ring_width = 14
        self._break_mode = False
        self._anim = QPropertyAnimation(self, b"value", self)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.setDuration(1000)
        self._gradient = QConicalGradient(QPointF(0, 0), 0)
        self._gradient.setColorAt(0.0, QColor(ACCENT_START))
        self._gradient.setColorAt(1.0, QColor(ACCENT_END))
        self._display = QLabel("00:00", self)
        font = QFont("Rubik SemiBold", 72)
        self._display.setFont(font)
        self._display.setStyleSheet(f"color: {TEXT_PRIMARY}")
        self._display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(self._display)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

    def sizeHint(self) -> QSize:
        return QSize(250, 250)

    def paintEvent(self, event) -> None:  # noqa: D401
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(10, 10, -10, -10)
        pen = QPen()
        pen.setWidth(self._ring_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setColor(QColor("#333"))
        painter.setPen(pen)
        painter.drawEllipse(rect)
        pen.setColor(QColor(TEXT_PRIMARY))
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

    def set_break_mode(self, enabled: bool) -> None:
        self._break_mode = enabled
        self._gradient.setColorAt(0.0, QColor(BREAK_START if enabled else ACCENT_START))
        self._gradient.setColorAt(1.0, QColor(BREAK_END if enabled else ACCENT_END))
        self.update()

    def set_progress(self, fraction: float) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._value)
        self._anim.setEndValue(fraction)
        self._anim.start()

    def set_time_text(self, text: str) -> None:
        self._display.setText(text)


@dataclass
class Slot:
    time: str
    title: str = ""
    color: QColor = field(default_factory=lambda: QColor("#ffffff"))
    completed: bool = False


class ScheduleModel(QAbstractListModel):
    """Model for 15 minute schedule slots."""

    def __init__(self) -> None:
        super().__init__()
        self.slots: List[Slot] = []
        for h in range(24):
            for q in range(4):
                self.slots.append(Slot(f"{h:02d}:{q*15:02d}"))

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: D401
        return len(self.slots)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> QVariant:
        if not index.isValid():
            return QVariant()
        slot = self.slots[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return f"{slot.time} {slot.title}"
        if role == Qt.ItemDataRole.BackgroundRole:
            return slot.color
        if role == Qt.ItemDataRole.FontRole and slot.completed:
            f = QFont()
            f.setStrikeOut(True)
            return f
        if role == Qt.ItemDataRole.ForegroundRole and slot.completed:
            c = QColor("#eee")
            c.setAlphaF(0.3)
            return c
        return QVariant()

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:  # noqa: D401
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def setData(self, index: QModelIndex, value: QVariant, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid():
            return False
        slot = self.slots[index.row()]
        if role == Qt.ItemDataRole.EditRole:
            slot.title = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False


class SlotDelegate(QStyledItemDelegate):
    """Delegate to edit slot title and choose color."""

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        container = QFrame(parent)
        layout = QHBoxLayout(container)
        edit = QLineEdit(container)
        btn = QPushButton("Color", container)
        layout.addWidget(edit)
        layout.addWidget(btn)
        container.edit = edit  # type: ignore[attr-defined]
        container.btn = btn  # type: ignore[attr-defined]
        btn.clicked.connect(lambda: self.choose_color(container, index))
        return container

    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        slot: Slot = index.model().slots[index.row()]  # type: ignore
        editor.edit.setText(slot.title)  # type: ignore[attr-defined]

    def setModelData(self, editor: QWidget, model: QAbstractListModel, index: QModelIndex) -> None:
        model.setData(index, editor.edit.text())  # type: ignore[attr-defined]

    def choose_color(self, editor: QWidget, index: QModelIndex) -> None:
        slot: Slot = index.model().slots[index.row()]  # type: ignore
        color = QColorDialog.getColor(slot.color, editor)
        if color.isValid():
            slot.color = color
            model: QAbstractListModel = index.model()
            model.dataChanged.emit(index, index, [Qt.ItemDataRole.BackgroundRole])


class PomodoroApp(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings("codex", "pomodoro")
        self.setWindowTitle("Pomodoro")
        self.resize(800, 480)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.timer_duration = 25 * 60
        self.remaining = self.timer_duration
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.auto_start = False

        self.load_theme()

        central = QFrame(self)
        central.setStyleSheet(
            f"background-color: {BG_PANEL}; border-radius: 20px;"
        )
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)

        header = QHBoxLayout()
        self.theme_toggle = QCheckBox("Light", self)
        self.auto_box = QCheckBox("Auto start next", self)
        header.addWidget(self.theme_toggle)
        header.addStretch(1)
        header.addWidget(self.auto_box)
        outer.addLayout(header)

        self.theme_toggle.toggled.connect(lambda s: self.apply_theme(not s))
        self.auto_box.toggled.connect(lambda s: setattr(self, "auto_start", s))

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)
        outer.addLayout(main_layout)

        self.ring = RingWidget(self)
        self.ring.set_break_mode(False)
        main_layout.addWidget(self.ring, 1)

        self.schedule_model = ScheduleModel()
        self.schedule_view = QListView()
        self.schedule_view.setModel(self.schedule_model)
        self.schedule_view.setItemDelegate(SlotDelegate(self.schedule_view))
        self.schedule_view.setFont(QFont("Rubik SemiBold", 12))
        self.schedule_view.setStyleSheet(f"color: {TEXT_PRIMARY};")
        main_layout.addWidget(self.schedule_view)

        btn_layout = QHBoxLayout()
        self.play_btn = QPushButton()
        self.pause_btn = QPushButton()
        self.reset_btn = QPushButton()

        for btn, icon_name in [
            (self.play_btn, "fa.play"),
            (self.pause_btn, "fa.pause"),
            (self.reset_btn, "fa.refresh"),
        ]:
            if qta:
                btn.setIcon(qta.icon(icon_name, color=TEXT_PRIMARY))
                btn.setIconSize(QSize(24, 24))
            else:
                btn.setText(icon_name.split(".")[1].title())
            btn.setFixedSize(56, 32)
            btn.setStyleSheet(
                f"background-color: {BG_PANEL}; border-radius: 16px; color: {TEXT_PRIMARY};"
                "border: none;"
            )
            shadow = QGraphicsDropShadowEffect(btn)
            shadow.setBlurRadius(8)
            shadow.setOffset(0, 2)
            btn.setGraphicsEffect(shadow)
            btn_layout.addWidget(btn)

        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addLayout(btn_layout)
        self.ring.layout().addLayout(vbox)

        self.play_btn.clicked.connect(self.start)
        self.pause_btn.clicked.connect(self.pause)
        self.reset_btn.clicked.connect(self.reset)

        self.shortcut_play = QAction(self)
        self.shortcut_play.setShortcut("Ctrl+Space")
        self.shortcut_play.triggered.connect(self.toggle_play)
        self.addAction(self.shortcut_play)

        self.shortcut_reset = QAction(self)
        self.shortcut_reset.setShortcut("R")
        self.shortcut_reset.triggered.connect(self.reset)
        self.addAction(self.shortcut_reset)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(0, 0, 0, 160))
        central.setGraphicsEffect(self.shadow)

        self.sound = QSoundEffect(self)
        self.sound.setSource(QUrl("qrc:/audio/ding.mp3"))

        self.update_display()

    # Theme handling
    def load_theme(self) -> None:
        dark = self.settings.value("dark", True, type=bool)
        self.apply_theme(dark)

    def apply_theme(self, dark: bool) -> None:
        pal = self.palette()
        if dark:
            pal.setColor(QPalette.ColorRole.Window, QColor(BG_DARK))
            pal.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_PRIMARY))
        else:
            pal.setColor(QPalette.ColorRole.Window, QColor("#fff"))
            pal.setColor(QPalette.ColorRole.WindowText, QColor("#000"))
        self.setPalette(pal)
        self.settings.setValue("dark", dark)

    # Timer
    def start(self) -> None:
        self.timer.start(1000)

    def pause(self) -> None:
        self.timer.stop()

    def toggle_play(self) -> None:
        if self.timer.isActive():
            self.pause()
        else:
            self.start()

    def reset(self) -> None:
        self.timer.stop()
        self.remaining = self.timer_duration
        self.update_display()
        self.ring.set_progress(1.0)

    def tick(self) -> None:
        if self.remaining > 0:
            self.remaining -= 1
            self.update_display()
            fraction = self.remaining / self.timer_duration
            self.ring.set_progress(fraction)
        if self.remaining == 0:
            self.timer.stop()
            self.sound.play()
            self.flash_screen()
            if self.auto_start:
                self.remaining = self.timer_duration
                self.start()

    def flash_screen(self) -> None:
        effect = QGraphicsColorizeEffect(self)
        effect.setColor(QColor("white"))
        self.setGraphicsEffect(effect)
        QTimer.singleShot(5000, lambda: self.setGraphicsEffect(None))

    def update_display(self) -> None:
        minutes = self.remaining // 60
        secs = self.remaining % 60
        self.ring.set_time_text(f"{minutes:02d}:{secs:02d}")


def main() -> None:
    app = QApplication([])
    QFontDatabase.addApplicationFont(":/fonts/Rubik-SemiBold.ttf")
    res = PomodoroApp()
    res.show()
    app.exec()


if __name__ == "__main__":
    main()
