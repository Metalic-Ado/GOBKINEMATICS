import mplstereonet
from mplstereonet import stereonet_math
from GOBESTEREONET import GobEstereonet as ge
import numpy as np
from shapely import geometry, ops, Point
from sklearn.cluster import DBSCAN

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

# __________________________________________________ PASO 2 ____________________________________________________________

# CREACION DE LOS POLIGONOS Y GENERAR LOS DIEDROS

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

# __________________________________________________________ PASO 3 ____________________________________________________

# Clasificar los diedros segun un punto central creado para cada caso de los diedros

# CASO 2
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

# CASO 3

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


# CASO 4

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


# Obtencion de los poligonos etiquetados segun un punto central

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

# ______________________________________________________ PASO 4 ________________________________________________________
# CLASIFICACION DE LA CINEMATICA

# cinematica correcta, pero en caso no tener ningun dato esta falla, ay que hacer algo al respecto como asumir o darle un valor fuera de eso como 5, ya
# que ese plano de falla si existe, pero no fue posible extraer este tipo de informacion, y tampoco se puede eliminar ya que estaria ligado a una lista del plano
# de falla
# para el caso digamos que faltara una dato en la lista, es posible rellenar con ceros, pero esto ya es muy peligroso

    # debe de colocarse 4 valores los cuales pueden combinarse
    # cine_1 tiene que ser diferente de cine 2 (Inverse en cine 1, no puede aver inverse en cine 2)
    # cine 1 no puede tener valor contrario que cine 2(tales como normal e inversa, e dextral con sinetral ) son incompatibles osea error
    # es posible solo rellenar cine_1 o cine_2 con cualquier valor y dejar el otro vacio. esto para casos especiales donde soloe s Normal digamos
    # se debe colocar valores a inverse, dextral, normal, sinestral
    # retornar los valores con sus etiquetas o solo valores o error si en caso no se cumple las condiciones que mencionarion
    # normal 1 e inversa -1, dextral 3 y sinestral -3, Nx + Dx =  3, Nx + Sx = -1, Ix + Dx = 1, Ix + Sx = - 3


def cinematic(cine_1, cine_2=None):

    KIN_MAP = {
        "Nx": 1, "Ix": -1, "Dx": 3, "Sx": -3,
        1: 1, -1: -1, 3: 3, -3: -3,
        "NX": 1, "IX": -1, "DX": 3, "SX": -3,
        "Normal": 1, "Inverse": -1, "Dextral": 3, "Sinestral": -3,
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


def arrow(plunge_rake, trend_rake, valor_cinematic):

    plunge_rake, trend_rake, valor_cinematic = np.atleast_1d(
        plunge_rake, trend_rake, valor_cinematic
    )

    lons = []
    lats = []
    us = []
    vs = []

    for p, t, vc in zip(plunge_rake, trend_rake, valor_cinematic):

        lon, lat = stereonet_math.line(p, t)
        mag = np.hypot(lon, lat)

        if vc in (-3, 3):
            continue
        if mag == 0:
            continue

        if vc in (1, 4, -2):
            u =  lon / mag
            v =  lat / mag
        elif vc in (-1, 2, -4):
            u = -lon / mag
            v = -lat / mag
        else:
            continue

        lons.append(lon)
        lats.append(lat)
        us.append(u)
        vs.append(v)

    if len(lons) == 0:
        return None

    return  np.array(lons), np.array(lats), np.array(us), np.array(vs)

# fechas dextrals y sinestral colocadas en el limite del stereograma
def arrow_geom(strike):
    theta = np.radians(strike)

    dx = np.sin(theta)
    dy = np.cos(theta)

    r0 = 0.50
    r1 = 0.55

    x0 = 0.5 + r0 * dx
    y0 = 0.5 + r0 * dy

    Lx = (r1 - r0) * dx
    Ly = (r1 - r0) * dy

    x1 = x0 + Lx
    y1 = y0 + Ly

    return x0, y0, x1, y1, Lx, Ly

def arrows_rigth_and_left(ax, strike, rigtholeft= 'left'):
    strike = np.atleast_1d(strike)
    strike_pos = (strike + 0.5)%360
    strike_ant = (strike - 0.5)%360

    for s in strike_ant:
        x0, y0, x1, y1, Lx, Ly = arrow_geom(s)
        if rigtholeft == 'left':
            ax.arrow(
                x1, y1,  # ← nuevo origen
                -Lx, -Ly,  # ← vector invertido
                transform=ax.transAxes,
                width=0.015,
                head_width=0.04,
                head_length=0.035,
                length_includes_head=True,
                shape=rigtholeft,
                facecolor='black',
                edgecolor='black',
                alpha=0.7,
                clip_on=False
            )
        elif rigtholeft == 'right':
            ax.arrow(
                x0, y0,  # ← nuevo origen
                Lx, Ly,  # ← vector invertido
                transform=ax.transAxes,
                width=0.015,
                head_width=0.04,
                head_length=0.035,
                length_includes_head=True,
                shape=rigtholeft,
                facecolor='black',
                edgecolor='black',
                alpha=0.7,
                clip_on=False
            )

    for s in strike_pos:
        x0, y0, x1, y1, Lx, Ly = arrow_geom(s)
        if rigtholeft == 'left':

            ax.arrow(
                x0, y0,  # ← nuevo origen
                Lx, Ly,  # ← vector invertido
                transform=ax.transAxes,
                width=0.015,
                head_width=0.04,
                head_length=0.035,
                length_includes_head=True,
                shape=rigtholeft,
                facecolor='black',
                edgecolor='black',
                alpha=0.7,
                clip_on=False
            )
        elif rigtholeft == 'right':
            ax.arrow(
                x1, y1,  # ← nuevo origen
                -Lx, -Ly,  # ← vector invertido
                transform=ax.transAxes,
                width=0.015,
                head_width=0.04,
                head_length=0.035,
                length_includes_head=True,
                shape=rigtholeft,
                facecolor='black',
                edgecolor='black',
                alpha=0.7,
                clip_on=False
            )

   # normal 1 e inversa -1, dextral 3 y sinestral -3, Nx + Dx =  4, Nx + Sx = -2, Ix + Dx = 2, Ix + Sx = - 4
def arrows_dex_and_sin(ax, strike, valor_cinematic):
    strike, valor_cinematic = np.atleast_1d(
        strike, valor_cinematic
    )


    for s, vc in zip(strike, valor_cinematic):

        if vc in (-1, 1):
            continue
        if vc in (3, 4, 2):
            arrows_rigth_and_left(ax,s,'right')

        elif vc in (-3, -2, -4):
            arrows_rigth_and_left(ax, s, 'left')
        else:
            continue

# arrow del sigma principal 1
# SE PUEDE MEJORAR USANDO EL TAMAÑO CON RESPECTO AL PLUNGE
def arrow_geom2(strike):
    theta = np.radians(strike)

    dx = np.sin(theta)
    dy = np.cos(theta)

    r0 = 0.50
    r1 = 0.6

    x0 = 0.5 + r0 * dx
    y0 = 0.5 + r0 * dy

    Lx = (r1 - r0) * dx
    Ly = (r1 - r0) * dy

    x1 = x0 + Lx
    y1 = y0 + Ly

    return x0, y0, x1, y1, Lx, Ly

def arrow_main(ax, trend_sigma1):
    trend_sigma1 = np.atleast_1d(trend_sigma1)
    for t in trend_sigma1:
        x0, y0, x1, y1, Lx, Ly = arrow_geom2(t)
        ax.arrow(
            x1, y1,  # ← nuevo origen
            -Lx, -Ly,  # ← vector invertido
            transform=ax.transAxes,
            width=0.015,
            head_width=0.04,
            head_length=0.035,
            length_includes_head=True,
            shape='full',
            facecolor='black',
            edgecolor='black',
            clip_on=False
        )



# Caso general: se condiciona los valores de strike dip y rake con el valor cinematico para obtener un valor que oscila entre 0 y 1 # en otras palabras retornar una lista de 0 e 1, esto con el modelo digamos de decir extensible o compresivo, pero repito el diedro central o el que interseccionaba con el Punto # todo el analisi se realizara para ese diedro o par de diedros # aun no se si usar el numero de diedros o el plano en si # condiciones
# normal 1 inversa -1 dextral 3 sinestral -3 (NxDx 4, NxSx -2, IxDx 2, IxSx -4)

# __________________________________________________________ PASO 5 ____________________________________________________
# INSERTAR CODIGO A LOS DIEDROS SEGUN LA CINEMATICA

# Se usa el valor de 1 o 0 segun la cinematica y el plano de falla, se le asigna al valor al diedro del centro y su par si tiene
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

# Para varios planos
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

# ____________________________________________PASO 6 ___________________________________________________________________
# GENERACION DE LOS DIEDROS RECTOS CON SU CODIGO CINEMATICO

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

# ____________________________________________________PASO 7 ___________________________________________________________
# CONTEO DE LOS DIEDROS DE DISTINTAS FALLAS, PARA OBTENER LA MAX EXTENSIO Y COMPRESION

def malla(tamaño = 0.2): # Malla Parametrizada
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

def point_de_diedros_principales_max_and_min(plunge, trend, scores):
    # seleccionar puntos extremos
    mask_max = scores == scores.max()
    mask_min = scores == scores.min()

    plu_max = plunge[mask_max]
    tre_max = trend[mask_max]

    plu_min = plunge[mask_min]
    tre_min = trend[mask_min]
    return plu_max, tre_max, plu_min, tre_min

# _______________________________________________ PASO 8 _______________________________________________________________
# ENCONTRAR LA CANTIDAD DE CLUSTER PORS DIEDRO PRINCIPALES

# 1. CONVERTIR PLUNGE Y TREND EN COORDENADAS POLARES (NO PROBADO AL 100PORCIENTE)
# el plunge es el radio que va de 0 a 90 se puede dividir entre 90 para normalizar data
# el trend se convierte en el angulo theta

# 2. CORTAR TODOS LOS POLIGONOS Y ENCONTRAR LOS POLIGONOS RESTANTES QUE INTERSECCIONAN CON LOS PUNTOS (NO PROBADO)

# 3. Usar Clustenring mas especificamente DBSCAN (AGRUPAMIENTO POR DENSIDAD) PROBADO UN 50%

def clustering_DBSCAN(plunges, trends, eps_deg = 10, samples_min = 5):
    plunges, trends = np.atleast_1d(plunges, trends)
    lon, lat = stereonet_math.line(plunges, trends)
    x, y, z = stereonet_math.sph2cart(lon, lat)
    Vector = np.column_stack([x, y, z])
    eps_deg1 = eps_deg  # prueba 8–15
    eps = 1 - np.cos(np.radians(eps_deg1))  # convertir a métrica coseno
    db = DBSCAN(
        eps=eps,
        min_samples=samples_min,
        metric='cosine'
    )
    labels1 = db.fit_predict(Vector)
    unique_labels = np.unique(labels1)
    unique_labels = unique_labels[unique_labels != -1]
    return len(unique_labels)  # devuelva valores de  0,1,2,3 de acuerdo al numero de grupos y -1 a los puntos que hacen ruido si se obtiene 0 y 1 significa 2 grupos


# hay un tema con la antipodalidad vectores que forman grupos pero de extremos


# ______________________________________________ PASO 9 ________________________________________________________________
# GENERAR EL VECTOR MEDIO DE CADA DIEDRO PRINCIPAL, OBTENIENDO EL PLUNGE Y TREND DE CADA PALEOSTRESS

def vector_media (plunges, trends, valor_labels):
    if valor_labels == 1:
        (plunge_1, trend_1), r1= mplstereonet.find_mean_vector(
            plunges, trends, measurement='lines')
    else:
        centers = mplstereonet.kmeans(
            plunges, trends,
            num=valor_labels,
            measurement='lines',
            bidirectional=True
        )
        lon_c = [c[0] for c in centers]
        lat_c = [c[1] for c in centers]

        plunge_1, trend_1 = stereonet_math.geographic2plunge_bearing(lon_c, lat_c)

    return plunge_1, trend_1


def plot_text(ax,plunges_1, trends_1, plunges_3, trends_3, eje_x =1.1, eje_y=0.95):
    plunges_1, trends_1 = np.atleast_1d(plunges_1, trends_1)
    plunges_3, trends_3 = np.atleast_1d(plunges_3, trends_3)
    x = eje_x
    y = eje_y
    dy = 0.05

    # TÍTULO
    ax.text(
        x, y,
        "Método de Diedros Rectos",
        transform=ax.transAxes,
        ha="left", va="top",
        fontsize=13,
        fontweight="bold",
        clip_on=False
    )
    vals_s1 = "\n".join(
        f"Plunge = {pl:.2f}°   Trend = {tr:.2f}°"
        for pl, tr in zip(plunges_1, trends_1)
    )

    # SUBTÍTULO σ1
    ax.text(
        x, y - dy,
        "Máxima Compresión (σ₁)",
        transform=ax.transAxes,
        ha="left", va="top",
        fontsize=11,
        fontweight="bold",
        clip_on=False
    )

    # VALORES σ1
    ax.text(
        x, y - 2 * dy,
        vals_s1,
        transform=ax.transAxes,
        ha="left", va="top",
        fontsize=10,
        clip_on=False
    )

    vals_s3 = "\n".join(
        f"Plunge = {pl:.2f}°   Trend = {tr:.2f}°"
        for pl, tr in zip(plunges_3, trends_3)
    )

    # SUBTÍTULO σ1
    ax.text(
        x, y - 3 * dy,
        r"Máxima Extensión ($\boldsymbol{\sigma_3}$)",
        transform=ax.transAxes,
        ha="left", va="top",
        fontsize=11,
        fontweight="bold",
        clip_on=False
    )

    # VALORES σ1
    ax.text(
        x, y - 4 * dy,
        vals_s3,
        transform=ax.transAxes,
        ha="left", va="top",
        fontsize=10,
        clip_on=False
    )





# _______________________________________________ PASO 10 ______________________________________________________________
# GENERAR LAS DENSIDADES O LIMITES DE ERROR SEGUN EL PUNTO CENTRAL

# _________________________________________ANALISIS GENERAL DE LOS DIEDROS RECTOS_______________________________________
class DiedrosRectosMethods:
    def __init__(self, strike, dip, rake, cinematic_1, cinematic_2):
        self.strike = strike
        self.dip = dip
        self.rake = rake
        self.cinematic_1 = cinematic_1
        self.cinematic_2 = cinematic_2

        self.Polygonos_with_label = assign_diedro_labels(self.strike, self.dip, self.rake, self.cinematic_1, self.cinematic_2)
        self.plunge, self.trend, self.scores = conteo_puntos(0.1, self.Polygonos_with_label)
        self.plunge_max, self.trend_max, self.plunge_min, self.trend_min = self.points_max_and_min()

        self.clustering_max = clustering_DBSCAN(self.plunge_max, self.trend_max)
        self.clustering_min = clustering_DBSCAN(self.plunge_min, self.trend_min)

        self.plunge_sigma_1, self.trend_sigma_1 = vector_media(self.plunge_max, self.trend_max, self.clustering_max)
        self.plunge_sigma_3, self.trend_sigma_3 = vector_media(self.plunge_min, self.trend_min, self.clustering_min)
        self.plunge_sigma_1 = np.atleast_1d(self.plunge_sigma_1)
        self.trend_sigma_1 = np.atleast_1d(self.trend_sigma_1)

        self.plunge_sigma_3 = np.atleast_1d(self.plunge_sigma_3)
        self.trend_sigma_3 = np.atleast_1d(self.trend_sigma_3)

        self.valores_cinematicos_rake = self.valor_cinematic()


    # Graficas de los diedros

    def diedro_color(self, ax):
        color_map = {1: 'black', 0: 'white'}
        for res in self.Polygonos_with_label:  # ← cada falla
            for p in res['polygons']:  # ← polígonos de esa falla
                poly = p['polygon']
                label = int(p['label'])  # np.int64 → int
                lon, lat = poly.exterior.xy
                ax.fill(lon, lat, color=color_map[label], alpha=0.5)


    # Grafico y conteo de los diedros de todas las fallas
    def conteo_diedros(self, ax):
        lon, lat = stereonet_math.line(self.plunge, self.trend)

        ax.line(self.plunge, self.trend, color='red')
        for p, t, s in zip(lon, lat, self.scores):
            # opcional, para no saturar
            ax.text(
                p, t,  # OJO: (trend, plunge)
                str(s),
                fontsize=10,
                ha='center',
                va='center',
                color='white',
                zorder=5
            )
    # Puntos de plunge y trend maximo y minimo del conteo de los diedros
    def points_max_and_min(self):
        plunge_max,trend_max, plunge_min, trend_min = point_de_diedros_principales_max_and_min(self.plunge, self.trend, self.scores)
        return plunge_max,trend_max, plunge_min, trend_min

    def graphic_point_max_and_min(self, ax):
        ax.line(self.plunge_max, self.trend_max, labels= "max")
        ax.line(self.plunge_min, self.trend_min, labels = "min")

    # Clasificar en numero de grupos los puntos maximo y minimo
    def plot_sigmas(self, ax):
        ax.line(self.plunge_sigma_1, self.trend_sigma_1, color="white", ms=10, mec="white")
        ax.line(self.plunge_sigma_3, self.trend_sigma_3,  color="black", ms=10, mec="white")
        # texto
        lon_1, lat_1 = stereonet_math.line(self.plunge_sigma_1, self.trend_sigma_1)
        for lo, la in zip(lon_1, lat_1):
            ax.text(lo+0.05, la+0.05, r"$\sigma_1$", fontsize=10, fontweight="bold", fontstyle="italic",fontfamily="serif",
                    ha='left', va='bottom', color='black', zorder=5,
                    bbox=dict(boxstyle="round,pad=0.2",facecolor="white",edgecolor="black",alpha=0.8 ))
        lon_3, lat_3 = stereonet_math.line(self.plunge_sigma_3, self.trend_sigma_3)
        for lo3, la3 in zip(lon_3, lat_3):
            ax.text(lo3+0.05, la3+0.05, r"$\sigma_3$", fontsize=10, fontweight="bold", fontstyle="italic",fontfamily="serif",
                    ha='left', va='bottom', color='black', zorder=5,
                    bbox=dict(boxstyle="round,pad=0.2",facecolor="white",edgecolor="black",alpha=0.8 ))


    def valor_cinematic(self):
        valores_cinematicos = cinematic_array(self.cinematic_1, self.cinematic_2)
        return valores_cinematicos

    def arrows(self, ax): #mejorar, falta probar si es cierto o no
        plunge_rake, trend_rake = ge._rake_to_plungeandtrend(self.strike, self.dip, self.rake)
        lon_rake, lat_rake, u, v = arrow(plunge_rake, trend_rake, self.valores_cinematicos_rake)
        ax.quiver(lon_rake, lat_rake, u, v, color='red', width=2, headwidth=4, units='dots', scale=0.03, zorder=5)

    def arrows_dex(self, ax):

        arrows_dex_and_sin(ax, self.strike,  self.valores_cinematicos_rake)
        strikecomplement = []
        for s in self.strike:
            strikes_com = (s + 180) % 360
            strikecomplement.append(strikes_com)
        arrows_dex_and_sin(ax,strikecomplement, self.valores_cinematicos_rake)
    def plot_arrow_main(self, ax):
        arrow_main(ax, self.trend_sigma_1)
        trend_complement = []
        for t in self.trend_sigma_1:
            trend_com = (t + 180)% 360
            trend_complement.append(trend_com)
        arrow_main(ax, trend_complement)

    def plot_text_main(self, ax):
        plot_text(ax, self.plunge_sigma_1, self.trend_sigma_1, self.plunge_sigma_3, self.trend_sigma_3)
        # SUBTÍTULO σ1
        ax.text(
            1.1, 0.95 - 6 * 0.05,
            f"Nº de FALLAS ANALISADAS\n {len(self.strike)} Fallas",
            transform=ax.transAxes,
            ha="left", va="top",
            fontsize=11,
            fontweight="bold",
            clip_on=False
        )

    def run(self, ax):
        self.diedro_color(ax)
        self.plot_sigmas(ax)
        self.arrows(ax)
        self.arrows_dex(ax)
        self.plot_arrow_main(ax)
        self.plot_text_main(ax)
        return {"sigma_1": (self.plunge_sigma_1, self.trend_sigma_1),"sigma_2":(self.plunge_sigma_3, self.trend_sigma_3)}


########################################################################################################################
############################################# FIN DE LOS DIEDROS RECTOS ################################################
########################################################################################################################


