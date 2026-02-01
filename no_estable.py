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


@dataclass
class FaultInput:
    strike: float
    dip: float | None
    rake: float | None
    cine_1: str | None
    cine_2: str | None
    extras: dict = field(default_factory=dict)


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


def make_fault(strike, dip=None, rake=None, cine_1=None, cine_2=None, **extras):
    return FaultInput(
        strike=normalize_value(strike),
        dip=normalize_value(dip),
        rake=normalize_value(rake),
        cine_1=normalize_value(cine_1),
        cine_2=normalize_value(cine_2),
        extras={k: normalize_value(v) for k, v in extras.items()}
    )

# desde listas y numeros datos sueltos

def from_lists(strike, dip, rake, cine_1=None, cine_2=None):

    strike, dip, rake, cine_1, cine_2 = np.atleast_1d(
        strike, dip, rake, cine_1, cine_2
    )

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


# clasifica a las fallas segun el numero de Nones que tiene en la primera normalizacion
# esta parte del sofware no elimina o discrimina las fallas que no entren en los valores solo las clasifica

def clasify_for_items(strike, dip, rake, cine_1, cine_2):
    strike, dip, rake, cine_1, cine_2 = np.atleast_1d(strike, dip, rake, cine_1, cine_2)

    resultados = []

    for i, (s, d, r, c1, c2) in enumerate(zip(strike, dip, rake, cine_1, cine_2)):

        registro = {
            "strike": s,
            "dip": d,
            "rake": r,
            "cine_1": c1,
            "cine_2": c2
        }
        n_valid = sum(es_valido(v) for v in registro.values())

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

        resultados.append({
            "id": i,
            "clase": clase,
            "datos": registro,
            "estado": "sin_evaluar"
        })

    return resultados



def _treatment_n5(registro):

    datos = registro["datos"]

    dip = datos["dip"]
    rake = datos["rake"]
    cine_1 = datos["cine_1"]
    cine_2 = datos["cine_2"]

    valor_cinematico = cinematic_array(cine_1, cine_2)

    conforme = False

    # Normal + Sinestral  | Inversa + Dextral
    if valor_cinematico in (2, -2):
        if (0 < rake < 90) and (dip != 0):
            conforme = True

    # Normal + Dextral | Inversa + Sinestral
    elif valor_cinematico in (4, -4):
        if (90 < rake < 180) and (dip != 0):
            conforme = True

    if conforme:
        registro["estado"] = "conforme"
    else:
        registro["estado"] = "inconforme"

    registro["valor_cinematico"] = valor_cinematico

    return registro

# CUANDO SE TIENEN SOLO 4 DATOS
# Normalizacion de la cinematica si existe un None en Cine 1 y no es Cine 2, se intercambia para que Cine 1 tenga el valor de Cine 2

def _normalize_kinematic_n4(registro):
    datos = registro["datos"]

    if datos["cine_1"] is None and datos["cine_2"] is not None:
        datos["cine_1"] = datos["cine_2"]
        datos["cine_2"] = None

    return registro

# Cuando existe 4 valores y un None, Existe 3 clasos posibles:
# 1 Cuando Cine 2 es Nones, pero solo existe 4 valores
# 2 Cuando Cine 2 es None, pero existe 5 valores (osea que el cine 2 puede ser autocompletado)
# 3 Cuando el rake es None

def _identify_subtype_n4(registro):
    datos = registro["datos"]

    rake = datos["rake"]
    cine_1 = datos["cine_1"]
    cine_2 = datos["cine_2"]

    # Caso 3: rake ausente, dos cinemáticas
    if rake is None and cine_1 is not None and cine_2 is not None:
        return "N4_caso_3"

    # Caso 1 y 2: rake presente, una sola cinemática
    if rake is not None and cine_1 is not None and cine_2 is None:
        return "N4_caso_1_o_2"

    return "N4_invalido"

# un cinematica pero esta no necesita mas datos

def _n4_case_1(registro):
    datos = registro["datos"]

    dip = datos["dip"]
    rake = datos["rake"]
    cine = datos["cine_1"]

    valor = cinematic_array(cine, None)
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

    valor = cinematic_array(cine, None)

    if dip is None or rake is None or valor is None:
        registro["estado"] = "invalido"
        return registro

    new_valor = None

    if 0 < rake < 90:
        if valor in (1, -3):
            new_valor = -2
        elif valor in (-1, 3):
            new_valor = 2

    elif 180 > rake > 90:
        if valor in (1, 3):
            new_valor = 4
        elif valor in (-1, -3):
            new_valor = -4

    # 🚨 AQUÍ está lo que faltaba 🚨
    if new_valor is not None:
        cine1, cine2 = cinematic_from_value(new_valor)

        datos["cine_1"] = cine1
        datos["cine_2"] = cine2

        registro["clase"] = "N5"
        registro["origen"] = "N4_autocompletado"

        return _treatment_n5(registro)

    registro["estado"] = "inconforme"
    return registro

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

    # --------------------------------------------------
    # 1. Normalizar cinemática (orden)
    # --------------------------------------------------
    registro = _normalize_kinematic_n4(registro)
    datos = registro["datos"]

    rake = datos["rake"]
    cine_1 = datos["cine_1"]
    cine_2 = datos["cine_2"]

    # --------------------------------------------------
    # 2. Identificar subtipo N4
    # --------------------------------------------------

    # 🔹 Caso 3: rake ausente + dos cinemáticas
    if rake is None and cine_1 is not None and cine_2 is not None:
        registro["modo"] = "N4_caso_3"
        return _n4_case_3(registro)

    # 🔹 Caso 1 o 2: rake presente + una cinemática
    if rake is not None and cine_1 is not None and cine_2 is None:
        # intentar primero conformidad directa
        reg1 = _n4_case_1(registro.copy())

        if reg1["estado"] == "conforme":
            return reg1

        # si no → intentar autocompletar
        registro["modo"] = "N4_caso_2"
        return _n4_case_2(registro)

    # --------------------------------------------------
    # 3. Estructura inválida
    # --------------------------------------------------
    registro["estado"] = "invalido"
    registro["motivo"] = "estructura_N4_invalida"
    return registro

# Cuando hay 3 valores solo hay dos casos:
# Caso 1 cuando no hay cinematica osea cine 1 y cine 2 es None
# Caso 2 Cuando No hay rake pero si hay una Cinematica osea Rake and Cine 2 is None
def _treatment_n3(registro):
    datos = registro["datos"]

    strike = datos["strike"]
    dip = datos["dip"]
    rake = datos["rake"]
    cine_1 = datos["cine_1"]
    cine_2 = datos["cine_2"]

    # -------------------------
    # Caso 1: geometría pura
    # -------------------------
    if (
        strike is not None and
        dip is not None and
        rake is not None and
        cine_1 is None and
        cine_2 is None
    ):
        registro["estado"] = "cuasi_conforme"
        registro["modo"] = "N3_caso_1"
        return registro

    # -------------------------
    # Caso 2: plano + una cinemática
    # -------------------------
    if (
        strike is not None and
        dip is not None and
        rake is None and
        (
            (cine_1 is not None and cine_2 is None) or
            (cine_1 is None and cine_2 is not None)
        )
    ):
        registro["estado"] = "cuasi_conforme"
        registro["modo"] = "N3_caso_2"
        return registro

    # -------------------------
    # Todo lo demás
    # -------------------------
    registro["estado"] = "invalido"
    registro["modo"] = "N3_estructura_invalida"
    return registro


def _treatment_n2(registro):
    registro["nivel"] = "N2"
    registro["modo"] = "N2_caso_unico"
    registro["estado"] = "cuasiconforme"
    registro["motivo"] = "plano_sin_cinematica"
    return registro

def _treatment_n1(registro):
    registro["nivel"] = "N1"
    registro["modo"] = "N1_caso_unico"
    registro["estado"] = "cuasiconforme"
    registro["motivo"] = "orientacion minima"
    return registro

# UNE TODOS LOS TRATAMIENTOS DEL 1 AL 5 (EL OBJETIVO ETIQUETAR TODOS LOS TIPOS DE FALLAS)

def process_registration(registro):
    """
    Aplica el tratamiento completo según la clase N1–N5
    y devuelve el registro totalmente clasificado.
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

    else:
        registro["estado"] = "invalido"
        registro["modo"] = "clase_desconocida"
        return registro
























