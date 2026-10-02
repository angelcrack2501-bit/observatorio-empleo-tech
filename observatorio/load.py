"""L de ETL: guarda las tablas limpias en SQLite y en CSV (el CSV es lo que lee el dashboard en la nube)."""
import sqlite3
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
DB = DATA / "observatorio.db"

ESQUEMA = """
CREATE TABLE IF NOT EXISTS ofertas (
    id TEXT PRIMARY KEY, titulo TEXT, empresa TEXT, ciudad TEXT, departamento TEXT,
    categoria TEXT, es_tech INTEGER, nivel TEXT, modalidad TEXT, contrato TEXT, jornada TEXT,
    salario REAL, experiencia_anios INTEGER, educacion TEXT, url TEXT, fecha TEXT
);
CREATE TABLE IF NOT EXISTS ofertas_habilidades (
    oferta_id TEXT REFERENCES ofertas(id), habilidad TEXT,
    PRIMARY KEY (oferta_id, habilidad)
);
CREATE INDEX IF NOT EXISTS idx_hab ON ofertas_habilidades(habilidad);
"""


def acumular(ofertas: pd.DataFrame, puente: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Une lo nuevo con el histórico de los CSV: así el dataset crece semana a semana
    aunque las ofertas viejas ya no estén publicadas."""
    csv_o, csv_h = DATA / "ofertas.csv", DATA / "ofertas_habilidades.csv"
    if not csv_o.exists():
        return ofertas, puente
    viejas = pd.read_csv(csv_o, parse_dates=["fecha"])
    viejas_h = pd.read_csv(csv_h)
    viejas = viejas[~viejas.id.isin(ofertas.id)]          # la versión nueva de una oferta reemplaza a la vieja
    viejas_h = viejas_h[viejas_h.oferta_id.isin(viejas.id)]
    return (pd.concat([ofertas, viejas], ignore_index=True),
            pd.concat([puente, viejas_h], ignore_index=True))


def cargar(ofertas: pd.DataFrame, puente: pd.DataFrame) -> None:
    DATA.mkdir(exist_ok=True)
    ofertas, puente = acumular(ofertas, puente)
    with sqlite3.connect(DB) as con:
        con.executescript("DROP TABLE IF EXISTS ofertas_habilidades; DROP TABLE IF EXISTS ofertas;" + ESQUEMA)
        o = ofertas.assign(fecha=ofertas["fecha"].dt.strftime("%Y-%m-%d"))
        o.to_sql("ofertas", con, if_exists="append", index=False)
        puente.to_sql("ofertas_habilidades", con, if_exists="append", index=False)
    ofertas.to_csv(DATA / "ofertas.csv", index=False)
    puente.to_csv(DATA / "ofertas_habilidades.csv", index=False)
    print(f"Cargadas {len(ofertas)} ofertas y {len(puente)} relaciones oferta-habilidad en {DB.name}")
