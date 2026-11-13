import numpy as np


def changes_magnitud_rake(dip, rake, valor_cinematic):
    # Caso vertical puro
    if rake == 90:
        return 0.0

    # Strike–slip puro
    if abs(valor_cinematic) == 3 and rake in (0, 180):
        return 1.0

    # Dip = 0, strike–slip oblicuo
    if dip == 0 and abs(valor_cinematic) == 3:
        if rake < 90:
            return 1.0 - (rake / 90.0)
        elif rake > 90:
            return 1.0 - (180.0 - rake) / 90.0

    # Casos oblicuos dip–slip
    if valor_cinematic in (2, -2):
        return 1.0 - (rake / 90.0)

    elif valor_cinematic in (4, -4):
        return 1.0 - (180.0 - rake) / 90.0

    return 0.0


def _rake_to_x(dip, rake, valor_cinematic):

    mag = changes_magnitud_rake(
        dip,
        rake,
        valor_cinematic
    )

    # Sinestral / componente negativa
    if valor_cinematic < 0:
        return -mag

    # Dextral / componente positiva
    return +mag


def _dip_to_y(dip, rake, valor_cinematic):

    y_mag = 1 - dip / 90

    # ---------------------------------------------
    # Rake = 0° o 180°
    # ---------------------------------------------

    if valor_cinematic > 0:

        if rake == 180:
            return -y_mag

        elif rake == 0:
            return y_mag

    elif valor_cinematic < 0:

        if rake == 180:
            return y_mag

        elif rake == 0:
            return -y_mag

    # ---------------------------------------------
    # Dip = 0°
    # Caso especial
    # ---------------------------------------------

    if dip == 0:

        if valor_cinematic > 0:
            return y_mag if rake < 90 else -y_mag

        if valor_cinematic < 0:
            return -y_mag if rake < 90 else +y_mag

        # valor_cinematic = 0
        return 0.0

    # ---------------------------------------------
    # Orientación vertical del movimiento
    # ---------------------------------------------

    # Ix arriba | Nx abajo
    if valor_cinematic in (-1, 2, -4):
        return +y_mag

    # Los demás
    return -y_mag


def dip_rake_to_xy(dip, rake, valor_cinematic):
    """
    Calcula las coordenadas X,Y de un registro individual.

    Los datos recibidos corresponden a un registro
    previamente procesado por FAULTCORE.

    Parámetros
    ----------
    dip : float
    rake : float
    valor_cinematic : float

    Returns
    -------
    x, y : float
        Coordenadas cartesianas.
    """

    y = _dip_to_y(
        dip,
        rake,
        valor_cinematic
    )

    x = _rake_to_x(
        dip,
        rake,
        valor_cinematic
    )

    return float(x), float(y)


def strike_to_xy(strike, r=1.5):
    """
    Convierte un strike en coordenadas cartesianas X, Y.

    Parámetros
    ----------
    strike : float
        Orientación del strike en grados.
        Valor previamente validado por FAULTCORE.

    r : float, opcional
        Radio de representación. Por defecto 1.5.

    Returns
    -------
    x, y : float
        Coordenadas cartesianas.
    """

    theta = np.radians(90 - strike)

    x = r * np.cos(theta)
    y = r * np.sin(theta)

    return float(x), float(y)


#caso 3
def transform_N4_caso_3(dip, valor_cinematico):
    """
    Devuelve los puntos (0, y) → (x1, y)
    para el caso N4 con rake ausente y dos cinemáticas.
    """

    if dip is None or valor_cinematico is None:
        return None

    y_mag = 1 - dip / 90

    if valor_cinematico in (-2, 4):
        y = -y_mag
    elif valor_cinematico in (-4, 2):
        y = y_mag
    else:
        return None

    if valor_cinematico in (2, 4):
        x1 = +1
    elif valor_cinematico in (-2, -4):
        x1 = -1
    else:
        return None

    return [(0, y), (x1, y)]

def transform_N3_caso_1(dip, rake):

    if dip is None or rake is None:
        return None

    y1 = 1.0 - dip / 90.0
    y2 = -y1

    # Único caso donde ambos puntos coinciden en el centro
    if dip == 90 and rake == 90:
        return (0.0, 0.0), (0.0, 0.0)

    # Fórmulas originales para X
    x0 = 1.0 - (rake / 90.0)
    x01 = 1.0 - (180.0 - rake) / 90.0

    if rake < 90:
        x1, x2 = x0, -x0

    elif rake > 90:
        x1, x2 = -x01, x01

    else:
        x1 = x2 = 0.0

    return (x1, y1), (x2, y2)


# N3 caso 2
def transform_N3_case2(dip, valor):
    y1 = 1 - dip / 90
    y2 = -y1

    # dip-slip → dos rectas horizontales
    if valor in (1, -1):
        y = y2 if valor == 1 else y1
        return (
            [(0, y), (1, y)],
            [(0, y), (-1, y)]
        )

    # strike-slip → dos rectas simétricas
    if valor in (3, -3):
        x = 1 if valor == 3 else -1
        return (
            [(0, y1), (x, y1)],
            [(0, y2), (x, y2)]
        )

def center_segment(p1, p2):
    """
    Calcula el punto medio de un segmento.
    """
    x1, y1 = p1
    x2, y2 = p2

    xc = (x1 + x2) / 2.0
    yc = (y1 + y2) / 2.0

    return xc, yc

#CASOS ESPECIALES N2 Y N3

def get_cinematic_point_position(
        cinematic,
        radius,
        offset=0.15,
        distance_horizontal=0.12,
        distance_vertical=0.08
):
    """
    Calcula la posición de un punto auxiliar
    respecto a una etiqueta cinemática.

    DX: derecha
    SX: izquierda
    IX: arriba
    NX: abajo
    """

    cinematic = str(cinematic).strip().lower()

    positions = {
        "dx": (radius + offset + distance_horizontal, 0),
        "sx": (-radius - offset - distance_horizontal, 0),
        "ix": (0, radius + offset + distance_vertical),
        "nx": (0, -radius - offset - distance_vertical)
    }

    return positions.get(cinematic)



def get_cinematic_pair_point_positions(
        cine_1,
        cine_2,
        radius=1.0,
        offset=0.15
):
    """
    Calcula las posiciones de dos puntos auxiliares
    para N3 especial.

    Cada punto se desplaza en la dirección
    correspondiente a la otra cinemática.

    El orden de cine_1 y cine_2 no altera
    las posiciones resultantes.
    """

    cine_1 = str(cine_1).strip().lower()
    cine_2 = str(cine_2).strip().lower()

    directions = {
        "dx": (1, 0),
        "sx": (-1, 0),
        "ix": (0, 1),
        "nx": (0, -1)
    }

    if cine_1 not in directions or cine_2 not in directions:
        return None

    # Posiciones base de cada etiqueta.
    base_1 = get_cinematic_point_position(
        cine_1,
        radius=radius,
        offset=0
    )

    base_2 = get_cinematic_point_position(
        cine_2,
        radius=radius,
        offset=0
    )

    # Desplazamiento según la otra cinemática.
    dx_1, dy_1 = directions[cine_2]
    dx_2, dy_2 = directions[cine_1]

    punto_1 = (
        base_1[0] + dx_1 * offset,
        base_1[1] + dy_1 * offset
    )

    punto_2 = (
        base_2[0] + dx_2 * offset,
        base_2[1] + dy_2 * offset
    )

    return punto_1, punto_2
