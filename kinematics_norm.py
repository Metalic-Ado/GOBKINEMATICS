import numpy as np
from . kinematics_logic import cinematic_array, cinematic_from_value

# CLASIFICADOR DE FALLAS, SI SON ACEPTABLES O NO PARA EL ANALISIS
# RESTRINGIR DATOS VACIOS, datos que tengan -, "", u otros valors, colocarle None
# RESTRINGIR DATOS DE ENTRADA osea valorse de strike dip y rake y valores cinematicos

from dataclasses import dataclass, field


# NORMALIZACION DE DATOS

# PRIMERO SE CREA UND DATACLASS QUE ES UN CLASSES CON INIT LO CUAL SE OBTENIEN UN OBJETO LLAMADO FAUTSINPUT
# SE NORMALIZA LOS VALORES NULOS O VACIOS
# SE ANALIZA SEGUN EL TIPO DE DATOS (SUELTOS, LISTAS, DATAFRAME, CSV, EXCEL, ETC) # aun no resuelto solo para lista
# Se obtiene el objeto Faultinput en un array normalizado
# Se convierte en objeto en lista de array para que sean utilizados en la normalizacion de fallas

# PRIMERA NORMALIZACION DE DATOS
# Normalizacion de datos nulos
# Normalizacion de strike dip, rake
# Normalizacion de cine_1 y cine_2

# SEGUNDA NORMALIZACION
# Normalizacion de estructura de datos (uso de estructura de datos)

# TERCERA NORMALIZACION
# Normalizacion de salida de datos (JSON y data de salida)


########################################################################################################################
################################################# PRIMERA NORMALIZACION ################################################
########################################################################################################################

# ESTA PRIMERA NORMALIZACION ACEPTA TODO TIPO DE VALORESE DE FALLAS, CON LA REGLA DE LA MANO DERECHA, se podria decir
# todo el espectro de fallas,
# PARA ELLO PRIMERO NORMALIZAMOS LOS VALORES NULOS


# Creacion de la Clase con todos los datos entrantes:
@dataclass
class FaultInput:
    strike: float
    dip: float | None
    rake: float | None
    cine_1: str | None
    cine_2: str | None
    extras: dict = field(default_factory=dict)


# Normalizacion de valores Nulos
VACIOS = {"", "-", "_", "/", "nan", "NaN", "null", "None"}


def normalize_value(x):
    # None explícito
    if x is None:
        return None

    # numpy nan
    if isinstance(x, float) and np.isnan(x):
        return None

    # strings
    if isinstance(x, str):
        x = x.strip().lower()
        if x in VACIOS:
            return None
        # intentar convertir a número
        try:
            return float(x)
        except ValueError:
            return x  # Nx, Dx, etc.

    # Enteros → float
    if isinstance(x, (int, np.integer)):
        return float(x)

    return x

def es_valido(x):
    return x is not None

# NORMALIZACION 2 DE DTOS GEOLOGICOS...
# CAMBIO DE LUGAR EL NONE osea si Cine 1 no tiene valor y cine 2 si, los cambia de valor
def shift_if_missing(a, b):
    if a is None and b is not None:
        return b, None
    return a, b


def normalize_angles(strike, dip=None, rake=None):
    """
    Normaliza strike, dip y rake.

    strike: obligatorio, 0–360
    dip: opcional, 0–90 o None
    rake: opcional, 0–180 o None
    """

    # ------------------------------
    # Strike (obligatorio)
    # ------------------------------
    strike = normalize_value(strike)

    if strike is None:
        raise ValueError("strike no puede ser None")

    if not (0 <= strike < 360):
        # opción: corregir con módulo
        raise ValueError(f"strike fuera de rango: {strike} (debe estar entre 0 y 360)")

    # ------------------------------
    # Dip (puede ser None)
    # ------------------------------
    dip = normalize_value(dip)

    if dip is not None:
        if not (0 <= dip <= 90):
            raise ValueError(f"dip fuera de rango: {dip} (debe estar entre 0 y 90)")

    # ------------------------------
    # Rake (puede ser None)
    # ------------------------------
    rake = normalize_value(rake)

    if rake is not None:
        if not (0 <= rake <= 180):
            raise ValueError(f"rake fuera de rango: {rake} (debe estar entre 0 y 180)")

    return strike, dip, rake

# normalizar data cinematica:
CINE_MAP = {
    # ----------------------------
    # Dextral → dx
    # ----------------------------
    "dx": "dx",
    "dextral": "dx",
    "destral": "dx",
    "dex": "dx",
    "d": "dx",

    # ----------------------------
    # Sinistral → sx
    # ----------------------------
    "sx": "sx",
    "sinistral": "sx",
    "sinestral": "sx",
    "sin": "sx",
    "s": "sx",

    # ----------------------------
    # Normal → nx
    # ----------------------------
    "nx": "nx",
    "normal": "nx",
    "nor": "nx",
    "n": "nx",

    # ----------------------------
    # Inversa → ix
    # ----------------------------
    "ix": "ix",
    "inverse": "ix",
    "inv": "ix",
    "inversa": "ix",
    "reverse": "ix",
    "reversa": "ix",
    "i": "ix",
}

def normalize_cinema(cine_1=None, cine_2=None):
    """
    Normaliza cine_1 y cine_2:

    - Limpia espacios
    - Convierte a minúsculas
    - Mapea sinónimos a: dx, sx, nx, ix
    - Aplica shift si cine_1 es None
    - Valida combinaciones permitidas
    """

    # ------------------------------
    # Normalización básica (None, vacíos)
    # ------------------------------
    cine_1 = normalize_value(cine_1)
    cine_2 = normalize_value(cine_2)

    # ------------------------------
    # Shift automático
    # ------------------------------
    cine_1, cine_2 = shift_if_missing(cine_1, cine_2)

    # ------------------------------
    # Normalizar string individual
    # ------------------------------
    def norm_one(x):
        if x is None:
            return None

        if not isinstance(x, str):
            raise TypeError(f"Cinemática debe ser string o None, no {type(x)}")

        # quitar espacios + minusculas
        key = x.strip().lower()

        # mapear sinónimos
        if key not in CINE_MAP:
            raise ValueError(f"Valor cinemático no reconocido: '{x}'")

        return CINE_MAP[key]

    cine_1 = norm_one(cine_1)
    cine_2 = norm_one(cine_2)

    # ------------------------------
    # Validaciones entre cine_1 y cine_2
    # ------------------------------
    if cine_1 is not None and cine_2 is not None:

        # 1. No pueden ser iguales
        if cine_1 == cine_2:
            raise ValueError(
                f"No puede repetirse la misma cinemática: {cine_1} y {cine_2}"
            )

        # 2. No pueden ser contrapartes
        contrapartes = {
            ("dx", "sx"),
            ("sx", "dx"),
            ("nx", "ix"),
            ("ix", "nx"),
        }

        if (cine_1, cine_2) in contrapartes:
            raise ValueError(
                f"No se permite combinación opuesta: {cine_1} y {cine_2}"
            )

        # 3. Solo combinaciones permitidas
        permitidas = {
            frozenset(("dx", "nx")),
            frozenset(("dx", "ix")),
            frozenset(("sx", "nx")),
            frozenset(("sx", "ix")),
        }

        if frozenset((cine_1, cine_2)) not in permitidas:
            raise ValueError(
                f"Combinación cinemática inválida: {cine_1} + {cine_2}"
            )

    return cine_1, cine_2


def normalize_fault_data(strike, dip=None, rake=None, cine_1=None, cine_2=None):
    """
    Normalización completa de una falla:

    - Normaliza strike/dip/rake (ángulos)
    - Normaliza cine_1/cine_2 (cinemática)
    """

    # ------------------------------
    # Normalización geométrica
    # ------------------------------
    strike, dip, rake = normalize_angles(strike, dip, rake)

    # ------------------------------
    # Normalización cinemática
    # ------------------------------
    cine_1, cine_2 = normalize_cinema(cine_1, cine_2)

    return strike, dip, rake, cine_1, cine_2


def make_fault(strike, dip=None, rake=None, cine_1=None, cine_2=None, **extras):

    # ------------------------------
    # Normalización completa
    # ------------------------------
    strike, dip, rake, cine_1, cine_2 = normalize_fault_data(
        strike, dip, rake, cine_1, cine_2
    )

    # ------------------------------
    # Construcción del objeto final
    # ------------------------------
    return FaultInput(
        strike=strike,
        dip=dip,
        rake=rake,
        cine_1=cine_1,
        cine_2=cine_2,
        extras={k: normalize_value(v) for k, v in extras.items()}
    )


# desde listas y numeros datos sueltos

def from_lists(strike, dip, rake, cine_1=None, cine_2=None):

    strike = np.atleast_1d(strike)
    dip    = np.atleast_1d(dip)
    rake   = np.atleast_1d(rake)

    n = len(strike)

    # Expandir cine si no se dio
    if cine_1 is None:
        cine_1 = [None] * n
    else:
        cine_1 = np.atleast_1d(cine_1)

    if cine_2 is None:
        cine_2 = [None] * n
    else:
        cine_2 = np.atleast_1d(cine_2)

    # Ahora sí chequeo de longitudes
    lengths = {
        "strike": len(strike),
        "dip": len(dip),
        "rake": len(rake),
        "cine_1": len(cine_1),
        "cine_2": len(cine_2),
    }

    if len(set(lengths.values())) != 1:
        raise ValueError(
            "Longitudes incompatibles: "
            + ", ".join(f"{k}={v}" for k, v in lengths.items())
        )

    faults = []
    for s, d, r, c1, c2 in zip(strike, dip, rake, cine_1, cine_2):
        faults.append(make_fault(s, d, r, c1, c2))

    return faults



# convierte el objeto en array

def extract_arrays(faults):
    strike = [f.strike for f in faults]
    dip    = [f.dip for f in faults]
    rake   = [f.rake for f in faults]
    cine_1 = [f.cine_1 for f in faults]
    cine_2 = [f.cine_2 for f in faults]
    return strike, dip, rake, cine_1, cine_2
