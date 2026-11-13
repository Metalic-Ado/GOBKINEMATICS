
# ======================================================
# IMPORTACIONES
# ======================================================

from .norm_basic import normalize_basic_data
from .clasify_nones import clasify_for_items
from .logic_clasify import process_registration


# ======================================================
# PROCESAMIENTO GENERAL
# ======================================================

def process_data(strike, dip, rake, cine_1, cine_2):
    """
    Ejecuta el procesamiento general de datos estructurales.

    Orden:
    1. Normalización y validación básica.
    2. Clasificación inicial N1-N5.
    3. Evaluación geométrica y cinemática.
    4. Organización de los registros procesados.

    Recibe:
        strike, dip, rake, cine_1, cine_2:
            Datos estructurales de entrada.

    Retorna:
        list: Registros procesados.

    Raises:
        ValueError: Si existen errores de estructura,
                    datos obligatorios o rangos.
        TypeError: Si existen tipos de datos no permitidos.
    """

    # --------------------------------------------------
    # 1. NORMALIZACIÓN Y VALIDACIÓN BÁSICA
    # --------------------------------------------------

    data = normalize_basic_data(
        strike, dip, rake, cine_1, cine_2
    )

    # --------------------------------------------------
    # 2. CLASIFICACIÓN INICIAL
    # --------------------------------------------------

    registros = clasify_for_items(
        data["strike"],
        data["dip"],
        data["rake"],
        data["cine_1"],
        data["cine_2"]
    )

    # --------------------------------------------------
    # 3. EVALUACIÓN GEOLÓGICA
    # --------------------------------------------------

    resultados = [
        process_registration(registro)
        for registro in registros
    ]

    return resultados
