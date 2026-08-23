# modulos
import pandas as pd
import geopandas as gpd
# pyrefly: ignore [missing-import]
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
from pathlib import Path

# rutas
BASE_DIR = Path(__file__).resolve().parent
FEATURES_CSV = BASE_DIR / "train_hh_features.csv"
GT_CSV = BASE_DIR / "train_hh_gt.csv"

# Archivos de salida
GT_CLEAN_CSV = BASE_DIR / "train_hh_gt_clean.csv"
MERGED_CSV = BASE_DIR / "train_hh_completo.csv"
RESUMEN_ZONA_CSV = BASE_DIR / "resumen_por_zona.csv"
RESUMEN_EDUCACION_CSV = BASE_DIR / "resumen_por_educacion.csv"
RESUMEN_ESTADISTICO_CSV = BASE_DIR / "resumen_estadistico.csv"


def cargar_y_limpiar_gt(ruta_gt: Path) -> pd.DataFrame:
    """Carga y corrige filas corruptas en el CSV de ground truth (train_hh_gt.csv)."""
    print(f"Cargando ground truth desde: {ruta_gt.name}")
    df_raw = pd.read_csv(ruta_gt, sep=";")

    # Separar filas válidas y filas mal formateadas con comas (88 filas con valores concatenados)
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
    df_clean = pd.concat([df_valid, df_repaired], ignore_index=True)
    df_clean.sort_values(by=["survey_id", "hhid"], inplace=True)
    df_clean.reset_index(drop=True, inplace=True)

    print(
        f"  - Filas válidas: {len(df_valid)}, Filas reparadas: {len(df_repaired)}"
    )
    print(f"  - Total Ground Truth limpio: {len(df_clean)} registros.")
    return df_clean


def main():
    print("=== INICIANDO PROCESAMIENTO Y EXPORTACIÓN DE CSVS ===\n")

    # 1. Cargar datos de características
    print(f"Cargando características desde: {FEATURES_CSV.name}")
    df_feat = pd.read_csv(FEATURES_CSV)
    print(f"  - Características cargadas: {df_feat.shape[0]} filas, {df_feat.shape[1]} columnas.")

    # 2. Cargar y limpiar ground truth
    df_gt = cargar_y_limpiar_gt(GT_CSV)

    # Exportar CSV de GT limpio
    df_gt.to_csv(GT_CLEAN_CSV, index=False, sep=";")
    print(f"-> Exportado CSV limpio GT: {GT_CLEAN_CSV.name}")

    # 3. Fusionar datasets (inner join por survey_id y hhid)
    print("\nFusionando características y ground truth...")
    df_merged = pd.merge(df_feat, df_gt, on=["survey_id", "hhid"], how="inner")
    print(f"  - Dataset fusionado: {df_merged.shape[0]} filas, {df_merged.shape[1]} columnas.")

    # Exportar el dataset completo fusionado
    df_merged.to_csv(MERGED_CSV, index=False)
    print(f"-> Exportado CSV fusionado completo: {MERGED_CSV.name}")

    # 4. Generar y exportar resúmenes estadísticos
    print("\nGenerando resúmenes estadísticos agrupados...")

    # Resumen por Zona (Urban / Rural)
    resumen_zona = df_merged.groupby("urban").agg(
        total_hogares=("hhid", "count"),
        consumo_promedio=("cons_ppp17", "mean"),
        consumo_mediana=("cons_ppp17", "median"),
        tamano_hogar_promedio=("hsize", "mean"),
        gasto_servicios_promedio=("utl_exp_ppp17", "mean")
    ).reset_index()
    resumen_zona.to_csv(RESUMEN_ZONA_CSV, index=False)
    print(f"-> Exportado resumen por zona: {RESUMEN_ZONA_CSV.name}")

    # Resumen por Nivel Educativo Máximo
    resumen_educacion = df_merged.groupby("educ_max", dropna=False).agg(
        total_hogares=("hhid", "count"),
        consumo_promedio=("cons_ppp17", "mean"),
        consumo_mediana=("cons_ppp17", "median"),
        tamano_hogar_promedio=("hsize", "mean")
    ).reset_index()
    resumen_educacion.to_csv(RESUMEN_EDUCACION_CSV, index=False)
    print(f"-> Exportado resumen por educación: {RESUMEN_EDUCACION_CSV.name}")

    # Resumen Estadístico General de Columnas Numéricas Clave
    cols_num = ["cons_ppp17", "utl_exp_ppp17", "hsize", "age", "num_children5", "weight"]
    resumen_general = df_merged[cols_num].describe().T.reset_index().rename(columns={"index": "variable"})
    resumen_general.to_csv(RESUMEN_ESTADISTICO_CSV, index=False)
    print(f"-> Exportado resumen estadístico general: {RESUMEN_ESTADISTICO_CSV.name}")

    print("\n=== EXPORTACIÓN FINALIZADA CON ÉXITO ===")


if __name__ == "__main__":
    main()



