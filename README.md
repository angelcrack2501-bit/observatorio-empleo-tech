# 📊 Observatorio de Empleo Tech Colombia

> ¿Qué habilidades piden las empresas de tecnología en Colombia y cuáles pagan más? Un pipeline de datos que lo responde automáticamente cada semana.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-ETL-150458?logo=pandas)
![SQLite](https://img.shields.io/badge/SQL-SQLite-003B57?logo=sqlite)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)
![Actualizar datos](https://github.com/angelcrack2501-bit/observatorio-empleo-tech/actions/workflows/actualizar.yml/badge.svg)

## Hallazgos (corte: 1 de octubre de 2026 · 371 ofertas de tecnología)

| | |
|---|---|
| 🥇 **SQL es la habilidad más pedida** | aparece en el **37 %** de las ofertas, por encima de Python (30 %) y APIs REST (30 %). |
| 💰 **Python paga más** | las ofertas que piden Python ofrecen un salario mediano de **$4,48 M** frente a **$2,65 M** de las que no (50 vs. 148 ofertas con salario publicado). Ojo: correlación, no causalidad; muchas son de IA y datos. |
| 🤖 **La automatización ya es mainstream** | **26 %** de las ofertas pide automatización o RPA. |
| 🏠 **El remoto es minoría** | 17 % remoto, 29 % híbrido, 54 % presencial. |
| 🎓 **Sí hay espacio para empezar** | **43 %** de las ofertas pide 1 año de experiencia o menos, o no exige experiencia. |
| 💵 **Transparencia salarial** | solo el 53 % de las ofertas publica salario; mediana: **$3,0 M**. |

## Cómo funciona

```
Computrabajo (páginas públicas)
   │  extract.py   urllib + regex, pausas entre peticiones
   ▼
data/raw/ofertas.json
   │  transform.py pandas: salario, modalidad, ciudad, nivel, experiencia, 35 habilidades
   ▼
SQLite (ofertas ──< ofertas_habilidades) + CSV
   │  load.py      acumula el histórico semana a semana
   ▼
app.py  Streamlit + Plotly            ⏰ GitHub Actions: cada lunes corre pruebas → ETL → commit
```

- **Modelo de datos normalizado:** relación muchos-a-muchos oferta ↔ habilidad con tabla puente.
- **SQL de análisis:** [`sql/consultas.sql`](sql/consultas.sql) incluye el top de habilidades, salario por categoría, la prima salarial de Python (`CASE WHEN EXISTS`), las parejas de habilidades que aparecen juntas (self-join) y las ofertas accesibles para estudiantes.
- **Calidad:** pruebas con pytest para cada función de limpieza; el workflow no publica datos si fallan.
- **Histórico:** las ofertas viejas no se pierden aunque las borren del sitio.

## Ejecutarlo

```bash
python -m venv .venv && .venv\Scripts\activate     # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python pipeline.py              # descarga + limpia + carga  (≈10 min)
python pipeline.py --sin-extraer   # solo re-procesa lo descargado
streamlit run app.py            # dashboard en http://localhost:8501
pytest -q                       # pruebas
```

## Estructura

```
observatorio/
  extract.py     # E: descarga
  transform.py   # T: limpieza y extracción de habilidades
  load.py        # L: SQLite + CSV, histórico acumulado
pipeline.py      # orquesta el ETL
app.py           # dashboard
sql/consultas.sql
tests/
.github/workflows/actualizar.yml
GUIA_ENTREVISTA.md   # decisiones de diseño y preguntas frecuentes
```

## Ética y limitaciones

- Solo se leen páginas públicas, sin iniciar sesión, con pausas para no cargar el servidor. No se publican las descripciones completas, solo campos agregados y el enlace a la oferta original.
- Una sola fuente (Computrabajo): describe ese portal, no todo el mercado laboral.
- Las habilidades se detectan con expresiones regulares; pueden escaparse sinónimos.
- Los salarios solo incluyen ofertas que los publican.

## Próximos pasos
- Más fuentes (elempleo, LinkedIn).
- Extracción de habilidades con un modelo de lenguaje.
- Modelo de regresión que estime el salario según las habilidades.

## Autor

**Ángel Santiago Vargas Castro** — Estudiante de Ingeniería en Ciencias de la Computación e IA, UDES (Bucaramanga) · [GitHub](https://github.com/angelcrack2501-bit)
