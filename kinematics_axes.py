from matplotlib.axes import Axes
from matplotlib.projections import register_projection
from matplotlib.patches import Circle
import numpy as np


from . import kinematics_logic
from . import kinematics_visual
from . import kinematics_norm
from . import kinematics_math



class KinematicAxes(Axes):
    name = "kinematic"

    # Constantes geométricas del gráfico
    KINEMATIC_RADIUS = 1.0
    STRIKE_RADIUS = 1.5
    AXIS_LIMIT = 1.6

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Límites del gráfico
        self.set_xlim(-self.AXIS_LIMIT, self.AXIS_LIMIT)
        self.set_ylim(-self.AXIS_LIMIT, self.AXIS_LIMIT)

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
        self._draw_limit_square()

    # -------------------------
    # Dibujo de la cruz central
    # -------------------------

    def _draw_cross(self):
        R = self.KINEMATIC_RADIUS

        # Horizontal
        self.plot(
            [-R, R], [0, 0],
            color="black",
            lw=1.5
        )

        # Vertical
        self.plot(
            [0, 0], [-R, R],
            color="black",
            lw=1.5
        )
    # -------------------------
    # Etiquetas cinemáticas
    # -------------------------
    def _draw_labels(self):
        R = self.KINEMATIC_RADIUS
        offset = 0.1

        # Horizontal
        self.text(
            R + offset, 0, "Dx",
            ha="left", va="center",
            fontsize=15, fontweight="bold",
            fontfamily="serif"
        )

        self.text(
            -R - offset, 0, "Sx",
            ha="right", va="center",
            fontsize=15, fontweight="bold",
            fontfamily="serif"
        )

        # Vertical
        self.text(
            0, R + offset, "Ix",
            ha="center", va="bottom",
            fontsize=15, fontweight="bold",
            fontfamily="serif"
        )

        self.text(
            0, -R - offset, "Nx",
            ha="center", va="top",
            fontsize=15, fontweight="bold",
            fontfamily="serif"
        )

    def _draw_dip_scale(self):
        dips = [0, 30, 60, 90]
        R = self.KINEMATIC_RADIUS
        x_text = -0.06
        dt = 0.04

        for dip in dips:
            y = R * (1 - dip / 90)

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

    def _draw_strike_ring(self):
        r = self.STRIKE_RADIUS

        circle = Circle(
            (0, 0), r,
            fill=False,
            lw=1,
            color="black"
        )
        self.add_patch(circle)

        labels = {
            0: (0, r + 0.06, "0°"),
            90: (r + 0.06, 0, "90°"),
            180: (0, -r - 0.06, "180°"),
            270: (-r - 0.08, 0, "270°"),
        }

        for _, (x, y, txt) in labels.items():
            self.text(
                x, y, txt,
                ha="center", va="center", fontsize=9
            )

    def _draw_limit_square(self):
        R = self.KINEMATIC_RADIUS

        square_x = [-R, R, R, -R, -R]
        square_y = [-R, -R, R, R, -R]

        self.plot(
            square_x,
            square_y,
            color="black",
            linewidth=1,
            linestyle="--",
            alpha=0.7
        )

    def _draw_rake_scale_right(self):
        rakes = [0, 30, 60, 120, 150, 180]
        y_text = 0.06
        dt = 0.04

        for rake in rakes:
            x = -(rake - 90) / 90

            # Tick horizontal hacia abajo
            self.plot(
                [x, x],
                [-dt, 0],
                color="black",
                lw=1
            )

            # Texto de la escala
            self.text(
                x, y_text, f"{rake}º",
                ha="center",
                va="bottom",
                fontsize=9
            )

        self.text(
            -0.9, y_text + 0.01, "Rake",
            ha="left",
            va="center",
            fontsize=9,
            alpha=0.7
        )

    def _draw_rake_scale_left(self):
        rakes = [0, 30, 60, 120, 150, 180]
        y_text = -0.06
        dt = 0.04

        for rake in rakes:
            x = (rake - 90) / 90

            # Tick horizontal hacia arriba
            self.plot(
                [x, x],
                [0, dt],
                color="black",
                lw=1
            )

            # Texto de la escala
            self.text(
                x, y_text, f"{rake}º",
                ha="center",
                va="top",
                fontsize=9
            )

        self.text(
            0.815, y_text - 0.03, "Rake",
            ha="center",
            va="bottom",
            fontsize=9,
            alpha=0.7
        )
########################################################################################################################
############################################### PLOT DE LOS DATOS ######################################################
# CREO QUE ES MEJOR SEPARAR Y LUEGO UNIR
# PLOTEAR EL PUNTO DE DIP AND RAKE
# PLOTEAR EL PUNTO DE STRIKE
# PLOTEO DE LOS LA UNION DEL DIPRAKE AND STRIKE
# PLOTEO DE LA UNION DE DOS PUNTOS RAKE DIP MEDIANTE LINEA
# PLOTEO DE LA UNION DE DOS PUNTOS DE STRIKES MEDIANTE LINEA
# PLOTEO DE LA UNION DE MAS DE DOS PUNTOS DE RAKE AN DIPS
# PLOTEO DE LA UNION DE MAS DE DOS PUNTOS DE STRIKES
# PLOTEO SEGUN LA CLASIFICACION GENERAL
# si los valores None para numeros es mejor np.Nan


    # ==========================================================
    # PLOT PRINCIPAL DE FALLAS
    # ==========================================================

    def _draw_kinematic_point(
            self,
            x,
            y,
            dip,
            valor_cinematic,
            **kwargs
    ):
        """
        Dibuja únicamente el punto cinemático.
        """

        # Caso especial: falla vertical
        if dip == 90:

            # Inversa
            if valor_cinematic in (-1, 2, -4):
                marker = kinematics_visual.half_circle_marker(
                    upper=True
                )

            # Normal
            elif valor_cinematic in (1, -2, 4):
                marker = kinematics_visual.half_circle_marker(
                    upper=False
                )

            else:
                marker = "o"

        else:
            marker = "o"

        return self.scatter(
            x,
            y,
            marker=marker,
            **kwargs
        )


    def _draw_strike_point(
            self,
            x,
            y,
            **kwargs
    ):
        """
        Dibuja únicamente el punto correspondiente al strike.
        """

        return self.scatter(
            x,
            y,
            marker="x",
            **kwargs
        )


    def _draw_connector(
            self,
            x1,
            y1,
            x2,
            y2,
            **kwargs
    ):
        """
        Dibuja la conexión entre el punto de strike
        y el punto cinemático.
        """

        return self.plot(
            [x1, x2],
            [y1, y2],
            **kwargs
        )


    def plot_fault(
            self,
            strike,
            dip,
            rake,
            cine_1,
            cine_2=None,
            show_strike=True,
            show_connector=True,
            **kwargs
    ):
        """
        Grafica fallas completas.

        Entrada pública para el usuario/geólogo:

            strike
            dip
            rake
            cine_1
            cine_2

        El usuario no necesita conocer valor_cinematic.
        """

        # ======================================================
        # 1. NORMALIZACIÓN BÁSICA
        # ======================================================

        data = kinematics_norm.normalize_basic_data(
            strike=strike,
            dip=dip,
            rake=rake,
            cine_1=cine_1,
            cine_2=cine_2
        )


        # ======================================================
        # 2. VALIDACIÓN GEOMÉTRICA
        # ======================================================

        data = kinematics_logic.validate_complete_faults(
            data
        )


        # ======================================================
        # 3. OPCIONES DE DIBUJO
        # ======================================================

        color = kwargs.pop("color", "black")

        zorder = kwargs.pop("zorder", 4)

        point_kwargs = {
            **kwargs,
            "color": color,
            "zorder": zorder
        }


        # ======================================================
        # 4. GRAFICAR CADA FALLA
        # ======================================================

        for (
            s,
            d,
            r,
            c1,
            c2,
            vc
        ) in zip(
            data["strike"],
            data["dip"],
            data["rake"],
            data["cine_1"],
            data["cine_2"],
            data["valor_cinematic"]
        ):

            # --------------------------------------------------
            # Coordenadas del STRIKE
            # --------------------------------------------------

            x_strike, y_strike = (
                kinematics_math.strike_to_xy(s)
            )

            # --------------------------------------------------
            # Coordenadas DIP-RAKE
            # --------------------------------------------------

            x_kin, y_kin = (
                kinematics_math.dip_rake_to_xy(
                    d,
                    r,
                    vc
                )
            )


            # ==================================================
            # CONECTOR
            # ==================================================

            if show_connector:

                self._draw_connector(
                    x_strike,
                    y_strike,
                    x_kin,
                    y_kin,
                    color="black",
                    linewidth=0.5,
                    linestyle=":",
                    alpha=0.5,
                    zorder=1
                )


            # ==================================================
            # PUNTO STRIKE
            # ==================================================

            if show_strike:

                self._draw_strike_point(
                    x_strike,
                    y_strike,
                    **point_kwargs
                )


            # ==================================================
            # PUNTO CINEMÁTICO
            # ==================================================

            self._draw_kinematic_point(
                x_kin,
                y_kin,
                d,
                vc,
                **point_kwargs
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
            x, y = kinematics_math.dip_rake_to_xy(
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
            x, y = kinematics_math.dip_rake_to_xy(d, r, c1, c2)
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
            x, y = kinematics_math.dip_rake_to_xy(d, r, c1, c2)
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
            xs, ys = kinematics_math.strike_to_xy(s)
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

        pts = kinematics_math.transform_N4_caso_3(dip, valor)
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

        pts = kinematics_math.transform_N3_caso_1(dip, rake)
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
        valor = int(valor[0])

        segmentos = kinematics_math.transform_N3_case2(dip, valor)

        if segmentos is None:
            return

        for segmento in segmentos:
            x, y = zip(*segmento)
            self.plot(x, y, **kwargs)

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
        - Solo strike.
        - Punto sobre el círculo.
        """
        x, y = kinematics_math.strike_to_xy(strike)

        return self._draw_strike_point(
            x,
            y,
            **kwargs
        )

    def plot_general_faults(self, strike, dip, rake, cine_1, cine_2 = None):
        faults = kinematics_norm.from_lists(strike, dip, rake, cine_1, cine_2)
        st, di, rak, cin1, cin2 = kinematics_norm.extract_arrays(faults)
        registro = kinematics_logic.clasify_for_items(st, di, rak, cin1, cin2)
        registros_finales = [kinematics_logic.process_registration(r) for r in registro]

        # STRIKE: representar todos los registros que lo tengan
        for r in registros_finales:
            d = r["datos"]
            strike = d.get("strike")

            if strike is None:
                continue

            x, y = kinematics_math.strike_to_xy(strike)

            self._draw_strike_point(
                x,
                y,
                color="black",
                alpha=0.6,
                zorder=4
            )

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
                color="red",
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