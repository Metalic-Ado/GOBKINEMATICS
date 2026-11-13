import numpy as np
# Metodo para inverse metodos
# primero angelier

# Convertir las fallas en vectores un vector normal del plano y un vector de deslizamiento del rake (ajustar ejes OJO)
# Crear una matriz reducidora
# Hallar el vector de cizalla de cada plano propuesto

def reduced_tensor(phi):
    return np.diag([1.0, phi, 0.0])

# contruir el vector rotacion utilizando los vectores de sigma 1 sima2 y sigma 3
# sigame 1 ligado al trend y plunge

def deg2rad(angle_deg):
    return np.deg2rad(angle_deg)

def normalize(v):
    return v / np.linalg.norm(v)

def sigma1_from_trend_plunge(trend_deg, plunge_deg):

    T = deg2rad(trend_deg)
    P = deg2rad(plunge_deg)

    sigma1 = np.array([
        np.cos(P) * np.sin(T),   # componente Este
        np.cos(P) * np.cos(T),   # componente Norte
        -np.sin(P)               # componente Vertical (hacia abajo)
    ])

    return normalize(sigma1)

# construccion del vector perpendicular a sigma 1 osea sigma 3
def perpendicular_base_vector(sigma1):

    a = np.array([0, 0, 1])  # vector vertical

    # Producto cruz para obtener perpendicular
    e3_0 = np.cross(a, sigma1)

    # Si sigma1 es vertical, este cross da cero
    if np.linalg.norm(e3_0) < 1e-8:
        raise ValueError("sigma1 es casi vertical, elegir otro vector auxiliar")

    return normalize(e3_0)
# rotar el sigma 3 median te un angulo psi_deg
def sigma3_from_sigma1_and_psi(sigma1, psi_deg):

    psi = deg2rad(psi_deg)

    # vector base perpendicular
    e3_0 = perpendicular_base_vector(sigma1)

    # segundo vector perpendicular dentro del plano
    v = np.cross(sigma1, e3_0)

    sigma3 = (
        np.cos(psi) * e3_0 +
        np.sin(psi) * v
    )

    return normalize(sigma3)

# obtener sigma 2

def sigma2_from_sigma1_sigma3(sigma1, sigma3):

    sigma2 = np.cross(sigma3, sigma1)

    return normalize(sigma2)

# ensamblar la matriz rotacion
def rotation_matrix_from_trend_plunge_psi(trend_deg, plunge_deg, psi_deg):
    """
    Construye la matriz R según Angelier:

    - sigma1 definido por trend/plunge
    - sigma3 rotado con psi alrededor de sigma1
    - sigma2 automático
    """

    # 1. sigma1
    sigma1 = sigma1_from_trend_plunge(trend_deg, plunge_deg)

    # 2. sigma3
    sigma3 = sigma3_from_sigma1_and_psi(sigma1, psi_deg)

    # 3. sigma2
    sigma2 = sigma2_from_sigma1_sigma3(sigma1, sigma3)

    # 4. Matriz R con columnas principales
    R = np.column_stack([sigma1, sigma2, sigma3])

    return R

# TENSOR GLOBAL
def stress_tensor_global(phi, R):
    """
    Construye el tensor de stress global:

        σ = R σ' Rᵀ

    phi = stress ratio
    R   = matriz de rotación (σ1 σ2 σ3)
    """
    sigma_red = reduced_tensor(phi)

    sigma = R @ sigma_red @ R.T

    return sigma

############################################################################# PLANO A VECTOR

def fault_normal_from_strike_dip(strike_deg, dip_deg):

    strike = np.deg2rad(strike_deg)
    dip    = np.deg2rad(dip_deg)

    n = np.array([
        -np.sin(dip) * np.sin(strike),   # East
         np.sin(dip) * np.cos(strike),   # North
        -np.cos(dip)                     # Down
    ])

    return n / np.linalg.norm(n)

import numpy as np


def slip_vector_from_strike_dip_rake(strike_deg, dip_deg, rake_deg):
    """
    Calcula el vector de deslizamiento observado s_obs
    desde strike, dip y rake.

    Coordenadas:
        x = East
        y = North
        z = Down

    Parámetros:
        strike_deg : strike (0–360)
        dip_deg    : dip (0–90)
        rake_deg   : rake (-180–180)

    Retorna:
        s_obs unitario (3,)
    """

    # Convertir a radianes
    S = np.deg2rad(strike_deg)
    D = np.deg2rad(dip_deg)
    R = np.deg2rad(rake_deg)

    # -----------------------------
    # Vector strike (horizontal)
    # -----------------------------
    u = np.array([
        np.sin(S),   # East
        np.cos(S),   # North
        0.0          # Down
    ])

    # -----------------------------
    # Vector dip (hacia abajo)
    # -----------------------------
    v = np.array([
        np.cos(S) * np.cos(D),    # East
       -np.sin(S) * np.cos(D),    # North
        np.sin(D)                 # Down
    ])

    # -----------------------------
    # Slip vector dentro del plano
    # -----------------------------
    s_obs = np.cos(R) * u + np.sin(R) * v

    # Normalizar
    s_obs = s_obs / np.linalg.norm(s_obs)

    return s_obs




def traction_vector(sigma, n):
    """
    t = σ n
    """
    return sigma @ n

def shear_vector(t, n):
    """
    τ = t - (t·n)n
    """
    normal_component = np.dot(t, n) * n
    tau = t - normal_component

    return tau

def shear_unit_vector(sigma, n):

    t = traction_vector(sigma, n)
    tau = shear_vector(t, n)

    return tau / np.linalg.norm(tau)



def angular_misfit(s_obs, s_theo):

    s_obs  = s_obs / np.linalg.norm(s_obs)
    s_theo = s_theo / np.linalg.norm(s_theo)

    cosang = np.clip(np.dot(s_obs, s_theo), -1, 1)

    theta = np.arccos(cosang)

    return np.rad2deg(theta)

def fault_misfit(strike, dip, rake, phi, R):

    # Tensor global
    sigma = stress_tensor_global(phi, R)

    # Normal del plano
    n = fault_normal_from_strike_dip(strike, dip)

    # Slip observado desde rake
    s_obs = slip_vector_from_strike_dip_rake(strike, dip, rake)

    # Slip teórico desde shear stress
    s_theo = shear_unit_vector(sigma, n)

    # Misfit angular
    theta = angular_misfit(s_obs, s_theo)

    return theta


