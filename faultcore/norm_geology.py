def shift_if_missing(cine_1, cine_2):
    """
    Reordena las cinemáticas cuando cine_1 está ausente
    y cine_2 contiene un valor.

    Reglas:
        None, valor -> valor, None
        valor, None -> valor, None
        valor, valor -> valor, valor
        None, None   -> None, None

    No normaliza ni valida los códigos cinemáticos.
    """

    if cine_1 is None and cine_2 is not None:
        return cine_2, None

    return cine_1, cine_2


def validate_cinematic_value(cinematic):
    """
    Valida individualmente un código cinemático.

    Valores permitidos:
        nx, ix, dx, sx, None

    No normaliza aliases.
    No modifica el valor recibido.
    No evalúa combinaciones cinemáticas.
    """

    valores_permitidos = {"nx", "ix", "dx", "sx"}

    if cinematic is None:
        return True

    if not isinstance(cinematic, str):
        raise TypeError(
            f"El valor cinemático debe ser string o None: "
            f"{cinematic!r}"
        )

    if cinematic not in valores_permitidos:
        raise ValueError(
            f"Cinemática no reconocida: {cinematic!r}. "
            f"Valores permitidos: {sorted(valores_permitidos)}."
        )

    return True


def validate_cinematic_combination(cine_1, cine_2):
    """
    Valida la compatibilidad entre dos cinemáticas.

    Reglas:
        - Una sola cinemática es válida.
        - Ninguna cinemática es válida.
        - No se permiten cinemáticas repetidas.
        - No se permiten cinemáticas contrapuestas.
        - Solo se permiten las combinaciones establecidas.

    No normaliza ni modifica los valores recibidos.
    """

    # --------------------------------------------------
    # 1. Validar cada cinemática individualmente
    # --------------------------------------------------

    validate_cinematic_value(cine_1)
    validate_cinematic_value(cine_2)

    # --------------------------------------------------
    # 2. Una o ninguna cinemática
    # --------------------------------------------------

    if cine_1 is None or cine_2 is None:
        return True

    # --------------------------------------------------
    # 3. Impedir repeticiones
    # --------------------------------------------------

    if cine_1 == cine_2:
        raise ValueError(
            f"No puede repetirse la misma cinemática: "
            f"{cine_1} y {cine_2}."
        )

    # --------------------------------------------------
    # 4. Combinaciones permitidas
    # --------------------------------------------------

    permitidas = {
        frozenset(("dx", "nx")),
        frozenset(("dx", "ix")),
        frozenset(("sx", "nx")),
        frozenset(("sx", "ix")),
    }

    if frozenset((cine_1, cine_2)) not in permitidas:
        raise ValueError(
            f"Combinación cinemática inválida: "
            f"{cine_1} + {cine_2}."
        )

    return True


CINE_VALUE = {
    None: 0,
    "nx": 1,
    "ix": -1,
    "dx": 3,
    "sx": -3,
}


def cinematic(cine_1, cine_2=None):
    """
    Convierte una o dos cinemáticas normalizadas
    a su representación numérica.

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

    No normaliza ni modifica los valores recibidos.
    """

    # Validar los valores individuales
    validate_cinematic_value(cine_1)
    validate_cinematic_value(cine_2)

    # Validar la combinación
    validate_cinematic_combination(cine_1, cine_2)

    # Obtener representación numérica
    c1 = CINE_VALUE[cine_1]
    c2 = CINE_VALUE[cine_2]

    return c1 + c2


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


def cinematic_from_value(value):
    """
    Convierte un valor numérico en sus componentes cinemáticos.

    No modifica datos ni realiza normalización geológica.
    """

    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(
            f"El valor cinemático debe ser un entero: {value!r}"
        )

    try:
        return CINE_FROM_VALUE[value]

    except KeyError:
        raise ValueError(
            f"Valor cinemático no reconocido: {value!r}"
        )


def validate_geometry_n5(dip, rake, valor_cinematic):
    """
    Valida las condiciones geométricas y cinemáticas
    correspondientes exclusivamente a registros N5.

    Precondición:
    Los datos ya fueron normalizados y validados
    mediante norm_basic.py.

    Condiciones:
    - dip, rake y valor_cinematic deben estar presentes.
    - dip debe ser diferente de 0.
    - valor_cinematic debe pertenecer a {-4, -2, 2, 4}.

    Restricciones según rake:
    - 0 < rake < 90: valor_cinematic debe ser ±2.
    - 90 < rake < 180: valor_cinematic debe ser ±4.

    Returns:
        True: si la geometría es válida.

    Raises:
        ValueError: si alguna condición no se cumple.
    """

    # 1. Comprobar datos obligatorios
    if dip is None:
        raise ValueError("N5: dip es obligatorio.")

    if rake is None:
        raise ValueError("N5: rake es obligatorio.")

    if valor_cinematic is None:
        raise ValueError("N5: valor_cinematic es obligatorio.")

    # 2. N5 no admite dip horizontal
    if dip == 0:
        raise ValueError(
            "N5: dip = 0° no es permitido para registros "
            "con dos componentes cinemáticas."
        )

    # 3. Validar valores cinemáticos permitidos para N5
    valores_n5 = {-4, -2, 2, 4}

    if valor_cinematic not in valores_n5:
        raise ValueError(
            f"N5: valor_cinematic no permitido: {valor_cinematic}. "
            f"Valores admitidos: {valores_n5}."
        )

    # 4. Validar correspondencia entre rake y cinemática
    if 0 < rake < 90:

        if abs(valor_cinematic) != 2:
            raise ValueError(
                "N5: para 0° < rake < 90°, "
                "valor_cinematic debe ser ±2."
            )

    elif 90 < rake < 180:

        if abs(valor_cinematic) != 4:
            raise ValueError(
                "N5: para 90° < rake < 180°, "
                "valor_cinematic debe ser ±4."
            )

    else:
        raise ValueError(
            f"N5: rake = {rake}° no es permitido. "
            "Los valores 0°, 90° y 180° corresponden "
            "a condiciones que deben evaluarse en otros niveles."
        )

    return True

def validate_geometry_n4_case_1(dip, rake, valor_cinematic):
    """
    Valida la geometría de N4 - Caso 1.

    Datos:
    - Strike
    - Dip
    - Rake
    - Una cinemática

    Reglas:
    - Si dip = 0°: rake entre 0° y 180°,
      exclusivamente Dx o Sx (±3).
    - Si dip > 0°:
      Nx/Ix (±1) requieren rake = 90°.
      Dx/Sx (±3) requieren rake = 0° o 180°.
    """

    if dip is None:
        raise ValueError("N4: dip es obligatorio.")

    if rake is None:
        raise ValueError("N4: rake es obligatorio.")

    if valor_cinematic is None:
        raise ValueError("N4: valor_cinematic es obligatorio.")

    # Validar valores cinemáticos permitidos para N4 - Caso 1
    valores_n4 = {-3, -1, 1, 3}

    if valor_cinematic not in valores_n4:
        raise ValueError(
            f"N4 - Caso 1: valor_cinematic no permitido: "
            f"{valor_cinematic}. Valores admitidos: {valores_n4}."
        )

    # Caso especial: plano horizontal
    if dip == 0:

        if valor_cinematic not in {-3, 3}:
            raise ValueError(
                "N4: cuando dip = 0°, "
                "solo se permiten las cinemáticas Dx o Sx (±3)."
            )

        return True

    # Caso general: dip > 0°
    if valor_cinematic in {-1, 1}:

        if rake != 90:
            raise ValueError(
                "N4: Nx/Ix requieren rake = 90°."
            )

    elif valor_cinematic in {-3, 3}:

        if rake not in {0, 180}:
            raise ValueError(
                "N4: Dx/Sx requieren rake = 0° o 180°."
            )

    else:
        raise ValueError(
            f"N4: valor_cinematic no permitido: {valor_cinematic}. "
            "Se esperan ±1 o ±3."
        )

    return True


# PARA N4_CASO 2 AUTOCOMPLETADO

def infer_missing_cinematic(rake, valor_cinematic):
    """
    Infiere el valor cinemático combinado a partir
    del rake y una cinemática conocida.

    No modifica registros ni asigna clasificaciones.
    """

    if 0 < rake < 90:

        if valor_cinematic in (1, -3):
            return -2

        elif valor_cinematic in (-1, 3):
            return 2

    elif 90 < rake < 180:

        if valor_cinematic in (1, 3):
            return 4

        elif valor_cinematic in (-1, -3):
            return -4

    return None

def validate_geometry_n4_case_3(dip, rake, valor_cinematic):
    """
    Valida N4 - Caso 3.

    Datos:
    - Strike
    - Dip
    - Dos cinemáticas compatibles.
    - Rake ausente.

    Restricciones:
    - Dip obligatorio y diferente de 0°.
    - Rake debe estar ausente.
    - valor_cinematic debe pertenecer a {-4, -2, 2, 4}.
    """

    if dip is None:
        raise ValueError("N4 - Caso 3: dip es obligatorio.")

    if rake is not None:
        raise ValueError(
            "N4 - Caso 3: rake debe estar ausente."
        )

    if dip == 0:
        raise ValueError(
            "N4 - Caso 3: dip = 0° no permite dos cinemáticas."
        )

    valores_n4_caso_3 = {-4, -2, 2, 4}

    if valor_cinematic not in valores_n4_caso_3:
        raise ValueError(
            "N4 - Caso 3: se requieren dos cinemáticas "
            "compatibles. Valores permitidos: ±2 y ±4."
        )

    return True

def validate_geometry_n3_case_1(dip, rake, valor_cinematic):
    """
    N3 - Caso 1:
    Strike + dip + rake, sin información cinemática.
    """

    if dip is None:
        raise ValueError("N3 - Caso 1: dip es obligatorio.")

    if rake is None:
        raise ValueError("N3 - Caso 1: rake es obligatorio.")

    if valor_cinematic != 0:
        raise ValueError(
            "N3 - Caso 1: no se permiten datos cinemáticos."
        )

    return True

def validate_geometry_n3_case_2(dip, rake, valor_cinematic):
    """
    N3 - Caso 2:
    Strike + dip + una cinemática, sin rake.

    Restricciones:
    - Dip = 0°: solo Dx o Sx (±3).
    - Dip > 0°: Nx, Ix, Dx o Sx (±1, ±3).
    """

    if dip is None:
        raise ValueError("N3 - Caso 2: dip es obligatorio.")

    if rake is not None:
        raise ValueError("N3 - Caso 2: rake debe estar ausente.")

    if valor_cinematic is None:
        raise ValueError(
            "N3 - Caso 2: valor_cinematic es obligatorio."
        )

    if dip == 0:

        if valor_cinematic not in {-3, 3}:
            raise ValueError(
                "N3 - Caso 2: con dip = 0°, "
                "solo se permiten valores cinemáticos ±3."
            )

    elif valor_cinematic not in {-3, -1, 1, 3}:
        raise ValueError(
            "N3 - Caso 2: valor_cinematic debe ser "
            "±1 o ±3."
        )

    return True

def validate_geometry_n2(dip, rake, valor_cinematic):
    """
    N2:
    Strike + dip.

    Restricciones:
    - Dip obligatorio.
    - Rake ausente.
    - Sin información cinemática.
    """

    if dip is None:
        raise ValueError("N2: dip es obligatorio.")

    if rake is not None:
        raise ValueError("N2: rake debe estar ausente.")

    if valor_cinematic != 0:
        raise ValueError(
            "N2: no se permiten datos cinemáticos."
        )

    return True

def validate_geometry_n1(dip, rake, valor_cinematic):
    """
    N1:
    Solamente strike.

    Restricciones:
    - Dip ausente.
    - Rake ausente.
    - Sin información cinemática.
    """

    if dip is not None:
        raise ValueError("N1: dip debe estar ausente.")

    if rake is not None:
        raise ValueError("N1: rake debe estar ausente.")

    if valor_cinematic != 0:
        raise ValueError(
            "N1: no se permiten datos cinemáticos."
        )

    return True