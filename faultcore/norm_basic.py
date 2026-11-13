import numpy as np

try:
    import pandas as pd
except ImportError:
    pd = None


def to_1d_sequence(value, field_name="campo"):
    """
    Convierte una entrada a una lista unidimensional sin modificar
    sus valores.

    Reglas:
    - Escalar         -> [valor]
    - None            -> [None]
    - String          -> [string]
    - Lista/tupla     -> conserva sus elementos
    - ndarray 1D      -> conserva sus elementos
    - ndarray 2D+     -> error
    - set/frozenset   -> error (no garantizan orden)
    """

    # 1. None se considera un valor individual
    if value is None:
        return [None]

    # 2. Rechazar conjuntos porque no garantizan el orden
    if isinstance(value, (set, frozenset)):
        raise ValueError(
            f"El campo '{field_name}' no puede recibir conjuntos "
            "porque no garantizan el orden de los registros."
        )

    # 3. Las cadenas se consideran valores individuales
    if isinstance(value, str):
        return [value]

    # 4. Intentar convertir la entrada en un array NumPy
    try:
        arr = np.asarray(value, dtype=object)

    except Exception as exc:
        raise ValueError(
            f"No se pudo interpretar la estructura de '{field_name}'."
        ) from exc

    # 5. Los escalares se convierten en listas de un elemento
    if arr.ndim == 0:
        return [arr.item()]

    # 6. Rechazar estructuras multidimensionales
    if arr.ndim != 1:
        raise ValueError(
            f"El campo '{field_name}' debe ser escalar "
            "o una secuencia unidimensional."
        )

    # 7. Devolver los elementos como lista
    return arr.tolist()


def validate_input_lengths(strike, dip, rake, cine_1, cine_2):
    """
    Comprueba que los cinco campos tengan exactamente
    la misma cantidad de elementos.

    Reglas:
    - Convierte las entradas a secuencias unidimensionales.
    - No normaliza los valores.
    - No completa datos.
    - No repite datos.
    - No elimina datos.
    - No modifica el orden de los registros.

    Retorna:
        dict: Diccionario con los cinco campos convertidos
              a listas unidimensionales.

    Raises:
        ValueError: Si alguna entrada tiene una estructura
                    incorrecta o las longitudes son diferentes.
    """

    # 1. Convertir las entradas a secuencias unidimensionales
    sequences = {
        "strike": to_1d_sequence(strike, "strike"),
        "dip": to_1d_sequence(dip, "dip"),
        "rake": to_1d_sequence(rake, "rake"),
        "cine_1": to_1d_sequence(cine_1, "cine_1"),
        "cine_2": to_1d_sequence(cine_2, "cine_2")
    }

    # 2. Calcular la longitud de cada campo
    lengths = {
        name: len(values)
        for name, values in sequences.items()
    }

    # 3. Comprobar que todas las longitudes sean iguales
    if len(set(lengths.values())) != 1:

        mensaje = (
            "\nERROR DE ESTRUCTURA DE ENTRADA\n\n"
            f"strike : {lengths['strike']}\n"
            f"dip    : {lengths['dip']}\n"
            f"rake   : {lengths['rake']}\n"
            f"cine_1 : {lengths['cine_1']}\n"
            f"cine_2 : {lengths['cine_2']}\n\n"
            "Todas las entradas deben tener exactamente "
            "la misma cantidad de elementos."
        )

        raise ValueError(mensaje)

    # 4. Retornar las secuencias
    return sequences



def normalize_value(value):
    """
    Normaliza un valor individual.

    Reglas:
    - None, NaN, pd.NA y pd.NaT se convierten en None.
    - Cadenas vacías y marcadores de ausencia se convierten en None.
    - Cadenas numéricas se convierten en float.
    - Valores numéricos enteros y decimales se convierten en float.
    - Los booleanos se conservan para que validate_data_types()
      pueda identificarlos como tipos no permitidos.
    - Los valores no compatibles se conservan para su validación posterior.
    """

    # 1. Valores nulos
    if value is None:
        return None

    # 2. No convertir booleanos a números
    if isinstance(value, (bool, np.bool_)):
        return value

    # 3. Detectar NaN de NumPy y Python
    if isinstance(value, (float, np.floating)):
        if np.isnan(value):
            return None

    # 4. Detectar valores ausentes de pandas
    if pd is not None:
        try:
            missing = pd.isna(value)

            if isinstance(missing, (bool, np.bool_)) and missing:
                return None

        except (TypeError, ValueError):
            pass

    # 5. Normalizar cadenas de texto
    if isinstance(value, str):

        value = value.strip()

        marcadores_vacios = {
            "",
            "-",
            "_",
            "/",
            "nan",
            "null",
            "none",
            "<na>",
            "nat"
        }

        if value.lower() in marcadores_vacios:
            return None

        # Intentar convertir cadenas numéricas
        try:
            return float(value)

        except ValueError:
            return value

    # 6. Convertir números enteros y decimales
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    # 7. Conservar otros tipos para validarlos posteriormente
    return value


def normalize_basic_values(data):
    """
    Normaliza los valores de todos los campos de entrada.

    - Convierte valores vacíos a None.
    - Convierte valores numéricos a float.
    - Convierte cadenas numéricas a float.
    - Conserva textos no numéricos para su validación posterior.
    - Mantiene la cantidad y posición de los registros.
    """

    required_fields = [
        "strike",
        "dip",
        "rake",
        "cine_1",
        "cine_2"
    ]

    # Comprobar que exista la estructura esperada
    if not isinstance(data, dict):
        raise TypeError("La entrada debe ser un diccionario.")

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        raise ValueError(
            f"Faltan campos obligatorios: {missing_fields}"
        )

    # Normalizar cada valor sin alterar las posiciones
    normalized_data = {
        field: [
            normalize_value(value)
            for value in data[field]
        ]
        for field in required_fields
    }

    return normalized_data


def validate_data_types(data):
    """
    Valida los tipos de datos de los cinco campos.

    Campos numéricos:
        strike, dip, rake -> int, float o None.

    Campos cinemáticos:
        cine_1, cine_2 -> str o None.

    Revisa todos los registros y acumula los errores
    antes de generar una excepción.

    No modifica los datos.
    """

    numeric_fields = ["strike", "dip", "rake"]
    cinematic_fields = ["cine_1", "cine_2"]

    errors = []

    # Validar campos numéricos
    for field in numeric_fields:

        for index, value in enumerate(data[field]):

            if value is None:
                continue

            # bool no se acepta como número
            if isinstance(value, (bool, np.bool_)):
                errors.append(
                    f"Registro {index + 1} | "
                    f"{field}: tipo booleano no permitido ({value!r})."
                )
                continue

            if not isinstance(value, (int, float, np.integer, np.floating)):
                errors.append(
                    f"Registro {index + 1} | "
                    f"{field}: se esperaba un número o None, "
                    f"se recibió {type(value).__name__} ({value!r})."
                )

    # Validar campos cinemáticos
    for field in cinematic_fields:

        for index, value in enumerate(data[field]):

            if value is None:
                continue

            if not isinstance(value, str):
                errors.append(
                    f"Registro {index + 1} | "
                    f"{field}: se esperaba una cadena de texto "
                    f"o None, se recibió "
                    f"{type(value).__name__} ({value!r})."
                )

    # Informar todos los errores encontrados
    if errors:
        mensaje = (
            "\nERROR DE VALIDACIÓN DE TIPOS\n\n"
            + "\n".join(errors)
        )
        raise ValueError(mensaje)

    return data


def validate_required_values(data):
    """
    Comprueba los datos obligatorios de cada registro.

    Regla:
    - strike debe existir y ser numérico.
    - dip, rake, cine_1 y cine_2 pueden ser None.

    No modifica los datos.
    """

    errors = []

    for index, strike in enumerate(data["strike"]):

        if strike is None:
            errors.append(
                f"Registro {index + 1} | strike: "
                "dato obligatorio ausente. "
                "Strike no puede ser None."
            )

    if errors:
        mensaje = (
            "\nERROR DE DATOS OBLIGATORIOS\n\n"
            + "\n".join(errors)
        )

        raise ValueError(mensaje)

    return data



def normalize_cinematic_values(data):
    """
    Normaliza los nombres de las cinemáticas.

    Equivalencias:
        dextral, destral, dex, d -> dx
        sinistral, sinestral, sin, s -> sx
        normal, nor, n -> nx
        inverse, inversa, inv, reverse, reversa, i -> ix

    - Reconoce mayúsculas y minúsculas.
    - Elimina espacios externos.
    - None permanece como None.
    - Los valores desconocidos se conservan para
      su diagnóstico posterior.

    No valida combinaciones cinemáticas.
    No desplaza valores entre cine_1 y cine_2.
    No modifica las reglas geológicas.
    """

    cinematic_map = {
        "dx": "dx",
        "dextral": "dx",
        "destral": "dx",
        "dex": "dx",
        "d": "dx",

        "sx": "sx",
        "sinistral": "sx",
        "sinestral": "sx",
        "sin": "sx",
        "s": "sx",

        "nx": "nx",
        "normal": "nx",
        "nor": "nx",
        "n": "nx",

        "ix": "ix",
        "inverse": "ix",
        "inversa": "ix",
        "inv": "ix",
        "reverse": "ix",
        "reversa": "ix",
        "i": "ix"
    }

    normalized_data = {
        field: values.copy()
        for field, values in data.items()
    }

    for field in ("cine_1", "cine_2"):

        normalized_data[field] = [
            cinematic_map.get(value.strip().lower(), value.strip())
            if isinstance(value, str)
            else value
            for value in data[field]
        ]

    return normalized_data



def validate_angle_ranges(data):
    """
    Valida los rangos individuales de strike, dip y rake.

    Rangos:
        strike: 0 <= strike < 360
        dip:    0 <= dip <= 90
        rake:   0 <= rake <= 180

    - None se permite en dip y rake.
    - None en strike debe haber sido detectado
      previamente por validate_required_values().
    - Acumula todos los errores encontrados.
    - No modifica los datos.

    Requiere que validate_data_types() se haya ejecutado antes.
    """

    errors = []

    angle_ranges = {
        "strike": (0, 360, False),
        "dip": (0, 90, True),
        "rake": (0, 180, True)
    }

    for field, (minimum, maximum, inclusive_max) in angle_ranges.items():

        for index, value in enumerate(data[field]):

            if value is None:
                continue

            if inclusive_max:
                valid = minimum <= value <= maximum
            else:
                valid = minimum <= value < maximum

            if not valid:
                if inclusive_max:
                    range_text = f"{minimum} <= valor <= {maximum}"
                else:
                    range_text = f"{minimum} <= valor < {maximum}"

                errors.append(
                    f"Registro {index + 1} | {field}: "
                    f"valor {value} fuera del rango permitido "
                    f"({range_text})."
                )

    if errors:
        mensaje = (
            "\nERROR DE RANGOS ANGULARES\n\n"
            + "\n".join(errors)
        )

        raise ValueError(mensaje)

    return data



def normalize_basic_data(strike, dip, rake, cine_1, cine_2):
    """
    Ejecuta el proceso completo de normalización básica.

    Orden:
    1. Conversión estructural y validación de longitudes.
    2. Normalización de valores.
    3. Validación de tipos.
    4. Validación de datos obligatorios.
    5. Normalización cinemática.
    6. Validación de rangos angulares.

    Reglas:
    - No completa datos ausentes.
    - No repite registros.
    - No elimina registros.
    - No modifica las entradas originales.
    - Conserva el orden de los registros.

    Retorna:
        dict: Base de datos normalizada.

    Raises:
        ValueError: Si se detectan errores estructurales
                    o de validación.
        TypeError: Si la entrada contiene tipos no permitidos.
    """

    # 1. Conversión estructural y validación de longitudes
    data = validate_input_lengths(
        strike, dip, rake, cine_1, cine_2
    )

    # 2. Normalización de valores
    data = normalize_basic_values(data)

    # 3. Validación de tipos
    validate_data_types(data)

    # 4. Validación de datos obligatorios
    validate_required_values(data)

    # 5. Normalización cinemática
    data = normalize_cinematic_values(data)

    # 6. Validación de rangos angulares
    validate_angle_ranges(data)

    return data