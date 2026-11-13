from matplotlib.axes import Axes
from matplotlib.projections import register_projection
from matplotlib.patches import Circle
import numpy as np

from . import kinematics_math, kinematics_visual, kinematics_norm



class KinematicAxes(Axes):
    name = "kinematic"

    # Constantes geométricas del gráfico
    KINEMATIC_RADIUS = 1.0
    STRIKE_RADIUS = 1.5
    AXIS_LIMIT = 1.6

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Registro de artistas para personalización de estilos
        self._style_artists = {
            "strike": {
                nivel: {} for nivel in ("N1", "N2", "N3", "N4", "N5")
            },
            "fault": {
                nivel: {} for nivel in ("N1", "N2", "N3", "N4", "N5")
            },
            "aux": {
                nivel: {} for nivel in ("N1", "N2", "N3", "N4", "N5")
            }
        }

        # Configuración de estilos personalizados
        self._style_overrides = {
            "strike": {
                "general": {},
                "levels": {
                    nivel: {} for nivel in ("N1", "N2", "N3", "N4", "N5")
                },
                "cases": {
                    nivel: {} for nivel in ("N1", "N2", "N3", "N4", "N5")
                }
            },
            "fault": {
                "general": {},
                "levels": {
                    nivel: {} for nivel in ("N1", "N2", "N3", "N4", "N5")
                },
                "cases": {
                    nivel: {} for nivel in ("N1", "N2", "N3", "N4", "N5")
                }
            }
        }

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

    def _register_style_artist(
            self,
            family,
            nivel,
            subtipo,
            artists,
            artist_type=None
    ):
        """
        Registra los artistas gráficos por familia,
        nivel y subtipo.

        artist_type permite identificar automáticamente
        el tipo de representación gráfica.
        """

        if family not in self._style_artists:
            raise ValueError(f"Familia gráfica no válida: {family}")

        if nivel not in self._style_artists[family]:
            raise ValueError(f"Nivel no válido: {nivel}")

        if artists is None:
            return

        # Normalizar a lista
        if not isinstance(artists, (list, tuple)):
            artists = [artists]

        # Asignar el tipo de artista cuando se indique
        if artist_type is not None:
            for artist in artists:
                artist._gobkinematics_artist_type = artist_type

        # Crear el espacio del subtipo si no existe
        if subtipo not in self._style_artists[family][nivel]:
            self._style_artists[family][nivel][subtipo] = []

        # Guardar el grupo de artistas
        self._style_artists[family][nivel][subtipo].append(
            list(artists)
        )

    def _apply_strike_artist_style(self, artists, **style):
        """
        Aplica estilos a los artistas de STRIKE.

        Admite:
        - PathCollection: strike convencional.
        - Circle + Line2D: símbolo N1.

        Las propiedades no compatibles se ignoran.
        """

        from matplotlib.collections import PathCollection
        from matplotlib.patches import Circle
        from matplotlib.lines import Line2D
        from matplotlib.markers import MarkerStyle

        for artist in artists:

            # STRIKE convencional: marcador X
            if isinstance(artist, PathCollection):

                if "color" in style:
                    artist.set_color(style["color"])

                if "markersize" in style:
                    artist.set_sizes([style["markersize"] ** 2])

                if "markeredgewidth" in style:
                    artist.set_linewidths(
                        [style["markeredgewidth"]]
                    )

                if "marker" in style:
                    marker = MarkerStyle(style["marker"])
                    artist.set_paths([marker.get_path().transformed(
                        marker.get_transform()
                    )])

            # Símbolo N1: círculo exterior
            elif isinstance(artist, Circle):

                if "color" in style:
                    artist.set_edgecolor(style["color"])

                if "markersize" in style:
                    base_size = artist._gobkinematics_base_size
                    factor = style["markersize"] / 6.0
                    artist.set_radius(base_size * factor)

            # Símbolo N1: X interior
            # Símbolo N1: X interior
            elif isinstance(artist, Line2D):

                if "color" in style:
                    artist.set_color(style["color"])

                if "markersize" in style:
                    factor = style["markersize"] / 6.0

                    center_x, center_y = artist._gobkinematics_center

                    base_x = artist._gobkinematics_base_xdata
                    base_y = artist._gobkinematics_base_ydata

                    artist.set_xdata(
                        center_x + (base_x - center_x) * factor
                    )

                    artist.set_ydata(
                        center_y + (base_y - center_y) * factor
                    )

    def _apply_fault_artist_style(self, artists, **style):
        """
        Aplica estilos a los artistas de FAULT.

        Tipos admitidos:

        - point:
            Puntos circulares.
            Permite modificar marcador, color, tamaño,
            borde, relleno y transparencia.

        - semicircle:
            Semicírculos.
            Permite modificar únicamente color,
            tamaño y transparencia.

        - segment:
            Segmentos geométricos.
            Permite modificar color, grosor,
            estilo de línea y transparencia.

        Las propiedades no compatibles se ignoran.

        La geometría, posición y orientación
        de los artistas permanecen protegidas.
        """

        from matplotlib.collections import PathCollection
        from matplotlib.lines import Line2D
        from matplotlib.markers import MarkerStyle

        for artist in artists:

            artist_type = getattr(
                artist,
                "_gobkinematics_artist_type",
                None
            )

            # ==================================================
            # 1. POINT: PUNTOS CIRCULARES
            # ==================================================

            if artist_type == "point":

                # ----------------------------------------------
                # PathCollection: puntos creados mediante scatter
                # ----------------------------------------------

                if isinstance(artist, PathCollection):

                    if "color" in style:
                        artist.set_color(style["color"])

                    if "markersize" in style:
                        artist.set_sizes([
                            style["markersize"] ** 2
                        ])

                    if "marker" in style:
                        marker = MarkerStyle(style["marker"])

                        artist.set_paths([
                            marker.get_path().transformed(
                                marker.get_transform()
                            )
                        ])

                    if "markeredgecolor" in style:
                        artist.set_edgecolor(
                            style["markeredgecolor"]
                        )

                    if "markerfacecolor" in style:
                        artist.set_facecolor(
                            style["markerfacecolor"]
                        )

                    if "markeredgewidth" in style:
                        artist.set_linewidths([
                            style["markeredgewidth"]
                        ])

                    if "alpha" in style:
                        artist.set_alpha(style["alpha"])

                # ----------------------------------------------
                # Line2D: puntos creados mediante plot
                # ----------------------------------------------

                elif isinstance(artist, Line2D):

                    if "color" in style:
                        artist.set_color(style["color"])

                    if "markersize" in style:
                        artist.set_markersize(
                            style["markersize"]
                        )

                    if "marker" in style:
                        artist.set_marker(
                            style["marker"]
                        )

                    if "markeredgecolor" in style:
                        artist.set_markeredgecolor(
                            style["markeredgecolor"]
                        )

                    if "markerfacecolor" in style:
                        artist.set_markerfacecolor(
                            style["markerfacecolor"]
                        )

                    if "markeredgewidth" in style:
                        artist.set_markeredgewidth(
                            style["markeredgewidth"]
                        )

                    if "alpha" in style:
                        artist.set_alpha(style["alpha"])

            # ==================================================
            # 2. SEMICIRCLE: SEMICÍRCULOS
            # ==================================================

            elif artist_type == "semicircle":

                if isinstance(artist, PathCollection):

                    if "color" in style:
                        artist.set_color(style["color"])

                    if "markersize" in style:
                        artist.set_sizes([
                            style["markersize"] ** 2
                        ])

                    if "alpha" in style:
                        artist.set_alpha(style["alpha"])

            # ==================================================
            # 3. SEGMENT: SEGMENTOS GEOMÉTRICOS
            # ==================================================

            elif artist_type == "segment":

                if isinstance(artist, Line2D):

                    if "color" in style:
                        artist.set_color(style["color"])

                    if "linewidth" in style:
                        artist.set_linewidth(
                            style["linewidth"]
                        )

                    if "linestyle" in style:
                        artist.set_linestyle(
                            style["linestyle"]
                        )

                    if "alpha" in style:
                        artist.set_alpha(style["alpha"])

    def _refresh_strike_styles(self):

        overrides = self._style_overrides["strike"]

        general_style = overrides["general"]
        level_styles = overrides["levels"]
        case_styles = overrides["cases"]

        for nivel, subtipos in self._style_artists["strike"].items():

            for subtipo, grupos in subtipos.items():

                # Combinar estilos según su prioridad
                effective_style = {}

                effective_style.update(general_style)
                effective_style.update(level_styles[nivel])
                effective_style.update(
                    case_styles[nivel].get(subtipo, {})
                )

                # Aplicar el estilo a cada grupo de artistas
                for artists in grupos:
                    self._apply_strike_artist_style(
                        artists,
                        **effective_style
                    )

    def _refresh_fault_styles(self):
        """
        Actualiza los estilos personalizados de FAULT.

        Prioridad:
            1. General
            2. Nivel
            3. Subtipo

        El estilo más específico prevalece.

        No modifica la geometría de los artistas.
        """

        overrides = self._style_overrides["fault"]

        general_style = overrides["general"]
        level_styles = overrides["levels"]
        case_styles = overrides["cases"]

        for nivel, subtipos in self._style_artists["fault"].items():

            for subtipo, grupos in subtipos.items():

                # ----------------------------------------------
                # Combinar estilos según su prioridad
                # ----------------------------------------------

                effective_style = {}

                # 1. Estilo general
                effective_style.update(general_style)

                # 2. Estilo por nivel
                effective_style.update(
                    level_styles[nivel]
                )

                # 3. Estilo por subtipo
                effective_style.update(
                    case_styles[nivel].get(subtipo, {})
                )

                # ----------------------------------------------
                # Aplicar estilo a cada grupo de artistas
                # ----------------------------------------------

                for artists in grupos:
                    self._apply_fault_artist_style(
                        artists,
                        **effective_style
                    )

    def _set_strike_style(self, nivel=None, caso=None, **kwargs):
        """
        Almacena y actualiza estilos personalizados de STRIKE.

        nivel=None: aplica estilo general.
        nivel definido y caso=None: aplica a todo el nivel.
        caso definido: aplica al subtipo indicado.
        """

        overrides = self._style_overrides["strike"]

        # Estilo general
        if nivel is None:
            overrides["general"].update(kwargs)

        # Estilo por nivel
        elif caso is None:
            overrides["levels"][nivel].update(kwargs)

        # Estilo por subtipo
        else:
            if isinstance(caso, str):
                casos = [caso]
            else:
                casos = caso

            for subtipo in casos:
                overrides["cases"][nivel].setdefault(
                    subtipo, {}
                ).update(kwargs)

        # Actualizar los artistas existentes
        self._refresh_strike_styles()

    def style_strike(self, **kwargs):
        """Personaliza todos los símbolos STRIKE."""
        self._set_strike_style(**kwargs)

    def style_strike_N1(self, caso=None, **kwargs):
        self._set_strike_style("N1", caso, **kwargs)

    def style_strike_N2(self, caso=None, **kwargs):
        self._set_strike_style("N2", caso, **kwargs)

    def style_strike_N3(self, caso=None, **kwargs):
        self._set_strike_style("N3", caso, **kwargs)

    def style_strike_N4(self, caso=None, **kwargs):
        self._set_strike_style("N4", caso, **kwargs)

    def style_strike_N5(self, caso=None, **kwargs):
        self._set_strike_style("N5", caso, **kwargs)

    def style_fault(self, **kwargs):
        """
        Personaliza todos los elementos geométrico-cinemáticos
        de FAULT.
        """
        self._set_fault_style(**kwargs)

    def style_fault_N1(self, caso=None, **kwargs):
        """Personaliza los elementos FAULT del nivel N1."""
        self._set_fault_style("N1", caso, **kwargs)

    def style_fault_N2(self, caso=None, **kwargs):
        """Personaliza los elementos FAULT del nivel N2."""
        self._set_fault_style("N2", caso, **kwargs)

    def style_fault_N3(self, caso=None, **kwargs):
        """Personaliza los elementos FAULT del nivel N3."""
        self._set_fault_style("N3", caso, **kwargs)

    def style_fault_N4(self, caso=None, **kwargs):
        """Personaliza los elementos FAULT del nivel N4."""
        self._set_fault_style("N4", caso, **kwargs)

    def style_fault_N5(self, caso=None, **kwargs):
        """Personaliza los elementos FAULT del nivel N5."""
        self._set_fault_style("N5", caso, **kwargs)



    def _set_fault_style(self, nivel=None, caso=None, **kwargs):
        """
        Almacena y actualiza estilos personalizados de FAULT.

        nivel=None:
            Aplica estilo general.

        nivel definido y caso=None:
            Aplica estilo a todo el nivel.

        caso definido:
            Aplica estilo a uno o varios subtipos.

        La prioridad de estilos es:
            General < Nivel < Subtipo.
        """

        overrides = self._style_overrides["fault"]

        niveles_validos = ("N1", "N2", "N3", "N4", "N5")

        # ==================================================
        # 1. ESTILO GENERAL
        # ==================================================

        if nivel is None:

            overrides["general"].update(kwargs)

        # ==================================================
        # 2. VALIDAR NIVEL
        # ==================================================

        else:

            if nivel not in niveles_validos:
                raise ValueError(
                    f"Nivel no válido: {nivel}. "
                    f"Niveles permitidos: {niveles_validos}"
                )

            # ==============================================
            # 3. ESTILO POR NIVEL
            # ==============================================

            if caso is None:

                overrides["levels"][nivel].update(kwargs)

            # ==============================================
            # 4. ESTILO POR SUBTIPO
            # ==============================================

            else:

                if isinstance(caso, str):
                    casos = [caso]
                else:
                    casos = caso

                for subtipo in casos:

                    overrides["cases"][nivel].setdefault(
                        subtipo, {}
                    ).update(kwargs)

        # ==================================================
        # 5. ACTUALIZAR ARTISTAS
        # ==================================================

        self._refresh_fault_styles()

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

        artist = self.scatter(
            x,
            y,
            marker=marker,
            **kwargs
        )

        # Identificar automáticamente el tipo de artista
        if marker == "o":
            artist._gobkinematics_artist_type = "point"
        else:
            artist._gobkinematics_artist_type = "semicircle"

        return artist


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
            return_artists=False,
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

        x_artist = self.plot(
            x + x_verts[:, 0],
            y + x_verts[:, 1],
            color=color,
            alpha=alpha,
            linewidth=linewidth,
            zorder=zorder
        )
        x_artist[0]._gobkinematics_center = (x, y)
        if return_artists:
            artists = (circle, x_artist[0])

            for artist in artists:
                artist._gobkinematics_base_size = size

            x_artist[0]._gobkinematics_base_xdata = (
                x + x_verts[:, 0]
            ).copy()

            x_artist[0]._gobkinematics_base_ydata = (
                y + x_verts[:, 1]
            ).copy()

            return artists

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

            artist1 = self.scatter(
                x1, y1,
                marker=marker2,
                s=50,
                facecolors="none",
                edgecolors="black",
                zorder=5,
                **kwargs
            )
            artist1._gobkinematics_artist_type = "semicircle"

            artist2 = self.scatter(
                x2, y2,
                marker=marker1,
                s=50,
                facecolors="none",
                edgecolors="black",
                zorder=5,
                **kwargs
            )
            artist2._gobkinematics_artist_type = "semicircle"

        else:
            artist = self.scatter(
                [x1, x2],
                [y1, y2],
                s=50,
                facecolors="none",
                edgecolors="black",
                zorder=5,
                **kwargs
            )
            artist._gobkinematics_artist_type = "point"

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
                    strike_artist = self._draw_strike_point(
                        x_strike,
                        y_strike,
                        color="black",
                        alpha=0.6,
                        zorder=4
                    )

                    self._register_style_artist(
                        family="strike",
                        nivel=nivel,
                        subtipo=subtipo,
                        artists=strike_artist
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

                # Registrar las líneas existentes antes del conector
                lineas_antes = len(self.lines)

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

                # Recuperar el conector creado
                aux_artists = self.lines[lineas_antes:]

                # Registrar los elementos de AUX
                self._register_style_artist(
                    family="aux",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=aux_artists
                )

                # Punto cinemático
                fault_artist = self._draw_kinematic_point(
                    x_kin,
                    y_kin,
                    d,
                    vc,
                    color="red",
                    zorder=4
                )

                self._register_style_artist(
                    family="fault",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=fault_artist
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

                # Registrar los artistas existentes antes del dibujo
                lineas_antes = len(self.lines)

                # Representación del segmento N4
                self.plot_fault_N4_caso_3(
                    dip=d,
                    valor_cinematic=vc,
                    representation_mode=representation_mode,
                    color="purple",
                    alpha=0.7
                )

                # Recuperar los artistas creados
                fault_artists = self.lines[lineas_antes:]

                self._register_style_artist(
                    family="fault",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=fault_artists,
                    artist_type="segment"
                )

                # Registrar las líneas existentes antes del conector
                lineas_antes = len(self.lines)

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

                # Recuperar el conector creado
                aux_artists = self.lines[lineas_antes:]

                # Registrar los elementos de AUX
                self._register_style_artist(
                    family="aux",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=aux_artists
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

                # Registrar las colecciones existentes antes del dibujo # tercera modificacion
                colecciones_antes = len(self.collections)

                # Dibujar los dos puntos N3
                self.plot_fault_N3_caso_1(
                    dip=d,
                    rake=r,
                    conectar_linea=False
                )

                # Recuperar los artistas creados
                fault_artists = self.collections[colecciones_antes:]

                # Registrar los elementos de FAULT
                self._register_style_artist(
                    family="fault",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=fault_artists
                )

                # Registrar las líneas existentes antes de dibujar los conectores
                lineas_antes = len(self.lines)

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

                # Recuperar los dos conectores creados
                aux_artists = self.lines[lineas_antes:]

                # Registrar los elementos de AUX
                self._register_style_artist(
                    family="aux",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=aux_artists
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
                lineas_antes = len(self.lines)

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

                fault_artists = self.lines[lineas_antes:]

                self._register_style_artist(
                    family="fault",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=fault_artists,
                    artist_type="segment"
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
                lineas_antes = len(self.lines)

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

                # Recuperar todos los conectores creados
                aux_artists = self.lines[lineas_antes:]

                # Registrar los elementos de AUX
                self._register_style_artist(
                    family="aux",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=aux_artists
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

                lineas_antes = len(self.lines)

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

                # Recuperar los conectores creados
                aux_artists = self.lines[lineas_antes:]

                # Registrar los elementos de AUX
                # Registrar los elementos de AUX
                self._register_style_artist(
                    family="aux",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=aux_artists
                )

                # ----------------------------------------------
                # 3. Dibujar los dos puntos auxiliares
                # ----------------------------------------------

                fault_artists = self.plot(
                    [x1, x2],
                    [y1, y2],
                    marker="o",
                    markersize=5,
                    color="red",
                    linestyle="None",
                    alpha=0.9,
                    zorder=5
                )

                self._register_style_artist(
                    family="fault",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=fault_artists,
                    artist_type="point"
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

                lineas_antes = len(self.lines)

                centros_n2 = self.plot_fault_N2_caso_1(
                    dip=d,
                    longitud_guion=0.08,
                    representation_mode=representation_mode,
                    color="red",
                    linewidth=2,
                    alpha=0.8,
                    zorder=5
                )

                fault_artists = self.lines[lineas_antes:]

                self._register_style_artist(
                    family="fault",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=fault_artists,
                    artist_type="segment"
                )

                lineas_antes = len(self.lines)

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

                # Recuperar todos los conectores creados
                aux_artists = self.lines[lineas_antes:]

                # Registrar los elementos de AUX
                self._register_style_artist(
                    family="aux",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=aux_artists
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

                # Registrar las líneas existentes antes del conector
                lineas_antes = len(self.lines)

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

                # Recuperar el conector creado
                aux_artists = self.lines[lineas_antes:]

                # Registrar los elementos de AUX
                self._register_style_artist(
                    family="aux",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=aux_artists
                )
                # ----------------------------------------------
                # 3. Dibujar el punto auxiliar
                # ----------------------------------------------

                fault_artists = self.plot(
                    [x_auxiliar],
                    [y_auxiliar],
                    marker="o",
                    markersize=5,
                    color="red",
                    linestyle="None",
                    alpha=0.9,
                    zorder=5
                )

                self._register_style_artist(
                    family="fault",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=fault_artists,
                    artist_type="point"
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

                strike_artists = self._draw_strike_only_marker(
                    x_strike,
                    y_strike,
                    color="black",
                    alpha=0.6,
                    zorder=4,
                    return_artists=True
                )

                self._register_style_artist(
                    family="strike",
                    nivel=nivel,
                    subtipo=subtipo,
                    artists=strike_artists
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