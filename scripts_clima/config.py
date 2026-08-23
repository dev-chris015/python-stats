import os
from pathlib import Path

# ==============================================================================
# 1. Rutas Relativas de Directorios
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Archivo de datos de entrada
CLIMA_CSV_PATH = PROJECT_ROOT / "clima_centro_america.csv"

# Directorios de salidas del paquete scripts_clima
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
FIGURES_DIR = BASE_DIR / "figuras"

# Asegurar la existencia de los directorios
for directory in [DATA_DIR, OUTPUT_DIR, FIGURES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# 2. Umbrales Metodológicos
# ==============================================================================
THRESHOLD_ALERT_IMPUTATION = 0.02  # 2%
THRESHOLD_CRITICAL_EXCLUSION = 0.10  # 10%


# ==============================================================================
# 3. Escala Beaufort para Velocidad del Viento
# ==============================================================================
# Categorías oficiales de la Escala Beaufort según actividades.md:
# Calma <0.3, Ventolina 0.3-1.5, Brisa ligera 1.6-3.3, Brisa suave 3.4-5.4,
# Brisa moderada 5.5-7.9, Brisa fresca 8.0-10.7, Brisa fuerte >=10.8 m/s
BEAUFORT_CATEGORIES = [
    {"name": "Calma", "min": 0.0, "max": 0.3},
    {"name": "Ventolina", "min": 0.3, "max": 1.5},
    {"name": "Brisa ligera", "min": 1.5, "max": 3.3},
    {"name": "Brisa suave", "min": 3.3, "max": 5.4},
    {"name": "Brisa moderada", "min": 5.4, "max": 7.9},
    {"name": "Brisa fresca", "min": 7.9, "max": 10.7},
    {"name": "Brisa fuerte", "min": 10.7, "max": float("inf")},
]

def clasificar_beaufort(viento_ms: float) -> str:
    """Clasifica una velocidad del viento (m/s) en la Escala Beaufort."""
    if float("-inf") < viento_ms < 0.3:
        return "Calma"
    elif 0.3 <= viento_ms <= 1.5:
        return "Ventolina"
    elif 1.5 < viento_ms <= 3.3:
        return "Brisa ligera"
    elif 3.3 < viento_ms <= 5.4:
        return "Brisa suave"
    elif 5.4 < viento_ms <= 7.9:
        return "Brisa moderada"
    elif 7.9 < viento_ms <= 10.7:
        return "Brisa fresca"
    else:
        return "Brisa fuerte"


# ==============================================================================
# 4. Estilos Visuales y Paletas para Matplotlib / Seaborn
# ==============================================================================
COLOR_PALETTE = ["#008080", "#FF6F61", "#4A90E2", "#50E3C2", "#F5A623", "#9013FE", "#D0021B"]
PAIS_COLORS = {
    "Belice": "#1f77b4",
    "Costa Rica": "#ff7f0e",
    "El Salvador": "#2ca02c",
    "Guatemala": "#d62728",
    "Honduras": "#9467bd",
    "Nicaragua": "#8c564b",
    "Panamá": "#e377c2"
}

def apply_custom_style():
    """Aplica configuraciones visuales profesionales a Matplotlib y Seaborn."""
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["figure.dpi"] = 300
    plt.rcParams["axes.titlesize"] = 13
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 9
    plt.rcParams["grid.alpha"] = 0.3
    plt.rcParams["grid.linestyle"] = "--"
    sns.set_palette(sns.color_palette(COLOR_PALETTE))
