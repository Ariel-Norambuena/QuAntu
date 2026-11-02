import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.special import wofz
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent / "Data_Rb_Gas.csv"

# ============================================================
# 1. Configuracion pagina
# ============================================================
st.set_page_config(page_title="Espectroscopía de Rubidio", layout="wide")

# ============================================================
# 2. Constantes y parametros iniciales
# ============================================================
c = 3.0e8
kB = 1.380649e-23
lambda0 = 780.241e-9
nu0 = c / lambda0

# Parámetros 85Rb y 87Rb
eta_85, m_85 = 0.7217, 85 * 1.660539e-27
centers_85, weights_85 = np.array([-2.05, 1.00]), np.array([0.32, 1.00])

eta_87, m_87 = 0.2783, 87 * 1.660539e-27
centers_87, weights_87 = np.array([-4.66, 2.20]), np.array([0.33, 1.15])
shift_global = 0.348

# ============================================================
# 3. Cargar datos
# ======================================================
@st.cache_data
def cargar_datos():
    if not DATA_FILE.is_file():
        raise FileNotFoundError(f"Required absorption data not found: {DATA_FILE}")
    data = np.loadtxt(DATA_FILE, delimiter=",", skiprows=1)
    x = data[:,0]
    y = data[:,1] / np.max(data[:,1])
    return x, y

x_exp, y_exp = cargar_datos()

if x_exp is not None:
    margin = abs(shift_global) + 1.0
    Omega = np.linspace(np.min(x_exp) - margin, np.max(x_exp) + margin, 3000)
else:
    Omega = np.linspace(-7, 5, 3000)
Omega_shifted = Omega + shift_global

# ============================================================
# 4. Perfil de Voight
# ============================================================
def calcular_absorcion(T, gamma_MHz, usar_85, usar_87):
    gamma_GHz = gamma_MHz / 1000.0
    sigma_85 = (nu0 * np.sqrt((8 * kB * T * np.log(2)) / (m_85 * c**2)) / 1e9) / (2 * np.sqrt(2 * np.log(2)))
    sigma_87 = (nu0 * np.sqrt((8 * kB * T * np.log(2)) / (m_87 * c**2)) / 1e9) / (2 * np.sqrt(2 * np.log(2)))

    Abs_total = np.zeros_like(Omega)
    
    if usar_85:
        for W, Omega0 in zip(weights_85, centers_85):
            z = ((Omega - Omega0) + 1j * gamma_GHz) / (sigma_85 * np.sqrt(2))
            Abs_total += (eta_85 * W) * np.real(wofz(z))
            
    if usar_87:
        for W, Omega0 in zip(weights_87, centers_87):
            z = ((Omega - Omega0) + 1j * gamma_GHz) / (sigma_87 * np.sqrt(2))
            Abs_total += (eta_87 * W) * np.real(wofz(z))
            
    if np.max(Abs_total) > 0: Abs_total /= np.max(Abs_total)
    return Abs_total, sigma_85

# ============================================================
# 5. Interfaz pagina
# ============================================================
# Título principal
st.title("Absorción Doppler en Rubidio QuAntu")
st.markdown("---")

# Crear columnas: Una estrecha para controles (sidebar), otra ancha para el gráfico
col1, col2 = st.columns([1, 3])

with col1:
    st.header("Parámetros")
    
    # Controles modernos
    T_val = st.slider("Temperatura (K)", min_value=10.0, max_value=3000.0, value=293.0, step=5.0)
    gamma_val = st.slider("Semiancho Lorentziano γ (MHz, HWHM)", min_value=0.0, max_value=300.0, value=6.0, step=0.5)
    
    st.subheader("Isótopos Activos")
    # Toggles (interruptores) modernos
    usar_85 = st.toggle("Activar 85-Rb (72.2%)", value=True)
    usar_87 = st.toggle("Activar 87-Rb (27.8%)", value=True)

with col2:
    # Recalcular física con los valores de la UI
    Abs_teorica, sigma_actual = calcular_absorcion(T_val, gamma_val, usar_85, usar_87)
    
    # Mostrar métricas clave arriba del gráfico
    m1, m2 = st.columns(2)
    m1.metric("Ancho Gaussiano (σ) 85Rb", f"{sigma_actual*1000:.1f} MHz")
    m2.metric("Picos Activos", (2 if usar_85 else 0) + (2 if usar_87 else 0))
    
    # Crear gráfica hermosa con Plotly
    fig = go.Figure()
    
    # Datos experimentales (si existen)
    if x_exp is not None:
        fig.add_trace(go.Scatter(x=x_exp, y=y_exp, mode='markers', 
                                 marker=dict(color='gray', size=4, opacity=0.5), name='Experimento'))
    
    # Curva teórica con relleno estético
    fig.add_trace(go.Scatter(x=Omega_shifted, y=Abs_teorica, mode='lines', 
                             line=dict(color='#00F0FF', width=3),
                             fill='tozeroy', fillcolor='rgba(0, 240, 255, 0.1)', 
                             name=f'Modelo Voigt'))

    fig.update_layout(
        xaxis_title="Detuning del Láser Ω (GHz)",
        yaxis_title="Absorción Normalizada",
        template="plotly_dark", # Tema oscuro nativo
        hovermode="x unified",
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    # Renderizar el gráfico en la web
    st.plotly_chart(fig, use_container_width=True)
