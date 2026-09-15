"""Pruebas básicas del paquete MeteoCam."""

import meteocam


def test_version_inicial() -> None:
    """Comprueba que MeteoCam expone correctamente su versión inicial."""
    assert meteocam.__version__ == "0.1.0"


# Fin de fichero
# Fin archivo: tests/test_package.py