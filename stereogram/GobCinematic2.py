import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.projections import register_projection
import numpy as np
from matplotlib.patches import Circle
from GOBESTEREONET import GobFallas2 as gf2

class KinematicAxes(Axes):
    name = "kinematic"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Límites internos
        self.set_xlim(-1.6, 1.6)
        self.set_ylim(-1.6, 1.6)

        # Relación 1:1
        self.set_aspect("equal", adjustable="box")

        # Ocultar ejes normales
        self.set_xticks([])
        self.set_yticks([])
        for spine in self.spines.values():
            spine.set_visible(False)

        # Dibujar estructura base
        self._draw_cross()
        self._draw_labels()
        self._draw_dip_scale()
        self._draw_rake_scale_right()
        self._draw_rake_scale_left()
        self._draw_strike_ring()
        self._draw_limit_squeare()



    # -------------------------
    # Dibujo de la cruz central
    # -------------------------

    def _draw_cross(self):
        R = 1.0  # radio cinemático base

        # Horizontal (Dip)
        self.plot([-R, R], [0, 0], color="black", lw=1.5)

        # Vertical (Rake)
        self.plot([0, 0], [-R, R], color="black", lw=1.5)
    # -------------------------
    # Etiquetas cinemáticas
    # -------------------------
    def _draw_labels(self):
        offset = 0.1 # de las etiquetas Ix, Sx etc

        # Horizontal (dip)
        self.text(1 + offset, 0, "Dx", ha="left", va="center", fontsize=15,
                  fontweight="bold",fontfamily="serif")
        self.text(-1 - offset, 0, "Sx", ha="right", va="center", fontsize=15,
                  fontweight="bold",fontfamily="serif")

        # Vertical (rake)
        self.text(0, 1 + offset, "Ix", ha="center", va="bottom", fontsize=15,
                  fontweight="bold",fontfamily="serif")
        self.text(0, -1 - offset, "Nx", ha="center", va="top", fontsize=15,
                  fontweight="bold",fontfamily="serif")

    def _draw_dip_scale(self):
        dips = [0, 30, 60, 90]
        x_text = -0.06
        dt = 0.04

        for dip in dips:
            y = 1 - dip / 90

            # Tick superior (Ix)
            self.plot(
                [-dt / 2, dt / 2],
                [y, y],
                color="black",
                lw=1
            )
            self.text(
                x_text, y, f"{dip}°",
                ha="right", va="center", fontsize=9
            )

            # Tick inferior (Nx)
            if dip != 90:
                self.plot(
                    [-dt / 2, dt / 2],
                    [-y, -y],
                    color="black",
                    lw=1
                )
                self.text(
                    x_text, -y, f"{dip}°",
                    ha="right", va="center", fontsize=9
                )

        # Etiquetas del eje
        self.text(
            x_text - 0.01, -0.835, "Dip",
            ha="right", va="center", fontsize=9,
            fontfamily="serif", alpha=0.8, rotation=90
        )
        self.text(
            x_text - 0.01, 0.835, "Dip",
            ha="right", va="center", fontsize=9,
            fontfamily="serif", alpha=0.8, rotation=90
        )

    def _draw_rake_scale_right(self):
        rakes = [0, 30, 60, 120, 150, 180]
        y_text = 0.06
        dt = 0.04  # largo del tick

        for rake in rakes:
            x = -(rake - 90) / 90

            # Tick horizontal (perpendicular al eje vertical)
            self.plot(
                [x, x],
                [-dt, 0],
                color="black",
                lw=1
            )

            # Texto
            self.text(
                x, y_text, f"{rake}º",
                ha="center", va="bottom", fontsize=9
            )

        self.text(
             -0.9, y_text + 0.01, "Rake" , ha="left", va="center", fontsize=9, alpha=0.7
        )

    def _draw_rake_scale_left(self):
        rakes = [0, 30, 60, 120, 150, 180]
        y_text = -0.06
        dt = 0.04

        for rake in rakes:
            x = (rake - 90) / 90

            # Tick horizontal hacia la izquierda
            self.plot(
                [x, x],
                [0, dt],
                color="black",
                lw=1
            )

            self.text(
                x, y_text, f"{rake}º",
                ha="center", va="top", fontsize=9
            )

        self.text(
             0.815, y_text-0.03, "Rake", ha="center", va="bottom", fontsize=9, alpha=0.7
        )

#######################################################################################################################
# base matematica, para el rake y dip

# normal 1 e inversa -1, dextral 3 y sinestral -3, Nx + Dx =  4, Nx + Sx = -2, Ix + Dx = 2, Ix + Sx = - 4

    # normal 1 e inversa -1, dextral 3 y sinestral -3, Nx + Dx =  4, Nx + Sx = -2, Ix + Dx = 2, Ix + Sx = - 4
    def _cinematic_main(self, cine_1, cine_2 = None):
        cine_1, cine_2 =  np.atleast_1d(cine_1, cine_2)
        valor_cinematic = gf2.cinematic_array(cine_1, cine_2)
        return valor_cinematic

# condiciones para el eje X

    # Valida las combinaciones del rake y el valor cinematico
    def _validate_rake(self, rake, valor_cinematic):

        # Combinaciones dip–slip oblicuas
        if valor_cinematic in (2, -2):  # IxDx, NxSx
            if not (0 <= rake < 90):
                raise ValueError("Rake fuera de dominio físico (0–90°)")

        elif valor_cinematic in (4, -4):  # NxDx, IxSx
            if not (90 < rake <= 180):
                raise ValueError("Rake fuera de dominio físico (90–180°)")

        # Strike-slip puro → solo 0 o 180
        elif abs(valor_cinematic) == 3:
            if rake not in (0, 180):
                raise ValueError("Strike-slip puro solo acepta rake 0 o 180")


    # define las formulas segun el rake y el valor cinematico asignado, OJO 0.0 ES EL CENTRO Y 1 SERIA UN EXTREMO
    def _rake_magnitude(self, rake, valor_cinematic):

        # Rake 90 → sin componente strike
        if rake == 90:
            return 0.0  # punto central

        if valor_cinematic in (2, -2):  # Ix Dx and Nx Sx tiene valores de 0–90
            return 1 - (rake / 90)

        elif valor_cinematic in (4, -4):  # NxDx, IxSx debe tener valores de  90–180
            return 1 - ((180 - rake) / 90)

        elif abs(valor_cinematic) == 3:  # solo un valor Sx o Nx
            return 1.0

        raise ValueError("Combinación rake–cinemática no válida")

# La maginitud del rake se coloca en coordenada x # veo un problema ya que no considera el -3 osea solo Sx
    def _rake_to_x(self, rake, valor_cinematic):

        self._validate_rake(rake, valor_cinematic)

        mag = self._rake_magnitude(rake, valor_cinematic)

        # Rake 90 → eje Y puro Quiere decir que esta en el punto central
        if mag == 0:
            return 0.0

        # Sx → izquierda  osea si tiene un valor cinematico de -2 y -4 NxSX and IxSx
        if valor_cinematic < 0:
            return -mag
        # pero si es positivo entonces se usa la magnitud positiva se cuenta desde Dx
        # Dx → derecha
        return +mag

# Para el eje y
    # plotear el dip en el eje y

    def _dip_to_y(self, dip, valor_cinematic):

        y_mag = 1 - dip / 90 # formula de conversion

        # Ix arriba | Nx abajo
        if valor_cinematic in (-1, 2, -4): # Ix, SxIx and IxDx inicia c ontar desde arria osea desde +1
            return +y_mag
        # si no se cumple esto inicia a contar desde abajo o desde -1
        return -y_mag

    def _strike_slip_xy(self, dip, rake, valor_cinematic):
        """
        Strike–slip puro (Dx o Sx)
        Funciona para dip = 0 y dip > 0
        """

        # X extremo
        x = -1 if valor_cinematic < 0 else +1

        # Magnitud Y por dip
        y_mag = 1 - dip / 90

        # -------------------------
        # Signo Y según cuadrantes
        # -------------------------
        if valor_cinematic < 0:  # Sx
            # rake=180 → IxSx | rake=0 → NxSx
            y = +y_mag if rake == 180 else -y_mag
        else:  # Dx
            # rake=0 → IxDx | rake=180 → NxDx
            y = +y_mag if rake == 0 else -y_mag

        return x, y

    def _dip_null_xy(self, dip, rake, valor_cinematic):
        """
        Caso dip = 0
        Cuadrantes curvados según Sx / Dx
        """

        rake = rake % 180

        # -------------------------
        # Magnitud X (plegado)
        # -------------------------
        x_mag = abs(1 - rake / 90)

        # Signo de X
        if valor_cinematic < 0:  # Sx
            x = -x_mag
        else:  # Dx
            x = +x_mag

        # -------------------------
        # Signo de Y (CLAVE)
        # -------------------------
        if valor_cinematic < 0:  # Sx
            # SxNx abajo | SxIx arriba
            y = -1 if rake < 90 else +1
        else:  # Dx
            # DxIx arriba | DxNx abajo
            y = +1 if rake < 90 else -1

        return x, y

    def dip_rake_to_xy(self, dip, rake, cine_1, cine_2=None):

        valor_cinematic = self._cinematic_main(cine_1, cine_2)

        if not (0 <= dip <= 90):
            raise ValueError("Dip debe estar entre 0 y 90")

        if not (0 <= rake <= 180):
            raise ValueError("Rake debe estar entre 0 y 180")

        # ----------------------------------
        # 1. DIP = 0 (cuadrantes curvos)
        # ----------------------------------
        if dip == 0:
            return self._dip_null_xy(dip, rake, valor_cinematic)

        # ----------------------------------
        # 2. STRIKE–SLIP PURO
        # ----------------------------------
        if abs(valor_cinematic) == 3:
            return self._strike_slip_xy(dip, rake, valor_cinematic)

        # ----------------------------------
        # 3. RAKE = 90 → vertical puro
        # ----------------------------------
        if rake == 90:
            x = 0.0
            y = self._dip_to_y(dip, valor_cinematic)
            return x, y

        # ----------------------------------
        # 4. CASO GENERAL
        # ----------------------------------
        x = self._rake_to_x(rake, valor_cinematic)
        y = self._dip_to_y(dip, valor_cinematic)

        return x, y

    def plot_kinematic(self, dip, rake, cine_1, cine_2=None, **kwargs):
        x, y = self.dip_rake_to_xy(dip, rake, cine_1, cine_2)
        self.scatter(x, y, **kwargs)

########################################################################################################################
    # grafico del circulo
    def _draw_strike_ring(self, r=1.5): # con 1.42 queda
        circle = Circle(
            (0, 0), r,
            fill=False,
            lw=1,
            color="black",
        )
        self.add_patch(circle)

        # Etiquetas principales
        labels = {
            0: (0, r + 0.06, "0°"),
            90: (r + 0.06, 0, "90°"),
            180: (0, -r - 0.06, "180°"),
            270: (-r - 0.08, 0, "270°"),
        }

        for _, (x, y, txt) in labels.items():
            self.text(x, y, txt, ha="center", va="center", fontsize=9)

    def strike_to_xy(self, strike, r=1.5):
        if not (0 <= strike < 360):
            raise ValueError("Strike debe estar entre 0 y 360")

        theta = np.radians(90 - strike)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return x, y

    def plot_strike(self, strike, r=1.5, **kwargs):
        if not (0 <= strike < 360):
            raise ValueError("Strike debe estar entre 0 y 360")

        theta = np.radians(90 - strike)
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        self.scatter(x, y, **kwargs)

    def _draw_limit_squeare(self, r=1.0):

        square_x = [-r, r, r, -r, -r]
        square_y = [-r, -r, r, r, -r]

        self.plot(
            square_x,
            square_y,
            color='black',
            linewidth=1,
            linestyle='--',
            alpha=0.7
        )

    def plot_fault(self, strike, dip, rake, cine_1, cine_2 = None, **kwargs):
        strike, dip, rake, cine_1, cine_2 = np.atleast_1d(strike, dip, rake, cine_1, cine_2)
        for s, d, r, c1, c2 in zip(strike, dip, rake, cine_1, cine_2):
            x1,y1 = self.strike_to_xy(s)
            x0,y0 = self.dip_rake_to_xy(d, r, c1, c2)
            self.plot(
                (x0,x1),(y0,y1),
                color='black',
                linewidth=0.5,
                linestyle=':',
                alpha=0.5
            )

            self.plot_strike(s, r=1.5, **kwargs)
            self.plot_kinematic(d, r, c1, c2, **kwargs)



# Registrar el Axes
register_projection(KinematicAxes)

