"""Punto de entrada ejecutable de MeteoCam."""

from meteocam import __version__


def main() -> int:
    """Ejecutar MeteoCam."""
    print(f"MeteoCam {__version__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# Fin de fichero
# Fin archivo: src/meteocam/__main__.py