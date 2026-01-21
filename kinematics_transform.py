import numpy as np
from . import kinematics_logic
from . import kinematics_math

def _rake_to_x(dip, rake, valor_cinematic):

    kinematics_logic._validate_rake( rake, valor_cinematic)

    mag = kinematics_math.changes_magnitud_rake(dip, rake, valor_cinematic)

    # Sx → izquierda
    if valor_cinematic < 0:
        return -mag

    # Dx → derecha
    return +mag

def _dip_to_y(dip, rake, valor_cinematic):


    y_mag = 1 - dip / 90 # formula de conversion
# caso donde rake es 180 y 0
    if  valor_cinematic > 0:
        if rake == 180:
            return -y_mag
        elif rake == 0:
            return y_mag
    elif valor_cinematic < 0:
        if rake == 180:
            return y_mag
        elif rake == 0:
            return -y_mag

#dip igual a 0
    if dip == 0:

        if valor_cinematic > 0:  # Nx
            return y_mag if rake < 90 else -y_mag

        if valor_cinematic < 0:  # Sx
            return -y_mag if rake < 90 else +y_mag


    # Ix arriba | Nx abajo
    if valor_cinematic in (-1, 2, -4):# Ix, SxIx and IxDx inicia c ontar desde arria osea desde +1
        return +y_mag
    # si no se cumple esto inicia a contar desde abajo o desde -1
    return -y_mag

def dip_rake_to_xy(dip, rake, cine_1, cine_2=None):
    dip, rake, cine_1, cine_2 = np.atleast_1d(dip, rake, cine_1, cine_2)

    valor_cinematic = kinematics_logic._cinematic_main(cine_1, cine_2)


    # -----------------
    # DIP → Y
    # -----------------
    xs, ys = [], []
    for d, r, vc in zip(dip, rake, valor_cinematic):
        y = _dip_to_y(d, r, vc)
        ys.append(y)
    # -----------------
    # RAKE → X (ida y vuelta)
    # -----------------

        x = _rake_to_x(d, r, vc)
        xs.append(x)

    return np.array(xs), np.array(ys)

def strike_to_xy(strike, r=1.5):
    strike = np.atleast_1d(strike)

    if np.any((strike < 0) | (strike >= 360)):
        raise ValueError("Strike debe estar entre 0 y 360")

    theta = np.radians(90 - strike)
    x = r * np.cos(theta)
    y = r * np.sin(theta)

    return x, y