import os
from pathlib import Path

# ==============================================================================
# 1. Rutas Relativas de Directorios
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent

# Directorios de datos, salidas y figuras
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
FIGURES_DIR = BASE_DIR / "figuras"

# Asegurar la existencia de los directorios
for directory in [DATA_DIR, OUTPUT_DIR, FIGURES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# 2. Umbrales Metodológicos
# ==============================================================================
# 2% para alertas o imputación de datos faltantes/atípicos
THRESHOLD_ALERT_IMPUTATION = 0.02

# 10% para exclusión o alertas críticas
THRESHOLD_CRITICAL_EXCLUSION = 0.10


# ==============================================================================
# 3. Escala Beaufort para Velocidad del Viento
# ==============================================================================
# Rangos estándar en m/s (metros por segundo) y km/h (kilómetros por hora)
# Estructura: (Límite Inferior (inclusive), Límite Superior (exclusivo), Nombre en Español, Nombre en Inglés)
BEAUFORT_SCALE_MS = [
    {"force": 0, "min": 0.0, "max": 0.5, "name_es": "Calma", "name_en": "Calm"},
    {"force": 1, "min": 0.5, "max": 1.5, "name_es": "Ventolina", "name_en": "Light air"},
    {"force": 2, "min": 1.5, "max": 3.3, "name_es": "Flojito (Brisa muy débil)", "name_en": "Light breeze"},
    {"force": 3, "min": 3.3, "max": 5.5, "name_es": "Flojo (Brisa ligera)", "name_en": "Gentle breeze"},
    {"force": 4, "min": 5.5, "max": 8.0, "name_es": "Bonancible (Brisa moderada)", "name_en": "Moderate breeze"},
    {"force": 5, "min": 8.0, "max": 10.8, "name_es": "Fresquito (Brisa fresca)", "name_en": "Fresh breeze"},
    {"force": 6, "min": 10.8, "max": 13.9, "name_es": "Fresco (Brisa fuerte)", "name_en": "Strong breeze"},
    {"force": 7, "min": 13.9, "max": 17.2, "name_es": "Frescachón (Viento fuerte)", "name_en": "High wind / Moderate gale"},
    {"force": 8, "min": 17.2, "max": 20.8, "name_es": "Temporal (Viento duro)", "name_en": "Gale / Fresh gale"},
    {"force": 9, "min": 20.8, "max": 24.5, "name_es": "Temporal fuerte (Muy duro)", "name_en": "Strong gale"},
    {"force": 10, "min": 24.5, "max": 28.5, "name_es": "Temporal duro (Tormenta)", "name_en": "Storm / Whole gale"},
    {"force": 11, "min": 28.5, "max": 32.7, "name_es": "Temporal muy duro (Borrasca)", "name_en": "Violent storm"},
    {"force": 12, "min": 32.7, "max": float("inf"), "name_es": "Huracán", "name_en": "Hurricane force"}
]

BEAUFORT_SCALE_KMH = [
    {"force": 0, "min": 0.0, "max": 1.0, "name_es": "Calma", "name_en": "Calm"},
    {"force": 1, "min": 1.0, "max": 5.0, "name_es": "Ventolina", "name_en": "Light air"},
    {"force": 2, "min": 5.0, "max": 11.0, "name_es": "Flojito (Brisa muy débil)", "name_en": "Light breeze"},
    {"force": 3, "min": 11.0, "max": 19.0, "name_es": "Flojo (Brisa ligera)", "name_en": "Gentle breeze"},
    {"force": 4, "min": 19.0, "max": 28.0, "name_es": "Bonancible (Brisa moderada)", "name_en": "Moderate breeze"},
    {"force": 5, "min": 28.0, "max": 38.0, "name_es": "Fresquito (Brisa fresca)", "name_en": "Fresh breeze"},
    {"force": 6, "min": 38.0, "max": 49.0, "name_es": "Fresco (Brisa fuerte)", "name_en": "Strong breeze"},
    {"force": 7, "min": 49.0, "max": 61.0, "name_es": "Frescachón (Viento fuerte)", "name_en": "High wind / Moderate gale"},
    {"force": 8, "min": 61.0, "max": 74.0, "name_es": "Temporal (Viento duro)", "name_en": "Gale / Fresh gale"},
    {"force": 9, "min": 74.0, "max": 88.0, "name_es": "Temporal fuerte (Muy duro)", "name_en": "Strong gale"},
    {"force": 10, "min": 88.0, "max": 102.0, "name_es": "Temporal duro (Tormenta)", "name_en": "Storm / Whole gale"},
    {"force": 11, "min": 102.0, "max": 117.0, "name_es": "Temporal muy duro (Borrasca)", "name_en": "Violent storm"},
    {"force": 12, "min": 117.0, "max": float("inf"), "name_es": "Huracán", "name_en": "Hurricane force"}
]

def get_beaufort_info(speed: float, unit: str = "m/s") -> dict:
    """
    Retorna la información de la Escala Beaufort correspondiente a una velocidad dada.
    
    Parámetros:
        speed (float): Velocidad del viento.
        unit (str): Unidad de medida. Soportados: 'm/s' o 'km/h'.
        
    Retorna:
        dict: Diccionario con la fuerza Beaufort, límites y nombres.
    """
    scale = BEAUFORT_SCALE_KMH if unit.lower() in ["km/h", "kmh"] else BEAUFORT_SCALE_MS
    for item in scale:
        if item["min"] <= speed < item["max"]:
            return item
    return scale[-1]


# ==============================================================================
# 4. Estilos Visuales y Paletas para Matplotlib / Seaborn
# ==============================================================================
# Paleta de colores principal (Sleek Dark / Teal and Coral Theme)
COLOR_PALETTE = ["#008080", "#FF6F61", "#4A90E2", "#50E3C2", "#F5A623", "#9013FE"]

# Paletas específicas
PALETTE_CATEGORICAL = COLOR_PALETTE
PALETTE_SEQUENTIAL = "viridis"
PALETTE_DIVERGING = "coolwarm"

# Mapa de alertas de color
PALETTE_ALERT = {
    "normal": "#2ecc71",     # Verde
    "alerta": "#f39c12",     # Naranja
    "critico": "#e74c3c"     # Rojo
}

def apply_custom_style():
    """
    Aplica configuraciones visuales homogéneas a Matplotlib y Seaborn
    para generar gráficos profesionales de alta calidad.
    """
    # pyrefly: ignore [missing-import]
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Configurar estilo básico de Seaborn
    sns.set_theme(style="whitegrid", palette="muted")
    
    # Parámetros personalizados de Matplotlib (rcParams)
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 10
    plt.rcParams["grid.alpha"] = 0.4
    plt.rcParams["grid.linestyle"] = "--"
    
    # Asignar la paleta por defecto en Seaborn
    sns.set_palette(sns.color_palette(COLOR_PALETTE))
