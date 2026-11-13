
def clasify_for_items(strike, dip, rake, cine_1, cine_2):
    """
    Clasifica cada registro según la cantidad de datos presentes.

    N5: 5 datos presentes.
    N4: 4 datos presentes.
    N3: 3 datos presentes.
    N2: 2 datos presentes.
    N1: 1 dato presente.
    INVALID0: ningún dato presente.

    Recibe datos previamente normalizados por norm_basic.py.

    Esta función:
    - Cuenta los valores diferentes de None.
    - Asigna la clasificación correspondiente.
    - Identifica registros sin strike.
    - Conserva los datos y el orden de los registros.

    No normaliza, valida tipos, evalúa geometría,
    evalúa cinemática ni modifica los datos.
    """

    # 1. Organizar los campos recibidos
    data = {
        "strike": strike,
        "dip": dip,
        "rake": rake,
        "cine_1": cine_1,
        "cine_2": cine_2
    }

    campos = (
        "strike",
        "dip",
        "rake",
        "cine_1",
        "cine_2"
    )

    resultados = []

    # 2. Recorrer los registros
    n_registros = len(strike)

    for i in range(n_registros):

        registro_datos = {
            campo: data[campo][i]
            for campo in campos
        }

        # 3. Contar datos presentes
        n_valid = sum(
            valor is not None
            for valor in registro_datos.values()
        )

        # 4. Asignar clasificación
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

        # 5. Identificar ausencia de strike
        if registro_datos["strike"] is None:
            estado = "invalido"
            motivo = "strike_ausente"

        else:
            estado = "sin_evaluar"
            motivo = None

        # 6. Guardar resultado
        resultados.append({
            "id": i + 1,
            "clase": clase,
            "datos": registro_datos,
            "estado": estado,
            "motivo": motivo
        })

    return resultados
