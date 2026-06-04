# =============================================================
#  PUNTO FIJO — EJEMPLOS + LANZAR INTERFAZ
#  Archivo: METODOS/Punto_Fijo.py
# =============================================================
import numpy as np
import matplotlib
matplotlib.use("TkAgg")          # mismo backend que la GUI
import matplotlib.pyplot as plt
from typing import Callable, List, Tuple
import os, sys

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
GRAFICAS_DIR = os.path.join(BASE_DIR, "Graficas")
os.makedirs(GRAFICAS_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════
#  NÚCLEO NUMÉRICO
# ══════════════════════════════════════════════════════════
def punto_fijo_sistema(
    G: Callable, x0: np.ndarray,
    tol: float = 1e-8, max_iter: int = 500, omega: float = 1.0
) -> Tuple[np.ndarray, List[float], int]:
    x = x0.copy().astype(float)
    errores = []
    for k in range(1, max_iter + 1):
        Gx = G(x)
        x_nuevo = (1 - omega) * x + omega * Gx
        error = np.linalg.norm(x_nuevo - x, ord=np.inf)
        errores.append(error)
        x = x_nuevo
        if error < tol:
            print(f"  Convergió en {k} iteraciones. Solución: {x}")
            return x, errores, k
    print(f"  No convergió en {max_iter} iteraciones. Última aprox.: {x}")
    return x, errores, max_iter

def norma_jacobiana(G: Callable, x: np.ndarray, h: float = 1e-5) -> float:
    n = len(x)
    J = np.zeros((n, n))
    for j in range(n):
        xp, xm = x.copy(), x.copy()
        xp[j] += h; xm[j] -= h
        J[:, j] = (G(xp) - G(xm)) / (2 * h)
    return np.linalg.norm(J, ord=np.inf)

# ══════════════════════════════════════════════════════════
#  EJEMPLO 1 — x² + y = 1,  x + y² = 1
# ══════════════════════════════════════════════════════════
def G_ejemplo1(x):
    x1, x2 = np.clip(x[0], 0, 1-1e-10), np.clip(x[1], 0, 1-1e-10)
    return np.array([np.sqrt(1 - x2), np.sqrt(1 - x1)])

print("=" * 55)
print("EJEMPLO 1: x² + y = 1,  x + y² = 1")
print("=" * 55)
x0_1 = np.array([0.5, 0.5])
nJ1 = norma_jacobiana(G_ejemplo1, x0_1)
print(f"  Norma Jacobiana en x0: {nJ1:.4f} ({'< 1 — Converge' if nJ1 < 1 else '>= 1'})")
sol1, err1, it1 = punto_fijo_sistema(G_ejemplo1, x0_1)
print(f"  Verif: f1={sol1[0]**2+sol1[1]-1:.2e}, f2={sol1[0]+sol1[1]**2-1:.2e}")

# ══════════════════════════════════════════════════════════
#  EJEMPLO 2 — Círculo x²+y²=4  ∩  Parábola y=x²-1
# ══════════════════════════════════════════════════════════
def G_ejemplo2(x):
    return np.array([np.sqrt(np.clip(4 - x[1]**2, 0, None)), x[0]**2 - 1])

print("\n" + "=" * 55)
print("EJEMPLO 2: x²+y²=4  ∩  y=x²-1")
print("=" * 55)
x0_2 = np.array([1.5, 0.5])
nJ2 = norma_jacobiana(G_ejemplo2, x0_2)
print(f"  Norma Jacobiana: {nJ2:.4f} — omega={'0.6' if nJ2>=1 else '1.0'}")
sol2, err2, it2 = punto_fijo_sistema(G_ejemplo2, x0_2, omega=0.6 if nJ2>=1 else 1.0)
print(f"  Verif: f1={sol2[0]**2+sol2[1]**2-4:.2e}, f2={sol2[1]-sol2[0]**2+1:.2e}")

# ══════════════════════════════════════════════════════════
#  EJEMPLO 3 — x·eʸ=2,  y·eˣ=3  (omega=0.5)
# ══════════════════════════════════════════════════════════
def G_ejemplo3(x):
    return np.array([2.0/np.exp(x[1]), 3.0/np.exp(x[0])])

print("\n" + "=" * 55)
print("EJEMPLO 3: x·eʸ=2,  y·eˣ=3  (omega=0.5)")
print("=" * 55)
x0_3 = np.array([0.5, 0.9])
nJ3 = norma_jacobiana(G_ejemplo3, x0_3)
print(f"  Norma Jacobiana: {nJ3:.4f} — omega=0.5")
sol3, err3, it3 = punto_fijo_sistema(G_ejemplo3, x0_3, omega=0.5, max_iter=500)
print(f"  Verif: f1={sol3[0]*np.exp(sol3[1])-2:.2e}, f2={sol3[1]*np.exp(sol3[0])-3:.2e}")

# ══════════════════════════════════════════════════════════
#  GRAFICA 1 — Convergencia de los 3 ejemplos
# ══════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("Método del Punto Fijo — Convergencia por Ejemplo",
             fontsize=14, fontweight='bold')
datos = [
    (err1, "Ejemplo 1\nx²+y=1, x+y²=1",   "royalblue"),
    (err2, "Ejemplo 2\nx²+y²=4, y=x²-1",  "darkorange"),
    (err3, "Ejemplo 3\nx·eʸ=2, y·eˣ=3",   "green"),
]
for ax, (errores, titulo, color) in zip(axes, datos):
    ax.semilogy(range(1, len(errores)+1), errores,
                color=color, linewidth=2, marker='o', markersize=3)
    ax.set_title(titulo, fontsize=11)
    ax.set_xlabel("Iteración"); ax.set_ylabel("Error (norma ∞)")
    ax.axhline(y=1e-6, color='red', linestyle='--', alpha=0.5, label='tol = 1e-6')
    ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
plt.tight_layout()
ruta1 = os.path.join(GRAFICAS_DIR, "Grafica1.png")
plt.savefig(ruta1, dpi=150, bbox_inches='tight')
print(f"\nGrafica1.png guardada → {ruta1}")
plt.show()

# ══════════════════════════════════════════════════════════
#  GRAFICA 2 — Geometría Ejemplo 1
# ══════════════════════════════════════════════════════════
fig2, ax2 = plt.subplots(figsize=(6, 6))
t = np.linspace(0, 1, 400)
ax2.plot(t, 1 - t**2, 'b-', linewidth=2, label='y = 1 − x²')
ax2.plot(1 - t**2, t, 'r-', linewidth=2, label='x = 1 − y²')
xi = np.array([0.5, 0.5]); traj = [xi.copy()]
for _ in range(15):
    xi = G_ejemplo1(xi); traj.append(xi.copy())
traj = np.array(traj)
ax2.plot(traj[:,0], traj[:,1], 'ko--', markersize=5, linewidth=1,
         alpha=0.6, label='Trayectoria')
ax2.plot(*sol1, 'g*', markersize=15,
         label=f'Solución ≈ ({sol1[0]:.4f}, {sol1[1]:.4f})')
ax2.set(xlim=(-0.1,1.2), ylim=(-0.1,1.2),
        xlabel="x", ylabel="y",
        title="Geometría y convergencia — Ejemplo 1")
ax2.legend(); ax2.grid(True, alpha=0.3); ax2.set_aspect('equal')
plt.tight_layout()
ruta2 = os.path.join(GRAFICAS_DIR, "Grafica2.png")
plt.savefig(ruta2, dpi=150, bbox_inches='tight')
print(f"Grafica2.png guardada → {ruta2}")
plt.show()

# ══════════════════════════════════════════════════════════
#  LANZAR INTERFAZ GRÁFICA (después de cerrar las gráficas)
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("  Abriendo interfaz gráfica interactiva...")
print("=" * 55)

# Importar y lanzar desde el mismo directorio
sys.path.insert(0, BASE_DIR)
from Interfaz_grafica import lanzar_interfaz
lanzar_interfaz()
