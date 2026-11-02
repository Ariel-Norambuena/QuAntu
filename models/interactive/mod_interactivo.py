import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons
from scipy.special import wofz
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent / "Data_Rb_Gas.csv"

# ============================================================
# 1. Constantes y parametros iniciales
# ============================================================
c = 3.0e8
kB = 1.380649e-23
lambda0 = 780.241e-9
nu0 = c / lambda0

# Parámetros del 85Rb (Abundancia 72.17%)
eta_85 = 0.7217
m_85 = 85 * 1.660539e-27
centers_85 = np.array([-2.05, 1.00])
weights_85 = np.array([0.32, 1.00])

# Parámetros del 87Rb (Abundancia 27.83%)
eta_87 = 0.2783
m_87 = 87 * 1.660539e-27
centers_87 = np.array([-4.66, 2.20])
weights_87 = np.array([0.33, 1.15])

# Corrimiento global del Modelo 3
shift_global = 0.348

# ============================================================
# 2. CARGA DE DATOS EXPERIMENTALES
# ============================================================
if not DATA_FILE.is_file():
    raise FileNotFoundError(f"Required absorption data not found: {DATA_FILE}")
data = np.loadtxt(DATA_FILE, delimiter=",", skiprows=1)
x_exp = data[:,0]
y_exp = data[:,1]
y_exp = y_exp / np.max(y_exp)

margin = abs(shift_global) + 1.0
Omega = np.linspace(np.min(x_exp) - margin, np.max(x_exp) + margin, 3000)
Omega_shifted = Omega + shift_global

# ============================================================
# 3. FUNCIÓN DEL PERFIL DE VOIGT (Susceptibilidad Microscópica)
# ============================================================
def calcular_absorcion(T, gamma_MHz, usar_85, usar_87):
    # Convertimos gamma a GHz
    gamma_GHz = gamma_MHz / 1000.0
    
    # Ensanchamiento térmico (sigma) para cada masa
    FWHM_85 = nu0 * np.sqrt((8 * kB * T * np.log(2)) / (m_85 * c**2)) / 1e9
    sigma_85 = FWHM_85 / (2 * np.sqrt(2 * np.log(2)))
    
    FWHM_87 = nu0 * np.sqrt((8 * kB * T * np.log(2)) / (m_87 * c**2)) / 1e9
    sigma_87 = FWHM_87 / (2 * np.sqrt(2 * np.log(2)))

    Abs_total = np.zeros_like(Omega)
    
    # Contribución del Rubidio 85
    if usar_85:
        for W, Omega0 in zip(weights_85, centers_85):
            A_eff = eta_85 * W
            # La función wofz(z) calcula el Perfil de Voigt
            z = ((Omega - Omega0) + 1j * gamma_GHz) / (sigma_85 * np.sqrt(2))
            Abs_total += A_eff * np.real(wofz(z))
            
    # Contribución del Rubidio 87
    if usar_87:
        for W, Omega0 in zip(weights_87, centers_87):
            A_eff = eta_87 * W
            z = ((Omega - Omega0) + 1j * gamma_GHz) / (sigma_87 * np.sqrt(2))
            Abs_total += A_eff * np.real(wofz(z))
            
    # Normalización
    if np.max(Abs_total) > 0:
        Abs_total /= np.max(Abs_total)
        
    return Abs_total

# ============================================================
# 4. ESTADO INICIAL
# ============================================================
T_ini = 293.0
gamma_ini = 6.0 # 6 MHz HWHM Lorentziano (valor histórico; FWHM = 2*gamma) 
Abs_ini = calcular_absorcion(T_ini, gamma_ini, True, True)

# ============================================================
# 5. CONFIGURACIÓN DE LA VENTANA (UI)
# ============================================================
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(11, 7))

# Ajustamos los bordes para dejar espacio a los botones y perillas
plt.subplots_adjust(left=0.1, bottom=0.3, right=0.85) 

# Dibujar datos experimentales
ax.scatter(x_exp, y_exp, color='#cccccc', s=15, alpha=0.5, label='Experimento')

# Dibujar modelo
linea_modelo, = ax.plot(Omega_shifted, Abs_ini, color='#00FFFF', linewidth=2.5, label='Modelo Teórico (Voigt)')

ax.set_title("Espectro de Absorción del Rubidio (Modelo Microscópico)", fontsize=16, pad=15)
ax.set_xlabel('Detuning del Láser Ω (GHz)', fontsize=14)
ax.set_ylabel('Absorción Normalizada', fontsize=14)
ax.grid(alpha=0.2, linestyle='--')
ax.legend(loc='upper left')

# ============================================================
# 6. CREACIÓN DE CONTROLES (Sliders y Checkboxes)
# ============================================================
# Perilla de Temperatura
eje_temp = plt.axes([0.15, 0.15, 0.6, 0.03])
slider_temp = Slider(eje_temp, 'Temp (K)', 10.0, 3000.0, valinit=T_ini, color='#00FFFF')

# Perilla de Gamma (Ensanchamiento Natural)
eje_gamma = plt.axes([0.15, 0.08, 0.6, 0.03])
slider_gamma = Slider(eje_gamma, 'γ HWHM (MHz)', 0.0, 300.0, valinit=gamma_ini, color='#FF3366')

# Checkboxes para los Isótopos (A la derecha)
eje_check = plt.axes([0.87, 0.5, 0.1, 0.15])
check_isotopos = CheckButtons(eje_check, ['85-Rb', '87-Rb'], [True, True])

# ============================================================
# 7. FUNCIÓN DE ACTUALIZACIÓN
# ============================================================
def actualizar(val):
    T_nueva = slider_temp.val
    gamma_nuevo = slider_gamma.val
    
    # Leer el estado de los checkboxes (True o False)
    estado_85 = check_isotopos.get_status()[0]
    estado_87 = check_isotopos.get_status()[1]
    
    # Recalcular todo al instante
    Abs_nueva = calcular_absorcion(T_nueva, gamma_nuevo, estado_85, estado_87)
    
    # Inyectar datos a la gráfica
    linea_modelo.set_ydata(Abs_nueva)
    fig.canvas.draw_idle()

# Conectar todos los controles a la función actualizar
slider_temp.on_changed(actualizar)
slider_gamma.on_changed(actualizar)
check_isotopos.on_clicked(actualizar)

plt.show()
