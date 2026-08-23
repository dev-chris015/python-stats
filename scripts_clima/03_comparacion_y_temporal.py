import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import config

def main():
    print("=== EJECUTANDO 03_COMPARACION_Y_TEMPORAL.PY (ACTIVIDADES 6 Y 7) ===")
    config.apply_custom_style()
    
    # 1. Cargar dataset
    df = pd.read_csv(config.CLIMA_CSV_PATH)
    
    # --------------------------------------------------------------------------
    # ACTIVIDAD 6: Tabla Comparativa entre Países
    # --------------------------------------------------------------------------
    df_pais_comp = df.groupby("pais").agg(
        Temp_Media_C=("temperatura_c", "mean"),
        Temp_Mediana_C=("temperatura_c", "median"),
        Temp_Std_C=("temperatura_c", "std"),
        Precip_Media_mm=("precipitacion_mensual_mm", "mean"),
        Precip_Mediana_mm=("precipitacion_mensual_mm", "median"),
        Precip_Std_mm=("precipitacion_mensual_mm", "std")
    ).round(2).reset_index()
    
    ruta_comp_pais = config.OUTPUT_DIR / "actividad_6_comparacion_pais.csv"
    df_pais_comp.to_csv(ruta_comp_pais, index=False)
    print(f"[Actividad 6] Tabla comparativa por país guardada en: {ruta_comp_pais}")
    print(df_pais_comp.to_string(index=False))
    
    # --------------------------------------------------------------------------
    # FIGURA OBLIGATORIA 2: Diagrama de Cajas de Precipitación Mensual por País
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 6))
    
    sns.boxplot(
        data=df,
        x="pais",
        y="precipitacion_mensual_mm",
        palette=config.PAIS_COLORS,
        ax=ax,
        fliersize=1.5,
        linewidth=1
    )
    
    ax.set_title("Figura 2: Distribución de la Precipitación Mensual por País en Centroamérica (2020–2025)")
    ax.set_xlabel("País")
    ax.set_ylabel("Precipitación Mensual (mm)")
    
    fig.text(0.12, 0.01, "Fuente: ERA5-Land, Copernicus Climate Change Service. Procesamiento propio. Muestra promedios no ponderados.", fontsize=8, color="gray")
    
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    ruta_fig2 = config.FIGURES_DIR / "fig2_boxplot_precipitacion.png"
    plt.savefig(ruta_fig2, dpi=300)
    plt.close()
    print(f"\n[Figura Obligatoria 2] Guardada en: {ruta_fig2}")
    
    # --------------------------------------------------------------------------
    # ACTIVIDAD 7 & FIGURA OBLIGATORIA 3: Figura Temporal de Dos Paneles
    # --------------------------------------------------------------------------
    # Panel A: Promedio mensual por coordenada -> agregar país y año
    df_panel_a = df.groupby(["pais", "latitude", "longitude", "anio"])["temperatura_c"].mean().reset_index()
    df_panel_a = df_panel_a.groupby(["pais", "anio"])["temperatura_c"].mean().reset_index()
    
    # Panel B: Perfil estacional (Enero a Diciembre)
    # Asegurar orden del mes
    meses_orden = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                   "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    df_panel_b = df.groupby(["pais", "numero_mes", "mes"])["precipitacion_mensual_mm"].mean().reset_index()
    df_panel_b.sort_values(by="numero_mes", inplace=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Graficar Panel A
    for pais, color in config.PAIS_COLORS.items():
        sub_a = df_panel_a[df_panel_a["pais"] == pais]
        ax1.plot(sub_a["anio"], sub_a["temperatura_c"], marker="o", linewidth=2, label=pais, color=color)
        
    ax1.set_title("Panel A: Evolución de la Temperatura Anual por País (2020–2025)")
    ax1.set_xlabel("Año")
    ax1.set_ylabel("Temperatura Media Anual (°C)")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8)
    
    # Graficar Panel B
    for pais, color in config.PAIS_COLORS.items():
        sub_b = df_panel_b[df_panel_b["pais"] == pais]
        ax2.plot(sub_b["numero_mes"], sub_b["precipitacion_mensual_mm"], marker="s", linewidth=2, label=pais, color=color)
        
    ax2.set_title("Panel B: Perfil Estacional Promedio de Precipitación (2020–2025)")
    ax2.set_xlabel("Mes del Calendario")
    ax2.set_ylabel("Precipitación Mensual Promedio (mm)")
    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels(["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"])
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="upper left", fontsize=8)
    
    fig.suptitle("Figura 3: Análisis Temporal y Estacional del Clima en Centroamérica", fontsize=14, fontweight="bold")
    fig.text(0.08, 0.01, "Fuente: ERA5-Land, Copernicus Climate Change Service. Procesamiento propio.", fontsize=8, color="gray")
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    ruta_fig3 = config.FIGURES_DIR / "fig3_temporal_dos_paneles.png"
    plt.savefig(ruta_fig3, dpi=300)
    plt.close()
    print(f"[Figura Obligatoria 3] Guardada en: {ruta_fig3}")

if __name__ == "__main__":
    main()
