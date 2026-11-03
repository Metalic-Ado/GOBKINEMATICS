import numpy as np


# ============================================================
# LÓGICA 1 — CODIFICACIÓN NUMÉRICA DE LA CINEMÁTICA
# ============================================================

CINE_VALUE = {
    None: 0,
    "nx": 1,
    "ix": -1,
    "dx": 3,
    "sx": -3,
}


def cinematic(cine_1, cine_2=None):
    """
    Convierte las cinemáticas normalizadas a un valor numérico.

    Valores individuales:

        None ->  0
        nx   -> +1
        ix   -> -1
        dx   -> +3
        sx   -> -3

    Combinaciones:

        nx + dx -> +4
        nx + sx -> -2
        ix + dx -> +2
        ix + sx -> -4
    """

    # --------------------------------------------------------
    # Cinemática 1
    # --------------------------------------------------------

    try:
        c1 = CINE_VALUE[cine_1]
    except KeyError:
        raise ValueError(
            f"Cinemática no normalizada o no reconocida: {cine_1!r}"
        )

    # --------------------------------------------------------
    # Cinemática 2
    # --------------------------------------------------------

    try:
        c2 = CINE_VALUE[cine_2]
    except KeyError:
        raise ValueError(
            f"Cinemática no normalizada o no reconocida: {cine_2!r}"
        )

    # --------------------------------------------------------
    # Valor cinemático
    # --------------------------------------------------------

    return c1 + c2

# QUE HACER CON VALORES SIN DATOS

# ============================================================
# LÓGICA 1 — INVERSA DE LA CODIFICACIÓN CINEMÁTICA
# ============================================================

def cinematic_from_value(value):
    """
    Convierte el valor numérico de la cinemática
    nuevamente en sus componentes canónicos.

    Retorna:
        (cine_1, cine_2)
    """

    CINE_FROM_VALUE = {
        0: (None, None),

        1: ("nx", None),
        -1: ("ix", None),

        3: ("dx", None),
        -3: ("sx", None),

        4: ("nx", "dx"),
        -2: ("nx", "sx"),

        2: ("ix", "dx"),
        -4: ("ix", "sx"),
    }

    try:
        return CINE_FROM_VALUE[value]
    except KeyError:
        raise ValueError(
            f"Valor cinemático no reconocido: {value!r}"
        )



def validate_geometry(dip, rake, valor_cinematic):
    """
    Valida la compatibilidad geométrica entre dip, rake
    y valor_cinematic.

    Esta función NO clasifica N1-N5 y NO modifica los datos.
    Solo determina si la combinación geométrica es válida.

    Reglas:

    1. dip = 0°
       - Caso especial.
       - Se permite cualquier rake entre 0° y 180°.
       - Se permite valor_cinematic = 0.
       - No se permiten Nx, Ix ni combinaciones que los contengan.
       - Dx/Sx son válidos.

    2. 0° < dip < 90°
       - valor ±2 -> 0° <= rake < 90°
       - valor ±4 -> 90° < rake <= 180°
       - rake = 0°   -> Dx/Sx
       - rake = 90°  -> Nx/Ix
       - rake = 180° -> Dx/Sx

    3. dip = 90°
       - rake = 0°   -> Dx/Sx
       - 0° < rake < 90° -> ±2
       - rake = 90°  -> Nx/Ix
       - 90° < rake < 180° -> ±4
       - rake = 180° -> Dx/Sx
    """

    # ---------------------------------------------------------
    # Validación básica
    # ---------------------------------------------------------

    if dip is None:
        raise ValueError("Dip no puede ser None en validate_geometry().")

    if rake is None:
        raise ValueError("Rake no puede ser None en validate_geometry().")

    if valor_cinematic is None:
        raise ValueError(
            "valor_cinematic no puede ser None en validate_geometry()."
        )

    # ---------------------------------------------------------
    # Valores permitidos de la cinemática
    # ---------------------------------------------------------

    valores_validos = {-4, -3, -2, -1, 0, 1, 2, 3, 4}

    if valor_cinematic not in valores_validos:
        raise ValueError(
            f"Valor cinemático no reconocido: {valor_cinematic!r}"
        )

    # ---------------------------------------------------------
    # DIP = 0°
    # CASO ESPECIAL
    # ---------------------------------------------------------

    if dip == 0:

        # Nx / Ix y combinaciones que los contienen
        if valor_cinematic in (-4, -2, -1, 1, 2, 4):
            raise ValueError(
                f"Geometría incompatible: dip=0° no permite "
                f"valor_cinematic={valor_cinematic}."
            )

        # 0, Dx y Sx son permitidos
        return True

    # ---------------------------------------------------------
    # 0° < DIP < 90°
    # ---------------------------------------------------------

    if 0 < dip < 90:

        # Rake = 0° -> strike-slip
        if rake == 0:
            if valor_cinematic not in (-3, 3):
                raise ValueError(
                    f"Geometría incompatible: con dip={dip}° y "
                    f"rake=0° solo se permite Dx/Sx."
                )
            return True

        # Rake = 90° -> dip-slip puro
        if rake == 90:
            if valor_cinematic not in (-1, 1):
                raise ValueError(
                    f"Geometría incompatible: con dip={dip}° y "
                    f"rake=90° solo se permite Nx/Ix."
                )
            return True

        # Rake = 180° -> strike-slip
        if rake == 180:
            if valor_cinematic not in (-3, 3):
                raise ValueError(
                    f"Geometría incompatible: con dip={dip}° y "
                    f"rake=180° solo se permite Dx/Sx."
                )
            return True

        # Rake entre 0° y 90°
        if 0 < rake < 90:
            if valor_cinematic not in (-2, 2):
                raise ValueError(
                    f"Geometría incompatible: con dip={dip}° y "
                    f"0° < rake < 90° solo se permite "
                    f"valor_cinematic=±2."
                )
            return True

        # Rake entre 90° y 180°
        if 90 < rake < 180:
            if valor_cinematic not in (-4, 4):
                raise ValueError(
                    f"Geometría incompatible: con dip={dip}° y "
                    f"90° < rake < 180° solo se permite "
                    f"valor_cinematic=±4."
                )
            return True

    # ---------------------------------------------------------
    # DIP = 90°
    # ---------------------------------------------------------

    if dip == 90:

        # Rake = 0°
        if rake == 0:
            if valor_cinematic not in (-3, 3):
                raise ValueError(
                    "Geometría incompatible: con dip=90° y "
                    "rake=0° solo se permite Dx/Sx."
                )
            return True

        # Rake = 90°
        if rake == 90:
            if valor_cinematic not in (-1, 1):
                raise ValueError(
                    "Geometría incompatible: con dip=90° y "
                    "rake=90° solo se permite Nx/Ix."
                )
            return True

        # Rake = 180°
        if rake == 180:
            if valor_cinematic not in (-3, 3):
                raise ValueError(
                    "Geometría incompatible: con dip=90° y "
                    "rake=180° solo se permite Dx/Sx."
                )
            return True

        # 0° < rake < 90°
        if 0 < rake < 90:
            if valor_cinematic not in (-2, 2):
                raise ValueError(
                    "Geometría incompatible: con dip=90° y "
                    "0° < rake < 90° solo se permite ±2."
                )
            return True

        # 90° < rake < 180°
        if 90 < rake < 180:
            if valor_cinematic not in (-4, 4):
                raise ValueError(
                    "Geometría incompatible: con dip=90° y "
                    "90° < rake < 180° solo se permite ±4."
                )
            return True

    # ---------------------------------------------------------
    # Si llegó aquí, la combinación no fue reconocida
    # ---------------------------------------------------------

    raise ValueError(
        f"Combinación geométrica no contemplada: "
        f"dip={dip}, rake={rake}, "
        f"valor_cinematic={valor_cinematic}"
    )


def validate_complete_faults(data):
    """
    Valida un conjunto de fallas completas/necesarias para el
    cálculo geométrico y matemático.

    Se espera recibir datos previamente normalizados mediante
    normalize_basic_data().

    Agrega el campo:
        valor_cinematic

    No clasifica N1-N5.
    No modifica los datos originales.
    """

    required_fields = (
        "strike",
        "dip",
        "rake",
        "cine_1",
        "cine_2",
    )

    # ---------------------------------------------------------
    # Comprobar estructura del diccionario
    # ---------------------------------------------------------

    if not isinstance(data, dict):
        raise TypeError(
            "data debe ser un diccionario."
        )

    missing = [
        field for field in required_fields
        if field not in data
    ]

    if missing:
        raise ValueError(
            f"Faltan campos requeridos: {missing}"
        )

    # ---------------------------------------------------------
    # Comprobar que todos tengan la misma longitud
    # ---------------------------------------------------------

    lengths = {
        field: len(data[field])
        for field in required_fields
    }

    if len(set(lengths.values())) != 1:
        raise ValueError(
            "Los campos no tienen la misma cantidad de registros: "
            f"{lengths}"
        )

    n = lengths["strike"]

    # ---------------------------------------------------------
    # Crear nuevo contenedor
    # No modificamos data
    # ---------------------------------------------------------

    result = {
        "strike": list(data["strike"]),
        "dip": list(data["dip"]),
        "rake": list(data["rake"]),
        "cine_1": list(data["cine_1"]),
        "cine_2": list(data["cine_2"]),
        "valor_cinematic": [],
    }

    # ---------------------------------------------------------
    # Procesar cada falla
    # ---------------------------------------------------------

    for i in range(n):

        strike = result["strike"][i]
        dip = result["dip"][i]
        rake = result["rake"][i]
        cine_1 = result["cine_1"][i]
        cine_2 = result["cine_2"][i]

        # ---------------------------------------------
        # Obtener valor numérico de la cinemática
        # ---------------------------------------------

        valor = cinematic(cine_1, cine_2)

        # ---------------------------------------------
        # Validar geometría
        # ---------------------------------------------

        try:
            validate_geometry(
                dip=dip,
                rake=rake,
                valor_cinematic=valor
            )

        except ValueError as e:
            raise ValueError(
                f"Error geométrico en registro {i + 1}: {e}"
            ) from e

        # ---------------------------------------------
        # Guardar valor cinemático
        # ---------------------------------------------

        result["valor_cinematic"].append(valor)

    return result








def _normalize_cine_value(val):
    if val in (None, "", " ", 0,"0"):
        return None
    return val

# VALORES PARA VARIOS DATOS
def cinematic_array(cine_1, cine_2=None):
    """
    Aplica cinematic() elemento a elemento.
    Soporta escalares o listas.
    """

    c1 = np.atleast_1d(cine_1)
    c2 = np.atleast_1d(cine_2) if cine_2 is not None else np.full_like(c1, None, dtype=object)

    if c1.size != c2.size:
        raise ValueError("cine_1 y cine_2 deben tener la misma longitud")

    result = []

    for a, b in zip(c1, c2):
        a = _normalize_cine_value(a)
        b = _normalize_cine_value(b)
        result.append(cinematic(a, b))

    return np.array(result)


########################################################################################################################
###############################################  CLASIFICADOR DE FALLAS ################################################
########################################################################################################################

# CLASIFICADOR DE FALLAS, SI SON ACEPTABLES O NO PARA EL ANALISIS
# RESTRINGIR DATOS VACIOS, datos que tengan -, "", u otros valors, colocarle None
# RESTRINGIR DATOS DE ENTRADA osea valorse de strike dip y rake y valores cinematicos



from . import kinematics_norm

def clasify_for_items(strike, dip, rake, cine_1, cine_2):
    """
    Clasifica cada registro según la cantidad de datos presentes.

    N5: 5 datos presentes.
    N4: 4 datos presentes.
    N3: 3 datos presentes.
    N2: 2 datos presentes.
    N1: 1 dato presente.
    INVALID0: ningún dato presente.

    Esta función no evalúa la compatibilidad geométrica ni
    elimina registros.

    Un registro sin strike se conserva, pero se marca como inválido.
    Las diferencias de longitud y los errores de tipo detienen
    el procesamiento del conjunto.
    """

    # --------------------------------------------------
    # 1. Validar estructura y conservar las filas
    # --------------------------------------------------
    data = kinematics_norm.validate_input_lengths(
        strike=strike,
        dip=dip,
        rake=rake,
        cine_1=cine_1,
        cine_2=cine_2,
    )

    # --------------------------------------------------
    # 2. Normalizar valores básicos
    # --------------------------------------------------
    data = {
        field: [
            kinematics_norm.normalize_value(value)
            for value in values
        ]
        for field, values in data.items()
    }

    # --------------------------------------------------
    # 3. Validar tipos, sin evaluar geometría
    # --------------------------------------------------
    kinematics_norm.validate_data_types(data)

    # --------------------------------------------------
    # 4. Clasificar cada registro por datos presentes
    # --------------------------------------------------
    campos = (
        "strike",
        "dip",
        "rake",
        "cine_1",
        "cine_2",
    )

    resultados = []

    n_registros = len(data["strike"])

    for i in range(n_registros):

        registro_datos = {
            campo: data[campo][i]
            for campo in campos
        }

        n_valid = sum(
            valor is not None
            for valor in registro_datos.values()
        )

        if n_valid == 5:
            clase = "N5"
        elif n_valid == 4:
            clase = "N4"
        elif n_valid == 3:
            clase = "N3"
        elif n_valid == 2:
            clase = "N2"
        elif n_valid == 1:
            clase = "N1"
        else:
            clase = "INVALID0"

        # El strike siempre es obligatorio.
        if registro_datos["strike"] is None:
            estado = "invalido"
            motivo = "strike_ausente"
        else:
            estado = "sin_evaluar"
            motivo = None

        resultados.append({
            "id": i,
            "clase": clase,
            "datos": registro_datos,
            "estado": estado,
            "motivo": motivo,
        })

    return resultados


def _treatment_n5(registro):
    """
    Evalúa la conformidad geométrica de una falla N5.

    Recibe un registro previamente normalizado y clasificado.
    No elimina ni reclasifica el registro.
    No modifica sus datos originales.
    """

    datos = registro["datos"]

    dip = datos["dip"]
    rake = datos["rake"]
    cine_1 = datos["cine_1"]
    cine_2 = datos["cine_2"]

    # N5 debe contener sus cinco datos.
    campos = ("strike", "dip", "rake", "cine_1", "cine_2")

    if any(datos[campo] is None for campo in campos):
        registro["estado"] = "invalido"
        registro["motivo"] = "N5_con_datos_ausentes"
        registro["nivel"] = "N5"
        return registro

    # Obtener la codificación cinemática ya definida.
    valor_cinematic = int(
        cinematic_array(cine_1, cine_2)[0]
    )

    registro["nivel"] = "N5"
    registro["valor_cinematic"] = valor_cinematic

    # Evaluar exclusivamente las restricciones geométricas de N5.
    try:
        validate_geometry(
            dip=dip,
            rake=rake,
            valor_cinematic=valor_cinematic,
        )
    except ValueError as e:
        registro["estado"] = "inconforme"
        registro["motivo"] = str(e)
        return registro

    registro["estado"] = "conforme"
    registro["motivo"] = None

    return registro


# CUANDO SE TIENEN SOLO 4 DATOS
# Normalizacion de la cinematica si existe un None en Cine 1 y no es Cine 2, se intercambia para que Cine 1 tenga el valor de Cine 2


# _______________________________________
# N4


def _identify_subtype_n4(registro):
    """
    Clasifica el subtipo de un registro N4.

    Requisitos:
    - N4 contiene exactamente cuatro datos presentes.
    - strike y dip deben estar presentes.
    - El orden de las cinemáticas ya fue normalizado.
    """
    datos = registro["datos"]

    strike = datos["strike"]
    dip = datos["dip"]
    rake = datos["rake"]
    cine_1 = datos["cine_1"]
    cine_2 = datos["cine_2"]

    # N4: falta rake y existen las dos cinemáticas.
    if (
        strike is not None
        and dip is not None
        and rake is None
        and cine_1 is not None
        and cine_2 is not None
    ):
        subtipo = "sin_rake_dos_cinematicas"

    # N4: existe rake y solo hay una cinemática.
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


# Cuando existe 4 valores y un None, Existe 3 clasos posibles:
# 1 Cuando Cine 2 es Nones, pero solo existe 4 valores
# 2 Cuando Cine 2 es None, pero existe 5 valores (osea que el cine 2 puede ser autocompletado)
# 3 Cuando el rake es None


def _n4_case_1(registro):
    datos = registro["datos"]

    dip = datos["dip"]
    rake = datos["rake"]
    cine = datos["cine_1"]

    valor = int(cinematic_array(cine, None)[0])
    conforme = False
    motivo = None

    # Nx o Ix → dip-slip puro
    if valor in (1, -1):
        if dip != 0 and rake == 90:
            conforme = True
            motivo = "dip-slip_puro"

# Dx o Sx → strike-slip puro
    elif valor in (3, -3):
        if (dip not in (0, 90)) and (rake in (0, 180)):
            conforme = True
            motivo = "strike-slip_puro"

        # Plano horizontal
        elif dip == 0:
            conforme = True
            motivo = "plano_horizontal"

    registro["estado"] = "conforme" if conforme else "inconforme"
    registro["valor_cinematico"] = valor
    registro["modo"] = "N4_caso_1"
    registro["motivo"] = motivo

    return registro

# Una cinematica pero falta completar una


def _n4_case_2(registro):
    datos = registro["datos"]

    dip = datos["dip"]
    rake = datos["rake"]
    cine = datos["cine_1"]

    valor = int(cinematic_array(cine, None)[0])

    if dip is None or rake is None:
        registro["estado"] = "invalido"
        registro["motivo"] = "datos_insuficientes_para_autocompletar"
        return registro

    new_valor = None

    if 0 < rake < 90:
        if valor in (1, -3):
            new_valor = -2
        elif valor in (-1, 3):
            new_valor = 2

    elif 90 < rake < 180:
        if valor in (1, 3):
            new_valor = 4
        elif valor in (-1, -3):
            new_valor = -4

    # Si no se puede inferir la cinemática, no autocompletar.
    if new_valor is None:
        registro["estado"] = "inconforme"
        registro["motivo"] = "cinematica_no_inferible"
        return registro

    cine1, cine2 = cinematic_from_value(new_valor)

    datos["cine_1"] = cine1
    datos["cine_2"] = cine2

    registro["clase"] = "N5"
    registro["origen"] = "N4_autocompletado"

    return _treatment_n5(registro)

# no rake, pero dos cinematicas si
def _n4_case_3(registro):
    datos = registro["datos"]

    dip = datos["dip"]

    # Rake ausente + dos cinemáticas
    if dip == 0:
        registro["estado"] = "inconforme"
        registro["motivo"] = "rake_ausente_plano_degenerado"
    else:
        registro["estado"] = "cuasi_conforme"
        registro["motivo"] = "rake_ausente"

    return registro


def _treatment_n4(registro):
    """
    Coordina el tratamiento de los subtipos N4.

    El orden de las cinemáticas ya debe estar normalizado
    antes de llegar a esta función.
    """
    registro = _identify_subtype_n4(registro)
    subtipo = registro["subtipo"]

    if subtipo == "sin_rake_dos_cinematicas":
        return _n4_case_3(registro)

    elif subtipo == "una_cinematica":
        # Primero evalúa si la cinemática existente
        # es suficiente para clasificar el registro.
        resultado = _n4_case_1(registro.copy())

        if resultado["estado"] == "conforme":
            return resultado

        # Si no es suficiente, intenta completar la
        # cinemática usando el rake y las reglas N4.
        return _n4_case_2(registro)

    else:
        registro["estado"] = "invalido"
        registro["motivo"] = "estructura_N4_invalida"
        return registro


def _treatment_n3(registro):
    datos = registro["datos"]

    strike = datos["strike"]
    dip = datos["dip"]
    rake = datos["rake"]
    cine_1 = datos["cine_1"]
    cine_2 = datos["cine_2"]

    # Caso 1: geometría pura, sin cinemáticas
    if (
        strike is not None
        and dip is not None
        and rake is not None
        and cine_1 is None
        and cine_2 is None
    ):
        registro["estado"] = "cuasi_conforme"
        registro["modo"] = "N3_caso_1"
        return registro

    # Caso 2: plano sin rake y con una cinemática
    if (
        strike is not None
        and dip is not None
        and rake is None
        and cine_1 is not None
        and cine_2 is None
    ):
        registro["estado"] = "cuasi_conforme"
        registro["modo"] = "N3_caso_2"
        return registro

    # Cualquier otra estructura no corresponde a los casos N3 definidos
    registro["estado"] = "invalido"
    registro["modo"] = "N3_estructura_invalida"
    return registro


def _treatment_n2(registro):
    registro["nivel"] = "N2"
    registro["modo"] = "N2_caso_unico"
    registro["estado"] = "cuasi_conforme"
    registro["motivo"] = "plano_sin_cinematica"
    return registro


def _treatment_n1(registro):
    registro["nivel"] = "N1"
    registro["modo"] = "N1_caso_unico"
    registro["estado"] = "cuasi_conforme"
    registro["motivo"] = "orientacion_minima"
    return registro


def process_registration(registro):
    """
    Aplica el tratamiento según la clase N1–N5
    y devuelve el registro tratado.
    """
    clase = registro["clase"]

    if clase == "N5":
        registro["nivel"] = "N5"
        return _treatment_n5(registro)

    elif clase == "N4":
        registro["nivel"] = "N4"
        return _treatment_n4(registro)

    elif clase == "N3":
        registro["nivel"] = "N3"
        return _treatment_n3(registro)

    elif clase == "N2":
        return _treatment_n2(registro)

    elif clase == "N1":
        return _treatment_n1(registro)

    elif clase == "INVALID0":
        registro["estado"] = "invalido"
        registro["modo"] = "sin_datos"
        registro["motivo"] = "ningun_dato_presente"
        return registro

    else:
        registro["estado"] = "invalido"
        registro["modo"] = "clase_desconocida"
        registro["motivo"] = f"clase_no_reconocida: {clase!r}"
        return registro
