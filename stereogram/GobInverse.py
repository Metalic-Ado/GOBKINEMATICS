import numpy as np

# ============================================================
# 1. UTILIDADES BÁSICAS
# ============================================================

def normalize(v):
    """Devuelve vector unitario"""
    return v / np.linalg.norm(v)


def angular_misfit(s_obs, s_theo):
    """
    Ángulo entre slip observado y slip teórico (en grados)
    """
    s_obs = normalize(s_obs)
    s_theo = normalize(s_theo)

    cosang = np.clip(np.dot(s_obs, s_theo), -1, 1)
    theta = np.arccos(cosang)

    return np.rad2deg(theta)


# ============================================================
# 2. SLIP OBSERVADO DESDE STRIKE/DIP/RAKE
# ============================================================

def slip_vector_from_strike_dip_rake(strike_deg, dip_deg, rake_deg):
    """
    Calcula el vector slip observado s_obs desde strike/dip/rake
    Sistema: x=East, y=North, z=Down
    """

    S = np.deg2rad(strike_deg)
    D = np.deg2rad(dip_deg)
    R = np.deg2rad(rake_deg)

    # Dirección strike (horizontal)
    u = np.array([
        np.sin(S),
        np.cos(S),
        0.0
    ])

    # Dirección dip (hacia abajo)
    v = np.array([
        np.cos(S) * np.cos(D),
       -np.sin(S) * np.cos(D),
        np.sin(D)
    ])

    # Slip dentro del plano
    s_obs = np.cos(R) * u + np.sin(R) * v

    return normalize(s_obs)


# ============================================================
# 3. NORMAL DEL PLANO DESDE STRIKE/DIP
# ============================================================

def fault_normal_from_strike_dip(strike_deg, dip_deg):
    """
    Normal unitaria del plano de falla
    """

    S = np.deg2rad(strike_deg)
    D = np.deg2rad(dip_deg)

    n = np.array([
        -np.sin(D) * np.sin(S),
         np.sin(D) * np.cos(S),
        -np.cos(D)
    ])

    return normalize(n)


# ============================================================
# 4. ROTACIÓN R SEGÚN ANGELIER
# ============================================================

def sigma1_from_trend_plunge(trend_deg, plunge_deg):
    """
    Construye sigma1 desde trend/plunge
    """

    T = np.deg2rad(trend_deg)
    P = np.deg2rad(plunge_deg)

    sigma1 = np.array([
        np.cos(P) * np.sin(T),
        np.cos(P) * np.cos(T),
        -np.sin(P)
    ])

    return normalize(sigma1)


def perpendicular_base_vector(sigma1):
    """
    Construye un vector perpendicular base e3_0
    """

    a = np.array([0, 0, 1])

    e3_0 = np.cross(a, sigma1)

    if np.linalg.norm(e3_0) < 1e-8:
        raise ValueError("sigma1 casi vertical")

    return normalize(e3_0)


def sigma3_from_sigma1_and_psi(sigma1, psi_deg):
    """
    Construye sigma3 rotando e3_0 alrededor de sigma1 con psi
    """

    psi = np.deg2rad(psi_deg)

    e3_0 = perpendicular_base_vector(sigma1)
    v = np.cross(sigma1, e3_0)

    sigma3 = np.cos(psi) * e3_0 + np.sin(psi) * v

    return normalize(sigma3)


def rotation_matrix_from_trend_plunge_psi(trend_deg, plunge_deg, psi_deg):
    """
    Matriz R = [sigma1 sigma2 sigma3]
    """

    sigma1 = sigma1_from_trend_plunge(trend_deg, plunge_deg)
    sigma3 = sigma3_from_sigma1_and_psi(sigma1, psi_deg)

    sigma2 = np.cross(sigma3, sigma1)
    sigma2 = normalize(sigma2)

    R = np.column_stack([sigma1, sigma2, sigma3])

    return R


# ============================================================
# 5. TENSOR REDUCIDO Y GLOBAL
# ============================================================

def reduced_tensor(phi):
    """
    Tensor reducido Angelier
    """
    return np.diag([1.0, phi, 0.0])


def stress_tensor_global(phi, R):
    """
    σ = R σ' Rᵀ
    """

    sigma_red = reduced_tensor(phi)

    sigma = R @ sigma_red @ R.T

    return sigma


# ============================================================
# 6. SHEAR TEÓRICO SOBRE UN PLANO
# ============================================================

def shear_unit_vector(sigma, n):
    """
    Dirección teórica del slip = dirección del shear stress
    """

    # Tracción total
    t = sigma @ n

    # Componente normal
    tn = np.dot(t, n) * n

    # Componente cortante
    tau = t - tn

    return normalize(tau)


# ============================================================
# 7. MISFIT PARA UNA FALLA
# ============================================================

def fault_misfit(strike, dip, rake, phi, trend, plunge, psi):

    # Rotación tensor
    R = rotation_matrix_from_trend_plunge_psi(trend, plunge, psi)

    # Tensor global
    sigma = stress_tensor_global(phi, R)

    # Normal del plano
    n = fault_normal_from_strike_dip(strike, dip)

    # Slip observado
    s_obs = slip_vector_from_strike_dip_rake(strike, dip, rake)

    # Slip teórico
    s_theo = shear_unit_vector(sigma, n)

    # Misfit angular
    theta = angular_misfit(s_obs, s_theo)

    return theta


# ============================================================
# 8. EJEMPLO CON 3 FALLAS
# ============================================================

faults = [
    # strike, dip, rake
    (120, 50, 90),
    (30, 60, -20),
    (270, 40, 120)
]


# ============================================================
# 9. GRID SEARCH SIMPLE (ANGELIER)
# ============================================================

best_F = 1e9
best_params = None

phis = np.linspace(0.1, 0.9, 10)
trends = np.arange(0, 360, 10)
plunges = np.arange(0, 90, 10)
psis = np.arange(0, 180, 10)

print("Buscando mejor tensor...\n")

for phi in phis:
    for trend in trends:
        for plunge in plunges:
            for psi in psis:

                misfits = []

                for strike, dip, rake in faults:
                    theta = fault_misfit(
                        strike, dip, rake,
                        phi, trend, plunge, psi
                    )
                    misfits.append(theta)

                F = np.mean(misfits)

                if F < best_F:
                    best_F = F
                    best_params = (phi, trend, plunge, psi)

print("======================================")
print("MEJOR SOLUCIÓN (GRID SEARCH)")
print("======================================")
print("Misfit promedio =", best_F, "grados")
print("phi     =", best_params[0])
print("trend   =", best_params[1])
print("plunge  =", best_params[2])
print("psi     =", best_params[3])

# ============================================================
# REFINAMIENTO CONTINUO (ANGELIER REAL)
# ============================================================

from scipy.optimize import minimize


# ------------------------------------------------------------
# 1. Función objetivo: suma de cuadrados de misfit
# ------------------------------------------------------------

def total_misfit(params, faults):
    """
    Función objetivo Angelier:

        F = Σ θ_i²

    params = [phi, trend, plunge, psi]
    faults = lista de fallas (strike, dip, rake)
    """

    phi, trend, plunge, psi = params

    # Penalizar valores imposibles
    if phi < 0 or phi > 1:
        return 1e9
    if plunge < 0 or plunge > 90:
        return 1e9

    misfits = []

    for strike, dip, rake in faults:
        theta = fault_misfit(
            strike, dip, rake,
            phi, trend, plunge, psi
        )
        misfits.append(theta)

    misfits = np.array(misfits)

    # Mínimos cuadrados
    return np.sum(misfits**2)


# ------------------------------------------------------------
# 2. Punto inicial: mejor solución del grid search
# ------------------------------------------------------------

phi0, trend0, plunge0, psi0 = best_params

x0 = [phi0, trend0, plunge0, psi0]

print("\n======================================")
print("REFINAMIENTO CONTINUO DESDE GRID SEARCH")
print("======================================")
print("Punto inicial (grid):", x0)


# ------------------------------------------------------------
# 3. Bounds físicos (Angelier)
# ------------------------------------------------------------

bounds = [
    (0.0, 1.0),     # phi
    (0.0, 360.0),   # trend
    (0.0, 90.0),    # plunge
    (0.0, 180.0)    # psi
]


# ------------------------------------------------------------
# 4. Minimización local (L-BFGS-B)
# ------------------------------------------------------------

result = minimize(
    total_misfit,
    x0,
    args=(faults,),
    bounds=bounds,
    method="L-BFGS-B"
)


# ------------------------------------------------------------
# 5. Resultado refinado
# ------------------------------------------------------------

phi_opt, trend_opt, plunge_opt, psi_opt = result.x
F_opt = result.fun

print("\n======================================")
print("SOLUCIÓN FINAL REFINADA (ANGELIER)")
print("======================================")
print("Misfit total (Σθ²) =", F_opt)

print("\nParámetros óptimos:")
print("phi     =", phi_opt)
print("trend   =", trend_opt)
print("plunge  =", plunge_opt)
print("psi     =", psi_opt)


# ------------------------------------------------------------
# 6. Mostrar σ1 σ2 σ3 finales
# ------------------------------------------------------------

R_opt = rotation_matrix_from_trend_plunge_psi(trend_opt, plunge_opt, psi_opt)

sigma1 = R_opt[:, 0]
sigma2 = R_opt[:, 1]
sigma3 = R_opt[:, 2]

print("\nEjes principales finales:")

print("\nσ1 =", sigma1)
print("σ2 =", sigma2)
print("σ3 =", sigma3)


# ------------------------------------------------------------
# 7. Misfit individual de cada falla
# ------------------------------------------------------------

print("\n======================================")
print("MISFIT POR FALLA")
print("======================================")

for i, (strike, dip, rake) in enumerate(faults):

    theta = fault_misfit(
        strike, dip, rake,
        phi_opt, trend_opt, plunge_opt, psi_opt
    )

    print(f"Falla {i+1}: strike={strike}, dip={dip}, rake={rake}")
    print("   θ =", theta, "grados")
