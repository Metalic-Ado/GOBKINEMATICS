
"""
KINEMATICS_NORM
===============

Punto de entrada de GOBKINEMATICS para el procesamiento de fallas.

La normalización, clasificación y evaluación geológica/cinemática
son responsabilidad exclusiva de FAULTCORE.

Este módulo únicamente:
1. Recibe los datos de entrada.
2. Ejecuta el procesamiento de FAULTCORE.
3. Entrega los registros procesados.
4. Extrae los campos necesarios para los módulos de representación.
"""

from ..faultcore.process import process_data

# ============================================================
# 1. PROCESAMIENTO PRINCIPAL
# ============================================================

def process_fault_data(
        strike,
        dip,
        rake,
        cine_1,
        cine_2
):
    """
    Procesa los datos estructurales mediante FAULTCORE.

    Parámetros:
        strike: dirección de la falla.
        dip: buzamiento.
        rake: ángulo de deslizamiento.
        cine_1: primera componente cinemática.
        cine_2: segunda componente cinemática.

    Returns:
        list[dict]: registros normalizados, clasificados y evaluados
                    por FAULTCORE.
    """

    return process_data(
        strike=strike,
        dip=dip,
        rake=rake,
        cine_1=cine_1,
        cine_2=cine_2
    )


# ============================================================
# 2. INTERFAZ PARA LISTAS
# ============================================================

def from_lists(
        strike,
        dip,
        rake,
        cine_1,
        cine_2
):
    """
    Recibe listas o valores individuales y ejecuta FAULTCORE.

    Esta función sustituye la antigua implementación basada
    en FaultInput y make_fault.

    No realiza normalización local.
    """

    return process_fault_data(
        strike=strike,
        dip=dip,
        rake=rake,
        cine_1=cine_1,
        cine_2=cine_2
    )


# ============================================================
# 3. EXTRACCIÓN DE ARRAYS
# ============================================================

def extract_arrays(registros):
    """
    Extrae los cinco campos estructurales de los registros
    procesados por FAULTCORE.

    No normaliza ni modifica los registros.
    """

    if not isinstance(registros, list):
        raise TypeError(
            "registros debe ser una lista."
        )

    campos = {
        "strike": [],
        "dip": [],
        "rake": [],
        "cine_1": [],
        "cine_2": []
    }

    for registro in registros:

        if not isinstance(registro, dict):
            raise TypeError(
                "Cada registro debe ser un diccionario."
            )

        datos = registro.get("datos")

        if not isinstance(datos, dict):
            raise ValueError(
                "El registro no contiene el diccionario 'datos'."
            )

        for campo in campos:
            campos[campo].append(
                datos.get(campo)
            )

    return (
        campos["strike"],
        campos["dip"],
        campos["rake"],
        campos["cine_1"],
        campos["cine_2"]
    )


# ============================================================
# 4. EXTRACCIÓN DE DATOS PARA REPRESENTACIÓN
# ============================================================

def extract_plot_data(registros):
    """
    Prepara los campos estructurales y el valor cinemático
    de los registros procesados por FAULTCORE.

    Conserva la correspondencia entre registros.
    No filtra ni modifica resultados.
    """

    if not isinstance(registros, list):
        raise TypeError(
            "registros debe ser una lista."
        )

    campos = {
        "strike": [],
        "dip": [],
        "rake": [],
        "cine_1": [],
        "cine_2": [],
        "valor_cinematic": [],
        "clase": [],
        "nivel": [],
        "subtipo": [],
        "estado": [],
        "motivo": []
    }

    for registro in registros:

        datos = registro.get("datos", {})

        campos["strike"].append(datos.get("strike"))
        campos["dip"].append(datos.get("dip"))
        campos["rake"].append(datos.get("rake"))
        campos["cine_1"].append(datos.get("cine_1"))
        campos["cine_2"].append(datos.get("cine_2"))

        campos["valor_cinematic"].append(
            registro.get("valor_cinematic")
        )

        campos["clase"].append(
            registro.get("clase")
        )

        campos["nivel"].append(
            registro.get("nivel")
        )

        campos["subtipo"].append(
            registro.get("subtipo")
        )

        campos["estado"].append(
            registro.get("estado")
        )

        campos["motivo"].append(
            registro.get("motivo")
        )

    return campos
