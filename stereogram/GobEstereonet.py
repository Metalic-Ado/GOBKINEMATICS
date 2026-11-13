import numpy as np
import mplstereonet
from mplstereonet import stereonet_math
from functools import wraps  # mantiene el nombre de la function original que se está decorando


# DATOS: PARA PLANOS O LINEAS QUE INTERACCIONAN LOS DATOS DEBERÁN NO ESTAR EN LISTA, LAS SALIDAS SIEMPRE SERAN EN LISTAS


def validate_ranges(ranges):
    """
    ranges: lista de tuplas [(min, max), ...] para cada argumento
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            validated_args = []

            for arg, (vmin, vmax) in zip(args, ranges):
                arr = np.atleast_1d(arg)

                if not np.issubdtype(arr.dtype, np.number):
                    raise TypeError("Los valores deben ser numéricos")

                if np.any(arr < vmin) or np.any(arr > vmax):
                    raise ValueError(
                        f"Valores fuera del rango permitido [{vmin}, {vmax}]"
                    )

                validated_args.append(arr)

            return func(*validated_args, **kwargs)

        return wrapper
    return decorator



# __________________________________________________ libreria Mejorada ___________________________________________________________


@validate_ranges([(0, 360), (0, 90), (0, 180)])   # valida que la entrada de datos este dentro de esos rangos
def _rake_to_plungeandtrend(strike, dip, rake):
    """
    Convierte el rake de un plano es un plunge y un trend
    :param strike: tipo array.
    :param dip:  tipo array.
    :param rake: tipo array.
    :return: plunge, trend
    """
    strike, dip, rake = np.atleast_1d(strike, dip, rake)  # muy importante hace que strike, dip, rake se pueda usar en lista y suelto
    plunge = np.zeros_like(strike, dtype=float)  # crea una lista rellenada por ceros de acuerdo al numero de datos de strike se tiene
    trend = np.zeros_like(strike, dtype=float)
    for i, (s, d, r) in enumerate(zip(strike, dip, rake)):  # i es para rellenar las listas de arriba zip UNE cosas en paralelo
        # caso 1: si r es igual de 90 y d es igual a 90
        if r == 90 and d == 90:
            plunge[i] = 90
            trend[i] = 90
        # caso 2: si r es diferente de 90 y d es igual a 90
        elif r != 0 and d == 90:
            if r < 90:
                plunge[i] = r
                trend[i] = s
            elif r > 90:
                plunge[i] = 180 - r
                trend[i] = (s + 180) % 360

        # caso 3: si d es igual a 0 y r es igual a 0
        elif d == 0 and r == 0:
            plunge[i] = 0
            trend[i] = s
        # caso 4: si d es igual a 0
        elif d == 0:
            plunge[i] = 0
            trend[i] = (s + r) % 360
        # caso 5: si r es igual a 0 o r es igual a 180
        elif r == 0 or r == 180:
            plunge[i] = 0
            trend[i] = (s + r) % 360
        else:
            lon, lat = stereonet_math.rake(s, d, r)
            p, t = mplstereonet.geographic2plunge_bearing(lon, lat)
            plunge[i] = p[0]
            trend[i] = t[0]
    return plunge, trend


@validate_ranges([(0, 360), (0, 90), (0, 90), (0, 360)])
def _pitches(strike, dip, plunge, trend):
    strike, dip, plunge, trend = np.atleast_1d(strike, dip, plunge, trend)
    rake = mplstereonet.project_onto_plane(strike, dip, plunge, trend)
    rake = np.where(rake < 0, rake + 180, rake)
    return rake


@validate_ranges([(0, 360), (0, 90), (0, 180), (0, 360), (0, 90), (0, 180)])
def _plane_from_rakes_pairs(strike0, dip0, rake0, strike1, dip1, rake1):
    strike0, dip0, rake0 = np.atleast_1d(strike0, dip0, rake0)
    strike1, dip1, rake1 = np.atleast_1d(strike1, dip1, rake1)

    strikes = []
    dips = []

    for s0, d0, r0, s1, d1, r1 in zip(
        strike0, dip0, rake0,
        strike1, dip1, rake1
    ):
        s, d = mplstereonet.fit_girdle(
            [s0, s1],
            [d0, d1],
            [r0, r1],
            measurement="rakes"
        )
        strikes.append(s)
        dips.append(d)

    return np.array(strikes), np.array(dips)


@validate_ranges([(0, 90), (0, 360), (0, 90), (0, 360)])
def _plane_from_lines_pairs(plunge0, trend0, plunge1, trend1):
    plunge0, trend0 = np.atleast_1d(plunge0, trend0)
    plunge1, trend1 = np.atleast_1d(plunge1, trend1)
    strike = []
    dip = []
    for p0, t0, p1, t1 in zip(plunge0, trend0, plunge1, trend1):
        s, d = mplstereonet.fit_girdle(
            [p0, p1],
            [t0, t1],
            measurement="lines"
        )
        strike.append(s)
        dip.append(d)
    return np.array(strike), np.array(dip)


@validate_ranges([(0, 90), (0, 360), (0, 90), (0, 360)])
def _distance_angular_between_lines_pairs(plunge0, trend0, plunge1, trend1, complement = True):
    plunge0, trend0 = np.atleast_1d(plunge0, trend0)
    plunge1, trend1 = np.atleast_1d(plunge1, trend1)
    strike, dip = _plane_from_lines_pairs(plunge0, trend0, plunge1, trend1)
    rake_0 = _pitches(strike, dip, plunge0, trend0)
    rake_1 = _pitches(strike, dip, plunge1, trend1)

    angle = np.abs(rake_1 - rake_0)

    if not complement:
        angle = 180 - angle

    return angle

# Falta una funcion que calcule el angulo entre dos planos o la distancia angular entre dos planos

@validate_ranges([(0, 360), (0, 90), (0, 180)])
def _planes_inverse(strike, dip, rake):
    strike, dip, rake = np.atleast_1d(strike, dip, rake)
    lon, lat = stereonet_math.pole(strike, dip)
    plunge, trend = mplstereonet.geographic2plunge_bearing(lon, lat)
    rake_pole = (rake + 90) % 180
    plunge_rake_pole, trend_rake_pole = _rake_to_plungeandtrend(strike, dip, rake_pole)
    strike_inv, dip_inv = _plane_from_lines_pairs(plunge, trend, plunge_rake_pole, trend_rake_pole)
    return strike_inv, dip_inv



# _____________________________________________________FIN ___________________________________________________________________________
















#  ________________________________________________________________________________________________________________________

#  _______________________________CAPITULO PARA ROTACIONES EN EL STEREOGRAMA


def _rot_x(angle):
    """
    REPRESENTA EL TREND DEL EJE DE ROTACION
    :param angle:
    :return:
    """
    MX = np.array([[1, 0, 0],
                   [0, np.cos(np.radians(angle)), - np.sin(np.radians(angle))],
                   [0, np.sin(np.radians(angle)), np.cos(np.radians(angle))]])  # para el eje central del estereograma
    return MX


def _rot_y(angle):
    """
    REPRESENTA AL PLUNGE DEL EJE 270 - 90 eje horizontal
    :param angle:
    :return:
    """
    MY = np.array([[np.cos(np.radians(angle)), 0, np.sin(np.radians(angle))],
                   [0, 1, 0],
                   [- np.sin(np.radians(angle)), 0, np.cos(np.radians(angle))]])
    return MY


def _rot_z(angle):
    """
    REPRESENTA AL eje 0 - 180
    :param angle:
    :return:
    """
    MZ = np.array([[np.cos(np.radians(angle)), - np.sin(np.radians(angle)), 0],
                   [np.sin(np.radians(angle)), np.cos(np.radians(angle)), 0],
                   [0, 0, 1]])
    return MZ


def eje_rot(plunge, trend):
    plunge= (plunge + 0)%90
    trend = (trend+0)%360
    MY = _rot_y(plunge)
    MX = _rot_x(-trend)
    M_eje = MX @ MY
    return M_eje


def _cantidad_giro_desde_eje(plunge, trend, angle):
    M_eje = eje_rot(plunge, trend)
    giro_y = _rot_z(angle)
    M_giro_eje = M_eje @ giro_y @ M_eje.T
    return M_giro_eje


def lonlat_a_xyz(lon, lat):
    x, y, z = stereonet_math.sph2cart(lon, lat)
    vector = np.hstack((x, y, z))
    return vector


def vector_giro_matriz(vector, matriz):
    vec_girado = np.dot(matriz, vector)
    x, y, z = vec_girado
    lon, lat = stereonet_math.cart2sph(x, y, z)
    return lon, lat


class RotationStereonet:
    def __init__(self, plunge_eje, trend_eje, angle, plunge, trend):
        self.plunge_eje = plunge_eje
        self.trend_eje = trend_eje
        self.angle = angle
        self.plunge = plunge
        self.trend = trend

        self.lon, self.lat = stereonet_math.line(self.plunge, self.trend)
        self.giro_eje = _cantidad_giro_desde_eje(self.plunge_eje, self.trend_eje, self.angle)
        self.vector = lonlat_a_xyz(self.lon, self.lat)

    def run(self):

        LON, LAT = vector_giro_matriz(self.vector, self.giro_eje)

        return LON, LAT

    def plot(self, ax):
        ax.line(self.plunge_eje, self.trend_eje, color='red')
        ax.line(self.plunge, self.trend, color='blue')
        lon, lat = self.run()
        ax.scatter(lon, lat, color='black')

