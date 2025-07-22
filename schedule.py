from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from PyQt6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    Qt,
    QVariant,
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QColorDialog,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QListView,
    QWidget,
)

from theme import PANEL_GLASS


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
        self.slots: List[Slot] = [
            Slot(f"{h:02d}:{q*15:02d}") for h in range(24) for q in range(4)
        ]

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
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )

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
        container.setStyleSheet(f"background:{PANEL_GLASS}; border-radius:4px;")
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


class ScheduleView(QListView):
    def __init__(self) -> None:
        super().__init__()
        self.setModel(ScheduleModel())
        self.setItemDelegate(SlotDelegate(self))
        self.setFont(QFont("Rubik SemiBold", 12))
        self.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)


