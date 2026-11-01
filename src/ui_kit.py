"""Small widgets shared by every page so the desktop app reads as one product."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from src import theme


def repolish(widget):
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def make_card(title=None, state=None):
    frame = QFrame()
    frame.setProperty("class", "card")
    if state:
        frame.setProperty("state", state)
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(18, 14, 18, 14)
    lay.setSpacing(8)
    if title:
        t = QLabel(title)
        t.setProperty("class", "card-title")
        lay.addWidget(t)
    return frame, lay


def tag(text):
    lbl = QLabel(text)
    lbl.setProperty("class", "tag")
    return lbl


def page_header(title, subtitle=None, right=None):
    """Page title in the display face, an optional one-line description and an optional widget on the right."""
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    col = QVBoxLayout()
    col.setSpacing(2)
    t = QLabel(title)
    t.setProperty("class", "page-title")
    col.addWidget(t)
    if subtitle:
        s = QLabel(subtitle)
        s.setProperty("class", "muted")
        col.addWidget(s)
    row.addLayout(col)
    row.addStretch()
    if right is not None:
        row.addWidget(right, alignment=Qt.AlignmentFlag.AlignVCenter)
    return box


class MetricTile(QFrame):
    """A small readout: label, big value, optional bar."""

    def __init__(self, label, unit="", value_px=34, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        self.value_px = value_px
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(2)
        self.label = QLabel(label)
        self.label.setProperty("class", "card-title")
        row = QHBoxLayout()
        row.setSpacing(6)
        self.value = QLabel("--")
        self.value.setStyleSheet(theme.css_display(value_px))
        self.unit = QLabel(unit)
        self.unit.setProperty("class", "faint")
        row.addWidget(self.value)
        row.addWidget(self.unit, alignment=Qt.AlignmentFlag.AlignBottom)
        row.addStretch()
        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(5)
        self.bar.setRange(0, 100)
        lay.addWidget(self.label)
        lay.addLayout(row)
        lay.addWidget(self.bar)

    def set(self, text, ratio=None, color=None):
        self.value.setText(text)
        col = color or theme.TEXT
        self.value.setStyleSheet(theme.css_display(self.value_px, col))
        if ratio is None:
            self.bar.setValue(0)
        else:
            self.bar.setValue(int(max(0.0, min(1.0, ratio)) * 100))
            self.bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {col}; border-radius: 2px; }}")


def kv_row(label, value_widget):
    """One label / value line inside a card."""
    row = QHBoxLayout()
    row.setSpacing(10)
    k = QLabel(label)
    k.setProperty("class", "muted")
    row.addWidget(k)
    row.addStretch()
    row.addWidget(value_widget)
    return row


def value_label(text="--", color=None):
    v = QLabel(text)
    v.setStyleSheet(theme.css_semi(18, color or theme.TEXT))
    return v
