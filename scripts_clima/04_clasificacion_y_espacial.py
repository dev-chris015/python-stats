import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from pathlib import Path
import config

def main():
    print("=== EJECUTANDO 04_CLASIFICACION_Y_ESPACIAL.PY (ACTIVIDADES 8, 9, 10, 11 Y 12) ===")
    config.apply_custom_style()
    
    # 1. Cargar dataset
    df = pd.read_csv(config.CLIMA_CSV_PATH)
    
    # --------------------------------------------------------------------------
    # ACTIVIDAD 8 & FIGURA OBLIGATORIA 4: Diagrama de Dispersión Geográfico
    # --------------------------------------------------------------------------
    # Promediar 2020-2025 por punto geográfico (lat, lon, pais)
    df_coords = df.groupby(["pais", "latitude", "longitude"])[["temperatura_c", "precipitacion_mensual_mm"]].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for pais, color in config.PAIS_COLORS.items():
        sub = df_coords[df_coords["pais"] == pais]
        ax.scatter(
            sub["longitude"],
            sub["latitude"],
            c=color,
            label=pais,
            alpha=0.6,
            edgecolors="none",
            s=25
        )
        
    ax.set_title("Figura 4: Distribución Geográfica de Puntos Observacionales de ERA5-Land por País")
    ax.set_xlabel("Longitud (°)")
    ax.set_ylabel("Latitud (°)")
    ax.legend(title="País", loc="lower left")
    
    fig.text(0.12, 0.01, "Fuente: ERA5-Land, Copernicus Climate Change Service. Promedios 2020–2025 por coordenada.", fontsize=8, color="gray")
    
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    ruta_fig4 = config.FIGURES_DIR / "fig4_dispersion_geografica.png"
    plt.savefig(ruta_fig4, dpi=300)
    plt.close()
    print(f"[Actividad 8 & Fig 4] Guardada en: {ruta_fig4}")
    
    # --------------------------------------------------------------------------
    # ACTIVIDAD 9: Categorización por Cuartiles Regionales
    # --------------------------------------------------------------------------
    # Cuartiles regionales globales de Temperatura y Precipitación
    q1_t, q2_t, q3_t = df["temperatura_c"].quantile([0.25, 0.50, 0.75])
    q1_p, q2_p, q3_p = df["precipitacion_mensual_mm"].quantile([0.25, 0.50, 0.75])
    
    def cat_cuartiles(val, q1, q2, q3):
        if val <= q1:
            return "Relativamente Baja"
        elif val <= q2:
            return "Media-Baja"
        elif val <= q3:
            return "Media-Alta"
        else:
            return "Alta"
            
    df["cat_temperatura"] = df["temperatura_c"].apply(lambda x: cat_cuartiles(x, q1_t, q2_t, q3_t))
    df["cat_precipitacion"] = df["precipitacion_mensual_mm"].apply(lambda x: cat_cuartiles(x, q1_p, q2_p, q3_p))
    
    # Tabla de frecuencias por país para temperatura
    freq_temp = pd.crosstab(df["pais"], df["cat_temperatura"], normalize="index") * 100
    ruta_cuartiles = config.OUTPUT_DIR / "actividad_9_cuartiles_temperatura_pais.csv"
    freq_temp.round(2).to_csv(ruta_cuartiles)
    print(f"\n[Actividad 9] Tabla de cuartiles por país guardada en: {ruta_cuartiles}")
    print(freq_temp.round(2))
    
    # --------------------------------------------------------------------------
    # ACTIVIDAD 10 & FIGURA OBLIGATORIA 5: Escala Beaufort y Barras Apiladas (100%)
    # --------------------------------------------------------------------------
    df["categoria_beaufort"] = df["velocidad_viento_ms"].apply(config.clasificar_beaufort)
    
    orden_beaufort = ["Calma", "Ventolina", "Brisa ligera", "Brisa suave", "Brisa moderada", "Brisa fresca", "Brisa fuerte"]
    
    # Cruzar con país (frecuencia relativa 100%)
    ct_beaufort = pd.crosstab(df["pais"], df["categoria_beaufort"], normalize="index") * 100
    columnas_presentes = [c for c in orden_beaufort if c in ct_beaufort.columns]
    ct_beaufort = ct_beaufort[columnas_presentes]
    
    ruta_beaufort = config.OUTPUT_DIR / "actividad_10_escala_beaufort_pais.csv"
    ct_beaufort.round(2).to_csv(ruta_beaufort)
    print(f"\n[Actividad 10] Clasificación Beaufort guardada en: {ruta_beaufort}")
    
    fig, ax = plt.subplots(figsize=(11, 6))
    
    ct_beaufort.plot(
        kind="bar",
        stacked=True,
        colormap="viridis",
        ax=ax,
        edgecolor="black",
        linewidth=0.5
    )
    
    ax.set_title("Figura 5: Distribución Proporcional (100%) de la Velocidad del Viento según Escala Beaufort")
    ax.set_xlabel("País")
    ax.set_ylabel("Porcentaje (%)")
    ax.legend(title="Categoría Beaufort", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=0)
    
    fig.text(0.12, 0.01, "Fuente: ERA5-Land, Copernicus Climate Change Service. Clasificación según Escala Beaufort en m/s.", fontsize=8, color="gray")
    
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    ruta_fig5 = config.FIGURES_DIR / "fig5_beaufort_apiladas.png"
    plt.savefig(ruta_fig5, dpi=300)
    plt.close()
    print(f"[Figura Obligatoria 5] Guardada en: {ruta_fig5}")
    
    # --------------------------------------------------------------------------
    # ACTIVIDAD 12 & FIGURA OBLIGATORIA 6: Mapa Climático Regional
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 8))
    
    scatter = ax.scatter(
        df_coords["longitude"],
        df_coords["latitude"],
        c=df_coords["temperatura_c"],
        cmap="coolwarm",
        s=30,
        alpha=0.8,
        edgecolors="none"
    )
    
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.7)
    cbar.set_label("Temperatura Promedio (°C)")
    
    ax.set_title("Figura 6: Mapa Climático Regional – Temperatura Promedio 2020–2025 en Centroamérica")
    ax.set_xlabel("Longitud (°)")
    ax.set_ylabel("Latitud (°)")
    
    fig.text(0.12, 0.01, "Fuente: ERA5-Land, Copernicus Climate Change Service. Promedio multianual 2020–2025 por coordenada.", fontsize=8, color="gray")
    
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    ruta_fig6 = config.FIGURES_DIR / "fig6_mapa_climatico.png"
    plt.savefig(ruta_fig6, dpi=300)
    plt.close()
    print(f"[Actividad 12 & Fig 6] Mapa guardado en: {ruta_fig6}")

if __name__ == "__main__":
    main()
