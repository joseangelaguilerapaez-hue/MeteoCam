# -*- coding: utf-8 -*-

"""Punto de entrada de MeteoCamPublisher.exe (empaquetado con PyInstaller).

PyInstaller necesita un script, no un módulo: este archivo solo delega en
meteocam.cameras.windows_service.main().
"""

from meteocam.cameras.windows_service import main


if __name__ == "__main__":
    main()


# Fin archivo: installer/meteocam_publisher.py
