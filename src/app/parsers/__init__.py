"""
Parsers package - Extracción de datos desde HTML.

Cada parser se especializa en una estructura HTML específica:
- HardGamersParser: Para hardgamers.com.ar
- [Futuro] CompraGamerParser: Para compragamer.com
- [Futuro] MercadoLibreParser: Para mercadolibre.com.ar

Principio: Un parser por sitio web para manejar sus particularidades.
"""

from .hardgamers_parser import HardGamersParser

__all__ = ["HardGamersParser"]