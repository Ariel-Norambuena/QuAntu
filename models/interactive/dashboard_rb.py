import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.special import wofz
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent / "Data_Rb_Gas.csv"

# ============================================================
# 1. Page configuration
# ============================================================
st.set_page_config(page_title="Rubidium Spectroscopy", layout="wide")

# ============================================================
# 2. Constants and initial parameters
# ============================================================
c = 3.0e8
kB = 1.380649e-23
lambda0 = 780.241e-9
nu0 = c / lambda0

# 85Rb and 87Rb parameters
eta_85, m_85 = 0.7217, 85 * 1.660539e-27
centers_85, weights_85 = np.array([-2.05, 1.00]), np.array([0.32, 1.00])

eta_87, m_87 = 0.2783, 87 * 1.660539e-27
centers_87, weights_87 = np.array([-4.66, 2.20]), np.array([0.33, 1.15])
shift_global = 0.348

# ============================================================
# 3. Load data
# ======================================================
@st.cache_data
def load_data():
    if not DATA_FILE.is_file():
        raise FileNotFoundError(f"Required absorption data not found: {DATA_FILE}")
    data = np.loadtxt(DATA_FILE, delimiter=",", skiprows=1)
    x = data[:,0]
    y = data[:,1] / np.max(data[:,1])
    return x, y

x_exp, y_exp = load_data()

if x_exp is not None:
    margin = abs(shift_global) + 1.0
    Omega = np.linspace(np.min(x_exp) - margin, np.max(x_exp) + margin, 3000)
else:
    Omega = np.linspace(-7, 5, 3000)
Omega_shifted = Omega + shift_global

# ============================================================
# 4. Voigt profile
# ============================================================
def calculate_absorption(T, gamma_MHz, use_rb85, use_rb87):
    gamma_GHz = gamma_MHz / 1000.0
    sigma_85 = (nu0 * np.sqrt((8 * kB * T * np.log(2)) / (m_85 * c**2)) / 1e9) / (2 * np.sqrt(2 * np.log(2)))
    sigma_87 = (nu0 * np.sqrt((8 * kB * T * np.log(2)) / (m_87 * c**2)) / 1e9) / (2 * np.sqrt(2 * np.log(2)))

    total_absorption = np.zeros_like(Omega)

    if use_rb85:
        for W, Omega0 in zip(weights_85, centers_85):
            z = ((Omega - Omega0) + 1j * gamma_GHz) / (sigma_85 * np.sqrt(2))
            total_absorption += (eta_85 * W) * np.real(wofz(z))

    if use_rb87:
        for W, Omega0 in zip(weights_87, centers_87):
            z = ((Omega - Omega0) + 1j * gamma_GHz) / (sigma_87 * np.sqrt(2))
            total_absorption += (eta_87 * W) * np.real(wofz(z))

    if np.max(total_absorption) > 0: total_absorption /= np.max(total_absorption)
    return total_absorption, sigma_85

# ============================================================
# 5. Page interface
# ============================================================
# Page title
st.title("QuAntü Rubidium Doppler Absorption")
st.markdown("---")

# Use a narrow controls column and a wide plot column
col1, col2 = st.columns([1, 3])

with col1:
    st.header("Parameters")

    # Interactive controls
    T_val = st.slider("Temperature (K)", min_value=10.0, max_value=3000.0, value=293.0, step=5.0)
    gamma_val = st.slider("Lorentzian HWHM γ (MHz)", min_value=0.0, max_value=300.0, value=6.0, step=0.5)

    st.subheader("Active Isotopes")
    # Isotope toggles
    use_rb85 = st.toggle("Enable 85-Rb (72.2%)", value=True)
    use_rb87 = st.toggle("Enable 87-Rb (27.8%)", value=True)

with col2:
    # Recalculate the model from the UI values
    theoretical_absorption, current_sigma = calculate_absorption(T_val, gamma_val, use_rb85, use_rb87)

    # Display key metrics above the plot
    m1, m2 = st.columns(2)
    m1.metric("85Rb Gaussian Width (σ)", f"{current_sigma*1000:.1f} MHz")
    m2.metric("Active Peaks", (2 if use_rb85 else 0) + (2 if use_rb87 else 0))

    # Create the Plotly figure
    fig = go.Figure()

    # Experimental reference data (when available)
    if x_exp is not None:
        fig.add_trace(go.Scatter(x=x_exp, y=y_exp, mode='markers',
                                 marker=dict(color='gray', size=4, opacity=0.5), name='Reference data'))

    # Theoretical curve with shading
    fig.add_trace(go.Scatter(x=Omega_shifted, y=theoretical_absorption, mode='lines',
                             line=dict(color='#00F0FF', width=3),
                             fill='tozeroy', fillcolor='rgba(0, 240, 255, 0.1)',
                             name=f'Voigt Model'))

    fig.update_layout(
        xaxis_title="Laser Detuning Ω (GHz)",
        yaxis_title="Normalized Absorption",
        template="plotly_dark", # Built-in dark theme
        hovermode="x unified",
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    # Render the plot in the dashboard
    st.plotly_chart(fig, use_container_width=True)
