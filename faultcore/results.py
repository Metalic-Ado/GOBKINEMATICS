
# ======================================================
# RESULTS
# ======================================================

def get_summary(resultados):
    """
    Genera un resumen estadístico de los resultados.

    No modifica los registros originales.
    """

    estados = (
        "conforme",
        "cuasi_conforme",
        "inconforme",
        "invalido"
    )

    niveles = ("N1", "N2", "N3", "N4", "N5")

    resumen = {
        "total": len(resultados),
        "estados": {estado: 0 for estado in estados},
        "niveles": {nivel: 0 for nivel in niveles},
        "subtipos": {}
    }

    for registro in resultados:

        estado = registro.get("estado")
        nivel = registro.get("nivel")
        subtipo = registro.get("subtipo")

        if estado in resumen["estados"]:
            resumen["estados"][estado] += 1

        if nivel in resumen["niveles"]:
            resumen["niveles"][nivel] += 1

        if subtipo is not None:
            resumen["subtipos"][subtipo] = (
                resumen["subtipos"].get(subtipo, 0) + 1
            )

    return resumen


# ======================================================
# FILTRAR POR ESTADO
# ======================================================

def filter_by_state(resultados, estado):
    """
    Devuelve los registros correspondientes a un estado.
    """

    return [
        registro
        for registro in resultados
        if registro.get("estado") == estado
    ]


# ======================================================
# FILTRAR POR NIVEL
# ======================================================

def filter_by_level(resultados, nivel):
    """
    Devuelve los registros correspondientes a un nivel.
    """

    return [
        registro
        for registro in resultados
        if registro.get("nivel") == nivel
    ]


# ======================================================
# FILTRAR POR SUBTIPO
# ======================================================

def filter_by_subtype(resultados, subtipo):
    """
    Devuelve los registros correspondientes a un subtipo.
    """

    return [
        registro
        for registro in resultados
        if registro.get("subtipo") == subtipo
    ]
