"""Ejecuta el ETL completo.

    python pipeline.py              # extrae ofertas nuevas + transforma + carga
    python pipeline.py --sin-extraer   # solo re-procesa los datos crudos ya descargados
"""
import argparse
import json

from observatorio.extract import RAW, extraer
from observatorio.load import cargar
from observatorio.transform import transformar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sin-extraer", action="store_true")
    ap.add_argument("--paginas", type=int, default=2)
    a = ap.parse_args()
    crudo = json.loads(RAW.read_text(encoding="utf-8")) if a.sin_extraer else extraer(a.paginas)
    ofertas, puente = transformar(crudo)
    cargar(ofertas, puente)


if __name__ == "__main__":
    main()
