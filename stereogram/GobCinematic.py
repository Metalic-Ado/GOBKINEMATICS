import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.projections import register_projection
import numpy as np
from matplotlib.patches import Circle
from GOBESTEREONET import GobFallas2 as gf2
from matplotlib.path import Path
from matplotlib.patches import FancyArrowPatch

def _double_dashed_arrow(
    self,
    x1, y1, x2, y2,
    arrow_scale=10,
    color='black',
    alpha=0.7,
    zorder=10
):
    # 1 → 2
    arr1 = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='-|>',
        mutation_scale=arrow_scale,
        linestyle='--',
        linewidth=1.2,
        color=color,
        alpha=alpha,
        zorder=zorder
    )

    # 2 → 1
    arr2 = FancyArrowPatch(
        (x2, y2), (x1, y1),
        arrowstyle='-|>',
        mutation_scale=arrow_scale,
        linestyle='--',
        linewidth=1.2,
        color=color,
        alpha=alpha,
        zorder=zorder
    )

    self.add_patch(arr1)
    self.add_patch(arr2)


def half_circle_marker(upper=True, n=30):
    """
    Retorna un marcador tipo medio círculo.
    upper=True  -> mitad superior
    upper=False -> mitad inferior
    """
    theta = np.linspace(0, np.pi, n)
    if not upper:
        theta = -theta

    verts = np.column_stack([
        np.cos(theta),
        np.sin(theta)
    ])

    verts = np.vstack([[0, 0], verts, [0, 0]])

    codes = (
        [Path.MOVETO] +
        [Path.LINETO] * (len(verts) - 2) +
        [Path.CLOSEPOLY]
    )

    return Path(verts, codes)


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

# ______________________________________________________________________________________________________________________
# base matematica, para el rake y dip

    # normal 1 e inversa -1, dextral 3 y sinestral -3, Nx + Dx =  4, Nx + Sx = -2, Ix + Dx = 2, Ix + Sx = - 4
    def _cinematic_main(self, cine_1, cine_2 = None):
        cine_1, cine_2 =  np.atleast_1d(cine_1, cine_2)
        valor_cinematic = gf2.cinematic_array(cine_1, cine_2)
        return valor_cinematic


    def _validate_rake(self, rake, valor_cinematic):

        if valor_cinematic in (2, -2):  # dominio 0–90
            if not (0 <= rake < 90):
                raise ValueError(
                    f"Rake {rake}° no existe para valor_cinematic={valor_cinematic}"
                )
        # normal 1 e inversa -1, dextral 3 y sinestral -3, Nx + Dx =  4, Nx + Sx = -2, Ix + Dx = 2, Ix + Sx = - 4
        elif valor_cinematic in (4, -4):  # dominio 90–180
            if not (90 < rake <= 180):
                raise ValueError(
                    f"Rake {rake}° no existe para valor_cinematic={valor_cinematic}"
                )

    def changes_magnitud_rake(self, dip, rake, valor_cinematic):
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

    # normal 1 e inversa -1, dextral 3 y sinestral -3, Nx + Dx =  4, Nx + Sx = -2, Ix + Dx = 2, Ix + Sx = - 4

    def _rake_to_x(self, dip, rake, valor_cinematic):

        self._validate_rake( rake, valor_cinematic)

        mag = self.changes_magnitud_rake(dip, rake, valor_cinematic)

        # Sx → izquierda
        if valor_cinematic < 0:
            return -mag

        # Dx → derecha
        return +mag

    def _dip_to_y(self, dip, rake, valor_cinematic):


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

    def dip_rake_to_xy(self, dip, rake, cine_1, cine_2=None):

        valor_cinematic = self._cinematic_main(cine_1, cine_2)

        # -----------------
        # Validaciones
        # -----------------
        if not (0 <= dip <= 90):
            raise ValueError("Dip debe estar entre 0 y 90")

        if not (0 <= rake <= 180):
            raise ValueError("Rake debe estar entre 0 y 180")


        # -----------------
        # DIP → Y
        # -----------------

        y = self._dip_to_y(dip,rake, valor_cinematic)
        # -----------------
        # RAKE → X (ida y vuelta)
        # -----------------
        x = self._rake_to_x(dip, rake, valor_cinematic)

        return x, y

    def plot_kinematic(self, dip, rake, cine_1, cine_2=None, **kwargs):

        x, y = self.dip_rake_to_xy(dip, rake, cine_1, cine_2)
        valor_cinematic = self._cinematic_main(cine_1, cine_2)

        # -----------------------------
        # Caso límite: dip = 90 # se crea una punto mediano que simboliza inversa o dextral
        # -----------------------------
        if dip == 90:
            # normal 1 e inversa -1, dextral 3 y sinestral -3, Nx + Dx =  4, Nx + Sx = -2, Ix + Dx = 2, Ix + Sx = - 4
            if valor_cinematic in (-1 ,2, -4):  # Ix → mitad superior
                marker = half_circle_marker(upper=True)

            elif valor_cinematic in (1, -2, 4):  # Nx → mitad inferior
                marker = half_circle_marker(upper=False)

            else:
                marker = "o"  # seguridad

            self.scatter(
                x, y,
                marker=marker,
                **kwargs
            )

        # -----------------------------
        # Caso normal
        # -----------------------------
        else:
            self.scatter(x, y, **kwargs)

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
        strike = np.atleast_1d(strike)

        if not (0 <= strike < 360):
            raise ValueError("Strike debe estar entre 0 y 360")

        theta = np.radians(90 - strike)
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        self.plot(
            x, y,
            linestyle='None',
            **kwargs
        )
# en el cuadrado se encuentran los casos especiales
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

    def plot_fault(
            self,
            strike, dip, rake,
            cine_1, cine_2=None,
            show_strike=True,
            show_connector=True,
            **kwargs
    ):


        strike, dip, rake, cine_1, cine_2 = np.atleast_1d(
            strike, dip, rake, cine_1, cine_2
        )


        for s, d, r, c1, c2 in zip(strike, dip, rake, cine_1, cine_2):




            # ----------------------------------
            # Color único por falla
            # ----------------------------------
            color = kwargs.get("color", None)
            if color is None:
                color = np.random.rand(3, )

            # ----------------------------------
            # Coordenadas
            # ----------------------------------
            x1, y1 = self.strike_to_xy(s)
            x0, y0 = self.dip_rake_to_xy(d, r, c1, c2)

            # ----------------------------------
            # Línea conectora
            # ----------------------------------
            if show_connector:
                self.plot(
                    (x0, x1), (y0, y1),
                    color="black",
                    linewidth=0.5,
                    linestyle=':',
                    alpha=0.5,
                    zorder=1
                )

            # ----------------------------------
            # Strike
            # ----------------------------------
            if show_strike:
                self.plot_strike(
                    s,
                    r=1.5,
                    color=color,
                    marker='x',  # 👈 símbolo distinto
                    markersize=15,
                    zorder=3,
                    **{k: v for k, v in kwargs.items() if k != "color"}
                )

            # ----------------------------------
            # Punto cinemático
            # ----------------------------------
            self.plot_kinematic(
                d, r, c1, c2,
                color=color,
                zorder=4,
                **{k: v for k, v in kwargs.items() if k != "color"}
            )

    # TEMPORALIDAD
    def plot_fault_temporal_chain(
            self,
            dip, rake,
            cine_1, cine_2=None,
            indices=None,
            color="crimson",
            linewidth=1.2,
            alpha=0.9,
            zorder=15
    ):
        if indices is None or len(indices) < 2:
            raise ValueError("La secuencia temporal debe tener al menos 2 fallas")

        dip, rake, cine_1, cine_2 = np.atleast_1d(
            dip, rake, cine_1, cine_2
        )

        # Coordenadas de la secuencia
        coords = []
        for i in indices:
            x, y = self.dip_rake_to_xy(
                dip[i], rake[i], cine_1[i], cine_2[i]
            )
            coords.append((x, y))

        # Flechas consecutivas: antigua → joven
        for (x0, y0), (x1, y1) in zip(coords[:-1], coords[1:]):
            self.annotate(
                "",
                xy=(x1, y1),  # más joven
                xytext=(x0, y0),  # más antigua
                arrowprops=dict(
                    arrowstyle="->",
                    color=color,
                    lw=linewidth,
                    linestyle="--",  # 👈 ENTRE CORTES
                    alpha=alpha
                ),
                zorder=zorder
            )

    def plot_fault_conjugates(
            self,
            strike, dip, rake,
            cine_1, cine_2=None,
            conjugate_groups=None,
            arrow_scale=15,
            **kwargs
    ):
        strike, dip, rake, cine_1, cine_2 = np.atleast_1d(
            strike, dip, rake, cine_1, cine_2
        )

        # ----------------------------------
        # Coordenadas cinemáticas
        # ----------------------------------
        XY = []
        for d, r, c1, c2 in zip(dip, rake, cine_1, cine_2):
            x, y = self.dip_rake_to_xy(d, r, c1, c2)
            XY.append((x, y))

        # ----------------------------------
        # Plot puntos cinemáticos
        # ----------------------------------
        for (x, y) in XY:
            self.scatter(
                x, y,
                s=60,
                color=kwargs.get("color", "black"),
                zorder=4
            )

        # ----------------------------------
        # Flechas conjugadas ↔ (entrecortadas)
        # ----------------------------------
        for group in conjugate_groups:
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    x1, y1 = XY[group[i]]
                    x2, y2 = XY[group[j]]

                    arr = FancyArrowPatch(
                        (x1, y1), (x2, y2),
                        arrowstyle='<->',  # 👈 doble cabeza
                        mutation_scale=arrow_scale,
                        linestyle='--',  # 👈 cuerpo entrecortado
                        linewidth=1.2,
                        color=kwargs.get("color", "black"),
                        alpha=0.7,
                        zorder=10
                    )

                    self.add_patch(arr)

    def _apply_offset_if_overlap(self, x0, y0, x1, y1, offset_mag=0.02):
        """
        Aplica un pequeño offset perpendicular SOLO si los puntos se superponen
        o están demasiado cerca.
        """

        dist = np.hypot(x1 - x0, y1 - y0)

        # Si están prácticamente encima
        if dist < 1e-2:
            return x0, y0, x1 + offset_mag, y1

        dx, dy = x1 - x0, y1 - y0

        # Vector normal (perpendicular)
        n = np.array([-dy, dx])
        n_norm = np.linalg.norm(n)

        if n_norm == 0:
            return x0, y0, x1, y1

        n /= n_norm
        ox, oy = offset_mag * n

        return x0 + ox, y0 + oy, x1 + ox, y1 + oy

    def plot_fault_date_chain(
            self,
            strike, dip, rake,
            cine_1, cine_2=None,
            color="darkblue",
            linewidth=1.2,
            alpha=0.9,
            zorder=12
    ):
        """
        Plot temporal automático:
        - Flechas consecutivas (0→1→2→…)
        - Strike y cinemática tratados por separado
        - Offset automático si hay superposición
        """

        strike, dip, rake, cine_1, cine_2 = np.atleast_1d(
            strike, dip, rake, cine_1, cine_2
        )

        n = len(dip)
        if n < 2:
            raise ValueError("Se requieren al menos 2 puntos")

        # ==================================================
        # DIP – RAKE (cinemática)
        # ==================================================
        kin_coords = []

        for d, r, c1, c2 in zip(dip, rake, cine_1, cine_2):
            x, y = self.dip_rake_to_xy(d, r, c1, c2)
            kin_coords.append((x, y))

            # Punto siempre
            self.scatter(
                x, y,
                color=color,
                s=20,
                zorder=zorder
            )

        # Flechas temporales (solo si cambia)
        for (x0, y0), (x1, y1) in zip(kin_coords[:-1], kin_coords[1:]):
            if np.allclose([x0, y0], [x1, y1]):
                continue

            x0o, y0o, x1o, y1o = self._apply_offset_if_overlap(
                x0, y0, x1, y1, offset_mag=0.02
            )

            self.annotate(
                "",
                xy=(x1o, y1o),
                xytext=(x0o, y0o),
                arrowprops=dict(
                    arrowstyle="->",
                    color=color,
                    lw=linewidth,
                    linestyle="--",
                    alpha=alpha
                ),
                zorder=zorder
            )

        # ==================================================
        # STRIKE
        # ==================================================
        strike_coords = []

        for s in strike:
            xs, ys = self.strike_to_xy(s)
            strike_coords.append((xs, ys))

            # Punto siempre
            self.scatter(
                xs, ys,
                color=color,
                s=20,
                zorder=zorder - 1
            )

        # Flechas solo si cambia strike
        for i in range(n - 1):
            if strike[i] == strike[i + 1]:
                continue

            x0, y0 = strike_coords[i]
            x1, y1 = strike_coords[i + 1]

            x0o, y0o, x1o, y1o = self._apply_offset_if_overlap(
                x0, y0, x1, y1, offset_mag=0.02
            )

            self.annotate(
                "",
                xy=(x1o, y1o),
                xytext=(x0o, y0o),
                arrowprops=dict(
                    arrowstyle="->",
                    color=color,
                    lw=linewidth,
                    linestyle="--",
                    alpha=alpha
                ),
                zorder=zorder - 1
            )

        # ==================================================
        # CONEXIONES STRIKE ↔ DIP–RAKE
        # ==================================================
        # Inicio
        self.plot(
            [strike_coords[0][0], kin_coords[0][0]],
            [strike_coords[0][1], kin_coords[0][1]],
            linestyle="--",
            color=color,
            alpha=0.5,
            zorder=zorder - 2
        )

        # Final
        self.plot(
            [strike_coords[-1][0], kin_coords[-1][0]],
            [strike_coords[-1][1], kin_coords[-1][1]],
            linestyle="--",
            color=color,
            alpha=0.5,
            zorder=zorder - 2
        )

        # ==============================
        # CONEXIONES STRIKE ↔ DIP–RAKE
        # ==============================
        # Inicio
        self.plot(
            [strike_coords[0][0], kin_coords[0][0]],
            [strike_coords[0][1], kin_coords[0][1]],
            linestyle="--",
            color=color,
            alpha=0.5,
            zorder=zorder - 2
        )

        # Final
        self.plot(
            [strike_coords[-1][0], kin_coords[-1][0]],
            [strike_coords[-1][1], kin_coords[-1][1]],
            linestyle="--",
            color=color,
            alpha=0.5,
            zorder=zorder - 2
        )



# Registrar el Axes
register_projection(KinematicAxes)

# tamaño del punto debe ser el peso o la importancia de la falla
# el color debe ser a litologia
# el simbolo debe ser el estilo de la falla
# el punto hueco debe ser un falla sin cinematica
# una fecha denota temporalidad
# flecha doble indica conjugada
# el color debe ser a litologia
# el simbolo debe ser el estilo de la falla
# flecha entrecortada  falla hereogenea
# numeracion para el mismo dominio
# si se puede eje z desplazamiento

