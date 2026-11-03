import numpy as np
from . import kinematics_logic

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
    Calcula X,Y a partir de datos geométricos
    previamente validados.

    Parámetros
    ----------
    dip : escalar o secuencia
    rake : escalar o secuencia
    valor_cinematic : escalar o secuencia

    Returns
    -------
    x, y : numpy.ndarray
    """

    dip = np.atleast_1d(dip)
    rake = np.atleast_1d(rake)
    valor_cinematic = np.atleast_1d(valor_cinematic)

    # ---------------------------------------------
    # Comprobar longitud
    # ---------------------------------------------

    if not (
        len(dip)
        == len(rake)
        == len(valor_cinematic)
    ):
        raise ValueError(
            "dip, rake y valor_cinematic deben "
            "tener la misma cantidad de elementos."
        )

    xs = []
    ys = []

    for d, r, vc in zip(
        dip,
        rake,
        valor_cinematic
    ):

        y = _dip_to_y(
            d,
            r,
            vc
        )

        x = _rake_to_x(
            d,
            r,
            vc
        )

        xs.append(x)
        ys.append(y)

    return np.array(xs), np.array(ys)


def strike_to_xy(strike, r=1.5):

    strike = np.atleast_1d(strike)

    if np.any((strike < 0) | (strike >= 360)):
        raise ValueError(
            "Strike debe estar entre 0 y 360"
        )

    theta = np.radians(90 - strike)

    x = r * np.cos(theta)
    y = r * np.sin(theta)

    return x, y























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

# puntos dobles
def transform_N3_caso_1(dip, rake):
    """
    Devuelve dos puntos opuestos para N3_caso_1
    """

    if dip is None or rake is None:
        return None

    y1 = 1 - dip / 90
    y2 = -y1

    x0 = 1.0 - (rake / 90.0)
    x01 = 1.0 - (180.0 - rake) / 90.0

    if rake < 90:
        x1, x2 = x0, -x0
    elif rake > 90:
        x1, x2 = -x01, x01
    elif rake == 0:
        x1 = x2 = 0

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

