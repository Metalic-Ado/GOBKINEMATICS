from matplotlib.path import Path
from matplotlib.patches import FancyArrowPatch
import numpy as np

def double_dashed_arrow(
    x1, y1, x2, y2,
    arrow_scale=15,
    color="black",
    alpha=0.7,
    zorder=10
):
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

    return arr1, arr2

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

def _apply_offset_if_overlap(x0, y0, x1, y1, offset_mag=0.02):
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

def strike_only_marker():
    """
    Retorna un marcador compuesto:
    X dentro de un círculo.

    Identifica estructuras que solamente
    contienen información de strike (N1).
    """

    circle = Path.unit_circle()

    x_verts = np.array([
        [-0.65, -0.65],
        [0.65, 0.65],
        [np.nan, np.nan],
        [-0.65, 0.65],
        [0.65, -0.65]
    ])

    return circle, x_verts
