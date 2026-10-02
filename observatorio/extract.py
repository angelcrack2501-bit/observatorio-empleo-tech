"""E de ETL: descarga ofertas públicas de Computrabajo Colombia.

Solo lee páginas públicas (sin iniciar sesión), con pausas entre peticiones para no
sobrecargar el sitio. Guarda el HTML ya reducido a texto en data/raw/ofertas.json,
acumulando entre ejecuciones (una oferta se identifica por el código al final de su URL).
"""
import html
import json
import re
import time
import urllib.request
from datetime import date
from pathlib import Path

BASE = "https://co.computrabajo.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "ofertas.json"

# búsqueda pública -> categoría con la que se etiqueta la oferta
BUSQUEDAS = {
    "trabajo-de-desarrollador-junior": "software",
    "trabajo-de-desarrollador-remoto": "software",
    "trabajo-de-programador": "software",
    "trabajo-de-desarrollador-full-stack": "software",
    "trabajo-de-desarrollador-backend": "software",
    "trabajo-de-desarrollador-frontend": "software",
    "trabajo-de-analista-de-datos": "datos",
    "trabajo-de-ingeniero-de-datos": "datos",
    "trabajo-de-cientifico-de-datos": "datos",
    "trabajo-de-analista-bi": "datos",
    "trabajo-de-inteligencia-artificial": "ia",
    "trabajo-de-machine-learning": "ia",
    "trabajo-de-desarrollador-ia": "ia",
    "trabajo-de-automatizacion-rpa": "automatizacion",
    "trabajo-de-tester-qa": "qa",
    "trabajo-de-soporte-tecnico": "soporte",
}


def get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es-CO"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def a_texto(fragmento: str) -> str:
    t = re.sub(r"<br\s*/?>|</p>|</li>|</span>", "\n", fragmento)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", t)).strip()


def enlaces(slug: str, pagina: int) -> list[str]:
    url = f"{BASE}/{slug}" + (f"?p={pagina}" if pagina > 1 else "")
    return [h.split("#")[0] for h in re.findall(r'class="js-o-link[^"]*" href="([^"]+)"', get(url))]


def detalle(path: str) -> dict:
    s = get(BASE + path)
    cab = re.search(r"<h1[^>]*>(.*?)</h1>\s*<p[^>]*>(.*?)</p>", s, re.S)
    i = s.find("Descripción de la oferta")
    j = s.find("Palabras clave", i)
    return {
        "titulo": a_texto(cab.group(1)) if cab else "",
        "empresa_lugar": a_texto(cab.group(2)) if cab else "",
        "descripcion": a_texto(s[i:(j if j > 0 else i + 15000)]) if i > 0 else "",
    }


def extraer(paginas: int = 2, pausa: float = 1.0) -> dict:
    """Recorre las búsquedas y devuelve el diccionario acumulado {id: oferta}."""
    datos = json.loads(RAW.read_text(encoding="utf-8")) if RAW.exists() else {}
    nuevas = 0
    for slug, categoria in BUSQUEDAS.items():
        for p in range(1, paginas + 1):
            try:
                paths = enlaces(slug, p)
            except OSError as e:
                print(f"! {slug} p{p}: {e}")
                break
            for path in paths:
                oid = path.rsplit("-", 1)[-1]
                if oid in datos:
                    if categoria not in datos[oid]["categorias"]:
                        datos[oid]["categorias"].append(categoria)
                    continue
                try:
                    o = detalle(path)
                except OSError as e:
                    print(f"! {path}: {e}")
                    continue
                o.update(id=oid, url=BASE + path, categorias=[categoria], visto=date.today().isoformat())
                datos[oid] = o
                nuevas += 1
                time.sleep(pausa)
        print(f"{slug}: ok")
    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{nuevas} ofertas nuevas, {len(datos)} en total")
    return datos
