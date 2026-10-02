# Guía para defender este proyecto en una entrevista

> Léela antes de cualquier entrevista. Si puedes explicar cada respuesta con tus palabras, el proyecto juega a tu favor.

## Tu pitch de 30 segundos

"Construí un observatorio que recolecta automáticamente ofertas de empleo tech de Computrabajo, las limpia con pandas, las guarda en una base de datos SQL y las muestra en un dashboard en Streamlit. Se actualiza solo cada semana con GitHub Actions. Lo hice para responder una pregunta real: ¿qué habilidades debo aprender para conseguir trabajo? Y encontré, por ejemplo, que las ofertas que piden Python ofrecen un salario mediano de $4,5 millones frente a $2,7 millones de las que no lo piden."

## La arquitectura (dibújala si te dejan)

```
Computrabajo (web pública)
      │  extract.py  — urllib + expresiones regulares
      ▼
data/raw/ofertas.json   (texto crudo)
      │  transform.py — pandas: salario, modalidad, ciudad, nivel, habilidades
      ▼
SQLite: ofertas  ──<  ofertas_habilidades   (+ CSV para el dashboard)
      │  load.py
      ▼
app.py (Streamlit + Plotly)        GitHub Actions: lunes 7 a. m. corre todo y guarda
```

## Preguntas que te pueden hacer

**1. ¿Qué es ETL y dónde está en tu proyecto?**
Extraer, Transformar, Cargar. `extract.py` descarga, `transform.py` limpia y estructura, `load.py` guarda en SQL. Separarlo así permite probar y cambiar cada parte sin romper las otras.

**2. ¿Por qué dos tablas y no una?**
Una oferta tiene muchas habilidades y una habilidad aparece en muchas ofertas: es una relación muchos-a-muchos. La tabla puente `ofertas_habilidades` (oferta_id, habilidad) es la forma normalizada de guardarla. Así puedo hacer `GROUP BY habilidad` o un `JOIN` para ver qué habilidades aparecen juntas (consulta 4 de `sql/consultas.sql`).

**3. ¿Cómo detectas las habilidades?**
Con expresiones regulares sobre el texto de la oferta. Ejemplo de un problema real: "java" también aparece dentro de "javascript"; lo resolví con `\bjava\b(?!script)` (palabra completa y que no siga "script"). Hay una prueba para eso.

**4. ¿Qué limitaciones tiene?** (te ven más maduro si las dices tú)
- Solo una fuente (Computrabajo), no todo el mercado.
- Solo ~53 % de las ofertas publica salario, así que los salarios tienen sesgo.
- Las regex pueden fallar con sinónimos; una mejora sería usar un modelo de lenguaje para extraer habilidades.
- Una correlación (Python paga más) no es causalidad: las ofertas de Python suelen ser de IA/datos, que ya pagan más.

**5. ¿Cómo sabes que el código funciona?**
Pruebas automáticas con pytest (`tests/`) para cada función de limpieza: salario, modalidad, experiencia, lugar, nivel. GitHub Actions corre las pruebas antes de actualizar los datos: si fallan, no se publica nada.

**6. ¿Por qué el histórico no se pierde si las ofertas se borran del sitio?**
`load.acumular()` mezcla lo nuevo con el CSV anterior; si una oferta ya existía, la versión nueva reemplaza a la vieja (`drop` por id). Así el dataset crece cada semana.

**7. ¿Es legal hacer scraping?**
Leo solo páginas públicas, sin iniciar sesión, con pausas entre peticiones para no cargar el servidor, y no publico las descripciones completas, solo datos agregados y el enlace a la oferta original.

**8. ¿Qué harías con más tiempo?**
Más fuentes (LinkedIn, elempleo), PostgreSQL en la nube, extraer habilidades con IA, y un modelo que estime el salario de una oferta según sus habilidades.

## Practica en voz alta
1. Abre `transform.py` y explica `parse_salario` línea por línea.
2. Ejecuta `pytest -q` y explica qué prueba cada test.
3. Corre la consulta 3 de `sql/consultas.sql` y explica el `CASE WHEN EXISTS`.
