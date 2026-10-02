"""T de ETL: convierte el texto crudo de cada oferta en columnas limpias (pandas).

Cada función `parse_*` recibe texto y devuelve un valor; así se pueden probar una por una
(ver tests/test_transform.py).
"""
import re

import pandas as pd

# Habilidad -> expresión regular que la detecta en el texto (minúsculas).
HABILIDADES = {
    "Python": r"\bpython\b", "SQL": r"\bsql\b|t-sql|pl/sql", "JavaScript": r"\bjavascript\b",
    "TypeScript": r"\btypescript\b", "Java": r"\bjava\b(?!script)", "C#/.NET": r"c#|\.net\b",
    "PHP": r"\bphp\b", "React": r"\breact\b", "Angular": r"\bangular\b", "Node.js": r"\bnode(\.js|js)?\b",
    "HTML/CSS": r"\bhtml\b|\bcss\b", "APIs REST": r"\bapis?\b|\brest(ful)?\b",
    "Excel": r"\bexcel\b", "Power BI": r"power ?bi", "Tableau": r"tableau", "ETL": r"\betl\b",
    "Pandas": r"\bpandas\b", "Estadística": r"estad[ií]stic", "PostgreSQL": r"postgre",
    "MySQL": r"mysql", "SQL Server": r"sql server", "MongoDB": r"mongo",
    "Machine Learning": r"machine learning|aprendizaje autom[aá]tico",
    "IA generativa": r"\bllms?\b|generativ|chatgpt|openai|\bgpt|copilot|langchain|\brag\b",
    "Deep Learning": r"deep learning|tensorflow|pytorch|keras",
    "Automatización/RPA": r"automatizaci|\brpa\b|power automate|uipath|n8n",
    "Git": r"\bgit(hub|lab)?\b", "Docker": r"docker", "AWS": r"\baws\b", "Azure": r"\bazure\b",
    "GCP": r"\bgcp\b|google cloud", "Linux": r"\blinux\b", "Testing/QA": r"\bqa\b|pruebas|testing|selenium|cypress",
    "Scrum/Ágil": r"scrum|\b[aá]gil|kanban|jira", "Inglés": r"ingl[eé]s|english",
}
_HAB_RX = {h: re.compile(rx) for h, rx in HABILIDADES.items()}


def cabecera(desc: str) -> list[str]:
    """Las primeras líneas de la descripción traen salario, contrato, jornada y modalidad."""
    es_cabecera = re.compile(r"^(\$|a convenir|contrato|tiempo|medio tiempo|por horas|beca|fines de semana|"
                             r"remoto|presencial)", re.I)
    cab = []
    for l in (x.strip() for x in re.split(r"\r?\n", desc)[1:10]):
        if not l:
            continue
        if not es_cabecera.match(l):
            break                     # empieza el cuerpo de la descripción
        cab.append(l)
    return cab


def parse_salario(cab: list[str]) -> float | None:
    """'$ 2.500.000,00 (Mensual)' -> 2500000.0 ; 'A convenir' -> None."""
    for l in cab:
        m = re.match(r"\$\s*([\d.]+)(?:,\d+)?", l)
        if m:
            valor = float(m.group(1).replace(".", ""))
            return valor if 500_000 <= valor <= 60_000_000 else None   # descarta valores absurdos
    return None


def parse_modalidad(cab: list[str]) -> str:
    texto = " ".join(cab).lower()
    if "presencial y remoto" in texto:
        return "Híbrido"
    if "remoto" in texto:
        return "Remoto"
    return "Presencial"


def parse_contrato(cab: list[str]) -> str | None:
    return next((l for l in cab if l.lower().startswith("contrato")), None)


def parse_jornada(cab: list[str]) -> str | None:
    claves = ("tiempo completo", "medio tiempo", "por horas", "beca/prácticas", "fines de semana", "tiempo parcial")
    return next((l for l in cab if l.lower() in claves), None)


def parse_experiencia(desc: str) -> int | None:
    m = re.search(r"Requerimientos.*?(\d+)\s+años? de experiencia", desc, re.S)
    return int(m.group(1)) if m else None


def parse_educacion(desc: str) -> str | None:
    m = re.search(r"Educación mínima:\s*([^\n\r]+)", desc)
    return m.group(1).strip() if m else None


def parse_lugar(empresa_lugar: str) -> tuple[str, str, str]:
    """'Grupo emi S.A.S - Bucaramanga, Santander' -> ('Grupo emi S.A.S', 'Bucaramanga', 'Santander')."""
    empresa, _, lugar = empresa_lugar.rpartition(" - ")
    partes = [p.strip() for p in lugar.split(",")]
    ciudad = partes[0] if partes else ""
    depto = partes[-1] if len(partes) > 1 else ciudad
    return empresa.strip() or "Confidencial", ciudad, depto


def parse_nivel(titulo: str, desc: str) -> str:
    t = (titulo + " " + desc[:1500]).lower()
    if re.search(r"practicante|aprendiz|pasant|trainee|pr[aá]cticas", t):
        return "Práctica"
    if re.search(r"\bsenior\b|\bsr\b|l[ií]der|\blead\b|arquitect", titulo.lower()):
        return "Senior"
    if re.search(r"semi ?senior|\bssr\b", t):
        return "Semi senior"
    if re.search(r"junior|\bjr\b|sin experiencia|reci[eé]n egresad", t):
        return "Junior"
    return "Sin especificar"


TITULO_TECH = re.compile(
    r"desarroll|program|developer|software|datos|data|anal[ií]tic|bi|inteligencia artificial|ia|"
    r"machine|python|java|automatiz|rpa|qa|tester|full ?stack|front|back|web|devops|cloud|sistemas|"
    r"soporte t[eé]cnico|ingenier[oa] de (software|datos)")


def es_tech(titulo: str) -> bool:
    return bool(TITULO_TECH.search(titulo.lower()))


def habilidades(texto: str) -> list[str]:
    t = texto.lower()
    return sorted(h for h, rx in _HAB_RX.items() if rx.search(t))


def transformar(crudo: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (ofertas, ofertas_habilidades): una tabla principal y una tabla puente."""
    filas, puente = [], []
    for o in crudo.values():
        cab = cabecera(o["descripcion"])
        empresa, ciudad, depto = parse_lugar(o["empresa_lugar"])
        filas.append({
            "id": o["id"], "titulo": o["titulo"], "empresa": empresa, "ciudad": ciudad, "departamento": depto,
            "categoria": o["categorias"][0], "es_tech": es_tech(o["titulo"]), "nivel": parse_nivel(o["titulo"], o["descripcion"]),
            "modalidad": parse_modalidad(cab), "contrato": parse_contrato(cab), "jornada": parse_jornada(cab),
            "salario": parse_salario(cab), "experiencia_anios": parse_experiencia(o["descripcion"]),
            "educacion": parse_educacion(o["descripcion"]), "url": o["url"], "fecha": o["visto"],
        })
        for h in habilidades(o["titulo"] + "\n" + o["descripcion"]):
            puente.append({"oferta_id": o["id"], "habilidad": h})
    ofertas = pd.DataFrame(filas).drop_duplicates("id")
    ofertas["fecha"] = pd.to_datetime(ofertas["fecha"])
    return ofertas, pd.DataFrame(puente, columns=["oferta_id", "habilidad"])
