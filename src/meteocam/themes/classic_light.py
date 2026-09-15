"""Tema MeteoCam Classic Claro."""

CLASSIC_LIGHT_STYLESHEET = """
QWidget {
    background-color: #d4d0c8;
    color: #202020;
    font-family: "Segoe UI";
    font-size: 10pt;
}

QMainWindow {
    background-color: #d4d0c8;
}

/* ---------------------------------------------------------
   Cabecera
   --------------------------------------------------------- */

QFrame {
    background-color: #d4d0c8;
}

QFrame#videoFrame {
    background-color: #101010;
    border-top: 2px solid #707070;
    border-left: 2px solid #707070;
    border-right: 2px solid #ffffff;
    border-bottom: 2px solid #ffffff;
}

QLabel#applicationTitle {
    font-size: 18pt;
    font-weight: bold;
    color: #101010;
}

QLabel#fieldTitle {
    font-size: 8pt;
    font-weight: bold;
    color: #505050;
}

QLabel#fieldValue {
    font-size: 10pt;
    font-weight: bold;
    color: #101010;
}

QLabel#videoPlaceholder {
    background-color: #101010;
    color: #b8b8b8;
    font-size: 11pt;
}

/* ---------------------------------------------------------
   GroupBox clásico
   --------------------------------------------------------- */

QGroupBox {
    background-color: #d4d0c8;
    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #707070;
    border-bottom: 2px solid #707070;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    background-color: #d4d0c8;
    color: #202020;
}

/* ---------------------------------------------------------
   Botones clásicos tridimensionales
   --------------------------------------------------------- */

QPushButton {
    background-color: #d4d0c8;
    color: #202020;

    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #606060;
    border-bottom: 2px solid #606060;

    padding: 6px 16px;
    min-height: 24px;
}

QPushButton:hover {
    background-color: #dedbd5;
}

QPushButton:pressed {
    background-color: #c4c0b8;

    border-top: 2px solid #606060;
    border-left: 2px solid #606060;
    border-right: 2px solid #ffffff;
    border-bottom: 2px solid #ffffff;

    padding-top: 8px;
    padding-left: 18px;
    padding-right: 14px;
    padding-bottom: 4px;
}

QPushButton:disabled {
    color: #808080;
    background-color: #c8c5be;
}

/* ---------------------------------------------------------
   Barra de estado
   --------------------------------------------------------- */

QStatusBar {
    background-color: #d4d0c8;
    color: #202020;

    border-top: 2px solid #707070;
}

QStatusBar::item {
    border: none;
}

/* ---------------------------------------------------------
   Menús preparados para fases posteriores
   --------------------------------------------------------- */

QMenuBar {
    background-color: #d4d0c8;
    color: #202020;
}

QMenuBar::item {
    background-color: transparent;
    padding: 4px 8px;
}

QMenuBar::item:selected {
    background-color: #0a64ad;
    color: #ffffff;
}

QMenu {
    background-color: #d4d0c8;
    color: #202020;

    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #606060;
    border-bottom: 2px solid #606060;
}

QMenu::item {
    padding: 5px 28px 5px 24px;
}

QMenu::item:selected {
    background-color: #0a64ad;
    color: #ffffff;
}

/* ---------------------------------------------------------
   Controles preparados para configuración futura
   --------------------------------------------------------- */

QLineEdit,
QComboBox,
QSpinBox {
    background-color: #ffffff;
    color: #101010;

    border-top: 2px solid #707070;
    border-left: 2px solid #707070;
    border-right: 2px solid #ffffff;
    border-bottom: 2px solid #ffffff;

    padding: 4px;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus {
    border: 2px solid #0a64ad;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #101010;
    selection-background-color: #0a64ad;
    selection-color: #ffffff;
}

/* ---------------------------------------------------------
   Scrollbars clásicas
   --------------------------------------------------------- */

QScrollBar:vertical {
    background-color: #d4d0c8;
    width: 18px;
    margin: 18px 0 18px 0;
}

QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    min-height: 24px;

    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #606060;
    border-bottom: 2px solid #606060;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    background-color: #d4d0c8;
    height: 18px;

    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-right: 1px solid #606060;
    border-bottom: 1px solid #606060;
}

QToolTip {
    background-color: #ffffdc;
    color: #101010;
    border: 1px solid #202020;
}
"""


# Fin de fichero
# Fin archivo: src/meteocam/themes/classic_light.py