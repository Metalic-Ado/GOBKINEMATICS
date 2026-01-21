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
    if valor_cinematic in (2, -2):  # 0–90
        return 1.0 - (rake / 90.0)

    elif valor_cinematic in (4, -4):  # 90–180
        return 1.0 - (180.0 - rake) / 90.0

    # Seguridad
        raise ValueError(
        f"Combinación no válida: dip={dip}, rake={rake}, valor_cinematic={valor_cinematic}"
    )

