# Python checks of alternative answers for WebInstruct-verified MULTI candidates (PROTOCOL.md section 5, item 6).
# Each check prints what was verified; verdicts are transcribed into example_checks.json.
import math

import numpy as np
import sympy as sp


def check_21088():
    # CAPM: E(R) = rf + beta (rm - rf); t-bill vs 30-year treasury as the risk-free rate
    beta, rm = 0.8, 9.5
    for rf in (1.2, 3.5):
        print(f"  21088 rf={rf}: E(R) = {rf + beta * (rm - rf):.2f}%")


def check_53602():
    # Closest points on x y^3 z^2 = 16 (Lagrange): y^2 = 3x^2, z^2 = 2x^2, 2*3^{3/2} x^6 = 16
    x2 = (16 / (2 * 3 ** 1.5)) ** (1 / 3)
    x, y, z = math.sqrt(x2), math.sqrt(3 * x2), math.sqrt(2 * x2)
    pts = [(sx * x, sy * y, sz * z) for sx in (1, -1) for sy in (1, -1) for sz in (1, -1)]
    on = [p for p in pts if abs(p[0] * p[1] ** 3 * p[2] ** 2 - 16) < 1e-9]
    d = math.sqrt(x2 * 6)
    print(f"  53602 min distance {d:.6f} vs 2*3^(1/4) = {2 * 3 ** 0.25:.6f}; points on surface at that distance: {len(on)}")
    # numeric check that nothing closer exists: sample the surface x = 16/(y^3 z^2)
    rng = np.random.default_rng(0)
    ys, zs = rng.uniform(0.2, 4, 200000), rng.uniform(0.2, 4, 200000)
    xs = 16 / (ys ** 3 * zs ** 2)
    print(f"  53602 sampled minimum distance {np.sqrt(xs**2 + ys**2 + zs**2).min():.6f} (>= {d:.6f})")


def check_61735():
    v = sp.Matrix([3, 4, 2])
    ref = sp.Matrix([1, sp.Rational(4, 3), sp.Rational(2, 3)])
    print(f"  61735 [3,4,2]: ratios {[v[0] / 3, v[1] / 4, v[2] / 2]}; equals 3*ref: {v == 3 * ref}")


def check_109949():
    x, y, k = sp.symbols("x y k", real=True)
    for name, F in (("<k,0>", (k, 0)), ("<x,0>", (x, 0)), ("<y,0>", (y, 0))):
        mag = sp.sqrt(F[0] ** 2 + F[1] ** 2)
        const_on_vertical = sp.simplify(sp.diff(mag, y)) == 0
        print(f"  109949 {name}: parallel to x-axis {F[1] == 0}; magnitude constant along vertical lines (d/dy = 0): {const_on_vertical}")


def check_151963():
    # Simpson error bound |E| <= (b-a)^5 / (180 n^4) * max|f''''| on [0, pi/4], f = cos(x^2)
    t = sp.symbols("t")
    f4 = sp.lambdify(t, sp.diff(sp.cos(t ** 2), t, 4), "numpy")
    grid = np.linspace(0, math.pi / 4, 200001)
    M = np.abs(f4(grid)).max()
    b = math.pi / 4
    for n in (2, 4, 6, 8):
        bound = b ** 5 / (180 * n ** 4) * M
        print(f"  151963 n={n}: max|f''''|={M:.4f}, error bound {bound:.6f} <= 0.0002: {bound <= 0.0002}")


def check_32718():
    from scipy.special import lambertw
    beta = np.linspace(-1 / math.e + 1e-9, -1e-9, 200001)
    W = lambertw(beta, 0).real
    p = np.sqrt(2 * (1 + math.e * beta))
    cands = {"reference (2p-3)/(p+3)": (2 * p - 3) / (p + 3), "Pass A -1+p-p^2/3": -1 + p - p ** 2 / 3, "Pass B -1": -np.ones_like(beta)}
    for name, fv in cands.items():
        print(f"  32718 {name}: f <= W0 on (-1/e,0): {bool(np.all(fv <= W + 1e-12))}; max(f - W0) = {np.max(fv - W):.2e}; "
              f"f > -1 everywhere except at -1/e: {bool(np.all(fv[1:] > -1))}")


if __name__ == "__main__":
    for fn in (check_21088, check_53602, check_61735, check_109949, check_151963, check_32718):
        print(fn.__name__)
        fn()
