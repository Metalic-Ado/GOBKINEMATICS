import numpy as np
from GOBESTEREONET import GobFallas2 as gf2


def cinematic(cine_1, cine_2=None):

    KIN_MAP = {
        "Nx": 1, "Ix": -1, "Dx": 3, "Sx": -3,
        1: 1, -1: -1, 3: 3, -3: -3,
        "NX": 1, "IX": -1, "DX": 3, "SX": -3,
        "Normal": 1, "Inverse": -1, "Dextral": 3, "Sinestral": -3,
        "nx": 1, "ix": -1, "dx": 3, "sx": -3
    }

    cine_1 = _normalize_cine_value(cine_1)
    cine_2 = _normalize_cine_value(cine_2)

    # Reordenar: si cine_1 es None y cine_2 no, intercambiar
    if cine_1 is None and cine_2 is not None:
        cine_1, cine_2 = cine_2, None

    # Caso totalmente vacío
    if cine_1 is None and cine_2 is None:
        return 0
    """
    Resuelve la combinación cinemática.

    Devuelve:
        valor entero representando la cinemática combinada

    Reglas:
    - No se permiten duplicados
    - No se permiten opuestos del mismo eje
    - Puede existir solo una cinemática
    """

    # ---------------------------
    # Normalización
    # ---------------------------
    try:
        c1 = KIN_MAP[cine_1]
        c2 = KIN_MAP[cine_2] if cine_2 is not None else None
    except KeyError:
        raise ValueError("Cinemática inválida")

    # ---------------------------
    # Un solo valor (casos especiales)
    # ---------------------------
    if c2 is None:
        return c1

    # ---------------------------
    # No duplicados
    # ---------------------------
    if c1 == c2:
        raise ValueError("No puede haber dos cinematicas iguales")

    # ---------------------------
    # No opuestos del mismo eje
    # ---------------------------
    if abs(c1) == abs(c2):
        raise ValueError("Cinemáticas opuestas incompatibles")

    # ---------------------------
    # Validación de ejes
    # ---------------------------
    axes = {abs(c1), abs(c2)}
    if axes != {1, 3}:
        raise ValueError("Combinación cinemática inválida")

    # ---------------------------
    # Resultado combinado
    # ---------------------------
    return c1 + c2

# QUE HACER CON VALORES SIN DATOS

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

# CINEMATICA INVERSA
def cinematic_from_value(valor):
    """
    Convierte un valor cinemático compuesto (±2, ±4)
    en (cine_1, cine_2)
    """

    if valor == 4:
        return "Nx", "Dx"

    elif valor == -2:
        return "Nx", "Sx"

    elif valor == 2:
        return "Ix", "Dx"

    elif valor == -4:
        return "Ix", "Sx"

    else:
        raise ValueError(f"Valor cinemático no invertible: {valor}")



# normal 1 e inversa -1, dextral 3 y sinestral -3, Nx + Dx =  4, Nx + Sx = -2, Ix + Dx = 2, Ix + Sx = - 4
def _cinematic_main(cine_1, cine_2 = None):
    cine_1, cine_2 =  np.atleast_1d(cine_1, cine_2)
    valor_cinematic = cinematic_array(cine_1, cine_2)
    return valor_cinematic


def _validate_rake(rake, valor_cinematic):
    if valor_cinematic in (2, -2):  # dominio 0–90
        if not (0 <= rake < 90):
            raise ValueError(
                f"Rake {rake}° no existe para valor_cinematic={valor_cinematic}"
            )
    # normal 1 e inversa -1, dextral 3 y sinestral -3, Nx + Dx =  4, Nx + Sx = -2, Ix + Dx = 2, Ix + Sx = - 4
    elif valor_cinematic in (4, -4):  # dominio 90–180
        if not (90 < rake <= 180):
            raise ValueError(
                f"Rake {rake}° no existe para valor_cinematic={valor_cinematic}"
            )