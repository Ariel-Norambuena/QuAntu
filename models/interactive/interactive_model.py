import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons
from scipy.special import wofz
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent / "Data_Rb_Gas.csv"

# ============================================================
# 1. Constants and initial parameters
# ============================================================
c = 3.0e8
kB = 1.380649e-23
lambda0 = 780.241e-9
nu0 = c / lambda0

# 85Rb parameters (72.17% abundance)
eta_85 = 0.7217
m_85 = 85 * 1.660539e-27
centers_85 = np.array([-2.05, 1.00])
weights_85 = np.array([0.32, 1.00])

# 87Rb parameters (27.83% abundance)
eta_87 = 0.2783
m_87 = 87 * 1.660539e-27
centers_87 = np.array([-4.66, 2.20])
weights_87 = np.array([0.33, 1.15])

# Global shift from Model 3
shift_global = 0.348

# ============================================================
# 2. LOAD EXPERIMENTAL REFERENCE DATA
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
# 3. VOIGT PROFILE (Microscopic Susceptibility)
# ============================================================
def calculate_absorption(T, gamma_MHz, use_rb85, use_rb87):
    # Convert the Lorentzian HWHM gamma to GHz
    gamma_GHz = gamma_MHz / 1000.0

    # Thermal broadening (sigma) for each atomic mass
    FWHM_85 = nu0 * np.sqrt((8 * kB * T * np.log(2)) / (m_85 * c**2)) / 1e9
    sigma_85 = FWHM_85 / (2 * np.sqrt(2 * np.log(2)))

    FWHM_87 = nu0 * np.sqrt((8 * kB * T * np.log(2)) / (m_87 * c**2)) / 1e9
    sigma_87 = FWHM_87 / (2 * np.sqrt(2 * np.log(2)))

    total_absorption = np.zeros_like(Omega)

    # Rubidium-85 contribution
    if use_rb85:
        for W, Omega0 in zip(weights_85, centers_85):
            A_eff = eta_85 * W
            # The wofz(z) function evaluates the Voigt profile
            z = ((Omega - Omega0) + 1j * gamma_GHz) / (sigma_85 * np.sqrt(2))
            total_absorption += A_eff * np.real(wofz(z))

    # Rubidium-87 contribution
    if use_rb87:
        for W, Omega0 in zip(weights_87, centers_87):
            A_eff = eta_87 * W
            z = ((Omega - Omega0) + 1j * gamma_GHz) / (sigma_87 * np.sqrt(2))
            total_absorption += A_eff * np.real(wofz(z))

    # Normalization
    if np.max(total_absorption) > 0:
        total_absorption /= np.max(total_absorption)

    return total_absorption

# ============================================================
# 4. INITIAL STATE
# ============================================================
initial_temperature = 293.0
initial_gamma = 6.0 # 6 MHz Lorentzian HWHM (historical value; FWHM = 2*gamma)
initial_absorption = calculate_absorption(initial_temperature, initial_gamma, True, True)

# ============================================================
# 5. WINDOW CONFIGURATION (UI)
# ============================================================
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(11, 7))

# Leave space for the buttons and sliders
plt.subplots_adjust(left=0.1, bottom=0.3, right=0.85)

# Plot experimental reference data
ax.scatter(x_exp, y_exp, color='#cccccc', s=15, alpha=0.5, label='Reference data')

# Plot the model
model_line, = ax.plot(Omega_shifted, initial_absorption, color='#00FFFF', linewidth=2.5, label='Theoretical model (Voigt)')

ax.set_title("Rubidium Absorption Spectrum (Microscopic Model)", fontsize=16, pad=15)
ax.set_xlabel('Laser Detuning Ω (GHz)', fontsize=14)
ax.set_ylabel('Normalized Absorption', fontsize=14)
ax.grid(alpha=0.2, linestyle='--')
ax.legend(loc='upper left')

# ============================================================
# 6. CREATE CONTROLS (Sliders and Checkboxes)
# ============================================================
# Temperature slider
temperature_axis = plt.axes([0.15, 0.15, 0.6, 0.03])
temperature_slider = Slider(temperature_axis, 'Temp (K)', 10.0, 3000.0, valinit=initial_temperature, color='#00FFFF')

# Gamma slider (Lorentzian HWHM)
gamma_axis = plt.axes([0.15, 0.08, 0.6, 0.03])
gamma_slider = Slider(gamma_axis, 'γ HWHM (MHz)', 0.0, 300.0, valinit=initial_gamma, color='#FF3366')

# Isotope checkboxes (right side)
checkbox_axis = plt.axes([0.87, 0.5, 0.1, 0.15])
isotope_checkboxes = CheckButtons(checkbox_axis, ['85-Rb', '87-Rb'], [True, True])

# ============================================================
# 7. UPDATE FUNCTION
# ============================================================
def update_spectrum(val):
    new_temperature = temperature_slider.val
    new_gamma = gamma_slider.val

    # Read checkbox states (True or False)
    rb85_enabled = isotope_checkboxes.get_status()[0]
    rb87_enabled = isotope_checkboxes.get_status()[1]

    # Recalculate the spectrum immediately
    new_absorption = calculate_absorption(new_temperature, new_gamma, rb85_enabled, rb87_enabled)

    # Update the plotted data
    model_line.set_ydata(new_absorption)
    fig.canvas.draw_idle()

# Connect all controls to the update function
temperature_slider.on_changed(update_spectrum)
gamma_slider.on_changed(update_spectrum)
isotope_checkboxes.on_clicked(update_spectrum)

plt.show()
