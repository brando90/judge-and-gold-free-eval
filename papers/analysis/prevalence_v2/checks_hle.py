# Python checks of alternative answers for HLE MULTI candidates that are math-like (PROTOCOL.md section 5, item 6).
import math

from scipy.integrate import quad
from scipy.optimize import brentq


def check_66fdb51b():
    # f(x) = a e^{2x} + b e^x + c with lim_{x->-inf} (f+3)/e^x = 1 -> c = -3, b = 1; f(ln 2) = 0 -> a = 1/4.
    f = lambda x: 0.25 * math.exp(2 * x) + math.exp(x) - 3
    assert abs(f(math.log(2))) < 1e-12
    g = lambda y: brentq(lambda x: f(x) - y, -50, 50)  # inverse of the increasing f
    # Question: find A, B with int_0^A g + int_{ln 2}^{ln B} f = A ln B, then report A + B.
    # Young's inequality: equality holds exactly when A = f(ln B), so every B > 2^(?) with A = f(ln B) >= 0 works.
    for B in (3.0, 4.0, 5.0):
        A = f(math.log(B))
        lhs = quad(g, 0, A)[0] + quad(f, math.log(2), math.log(B))[0]
        print(f"  66fdb51b B={B}: A=f(ln B)={A:.4f}; LHS={lhs:.6f}; A ln B={A * math.log(B):.6f}; A+B={A + B:.4f}")
    # a non-solution for contrast (A off the curve)
    B, A = 4.0, 4.0
    lhs = quad(g, 0, A)[0] + quad(f, math.log(2), math.log(B))[0]
    print(f"  66fdb51b off-curve B=4, A=4: LHS={lhs:.6f} vs A ln B={A * math.log(B):.6f} (not equal)")


def check_6712787d():
    # Herd-immunity coverage Vc = (1 - 1/R0) / VE, R0 = 3, 35% of the population vaccinated, "6% of vaccinated ... got the infection"
    R0, ppv = 3.0, 0.35
    pcv = 0.06  # reading 1 (reference): 6% of cases were vaccinated -> screening-method VE
    ve1 = 1 - (pcv / (1 - pcv)) * ((1 - ppv) / ppv)
    ve2 = 1 - 0.06  # reading 2 (literal): 6% of vaccinated people were infected -> VE = 94% (breakthrough rate)
    for name, ve in (("screening method", ve1), ("breakthrough rate", ve2)):
        print(f"  6712787d {name}: VE={ve:.4f}; coverage threshold={(1 - 1 / R0) / ve * 100:.1f}%")


def check_672db430():
    # The 17 wallpaper groups and the order of their point groups
    point_group_order = {"p1": 1, "p2": 2, "pm": 2, "pg": 2, "cm": 2, "pmm": 4, "pmg": 4, "pgg": 4, "cmm": 4, "p4": 4,
                         "p4m": 8, "p4g": 8, "p3": 3, "p3m1": 6, "p31m": 6, "p6": 6, "p6m": 12}
    assert len(point_group_order) == 17
    two = [g for g, o in point_group_order.items() if o == 2]
    print(f"  672db430 wallpaper groups with point group of order 2: {two} -> {len(two)}; "
          f"C2 only (rotation): 1 (p2); D1 only (reflection): 3 (pm, pg, cm)")


if __name__ == "__main__":
    for fn in (check_66fdb51b, check_6712787d, check_672db430):
        print(fn.__name__)
        fn()
