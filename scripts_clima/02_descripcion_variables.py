import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import config

def main():
    print("=== EJECUTANDO 02_DESCRIPCION_VARIABLES.PY (ACTIVIDADES 3, 4 Y 5) ===")
    config.apply_custom_style()
    
    # 1. Cargar dataset
    df = pd.read_csv(config.CLIMA_CSV_PATH)
    
    variables_climaticas = [
        "temperatura_c",
        "precipitacion_mensual_mm",
        "humedad_suelo",
        "radiacion_mj_m2_dia",
        "velocidad_viento_ms"
    ]
    
    # Actividad 3: Tabla Sintética Descriptiva
    stats_list = []
    for var in variables_climaticas:
        series = df[var]
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        
        stats_list.append({
            "Variable": var,
            "Media": round(series.mean(), 2),
            "Mediana": round(series.median(), 2),
            "Desv_Estandar": round(series.std(), 2),
            "Q1": round(q1, 2),
            "Q3": round(q3, 2),
            "IQR": round(iqr, 2),
            "Minimo": round(series.min(), 2),
            "Maximo": round(series.max(), 2)
        })
        
    df_sintetica = pd.DataFrame(stats_list)
    ruta_sintetica = config.OUTPUT_DIR / "actividad_3_tabla_sintetica.csv"
    df_sintetica.to_csv(ruta_sintetica, index=False)
    print(f"[Actividad 3] Tabla sintética guardada en: {ruta_sintetica}")
    print(df_sintetica.to_string(index=False))
    
    # Actividad 5: Identificación de Atípicos (IQR)
    atipicos_list = []
    for var in variables_climaticas:
        series = df[var]
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        mask_outliers = (series < lower_bound) | (series > upper_bound)
        count_outliers = mask_outliers.sum()
        pct_outliers = (count_outliers / len(df)) * 100
        
        atipicos_list.append({
            "Variable": var,
            "Limite_Inferior_IQR": round(lower_bound, 2),
            "Limite_Superior_IQR": round(upper_bound, 2),
            "Cantidad_Atipicos": count_outliers,
            "Porcentaje_Atipicos": round(pct_outliers, 2)
        })
        
    df_atipicos = pd.DataFrame(atipicos_list)
    ruta_atipicos = config.OUTPUT_DIR / "actividad_5_analisis_atipicos.csv"
    df_atipicos.to_csv(ruta_atipicos, index=False)
    print(f"\n[Actividad 5] Análisis de atípicos guardado en: {ruta_atipicos}")
    print(df_atipicos.to_string(index=False))
    
    # Figura Obligatoria 1: Histograma de Distribución
    fig, ax = plt.subplots(figsize=(11, 6.5))
    
    # Histograma con KDE para temperatura
    sns.histplot(
        df["temperatura_c"],
        bins=35,
        kde=True,
        color="#008080",
        edgecolor="black",
        alpha=0.6,
        ax=ax
    )
    
    # Indicadores de Media y Mediana
    mean_temp = df["temperatura_c"].mean()
    median_temp = df["temperatura_c"].median()
    
    ax.axvline(mean_temp, color="#d62728", linestyle="--", linewidth=2, label=f"Media ({mean_temp:.2f} °C)")
    ax.axvline(median_temp, color="#2ca02c", linestyle="-.", linewidth=2, label=f"Mediana ({median_temp:.2f} °C)")
    
    ax.set_title("Figura 1: Distribución Regional de la Temperatura Media Mensual\nen Centroamérica (2020–2025)", pad=15)
    ax.set_xlabel("Temperatura (°C)")
    ax.set_ylabel("Frecuencia (Número de Observaciones)")
    ax.legend(title="Medidas Centrales", loc="upper left")
    
    # Nota de Fuente
    fig.text(0.12, 0.02, "Fuente: ERA5-Land, Copernicus Climate Change Service. Procesamiento propio.", fontsize=8, color="gray")
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    ruta_fig1 = config.FIGURES_DIR / "fig1_histograma_distribucion.png"
    plt.savefig(ruta_fig1, dpi=300)
    plt.close()
    print(f"\n[Figura Obligatoria 1] Guardada en: {ruta_fig1}")

if __name__ == "__main__":
    main()
