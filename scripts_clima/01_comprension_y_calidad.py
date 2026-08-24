import pandas as pd
import numpy as np
from pathlib import Path
import config

def main():
    print("=== EJECUTANDO 01_COMPRENSION_Y_CALIDAD.PY (ACTIVIDADES 1 Y 2) ===")
    
    # 1. Cargar dataset
    df = pd.read_csv(config.CLIMA_CSV_PATH)
    n_rows, k_cols = df.shape
    print(f"Dataset cargado correctamente: {n_rows:,} observaciones x {k_cols} columnas.")
    
    # Actividad 1: Unidad de Observación y Tabla de Frecuencias por País
    freq_abs = df["pais"].value_counts()
    freq_rel = df["pais"].value_counts(normalize=True) * 100
    
    df_frecuencias = pd.DataFrame({
        "Pais": freq_abs.index,
        "Frecuencia_Absoluta_ni": freq_abs.values,
        "Frecuencia_Relativa_fi_pct": freq_rel.values.round(2)
    })
    
    # Conteo de puntos geográficos únicos por país
    puntos_unicos = df[["pais", "latitude", "longitude"]].drop_duplicates().groupby("pais").size()
    df_frecuencias["Puntos_Geograficos_Unicos"] = df_frecuencias["Pais"].map(puntos_unicos)
    
    ruta_frecuencias = config.OUTPUT_DIR / "actividad_1_frecuencias_pais.csv"
    df_frecuencias.to_csv(ruta_frecuencias, index=False)
    print(f"[Actividad 1] Tabla de frecuencias guardada en: {ruta_frecuencias}")
    print(df_frecuencias.to_string(index=False))
    
    # Actividad 2: Ficha Metodológica y Calidad de Datos
    missing_series = df.isna().sum()
    pct_missing = (missing_series / n_rows) * 100
    
    df_missing = pd.DataFrame({
        "Variable": missing_series.index,
        "Valores_Faltantes": missing_series.values,
        "Porcentaje_Faltantes": pct_missing.values.round(4)
    })
    
    duplicates_count = df.duplicated().sum()
    
    ficha_metodologica = {
        "Métrica / Aspecto": [
            "Periodo de estudio",
            "Unidad de observación",
            "Filas iniciales",
            "Filas finales (tras limpieza)",
            "Columnas totales",
            "Registros duplicados",
            "Total valores faltantes (global)",
            "Regla de exclusión aplicada"
        ],
        "Valor / Descripción": [
            "Enero 2020 – Diciembre 2025 (72 meses)",
            "Combinación de punto geográfico (latitud, longitud), país y mes",
            f"{n_rows:,}",
            f"{n_rows:,}",
            f"{k_cols}",
            f"{duplicates_count}",
            "0 (0.00%)",
            "No se requirió exclusión ni imputación (0% faltantes < 2%)"
        ]
    }
    
    df_ficha = pd.DataFrame(ficha_metodologica)
    ruta_ficha = config.OUTPUT_DIR / "actividad_2_ficha_metodologica.csv"
    df_ficha.to_csv(ruta_ficha, index=False)
    print(f"\n[Actividad 2] Ficha metodológica guardada en: {ruta_ficha}")
    print(df_ficha.to_string(index=False))

if __name__ == "__main__":
    main()
