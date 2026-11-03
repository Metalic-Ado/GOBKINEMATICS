import numpy as np
from . kinematics_logic import cinematic_array, cinematic_from_value

# CLASIFICADOR DE FALLAS, SI SON ACEPTABLES O NO PARA EL ANALISIS
# RESTRINGIR DATOS VACIOS, datos que tengan -, "", u otros valors, colocarle None
# RESTRINGIR DATOS DE ENTRADA osea valorse de strike dip y rake y valores cinematicos

# _____________________________________________________________________________________________________________________
# PRIMERA REGLA:  TODOS LOS DATOS CRUDOS DE ENTRADA DEBEN DE TENER LA MISMA LONGITUD, SI NO LA TIENEN RELLENAS CON ""

def to_1d_sequence(value):
    """
    Convierte una entrada a una secuencia 1D sin modificar sus valores.

    Reglas:
    - Escalar      -> secuencia de 1 elemento
    - None         -> [None]
    - String       -> [string]
    - Lista/tupla  -> conserva sus elementos
    - ndarray 1D   -> conserva sus elementos
    - ndarray 2D+  -> error
    """

    # None es un elemento
    if value is None:
        return [None]

    # Los strings son valores individuales, no secuencias de caracteres
    if isinstance(value, str):
        return [value]

    # Convertimos el resto a ndarray de tipo object
    arr = np.asarray(value, dtype=object)

    # Escalar
    if arr.ndim == 0:
        return [arr.item()]

    # Solo aceptamos una dimensión
    if arr.ndim != 1:
        raise ValueError(
            "La entrada debe ser escalar o una secuencia de una sola dimensión."
        )

    return arr.tolist()


def validate_input_lengths(strike, dip, rake, cine_1, cine_2):
    """
    Primera regla de entrada:

    Todas las entradas deben contener exactamente
    la misma cantidad de elementos.

    No modifica los valores.
    No normaliza.
    No completa datos.
    No repite datos.
    """

    sequences = {
        "strike": to_1d_sequence(strike),
        "dip": to_1d_sequence(dip),
        "rake": to_1d_sequence(rake),
        "cine_1": to_1d_sequence(cine_1),
        "cine_2": to_1d_sequence(cine_2),
    }

    lengths = {
        name: len(values)
        for name, values in sequences.items()
    }

    unique_lengths = set(lengths.values())

    if len(unique_lengths) != 1:
        mensaje = (
            "\nERROR DE ESTRUCTURA DE ENTRADA\n\n"
            f"strike : {lengths['strike']}\n"
            f"dip    : {lengths['dip']}\n"
            f"rake   : {lengths['rake']}\n"
            f"cine_1 : {lengths['cine_1']}\n"
            f"cine_2 : {lengths['cine_2']}\n\n"
            "Todas las entradas deben contener exactamente "
            "la misma cantidad de elementos."
        )

        raise ValueError(mensaje)

    return sequences


# ______________________________________________________________________________________________________________________

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
    strike: float | None
    dip: float | None
    rake: float | None
    cine_1: str | None
    cine_2: str | None

# PASO 2: NORMALIZACION DE VALORES NULOS A None o string numericos digamos "120" a 120

# Normalización de valores nulos
VACIOS = {"", "-", "_", "/", "nan", "NaN", "null", "None"}


def normalize_value(x):
    # Vacío real
    if x is None:
        return None

    # NaN numérico: np.nan, float("nan"), etc.
    if isinstance(x, (float, np.floating)) and np.isnan(x):
        return None

    # Cadenas
    if isinstance(x, str):
        value = x.strip()

        if value.lower() in {
            "",
            "-",
            "_",
            "/",
            "nan",
            "null",
            "none",
        }:
            return None

        # Intentar convertir números escritos como texto
        try:
            return float(value)
        except ValueError:
            return value

    # Números enteros
    if isinstance(x, (int, np.integer)):
        return float(x)

    return x

# PASO 3: VALIDACION DEL TIPO DE DATO: STRIKE DIP RAKE SON NUMERTOS Y CINMETICA STRING, ojo no interesa aun el valor o la palabra
# por ejemplo el string puede ser lo que sea "pasto" pero debe estar en cinematica y digamo el rake puede ser 400 despues ya se condicionara

def validate_data_types(data):
    """
    Valida los tipos de datos después de la normalización básica.

    Tipos permitidos:
        strike -> float | None
        dip    -> float | None
        rake   -> float | None
        cine_1 -> str | None
        cine_2 -> str | None

    Si encuentra un error, detiene el procesamiento y muestra
    el campo, registro y valor problemático.
    """

    numeric_fields = {"strike", "dip", "rake"}
    cinematic_fields = {"cine_1", "cine_2"}

    errors = []

    for field, values in data.items():

        for index, value in enumerate(values):

            # None siempre es válido
            if value is None:
                continue

            # Campos numéricos
            if field in numeric_fields:

                if not isinstance(value, (float, np.floating)):
                    errors.append({
                        "registro": index + 1,
                        "campo": field,
                        "valor": value,
                        "tipo_esperado": "número o None"
                    })

            # Campos cinemáticos
            elif field in cinematic_fields:

                if not isinstance(value, str):
                    errors.append({
                        "registro": index + 1,
                        "campo": field,
                        "valor": value,
                        "tipo_esperado": "string o None"
                    })

    if errors:
        mensaje = "\nERROR DE TIPO DE DATO\n\n"

        for error in errors:
            mensaje += (
                f"Registro : {error['registro']}\n"
                f"Campo    : {error['campo']}\n"
                f"Valor    : {repr(error['valor'])}\n"
                f"Esperado : {error['tipo_esperado']}\n"
                f"Tipo     : {type(error['valor']).__name__}\n"
                "\n"
            )

        mensaje += (
            "Los datos contienen errores de tipo.\n"
            "Corrija los valores indicados antes de continuar."
        )

        raise ValueError(mensaje)

    return data


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


def validate_cinematic_value(value):
    """
    Valida que un valor de cinemática pueda ser reconocido
    por CINE_MAP.

    Esta función NO normaliza el valor.
    Solo determina si la entrada es válida.
    """

    if value is None:
        return

    if not isinstance(value, str):
        raise TypeError(
            f"Valor cinemático inválido: {value!r}. "
            "La cinemática debe ser un string o None."
        )

    key = value.strip().lower()

    if key not in CINE_MAP:
        raise ValueError(
            f"Valor cinemático no reconocido: {value!r}."
        )


def normalize_cinematic_value(value):
    """
    Normaliza un valor cinemático utilizando CINE_MAP.

    La función recibe un valor que ya ha sido validado
    y devuelve su representación canónica.
    """

    if value is None:
        return None

    key = value.strip().lower()

    return CINE_MAP[key]

# CAMBIO DE LUGAR EL NONE osea si Cine 1 no tiene valor y cine 2 si, los cambia de valor
def shift_if_missing(a, b):
    if a is None and b is not None:
        return b, None
    return a, b


def validate_cinematic_combination(cine_1, cine_2):
    """
    Valida la combinación entre cine_1 y cine_2.

    Las combinaciones permitidas son:
        dx + nx
        dx + ix
        sx + nx
        sx + ix

    Una sola cinemática o ninguna también son válidas.

    Esta función no normaliza valores ni modifica
    la posición de cine_1 y cine_2.
    """

    # Una o ninguna cinemática: no hay combinación que validar
    if cine_1 is None or cine_2 is None:
        return

    # 1. No pueden ser iguales
    if cine_1 == cine_2:
        raise ValueError(
            f"No puede repetirse la misma cinemática: "
            f"{cine_1} y {cine_2}"
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
            f"No se permite combinación opuesta: "
            f"{cine_1} y {cine_2}"
        )

    # 3. Solo se permiten estas combinaciones
    permitidas = {
        frozenset(("dx", "nx")),
        frozenset(("dx", "ix")),
        frozenset(("sx", "nx")),
        frozenset(("sx", "ix")),
    }

    if frozenset((cine_1, cine_2)) not in permitidas:
        raise ValueError(
            f"Combinación cinemática inválida: "
            f"{cine_1} + {cine_2}"
        )



def normalize_cinema(cine_1=None, cine_2=None):
    """
    Normaliza cine_1 y cine_2 mediante etapas independientes:

    1. Normalización básica del valor:
       None, vacíos, NaN, etc.
    2. Validación del valor cinemático.
    3. Normalización mediante CINE_MAP.
    4. Reordenamiento de None.
    5. Validación de la combinación cinemática.

    Retorna:
        tuple: (cine_1, cine_2)
    """

    # --------------------------------------------------
    # 1. NORMALIZACIÓN BÁSICA
    # --------------------------------------------------

    cine_1 = normalize_value(cine_1)
    cine_2 = normalize_value(cine_2)

    # --------------------------------------------------
    # 2. VALIDAR VALORES CINEMÁTICOS
    # --------------------------------------------------

    validate_cinematic_value(cine_1)
    validate_cinematic_value(cine_2)

    # --------------------------------------------------
    # 3. NORMALIZAR MEDIANTE CINE_MAP
    # --------------------------------------------------

    cine_1 = normalize_cinematic_value(cine_1)
    cine_2 = normalize_cinematic_value(cine_2)

    # --------------------------------------------------
    # 4. CAMBIAR DE LUGAR EL None
    # --------------------------------------------------

    cine_1, cine_2 = shift_if_missing(cine_1, cine_2)

    # --------------------------------------------------
    # 5. VALIDAR COMBINACIÓN
    # --------------------------------------------------

    validate_cinematic_combination(cine_1, cine_2)

    return cine_1, cine_2


def normalize_angles(strike=None, dip=None, rake=None):
    """
    Normaliza strike, dip y rake.

    strike: obligatorio, 0–360
    dip: opcional, 0–90 o None
    rake: opcional, 0–180 o None
    """

    # ------------------------------
    # Strike
    # ------------------------------
    strike = normalize_value(strike)

    if strike is None:
        raise ValueError(
            "strike es obligatorio y no puede ser None."
        )

    if not (0 <= strike < 360):
        raise ValueError(
            f"strike fuera de rango: {strike} "
            f"(debe estar entre 0 y 360)"
        )
    # ------------------------------
    # Dip
    # ------------------------------

    dip = normalize_value(dip)

    if dip is not None:
        if not (0 <= dip <= 90):
            raise ValueError(
                f"dip fuera de rango: {dip} "
                f"(debe estar entre 0 y 90)"
            )

    # ------------------------------
    # Rake
    # ------------------------------

    rake = normalize_value(rake)

    if rake is not None:
        if not (0 <= rake <= 180):
            raise ValueError(
                f"rake fuera de rango: {rake} "
                f"(debe estar entre 0 y 180)"
            )

    return strike, dip, rake



# FUNCION QUE UNE TODO: ENTRA DATOS CRUDOS SALE DATOS NORMALIZADOS

def normalize_basic_data(
    strike=None,
    dip=None,
    rake=None,
    cine_1=None,
    cine_2=None,
):
    """
    Normaliza los datos básicos de fallas.

    Etapas:
        1. Validación estructural de longitudes.
        2. Normalización básica de valores.
        3. Validación de tipos.
        4. Normalización de strike, dip y rake.
        5. Normalización de cine_1 y cine_2.

    No aplica todavía reglas geológicas entre rake y cinemática.

    Retorna:
        dict con:
            strike
            dip
            rake
            cine_1
            cine_2
    """

    # --------------------------------------------------
    # 1. ESTRUCTURA DE ENTRADA
    # --------------------------------------------------

    data = validate_input_lengths(
        strike,
        dip,
        rake,
        cine_1,
        cine_2,
    )

    # --------------------------------------------------
    # 2. NORMALIZACIÓN BÁSICA
    # --------------------------------------------------

    data = {
        name: [normalize_value(value) for value in values]
        for name, values in data.items()
    }

    # --------------------------------------------------
    # 3. VALIDACIÓN DE TIPOS
    # --------------------------------------------------

    validate_data_types(data)

    # --------------------------------------------------
    # 4. NORMALIZACIÓN DE ÁNGULOS
    # --------------------------------------------------

    strike_normalized = []
    dip_normalized = []
    rake_normalized = []

    for s, d, r in zip(
        data["strike"],
        data["dip"],
        data["rake"],
    ):
        s, d, r = normalize_angles(s, d, r)

        strike_normalized.append(s)
        dip_normalized.append(d)
        rake_normalized.append(r)

    # --------------------------------------------------
    # 5. NORMALIZACIÓN DE CINEMÁTICA
    # --------------------------------------------------

    cine_1_normalized = []
    cine_2_normalized = []

    for c1, c2 in zip(
        data["cine_1"],
        data["cine_2"],
    ):
        c1, c2 = normalize_cinema(c1, c2)

        cine_1_normalized.append(c1)
        cine_2_normalized.append(c2)

    # --------------------------------------------------
    # 6. RESULTADO
    # --------------------------------------------------

    return {
        "strike": strike_normalized,
        "dip": dip_normalized,
        "rake": rake_normalized,
        "cine_1": cine_1_normalized,
        "cine_2": cine_2_normalized,
    }








def normalize_fault_data(strike = None , dip=None, rake=None, cine_1=None, cine_2=None):
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

def normalize_inputs(strike=None, dip=None, rake=None, cine_1=None, cine_2=None):

    # arrays
    if strike is not None:
        strike = np.atleast_1d(strike)

    if dip is not None:
        dip = np.atleast_1d(dip)

    if rake is not None:
        rake = np.atleast_1d(rake)

    if cine_1 is not None:
        cine_1 = np.atleast_1d(cine_1)

    if cine_2 is not None:
        cine_2 = np.atleast_1d(cine_2)

    return {
        "strike": strike,
        "dip": dip,
        "rake": rake,
        "cine_1": cine_1,
        "cine_2": cine_2
    }


def make_fault(strike = None, dip=None, rake=None, cine_1=None, cine_2=None):

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
        cine_2=cine_2)



# desde listas y numeros datos sueltos

def from_lists(strike = None, dip = None, rake = None, cine_1=None, cine_2=None):

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


def extract_arrays(faults):
    strike = [f.strike for f in faults]
    dip = [f.dip for f in faults]
    rake = [f.rake for f in faults]
    cine_1 = [f.cine_1 for f in faults]
    cine_2 = [f.cine_2 for f in faults]

    return strike, dip, rake, cine_1, cine_2
