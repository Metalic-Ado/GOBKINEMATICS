from matplotlib.axes import Axes
from matplotlib.projections import register_projection
from matplotlib.patches import Circle
import numpy as np


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
    # PARA EL STRIKE
    def _draw_strike_only_marker(
            self,
            x,
            y,
            size=0.025,
            **kwargs
    ):
        """
        Dibuja el símbolo N1:
        círculo con una X interior.
        """

        color = kwargs.get("color", "black")
        alpha = kwargs.get("alpha", 1.0)
        zorder = kwargs.get("zorder", 4)
        linewidth = kwargs.get("linewidth", 1.2)

        # Círculo exterior
        circle = Circle(
            (x, y),
            radius=size,
            fill=False,
            edgecolor=color,
            linewidth=linewidth,
            alpha=alpha,
            zorder=zorder
        )

        self.add_patch(circle)

        # X interior
        x_verts = np.array([
            [-0.65, -0.65],
            [0.65, 0.65],
            [np.nan, np.nan],
            [-0.65, 0.65],
            [0.65, -0.65]
        ])

        x_verts = x_verts * size

        self.plot(
            x + x_verts[:, 0],
            y + x_verts[:, 1],
            color=color,
            alpha=alpha,
            linewidth=linewidth,
            zorder=zorder
        )

        return circle

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

        kwargs.setdefault("color", "gray")
        kwargs.setdefault("alpha", 0.25)
        kwargs.setdefault("linewidth", 0.7)
        kwargs.setdefault("linestyle", "-")
        kwargs.setdefault("zorder", 1)

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
        Grafica fallas completas procesadas por FAULTCORE.

        Entrada pública:
            strike
            dip
            rake
            cine_1
            cine_2

        FAULTCORE se encarga de:
            - Normalización.
            - Clasificación.
            - Validación.
            - Evaluación cinemática.

        GOBKINEMATICS se encarga únicamente
        de la representación gráfica.
        """

        # ======================================================
        # 1. PROCESAMIENTO MEDIANTE FAULTCORE
        # ======================================================

        registros = kinematics_norm.process_fault_data(
            strike=strike,
            dip=dip,
            rake=rake,
            cine_1=cine_1,
            cine_2=cine_2
        )

        # ======================================================
        # 2. OPCIONES DE DIBUJO
        # ======================================================

        color = kwargs.pop("color", "black")
        zorder = kwargs.pop("zorder", 4)

        point_kwargs = {
            **kwargs,
            "color": color,
            "zorder": zorder
        }

        # ======================================================
        # 3. REPRESENTACIÓN DE FALLAS COMPLETAS
        # ======================================================

        for registro in registros:

            # Solo representar registros N5 conformes.
            if registro.get("nivel") != "N5":
                continue

            if registro.get("estado") != "conforme":
                continue

            datos = registro["datos"]

            s = datos.get("strike")
            d = datos.get("dip")
            r = datos.get("rake")
            vc = registro.get("valor_cinematic")

            # Verificar que los datos necesarios para
            # esta representación estén disponibles.
            if any(valor is None for valor in (s, d, r, vc)):
                continue

            # ==================================================
            # 4. COORDENADAS DEL STRIKE
            # ==================================================

            x_strike, y_strike = (
                kinematics_math.strike_to_xy(s)
            )

            # ==================================================
            # 5. COORDENADAS DIP-RAKE
            # ==================================================

            x_kin, y_kin = (
                kinematics_math.dip_rake_to_xy(
                    d,
                    r,
                    vc
                )
            )

            # ==================================================
            # 6. CONECTOR
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
            # 7. PUNTO STRIKE
            # ==================================================

            if show_strike:
                self._draw_strike_point(
                    x_strike,
                    y_strike,
                    **point_kwargs
                )

            # ==================================================
            # 8. PUNTO CINEMÁTICO
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
            strike,
            dip,
            rake,
            cine_1,
            cine_2=None,
            indices=None,
            color="crimson",
            linewidth=1.2,
            alpha=0.9,
            zorder=15
    ):
        """
        Representa la evolución temporal de las fallas.

        strike:
            Se recibe y procesa mediante FAULTCORE.
            Su función dentro del análisis temporal
            se desarrollará posteriormente.

        dip, rake y componentes cinemáticas:
            Se utilizan para calcular las coordenadas
            de los puntos cinemáticos.

        indices:
            Orden temporal de las fallas.
            Del registro más antiguo al más reciente.
        """

        # ======================================================
        # 1. COMPROBAR ÍNDICES
        # ======================================================

        if indices is None or len(indices) < 2:
            raise ValueError(
                "La secuencia temporal debe tener al menos 2 fallas."
            )

        # ======================================================
        # 2. PROCESAMIENTO MEDIANTE FAULTCORE
        # ======================================================

        registros = kinematics_norm.process_fault_data(
            strike=strike,
            dip=dip,
            rake=rake,
            cine_1=cine_1,
            cine_2=cine_2
        )

        # ======================================================
        # 3. OBTENER COORDENADAS CINEMÁTICAS
        # ======================================================

        coords = []

        for i in indices:

            if not isinstance(i, (int, np.integer)):
                raise TypeError(
                    "Los índices temporales deben ser enteros."
                )

            if i < 0 or i >= len(registros):
                raise IndexError(
                    f"El índice temporal {i} está fuera del rango."
                )

            registro = registros[i]

            # Solo utilizar registros N5 conformes.
            if (
                    registro.get("nivel") != "N5"
                    or registro.get("estado") != "conforme"
            ):
                raise ValueError(
                    f"El registro {i} no es una falla N5 conforme."
                )

            datos = registro["datos"]

            d = datos.get("dip")
            r = datos.get("rake")
            vc = registro.get("valor_cinematic")

            if any(valor is None for valor in (d, r, vc)):
                raise ValueError(
                    f"El registro {i} no contiene datos suficientes "
                    "para calcular sus coordenadas."
                )

            x, y = kinematics_math.dip_rake_to_xy(
                d,
                r,
                vc
            )

            coords.append((float(x[0]), float(y[0])))

        # ======================================================
        # 4. REPRESENTAR EVOLUCIÓN TEMPORAL
        # ======================================================

        for (x0, y0), (x1, y1) in zip(
                coords[:-1],
                coords[1:]
        ):
            self.annotate(
                "",
                xy=(x1, y1),
                xytext=(x0, y0),
                arrowprops=dict(
                    arrowstyle="->",
                    color=color,
                    lw=linewidth,
                    linestyle="--",
                    alpha=alpha
                ),
                zorder=zorder
            )

    def plot_fault_conjugates(
            self,
            strike,
            dip,
            rake,
            cine_1,
            cine_2=None,
            conjugate_groups=None,
            arrow_scale=15,
            **kwargs
    ):
        """
        Representa fallas conjugadas.

        FAULTCORE realiza el procesamiento y evaluación.
        GOBKINEMATICS calcula las coordenadas y representa
        los puntos y las relaciones conjugadas.
        """

        # ======================================================
        # 1. PROCESAMIENTO MEDIANTE FAULTCORE
        # ======================================================

        registros = kinematics_norm.process_fault_data(
            strike=strike,
            dip=dip,
            rake=rake,
            cine_1=cine_1,
            cine_2=cine_2
        )

        # ======================================================
        # 2. OBTENER COORDENADAS CINEMÁTICAS
        # ======================================================

        XY = []

        for i, registro in enumerate(registros):

            if (
                    registro.get("nivel") != "N5"
                    or registro.get("estado") != "conforme"
            ):
                raise ValueError(
                    f"El registro {i} no es una falla N5 conforme."
                )

            datos = registro["datos"]

            d = datos.get("dip")
            r = datos.get("rake")
            vc = registro.get("valor_cinematic")

            if any(valor is None for valor in (d, r, vc)):
                raise ValueError(
                    f"El registro {i} no contiene datos suficientes."
                )

            x, y = kinematics_math.dip_rake_to_xy(
                d,
                r,
                vc
            )

            XY.append((
                float(x[0]),
                float(y[0])
            ))

        # ======================================================
        # 3. REPRESENTAR LOS PUNTOS
        # ======================================================

        for x, y in XY:
            self.scatter(
                x,
                y,
                s=kwargs.get("s", 60),
                color=kwargs.get("color", "black"),
                zorder=4
            )

        # ======================================================
        # 4. REPRESENTAR RELACIONES CONJUGADAS
        # ======================================================

        if not conjugate_groups:
            return

        for group in conjugate_groups:

            for i in range(len(group)):

                for j in range(i + 1, len(group)):

                    idx1 = group[i]
                    idx2 = group[j]

                    if not (
                            0 <= idx1 < len(XY)
                            and 0 <= idx2 < len(XY)
                    ):
                        raise IndexError(
                            "Un índice de conjugación está fuera "
                            "del rango de registros."
                        )

                    x1, y1 = XY[idx1]
                    x2, y2 = XY[idx2]

                    arr1, arr2 = kinematics_visual.double_dashed_arrow(
                        x1,
                        y1,
                        x2,
                        y2,
                        arrow_scale=arrow_scale,
                        color=kwargs.get("color", "black")
                    )

                    self.add_patch(arr1)
                    self.add_patch(arr2)

    def plot_fault_hetereogeneous(
            self,
            strike,
            dip,
            rake,
            cine_1,
            cine_2=None,
            color="darkblue",
            linewidth=1.2,
            alpha=0.9,
            zorder=12
    ):
        """
        Representa la evolución temporal heterogénea.

        - Evolución cinemática Dip-Rake.
        - Evolución independiente del Strike.
        - Conexiones entre Strike y Dip-Rake.
        - Offset automático cuando existen superposiciones.

        FAULTCORE procesa y evalúa los registros.
        GOBKINEMATICS realiza la representación.
        """

        # ==================================================
        # 1. PROCESAMIENTO MEDIANTE FAULTCORE
        # ==================================================

        registros = kinematics_norm.process_fault_data(
            strike=strike,
            dip=dip,
            rake=rake,
            cine_1=cine_1,
            cine_2=cine_2
        )

        # ==================================================
        # 2. VALIDAR CANTIDAD DE REGISTROS
        # ==================================================

        n = len(registros)

        if n < 2:
            raise ValueError(
                "Se requieren al menos 2 fallas."
            )

        # ==================================================
        # 3. OBTENER DATOS Y COORDENADAS
        # ==================================================

        kin_coords = []
        strike_coords = []

        for i, registro in enumerate(registros):

            # Solo admitir fallas N5 conformes.
            if (
                    registro.get("nivel") != "N5"
                    or registro.get("estado") != "conforme"
            ):
                raise ValueError(
                    f"El registro {i} no es una falla N5 conforme."
                )

            datos = registro["datos"]

            s = datos.get("strike")
            d = datos.get("dip")
            r = datos.get("rake")
            vc = registro.get("valor_cinematic")

            if any(valor is None for valor in (s, d, r, vc)):
                raise ValueError(
                    f"El registro {i} no contiene datos suficientes."
                )

            # ----------------------------------------------
            # Coordenadas DIP-RAKE
            # ----------------------------------------------

            x, y = kinematics_math.dip_rake_to_xy(
                d,
                r,
                vc
            )

            kin_coords.append((
                float(x[0]),
                float(y[0])
            ))

            # ----------------------------------------------
            # Coordenadas STRIKE
            # ----------------------------------------------

            xs, ys = kinematics_math.strike_to_xy(s)

            strike_coords.append((
                float(xs[0]),
                float(ys[0])
            ))

        # ==================================================
        # 4. REPRESENTACIÓN DIP-RAKE
        # ==================================================

        for x, y in kin_coords:
            self.scatter(
                x,
                y,
                color=color,
                s=20,
                zorder=zorder
            )

        # Flechas temporales cinemáticas
        for (x0, y0), (x1, y1) in zip(
                kin_coords[:-1],
                kin_coords[1:]
        ):

            if np.allclose([x0, y0], [x1, y1]):
                continue

            x0o, y0o, x1o, y1o = (
                kinematics_visual._apply_offset_if_overlap(
                    x0,
                    y0,
                    x1,
                    y1,
                    offset_mag=0.02
                )
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
        # 5. REPRESENTACIÓN STRIKE
        # ==================================================

        for xs, ys in strike_coords:
            self.scatter(
                xs,
                ys,
                color=color,
                s=20,
                zorder=zorder - 1
            )

        # Flechas temporales Strike
        for i in range(n - 1):

            if registros[i]["datos"]["strike"] == (
                    registros[i + 1]["datos"]["strike"]
            ):
                continue

            x0, y0 = strike_coords[i]
            x1, y1 = strike_coords[i + 1]

            x0o, y0o, x1o, y1o = (
                kinematics_visual._apply_offset_if_overlap(
                    x0,
                    y0,
                    x1,
                    y1,
                    offset_mag=0.02
                )
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
        # 6. CONEXIONES STRIKE ↔ DIP-RAKE
        # ==================================================

        # Conexión inicial
        self.plot(
            [strike_coords[0][0], kin_coords[0][0]],
            [strike_coords[0][1], kin_coords[0][1]],
            linestyle="--",
            color=color,
            alpha=0.5,
            zorder=zorder - 2
        )

        # Conexión final
        self.plot(
            [strike_coords[-1][0], kin_coords[-1][0]],
            [strike_coords[-1][1], kin_coords[-1][1]],
            linestyle="--",
            color=color,
            alpha=0.5,
            zorder=zorder - 2
        )

    def plot_fault_N4_caso_3(
            self,
            dip,
            valor_cinematic,
            longitud_guion=0.08,
            representation_mode="compact",
            **kwargs
    ):
        """
        Representación gráfica de N4 caso 3.

        Complete:
            Dibuja el segmento geométrico original.

        Compact:
            Dibuja un pequeño guion centrado
            y orientado según el segmento original.
        """

        if representation_mode not in ("complete", "compact"):
            raise ValueError(
                "representation_mode debe ser 'complete' o 'compact'."
            )

        pts = kinematics_math.transform_N4_caso_3(
            dip,
            valor_cinematic
        )

        if pts is None:
            return

        (x1, y1), (x2, y2) = pts

        # ==========================================
        # 1. CALCULAR EL CENTRO DEL SEGMENTO
        # ==========================================

        xc, yc = kinematics_math.center_segment(
            (x1, y1),
            (x2, y2)
        )

        # ==========================================
        # 2. REPRESENTACIÓN COMPLETA
        # ==========================================

        if representation_mode == "complete":

            self.plot(
                [x1, x2],
                [y1, y2],
                **kwargs
            )

        # ==========================================
        # 3. REPRESENTACIÓN COMPACTA
        # ==========================================

        elif representation_mode == "compact":

            dx = x2 - x1
            dy = y2 - y1

            longitud = (dx ** 2 + dy ** 2) ** 0.5

            if longitud == 0:
                return

            # Vector unitario
            ux = dx / longitud
            uy = dy / longitud

            # Mitad de la longitud del guion
            mitad = longitud_guion / 2.0

            # Extremos del guion central
            xa = xc - ux * mitad
            ya = yc - uy * mitad

            xb = xc + ux * mitad
            yb = yc + uy * mitad

            self.plot(
                [xa, xb],
                [ya, yb],
                **kwargs
            )

        # Devolver el mismo centro en ambos modos
        return (xc, yc)

    def plot_fault_N3_caso_1(
            self,
            dip,
            rake,
            conectar_linea=False,
            **kwargs
    ):
        pts = kinematics_math.transform_N3_caso_1(dip, rake)

        if pts is None:
            return

        (x1, y1), (x2, y2) = pts

        # Caso especial: falla vertical
        if dip == 90:

            # Primer punto: orientación según la cinemática inversa
            if rake <= 90:

                marker1 = kinematics_visual.half_circle_marker(upper=False)
                marker2 = kinematics_visual.half_circle_marker(upper=True)

            else:
                marker1 = kinematics_visual.half_circle_marker(upper=False)
                marker2 = kinematics_visual.half_circle_marker(upper=True)

            self.scatter(
                x1, y1,
                marker=marker2,
                s=50,
                facecolors="none",
                edgecolors="black",
                zorder=5,
                **kwargs
            )

            self.scatter(
                x2, y2,
                marker=marker1,
                s=50,
                facecolors="none",
                edgecolors="black",
                zorder=5,
                **kwargs
            )

        else:
            self.scatter(
                [x1, x2],
                [y1, y2],
                s=50,
                facecolors="none",
                edgecolors="black",
                zorder=5,
                **kwargs
            )

        if conectar_linea:
            self.plot(
                [x1, x2],
                [y1, y2],
                linestyle="--",
                color="black",
                alpha=0.3,
                zorder=1
            )

    def plot_fault_N3_caso_2(
            self,
            dip,
            valor_cinematic,
            longitud_guion=0.08,
            representation_mode="compact",
            **kwargs
    ):
        """
        Representación gráfica de N3 caso 2.

        Complete:
            Dibuja los dos segmentos originales.

        Compact:
            Dip-slip (1, -1):
                Un único guion central entre los dos segmentos.

            Strike-slip (3, -3):
                Dos guiones centrales, uno por cada segmento.
        """

        if representation_mode not in ("complete", "compact"):
            raise ValueError(
                "representation_mode debe ser 'complete' o 'compact'."
            )

        segmentos = kinematics_math.transform_N3_case2(
            dip,
            valor_cinematic
        )

        if segmentos is None:
            return

        # ==========================================
        # 1. DETERMINAR LOS CENTROS
        # ==========================================

        if valor_cinematic in (1, -1):

            centros = [
                kinematics_math.center_segment(
                    segmento[0],
                    segmento[1]
                )
                for segmento in segmentos
            ]

            centro_general = kinematics_math.center_segment(
                centros[0],
                centros[1]
            )

            centros_representacion = [centro_general]

        elif valor_cinematic in (3, -3):

            centros_representacion = [
                kinematics_math.center_segment(
                    segmento[0],
                    segmento[1]
                )
                for segmento in segmentos
            ]

        else:
            return

        # ==========================================
        # 2. REPRESENTACIÓN COMPLETA
        # ==========================================

        if representation_mode == "complete":

            for segmento in segmentos:
                (x1, y1), (x2, y2) = segmento

                self.plot(
                    [x1, x2],
                    [y1, y2],
                    **kwargs
                )

        # ==========================================
        # 3. REPRESENTACIÓN COMPACTA
        # ==========================================

        elif representation_mode == "compact":

            for centro in centros_representacion:
                xc, yc = centro

                self.plot(
                    [
                        xc - longitud_guion / 2,
                        xc + longitud_guion / 2
                    ],
                    [yc, yc],
                    **kwargs
                )

        # Devolver los mismos centros en ambos modos
        return centros_representacion

    def plot_fault_N2_caso_1(
            self,
            dip,
            longitud_guion=0.08,
            representation_mode="compact",
            **kwargs
    ):
        """
        N2 caso único:
        - Strike + dip.
        - Sin rake.
        - Sin cinemática.

        Modo completo:
            Dibuja los cuatro segmentos geométricos originales.

        Modo compacto:
            Dibuja dos guiones representativos.

        Los centros geométricos se conservan
        independientemente del modo de representación.
        """

        if representation_mode not in ("complete", "compact"):
            raise ValueError(
                "representation_mode debe ser 'complete' o 'compact'."
            )

        # ==========================================
        # 1. GEOMETRÍA ORIGINAL
        # ==========================================

        y1 = 1 - dip / 90
        y2 = -y1

        segmentos = [
            ((0, y1), (1, y1)),
            ((0, y1), (-1, y1)),
            ((0, y2), (1, y2)),
            ((0, y2), (-1, y2))
        ]

        # Centros representativos originales
        centros = [
            (0, y1),
            (0, y2)
        ]

        # ==========================================
        # 2. MODO COMPLETO
        # ==========================================

        if representation_mode == "complete":

            for (x1, y_inicio), (x2, y_fin) in segmentos:
                self.plot(
                    [x1, x2],
                    [y_inicio, y_fin],
                    **kwargs
                )

        # ==========================================
        # 3. MODO COMPACTO
        # ==========================================

        elif representation_mode == "compact":

            for xc, yc in centros:
                self.plot(
                    [
                        xc - longitud_guion / 2,
                        xc + longitud_guion / 2
                    ],
                    [yc, yc],
                    **kwargs
                )

        return centros

    def plot_fault_N1_caso_unico(self, strike, **kwargs):
        x, y = kinematics_math.strike_to_xy(strike)
        return self._draw_strike_only_marker(x, y, **kwargs)

    def plot_general_faults(
            self,
            strike,
            dip,
            rake,
            cine_1,
            cine_2=None,
            representation_mode="complete"
    ):
        """
        Representa los registros estructurales procesados por FAULTCORE.

        Función temporal de diagnóstico:
            - Identifica nivel y subtipo.
            - Comprueba el estado.
            - Registra qué representación se ejecuta.
            - Identifica casos no representados.
        """
        # ==================================================
        # 0. VALIDAR MODO DE REPRESENTACIÓN
        # ==================================================

        if representation_mode not in ("complete", "compact"):
            raise ValueError(
                "representation_mode debe ser 'complete' o 'compact'."
            )
        # ==================================================
        # 1. PROCESAMIENTO DE DATOS
        # ==================================================

        registros_finales = kinematics_norm.process_fault_data(
            strike=strike,
            dip=dip,
            rake=rake,
            cine_1=cine_1,
            cine_2=cine_2
        )

        # ==================================================
        # 2. CONTADORES
        # ==================================================

        conteo_dibujo = {
            "N1": 0,
            "N2": 0,
            "N2_caso_2": 0,
            "N3_caso_1": 0,
            "N3_caso_2": 0,
            "N3_caso_3": 0,
            "N4_caso_3": 0,
            "N5": 0
        }

        conteo_estado = {
            "conforme": 0,
            "inconforme": 0,
            "otros": 0
        }

        no_representados = []

        # ==================================================
        # 3. DIAGNÓSTICO DE REGISTROS
        # ==================================================

        print("\n========== DIAGNÓSTICO GENERAL ==========")
        print(f"TOTAL DE REGISTROS: {len(registros_finales)}")

        for i, registro in enumerate(registros_finales):
            datos = registro.get("datos", {})

            print(f"\nREGISTRO {i + 1}")
            print(f"  Nivel: {registro.get('nivel')}")
            print(f"  Subtipo: {registro.get('subtipo')}")
            print(f"  Estado: {registro.get('estado')}")
            print(f"  Strike: {datos.get('strike')}")
            print(f"  Dip: {datos.get('dip')}")
            print(f"  Rake: {datos.get('rake')}")
            print(f"  Cine 1: {datos.get('cine_1')}")
            print(f"  Cine 2: {datos.get('cine_2')}")
            print(f"  Valor cinemático: {registro.get('valor_cinematic')}")

        print("\n=========================================\n")

        # ==================================================
        # 4. RECORRER REGISTROS
        # ==================================================

        for i, registro in enumerate(registros_finales):

            nivel = registro.get("nivel")
            subtipo = registro.get("subtipo")
            estado = registro.get("estado")

            datos = registro.get("datos", {})

            s = datos.get("strike")
            d = datos.get("dip")
            r = datos.get("rake")

            vc = registro.get("valor_cinematic")

            print(
                f"\n[DIBUJO] Registro {i + 1} | "
                f"{nivel} | {subtipo} | {estado}"
            )

            # --------------------------------------------------
            # 4.1 ESTADO
            # --------------------------------------------------

            if estado == "conforme":
                conteo_estado["conforme"] += 1

            elif estado == "inconforme":
                conteo_estado["inconforme"] += 1

            else:
                conteo_estado["otros"] += 1

            # Solo representar registros conformes
            if estado != "conforme":
                print("  DESCARTADO: estado diferente de conforme")

                no_representados.append(
                    (i + 1, nivel, subtipo, estado)
                )

                continue

            # ==================================================
            # 5. REPRESENTACIÓN DEL STRIKE
            # ==================================================

            x_strike = None
            y_strike = None

            if s is not None:
                x_strike, y_strike = kinematics_math.strike_to_xy(s)

                if not (
                        nivel == "N1"
                        and subtipo == "solamente_strike"
                ):
                    self._draw_strike_point(
                        x_strike,
                        y_strike,
                        color="black",
                        alpha=0.6,
                        zorder=4
                    )
            # ==================================================
            # 6. N5: FALLAS COMPLETAS
            # ==================================================

            if nivel == "N5":

                if any(valor is None for valor in (s, d, r, vc)):
                    print("  DESCARTADO: faltan datos para N5")

                    no_representados.append(
                        (i + 1, nivel, subtipo, "datos faltantes")
                    )

                    continue

                x_kin, y_kin = (
                    kinematics_math.dip_rake_to_xy(
                        d,
                        r,
                        vc
                    )
                )

                # Conector strike-cinemática
                self._draw_connector(
                    x_strike,
                    y_strike,
                    x_kin,
                    y_kin,
                    color="black",
                    linewidth=0.5,
                    linestyle="--",
                    alpha=0.25,
                    zorder=1
                )

                # Punto cinemático
                self._draw_kinematic_point(
                    x_kin,
                    y_kin,
                    d,
                    vc,
                    color="red",
                    zorder=4
                )

                conteo_dibujo["N5"] += 1

                print("  REPRESENTACIÓN: N5")
                continue

            # ==================================================
            # 7. N4: CASO 3
            # ==================================================

            elif (
                    nivel == "N4"
                    and subtipo == "sin_rake_dos_cinematicas"
            ):

                if d is None or vc is None or s is None:
                    print("  DESCARTADO: faltan datos para N4")

                    no_representados.append(
                        (i + 1, nivel, subtipo, "datos faltantes")
                    )

                    continue

                # Obtener los extremos del segmento N4
                puntos_n4 = kinematics_math.transform_N4_caso_3(
                    d,
                    vc
                )

                if puntos_n4 is None:
                    print("  DESCARTADO: no se pudo calcular el segmento N4")

                    no_representados.append(
                        (i + 1, nivel, subtipo, "error geométrico")
                    )

                    continue

                p1, p2 = puntos_n4

                # Calcular el centro del segmento
                x_centro, y_centro = kinematics_math.center_segment(
                    p1,
                    p2
                )

                # Representación del segmento N4
                self.plot_fault_N4_caso_3(
                    dip=d,
                    valor_cinematic=vc,
                    representation_mode=representation_mode,
                    color="purple",
                    alpha=0.7
                )

                # Conectar el strike con el centro del segmento
                self._draw_connector(
                    x_strike,
                    y_strike,
                    x_centro,
                    y_centro,
                    color="black",
                    linewidth=0.7,
                    linestyle="--",
                    alpha=0.25,
                    zorder=1
                )

                conteo_dibujo["N4_caso_3"] += 1

                print("  REPRESENTACIÓN: N4 caso 3")
                continue
            # ==================================================
            # 8. N3: CASO 1
            # ==================================================

            elif (
                    nivel == "N3"
                    and subtipo == "geometria_sin_cinematicas"
            ):

                if d is None or r is None or s is None:
                    print("  DESCARTADO: faltan datos para N3 caso 1")

                    no_representados.append(
                        (i + 1, nivel, subtipo, "datos faltantes")
                    )

                    continue

                # Obtener los dos puntos geométricos N3
                puntos_n3 = kinematics_math.transform_N3_caso_1(d, r)

                if puntos_n3 is None:
                    print("  DESCARTADO: no se pudieron calcular los puntos N3")

                    no_representados.append(
                        (i + 1, nivel, subtipo, "error geométrico")
                    )

                    continue

                (x1, y1), (x2, y2) = puntos_n3

                # Dibujar los dos puntos N3
                self.plot_fault_N3_caso_1(
                    dip=d,
                    rake=r,
                    conectar_linea=False
                )

                # Conectar el strike con el primer punto N3
                self._draw_connector(
                    x_strike,
                    y_strike,
                    x1,
                    y1,
                    color="black",
                    linewidth=0.7,
                    linestyle="--",
                    alpha=0.25,
                    zorder=1
                )

                # Conectar el strike con el segundo punto N3
                self._draw_connector(
                    x_strike,
                    y_strike,
                    x2,
                    y2,
                    color="black",
                    linewidth=0.7,
                    linestyle="--",
                    alpha=0.25,
                    zorder=1
                )

                conteo_dibujo["N3_caso_1"] += 1

                print("  REPRESENTACIÓN: N3 caso 1")
                continue
            # ==================================================
            # 9. N3: CASO 2
            # ==================================================

            # ==================================================
            # 9. N3: CASO 2
            # ==================================================

            elif (
                    nivel == "N3"
                    and subtipo == "una_cinematica_sin_rake"
            ):

                if d is None or vc is None or s is None:
                    print("  DESCARTADO: faltan datos para N3 caso 2")

                    no_representados.append(
                        (i + 1, nivel, subtipo, "datos faltantes")
                    )

                    continue

                # ----------------------------------------------
                # 1. Dibujar los guiones centrales
                # ----------------------------------------------

                centros_n3 = self.plot_fault_N3_caso_2(
                    dip=d,
                    valor_cinematic=vc,
                    longitud_guion=0.08,
                    representation_mode=representation_mode,
                    color="red",
                    linewidth=2,
                    alpha=0.8,
                    zorder=5
                )

                if centros_n3 is None:
                    print("  DESCARTADO: no se pudo representar N3 caso 2")

                    no_representados.append(
                        (i + 1, nivel, subtipo, "error geométrico")
                    )

                    continue

                # ----------------------------------------------
                # 2. Conectar cada centro con el strike
                # ----------------------------------------------

                for x_centro, y_centro in centros_n3:
                    self._draw_connector(
                        x_strike,
                        y_strike,
                        x_centro,
                        y_centro,
                        color="black",
                        linewidth=0.7,
                        linestyle="--",
                        alpha=0.25,
                        zorder=1
                    )

                # ----------------------------------------------
                # 3. Registrar representación
                # ----------------------------------------------

                conteo_dibujo["N3_caso_2"] += 1

                print(
                    f"  REPRESENTACIÓN: N3 caso 2 | "
                    f"Valor cinemático: {vc} | "
                    f"Guiones: {len(centros_n3)}"
                )

                continue


            # ==================================================
            # N3: CASO 3
            # STRIKE + DOS CINEMÁTICAS, SIN DIP NI RAKE
            # ==================================================

            elif (
                    nivel == "N3"
                    and subtipo == "dos_cinematicas_sin_dip_ni_rake"
            ):

                cine_1 = datos.get("cine_1")
                cine_2 = datos.get("cine_2")

                if s is None or cine_1 is None or cine_2 is None:
                    print("  DESCARTADO: faltan datos para N3 caso 3")

                    no_representados.append(
                        (i + 1, nivel, subtipo, "datos faltantes")
                    )

                    continue

                # ----------------------------------------------
                # 1. Calcular las posiciones de ambos puntos
                # ----------------------------------------------

                puntos_n3 = kinematics_math.get_cinematic_pair_point_positions(
                    cine_1=cine_1,
                    cine_2=cine_2,
                    radius=1.0,
                    offset=0.15
                )

                if puntos_n3 is None:
                    print("  DESCARTADO: combinación cinemática no reconocida")

                    no_representados.append(
                        (i + 1, nivel, subtipo, "error de ubicación")
                    )

                    continue

                (x1, y1), (x2, y2) = puntos_n3

                # ----------------------------------------------
                # 2. Conectar ambos puntos con el strike
                # ----------------------------------------------

                for x_auxiliar, y_auxiliar in puntos_n3:
                    self._draw_connector(
                        x_strike,
                        y_strike,
                        x_auxiliar,
                        y_auxiliar,
                        color="black",
                        linewidth=0.7,
                        linestyle="--",
                        alpha=0.25,
                        zorder=1
                    )

                # ----------------------------------------------
                # 3. Dibujar los dos puntos auxiliares
                # ----------------------------------------------

                self.plot(
                    [x1, x2],
                    [y1, y2],
                    marker="o",
                    markersize=5,
                    color="red",
                    linestyle="None",
                    alpha=0.9,
                    zorder=5
                )

                # ----------------------------------------------
                # 4. Registrar representación
                # ----------------------------------------------

                conteo_dibujo["N3_caso_3"] += 1

                print(
                    f"  REPRESENTACIÓN: N3 caso 3 | "
                    f"Cinemáticas: {cine_1} + {cine_2} | "
                    f"Puntos: {puntos_n3}"
                )

                continue


            # ==================================================
            # 10. N2: CASO 1
            # ==================================================
            # ==================================================
            # 10. N2: CASO 1
            # ==================================================

            elif (
                    nivel == "N2"
                    and subtipo == "plano_sin_rake_ni_cinematica"
            ):

                if d is None:
                    print("  DESCARTADO: falta dip para N2")

                    no_representados.append(
                        (i + 1, nivel, subtipo, "dip faltante")
                    )

                    continue

                centros_n2 = self.plot_fault_N2_caso_1(
                    dip=d,
                    longitud_guion=0.08,
                    representation_mode=representation_mode,
                    color="red",
                    linewidth=2,
                    alpha=0.8,
                    zorder=5
                )

                for x_centro, y_centro in centros_n2:
                    self._draw_connector(
                        x_strike,
                        y_strike,
                        x_centro,
                        y_centro,
                        color="black",
                        linewidth=0.7,
                        linestyle="--",
                        alpha=0.25,
                        zorder=1
                    )

                conteo_dibujo["N2"] += 1

                print(
                    f"  REPRESENTACIÓN: N2 | "
                    f"Guiones: {len(centros_n2)}"
                )

                continue

            # ==================================================
            # N2: CASO 2
            # STRIKE + UNA CINEMÁTICA, SIN DIP NI RAKE
            # ==================================================

            elif (
                    nivel == "N2"
                    and subtipo == "strike_con_una_cinematica"
            ):

                cine_1 = datos.get("cine_1")

                if s is None or cine_1 is None:
                    print("  DESCARTADO: faltan datos para N2 caso 2")

                    no_representados.append(
                        (i + 1, nivel, subtipo, "datos faltantes")
                    )

                    continue

                # ----------------------------------------------
                # 1. Calcular la posición del punto auxiliar
                # ----------------------------------------------

                punto_auxiliar = kinematics_math.get_cinematic_point_position(
                    cinematic=cine_1,
                    radius=1.0
                )

                if punto_auxiliar is None:
                    print("  DESCARTADO: cinemática no reconocida")

                    no_representados.append(
                        (i + 1, nivel, subtipo, "error de ubicación")
                    )

                    continue

                x_auxiliar, y_auxiliar = punto_auxiliar

                # ----------------------------------------------
                # 2. Conectar el punto auxiliar con el strike
                # ----------------------------------------------

                self._draw_connector(
                    x_strike,
                    y_strike,
                    x_auxiliar,
                    y_auxiliar,
                    color="black",
                    linewidth=0.7,
                    linestyle="--",
                    alpha=0.25,
                    zorder=1
                )

                # ----------------------------------------------
                # 3. Dibujar el punto auxiliar
                # ----------------------------------------------

                self.plot(
                    [x_auxiliar],
                    [y_auxiliar],
                    marker="o",
                    markersize=5,
                    color="red",
                    linestyle="None",
                    alpha=0.9,
                    zorder=5
                )

                # ----------------------------------------------
                # 4. Registrar representación
                # ----------------------------------------------

                conteo_dibujo["N2_caso_2"] += 1

                print(
                    f"  REPRESENTACIÓN: N2 caso 2 | "
                    f"Cinemática: {cine_1} | "
                    f"Punto: {punto_auxiliar}"
                )

                continue

            # ==================================================
            # 11. N1: CASO ÚNICO
            # ==================================================

            elif (

                    nivel == "N1"

                    and subtipo == "solamente_strike"

            ):

                self._draw_strike_only_marker(

                    x_strike,

                    y_strike,

                    color="black",

                    alpha=0.6,

                    zorder=4

                )

                conteo_dibujo["N1"] += 1

                print("  REPRESENTACIÓN: N1")

                continue

            # ==================================================
            # 12. NIVEL O SUBTIPO NO RECONOCIDO
            # ==================================================

            print("  SIN REPRESENTACIÓN: nivel/subtipo no reconocido")

            no_representados.append(
                (i + 1, nivel, subtipo, "sin función gráfica")
            )

        # ==================================================
        # 13. RESUMEN DE REPRESENTACIONES
        # ==================================================

        print("\n========== RESUMEN DE REPRESENTACIÓN ==========")

        print("\nEstados:")
        for estado, cantidad in conteo_estado.items():
            print(f"  {estado}: {cantidad}")

        print("\nRepresentaciones ejecutadas:")
        for caso, cantidad in conteo_dibujo.items():
            print(f"  {caso}: {cantidad}")

        print("\nRegistros no representados:")

        if no_representados:
            for registro in no_representados:
                print(
                    f"  Registro {registro[0]} | "
                    f"Nivel: {registro[1]} | "
                    f"Subtipo: {registro[2]} | "
                    f"Motivo: {registro[3]}"
                )
        else:
            print("  Ninguno")

        print("\n===============================================\n")


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