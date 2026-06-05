# =============================================================
#  INTERFAZ GRÁFICA — MÉTODO DEL PUNTO FIJO (LEGACY v1.x)
#  Métodos Numéricos — Universidad Distrital 2026-1
#  Archivo: METODOS/Interfaz_grafica.py
# =============================================================
"""
Legacy GUI Module for Fixed-Point Method (v1.x).

DEPRECATED: Use main_app.py for the new unified interface (v2.0+).

This module provides a tabbed GUI interface with automatic graph 
generation. It is maintained for backwards compatibility but should 
not be used for new features.

Architecture:
    - 3-tab Tkinter interface (Entrada, Pasos, Resultado)
    - Automatic graph generation during execution
    - Linear workflow from input to visualization
    
Migration Path:
    Old: python Punto_Fijo_v2.py → Punto_Fijo.py → Interfaz_grafica.py
    New: python Punto_Fijo_v2.py → main_app.py (unified interface)

Dependencies:
    - tkinter: GUI framework
    - numpy: Numerical computations
    - matplotlib: Visualization

Author: Andrés Cerdas Padilla
Institution: Universidad Distrital Francisco José de Caldas
Year: 2026
Status: Legacy (maintained for compatibility)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os, sys, math, cmath

# ── colores y fuentes ──────────────────────────────────────
BG        = "#1e1e2e"
SURFACE   = "#2a2a3e"
SURFACE2  = "#313149"
ACCENT    = "#7c9eff"
ACCENT2   = "#a6e3a1"
TEXT      = "#cdd6f4"
TEXT_MUTED= "#a6adc8"
RED_ERR   = "#f38ba8"
YELLOW    = "#f9e2af"
FONT_BODY = ("Consolas", 11)
FONT_HEAD = ("Segoe UI", 13, "bold")
FONT_MONO = ("Consolas", 10)

# ── núcleo numérico (copiado de Punto_Fijo.py) ────────────
def punto_fijo_sistema(G, x0, tol=1e-8, max_iter=500, omega=1.0):
    x = x0.copy().astype(float)
    historial, errores = [x.copy()], []
    for k in range(1, max_iter + 1):
        Gx = G(x)
        x_nuevo = (1 - omega) * x + omega * Gx
        error = np.linalg.norm(x_nuevo - x, ord=np.inf)
        errores.append(error)
        x = x_nuevo
        historial.append(x.copy())
        if error < tol:
            return x, errores, historial, k, True
    return x, errores, historial, max_iter, False

def norma_jacobiana(G, x, h=1e-5):
    n = len(x)
    J = np.zeros((n, n))
    for j in range(n):
        xp, xm = x.copy(), x.copy()
        xp[j] += h; xm[j] -= h
        J[:, j] = (G(xp) - G(xm)) / (2 * h)
    return np.linalg.norm(J, ord=np.inf), J

# ── utilidad: parsear expresión del usuario ───────────────
SAFE_NS = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
SAFE_NS.update({"np": np, "sqrt": math.sqrt, "exp": math.exp,
                "log": math.log, "sin": math.sin, "cos": math.cos,
                "tan": math.tan, "abs": abs, "pi": math.pi, "e": math.e})

def build_G(expr_g1, expr_g2):
    """Construye G(x) = [g1(x,y), g2(x,y)] desde strings."""
    def G(x_arr):
        x, y = float(x_arr[0]), float(x_arr[1])
        ns = dict(SAFE_NS); ns.update({"x": x, "y": y})
        r1 = eval(expr_g1, {"__builtins__": {}}, ns)
        r2 = eval(expr_g2, {"__builtins__": {}}, ns)
        return np.array([float(r1), float(r2)])
    return G

# ═══════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ═══════════════════════════════════════════════════════════
class AppPuntoFijo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Método del Punto Fijo — Universidad Distrital 2026-1")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.geometry("1100x720")
        self._build_header()
        self._build_notebook()
        self._build_statusbar()

    # ── cabecera ──────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg="#11111b", pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚙  Método del Punto Fijo para Sistemas No Lineales",
                 bg="#11111b", fg=ACCENT, font=("Segoe UI", 15, "bold")).pack(side="left", padx=20)
        tk.Label(hdr, text="Métodos Numéricos · UD 2026-1",
                 bg="#11111b", fg=TEXT_MUTED, font=("Segoe UI", 10)).pack(side="right", padx=20)

    # ── notebook con pestañas ────────────────────────────
    def _build_notebook(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",        background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",    background=SURFACE, foreground=TEXT_MUTED,
                        font=("Segoe UI", 11), padding=[16, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", SURFACE2)],
                  foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=(6, 0))

        self.tab_entrada   = tk.Frame(nb, bg=BG)
        self.tab_pasos     = tk.Frame(nb, bg=BG)
        self.tab_resultado = tk.Frame(nb, bg=BG)

        nb.add(self.tab_entrada,   text="  📥  Entrada  ")
        nb.add(self.tab_pasos,     text="  📋  Pasos  ")
        nb.add(self.tab_resultado, text="  📈  Resultado  ")
        self.nb = nb

        self._build_tab_entrada()
        self._build_tab_pasos()
        self._build_tab_resultado()

    # ── TAB 1 — Entrada ───────────────────────────────────
    def _build_tab_entrada(self):
        p = self.tab_entrada
        pad = dict(padx=16, pady=6)

        # ─ instrucciones ─
        info = tk.Frame(p, bg=SURFACE, bd=0, relief="flat")
        info.pack(fill="x", **pad)
        tk.Label(info, text="ℹ  Ingresa la función de iteración  x = G(x, y)  e  y = G(x, y)\n"
                            "   Operadores disponibles: +  -  *  /  **  sqrt()  exp()  log()  sin()  cos()  tan()  abs()  pi  e",
                 bg=SURFACE, fg=TEXT_MUTED, font=("Segoe UI", 10), justify="left",
                 wraplength=900).pack(padx=12, pady=8, anchor="w")

        # ─ campos de entrada ─
        frame_campos = tk.Frame(p, bg=BG)
        frame_campos.pack(fill="x", padx=16, pady=4)

        def campo(parent, label, row, placeholder, var_name):
            tk.Label(parent, text=label, bg=BG, fg=TEXT, font=FONT_HEAD,
                     width=12, anchor="e").grid(row=row, column=0, padx=(0,10), pady=6, sticky="e")
            sv = tk.StringVar(value=placeholder)
            e = tk.Entry(parent, textvariable=sv, bg=SURFACE2, fg=ACCENT,
                         font=("Consolas", 12), insertbackground=ACCENT,
                         relief="flat", bd=6, width=55)
            e.grid(row=row, column=1, padx=4, pady=6, sticky="w")
            setattr(self, var_name, sv)
            return e

        campo(frame_campos, "G₁(x, y) =", 0, "sqrt(1 - y)", "sv_g1")
        campo(frame_campos, "G₂(x, y) =", 1, "sqrt(1 - x)", "sv_g2")
        campo(frame_campos, "x₀ =",       2, "0.5",         "sv_x0")
        campo(frame_campos, "y₀ =",       3, "0.5",         "sv_y0")

        # ─ parámetros ─
        frame_params = tk.Frame(p, bg=BG)
        frame_params.pack(fill="x", padx=16, pady=4)

        def param(parent, label, col, default, var_name):
            tk.Label(parent, text=label, bg=BG, fg=TEXT_MUTED,
                     font=("Segoe UI", 10)).grid(row=0, column=col*2, padx=(20,4), sticky="e")
            sv = tk.StringVar(value=default)
            e = tk.Entry(parent, textvariable=sv, bg=SURFACE2, fg=YELLOW,
                         font=FONT_MONO, relief="flat", bd=4, width=12)
            e.grid(row=0, column=col*2+1, padx=(0,10))
            setattr(self, var_name, sv)

        param(frame_params, "Tolerancia:", 0, "1e-8",  "sv_tol")
        param(frame_params, "Máx. iter:",  1, "500",   "sv_maxiter")
        param(frame_params, "Omega (ω):",  2, "1.0",   "sv_omega")

        # ─ botón ─
        btn = tk.Button(p, text="  ▶  EJECUTAR MÉTODO  ",
                        bg=ACCENT, fg="#1e1e2e", font=("Segoe UI", 12, "bold"),
                        relief="flat", bd=0, padx=20, pady=10,
                        activebackground="#5a7fee", cursor="hand2",
                        command=self.ejecutar)
        btn.pack(pady=20)

        # ─ ejemplo rápido ─
        tk.Label(p, text="Ejemplos rápidos:", bg=BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20)
        ejemplos_frame = tk.Frame(p, bg=BG)
        ejemplos_frame.pack(fill="x", padx=20)
        ejemplos = [
            ("Ej 1: Cuadrático",    "sqrt(1 - y)",       "sqrt(1 - x)",       "0.5", "0.5"),
            ("Ej 2: Círculo/Parábola","sqrt(4 - y**2)",  "x**2 - 1",          "1.5", "0.5"),
            ("Ej 3: Exponencial",   "2 / exp(y)",        "3 / exp(x)",        "0.5", "0.9"),
        ]
        for i, (name, g1, g2, x0, y0) in enumerate(ejemplos):
            def cargar(g1=g1, g2=g2, x0=x0, y0=y0):
                self.sv_g1.set(g1); self.sv_g2.set(g2)
                self.sv_x0.set(x0); self.sv_y0.set(y0)
            tk.Button(ejemplos_frame, text=name, bg=SURFACE, fg=TEXT,
                      font=("Segoe UI", 9), relief="flat", bd=0, padx=10, pady=5,
                      cursor="hand2", command=cargar).grid(row=0, column=i, padx=6, pady=4)

    # ── TAB 2 — Pasos ─────────────────────────────────────
    def _build_tab_pasos(self):
        p = self.tab_pasos
        self.txt_pasos = scrolledtext.ScrolledText(
            p, bg="#11111b", fg=TEXT, font=FONT_MONO,
            insertbackground=TEXT, relief="flat", bd=0,
            wrap="none", state="disabled")
        self.txt_pasos.pack(fill="both", expand=True, padx=10, pady=10)
        # tags de color
        self.txt_pasos.tag_config("titulo",    foreground=ACCENT,   font=("Consolas", 11, "bold"))
        self.txt_pasos.tag_config("ok",        foreground=ACCENT2)
        self.txt_pasos.tag_config("warn",      foreground=YELLOW)
        self.txt_pasos.tag_config("error",     foreground=RED_ERR)
        self.txt_pasos.tag_config("iter_head", foreground=TEXT_MUTED, font=("Consolas", 9))
        self.txt_pasos.tag_config("iter_row",  foreground=TEXT,       font=("Consolas", 10))

    def _pasos_write(self, text, tag=""):
        self.txt_pasos.config(state="normal")
        self.txt_pasos.insert("end", text, tag)
        self.txt_pasos.config(state="disabled")
        self.txt_pasos.see("end")

    def _pasos_clear(self):
        self.txt_pasos.config(state="normal")
        self.txt_pasos.delete("1.0", "end")
        self.txt_pasos.config(state="disabled")

    # ── TAB 3 — Resultado ─────────────────────────────────
    def _build_tab_resultado(self):
        p = self.tab_resultado
        p.columnconfigure(0, weight=1)
        p.columnconfigure(1, weight=1)
        p.rowconfigure(0, weight=1)

        # panel izquierdo: métricas
        left = tk.Frame(p, bg=SURFACE, bd=0)
        left.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=10)
        tk.Label(left, text="Resumen", bg=SURFACE, fg=ACCENT,
                 font=FONT_HEAD).pack(anchor="w", padx=14, pady=(12,4))
        self.lbl_resumen = tk.Label(left, text="—", bg=SURFACE, fg=TEXT,
                                     font=("Consolas", 11), justify="left",
                                     anchor="nw", wraplength=420)
        self.lbl_resumen.pack(anchor="nw", padx=14, pady=6, fill="x")

        # panel derecho: gráfica embebida
        right = tk.Frame(p, bg=BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(5,10), pady=10)
        self.fig_frame = right
        self.canvas_widget = None

    def _mostrar_grafica(self, errores, historial, sol, convergio, iters):
        # limpiar canvas anterior
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()

        fig, axes = plt.subplots(1, 2, figsize=(8, 3.8),
                                 facecolor="#11111b")
        fig.subplots_adjust(wspace=0.35)

        color_conv = "#a6e3a1" if convergio else "#f38ba8"

        # subplot 1: convergencia
        ax1 = axes[0]
        ax1.set_facecolor("#1e1e2e")
        ax1.semilogy(range(1, len(errores)+1), errores,
                     color=ACCENT, linewidth=1.8, marker='o', markersize=2)
        ax1.set_title("Convergencia del Error", color=TEXT, fontsize=9)
        ax1.set_xlabel("Iteración", color=TEXT_MUTED, fontsize=8)
        ax1.set_ylabel("Error (norma ∞)", color=TEXT_MUTED, fontsize=8)
        ax1.tick_params(colors=TEXT_MUTED, labelsize=7)
        for spine in ax1.spines.values():
            spine.set_edgecolor("#313149")
        ax1.grid(True, alpha=0.2, color=TEXT_MUTED)
        ax1.axhline(y=float(self.sv_tol.get()), color=RED_ERR,
                    linestyle='--', alpha=0.6, linewidth=1, label=f"tol")
        ax1.legend(fontsize=7, facecolor=SURFACE, labelcolor=TEXT)

        # subplot 2: trayectoria (x1 vs x2)
        ax2 = axes[1]
        ax2.set_facecolor("#1e1e2e")
        hist = np.array(historial)
        ax2.plot(hist[:, 0], hist[:, 1], 'o--',
                 color=ACCENT, linewidth=1.2, markersize=3, alpha=0.7,
                 label="Trayectoria")
        ax2.plot(sol[0], sol[1], '*', color=color_conv,
                 markersize=14, label=f"Solución\n({sol[0]:.5f}, {sol[1]:.5f})")
        ax2.set_title("Trayectoria Iterativa", color=TEXT, fontsize=9)
        ax2.set_xlabel("x", color=TEXT_MUTED, fontsize=8)
        ax2.set_ylabel("y", color=TEXT_MUTED, fontsize=8)
        ax2.tick_params(colors=TEXT_MUTED, labelsize=7)
        for spine in ax2.spines.values():
            spine.set_edgecolor("#313149")
        ax2.grid(True, alpha=0.2, color=TEXT_MUTED)
        ax2.legend(fontsize=7, facecolor=SURFACE, labelcolor=TEXT)

        canvas = FigureCanvasTkAgg(fig, master=self.fig_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas_widget = canvas

        # guardar PNG en carpeta Graficas/
        base = os.path.dirname(os.path.abspath(__file__))
        graficas_dir = os.path.join(base, "Graficas")
        os.makedirs(graficas_dir, exist_ok=True)
        ruta = os.path.join(graficas_dir, "Grafica_usuario.png")
        fig.savefig(ruta, dpi=150, bbox_inches='tight',
                    facecolor=fig.get_facecolor())
        self.set_status(f"Gráfica guardada → {ruta}", "ok")

    # ── lógica principal ──────────────────────────────────
    def ejecutar(self):
        self._pasos_clear()
        self.nb.select(1)   # ir a pestaña Pasos

        expr_g1  = self.sv_g1.get().strip()
        expr_g2  = self.sv_g2.get().strip()

        try:
            x0_val = float(self.sv_x0.get())
            y0_val = float(self.sv_y0.get())
            tol    = float(self.sv_tol.get())
            maxiter= int(self.sv_maxiter.get())
            omega  = float(self.sv_omega.get())
        except ValueError as e:
            messagebox.showerror("Error de parámetros", str(e))
            return

        # ─ paso 1: mostrar sistema ─
        self._pasos_write("═"*60 + "\n", "titulo")
        self._pasos_write(" PASO 1 — Sistema ingresado\n", "titulo")
        self._pasos_write("═"*60 + "\n", "titulo")
        self._pasos_write(f"  G₁(x, y) = {expr_g1}\n", "ok")
        self._pasos_write(f"  G₂(x, y) = {expr_g2}\n", "ok")
        self._pasos_write(f"  x⁽⁰⁾ = ({x0_val}, {y0_val})\n")
        self._pasos_write(f"  Tolerancia = {tol},  Máx iter = {maxiter},  ω = {omega}\n\n")

        # ─ construir G ─
        try:
            G = build_G(expr_g1, expr_g2)
            x0 = np.array([x0_val, y0_val])
            _ = G(x0)  # test
        except Exception as e:
            self._pasos_write(f"\n  ✗ Error al evaluar G: {e}\n", "error")
            messagebox.showerror("Error en la función", str(e))
            return

        # ─ paso 2: norma jacobiana ─
        self._pasos_write("═"*60 + "\n", "titulo")
        self._pasos_write(" PASO 2 — Verificación de convergencia (Jacobiana)\n", "titulo")
        self._pasos_write("═"*60 + "\n", "titulo")
        try:
            norm_J, J = norma_jacobiana(G, x0)
            self._pasos_write(f"  Jacobiana de G en x⁽⁰⁾ (diferencias finitas):\n", "warn")
            self._pasos_write(f"    J[0,0]={J[0,0]:+.6f}  J[0,1]={J[0,1]:+.6f}\n")
            self._pasos_write(f"    J[1,0]={J[1,0]:+.6f}  J[1,1]={J[1,1]:+.6f}\n\n")
            self._pasos_write(f"  ‖J_G‖∞ = {norm_J:.6f}\n")
            if norm_J < 1:
                self._pasos_write(f"  → Criterio CUMPLIDO (‖J‖∞ < 1) — convergencia garantizada ✓\n\n", "ok")
            else:
                self._pasos_write(f"  → Criterio NO cumplido (‖J‖∞ ≥ 1) — se intentará con ω={omega}\n\n", "warn")
        except Exception as e:
            self._pasos_write(f"  (No se pudo calcular la Jacobiana: {e})\n\n", "warn")

        # ─ paso 3: iteraciones ─
        self._pasos_write("═"*60 + "\n", "titulo")
        self._pasos_write(" PASO 3 — Iteraciones\n", "titulo")
        self._pasos_write("═"*60 + "\n", "titulo")
        self._pasos_write(f"  {'k':>5}  {'x':>14}  {'y':>14}  {'Error':>14}\n", "iter_head")
        self._pasos_write("  " + "-"*54 + "\n", "iter_head")

        # ejecutar método
        try:
            sol, errores, historial, iters, convergio = punto_fijo_sistema(
                G, x0, tol=tol, max_iter=maxiter, omega=omega)
        except Exception as e:
            self._pasos_write(f"\n  ✗ Error durante la iteración: {e}\n", "error")
            return

        MAX_MOSTRAR = 50
        for i, (h, err) in enumerate(zip(historial[1:], errores)):
            if i < MAX_MOSTRAR:
                self._pasos_write(
                    f"  {i+1:>5}  {h[0]:>14.8f}  {h[1]:>14.8f}  {err:>14.2e}\n",
                    "iter_row")
        if iters > MAX_MOSTRAR:
            self._pasos_write(f"\n  ... ({iters - MAX_MOSTRAR} iteraciones omitidas) ...\n\n", "iter_head")
            h_last = historial[-1]
            self._pasos_write(
                f"  {iters:>5}  {h_last[0]:>14.8f}  {h_last[1]:>14.8f}  {errores[-1]:>14.2e}\n",
                "iter_row")

        # ─ paso 4: resultado ─
        self._pasos_write("\n" + "═"*60 + "\n", "titulo")
        self._pasos_write(" PASO 4 — Resultado final\n", "titulo")
        self._pasos_write("═"*60 + "\n", "titulo")
        if convergio:
            self._pasos_write(f"  ✓ CONVERGIÓ en {iters} iteraciones\n", "ok")
        else:
            self._pasos_write(f"  ✗ NO convergió en {iters} iteraciones (última aprox.)\n", "error")
        self._pasos_write(f"  x* ≈ {sol[0]:.10f}\n", "ok")
        self._pasos_write(f"  y* ≈ {sol[1]:.10f}\n", "ok")
        try:
            Gsol = G(sol)
            res_x = abs(Gsol[0] - sol[0])
            res_y = abs(Gsol[1] - sol[1])
            self._pasos_write(f"\n  Verificación  |G₁(x*,y*) - x*| = {res_x:.2e}\n")
            self._pasos_write(f"                |G₂(x*,y*) - y*| = {res_y:.2e}\n")
        except:
            pass

        # ─ actualizar pestaña Resultado ─
        estado = "CONVERGIÓ" if convergio else "No convergió"
        color_estado = ACCENT2 if convergio else RED_ERR
        resumen = (
            f"Estado:      {estado}\n"
            f"Iteraciones: {iters}\n"
            f"Error final: {errores[-1]:.2e}\n"
            f"Tolerancia:  {tol}\n"
            f"Omega (ω):   {omega}\n\n"
            f"Solución aproximada:\n"
            f"  x* = {sol[0]:.10f}\n"
            f"  y* = {sol[1]:.10f}\n\n"
            f"G₁(x, y) = {expr_g1}\n"
            f"G₂(x, y) = {expr_g2}"
        )
        self.lbl_resumen.config(text=resumen, fg=color_estado if not convergio else TEXT)
        self._mostrar_grafica(errores, historial, sol, convergio, iters)
        self.nb.select(2)   # ir a pestaña Resultado
        self.set_status(f"Listo — {'convergió' if convergio else 'no convergió'} en {iters} iteraciones", "ok" if convergio else "warn")

    # ── barra de estado ───────────────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self, bg="#11111b", height=26)
        bar.pack(fill="x", side="bottom")
        self.lbl_status = tk.Label(bar, text="Listo", bg="#11111b",
                                    fg=TEXT_MUTED, font=("Segoe UI", 9),
                                    anchor="w")
        self.lbl_status.pack(side="left", padx=12)

    def set_status(self, msg, kind=""):
        colors = {"ok": ACCENT2, "warn": YELLOW, "error": RED_ERR, "": TEXT_MUTED}
        self.lbl_status.config(text=msg, fg=colors.get(kind, TEXT_MUTED))


# ── punto de entrada ──────────────────────────────────────
def lanzar_interfaz():
    app = AppPuntoFijo()
    app.mainloop()

if __name__ == "__main__":
    lanzar_interfaz()
