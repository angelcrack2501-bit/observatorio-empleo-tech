"""Dashboard del Observatorio de Empleo Tech Colombia.

    streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path(__file__).parent / "data"
AZUL = "#1f6feb"

st.set_page_config(page_title="Observatorio de Empleo Tech Colombia", page_icon="📊", layout="wide")


@st.cache_data
def cargar():
    ofertas = pd.read_csv(DATA / "ofertas.csv", parse_dates=["fecha"])
    hab = pd.read_csv(DATA / "ofertas_habilidades.csv")
    return ofertas, hab


ofertas, hab = cargar()

# ── Filtros ────────────────────────────────────────────────────────────────
st.sidebar.header("Filtros")
solo_tech = st.sidebar.toggle("Solo cargos de tecnología", value=True)
cats = st.sidebar.multiselect("Categoría", sorted(ofertas.categoria.unique()), default=sorted(ofertas.categoria.unique()))
mods = st.sidebar.multiselect("Modalidad", ["Remoto", "Híbrido", "Presencial"], default=["Remoto", "Híbrido", "Presencial"])
niveles = st.sidebar.multiselect("Nivel", sorted(ofertas.nivel.unique()), default=sorted(ofertas.nivel.unique()))
solo_santander = st.sidebar.toggle("Solo Santander + remoto", value=False)

f = ofertas[ofertas.categoria.isin(cats) & ofertas.modalidad.isin(mods) & ofertas.nivel.isin(niveles)]
if solo_tech:
    f = f[f.es_tech]
if solo_santander:
    f = f[(f.departamento == "Santander") | (f.modalidad == "Remoto")]
h = hab[hab.oferta_id.isin(f.id)]

# ── Encabezado y KPIs ──────────────────────────────────────────────────────
st.title("📊 Observatorio de Empleo Tech Colombia")
st.caption(f"Ofertas públicas de Computrabajo · actualizado {ofertas.fecha.max():%d/%m/%Y} · "
           "fuente y metodología en el README del proyecto")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ofertas analizadas", f"{len(f):,}")
c2.metric("Salario mediano", f"${f.salario.median():,.0f}".replace(",", ".") if f.salario.notna().any() else "—")
c3.metric("% remotas", f"{100 * (f.modalidad == 'Remoto').mean():.0f}%" if len(f) else "—")
c4.metric("% que publican salario", f"{100 * f.salario.notna().mean():.0f}%" if len(f) else "—")

if f.empty:
    st.warning("No hay ofertas con esos filtros.")
    st.stop()

# ── Habilidades ────────────────────────────────────────────────────────────
st.subheader("¿Qué habilidades piden?")
top = (h.habilidad.value_counts().head(15) / len(f) * 100).round(1).rename("porcentaje").reset_index()
fig = px.bar(top.sort_values("porcentaje"), x="porcentaje", y="habilidad", orientation="h",
             labels={"porcentaje": "% de ofertas", "habilidad": ""}, color_discrete_sequence=[AZUL])
fig.update_layout(height=480, margin=dict(l=0, r=0, t=10, b=0))
st.plotly_chart(fig, use_container_width=True)

# ── Prima salarial por habilidad ───────────────────────────────────────────
st.subheader("¿Qué habilidad paga más?")
st.caption("Salario promedio de las ofertas que piden cada habilidad (solo ofertas que publican salario, mínimo 8).")
con_sal = f[f.salario.notna()][["id", "salario"]].merge(h, left_on="id", right_on="oferta_id")
prima = (con_sal.groupby("habilidad").salario.agg(["mean", "count"]).query("count >= 8")
         .sort_values("mean", ascending=False).head(12).reset_index())
if not prima.empty:
    fig = px.bar(prima, x="habilidad", y="mean", text="count",
                 labels={"mean": "Salario promedio (COP)", "habilidad": "", "count": "ofertas"},
                 color_discrete_sequence=[AZUL])
    fig.add_hline(y=f.salario.mean(), line_dash="dot", annotation_text="promedio general")
    fig.update_traces(texttemplate="n=%{text}", textposition="outside")
    fig.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Pocas ofertas con salario para estos filtros.")

# ── Modalidad, ciudad y nivel ──────────────────────────────────────────────
a, b = st.columns(2)
with a:
    st.subheader("Modalidad")
    m = f.modalidad.value_counts().reset_index()
    st.plotly_chart(px.pie(m, names="modalidad", values="count", hole=.55,
                           color_discrete_sequence=[AZUL, "#7cc4ff", "#c9d6e3"]), use_container_width=True)
with b:
    st.subheader("Ciudades con más ofertas")
    c = f[f.modalidad != "Remoto"].ciudad.value_counts().head(8).reset_index()
    st.plotly_chart(px.bar(c, x="count", y="ciudad", orientation="h", labels={"count": "ofertas", "ciudad": ""},
                           color_discrete_sequence=[AZUL]).update_yaxes(autorange="reversed"),
                    use_container_width=True)

st.subheader("Experiencia que piden")
exp = f.experiencia_anios.fillna(-1).astype(int).value_counts().sort_index().reset_index()
exp["etiqueta"] = exp.experiencia_anios.map(lambda x: "No especifica" if x < 0 else f"{x} año{'s' * (x != 1)}")
st.plotly_chart(px.bar(exp, x="etiqueta", y="count", labels={"etiqueta": "", "count": "ofertas"},
                       color_discrete_sequence=[AZUL]), use_container_width=True)

# ── Tabla ──────────────────────────────────────────────────────────────────
st.subheader("Ofertas")
st.dataframe(
    f.sort_values("fecha", ascending=False)[["titulo", "empresa", "ciudad", "modalidad", "nivel", "salario", "url"]],
    column_config={"url": st.column_config.LinkColumn("enlace", display_text="ver"),
                   "salario": st.column_config.NumberColumn(format="$%d")},
    hide_index=True, use_container_width=True)

st.caption("Proyecto de Ángel Santiago Vargas Castro · github.com/angelcrack2501-bit · "
           "Las cifras describen solo las ofertas publicadas en Computrabajo, no todo el mercado.")
