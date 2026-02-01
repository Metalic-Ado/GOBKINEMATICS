from matplotlib.axes import Axes
from matplotlib.projections import register_projection
from matplotlib.patches import Circle
import numpy as np

from . import kinematics_transform
from . import kinematics_logic
from . import kinematics_visual
from . import no_estable

class KinematicAxes(Axes):
    name = 'kinematic'

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

    def plot_kinematic(self, dip, rake, cine_1, cine_2=None, **kwargs):

        dip = np.atleast_1d(dip)
        rake = np.atleast_1d(rake)
        cine_1 = np.atleast_1d(cine_1)
        cine_2 = np.atleast_1d(cine_2) if cine_2 is not None else None

        x, y = kinematics_transform.dip_rake_to_xy(dip, rake, cine_1, cine_2)
        valor_cinematic = kinematics_logic._cinematic_main(cine_1, cine_2)

        for xi, yi, d, vc in zip(x, y, dip, valor_cinematic):

            # -----------------------------
            # Caso límite: dip = 90
            # -----------------------------
            if d == 90:
                if vc in (-1, 2, -4):  # Ix
                    marker = kinematics_visual.half_circle_marker(upper=True)
                elif vc in (1, -2, 4):  # Nx
                    marker = kinematics_visual.half_circle_marker(upper=False)
                else:
                    marker = "o"
            else:
                marker = "o"

            self.scatter(xi, yi, marker=marker, **kwargs)

    def plot_strike(self, strike, r=1.5, **kwargs):

        x, y = kinematics_transform.strike_to_xy(strike, r)

        self.scatter(
            x, y,
            **kwargs
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
            x1, y1 = kinematics_transform.strike_to_xy(s)
            x0, y0 = kinematics_transform.dip_rake_to_xy(d, r, c1, c2)

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
                    s=100,
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
    def plot_fault_temporality(
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
            x, y = kinematics_transform.dip_rake_to_xy(
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

        # ------------------------------
        # Coordenadas cinemáticas
        # ------------------------------
        XY = []
        for d, r, c1, c2 in zip(dip, rake, cine_1, cine_2):
            x, y = kinematics_transform.dip_rake_to_xy(d, r, c1, c2)
            XY.append((x, y))

        # ------------------------------
        # Plot puntos
        # ------------------------------
        for x, y in XY:
            self.scatter(
                x, y,
                s=kwargs.get("s", 60),
                color=kwargs.get("color", "black"),
                zorder=4
            )

        if not conjugate_groups:
            return

        # ------------------------------
        # Flechas conjugadas
        # ------------------------------
        for group in conjugate_groups:
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    x1, y1 = map(float, XY[group[i]])
                    x2, y2 = map(float, XY[group[j]])

                    arr1, arr2 = kinematics_visual.double_dashed_arrow(
                        x1, y1, x2, y2,
                        arrow_scale=arrow_scale,
                        color=kwargs.get("color", "black")
                    )

                    self.add_patch(arr1)
                    self.add_patch(arr2)

    def plot_fault_hetereogeneous(
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
            x, y = kinematics_transform.dip_rake_to_xy(d, r, c1, c2)
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

            x0o, y0o, x1o, y1o = kinematics_visual._apply_offset_if_overlap(
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
            xs, ys = kinematics_transform.strike_to_xy(s)
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

            x0o, y0o, x1o, y1o = kinematics_visual._apply_offset_if_overlap(
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

# PLOT GENERAL  DESDE ARRAYS

    def plot_fault_N4_caso_3(self, dip, cine_1, cine_2, **kwargs):
        """
        Plot especial para N4 caso 3 (sin rake, dos cinemáticas)
        """

        valor = kinematics_logic.cinematic_array(cine_1, cine_2)

        pts = kinematics_transform.transform_N4_caso_3(dip, valor)
        if pts is None:
            return

        x, y = zip(*pts)

        self.plot(
            x, y,
            linewidth=2,
            linestyle="--",
            **kwargs
        )

    def plot_fault_N3_caso_1(self, dip, rake, conectar_linea=False, **kwargs):
        """
        Plot especial para N3 caso 1
        """

        pts = kinematics_transform.transform_N3_caso_1(dip, rake)
        if pts is None:
            return

        (x1, y1), (x2, y2) = pts

        # ---------------------------
        # 1️⃣ Puntos huecos
        # ---------------------------
        self.scatter(
            [x1, x2],
            [y1, y2],
            s=50,
            facecolors='none',  # huecos
            edgecolors='black',
            zorder=5,
            **kwargs
        )

        # ---------------------------
        # 2️⃣ Línea opcional
        # ---------------------------
        if conectar_linea:
            self.plot(
                [x1, x2],
                [y1, y2],
                linestyle='--',
                color='black',
                alpha=0.3,
                zorder=1
            )

    def plot_fault_N3_caso_2(self, dip, cine_1, cine_2=None, **kwargs):

        valor = kinematics_logic.cinematic_array(cine_1, cine_2)

        y1 = 1 - dip / 90
        y2 = -y1

        if valor in (1, -1):  # normal / inversa
            y = y2 if valor == 1 else y1
            self.plot([0, 1], [y, y], **kwargs)
            self.plot([0, -1], [y, y], **kwargs)

        elif valor in (3, -3):  # dextral / sinestral
            xa = 1 if valor == 3 else -1
            self.plot([0, xa], [y1, y1], **kwargs)
            self.plot([0, xa], [y2, y2], **kwargs)

    def plot_fault_N2_caso_1(self, dip, **kwargs):
        """
        N2 caso único:
        - strike + dip
        - sin rake
        - sin cinemática
        - 4 rectas horizontales simétricas
        """

        x0 = 0
        xp = 1
        xn = -1

        y1 = 1 - dip / 90
        y2 = -y1

        # Todas las líneas comparten los mismos kwargs (color, alpha, lw, etc.)
        self.plot([x0, xp], [y1, y1], **kwargs)
        self.plot([x0, xn], [y1, y1], **kwargs)

        self.plot([x0, xp], [y2, y2], **kwargs)
        self.plot([x0, xn], [y2, y2], **kwargs)

    def plot_fault_N1_caso_unico(self, strike, **kwargs):
        """
        N1 caso único:
        - solo strike
        - punto sobre el círculo
        """
        self.plot_strike(strike, **kwargs)

    def plot_general_faults(self, strike, dip, rake, cine_1, cine_2 = None):
        faults = no_estable.from_lists(strike, dip, rake, cine_1, cine_2)
        st, di, rak, cin1, cin2 = no_estable.extract_arrays(faults)
        registro = no_estable.clasify_for_items(st, di, rak, cin1, cin2)
        registros_finales = [no_estable.process_registration(r) for r in registro]

        # PARA N5
        conformes = [r for r in registros_finales if r["estado"] == "conforme"]
        strike_c = []
        dip_c = []
        rake_c = []
        cine1_c = []
        cine2_c = []

        for r in conformes:
            d = r["datos"]
            strike_c.append(d["strike"])
            dip_c.append(d["dip"])
            rake_c.append(d["rake"])
            cine1_c.append(d["cine_1"])
            cine2_c.append(d["cine_2"])

        self.plot_fault(
            strike_c,
            dip_c,
            rake_c,
            cine1_c,
            cine2_c,
            color="red",
            label="Conformes"
        )

        # caso N4 caso 3

        n4_caso_3 = [
            r for r in registros_finales
            if r.get("modo") == "N4_caso_3"
        ]

        for r in n4_caso_3:
            d = r["datos"]
            self.plot_fault_N4_caso_3(
                dip=d["dip"],
                cine_1=d["cine_1"],
                cine_2=d["cine_2"],
                color="purple",
                alpha=0.7
            )

        # caso N3 caso 1
        n3_caso_1 = [r for r in registros_finales if r.get("modo") == "N3_caso_1"]
        for r in n3_caso_1:
            d = r["datos"]
            self.plot_fault_N3_caso_1(
                dip=d["dip"],
                rake=d["rake"],
                conectar_linea=True  # opcional
            )
        n3_caso_2 = [r for r in registros_finales if r.get("modo") == "N3_caso_2"]

        for r in n3_caso_2:
            d = r["datos"]
            self.plot_fault_N3_caso_2(
                dip=d["dip"],
                cine_1=d["cine_1"],
                cine_2=d["cine_2"],
                color="red",
                linestyle="--",
                alpha=0.8
            )

        n2 = [r for r in registros_finales if r.get("modo") == "N2_caso_unico"]

        for r in n2:
            d = r["datos"]
            self.plot_fault_N2_caso_1(
                dip=d["dip"],
                color="gray",
                linestyle="--",
                linewidth=1.5,
                alpha=0.8
            )
        # caso N1
        n1 = [r for r in registros_finales if r.get("modo") == "N1_caso_unico"]

        for r in n1:
            d = r["datos"]
            self.plot_fault_N1_caso_unico(
                strike=d["strike"],
                s=100,
                facecolors="none",  # hueco
                edgecolors="black",
                alpha=0.6
            )



# Registrar el Axes
register_projection(KinematicAxes)

# crear condiciones para colocar o rellenar data que se sobreentiende
# validadcion de datos
# si solo existe el strike y dip, se hace dos linea rectas pertenecientes al dip
# si tenemos strike, dip y rake, se plotean dos puntos
# strike dip
# strike dip 1 cinematica
# strike dip 2 cinematicas
# strike dip rake
# strike dip rake 1 cinematica