# ==================================================
# GOBKINEMATICS
# API PUBLICA
# ==================================================

from .kinematics.kinematics_axes import KinematicAxes

from .kinematics.kinematics_math import (
    changes_magnitud_rake,
    dip_rake_to_xy,
    strike_to_xy
)

from .kinematics.kinematics_visual import half_circle_marker


__version__ = "0.9-dev"


__all__ = [
    "KinematicAxes",
    "changes_magnitud_rake",
    "dip_rake_to_xy",
    "strike_to_xy",
    "half_circle_marker",
]