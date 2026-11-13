from .norm_geology import (
    cinematic,
    cinematic_from_value,
    infer_missing_cinematic,
    shift_if_missing,
    validate_geometry_n5,
    validate_geometry_n4_case_1,
    validate_geometry_n4_case_3,
    validate_geometry_n3_case_1,
    validate_geometry_n3_case_2,
    validate_geometry_n2,
    validate_geometry_n1,
)

def _treatment_n5(registro):
    """
    Evalúa la conformidad geométrica de un registro N5.

    Recibe un registro previamente normalizado y clasificado.

    Reutiliza las reglas geométricas y cinemáticas de norm_geology.py.

    No elimina ni modifica los datos originales del registro.
    """

    datos = registro["datos"]

    dip = datos["dip"]
    rake = datos["rake"]
    cine_1 = datos["cine_1"]
    cine_2 = datos["cine_2"]

    # --------------------------------------------------
    # 1. Verificar que N5 tenga sus cinco datos
    # --------------------------------------------------

    campos = (
        "strike",
        "dip",
        "rake",
        "cine_1",
        "cine_2",
    )

    if any(datos[campo] is None for campo in campos):
        registro["estado"] = "invalido"
        registro["motivo"] = "N5_con_datos_ausentes"
        registro["nivel"] = "N5"
        return registro

    # --------------------------------------------------
    # 2. Obtener la codificación cinemática
    # --------------------------------------------------

    try:
        valor_cinematic = cinematic(cine_1, cine_2)

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        registro["nivel"] = "N5"
        return registro

    registro["nivel"] = "N5"
    registro["valor_cinematic"] = valor_cinematic

    # --------------------------------------------------
    # 3. Evaluar las restricciones geométricas N5
    # --------------------------------------------------

    try:
        validate_geometry_n5(
            dip=dip,
            rake=rake,
            valor_cinematic=valor_cinematic,
        )

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    # --------------------------------------------------
    # 4. Resultado
    # --------------------------------------------------

    registro["estado"] = "conforme"
    registro["motivo"] = None

    return registro


def _identify_subtype_n4(registro):

    datos = registro["datos"]

    # Normalizar el orden de las cinemáticas.
    cine_1, cine_2 = shift_if_missing(
        datos["cine_1"],
        datos["cine_2"],
    )

    datos["cine_1"] = cine_1
    datos["cine_2"] = cine_2

    strike = datos["strike"]
    dip = datos["dip"]
    rake = datos["rake"]

    # Caso 3: sin rake y con dos cinemáticas.
    if (
        strike is not None
        and dip is not None
        and rake is None
        and cine_1 is not None
        and cine_2 is not None
    ):
        subtipo = "sin_rake_dos_cinematicas"

    # Casos 1 y 2: con rake y una cinemática.
    elif (
        strike is not None
        and dip is not None
        and rake is not None
        and cine_1 is not None
        and cine_2 is None
    ):
        subtipo = "una_cinematica"

    else:
        subtipo = "estructura_N4_invalida"

    registro["subtipo"] = subtipo

    return registro

def _n4_case_1(registro):
    """
    Evalúa N4 caso 1:
    strike + dip + rake + una cinemática.

    Comprueba si la geometría es conforme sin
    necesidad de inferir una segunda cinemática.
    """

    datos = registro["datos"]

    dip = datos["dip"]
    rake = datos["rake"]
    cine = datos["cine_1"]

    registro["nivel"] = "N4"

    # Obtener el valor cinemático.
    try:
        valor = cinematic(cine)

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    registro["valor_cinematic"] = valor

    # Evaluar las reglas geométricas N4 caso 1.
    try:
        validate_geometry_n4_case_1(
            dip=dip,
            rake=rake,
            valor_cinematic=valor,
        )

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    registro["estado"] = "conforme"
    registro["motivo"] = None

    return registro

def _n4_case_2(registro):
    """
    N4 caso 2: autocompletado de la segunda cinemática.

    Recibe:
        strike + dip + rake + una cinemática.

    Si la cinemática faltante puede inferirse:
        1. Calcula el valor cinemático existente.
        2. Infiere el valor cinemático combinado.
        3. Reconstruye las dos cinemáticas.
        4. Reclasifica el registro como N5.
        5. Evalúa la geometría mediante _treatment_n5().
    """

    datos = registro["datos"]

    dip = datos["dip"]
    rake = datos["rake"]
    cine = datos["cine_1"]

    registro["nivel"] = "N4"

    # --------------------------------------------------
    # 1. Comprobar los datos necesarios
    # --------------------------------------------------

    if dip is None or rake is None or cine is None:
        registro["estado"] = "invalido"
        registro["motivo"] = "datos_insuficientes_para_autocompletar"
        return registro

    # --------------------------------------------------
    # 2. Obtener el valor cinemático existente
    # --------------------------------------------------

    try:
        valor = cinematic(cine)

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    # --------------------------------------------------
    # 3. Inferir la cinemática faltante
    # --------------------------------------------------

    try:
        nuevo_valor = infer_missing_cinematic(
            rake=rake,
            valor_cinematic=valor,
        )

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    if nuevo_valor is None:
        registro["estado"] = "inconforme"
        registro["motivo"] = "cinematica_no_inferible"
        return registro

    # --------------------------------------------------
    # 4. Reconstruir las dos cinemáticas
    # --------------------------------------------------

    try:
        cine_1, cine_2 = cinematic_from_value(nuevo_valor)

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    datos["cine_1"] = cine_1
    datos["cine_2"] = cine_2

    # --------------------------------------------------
    # 5. Reclasificar como N5
    # --------------------------------------------------

    registro["clase"] = "N5"

    resultado = _treatment_n5(registro)

    if resultado["estado"] == "conforme":
        resultado["subtipo"] = "N4_autocompletado"
        resultado["motivo"] = (
            "N4_autocompletado: segunda cinematica inferida"
        )

    return resultado

def _n4_case_3(registro):
    """
    N4 caso 3:
    strike + dip + dos cinemáticas, sin rake.

    Evalúa la compatibilidad cinemática y geométrica
    utilizando las reglas de norm_geology.py.

    No infiere ni modifica datos originales.
    """

    datos = registro["datos"]

    dip = datos["dip"]
    rake = datos["rake"]
    cine_1 = datos["cine_1"]
    cine_2 = datos["cine_2"]

    registro["nivel"] = "N4"

    # --------------------------------------------------
    # 1. Verificar la estructura del registro
    # --------------------------------------------------

    if (
        datos["strike"] is None
        or dip is None
        or rake is not None
        or cine_1 is None
        or cine_2 is None
    ):
        registro["estado"] = "invalido"
        registro["motivo"] = "estructura_N4_caso_3_invalida"
        return registro

    # --------------------------------------------------
    # 2. Obtener el valor cinemático
    # --------------------------------------------------

    try:
        valor_cinematic = cinematic(cine_1, cine_2)

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    registro["valor_cinematic"] = valor_cinematic

    # --------------------------------------------------
    # 3. Evaluar las restricciones geométricas
    # --------------------------------------------------

    try:
        validate_geometry_n4_case_3(
            dip=dip,
            rake=rake,
            valor_cinematic=valor_cinematic,
        )

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    # --------------------------------------------------
    # 4. Resultado
    # --------------------------------------------------

    registro["estado"] = "conforme"
    registro["motivo"] = "rake_ausente"

    return registro

def _treatment_n4(registro):
    """
    Coordina los tres casos de N4.
    """

    registro["nivel"] = "N4"

    # Identificar el subtipo y normalizar el orden
    # de las cinemáticas.
    registro = _identify_subtype_n4(registro)

    subtipo = registro["subtipo"]

    if subtipo == "sin_rake_dos_cinematicas":
        return _n4_case_3(registro)

    elif subtipo == "una_cinematica":

        # Primero comprobar N4 caso 1.
        resultado = _n4_case_1(registro.copy())

        if resultado["estado"] == "conforme":
            return resultado

        # Si no cumple N4 caso 1, intentar autocompletar.
        return _n4_case_2(registro)

    else:
        registro["estado"] = "invalido"
        registro["motivo"] = "estructura_N4_invalida"
        return registro


def _n3_case_1(registro):
    """
    N3 caso 1:
    strike + dip + rake, sin cinemáticas.
    """

    datos = registro["datos"]

    dip = datos["dip"]
    rake = datos["rake"]

    registro["nivel"] = "N3"
    registro["subtipo"] = "geometria_sin_cinematicas"

    try:
        validate_geometry_n3_case_1(
            dip=dip,
            rake=rake,
            valor_cinematic=0,
        )

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    registro["estado"] = "conforme"
    registro["motivo"] = "sin_informacion_cinematica"

    return registro

def _n3_case_2(registro):
    """
    N3 caso 2:
    strike + dip + una cinemática, sin rake.
    """

    datos = registro["datos"]

    dip = datos["dip"]

    # Normalizar la posición de la cinemática.
    cine_1, cine_2 = shift_if_missing(
        datos["cine_1"],
        datos["cine_2"],
    )

    datos["cine_1"] = cine_1
    datos["cine_2"] = cine_2

    registro["nivel"] = "N3"
    registro["subtipo"] = "una_cinematica_sin_rake"

    # Comprobar que la estructura corresponda al caso N3.
    if (
        dip is None
        or datos["rake"] is not None
        or cine_1 is None
        or cine_2 is not None
    ):
        registro["estado"] = "invalido"
        registro["motivo"] = "estructura_N3_caso_2_invalida"
        return registro

    # Obtener el valor cinemático.
    try:
        valor_cinematic = cinematic(cine_1)

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    registro["valor_cinematic"] = valor_cinematic

    # Evaluar las reglas geométricas N3.
    try:
        validate_geometry_n3_case_2(
            dip=dip,
            rake=None,
            valor_cinematic=valor_cinematic,
        )

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    registro["estado"] = "conforme"
    registro["motivo"] = "rake_ausente"

    return registro


def _n3_case_3(registro):
    """
    N3 caso 3:
    Strike + dos cinemáticas, sin dip ni rake.
    """

    datos = registro["datos"]

    cine_1 = datos["cine_1"]
    cine_2 = datos["cine_2"]

    registro["nivel"] = "N3"
    registro["subtipo"] = "dos_cinematicas_sin_dip_ni_rake"

    # --------------------------------------------------
    # 1. Comprobar la estructura del registro
    # --------------------------------------------------

    if (
        datos["strike"] is None
        or datos["dip"] is not None
        or datos["rake"] is not None
        or cine_1 is None
        or cine_2 is None
    ):
        registro["estado"] = "invalido"
        registro["motivo"] = "estructura_N3_caso_3_invalida"
        return registro

    # --------------------------------------------------
    # 2. Obtener el valor cinemático
    # --------------------------------------------------

    try:
        valor_cinematic = cinematic(cine_1, cine_2)

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    registro["valor_cinematic"] = valor_cinematic

    # --------------------------------------------------
    # 3. Resultado
    # --------------------------------------------------

    registro["estado"] = "conforme"
    registro["motivo"] = "sin_dip_ni_rake_con_dos_cinematicas"

    return registro



def _treatment_n3(registro):
    """
    Coordina los tratamientos N3.

    N3 caso 1: strike + dip + rake.
    N3 caso 2: strike + dip + una cinemática.
    N3 caso 3: strike + dos cinemáticas, sin dip ni rake.
    """

    datos = registro["datos"]

    registro["nivel"] = "N3"

    # --------------------------------------------------
    # Caso 1: geometría sin cinemáticas.
    # --------------------------------------------------

    if (
        datos["strike"] is not None
        and datos["dip"] is not None
        and datos["rake"] is not None
        and datos["cine_1"] is None
        and datos["cine_2"] is None
    ):
        return _n3_case_1(registro)

    # --------------------------------------------------
    # Caso 2: geometría sin rake y una cinemática.
    # --------------------------------------------------

    elif (
        datos["strike"] is not None
        and datos["dip"] is not None
        and datos["rake"] is None
        and (
            datos["cine_1"] is not None
            or datos["cine_2"] is not None
        )
    ):
        return _n3_case_2(registro)

    # --------------------------------------------------
    # Caso 3: dos cinemáticas sin dip ni rake.
    # --------------------------------------------------

    elif (
        datos["strike"] is not None
        and datos["dip"] is None
        and datos["rake"] is None
        and datos["cine_1"] is not None
        and datos["cine_2"] is not None
    ):
        return _n3_case_3(registro)

    # --------------------------------------------------
    # Estructura no reconocida.
    # --------------------------------------------------

    registro["estado"] = "invalido"
    registro["motivo"] = "estructura_N3_invalida"

    return registro

# ======================================================
# N2
# ======================================================

def _n2_case_1(registro):
    """
    N2 caso 1:
    Strike + dip, sin rake ni cinemáticas.

    Evalúa las restricciones geométricas mediante
    validate_geometry_n2() de norm_geology.py.
    """

    datos = registro["datos"]

    dip = datos["dip"]
    rake = datos["rake"]

    registro["nivel"] = "N2"
    registro["subtipo"] = "plano_sin_rake_ni_cinematica"

    # --------------------------------------------------
    # 1. Comprobar la estructura del registro
    # --------------------------------------------------

    if (
        datos["strike"] is None
        or dip is None
        or rake is not None
        or datos["cine_1"] is not None
        or datos["cine_2"] is not None
    ):
        registro["estado"] = "invalido"
        registro["motivo"] = "estructura_N2_invalida"
        return registro

    # --------------------------------------------------
    # 2. Evaluar las restricciones geométricas N2
    # --------------------------------------------------

    try:
        validate_geometry_n2(
            dip=dip,
            rake=rake,
            valor_cinematic=0,
        )

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    # --------------------------------------------------
    # 3. Resultado
    # --------------------------------------------------

    registro["estado"] = "conforme"
    registro["motivo"] = "sin_rake_ni_informacion_cinematica"

    return registro

# CASOS ESPCIAL UN STRIKE UNA CINEMATICA CASO NUEVO
def _n2_case_2(registro):
    """
    N2 caso 2:
    Strike + una cinemática, sin dip ni rake.
    """

    datos = registro["datos"]

    # Normalizar la posición de la cinemática.
    cine_1, cine_2 = shift_if_missing(
        datos["cine_1"],
        datos["cine_2"],
    )

    datos["cine_1"] = cine_1
    datos["cine_2"] = cine_2

    registro["nivel"] = "N2"
    registro["subtipo"] = "strike_con_una_cinematica"

    # 1. Comprobar la estructura del registro.
    if (
        datos["strike"] is None
        or datos["dip"] is not None
        or datos["rake"] is not None
        or cine_1 is None
        or cine_2 is not None
    ):
        registro["estado"] = "invalido"
        registro["motivo"] = "estructura_N2_caso_2_invalida"
        return registro

    # 2. Obtener el valor cinemático.
    try:
        valor_cinematic = cinematic(cine_1)

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    registro["valor_cinematic"] = valor_cinematic

    # 3. Resultado.
    registro["estado"] = "conforme"
    registro["motivo"] = "sin_dip_ni_rake_con_informacion_cinematica"

    return registro


def _treatment_n2(registro):
    """
    Coordina los tratamientos N2.

    N2 caso 1: strike + dip.
    N2 caso 2: strike + una cinemática.
    """

    datos = registro["datos"]

    # Caso 1: strike + dip, sin rake ni cinemáticas.
    if (
        datos["strike"] is not None
        and datos["dip"] is not None
        and datos["rake"] is None
        and datos["cine_1"] is None
        and datos["cine_2"] is None
    ):
        return _n2_case_1(registro)

    # Caso 2: strike + una cinemática, sin dip ni rake.
    elif (
        datos["strike"] is not None
        and datos["dip"] is None
        and datos["rake"] is None
        and (
            datos["cine_1"] is not None
            or datos["cine_2"] is not None
        )
    ):
        return _n2_case_2(registro)

    registro["estado"] = "invalido"
    registro["motivo"] = "estructura_N2_invalida"

    return registro


# ======================================================
# N1
# ======================================================

def _n1_case_1(registro):
    """
    N1 caso 1:
    Solamente strike.

    Evalúa las restricciones geométricas mediante
    validate_geometry_n1() de norm_geology.py.
    """

    datos = registro["datos"]

    dip = datos["dip"]
    rake = datos["rake"]

    registro["nivel"] = "N1"
    registro["subtipo"] = "solamente_strike"

    # --------------------------------------------------
    # 1. Comprobar la estructura del registro
    # --------------------------------------------------

    if (
        datos["strike"] is None
        or dip is not None
        or rake is not None
        or datos["cine_1"] is not None
        or datos["cine_2"] is not None
    ):
        registro["estado"] = "invalido"
        registro["motivo"] = "estructura_N1_invalida"
        return registro

    # --------------------------------------------------
    # 2. Evaluar las restricciones geométricas N1
    # --------------------------------------------------

    try:
        validate_geometry_n1(
            dip=dip,
            rake=rake,
            valor_cinematic=0,
        )

    except (TypeError, ValueError) as exc:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(exc)
        return registro

    # --------------------------------------------------
    # 3. Resultado
    # --------------------------------------------------

    registro["estado"] = "conforme"
    registro["motivo"] = "orientacion_minima"

    return registro


def _treatment_n1(registro):
    """
    Coordina el tratamiento de registros N1.

    N1 tiene un único caso definido.
    """

    return _n1_case_1(registro)


# ======================================================
# COORDINADOR GENERAL
# ======================================================

def process_registration(registro):
    """
    Aplica el tratamiento correspondiente según la clase N1–N5.

    Recibe un registro previamente normalizado y clasificado.

    No normaliza ni modifica la clasificación inicial,
    excepto cuando existe un autocompletado N4 que
    permite reclasificar el registro como N5.
    """

    clase = registro["clase"]

    # --------------------------------------------------
    # N5
    # --------------------------------------------------

    if clase == "N5":
        return _treatment_n5(registro)

    # --------------------------------------------------
    # N4
    # --------------------------------------------------

    elif clase == "N4":
        return _treatment_n4(registro)

    # --------------------------------------------------
    # N3
    # --------------------------------------------------

    elif clase == "N3":
        return _treatment_n3(registro)

    # --------------------------------------------------
    # N2
    # --------------------------------------------------

    elif clase == "N2":
        return _treatment_n2(registro)

    # --------------------------------------------------
    # N1
    # --------------------------------------------------

    elif clase == "N1":
        return _treatment_n1(registro)

    # --------------------------------------------------
    # SIN DATOS
    # --------------------------------------------------

    elif clase == "INVALID0":
        registro["estado"] = "invalido"
        registro["motivo"] = "ningun_dato_presente"
        registro["nivel"] = None
        return registro

    # --------------------------------------------------
    # CLASE DESCONOCIDA
    # --------------------------------------------------

    else:
        registro["estado"] = "invalido"
        registro["motivo"] = f"clase_no_reconocida: {clase!r}"
        return registro