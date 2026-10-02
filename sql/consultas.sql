-- Consultas de análisis sobre data/observatorio.db
-- Ejecutar con: sqlite3 data/observatorio.db < sql/consultas.sql

-- 1. Top 10 habilidades más pedidas y % de ofertas que las piden
SELECT h.habilidad,
       COUNT(*) AS ofertas,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM ofertas), 1) AS porcentaje
FROM ofertas_habilidades h
GROUP BY h.habilidad
ORDER BY ofertas DESC
LIMIT 10;

-- 2. Salario mediano aproximado por categoría (solo ofertas que publican salario)
SELECT categoria,
       COUNT(salario) AS con_salario,
       ROUND(AVG(salario)) AS salario_promedio,
       MIN(salario) AS minimo,
       MAX(salario) AS maximo
FROM ofertas
WHERE salario IS NOT NULL
GROUP BY categoria
ORDER BY salario_promedio DESC;

-- 3. ¿Pagan más las ofertas que piden Python? (comparación con / sin la habilidad)
SELECT CASE WHEN EXISTS (SELECT 1 FROM ofertas_habilidades h
                         WHERE h.oferta_id = o.id AND h.habilidad = 'Python')
            THEN 'Pide Python' ELSE 'No pide Python' END AS grupo,
       COUNT(*) AS ofertas,
       ROUND(AVG(o.salario)) AS salario_promedio
FROM ofertas o
WHERE o.salario IS NOT NULL
GROUP BY grupo;

-- 4. Parejas de habilidades que más aparecen juntas
SELECT a.habilidad AS habilidad_1, b.habilidad AS habilidad_2, COUNT(*) AS veces
FROM ofertas_habilidades a
JOIN ofertas_habilidades b ON a.oferta_id = b.oferta_id AND a.habilidad < b.habilidad
GROUP BY a.habilidad, b.habilidad
ORDER BY veces DESC
LIMIT 10;

-- 5. Ofertas accesibles para un estudiante: práctica/junior, remoto o en Santander, <= 1 año de experiencia
SELECT titulo, empresa, ciudad, modalidad, salario, url
FROM ofertas
WHERE nivel IN ('Práctica', 'Junior')
  AND (modalidad = 'Remoto' OR departamento = 'Santander')
  AND COALESCE(experiencia_anios, 0) <= 1
ORDER BY salario DESC NULLS LAST;
