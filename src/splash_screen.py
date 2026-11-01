from PyQt6.QtWidgets import QSplashScreen, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPixmap, QPainter, QPolygonF

from src import theme
from src.theme import qc


class RideShieldSplash(QSplashScreen):
    """Start-up screen in the website's look: deep violet field, the logo, a violet progress bar."""

    W, H = 900, 500

    def __init__(self):
        pixmap = QPixmap(self.W, self.H)
        pixmap.fill(qc(theme.HERO))
        p = QPainter(pixmap)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        # The slanted slab from the website hero
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(qc("#150C30"))
        p.drawPolygon(QPolygonF([QPointF(520, 0), QPointF(900, 0), QPointF(900, 500), QPointF(400, 500)]))
        logo = theme.brand("logo-night.png")
        if not logo.isNull():
            logo = logo.scaledToWidth(520, Qt.TransformationMode.SmoothTransformation)
            p.drawPixmap((self.W - logo.width()) // 2, 120, logo)
        p.end()
        super().__init__(pixmap)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.status_label = QLabel("Starting", self)
        self.status_label.setStyleSheet(f"color: {theme.MUTED}; font-size: 14px; background: transparent;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setGeometry(0, self.H - 70, self.W, 24)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(80, self.H - 36, self.W - 160, 6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(
            f"QProgressBar {{ background-color: rgba(255,255,255,0.12); border: none; border-radius: 3px; }}"
            f"QProgressBar::chunk {{ background-color: {theme.ACCENT}; border-radius: 3px; }}"
        )

    def set_progress(self, value, text):
        self.progress_bar.setValue(value)
        self.status_label.setText(text)
        self.repaint()
