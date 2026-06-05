# Método del Punto Fijo — Solucionador de Sistemas No Lineales

**Versión:** 2.0  
**Asignatura:** Métodos Numéricos  
**Periodo Académico:** 2026-1

---

## Descripción

Aplicación GUI profesional para resolver sistemas de ecuaciones no lineales usando el método de iteración de punto fijo. El solucionador proporciona una interfaz intuitiva con visualizaciones bajo demanda, ejemplos predefinidos y análisis de convergencia en tiempo real.

**Mejora clave en v2.0:** Ventana única unificada con navegación de barra lateral, eliminando la generación automática de gráficas y desorden de múltiples ventanas. Todas las visualizaciones se crean bajo demanda cuando las solicita el usuario.

---

## Características

✅ **Solucionador Interactivo**
- Ingresa funciones personalizadas G₁(x,y) y G₂(x,y)
- Aproximaciones iniciales y parámetros definidos por el usuario
- Verificación de convergencia en tiempo real usando norma jacobiana

✅ **Ejemplos Predefinidos**
- 3 sistemas de ejemplo integrados (cuadrático, círculo/parábola, exponencial)
- Ejecución de un clic con selección automática de parámetros
- Validación y verificación de exactitud de soluciones

✅ **Visualizaciones Bajo Demanda**
- Curvas de convergencia (error vs. iteración)
- Trayectoria iterativa en espacio de fase
- Tema profesional oscuro con características de accesibilidad
- **Gráficas ampliables** para mejor visualización

✅ **Análisis Matemático**
- Cálculo de jacobiana mediante diferencias finitas
- Verificación de criterio de convergencia (‖J‖∞ < 1)
- Parámetro de relajación (ω) para convergencia mejorada

✅ **Interfaz Moderna**
- Ventana única con navegación de barra lateral (6 secciones)
- Sin generación automática de gráficas (previene ralentizaciones)
- Interfaz responsiva y accesible
- **Pantalla completa** automáticamente

---

## Estructura del Proyecto

```
METODOS/
├── main_app.py                   # Aplicación principal (v2.0 - GUI unificada)
├── Punto_Fijo_v2.py              # Punto de entrada (lanza main_app)
├── Interfaz_grafica.py            # GUI heredada (compatible hacia atrás)
├── README.md                      # Este archivo
└── Graficas/                      # Directorio de salida para visualizaciones guardadas
```

### Descripción General de la Arquitectura

**Componentes principales:**

1. **Motor Numérico Principal** (`main_app.py`)
   - `punto_fijo_sistema()`: Algoritmo de iteración de punto fijo
   - `norma_jacobiana()`: Cálculo de jacobiana mediante diferencias finitas
   - `build_G()`: Analizador seguro de expresiones para entrada de usuario

2. **Aplicación GUI** (`main_app.py::MainApplication`)
   - Navegación de barra lateral con 6 secciones
   - Gestión de estado (persistencia de resultados entre secciones)
   - Renderización de gráficas bajo demanda usando Matplotlib

3. **Flujo de Datos**
   ```
   Entrada del Usuario → Analizador de Expresiones → Solucionador Numérico → Almacenamiento de Estado
                                                             ↓
                                       Análisis de Convergencia
                                                             ↓
                                    Visualización (Bajo Demanda)
   ```

---

## Installation

### Requisitos

- Python 3.7+
- tkinter (generalmente incluido con Python)
- NumPy
- Matplotlib

### Instalación

```bash
# Navega al directorio del proyecto
cd METODOS

# Instala las dependencias
pip install numpy matplotlib

# Ejecuta la aplicación
python Punto_Fijo_v2.py
```

---

## Requisitos Técnicos

```
Python >= 3.7
NumPy >= 1.19.0
Matplotlib >= 3.3.0
tkinter (incluido con Python)
```

### Entorno Virtual (recomendado)

```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

pip install numpy matplotlib
```

---

## Uso

### Lanzar la Aplicación

```bash
python Punto_Fijo_v2.py
```

La aplicación se abre automáticamente en pantalla completa.

### 1. Sección Inicio (🏠)
Guía de inicio rápido y descripción general de características. Comienza aquí si eres nuevo en la aplicación.

### 2. Sección Solucionador (🧮)
**Ingresa tus propias funciones:**

1. Introduce las funciones de iteración G₁(x,y) y G₂(x,y)
   - Ejemplo: `G₁ = sqrt(1 - y)`, `G₂ = sqrt(1 - x)`
   
2. Especifica la aproximación inicial (x₀, y₀)
   - Ejemplo: `x₀ = 0.5, y₀ = 0.5`

3. Establece los parámetros:
   - **Tolerancia (tol)**: Criterio de convergencia (predeterminado: 1e-8)
   - **Máx. iteraciones**: Límite de seguridad (predeterminado: 500)
   - **Omega (ω)**: Factor de relajación (predeterminado: 1.0)

4. Haz clic en **▶ EJECUTAR MÉTODO**

5. Visualiza el resumen de resultados

6. Haz clic en **📈 Ver Gráfica** para ver las visualizaciones

### 3. Sección Ejemplos (📚)
Ejecuta ejemplos predefinidos con un clic:

- **Ejemplo 1**: x² + y = 1, x + y² = 1
- **Ejemplo 2**: Círculo (x²+y²=4) ∩ Parábola (y=x²-1)
- **Ejemplo 3**: Sistema exponencial (x·e^y=2, y·e^x=3)

### 4. Sección Visualizaciones (📈)
Ve las gráficas de convergencia y trayectorias iterativas. Haz clic en **🔍 Ampliar Gráfica** para expandir.

### 5. Sección Configuración (⚙️)
Guía de parámetros y explicación de criterios de convergencia.

### 6. Sección Acerca de (ℹ️)
Información de la aplicación y pila tecnológica.



---

## Ejemplos Matemáticos

### Ejemplo 1: Sistema Cuadrático Simple

**Sistema:**
```
x² + y = 1
x + y² = 1
```

**Funciones de Iteración:**
```
G₁(x,y) = sqrt(1 - y)
G₂(x,y) = sqrt(1 - x)
```

**Solución:**
```
x* ≈ 0.6823278...
y* ≈ 0.6823278...
```

**Convergencia:** ~15 iteraciones con tolerancia predeterminada

### Ejemplo 2: Intersección de Círculo y Parábola

**Sistema:**
```
x² + y² = 4         (círculo)
y = x² - 1          (parábola)
```

**Funciones de Iteración:**
```
G₁(x,y) = sqrt(4 - y²)
G₂(x,y) = x² - 1
```

**Configuración:** ω = 0.6 (factor de relajación necesario)

### Ejemplo 3: Sistema Exponencial

**Sistema:**
```
x·e^y = 2
y·e^x = 3
```

**Funciones de Iteración:**
```
G₁(x,y) = 2/e^y
G₂(x,y) = 3/e^x
```

**Configuración:** ω = 0.5, máx. iteraciones = 500

## Trasfondo Matemático

### Método de Iteración de Punto Fijo

Para un sistema **x = G(x)**, la iteración es:
```
x^(k+1) = G(x^(k))
```

O con parámetro de relajación:
```
x^(k+1) = (1-ω)·x^(k) + ω·G(x^(k))
```

### Criterio de Convergencia

La convergencia local está garantizada si:
```
‖J_G(x*)‖∞ < 1
```

donde J_G es la matriz jacobiana de G.

### Medición de Error

El algoritmo utiliza la norma infinita (máximo componente absoluto):
```
error = ‖x^(k+1) - x^(k)‖∞ = max(|Δx_i|)
```

---

## Contribuciones

Este es un proyecto académico. Las contribuciones se aceptan mediante:

- Reportes de errores y sugerencias de características
- Mejoras y optimización del código
- Mejoras en la documentación
- Ejemplos adicionales

---

## Licencia

**Licencia de Proyecto Académico**  
Universidad Distrital Francisco José de Caldas — 2026-1

Solo para uso educativo y no comercial.

---

## Registro de Cambios

### v2.0 (Actual)
- ✨ Nueva GUI unificada con navegación de barra lateral
- 🚀 Visualización bajo demanda (sin generación automática de gráficas)
- 📦 Arquitectura modular de 6 secciones
- 🎨 Interfaz moderna con tema oscuro
- 📚 Documentación profesional con docstrings en inglés
- 🔧 Gestión mejorada de estado entre secciones
- 🖥️ Pantalla completa automática
- 🔍 Gráficas ampliables en ventanas independientes

### v1.x (Heredada)
- GUI original con múltiples ventanas
- Ejecución automática de ejemplos al inicio
- Generación de gráficas durante la inicialización

---

## Solución de Problemas

### "Error en Expresión"

- Verifica la sintaxis: usa solo operadores soportados (`+, -, *, /, **`)
- Funciones válidas: `sqrt(), exp(), log(), sin(), cos(), tan(), abs()`
- Las variables deben ser `x` e `y` (sensible a mayúsculas/minúsculas)
- Ejemplo correcto: `sqrt(1 - y)` ✓
- Ejemplo incorrecto: `sqrt{1 - y}` ✗

### "Norma Jacobiana ≥ 1"

La convergencia puede no ocurrir:
- Intenta una aproximación inicial diferente (x₀, y₀)
- Usa parámetro de relajación ω < 1 (recomendado: 0.5-0.8)
- Verifica la función de iteración G(x)
- Consulta la sección Configuración para más detalles

### "Sin Convergencia"

- Aumenta el número máximo de iteraciones
- Disminuye ligeramente la tolerancia
- Verifica que la aproximación inicial esté en el dominio de G
- Considera usar factor de relajación ω < 1

### Errores de Importación de Módulos

```bash
# Actualiza las dependencias
pip install --upgrade numpy matplotlib

# O reinstala desde cero
pip uninstall numpy matplotlib
pip install numpy matplotlib
```

---

## Referencias

- Numerical Recipes: The Art of Scientific Computing
- Kincaid & Cheney: Numerical Analysis
- Burden & Faires: Numerical Analysis

---

## Soporte

Para problemas o preguntas:
1. Consulta la sección "Solución de Problemas"
2. Verifica los ejemplos predefinidos
3. Revisa la documentación en cada sección de la aplicación

---

**Última Actualización:** 5 de Junio de 2026  
**Versión:** 2.0  
**Estado:** Listo para Producción
