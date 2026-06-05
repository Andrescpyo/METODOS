# =============================================================
#  PUNTO FIJO — APLICACIÓN PRINCIPAL CON NAVEGACIÓN UNIFICADA
#  Métodos Numéricos — Universidad Distrital 2026-1
#  Archivo: METODOS/main_app.py
# =============================================================
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os, sys, math

# ── COLORES Y FUENTES ──────────────────────────────────────
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

# ── NÚCLEO NUMÉRICO ────────────────────────────────────────
def punto_fijo_sistema(G, x0, tol=1e-8, max_iter=500, omega=1.0):
    """
    Fixed point iteration method for systems.
    
    Parameters:
        G: Function G(x) = [g1(x,y), g2(x,y)]
        x0: Initial approximation
        tol: Tolerance
        max_iter: Maximum iterations
        omega: Relaxation parameter
        
    Returns:
        (solution, errors, history, iterations, converged)
    """
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
    """Compute Jacobian norm of G at x using finite differences."""
    n = len(x)
    J = np.zeros((n, n))
    for j in range(n):
        xp, xm = x.copy(), x.copy()
        xp[j] += h; xm[j] -= h
        J[:, j] = (G(xp) - G(xm)) / (2 * h)
    return np.linalg.norm(J, ord=np.inf), J

SAFE_NS = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
SAFE_NS.update({"np": np, "sqrt": math.sqrt, "exp": math.exp,
                "log": math.log, "sin": math.sin, "cos": math.cos,
                "tan": math.tan, "abs": abs, "pi": math.pi, "e": math.e})

def build_G(expr_g1, expr_g2):
    """Build G(x) = [g1(x,y), g2(x,y)] from string expressions."""
    def G(x_arr):
        x, y = float(x_arr[0]), float(x_arr[1])
        ns = dict(SAFE_NS); ns.update({"x": x, "y": y})
        r1 = eval(expr_g1, {"__builtins__": {}}, ns)
        r2 = eval(expr_g2, {"__builtins__": {}}, ns)
        return np.array([float(r1), float(r2)])
    return G

# ── DEFINICIÓN DE EJEMPLOS ────────────────────────────────
EJEMPLOS = {
    "Ejemplo 1: Cuadrático": {
        "desc": "x² + y = 1,  x + y² = 1",
        "g1": "sqrt(1 - y)",
        "g2": "sqrt(1 - x)",
        "x0": 0.5,
        "y0": 0.5,
        "omega": 1.0,
    },
    "Ejemplo 2: Círculo/Parábola": {
        "desc": "x²+y²=4  ∩  y=x²-1",
        "g1": "sqrt(4 - y**2)",
        "g2": "x**2 - 1",
        "x0": 1.5,
        "y0": 0.5,
        "omega": 0.6,
    },
    "Ejemplo 3: Exponencial": {
        "desc": "x·eʸ=2,  y·eˣ=3",
        "g1": "2 / exp(y)",
        "g2": "3 / exp(x)",
        "x0": 0.5,
        "y0": 0.9,
        "omega": 0.5,
    },
}

# ═══════════════════════════════════════════════════════════
#  APLICACIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════
class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Método del Punto Fijo — Universidad Distrital 2026-1")
        self.configure(bg=BG)
        self.resizable(True, True)
        
        # Pantalla completa automática
        self.state('zoomed')  # Windows
        
        # Estado compartido
        self.current_section = tk.StringVar(value="home")
        self.last_solution = None
        self.last_errors = None
        self.last_historial = None
        self.canvas_widget = None
        
        self._build_ui()
    
    def _build_ui(self):
        """Construir interfaz con navegación lateral."""
        main_frame = tk.Frame(self, bg=BG)
        main_frame.pack(fill="both", expand=True)
        
        # Sidebar
        self._build_sidebar(main_frame)
        
        # Content area
        self.content_frame = tk.Frame(main_frame, bg=BG)
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Mostrar sección inicial
        self._show_section("home")
    
    def _build_sidebar(self, parent):
        """Barra lateral con navegación."""
        sidebar = tk.Frame(parent, bg=SURFACE, width=200)
        sidebar.pack(side="left", fill="y", padx=0, pady=0)
        sidebar.pack_propagate(False)
        
        # Encabezado
        hdr = tk.Frame(sidebar, bg="#11111b", height=80)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⚙", bg="#11111b", fg=ACCENT,
                font=("Segoe UI", 24)).pack(pady=10)
        tk.Label(hdr, text="Punto Fijo", bg="#11111b", fg=ACCENT,
                font=("Segoe UI", 12, "bold")).pack()
        
        # Botones de navegación
        sections = [
            ("home", "🏠  Inicio"),
            ("solver", "🧮  Solucionador"),
            ("examples", "📚  Ejemplos"),
            ("visualizations", "📈  Visualizaciones"),
            ("settings", "⚙️  Configuración"),
            ("about", "ℹ️  Acerca de"),
        ]
        
        for sec_id, label in sections:
            btn = tk.Button(
                sidebar, text=label, bg=SURFACE, fg=TEXT_MUTED,
                font=("Segoe UI", 11), relief="flat", bd=0,
                padx=16, pady=12, anchor="w", cursor="hand2",
                command=lambda s=sec_id: self._show_section(s)
            )
            btn.pack(fill="x", padx=0, pady=2)
            btn.config(activebackground=SURFACE2, activeforeground=ACCENT)
    
    def _clear_content(self):
        """Limpiar área de contenido."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _show_section(self, section):
        """Mostrar sección especificada."""
        self._clear_content()
        self.current_section.set(section)
        
        if section == "home":
            self._section_home()
        elif section == "solver":
            self._section_solver()
        elif section == "examples":
            self._section_examples()
        elif section == "visualizations":
            self._section_visualizations()
        elif section == "settings":
            self._section_settings()
        elif section == "about":
            self._section_about()
    
    # ── SECCIONES ──────────────────────────────────────────
    def _section_home(self):
        """Sección de inicio."""
        frame = tk.Frame(self.content_frame, bg=BG)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="Bienvenido", bg=BG, fg=ACCENT,
                font=("Segoe UI", 20, "bold")).pack(pady=(0, 20))
        
        info_text = """
El Método del Punto Fijo es una técnica numérica para resolver sistemas 
de ecuaciones no lineales de la forma:
    
    x = G₁(x, y)
    y = G₂(x, y)

CARACTERÍSTICAS:
• Solucionador: Ingresa tus propias funciones G₁ y G₂
• Ejemplos: Tres casos de uso predefinidos
• Visualizaciones: Gráficas de convergencia y trayectoria
• Configuración: Ajusta parámetros numéricos
• Análisis: Verifica convergencia mediante norma jacobiana

CÓMO USAR:
1. Ve a "Solucionador" para ingresar tus funciones
2. O explora "Ejemplos" para ver casos predefinidos
3. Usa "Visualizaciones" para ver gráficas de convergencia
4. Ajusta parámetros en "Configuración" si es necesario
        """
        
        txt = tk.Label(frame, text=info_text, bg=BG, fg=TEXT,
                      font=("Segoe UI", 10), justify="left",
                      wraplength=800)
        txt.pack(anchor="nw", pady=20)
    
    def _section_solver(self):
        """Solucionador interactivo."""
        frame = tk.Frame(self.content_frame, bg=BG)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="Solucionador Interactivo", bg=BG, fg=ACCENT,
                font=FONT_HEAD).pack(anchor="w", pady=(0, 15))
        
        # Instrucciones
        info_frame = tk.Frame(frame, bg=SURFACE, bd=0, relief="flat")
        info_frame.pack(fill="x", pady=(0, 15))
        tk.Label(info_frame, text="ℹ  Ingresa G₁(x,y) y G₂(x,y)\n"
                                 "   Operadores: + - * / ** sqrt() exp() log() sin() cos() tan() abs()",
                bg=SURFACE, fg=TEXT_MUTED, font=("Segoe UI", 9), justify="left",
                wraplength=800).pack(padx=12, pady=8, anchor="w")
        
        # Campos
        campo_frame = tk.Frame(frame, bg=BG)
        campo_frame.pack(fill="x", pady=(0, 15))
        
        def campo(parent, label, row, placeholder, var_name):
            tk.Label(parent, text=label, bg=BG, fg=TEXT, font=FONT_HEAD,
                    width=12, anchor="e").grid(row=row, column=0, padx=(0,10), pady=6, sticky="e")
            sv = tk.StringVar(value=placeholder)
            e = tk.Entry(parent, textvariable=sv, bg=SURFACE2, fg=ACCENT,
                        font=("Consolas", 11), insertbackground=ACCENT,
                        relief="flat", bd=6, width=50)
            e.grid(row=row, column=1, padx=4, pady=6, sticky="w")
            setattr(self, var_name, sv)
            return e
        
        campo(campo_frame, "G₁(x, y) =", 0, "sqrt(1 - y)", "sv_g1")
        campo(campo_frame, "G₂(x, y) =", 1, "sqrt(1 - x)", "sv_g2")
        campo(campo_frame, "x₀ =", 2, "0.5", "sv_x0")
        campo(campo_frame, "y₀ =", 3, "0.5", "sv_y0")
        
        # Parámetros
        param_frame = tk.Frame(frame, bg=BG)
        param_frame.pack(fill="x", pady=(0, 20))
        
        def param(parent, label, col, default, var_name):
            tk.Label(parent, text=label, bg=BG, fg=TEXT_MUTED,
                    font=("Segoe UI", 10)).grid(row=0, column=col*2, padx=(0,8), sticky="e")
            sv = tk.StringVar(value=default)
            e = tk.Entry(parent, textvariable=sv, bg=SURFACE2, fg=YELLOW,
                        font=FONT_MONO, relief="flat", bd=4, width=12)
            e.grid(row=0, column=col*2+1, padx=(0,20))
            setattr(self, var_name, sv)
        
        param(param_frame, "Tolerancia:", 0, "1e-8", "sv_tol")
        param(param_frame, "Máx. iter:", 1, "500", "sv_maxiter")
        param(param_frame, "Omega (ω):", 2, "1.0", "sv_omega")
        
        # Botón ejecutar
        btn = tk.Button(frame, text="▶  EJECUTAR MÉTODO",
                       bg=ACCENT, fg="#1e1e2e", font=("Segoe UI", 12, "bold"),
                       relief="flat", bd=0, padx=20, pady=10,
                       activebackground="#5a7fee", cursor="hand2",
                       command=self._ejecutar_solucionador)
        btn.pack(pady=15)
        
        # Resultado
        self.solver_result_frame = tk.Frame(frame, bg=BG)
        self.solver_result_frame.pack(fill="both", expand=True, pady=(15, 0))
    
    def _ejecutar_solucionador(self):
        """Ejecutar método del solucionador."""
        for widget in self.solver_result_frame.winfo_children():
            widget.destroy()
        
        try:
            expr_g1 = self.sv_g1.get().strip()
            expr_g2 = self.sv_g2.get().strip()
            x0_val = float(self.sv_x0.get())
            y0_val = float(self.sv_y0.get())
            tol = float(self.sv_tol.get())
            maxiter = int(self.sv_maxiter.get())
            omega = float(self.sv_omega.get())
        except ValueError as e:
            messagebox.showerror("Error", f"Parámetro inválido: {e}")
            return
        
        try:
            G = build_G(expr_g1, expr_g2)
            x0 = np.array([x0_val, y0_val])
            _ = G(x0)
        except Exception as e:
            messagebox.showerror("Error", f"Error en función G: {e}")
            return
        
        # Ejecutar método
        try:
            sol, errores, historial, iters, convergio = punto_fijo_sistema(
                G, x0, tol=tol, max_iter=maxiter, omega=omega)
        except Exception as e:
            messagebox.showerror("Error", f"Error en iteración: {e}")
            return
        
        # Guardar resultados
        self.last_solution = sol
        self.last_errors = errores
        self.last_historial = historial
        
        # Mostrar resumen
        result_frame = tk.Frame(self.solver_result_frame, bg=SURFACE, relief="flat", bd=0)
        result_frame.pack(fill="x", padx=16, pady=10)
        
        estado = "✓ CONVERGIÓ" if convergio else "✗ No convergió"
        color = ACCENT2 if convergio else RED_ERR
        
        resumen = f"""
{estado} en {iters} iteraciones
Error final: {errores[-1]:.2e}

Solución:
  x* = {sol[0]:.10f}
  y* = {sol[1]:.10f}
        """.strip()
        
        tk.Label(result_frame, text=resumen, bg=SURFACE, fg=color,
                font=("Consolas", 10), justify="left",
                anchor="nw").pack(padx=12, pady=8, fill="x")
        
        # Botón para ver gráfica
        btn_graph = tk.Button(self.solver_result_frame, text="📈  Ver Gráfica",
                             bg=ACCENT, fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
                             relief="flat", bd=0, padx=15, pady=8,
                             activebackground="#5a7fee", cursor="hand2",
                             command=self._mostrar_grafica_solucionador)
        btn_graph.pack(pady=10)
    
    def _mostrar_grafica_solucionador(self):
        """Mostrar gráfica de convergencia."""
        if self.last_solution is None:
            messagebox.showwarning("Advertencia", "Ejecuta el método primero")
            return
        
        for widget in self.solver_result_frame.winfo_children():
            widget.destroy()
        
        # Frame para botones
        btn_frame = tk.Frame(self.solver_result_frame, bg=BG)
        btn_frame.pack(fill="x", pady=10)
        
        btn_expand = tk.Button(btn_frame, text="🔍 Ampliar Gráfica",
                              bg=ACCENT, fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
                              relief="flat", bd=0, padx=15, pady=8,
                              activebackground="#5a7fee", cursor="hand2",
                              command=self._ampliar_grafica_solucionador)
        btn_expand.pack(side="left", padx=10)
        
        fig, axes = plt.subplots(1, 2, figsize=(10, 4),
                                facecolor="#11111b")
        fig.subplots_adjust(wspace=0.35)
        
        # Convergencia
        ax1 = axes[0]
        ax1.set_facecolor("#1e1e2e")
        ax1.semilogy(range(1, len(self.last_errors)+1), self.last_errors,
                    color=ACCENT, linewidth=1.8, marker='o', markersize=2)
        ax1.set_title("Convergencia del Error", color=TEXT, fontsize=9)
        ax1.set_xlabel("Iteración", color=TEXT_MUTED, fontsize=8)
        ax1.set_ylabel("Error (norma ∞)", color=TEXT_MUTED, fontsize=8)
        ax1.tick_params(colors=TEXT_MUTED, labelsize=7)
        for spine in ax1.spines.values():
            spine.set_edgecolor("#313149")
        ax1.grid(True, alpha=0.2, color=TEXT_MUTED)
        
        # Trayectoria
        ax2 = axes[1]
        ax2.set_facecolor("#1e1e2e")
        hist = np.array(self.last_historial)
        ax2.plot(hist[:, 0], hist[:, 1], 'o--',
                color=ACCENT, linewidth=1.2, markersize=3, alpha=0.7,
                label="Trayectoria")
        ax2.plot(self.last_solution[0], self.last_solution[1], '*',
                color=ACCENT2, markersize=14, label="Solución")
        ax2.set_title("Trayectoria Iterativa", color=TEXT, fontsize=9)
        ax2.set_xlabel("x", color=TEXT_MUTED, fontsize=8)
        ax2.set_ylabel("y", color=TEXT_MUTED, fontsize=8)
        ax2.tick_params(colors=TEXT_MUTED, labelsize=7)
        for spine in ax2.spines.values():
            spine.set_edgecolor("#313149")
        ax2.grid(True, alpha=0.2, color=TEXT_MUTED)
        ax2.legend(fontsize=7, facecolor=SURFACE, labelcolor=TEXT)
        
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
        
        canvas = FigureCanvasTkAgg(fig, master=self.solver_result_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)
        self.canvas_widget = canvas
        self.fig_cache = fig
    
    def _ampliar_grafica_solucionador(self):
        """Abrir gráfica ampliada en ventana nueva."""
        if self.last_solution is None:
            messagebox.showwarning("Advertencia", "Ejecuta el método primero")
            return
        
        top = tk.Toplevel(self)
        top.title("Gráfica Ampliada")
        top.geometry("1200x600")
        top.configure(bg=BG)
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6),
                                facecolor="#11111b")
        fig.subplots_adjust(wspace=0.35)
        
        # Convergencia
        ax1 = axes[0]
        ax1.set_facecolor("#1e1e2e")
        ax1.semilogy(range(1, len(self.last_errors)+1), self.last_errors,
                    color=ACCENT, linewidth=2.5, marker='o', markersize=4)
        ax1.set_title("Convergencia del Error", color=TEXT, fontsize=14, fontweight='bold')
        ax1.set_xlabel("Iteración", color=TEXT_MUTED, fontsize=12)
        ax1.set_ylabel("Error (norma ∞)", color=TEXT_MUTED, fontsize=12)
        ax1.tick_params(colors=TEXT_MUTED, labelsize=10)
        for spine in ax1.spines.values():
            spine.set_edgecolor("#313149")
        ax1.grid(True, alpha=0.2, color=TEXT_MUTED)
        
        # Trayectoria
        ax2 = axes[1]
        ax2.set_facecolor("#1e1e2e")
        hist = np.array(self.last_historial)
        ax2.plot(hist[:, 0], hist[:, 1], 'o--',
                color=ACCENT, linewidth=2, markersize=5, alpha=0.7,
                label="Trayectoria")
        ax2.plot(self.last_solution[0], self.last_solution[1], '*',
                color=ACCENT2, markersize=20, label="Solución")
        ax2.set_title("Trayectoria Iterativa", color=TEXT, fontsize=14, fontweight='bold')
        ax2.set_xlabel("x", color=TEXT_MUTED, fontsize=12)
        ax2.set_ylabel("y", color=TEXT_MUTED, fontsize=12)
        ax2.tick_params(colors=TEXT_MUTED, labelsize=10)
        for spine in ax2.spines.values():
            spine.set_edgecolor("#313149")
        ax2.grid(True, alpha=0.2, color=TEXT_MUTED)
        ax2.legend(fontsize=10, facecolor=SURFACE, labelcolor=TEXT)
        
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _section_examples(self):
        """Sección de ejemplos predefinidos."""
        frame = tk.Frame(self.content_frame, bg=BG)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="Ejemplos Predefinidos", bg=BG, fg=ACCENT,
                font=FONT_HEAD).pack(anchor="w", pady=(0, 20))
        
        for name, data in EJEMPLOS.items():
            self._crear_tarjeta_ejemplo(frame, name, data)
    
    def _crear_tarjeta_ejemplo(self, parent, name, data):
        """Crear tarjeta con ejemplo."""
        card = tk.Frame(parent, bg=SURFACE, relief="flat", bd=0)
        card.pack(fill="x", pady=10)
        
        # Encabezado
        hdr = tk.Frame(card, bg=SURFACE2)
        hdr.pack(fill="x")
        tk.Label(hdr, text=name, bg=SURFACE2, fg=ACCENT,
                font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=8)
        
        # Descripción
        tk.Label(card, text=data["desc"], bg=SURFACE, fg=TEXT_MUTED,
                font=("Segoe UI", 10), justify="left").pack(anchor="w", padx=12, pady=4)
        
        # Fórmulas
        fmla = f"G₁(x,y) = {data['g1']}\nG₂(x,y) = {data['g2']}"
        tk.Label(card, text=fmla, bg=SURFACE, fg=ACCENT,
                font=("Consolas", 9), justify="left").pack(anchor="w", padx=12, pady=4)
        
        # Botón ejecutar
        btn = tk.Button(card, text="▶  Ejecutar este ejemplo",
                       bg=ACCENT, fg="#1e1e2e", font=("Segoe UI", 10),
                       relief="flat", bd=0, padx=15, pady=8,
                       activebackground="#5a7fee", cursor="hand2",
                       command=lambda: self._ejecutar_ejemplo(name, data))
        btn.pack(pady=8, padx=12)
    
    def _ejecutar_ejemplo(self, name, data):
        """Ejecutar ejemplo específico."""
        try:
            G = build_G(data["g1"], data["g2"])
            x0 = np.array([data["x0"], data["y0"]])
            sol, errores, historial, iters, convergio = punto_fijo_sistema(
                G, x0, tol=1e-8, max_iter=500, omega=data["omega"])
            
            self.last_solution = sol
            self.last_errors = errores
            self.last_historial = historial
            
            # Mostrar resultado
            msg = f"✓ Convergió en {iters} iteraciones\n\n"
            msg += f"Solución:\n  x* = {sol[0]:.10f}\n  y* = {sol[1]:.10f}"
            messagebox.showinfo(name, msg)
            
            # Ir a visualizaciones
            self._show_section("visualizations")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _section_visualizations(self):
        """Sección de visualizaciones."""
        frame = tk.Frame(self.content_frame, bg=BG)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="Visualizaciones", bg=BG, fg=ACCENT,
                font=FONT_HEAD).pack(anchor="w", pady=(0, 15))
        
        if self.last_solution is None:
            tk.Label(frame, text="Ejecuta el método primero para generar gráficas.",
                    bg=BG, fg=TEXT_MUTED, font=("Segoe UI", 10)).pack(pady=50)
            return
        
        # Frame para botones
        btn_frame = tk.Frame(frame, bg=BG)
        btn_frame.pack(fill="x", pady=(0, 15))
        
        btn_expand = tk.Button(btn_frame, text="🔍 Ampliar Gráfica",
                              bg=ACCENT, fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
                              relief="flat", bd=0, padx=15, pady=8,
                              activebackground="#5a7fee", cursor="hand2",
                              command=self._ampliar_grafica_visualizaciones)
        btn_expand.pack(side="left", padx=10)
        
        # Gráfica
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.5),
                                facecolor="#11111b")
        fig.subplots_adjust(wspace=0.35)
        
        # Convergencia
        ax1 = axes[0]
        ax1.set_facecolor("#1e1e2e")
        ax1.semilogy(range(1, len(self.last_errors)+1), self.last_errors,
                    color=ACCENT, linewidth=1.8, marker='o', markersize=2)
        ax1.set_title("Convergencia del Error", color=TEXT, fontsize=10)
        ax1.set_xlabel("Iteración", color=TEXT_MUTED, fontsize=9)
        ax1.set_ylabel("Error (norma ∞)", color=TEXT_MUTED, fontsize=9)
        ax1.tick_params(colors=TEXT_MUTED, labelsize=8)
        for spine in ax1.spines.values():
            spine.set_edgecolor("#313149")
        ax1.grid(True, alpha=0.2, color=TEXT_MUTED)
        
        # Trayectoria
        ax2 = axes[1]
        ax2.set_facecolor("#1e1e2e")
        hist = np.array(self.last_historial)
        ax2.plot(hist[:, 0], hist[:, 1], 'o--',
                color=ACCENT, linewidth=1.2, markersize=3, alpha=0.7,
                label="Trayectoria")
        ax2.plot(self.last_solution[0], self.last_solution[1], '*',
                color=ACCENT2, markersize=14, label="Solución")
        ax2.set_title("Trayectoria Iterativa", color=TEXT, fontsize=10)
        ax2.set_xlabel("x", color=TEXT_MUTED, fontsize=9)
        ax2.set_ylabel("y", color=TEXT_MUTED, fontsize=9)
        ax2.tick_params(colors=TEXT_MUTED, labelsize=8)
        for spine in ax2.spines.values():
            spine.set_edgecolor("#313149")
        ax2.grid(True, alpha=0.2, color=TEXT_MUTED)
        ax2.legend(fontsize=8, facecolor=SURFACE, labelcolor=TEXT)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _ampliar_grafica_visualizaciones(self):
        """Abrir gráfica ampliada de visualizaciones en ventana nueva."""
        if self.last_solution is None:
            messagebox.showwarning("Advertencia", "Ejecuta el método primero")
            return
        
        top = tk.Toplevel(self)
        top.title("Gráfica Ampliada - Visualizaciones")
        top.geometry("1200x600")
        top.configure(bg=BG)
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6),
                                facecolor="#11111b")
        fig.subplots_adjust(wspace=0.35)
        
        # Convergencia
        ax1 = axes[0]
        ax1.set_facecolor("#1e1e2e")
        ax1.semilogy(range(1, len(self.last_errors)+1), self.last_errors,
                    color=ACCENT, linewidth=2.5, marker='o', markersize=4)
        ax1.set_title("Convergencia del Error", color=TEXT, fontsize=14, fontweight='bold')
        ax1.set_xlabel("Iteración", color=TEXT_MUTED, fontsize=12)
        ax1.set_ylabel("Error (norma ∞)", color=TEXT_MUTED, fontsize=12)
        ax1.tick_params(colors=TEXT_MUTED, labelsize=10)
        for spine in ax1.spines.values():
            spine.set_edgecolor("#313149")
        ax1.grid(True, alpha=0.2, color=TEXT_MUTED)
        
        # Trayectoria
        ax2 = axes[1]
        ax2.set_facecolor("#1e1e2e")
        hist = np.array(self.last_historial)
        ax2.plot(hist[:, 0], hist[:, 1], 'o--',
                color=ACCENT, linewidth=2, markersize=5, alpha=0.7,
                label="Trayectoria")
        ax2.plot(self.last_solution[0], self.last_solution[1], '*',
                color=ACCENT2, markersize=20, label="Solución")
        ax2.set_title("Trayectoria Iterativa", color=TEXT, fontsize=14, fontweight='bold')
        ax2.set_xlabel("x", color=TEXT_MUTED, fontsize=12)
        ax2.set_ylabel("y", color=TEXT_MUTED, fontsize=12)
        ax2.tick_params(colors=TEXT_MUTED, labelsize=10)
        for spine in ax2.spines.values():
            spine.set_edgecolor("#313149")
        ax2.grid(True, alpha=0.2, color=TEXT_MUTED)
        ax2.legend(fontsize=10, facecolor=SURFACE, labelcolor=TEXT)
        
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _section_settings(self):
        """Sección de configuración."""
        frame = tk.Frame(self.content_frame, bg=BG)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="Configuración", bg=BG, fg=ACCENT,
                font=FONT_HEAD).pack(anchor="w", pady=(0, 20))
        
        settings_text = """
PARÁMETROS PREDETERMINADOS:

• Tolerancia (tol): Criterio de convergencia
  Valor por defecto: 1e-8
  Rango recomendado: 1e-12 a 1e-4

• Máximo de iteraciones: Límite de iteraciones
  Valor por defecto: 500
  Rango recomendado: 100 a 1000

• Omega (ω): Factor de relajación
  Valor por defecto: 1.0
  Rango: 0 < ω ≤ 1
  Si ‖J‖∞ ≥ 1, usar ω < 1 para mejorar convergencia

CRITERIO DE CONVERGENCIA:
  El método converge si ‖J_G‖∞ < 1, donde J_G es la Jacobiana.
  
  Si ‖J‖∞ ≥ 1:
  • Verificar la función G(x)
  • Usar factor de relajación ω < 1
  • Cambiar punto inicial x₀
        """
        
        txt = tk.Label(frame, text=settings_text, bg=BG, fg=TEXT,
                      font=("Consolas", 9), justify="left",
                      wraplength=900)
        txt.pack(anchor="nw", pady=20)
    
    def _section_about(self):
        """Sección de información."""
        frame = tk.Frame(self.content_frame, bg=BG)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="Acerca de", bg=BG, fg=ACCENT,
                font=FONT_HEAD).pack(anchor="w", pady=(0, 20))
        
        about_text = """
MÉTODO DEL PUNTO FIJO

Versión: 2.0
Institución: Universidad Distrital Francisco José de Caldas
Asignatura: Métodos Numéricos
Periodo: 2026-1

DESCRIPCIÓN:
Aplicación para resolver sistemas de ecuaciones no lineales 
mediante el método del punto fijo (fixed-point iteration).

TECNOLOGÍA:
• Python 3.x
• Tkinter (GUI)
• NumPy (Cálculos numéricos)
• Matplotlib (Visualización)

AUTOR:
Andrés Cerdas Padilla

GitHub:
https://github.com/Andrescpyo

LICENCIA:
Proyecto académico — Universidad Distrital 2026-1

CARACTERÍSTICAS:
✓ Interfaz intuitiva y moderna
✓ Ejecución bajo demanda (sin gráficas automáticas)
✓ Análisis de convergencia mediante Jacobiana
✓ Ejemplos predefinidos
✓ Visualización de trayectorias e iteraciones
✓ Parámetros personalizables
        """
        
        txt = tk.Label(frame, text=about_text, bg=BG, fg=TEXT,
                      font=("Consolas", 9), justify="left",
                      wraplength=900, anchor="nw")
        txt.pack(pady=20, fill="both", expand=True)


def main():
    app = MainApplication()
    app.mainloop()


if __name__ == "__main__":
    main()
