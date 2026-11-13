import mplstereonet
from mplstereonet import stereonet_math
from GOBESTEREONET import GobEstereonet
import numpy as np
from shapely import geometry, ops
from collections import defaultdict

#  que tengo que hacer arreglar los graficos de fallas, hacer el grafico para estrain ellipsoide y el grafico del strain de cizalla en
#  el estereonet, tambien hacer los graficos para los pliegues, hacer el grafico de de mohr con 3 strain, hacer los graficos para clastos
# hacer el grafico de flochis, hacer nuestro grafico, hacer el circulo de mohr, hacer las inversas de stress paleoestrss
# hacer perfiles


def _coord_circunference(angle=0.1, segment=500):

    """
    Crea las coordenadas de una circunferencia utilizando el plunge y el trend
    :param angle: Angulo de Plunge de la circunferencia, deberá ser cercano a 0
    :param segment: Número de separaciones
    :return: lon, lat
    """

    plunge = angle * np.ones(segment).reshape(segment, 1)  # se crea una lista de 500 datos del angulo, reshape sirve para crear la lista
    trend = np.linspace(0, 360, segment).reshape(segment, 1)  # crea una lista de 500 datos del trend que va desde 0 hasta 360
    lon, lat = stereonet_math.line(plunge, trend)  # Se extrae las coordenadas lon, lat de esa listas de datos

    return lon, lat


def _plane_inverse(strike, dip, rake):
    """
    Se crea un plano inverso utilizando el strike dip y rake
    :param strike: medida en grados de 0 - 360
    :param dip:  medida en grados de 0 - 90
    :param rake:  medida en grados de 0 - 180
    para las medidas se utiliza la hand right rule
    :return:
    """
    lon, lat = stereonet_math.pole(strike, dip)  # Se halla el polo del plano principal en lon, lat
    P0, T0 = mplstereonet.geographic2plunge_bearing(lon, lat)  # transform lon, lat del polo en plunge y trend

    # Nos aseguramos que los datos de input del rake este en una lista o de manera sola para utilizarlo
    if isinstance(rake, (int, float)):
        rake2 = (rake + 90) % 180  # El porcentaje means que no tiene que pasar de ese número
    elif isinstance(rake, list):  # isinstance verifica si la variable cumpla cierto tipo de dato ya sea una lista, int, float etc
        rake2 = (rake[0] + 90) % 180
    else:
        raise TypeError("rake debe ser un número o una lista")

    P, T = GobEstereonet.Rake_a_PlungeyTrend(strike, dip, rake2)  # Hallamos el plunge y trend del nuevo rake
    S, D = GobEstereonet.Planos_desde_lineas(P0, T0, P, T)  # joining los dos Puntos para crear un plano S, D
    return S, D


def _plane_inverse2(strike, dip, rake):  # lISTA
    """
    Se crea un plano inverso utilizando el strike dip y rake
    :param strike: medida en grados de 0 - 360
    :param dip:  medida en grados de 0 - 90
    :param rake:  medida en grados de 0 - 180
    para las medidas se utiliza la hand right rule
    :return:
    """
    lon, lat = stereonet_math.pole(strike, dip)  # Se halla el polo del plano principal en lon, lat
    P0, T0 = mplstereonet.geographic2plunge_bearing(lon, lat)  # transform lon, lat del polo en plunge y trend

    rake2 = []
    for i in range(len(rake)):
        rake2.append((rake[i] + 90) % 180)

    P, T = GobEstereonet.Rake_a_PlungeyTrend(strike, dip, rake2)  # Hallamos el plunge y trend del nuevo rake

    strike_inv_list = []
    dip_inv_list = []

    for i in range(len(P0)):
        S, D = GobEstereonet.Planos_desde_lineas2(P0[i], T0[i], P[i], T[i])

        strike_inv_list.append(S)
        dip_inv_list.append(D)

    return strike_inv_list, dip_inv_list


# DESDE AQUI SE GENERA GEOMETRIES EN FORMATO SHAPELY PLANOS, POLIGONOS Y PUNTOS


def _shape(shape_type, strike=0, dip=0, angle=0.1):
    """
    Shape genera líneas o poligonos de acuerdo al dato: Linestring para planos, y polygon para la circunferencia
    """
    if shape_type == 'plane':
        lon, lat = stereonet_math.plane(strike, dip)
        return geometry.LineString(np.hstack((lon, lat)))  # Se coloca de esta manera para que Shapefile lo reconosca

    elif shape_type == 'base':
        lon, lat = _coord_circunference(angle)
        return geometry.Polygon(np.hstack((lon[1:-1], lat[1:-1])))

# Puntos para el caso general, lo que manda es el Dx y el Sx


def _shape_point_strike(cinematica, cinematica2, strike):
    """
    Crea un punto geometrico para utilizarlo como sentido cinematico para el caso general
    :param cinematica: puede ser Dx o Sx
    :param cinematica2: puede ser Dx o Sx
    :param strike: medida en grados de 0 - 360°
    :return: Punto geometrico
    """
    if cinematica == 'Dx' or cinematica2 == 'Dx':  # Si se encuentra 'Dx en el primer o segundo termino
        SD = (strike[0] - 1) % 360  # Si en caso esto es verdad se le resta 1 al strike, este no debe de pasar de 360
        lon, lat = stereonet_math.line([0.05], [SD])  # se halla lon, lat del punto con un plunge cercano a 0 y el trend hallado
        return geometry.Point(np.hstack((lon, lat)))  # Se convierte en geometría
    elif cinematica == 'Sx' or cinematica2 == 'Sx':
        SD = (strike[0] + 1) % 360
        lon, lat = stereonet_math.line([0.05], [SD])
        return geometry.Point(np.hstack((lon, lat)))


# Para casos especiales


def _shape_point_strike2(cinematica, strike):
    """
    Crea geometria utilizando una sola cinematica Ix o Nx la cual manda en este caso
    :param cinematica: Ix o Nx solo se usa en caso especial
    :param strike: en grados 0 - 360°
    :return: geometria del punto
    """
    if cinematica == 'Ix':  # si cinematica es igual a Ix entonces se resta
        SD = (strike[0] + 1) % 360   # plunge del nuevo punto
        lon, lat = stereonet_math.line([0.1], [SD])
        return geometry.Point(np.hstack((lon, lat)))
    elif cinematica == 'Nx':
        SD = (strike[0] + 1) % 360
        lon, lat = stereonet_math.line([0.1], [SD])
        return geometry.Point(np.hstack((lon, lat)))


def _shape_point_pole(pole, strike, dip):
    """
    Crea un punto a partir del polo de un plano
    :param pole: estructura 'Pole'
    :param strike: grados 0 - 360°
    :param dip: grados de 0 - 90°
    :return: punto geometrico
    """
    if pole == 'Pole':
        lon, lat = stereonet_math.pole(strike, dip)
        return geometry.Point(np.hstack((lon, lat)))


def _shape_point_rake(cinematica, plunge, trend):
    """
    Crea un punto geometrico a partir del Plunge y Trend del rake de la falla con su cinematica
    :param cinematica: Nx e Ix
    :param plunge: 0 - 90 en grados
    :param trend: 0 - 360° en grados
    :return: punto geometrico
    """
    if cinematica == 'Ix':
        po = [plunge[0] + 1]
        lon, lat = stereonet_math.line(po, trend)
        return geometry.Point(np.hstack((lon, lat)))
    elif cinematica == 'Nx':
        po = [plunge[0] - 1]
        lon, lat = stereonet_math.line(po, trend)
        return geometry.Point(np.hstack((lon, lat)))

# ___________________COLORIMETRIA DE LOS DIEDROS SEGUN SU CINEMATICA


def _color(cinematica, cinematica2, rake):
    """
    ASIGNA COLOR SEGÚN SU DOS CINEMATICA Y SEGÚN LAS COMBINACIONES DE ESTA Nx, Sx, Ix, Dx
    :param cinematica: primer tipo de cinematica
    :param cinematica2: segundo tipo de cinematica
    :param rake: valores en grados de 0 - 180°
    :return: color white o black
    """
    cinematica_set = {cinematica, cinematica2}  # Primero se crea un conjunto que abarque las dos cinematicas esto por razones para que las variables puedan ser intercambiables

    # _______________ PARA DEXTRAL
    if 'Dx' in cinematica_set and 'Ix' in cinematica_set:  # si hay Dx y Ix obligatoriamente el rake debe ser menor que 90
        if rake < 90:
            return 'white'  # Si la condición se cumple devolverá el color black
        elif rake == 90:
            raise ValueError("Error: rake no puede ser 90°")
        elif rake > 90:
            raise ValueError("Error: rake no puede ser mayor que 90°")

    elif 'Dx' in cinematica_set and 'Nx' in cinematica_set:  # Si hay Dx y Nx entonces rake > 90
        if rake > 90:
            return 'white'  # Si se cumple devuelve white, si no dará error
        elif rake == 90:
            raise ValueError("Error: rake no puede ser 90°")
        elif rake < 90:
            raise ValueError("Error: rake no puede ser menor que 90°")

    # Casos especiales
    elif 'Dx' in cinematica_set and cinematica2 is None:  # Si solo hay un Dx entonces el rake sera 0 ó 180
        if rake == 0 or rake == 180:
            return 'black'
    elif 'Dx' in cinematica_set and 'Dx' in cinematica_set:  # Si se repiten los valores dará error
        raise ValueError("Error: No puede existir dos cinematicas Dx°")

    # ______________PARA SINESTRAL
    elif 'Sx' in cinematica_set and 'Nx' in cinematica_set:  # Si Sx y Nx entonces rake < 90
        if rake < 90:
            return 'white'  # Devuelve color blanco o error si no se cumple
        elif rake == 90:
            raise ValueError("Error: rake no puede ser 90°")
        elif rake > 90:
            raise ValueError("Error: rake no puede ser mayor que 90°")

    elif 'Sx' in cinematica_set and 'Ix' in cinematica_set:  # Si Sx y Ix entonces rake mayor que 90
        if rake > 90:
            return 'black'
        elif rake == 90:
            raise ValueError("Error: rake no puede ser 90°")
        elif rake < 90:
            raise ValueError("Error: rake no puede ser menor que 90°")

    # Casos Especiales
    elif 'Sx' in cinematica_set and cinematica2 is None:  # Si solo hay Sx entonces el rake es 0 ó 180°
        if rake == 0 or rake == 180:
            return 'white'
    elif 'Sx' in cinematica_set and 'Sx' in cinematica_set:  # Si se repiten los valores dará error
        raise ValueError("Error: No puede existir dos cinematicas Sx°")

    # Casos especiales Inversa y Normal

    elif 'Ix' in cinematica_set and cinematica2 is None:  # Si solo hay Ix se asume que el rake es igual a 90°
        if rake == 90:
            return 'black'
    elif 'Ix' in cinematica_set and 'Ix' in cinematica_set:  # Si se repiten los valores dará error
        raise ValueError("Error: No puede existir dos cinematicas Ix°")

    elif 'Nx' in cinematica_set and cinematica2 is None:  # Si solo hay Nx se asume que el rake es igual a 90°
        if rake == 90:
            return 'white'
    elif 'Nx' in cinematica_set and 'Nx' in cinematica_set:  # Si se repiten los valores dará error
        raise ValueError("Error: No puede existir dos cinematicas Nx°")


def _color2(cinematic, cinematic2, dip):
    cinematica_set = {cinematic, cinematic2}
    if None in cinematica_set and None in cinematica_set:  # si hay Dx y Ix obligatoriamente el rake debe ser menor que 90
        if dip == 0:
            return 'black'  # Si la condicion se cumple devolvera el color black
        elif dip != 0:
            raise ValueError("Error: el dip tiene que ser cero°")


def _color3(cinematic, cinematic2, rake, dip):
    if rake == 90 and dip == 90:
        if cinematic == 'Nx' and cinematic2 is None:
            return 'white'
        elif cinematic == 'Ix' and cinematic2 is None:
            return 'black'


# ____________________________________________ FINAL DE LOS DATOS_______--AÚN FALTA CON EL DIP PERO MAS ADELANTE

# _____________________________________________ANALISIS DE LOS DIEDROS RECTOS


class AnalisisDiedrosInversos:

    def __init__(self, strike, dip, rake, cinematica=None, cinematica2=None):

        """
        ANALISIS DE DIEDROS INVERSOS
        :param strike: de 0 - 360° en grados
        :param dip:  0 - 90° en grados
        :param rake:  0 - 180 en grados
        :param cinematica:  Nx, Dx, Sx, Ix
        :param cinematica2:  Nx, Dx, Sx, Ix
        """
        self.strike = strike
        self.dip = dip
        self.rake = rake
        self.cinematica = cinematica
        self.cinematica2 = cinematica2

        # _______________________CALCULOS INICIALES
        self.S_second, self.D_second = self.calcular_plano_inverso()  # PLANO INVERSO
        self.Plunge_rake, self.Trend_rake = self.calcular_plunge_y_trend()  # PLUNGE Y TREND del CABECEO

        # _______________________GEOMETRIAS NECESARIAS UTILIZADAS EN SHAPELY PARA EL CALCULO TOPOLOGICO
        self.BASE = _shape('base', angle=0.01)  # La base de la circunferencia / polygon
        self.plane_main = _shape('plane', self.strike, self.dip)  # plano principal / Linestring
        self.plane_second = _shape('plane', self.S_second, self.D_second)  # plano secundaria o inverso / Linestring

        # Geometria Secundaria
        # __ Caso General
        self.point_strike = self.shape_point_strike(self.cinematica, self.cinematica2)  # Punto geometrico de referencia Dx o Sx
        self.point_strike_inv = self.shape_point_strike(self.point_strike_inv(self.cinematica), self.point_strike_inv(self.cinematica2))  # Inversa del Punto

        # ___Caso donde se usa el polo y el punto de rake
        self.pole = self.pole_geometric('Pole')

        # ___ Caso especial donde el dip es igual a cero
        self.point2 = self.calcular_punto('Ix')  # Se coloca Ix puesto con esto sumo el plunge cero y lo vuelvo en 1 para hallar la zona

        # ____ Caso especial donde el dip es 90 y el rake 90
        self.pointstrike = self.calcular_punto_strike(self.cinematica)

    # _____________________________FUNCIONES NECESARIAS PARA LOS CALCULOS DE ARRIBA 0 CALCULOS INICIALES

    def calcular_plano_inverso(self):  # Función que calculo el plano inverso segun dos datos de strike  dip y rake
        return _plane_inverse(self.strike, self.dip, self.rake)  # devuelve strike y dip

    def calcular_plunge_y_trend(self):  # Función que calculo el Plunge y Trend del Cabeceo
        return GobEstereonet.Rake_a_PlungeyTrend(self.strike, self.dip, self.rake)

    #  _____________________________FUNCIONES NECESARIAS PARA LAS GEOMETRIAS UTILIZADAS EN SHAPELY ARRIBA
    # Modo general / aquí manda Dx y Sx
    def shape_point_strike(self, cinematica, cinematica2):  # Crea un punto geometrico a partir de las cinematicas y el strike
        return _shape_point_strike(cinematica, cinematica2, self.strike)  # devuelve un punto geometrico

    def point_strike_inv(self, cinematica):  # Funcion que invierte las cinematicas si es Dx EN Ix
        if cinematica == 'Dx':
            return 'Sx'
        elif cinematica == 'Sx':
            return 'Dx'

    # Modo polo para el analisis 2 y 3
    def pole_geometric(self, pole):  # Crea un polo en un punto geometrico usando el strike dip y pole
        return _shape_point_pole(pole, self.strike, self.dip)

    def calcular_punto(self, cinematica):  # Se halla el el punto geometrico del plunge y trend del rake
        return _shape_point_rake(cinematica, self.Plunge_rake, self.Trend_rake)

    def invertir_cinematica(self):
        if self.cinematica == 'Ix':
            return 'Nx'
        elif self.cinematica == 'Nx':
            return 'Ix'
        else:
            raise ValueError("Cinematica no reconocida")

    # Modo polo para el analisis 4

    def calcular_punto_strike(self, cinematica):
        return _shape_point_strike2(cinematica, self.strike)

    # ___________________________________________________

    # _________ INVERSION DEL COLOR

    def inverso_color(self, color):
        if color == 'white':
            return 'black'
        elif color == 'black':
            return 'white'

    # _________________-CALCULO PARA EL GRAFICO DE ARROWS

    def arrows(self, cinematica, cinematica2):
        plunge, trend = self.calcular_plunge_y_trend()
        lon, lat = stereonet_math.line(plunge, trend)
        mag = np.hypot(lon, lat)
        if cinematica == 'Nx' or cinematica2 == 'Nx':
            u, v = lon / mag, lat / mag
            return lon, lat, u, v
        elif cinematica == 'Ix' or cinematica2 == 'Ix':
            u, v = -lon / mag, -lat / mag
            return lon, lat, u, v

    # ________________________________________TIPOS DE ANALISIS GEOMÉTRICOS Y SUS CONDICIONES ________________________
    def analisis_general(self):  # Genera cuatro poligonos

        # ____________GEOMETRIA ___________PRIMER CORTE
        primer_corte = ops.split(self.BASE, self.plane_main)  # split corta en dos la base con el plano main

        if self.point_strike.intersects(primer_corte.geoms[0]):  # se busca el poligono que intersecta con el punto geometrico
            area_prin = primer_corte.geoms[0]
            area_sec = primer_corte.geoms[1]
        else:
            area_prin = primer_corte.geoms[1]
            area_sec = primer_corte.geoms[0]

        # _____________________SEGUNDO CORTE QUE SE HACE A EL AREA PRINCIPAL
        second_corte = ops.split(area_prin, self.plane_second)

        if self.point_strike.intersects(second_corte.geoms[0]):  # Se busca la interseccion entre el punto geometrico y el diedro principal
            diedro_prin1 = second_corte.geoms[0]  # diedro principal
            diedro_second1 = second_corte.geoms[1]  # diedro secundario
        else:
            diedro_prin1 = second_corte.geoms[1]
            diedro_second1 = second_corte.geoms[0]

        # ________________________TERCER CORTE QUE SE HACE A EL AREA SECUNDARIA
        tercer_corte = ops.split(area_sec, self.plane_second)

        if self.point_strike_inv.intersects(tercer_corte.geoms[0]):  # Se usa el punto inverso geometrico para hallar el diedro secundario
            diedro_second2 = tercer_corte.geoms[0]
            diedro_prin2 = tercer_corte.geoms[1]
        else:
            diedro_second2 = tercer_corte.geoms[1]
            diedro_prin2 = tercer_corte.geoms[0]

        return diedro_prin1, diedro_prin2, diedro_second1, diedro_second2  # retorna los 4 poligonos separados en diedros principales y secundarios

    def analisis_polygon_3(self):  # ESTA FUNCIÓN DEVUELVE 3 POLIGONOS SOLO SE USA CUANDO EL RAKE ES 90 GRADOS

        # _____________________________PRIMER CORTE
        primer_corte = ops.split(self.BASE, self.plane_main)

        if self.pole.intersects(primer_corte.geoms[0]):  # Se usa el polo geometric para hallar el área main que lo contiene
            area_main = primer_corte.geoms[0]  # diedro main ya es un diedro principal
            diedro_main = primer_corte.geoms[1]
        else:
            area_main = primer_corte.geoms[1]
            diedro_main = primer_corte.geoms[0]

        # _______________________________SEGUNDO CORTE
        second_corte = ops.split(area_main, self.plane_second)
        self.point_inverso = self.calcular_punto(self.invertir_cinematica())
        if self.point_inverso.intersects(second_corte.geoms[0]):
            diedro_second2 = second_corte.geoms[0]
            diedro_prin2 = second_corte.geoms[1]
        else:
            diedro_second2 = second_corte.geoms[1]
            diedro_prin2 = second_corte.geoms[0]

        # Retorno basado en la condición que definiste
        return diedro_main, diedro_prin2, diedro_second2

    def analisis_polygon_2(self):  # Este analisis devuelve dos poligonos / Cuando el dip es igual a cero

        # Cuando el dip es cero, el rake debe representar no solamente la dirección de la estría, sino también el sentido
        # Repito en este analisis el sentido de la falla estará dado por el rake aquí no existe Nx Ix, Sx, Dx

        # ________________________________________PRIMER CORTE
        primer_corte = ops.split(self.BASE, self.plane_second)  # Cortamos la base con el plano inverso
        # Esto porque el dip es cero y está en la periferia y no se ve
        if self.point2.intersects(primer_corte.geoms[0]):
            diedro_main = primer_corte.geoms[0]
            diedro_second = primer_corte.geoms[1]
        else:
            diedro_main = primer_corte.geoms[1]
            diedro_second = primer_corte.geoms[0]

        return diedro_main, diedro_second

    def analisis_polygon_1(self):  # Caso especial donde el dip es 90 y el cabeceo es 90 solo funciona con Ix o Nx

        # _____________________________PRIMER CORTE
        primer_corte = ops.split(self.BASE, self.plane_main)

        if self.pointstrike.intersects(primer_corte.geoms[0]):  # Se busca la interseccion entre el punto de strike y la base
            diedro_main = primer_corte.geoms[0]
            diedro_second = primer_corte.geoms[1]
        else:
            diedro_main = primer_corte.geoms[1]
            diedro_second = primer_corte.geoms[0]

        return diedro_main, diedro_second

#  _____________________________________________RUN SOLO CORRER LOS POLIGONOS

    def run(self):

        if self.rake[0] == 90 and self.dip[0] != 0 and self.dip[0] != 90:  # este debe aceptar Ix o Nx
            m, m1, m2 = self.analisis_polygon_3()
            print('Es necesario 3 polígonos')

            self.color_m = _color(self.cinematica, self.cinematica2, self.rake[0])

            self.color_inv = self.inverso_color(self.color_m)

            return m, m1, m2  # Retorna 3 valores si la condición es True

        elif self.dip[0] == 0:  # este debe decir none none
            d_main, d_second = self.analisis_polygon_2()
            print('Es necesario 2 polígonos')

            self.color_d_main = _color2(self.cinematica, self.cinematica2, self.dip[0])
            self.color_d_main_inv = self.inverso_color(self.color_d_main)

            return d_main, d_second

        elif self.dip[0] == 90 and self.rake[0] == 90:  # solo debe aceptar Ix o Nx
            dd_main, dd_second = self.analisis_polygon_1()
            print('es necesario 2 poligonos')

            self.color_dd_main = _color3(self.cinematica, self.cinematica2, self.rake[0], self.dip[0])
            self.color_dd_main_inv = self.inverso_color(self.color_dd_main)

            print(f"Color principal: {self.color_dd_main}")
            print(f"Color inverso: {self.color_dd_main_inv}")
            print({self.color_dd_main:dd_main, self.color_dd_main_inv: dd_second})

            return {self.color_dd_main:dd_main, self.color_dd_main_inv: dd_second}

        else:
            a, b, c, d = self.analisis_general()  # este debe aceptar Dx Y Nx
            print('Cuatro polígonos')

            self.color_a = _color(self.cinematica, self.cinematica2, self.rake[0])
            self.color_inv2 = self.inverso_color(self.color_a)

            print({self.color_a: [a, b], self.color_inv2: [c, d]})
            return {self.color_a: [a, b], self.color_inv2: [c, d]}

    def run2(self, ax):

        if self.rake[0] == 90 and self.dip[0] != 0 and self.dip[0] != 90:  # este debe aceptar Ix o Nx
            m, m1, m2 = self.analisis_polygon_3()
            print('Es necesario 3 polígonos')

            lonm, latm = m.exterior.xy
            lonm1, latm1 = m1.exterior.xy
            lonm2, latm2 = m2.exterior.xy

            self.color_m = _color(self.cinematica, self.cinematica2, self.rake[0])

            self.color_inv = self.inverso_color(self.color_m)

            x, y, u, v = self.arrows(self.cinematica, self.cinematica2)

            ax.quiver(x, y, u, v, color='red', width=1, headwidth=4, units='dots', scale=0.01)
            ax.plane(self.strike, self.dip, c='red')
            ax.rake(self.strike, self.dip, self.rake, c='red')
            ax.fill(lonm, latm, self.color_m, alpha = 0.2)
            ax.fill(lonm1, latm1, self.color_m, alpha = 0.2)
            ax.fill(lonm2, latm2, self.color_inv, alpha = 0.2)
            ax.quiver(x, y, u, v, color='red', width=2, headwidth=4, units='dots', scale=0.04)

            return {self.color_m: [m, m1], self.color_inv: [m2]}  # Retorna 3 valores si la condición es True

        elif self.dip[0] == 0:  # este debe decir none none
            d_main, d_second = self.analisis_polygon_2()
            print('Es necesario 2 polígonos')

            lond_main, latd_main = d_main.exterior.xy
            lond_second, latd_second = d_second.exterior.xy

            self.color_d_main = _color2(self.cinematica, self.cinematica2, self.dip[0])
            self.color_d_main_inv = self.inverso_color(self.color_d_main)

            ax.plane(self.strike, self.dip)
            ax.rake(self.strike, self.dip, self.rake)
            ax.fill(lond_main, latd_main, self.color_d_main)
            ax.fill(lond_second, latd_second, self.color_d_main_inv)

            return {self.color_d_main: [d_main], self.color_d_main_inv: [d_second]}

        elif self.dip[0] == 90 and self.rake[0] == 90:  # solo debe aceptar Ix o Nx
            dd_main, dd_second = self.analisis_polygon_1()
            print('es necesario 2 poligonos')

            lond_main1, latd_main1 = dd_main.exterior.xy
            lond_second1, latd_second1 = dd_second.exterior.xy

            self.color_dd_main = _color3(self.cinematica, self.cinematica2, self.rake[0], self.dip[0])
            self.color_dd_main_inv = self.inverso_color(self.color_dd_main)

            print(f"Color principal: {self.color_dd_main}")
            print(f"Color inverso: {self.color_dd_main_inv}")

            ax.plane(self.strike, self.dip)
            ax.rake(self.strike, self.dip, self.rake)
            ax.fill(lond_main1, latd_main1, self.color_dd_main )
            ax.fill(lond_second1, latd_second1, self.color_dd_main_inv)

            print({self.color_dd_main: dd_main, self.color_dd_main_inv: dd_second})

            return {self.color_dd_main: [dd_main], self.color_dd_main_inv: [dd_second]}

        else:
            a, b, c, d = self.analisis_general()  # este debe aceptar Dx Y Nx
            print('Cuatro polígonos')

            lona, lata = a.exterior.xy
            lonb, latb = b.exterior.xy
            lonc, latc = c.exterior.xy
            lond, latd = d.exterior.xy

            self.color_a = _color(self.cinematica, self.cinematica2, self.rake[0])
            self.color_inv2 = self.inverso_color(self.color_a)

            x, y, u, v = self.arrows(self.cinematica, self.cinematica2)

            ax.plane(self.strike, self.dip, c='red')
            ax.rake(self.strike, self.dip, self.rake, c='red')
            ax.fill(lona, lata, self.color_a, alpha= 0.5)
            ax.fill(lonb, latb, self.color_a, alpha= 0.5)
            ax.fill(lonc, latc, self.color_inv2, alpha= 0.5)
            ax.fill(lond, latd, self.color_inv2, alpha= 0.5)
            ax.quiver(x, y, u, v, color='red', width=2, headwidth=4, units='dots', scale=0.04)

            print({self.color_a: [a, b], self.color_inv2: [c, d]})
            return {self.color_a: [a, b], self.color_inv2: [c, d]}

# esta clase ayuda a uilizar el codigo en tipo lista


class AnalisisdeDiedrosRectosLista:
    def __init__(self, strike, dip, rake, cine1, cine2, ax):
        self.strike = strike
        self.dip = dip
        self.rake = rake
        self.cine1 = cine1
        self.cine2 = cine2
        self.ax = ax

        self.Resultados = []
        for s, d, r, c1, c2 in zip(self.strike, self.dip, self.rake, self.cine1, self.cine2):
            self.Polygons = AnalisisDiedrosInversos([s], [d], [r], c1, c2).run2(self.ax)
            self.Resultados.append(self.Polygons)

# se necesita colocar el color ya sea blanco o negro y el resultado en formato diccionario


def _primera_intersection(resultado, color):
    first_polygon = []
    non_firs_intersection = []
    for i in range(len(resultado)):
        for j in range(i + 1, len(resultado)):
            color_polygon_1 = resultado[i][color]
            color_polygon_2 = resultado[j][color]
            for poly1 in color_polygon_1:
                for poly2 in color_polygon_2:
                    if poly1.intersects(poly2):
                        inter_polygon = poly1.intersection(poly2)
                        if inter_polygon.geom_type == 'Polygon':
                            first_polygon.append(inter_polygon)
                    else:
                        non_firs_intersection.append((poly1, poly2))
    return first_polygon  # retorna los poligonos que han sido interseccionado


def _second_intersection(first_intersection):
    second_polygon = []
    non_second_polygon = []
    polygon_count = defaultdict(int)

    for i in range(len(first_intersection)):
        for j in range(i + 1, len(first_intersection)):
            if first_intersection[i].intersects(first_intersection[j]):
                inter2_poly = first_intersection[i].intersection(first_intersection[j])
                if inter2_poly.geom_type == 'Polygon':
                    found = False
                    for p in second_polygon:
                        if inter2_poly.equals_exact(p, tolerance=3):
                            polygon_count[p] += 1
                            found = True
                            break
                    if not found:
                        second_polygon.append(inter2_poly)
                        polygon_count[inter2_poly] = 1
            else:
                non_second_polygon.append((first_intersection[i], first_intersection[j]))
    return second_polygon

# ______________________________________________________________________________________________________________________

# _________________________________________DIEDROS RECTOS ______________________________________________________________


# crea un diccionario en la cual estan todos los puntos con sus respectivos valores de la falla
def _diccionario_strike_dip_(strike, dip, rake):
    trend = np.linspace(0, 360, 60)  # Azimut (0 a 360 grados)
    plunge = np.linspace(0, 90, 20)  # Inmersión (0 a 90 grados)

    # Generar malla bidimensional
    trend_grid, plunge_grid = np.meshgrid(trend, plunge)
    # Aplanar las matrices para trabajar con vectores
    trend_flat = trend_grid.flatten()
    plunge_flat = plunge_grid.flatten()

    # Generar los vectores a partir de plunge y trend
    vectores = [gv.plungetrend_to_vector(p, t) for p, t in zip(plunge_flat, trend_flat)]

    vector_plane = gv._strike_dip_to_vector_normal(strike, dip)
    strike_inv, dip_inv = _plane_inverse(strike, dip, rake)
    vector_plane_inv = gv._strike_dip_to_vector_normal(strike_inv[0], dip_inv[0])

    d1 = np.array([np.dot(vector_plane, v) for v in vectores])
    d2 = np.array([np.dot(vector_plane_inv, v) for v in vectores])

    # Crear un array de ceros con el mismo tamaño que d1
    values = np.zeros_like(d1)

    # Aplicar las condiciones del diedro
    values[(d1 > 0) & (d2 > 0)] = 100  # Diedro P
    values[(d1 < 0) & (d2 < 0)] = 100  # Diedro T
    values[(d1 > 0) & (d2 < 0)] = 0  # Intersección
    values[(d1 < 0) & (d2 > 0)] = 0  # Otro caso

    values_grid = values.reshape(trend_grid.shape)

    # Crear el diccionario para almacenar los resultados
    result_dict = {}

    # Clasificar y almacenar los vectores convertidos a plunge y trend en sus respectivas zonas
    for vector, value in zip(vectores, values):
        # Convertir el vector a plunge y trend
        plunge, trend = gv._vector_to_plungetrend(vector)

        # Redondear para evitar problemas con flotantes
        plunge = round(plunge, 2)
        trend = round(trend, 2)

        # Agregar al diccionario con el par como clave y el valor como valor
        result_dict[(plunge, trend)] = value

    return result_dict

# Usaremos la idea del libro de Ramsay 3 en los que coloca los puntos de manera cuadricular, eso es solo para vista
# Agarra el punto 90, 90 para la clasificacion de los diedros
# entender como funciona el lon y lat en mplstereonet
# x y z son cosenos directores y lon y lat

# DIEDROS RECTOS
# TRIEDROS RECTOS
# TODOS LOS METODOS DE INVERSION

########################################################################################################################
############################################# DIEDROS RECTOS ###########################################################
########################################################################################################################

# ESTA LIBRERIA CONTIENE

# CRECION DEL PLANO INVERSO
# CREACION DE LOS POLIGONOS O DIEDROS
# CLASIFICACION DE LOS POLIGONOS
# VALORIZACION DE LOS POLIGONOS
# CONTEO DE LA VALORIZACION



def _coord_circunference(angle=0.1, segment=500):

    """
    Crea las coordenadas de una circunferencia utilizando el plunge y el trend
    :param angle: Angulo de Plunge de la circunferencia, deberá ser cercano a 0
    :param segment: Número de separaciones
    :return: lon, lat
    """
    plunge = angle * np.ones(segment).reshape(segment, 1)  # se crea una lista de 500 datos del angulo, reshape sirve para crear la lista
    trend = np.linspace(0, 360, segment).reshape(segment, 1)  # crea una lista de 500 datos del trend que va desde 0 hasta 360
    lon, lat = stereonet_math.line(plunge, trend)  # Se extrae las coordenadas lon, lat de esa listas de datos
    return lon, lat


def _shape(shape_type, strike=0, dip=0, plunge = 0, trend = 0, angle=0.1):
    """
    Shape genera líneas (plano), puntos (linea) o polígonos de acuerdo al dato: Linestring para planos, y polygon para la circunferencia
    """

    if shape_type == 'plane':
        lon, lat = stereonet_math.plane(strike, dip)
        return geometry.LineString(np.hstack((lon, lat)))  # Se coloca de esta manera para que Shapefile lo reconosca

    elif shape_type == 'line':
        lon, lat = stereonet_math.line([plunge], [trend])
        return geometry.Point(np.hstack((lon, lat)))

    elif shape_type == 'base':
        lon, lat = _coord_circunference(angle)
        return geometry.Polygon(np.hstack((lon[1:-1], lat[1:-1])))


# Crea poligonos segun el numero de diedros pertenecientes al tipo de plano de falla (Strike, Dip, Rake)

def cutt_diedros(strike, dip, rake):
    strike, dip, rake = np.atleast_1d(strike, dip, rake)

    base = _shape('base', angle=0.01)
    all_regions = []

    for s, d, r in zip(strike, dip, rake):

        regions = [base]   # ← ahora SÍ va aquí

        plane_main = _shape('plane', s, d)
        s2, d2 = ge._planes_inverse(s, d, r)
        plane_sec = _shape('plane', s2, d2)

        planes_to_use = []

        if r == 90 and d == 90:
            planes_to_use.append(plane_main)
        elif d == 0:
            planes_to_use.append(plane_sec)
        else:
            planes_to_use.append(plane_main)
            planes_to_use.append(plane_sec)

        for plane in planes_to_use:
            new_regions = []
            for reg in regions:
                try:
                    split_result = ops.split(reg, plane)
                    new_regions.extend(split_result.geoms)
                except Exception:
                    new_regions.append(reg)
            regions = new_regions

        all_regions.append(regions)

    return all_regions  # devuelve un numero de poligonos (4,3,2) depende de los datos de entrada


# Se clasifica a los diedros segun el valor 0 y 1 (donde 1 es el poligono que se encuentra en el centro y su conjugada)
# y 0 que no pertenece al centro y su conjungada

def clasy_polygon2(strike, dip, rake):
    Punto_central = _shape('line', 0,0,90,90)
    all_regions = cutt_diedros(strike, dip, rake)

    for region in all_regions:
        n = len(region)

        if n == 3:
            central_polygons = []

            for poly in region:
                if poly.intersects(Punto_central):
                    central_polygons.append(poly)

            print("Polígonos que intersectan el centro:", central_polygons)



def classify_case_3(region, punto_central, eps = 1e-6):
    """
    Clasifica un caso de 3 diedros.
    Devuelve:
      - central: lista con 1 polígono
      - others: lista con 2 polígonos
    """
    central = []
    others = []

    for poly in region:
        if poly.distance(punto_central) < eps:
            central.append(poly)
        else:
            others.append(poly)
    # revision de seguridad
    if len(central) != 1 or len(others) != 2:
        raise ValueError("Configuracion invalidad para 3 diedros")

    return central, others

def classify_case_2(region, punto_pole, eps = 1e-6):
    """
    Clasifica un caso de 2 diedros.
    Devuelve:
      - central: lista con 1 polígono
      - others: lista con 1 polígonos
    """
    central = []
    other = []

    for poly in region:
        if poly.distance(punto_pole) < eps:
            central.append(poly)
        else:
            other.append(poly)
    # revision de seguridad
    if len(central) != 1 or len(other) != 1:
        raise ValueError("Configuracion invalidad para 2 diedros")

    return central, other

# caso 4

def are_adjacent(polyA, polyB, eps=1e-9):
    inter = polyA.intersection(polyB)

    if inter.is_empty:
        return False

    # Línea compartida → adyacentes
    if inter.geom_type in ("LineString", "MultiLineString"):
        return inter.length > eps

    return False


def pair_diedros_case_4(region, eps=1e-9):
    if len(region) != 4:
        raise ValueError("Solo válido para 4 diedros")

    poly0 = region[0]

    adjacent = []
    opposite = []

    for poly in region[1:]:
        if are_adjacent(poly0, poly, eps):
            adjacent.append(poly)
        else:
            opposite.append(poly)

    # En un caso ideal:
    # poly0 tiene 2 adyacentes y 1 opuesto
    if len(adjacent) != 2 or len(opposite) != 1:
        raise ValueError(
            f"Configuración inválida: adj={len(adjacent)}, opp={len(opposite)}"
        )

    pair_1 = [poly0, opposite[0]]
    pair_2 = adjacent

    return pair_1, pair_2


def select_active_pair(pair_1, pair_2, punto_rake, eps=1e-6):
    """
    Devuelve:
      - active_pair: el par donde cae el movimiento
      - passive_pair: el otro par
    """

    def pair_distance(pair):
        return min(poly.distance(punto_rake) for poly in pair)

    d1 = pair_distance(pair_1)
    d2 = pair_distance(pair_2)

    if d1 < d2:
        return pair_1, pair_2
    else:
        return pair_2, pair_1



def clasy_polygon(strike, dip, rake):
    strike, dip, rake = np.atleast_1d(strike, dip, rake)

    all_regions = cutt_diedros(strike, dip, rake)

    results = []

    for i, region in enumerate(all_regions):
        n = len(region)

        s = strike[i]
        d = dip[i]
        r = rake[i]

        EPS_ANG = 1e-3
        trend = (s + r - EPS_ANG) % 360
        plunge = (90 - EPS_ANG)%90

        Punto_rake = _shape('line', 0, 0, plunge, trend)
        # ==========================
        # CASO 3 DIEDROS
        # ==========================
        if n == 3:
            central, others = classify_case_3(region, Punto_rake)

            results.append({
                'case': 3,
                'central': central,
                'others': others
            })

        # ==========================
        # CASO 2 DIEDROS
        # ==========================
        elif n == 2:

            central, others = classify_case_2(region, Punto_rake)

            results.append({
                'case': 2,
                'central': central,
                'others': others
            })

        elif n == 4:
            pair_1, pair_2 = pair_diedros_case_4(region)

            active, passive = select_active_pair(pair_1, pair_2, Punto_rake)

            results.append({
                'case': 4,
                'central': active,
                'others': passive
            })


    return results



# cinematica correcta, pero en caso no tener ningun dato esta falla, ay que hacer algo al respecto como asumir o darle un valor fuera de eso como 5, ya
# que ese plano de falla si existe, pero no fue posible extraer este tipo de informacion, y tampoco se puede eliminar ya que estaria ligado a una lista del plano
# de falla
# para el caso digamos que faltara una dato en la lista, es posible rellenar con ceros, pero esto ya es muy peligroso

def cinematic(cine_1, cine_2=None):

    KIN_MAP = {
        "Nx": 1,
        "Ix": -1,
        "Dx": 3,
        "Sx": -3,
        1: 1,
        -1: -1,
        3: 3,
        -3: -3,
        "NX": 1,
        "IX": -1,
        "DX": 3,
        "SX": -3,
        "Normal": 1,
        "Inverse": -1,
        "Dextral": 3,
        "Sinestral": -3,
    }
    cine_1 = _normalize_cine_value(cine_1)
    cine_2 = _normalize_cine_value(cine_2)

    # Reordenar: si cine_1 es None y cine_2 no, intercambiar
    if cine_1 is None and cine_2 is not None:
        cine_1, cine_2 = cine_2, None

    # Caso totalmente vacío
    if cine_1 is None and cine_2 is None:
        raise ValueError("No se especificó ninguna cinemática")
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

    # debe de colocarse 4 valores los cuales pueden combinarse
    # cine_1 tiene que ser diferente de cine 2 (Inverse en cine 1, no puede aver inverse en cine 2)
    # cine 1 no puede tener valor contrario que cine 2(tales como normal e inversa, e dextral con sinetral ) son incompatibles osea error
    # es posible solo rellenar cine_1 o cine_2 con cualquier valor y dejar el otro vacio. esto para casos especiales donde soloe s Normal digamos
    # se debe colocar valores a inverse, dextral, normal, sinestral
    # retornar los valores con sus etiquetas o solo valores o error si en caso no se cumple las condiciones que mencionarion
    # normal 1 e inversa -1, dextral 3 y sinestral -3, Nx + Dx =  3, Nx + Sx = -1, Ix + Dx = 1, Ix + Sx = - 3


def _normalize_cine_value(val):
    if val in (None, "", " ", 0,"0"):
        return None
    return val


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

# Caso general: se condiciona los valores de strike dip y rake con el valor cinematico para obtener un valor que oscila entre 0 y 1 # en otras palabras retornar una lista de 0 e 1, esto con el modelo digamos de decir extensible o compresivo, pero repito el diedro central o el que interseccionaba con el Punto # todo el analisi se realizara para ese diedro o par de diedros # aun no se si usar el numero de diedros o el plano en si # condiciones
# normal 1 inversa -1 dextral 3 sinestral -3 (NxDx 4, NxSx -2, IxDx 2, IxSx -4)


def _insert_valor_diedro_pairs(strike, dip, rake, valor_cinematic):

    valor = None  # ← CLAVE

    if dip == 90:
        if rake == 90:
            if valor_cinematic == -1:
                valor = 1
            elif valor_cinematic == 1:
                valor = 0

        elif rake in (0, 180):
            if valor_cinematic == -3:
                valor = 1
            elif valor_cinematic == 3:
                valor = 0

        elif rake > 90:
            if valor_cinematic == 4:
                valor = 0
            elif valor_cinematic == -4:
                valor = 1

        else:
            if valor_cinematic == -2:
                valor = 0
            elif valor_cinematic == 2:
                valor = 1

    elif dip == 0:
        if valor_cinematic == 3:
            valor = 1
        elif valor_cinematic == -3:
            valor = 0

    else:
        if rake == 90:
            if valor_cinematic == 1:
                valor = 1
            elif valor_cinematic == -1:
                valor = 0

        elif rake == 0:
            if valor_cinematic == 3:
                valor = 0
            elif valor_cinematic == -3:
                valor = 1

        elif rake == 180:
            if valor_cinematic == 3:
                valor = 1
            elif valor_cinematic == -3:
                valor = 0

        elif rake > 90:
            if valor_cinematic == 4:
                valor = 1
            elif valor_cinematic == -4:
                valor = 0

        else:
            if valor_cinematic == -2:
                valor = 1
            elif valor_cinematic == 2:
                valor = 0

    if valor is None:
        raise ValueError(
            f"Configuración no válida: dip={dip}, rake={rake}, valor_cinematic={valor_cinematic}"
        )

    return valor

def insert_valor_diedro_pairs_array(strike, dip, rake, valor_cinematic):
    strike, dip, rake, valor_cinematic = np.atleast_1d(
        strike, dip, rake, valor_cinematic
    )

    if not (len(strike) == len(dip) == len(rake) == len(valor_cinematic)):
           raise ValueError("Todas las entradas deben tener la misma longitud")

    result = np.zeros(len(strike), dtype=int)

    for i, (s, d, r, v) in enumerate(zip(strike, dip, rake, valor_cinematic)):
        result[i] = _insert_valor_diedro_pairs(s, d, r, v)

    return result


# ___________________________

def assign_diedro_labels(strike, dip, rake, cine1, cine2):
    strike, dip, rake = np.atleast_1d(strike, dip, rake)

    # 1. Geometría
    regions = clasy_polygon(strike, dip, rake)

    # 2. Cinemática
    valor_cinematic = cinematic_array(cine1, cine2)

    # 3. Valor binario del diedro central
    central_values = insert_valor_diedro_pairs_array(
        strike, dip, rake, valor_cinematic
    )

    results = []

    for i, region in enumerate(regions):

        central_val = central_values[i]
        other_val   = 1 - central_val

        poly_labels = []

        for poly in region['central']:
            poly_labels.append({
                'polygon': poly,
                'label': central_val
            })

        for poly in region['others']:
            poly_labels.append({
                'polygon': poly,
                'label': other_val
            })

        results.append({
            'case': region['case'],
            'polygons': poly_labels
        })

    return results

def malla(tamaño = 0.2):
    # Parameters
    R = 2
    dx = tamaño  # change this to control mesh density

    # Create grid
    x = np.arange(-R, R + dx, dx)
    y = np.arange(-R, R + dx, dx)
    X, Y = np.meshgrid(x, y)

    # Mask points inside circle
    mask = X ** 2 + Y ** 2 < R ** 2

    plunge, trend = stereonet_math.geographic2plunge_bearing(X[mask], Y[mask])
    return plunge, trend

# def conteo_puntos(tamaño, results):
#     import numpy as np
#     from shapely.geometry import Point
#     from mplstereonet import stereonet_math
#
#     # 1. Malla direccional
#     plunge, trend = malla(tamaño)
#
#     # 2. Proyección al plano estereográfico
#     x, y = stereonet_math.line(plunge, trend)
#
#     # 3. Puntos shapely
#     points = [Point(xi, yi) for xi, yi in zip(x, y)]
#
#     # 4. Acumulador
#     scores = np.zeros(len(points), dtype=int)
#
#     # 5. Conteo
#     for result in results:
#         for poly_dict in result['polygons']:
#             poly = poly_dict['polygon']
#             label = poly_dict['label']
#
#             if label == 0:
#                 continue
#
#             for i, pt in enumerate(points):
#                 if poly.covers(pt):
#                     scores[i] += label
#
#     # 6. Devolver todo alineado por índice
#     return plunge, trend, scores

def conteo_puntos(tamaño, results):

    plunge, trend = malla(tamaño)
    lon, lat = stereonet_math.line(plunge, trend)
    points = [Point(lo, la) for lo, la in zip(lon, lat)]

    scores = np.zeros(len(points), dtype=int)

    for i, pt in enumerate(points):

        for result in results:  # una falla

            diedros_intersectados = []

            for poly_dict in result['polygons']:
                poly = poly_dict['polygon']
                label = int(poly_dict['label'])

                if poly.intersects(pt):
                    diedros_intersectados.append(label)

            # CASO NORMAL: exactamente uno
            if len(diedros_intersectados) == 1:
                scores[i] += diedros_intersectados[0]

            # CASO BORDE: dos diedros (muy común)
            elif len(diedros_intersectados) > 1:
                # regla física: el diedro activo domina
                scores[i] += max(diedros_intersectados)

            # CASO RARO: ninguno
            else:
                scores[i] += 0

    return  plunge, trend, scores

# hallar el punto central de cada grupo de puntos que pertenecen a los sigmas 1 y 2

def eje_principal(plunge, trend):

    lon, lat = stereonet_math.line(plunge, trend)
    V = np.column_stack(stereonet_math.sph2cart(lon, lat))

    cov = np.cov(V.T)
    eigvals, _ = np.linalg.eigh(cov)
    eigvals = eigvals[::-1]

    if eigvals[0] / eigvals[1] > 3:
        # 1 grupo
        eje, r = mplstereonet.find_mean_vector(
            plunge, trend, measurement='lines'
        )
        return [eje]

    else:
        # 2 grupos
        centers = mplstereonet.kmeans(
            plunge, trend,
            num=2,
            measurement='lines',
            bidirectional=True
        )
        lon_c, lat_c = centers[:,0], centers[:,1]
        return list(stereonet_math.geographic2plunge_bearing(lon_c, lat_c))



import networkx as nx


def detectar_grupos(plunge, trend, ang_deg=1):
    lon, lat = stereonet_math.line(plunge, trend)
    ang = np.radians(ang_deg)

    G = nx.Graph()
    n = len(lon)

    G.add_nodes_from(range(n))

    for i in range(n):
        for j in range(i+1, n):
            d = stereonet_math.angular_distance(
                (lon[i], lat[i]),
                (lon[j], lat[j]),
                bidirectional=True
            )
            if d < ang:
                G.add_edge(i, j)

    grupos = list(nx.connected_components(G))
    return grupos
