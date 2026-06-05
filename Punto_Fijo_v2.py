# =============================================================
#  PUNTO FIJO — PUNTO DE ENTRADA PRINCIPAL
#  Métodos Numéricos — Universidad Distrital 2026-1
#  Archivo: METODOS/Punto_Fijo_v2.py
# =============================================================
"""
Punto de entrada para la aplicación de Método del Punto Fijo.

CAMBIOS EN VERSIÓN 2.0:
- Eliminada ejecución automática de ejemplos
- Gráficas bajo demanda en lugar de automáticas
- Nueva interfaz con navegación única
- Mejor experiencia de usuario

Lanzar con: python Punto_Fijo_v2.py
"""

import os
import sys

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, BASE_DIR)
    
    # Importar y lanzar aplicación principal
    from main_app import main
    main()
