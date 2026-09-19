"""Tema MeteoCam Classic Claro inspirado en Windows 3.1."""

CLASSIC_LIGHT_STYLESHEET = """
/* =========================================================
   METEOCAM CLASSIC CLARO
   Inspiración visual: Microsoft Windows 3.1
   ========================================================= */

QWidget {
    background-color: #c0c0c0;
    color: #000000;
    font-family: "MS Sans Serif", "Microsoft Sans Serif", "Segoe UI";
    font-size: 10pt;
}

QMainWindow {
    background-color: #c0c0c0;
}


/* =========================================================
   SUPERFICIE PRINCIPAL
   ========================================================= */

QWidget#mainWindowSurface {
    background-color: #c0c0c0;

    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #000000;
    border-bottom: 2px solid #000000;
}


/* =========================================================
   BARRA DE TÍTULO WINDOWS 3.1
   ========================================================= */

QFrame#win31TitleBar {
    background-color: #000080;

    border-top: 1px solid #ffffff;
    border-left: 1px solid #ffffff;
    border-right: 1px solid #000000;
    border-bottom: 1px solid #000000;
}

QLabel#win31TitleText {
    background-color: #000080;
    color: #ffffff;

    font-weight: bold;
    font-size: 11pt;

    padding-left: 4px;
}


/* =========================================================
   BOTONES DE LA BARRA DE TÍTULO
   ========================================================= */

QPushButton#win31SystemButton,
QPushButton#win31CaptionButton {
    background-color: #c0c0c0;
    color: #000000;

    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #000000;
    border-bottom: 2px solid #000000;

    padding: 0px;
    margin: 0px;

    font-weight: bold;
    font-size: 9pt;
}

QPushButton#win31SystemButton:pressed,
QPushButton#win31CaptionButton:pressed {
    background-color: #c0c0c0;

    border-top: 2px solid #000000;
    border-left: 2px solid #000000;
    border-right: 2px solid #ffffff;
    border-bottom: 2px solid #ffffff;

    padding-top: 2px;
    padding-left: 2px;
}


/* =========================================================
   MENÚ PRINCIPAL
   ========================================================= */

QFrame#win31MenuBar {
    background-color: #c0c0c0;
    border: none;
}

QLabel#win31MenuItem {
    background-color: #c0c0c0;
    color: #000000;

    padding: 2px 1px;
}

QLabel#win31MenuItem:hover {
    background-color: #000080;
    color: #ffffff;
}


/* =========================================================
   BARRA DE HERRAMIENTAS
   ========================================================= */

QFrame#win31ToolBar {
    background-color: #c0c0c0;

    border-top: 1px solid #ffffff;
    border-bottom: 1px solid #808080;
}

QFrame#win31ToolSeparator {
    color: #808080;
    background-color: #c0c0c0;
}

QLabel#toolbarVersion {
    background-color: #c0c0c0;
    color: #000000;

    padding-right: 4px;
}


/* =========================================================
   CABECERAS Y CAMPOS
   ========================================================= */

QFrame {
    background-color: #c0c0c0;
}

QLabel#applicationTitle {
    font-weight: bold;
    color: #000000;
}

QLabel#fieldTitle {
    color: #000000;
}

QLabel#fieldValue {
    color: #000000;
}


/* =========================================================
   GROUPBOX WINDOWS 3.1
   ========================================================= */

QGroupBox {
    background-color: #c0c0c0;
    color: #000000;

    border-top: 1px solid #808080;
    border-left: 1px solid #808080;
    border-right: 1px solid #ffffff;
    border-bottom: 1px solid #ffffff;

    margin-top: 8px;
    padding-top: 7px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;

    left: 8px;
    padding: 0px 4px;

    background-color: #c0c0c0;
    color: #000000;
}


/* =========================================================
   VISOR DE VÍDEO HUNDIDO
   ========================================================= */

QFrame#videoFrame {
    background-color: #000000;

    border-top: 2px solid #808080;
    border-left: 2px solid #808080;
    border-right: 2px solid #ffffff;
    border-bottom: 2px solid #ffffff;
}

QLabel#videoPlaceholder {
    background-color: #000000;
    color: #c0c0c0;
}


/* =========================================================
   BOTONES WINDOWS 3.1
   ========================================================= */

QPushButton {
    background-color: #c0c0c0;
    color: #000000;

    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #000000;
    border-bottom: 2px solid #000000;

    padding: 4px 12px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #c0c0c0;
}

QPushButton:focus {
    outline: 1px dotted #000000;
}

QPushButton:pressed {
    background-color: #c0c0c0;

    border-top: 2px solid #000000;
    border-left: 2px solid #000000;
    border-right: 2px solid #ffffff;
    border-bottom: 2px solid #ffffff;

    padding-top: 6px;
    padding-left: 14px;
    padding-right: 10px;
    padding-bottom: 2px;
}

QPushButton:disabled {
    background-color: #c0c0c0;
    color: #808080;

    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #808080;
    border-bottom: 2px solid #808080;
}


/* =========================================================
   CAMPOS DE ENTRADA
   ========================================================= */

QLineEdit,
QComboBox,
QSpinBox {
    background-color: #ffffff;
    color: #000000;

    border-top: 2px solid #808080;
    border-left: 2px solid #808080;
    border-right: 2px solid #ffffff;
    border-bottom: 2px solid #ffffff;

    padding: 2px;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus {
    border-top: 2px solid #000000;
    border-left: 2px solid #000000;
    border-right: 2px solid #ffffff;
    border-bottom: 2px solid #ffffff;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #000000;

    selection-background-color: #000080;
    selection-color: #ffffff;
}


/* =========================================================
   MENÚS EMERGENTES
   ========================================================= */

QMenu {
    background-color: #c0c0c0;
    color: #000000;

    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #000000;
    border-bottom: 2px solid #000000;
}

QMenu::item {
    padding: 4px 24px 4px 20px;
}

QMenu::item:selected {
    background-color: #000080;
    color: #ffffff;
}


/* =========================================================
   BARRA DE ESTADO
   ========================================================= */

QStatusBar#win31StatusBar {
    background-color: #c0c0c0;
    color: #000000;

    border-top: 2px solid #808080;
    border-left: 2px solid #808080;
    border-right: 2px solid #ffffff;
    border-bottom: 2px solid #ffffff;

    min-height: 20px;
}

QStatusBar#win31StatusBar::item {
    border: none;
}


/* =========================================================
   SCROLLBARS CLÁSICAS
   ========================================================= */

QScrollBar:vertical {
    background-color: #c0c0c0;
    width: 16px;
    margin: 16px 0px 16px 0px;
}

QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    min-height: 20px;

    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #000000;
    border-bottom: 2px solid #000000;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    background-color: #c0c0c0;
    height: 16px;

    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #000000;
    border-bottom: 2px solid #000000;
}

QScrollBar:horizontal {
    background-color: #c0c0c0;
    height: 16px;
    margin: 0px 16px 0px 16px;
}

QScrollBar::handle:horizontal {
    background-color: #c0c0c0;
    min-width: 20px;

    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #000000;
    border-bottom: 2px solid #000000;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    background-color: #c0c0c0;
    width: 16px;

    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #000000;
    border-bottom: 2px solid #000000;
}


/* =========================================================
   TOOLTIPS
   ========================================================= */

QToolTip {
    background-color: #ffffe1;
    color: #000000;
    border: 1px solid #000000;
}
"""


# Fin de fichero
# Fin archivo: src/meteocam/themes/classic_light.py