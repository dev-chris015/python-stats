import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Importar configuración del proyecto
import config

def limpiar_gasto(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y repara el DataFrame de Ground Truth (gasto), corrigiendo
    filas corruptas con valores concatenados por comas.
    """
    # Separar filas válidas y mal formateadas
    valid_mask = pd.to_numeric(df_raw["hhid"], errors="coerce").notna()
    df_valid = df_raw[valid_mask].copy()
    df_valid["survey_id"] = df_valid["survey_id"].astype(int)
    df_valid["hhid"] = df_valid["hhid"].astype(int)
    df_valid["cons_ppp17"] = df_valid["cons_ppp17"].astype(float)

    # Reparar filas corruptas
    df_corrupt = df_raw[~valid_mask].copy()
    repaired_rows = []
    for _, row in df_corrupt.iterrows():
        parts = str(row["survey_id"]).split(",")
        if len(parts) == 5:
            s_id = int(parts[0] + parts[1])
            h_id = int(parts[2] + parts[3])
            c_val = float(parts[4])
            repaired_rows.append(
                {"survey_id": s_id, "hhid": h_id, "cons_ppp17": c_val}
            )

    df_repaired = pd.DataFrame(repaired_rows)
    
    # Combinar y ordenar
    df_clean = pd.concat([df_valid, df_repaired], ignore_index=True)
    df_clean.sort_values(by=["survey_id", "hhid"], inplace=True)
    df_clean.reset_index(drop=True, inplace=True)
    
    return df_clean

def main():
    print("=== INICIANDO SECCIÓN A: LIMPIEZA Y FRECUENCIAS ===")
    
    # 1. Rutas de archivos
    ruta_features = config.DATA_DIR / "train_hh_features.csv"
    ruta_gasto = config.DATA_DIR / "train_hh_gt.csv"
    
    # Cargar datasets iniciales
    df_feat_raw = pd.read_csv(ruta_features)
    df_gasto_raw = pd.read_csv(ruta_gasto, sep=";")
    
    # Reportar dimensiones iniciales
    n_feat_init, k_feat_init = df_feat_raw.shape
    n_gasto_init, k_gasto_init = df_gasto_raw.shape
    print(f"Dimensiones iniciales:")
    print(f"  - Características (Features): {n_feat_init} filas x {k_feat_init} columnas")
    print(f"  - Gasto (Ground Truth): {n_gasto_init} filas x {k_gasto_init} columnas")
    
    # 2. Limpiar y reparar Ground Truth
    df_gasto_clean = limpiar_gasto(df_gasto_raw)
    
    # Fusionar datasets
    df_merged = pd.merge(df_feat_raw, df_gasto_clean, on=["survey_id", "hhid"], how="inner")
    n_merged, k_merged = df_merged.shape
    print(f"Dimensiones del dataset fusionado inicial: {n_merged} filas x {k_merged} columnas")
    
    # 3. Cuantificación de valores faltantes
    # Calcular porcentaje de nans global y por país (survey_id)
    countries = sorted(df_merged["survey_id"].unique())
    
    missing_data = []
    for col in df_merged.columns:
        if col in ["survey_id", "hhid"]:
            continue
            
        pct_global = df_merged[col].isna().mean()
        row_dict = {"variable": col, "global_nan_pct": pct_global * 100}
        
        # Por país
        for country in countries:
            pct_country = df_merged[df_merged["survey_id"] == country][col].isna().mean()
            row_dict[f"nan_pct_{country}"] = pct_country * 100
            
        # Determinar estado según umbrales de config
        if pct_global > config.THRESHOLD_CRITICAL_EXCLUSION:
            row_dict["estado"] = f"Exclusión (>{config.THRESHOLD_CRITICAL_EXCLUSION * 100:.0f}%)"
        elif pct_global > config.THRESHOLD_ALERT_IMPUTATION:
            row_dict["estado"] = f"Alerta/Imputación (>{config.THRESHOLD_ALERT_IMPUTATION * 100:.0f}%)"
        else:
            row_dict["estado"] = "Normal"
            
        missing_data.append(row_dict)
        
    df_missing = pd.DataFrame(missing_data)
    
    # 4. Filtrado contra umbral del 10% para columnas
    cols_to_exclude = df_missing[df_missing["estado"].str.startswith("Exclusión")]["variable"].tolist()
    print(f"Columnas excluidas por superar el umbral del {config.THRESHOLD_CRITICAL_EXCLUSION * 100:.0f}%:")
    for col in cols_to_exclude:
        pct = df_missing[df_missing["variable"] == col]["global_nan_pct"].values[0]
        print(f"  - {col}: {pct:.2f}% de datos faltantes")
        
    # Dropear columnas excluidas
    df_filtered_cols = df_merged.drop(columns=cols_to_exclude)
    
    # 5. Filtrado de filas con valores faltantes en las columnas restantes
    df_clean_final = df_filtered_cols.dropna()
    n_final, k_final = df_clean_final.shape
    print(f"Dimensiones finales tras limpieza de filas:")
    print(f"  - Dataset limpio final: {n_final} filas x {k_final} columnas")
    
    # Exportar dataset limpio completo para uso de siguientes scripts
    ruta_clean_dataset = config.DATA_DIR / "train_hh_completo_clean.csv"
    df_clean_final.to_csv(ruta_clean_dataset, index=False)
    print(f"-> Dataset limpio exportado a: {ruta_clean_dataset.name}")
    
    # 6. Tabla de frecuencias por país (sobre el dataset limpio final)
    frecuencias = df_clean_final["survey_id"].value_counts().sort_index()
    porcentajes = df_clean_final["survey_id"].value_counts(normalize=True).sort_index() * 100
    
    df_frecuencias = pd.DataFrame({
        "survey_id": frecuencias.index,
        "frecuencia_absoluta": frecuencias.values,
        "frecuencia_relativa_porcentaje": porcentajes.values.round(2)
    })
    
    print("\nTabla de Frecuencias Final por País:")
    print(df_frecuencias.to_string(index=False))
    
    # 7. Exportación de ficha metodológica y tablas a output/frecuencias_pais.csv
    ruta_salida = config.OUTPUT_DIR / "frecuencias_pais.csv"
    
    with open(ruta_salida, "w", encoding="utf-8") as f:
        # Ficha Metodológica con bordes Unicode elegantes
        f.write("# ╔══════════════════════════════════════════════════════════════════════════════════╗\n")
        f.write("# ║                   FICHA METODOLÓGICA DE LIMPIEZA Y PROCESAMIENTO                   ║\n")
        f.write("# ╠══════════════════════════════════════════════════════════════════════════════════╣\n")
        f.write(f"# ║  • Fecha de Ejecución:                           {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<31} ║\n")
        f.write(f"# ║  • Dimensiones Iniciales (Features):             {f'{n_feat_init} filas x {k_feat_init} cols':<31} ║\n")
        f.write(f"# ║  • Dimensiones Iniciales (Ground Truth):         {f'{n_gasto_init} filas x {k_gasto_init} cols':<31} ║\n")
        f.write(f"# ║  • Dataset Fusionado (Inicial):                  {f'{n_merged} filas x {k_merged} cols':<31} ║\n")
        f.write(f"# ║  • Dataset Fusionado (Final Limpio):             {f'{n_final} filas x {k_final} cols':<31} ║\n")
        f.write(f"# ║  • Umbral de Alerta / Imputación:                {f'{config.THRESHOLD_ALERT_IMPUTATION * 100:.1f}%':<31} ║\n")
        f.write(f"# ║  • Umbral de Exclusión Crítica:                  {f'{config.THRESHOLD_CRITICAL_EXCLUSION * 100:.1f}%':<31} ║\n")
        f.write(f"# ║  • Variable(s) Excluidas (>10% NaNs):            {f'{", ".join(cols_to_exclude) if cols_to_exclude else "Ninguna"}':<31} ║\n")
        f.write("# ╚══════════════════════════════════════════════════════════════════════════════════╝\n#\n")
        
        # Tabla 1: Frecuencias
        f.write("# ┌──────────────────────────────────────────────────────────────────────────────────┐\n")
        f.write("# │ TABLA 1: FRECUENCIAS ABSOLUTAS Y RELATIVAS POR PAÍS (SURVEY_ID)                  │\n")
        f.write("# └──────────────────────────────────────────────────────────────────────────────────┘\n")
        df_frecuencias.to_csv(f, index=False)
        
        # Tabla 2: Cuantificación de Nans
        f.write("\n# ┌──────────────────────────────────────────────────────────────────────────────────┐\n")
        f.write("# │ TABLA 2: CUANTIFICACIÓN DE VALORES FALTANTES Y EVALUACIÓN DE UMBRALES            │\n")
        f.write("# └──────────────────────────────────────────────────────────────────────────────────┘\n")
        
        # Filtrar variables que tenían nans para no inundar el archivo
        df_missing_nans = df_missing[df_missing["global_nan_pct"] > 0].sort_values(by="global_nan_pct", ascending=False)
        
        # Formatear columnas de porcentajes a 4 decimales
        cols_pct = ["global_nan_pct"] + [f"nan_pct_{c}" for c in countries]
        for col_pct in cols_pct:
            df_missing_nans[col_pct] = df_missing_nans[col_pct].round(4)
            
        df_missing_nans.to_csv(f, index=False)
        
    print(f"\n-> Ficha metodológica y tablas exportadas exitosamente a: {ruta_salida.name}")
    print("=== SECCIÓN A COMPLETADA CON ÉXITO ===\n")

if __name__ == "__main__":
    main()
