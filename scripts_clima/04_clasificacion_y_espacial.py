import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
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
    
    # Figura Obligatoria 4: Diagrama de Dispersión Climatológico
    # Promediar 2020-2025 por punto geográfico (lat, lon, pais)
    df_coords = df.groupby(["pais", "latitude", "longitude"])[["temperatura_c", "precipitacion_mensual_mm"]].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(11, 6.5))
    
    sns.scatterplot(
        data=df_coords,
        x="temperatura_c",
        y="precipitacion_mensual_mm",
        hue="pais",
        palette=config.PAIS_COLORS,
        alpha=0.65,
        edgecolor="white",
        linewidth=0.3,
        s=40,
        ax=ax
    )
    
    # Cuadro explicativo de la diferencia entre el máximo mensual bruto y el promedio por coordenada
    max_coord_p = df_coords["precipitacion_mensual_mm"].max()
    max_raw_p = df["precipitacion_mensual_mm"].max()
    min_raw_p = df["precipitacion_mensual_mm"].min()
    
    aclaracion_text = (
        f"Aclaración Metodológica de Valores Máximos:\n"
        f"• Máx. en este gráfico (Promedio 2020–2025 por coordenada): {max_coord_p:.2f} mm/mes\n"
        f"• Máx. mensual bruto puntual (Serie completa 304,272 obs.): {max_raw_p:.2f} mm\n"
        f"• Mín. mensual bruto: {min_raw_p:.2f} mm | Rango mensual bruto: {max_raw_p - min_raw_p:.2f} mm\n"
        f"El promediado multianual suaviza los eventos extremos mensuales puntuales."
    )
    ax.text(
        0.03, 0.95, aclaracion_text,
        transform=ax.transAxes,
        fontsize=8.5,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.92, edgecolor="#008080")
    )
    
    ax.set_title("Figura 4: Diagrama de Dispersión Climatológico – Precipitación Promedio vs. Temperatura Promedio\n(Promedios Multianuales 2020–2025 por Coordenada Geográfica, N = 4,226 puntos)", pad=15)
    ax.set_xlabel("Temperatura Promedio (°C)")
    ax.set_ylabel("Precipitación Mensual Promedio (mm)")
    ax.legend(title="País", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.4)
    
    fig.text(0.06, 0.015, "Fuente: ERA5-Land, Copernicus Climate Change Service. Procesamiento propio. Promedios 2020–2025 por coordenada.", fontsize=8, color="gray")
    
    plt.tight_layout(rect=[0, 0.04, 1, 0.96])
    ruta_fig4 = config.FIGURES_DIR / "fig4_dispersion_geografica.png"
    plt.savefig(ruta_fig4, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[Actividad 8 & Fig 4] Guardada en: {ruta_fig4}")
    
    # Actividad 9: Categorización por Cuartiles Regionales
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
    
    orden_cat = ["Relativamente Baja", "Media-Baja", "Media-Alta", "Alta"]
    
    freq_temp = pd.crosstab(df["pais"], df["cat_temperatura"], normalize="index") * 100
    freq_temp = freq_temp.reindex(columns=orden_cat).round(2)
    freq_temp.insert(0, "Variable", "temperatura_c")

    freq_precip = pd.crosstab(df["pais"], df["cat_precipitacion"], normalize="index") * 100
    freq_precip = freq_precip.reindex(columns=orden_cat).round(2)
    freq_precip.insert(0, "Variable", "precipitacion_mensual_mm")

    freq_combinada = pd.concat([freq_temp, freq_precip]).reset_index()
    ruta_cuartiles_comb = config.OUTPUT_DIR / "actividad_9_cuartiles_regional_pais.csv"
    freq_combinada.to_csv(ruta_cuartiles_comb, index=False)
    print(f"\n[Actividad 9] Tabla consolidada de cuartiles por país guardada en: {ruta_cuartiles_comb}")
    
    # Actividad 10 & Figura Obligatoria 5: Escala Beaufort y Barras Apiladas (100%)
    df["categoria_beaufort"] = df["velocidad_viento_ms"].apply(config.clasificar_beaufort)
    
    orden_beaufort = ["Calma", "Ventolina", "Brisa ligera", "Brisa suave", "Brisa moderada", "Brisa fresca", "Brisa fuerte"]
    
    ct_beaufort = pd.crosstab(df["pais"], df["categoria_beaufort"], normalize="index") * 100
    columnas_presentes = [c for c in orden_beaufort if c in ct_beaufort.columns]
    ct_beaufort = ct_beaufort[columnas_presentes]
    
    ruta_beaufort = config.OUTPUT_DIR / "actividad_10_escala_beaufort_pais.csv"
    ct_beaufort.round(2).to_csv(ruta_beaufort)
    print(f"[Actividad 10] Clasificación Beaufort guardada en: {ruta_beaufort}")
    
    fig, ax = plt.subplots(figsize=(11, 6.5))
    
    colors_beaufort = ["#e0f3f8", "#91bfdb", "#4575b4", "#fee090", "#fc8d59", "#d73027", "#800026"]
    colors_used = colors_beaufort[:len(columnas_presentes)]
    
    bars = ct_beaufort.plot(
        kind="bar",
        stacked=True,
        color=colors_used,
        ax=ax,
        edgecolor="black",
        linewidth=0.5
    )
    
    # Agregar etiquetas porcentuales en segmentos significativos (> 4%)
    for container in ax.containers:
        labels = [f"{v.get_height():.1f}%" if v.get_height() >= 4.0 else "" for v in container]
        ax.bar_label(container, labels=labels, label_type="center", fontsize=7.5, color="black", weight="bold")
    
    ax.set_title("Figura 5: Distribución Proporcional (100%) de la Velocidad del Viento según Escala Beaufort por País", pad=15)
    ax.set_xlabel("País")
    ax.set_ylabel("Porcentaje (%)")
    ax.set_ylim(0, 100)
    ax.legend(title="Categoría Beaufort", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)
    plt.xticks(rotation=0)
    
    fig.text(0.06, 0.015, "Fuente: ERA5-Land, Copernicus Climate Change Service. Clasificación de la velocidad del viento a 10 m en m/s.", fontsize=8, color="gray")
    
    plt.tight_layout(rect=[0, 0.04, 1, 0.96])
    ruta_fig5 = config.FIGURES_DIR / "fig5_beaufort_apiladas.png"
    plt.savefig(ruta_fig5, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[Figura Obligatoria 5] Guardada en: {ruta_fig5}")
    
    # Actividad 12 & Figura Obligatoria 6: Mapa Climático Regional
    fig, ax = plt.subplots(figsize=(11, 7.5))
    
    scatter = ax.scatter(
        df_coords["longitude"],
        df_coords["latitude"],
        c=df_coords["temperatura_c"],
        cmap="coolwarm",
        s=35,
        alpha=0.85,
        edgecolors="none"
    )
    
    # Mantener relación de aspecto geográfica real
    ax.set_aspect("equal")
    
    # Anotar nombres de países en sus centros aproximados
    country_centroids = df_coords.groupby("pais")[["longitude", "latitude"]].mean()
    for pais, row in country_centroids.iterrows():
        ax.text(
            row["longitude"], row["latitude"], str(pais),
            fontsize=9, fontweight="bold", color="black",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7, edgecolor="none")
        )
    
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label("Temperatura Promedio (°C)", fontsize=10, fontweight="bold")
    
    ax.set_title("Figura 6: Mapa Climático Regional – Temperatura Promedio Multianual (2020–2025) en Centroamérica", pad=15)
    ax.set_xlabel("Longitud (°W)")
    ax.set_ylabel("Latitud (°N)")
    ax.grid(True, linestyle="--", alpha=0.3)
    
    fig.text(0.06, 0.015, "Fuente: ERA5-Land, Copernicus Climate Change Service. Promedio multianual 2020–2025 por coordenada (N = 4,226 puntos).", fontsize=8, color="gray")
    
    plt.tight_layout(rect=[0, 0.04, 1, 0.96])
    ruta_fig6 = config.FIGURES_DIR / "fig6_mapa_climatico.png"
    plt.savefig(ruta_fig6, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[Actividad 12 & Fig 6] Mapa guardado en: {ruta_fig6}")


if __name__ == "__main__":
    main()
