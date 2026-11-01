"""RideShield AI desktop theme: the website's night palette, fonts and brand art in one place."""
import os
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QPixmap
from src.paths import resource

# Night palette (same values as the website's dark theme).
BG = "#0A0A0F"
BG2 = "#0F0F16"
DEVICE = "#07070C"        # instrument surfaces
SURFACE = "#14141C"
SURFACE2 = "#1B1B25"
LINE = "#252530"
LINE2 = "#363642"
TEXT = "#EEEDF5"
MUTED = "#A8A6BA"
FAINT = "#8C8AA5"
ACCENT = "#B79CFF"        # lavender, text and outlines on dark
VIOLET = "#7C4DFF"        # logo violet, fills
HERO = "#1E1240"          # deep violet field
OK = "#3DDC97"
BAD = "#FF6674"
WARN = "#F5B84B"

DISPLAY_FAMILY = "Barlow Condensed ExtraBold"
DISPLAY_SEMI = "Barlow Condensed"
BODY_FAMILY = "Geist"


def qc(hex_color: str, alpha: int = 255) -> QColor:
    c = QColor(hex_color)
    c.setAlpha(alpha)
    return c


def load_fonts() -> None:
    """Register the bundled fonts. Falls back to system fonts if a file is missing."""
    folder = resource("assets", "fonts")
    for name in ("BarlowCondensed-600.ttf", "BarlowCondensed-700.ttf", "BarlowCondensed-800.ttf", "Geist-Variable.ttf"):
        path = os.path.join(folder, name)
        if os.path.exists(path):
            QFontDatabase.addApplicationFont(path)


def display_font(pixel_size: int) -> QFont:
    f = QFont(DISPLAY_FAMILY)
    f.setPixelSize(max(6, int(pixel_size)))
    return f


def semi_font(pixel_size: int) -> QFont:
    f = QFont(DISPLAY_SEMI)
    f.setPixelSize(max(6, int(pixel_size)))
    f.setBold(True)
    return f


def body_font(pixel_size: int, bold: bool = False) -> QFont:
    f = QFont(BODY_FAMILY)
    f.setPixelSize(max(6, int(pixel_size)))
    if bold:
        f.setWeight(QFont.Weight.DemiBold)
    return f


def brand(name: str) -> QPixmap:
    return QPixmap(resource("assets", "brand", name))


def css_display(px: int, color: str = None) -> str:
    """Stylesheet fragment for big condensed numbers and headings (the app stylesheet overrides setFont)."""
    return f"font-family: 'Barlow Condensed ExtraBold'; font-size: {int(px)}px;" + (f" color: {color};" if color else "")


def css_semi(px: int, color: str = None) -> str:
    return f"font-family: 'Barlow Condensed'; font-weight: 700; font-size: {int(px)}px;" + (f" color: {color};" if color else "")
