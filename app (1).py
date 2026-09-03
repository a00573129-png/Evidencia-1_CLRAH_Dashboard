import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="CLRAH — Diagnóstico de Cadena de Suministro", layout="wide")

NAVY, CORAL, GRAY, GREEN = "#1F3864", "#C55A11", "#808080", "#4C7C4C"
MESES_ORDEN = ["Enero","Febrero","Marzo","Abril","Mayo","junio","julio","Agosto","Sept","Oct","Nov","Dic"]

# Código ISO-3 por país, necesario para el mapa (más confiable que nombres por acentos/idioma)
ISO3 = {
    "Argentina": "ARG", "Barbados": "BRB", "Belice": "BLZ", "Bolivia": "BOL", "Brasil": "BRA",
    "Chad": "TCD", "Colombia": "COL", "Costa Rica": "CRI", "Cuba": "CUB", "Dominica": "DMA",
    "Ecuador": "ECU", "El Salvador": "SLV", "Granada": "GRD", "Guadalupe": "GLP", "Guatemala": "GTM",
    "Haití": "HTI", "Honduras": "HND", "Jamaica": "JAM", "Panamá": "PAN",
    "República Dominicana": "DOM", "San Vicente y las Granadinas": "VCT", "Santa Lucía": "LCA",
    "Uruguay": "URY", "Venezuela": "VEN",
}

# Agregado mensual 2026 (enero-julio), por usuario — no tiene desglose por país/transporte/socio
DATA_2026 = pd.DataFrame({
    "MesNombre": ["Enero","Febrero","Marzo","Abril","Mayo","junio","julio"],
    "UNHRD": [90, 181.8, 63, 42.7, 36.5, 129.6, 145.16],
    "IFRC":  [2.7, 16.9, 22, 164.6, 66.7, 204.7, 84.87],
})
DATA_2026["Tons"] = DATA_2026["UNHRD"] + DATA_2026["IFRC"]

@st.cache_data
def load_data():
    df = pd.read_csv("master_clean_es.csv", parse_dates=["Fecha"])
    df["ISO3"] = df["Country_clean"].map(ISO3)
    return df

df = load_data()

# ---------------- Encabezado ----------------
st.title("📦 CLRAH — Diagnóstico de la Cadena de Suministro Humanitaria")
st.caption("Datos de despacho línea por línea, 2025 (375 registros limpios) + agregado 2026 (ene-jul). Fuente: CLRAH.")

# ---------------- Filtros (sidebar) ----------------
st.sidebar.header("Filtros (aplican a 2025)")
meses_disponibles = [m for m in MESES_ORDEN if m in df["MesNombre"].unique()]
mes_sel = st.sidebar.multiselect("Mes", meses_disponibles, default=meses_disponibles)
usuarios_disponibles = sorted(df["User_clean"].dropna().unique())
usuario_sel = st.sidebar.multiselect("Usuario", usuarios_disponibles, default=usuarios_disponibles)
paises_disponibles = sorted(df["Country_clean"].dropna().unique())
pais_sel = st.sidebar.multiselect("País", paises_disponibles, default=paises_disponibles)
st.sidebar.markdown("---")
st.sidebar.caption("Diagnóstico CLRAH · Eugenio Sánchez Velázquez · Tecnológico de Monterrey")

df_f = df[df["MesNombre"].isin(mes_sel) & df["User_clean"].isin(usuario_sel) & df["Country_clean"].isin(pais_sel)]
if df_f.empty:
    st.warning("No hay datos para los filtros seleccionados. Ajusta los filtros en la barra lateral.")
    st.stop()

# ---------------- KPIs ----------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Toneladas (2025, filtrado)", f"{df_f['Tons'].sum():,.1f}")
col2.metric("USD movilizados", f"${df_f['Stock Value USD'].sum():,.0f}")
col3.metric("Países", df_f["Country_clean"].nunique())
col4.metric("Despachos", len(df_f))

st.divider()

# ---------------- Mapa interactivo de toda Latinoamérica y el Caribe ----------------
st.subheader("🗺️ Mapa de cobertura — América Latina y el Caribe")
metric_choice = st.radio("Mostrar por:", ["Toneladas", "USD"], horizontal=True)
by_country_map = df_f.groupby(["Country_clean", "ISO3"])[["Tons", "Stock Value USD"]].sum().reset_index()
value_col = "Tons" if metric_choice == "Toneladas" else "Stock Value USD"

fig_map = px.choropleth(
    by_country_map, locations="ISO3", color=value_col,
    hover_name="Country_clean",
    hover_data={"ISO3": False, "Tons": ":.1f", "Stock Value USD": ":,.0f"},
    color_continuous_scale="Blues",
    scope="world",
)
fig_map.update_geos(
    center=dict(lat=10, lon=-75), projection_scale=2.6,
    showcountries=True, countrycolor="#DDDDDD", showland=True, landcolor="#F5F5F5",
)
fig_map.update_layout(
    margin=dict(l=0, r=0, t=10, b=0),
    coloraxis_colorbar=dict(title="Toneladas" if metric_choice == "Toneladas" else "USD"),
    height=500,
)
st.plotly_chart(fig_map, use_container_width=True)
st.caption(f"{by_country_map.shape[0]} países con envíos registrados en el periodo filtrado.")

st.divider()

# ---------------- Serie de tiempo: 2025 (filtrado) + 2026 (agregado, sin filtro) ----------------
st.subheader("📈 Serie de tiempo continua — 2025 → 2026 (enero-julio)")
monthly_2025 = df_f.groupby("MesNombre")["Tons"].sum().reindex(
    [m for m in MESES_ORDEN if m in df_f["MesNombre"].unique()]
).reset_index()
monthly_2025["Etiqueta"] = monthly_2025["MesNombre"] + " 2025"
monthly_2026 = DATA_2026[["MesNombre", "Tons"]].copy()
monthly_2026["Etiqueta"] = monthly_2026["MesNombre"] + " 2026"
serie = pd.concat([monthly_2025, monthly_2026], ignore_index=True).reset_index(drop=True)
n_2025 = len(monthly_2025)

fig_serie = go.Figure()
fig_serie.add_trace(go.Bar(
    x=serie["Etiqueta"], y=serie["Tons"], marker_color=NAVY,
    hovertemplate="<b>%{x}</b><br>Toneladas: %{y:,.0f}<extra></extra>",
))
fig_serie.add_vline(x=n_2025 - 0.5, line_dash="dash", line_color=GRAY)
fig_serie.add_annotation(x=n_2025 - 0.5, y=serie["Tons"].max(), text="Inicio 2026", showarrow=False,
                          yshift=15, font=dict(color=GRAY, size=11))
fig_serie.update_layout(xaxis_title="", yaxis_title="Toneladas", showlegend=False,
                         xaxis=dict(tickangle=-45))
st.plotly_chart(fig_serie, use_container_width=True)
st.caption("2026 es un agregado mensual por usuario (no tiene desglose por país/transporte/socio) — no responde a los filtros de la barra lateral.")

st.divider()

# ---------------- Concentración geográfica (Pareto) + Diversificación de socios ----------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Concentración geográfica (Pareto)")
    by_country = df_f.groupby("Country_clean")["Tons"].sum().sort_values(ascending=False).head(10)
    cum_pct = (by_country.cumsum() / df_f.groupby("Country_clean")["Tons"].sum().sum() * 100)
    fig_p = make_subplots(specs=[[{"secondary_y": True}]])
    fig_p.add_trace(go.Bar(x=by_country.index, y=by_country.values, name="Toneladas", marker_color=NAVY), secondary_y=False)
    fig_p.add_trace(go.Scatter(x=by_country.index, y=cum_pct.values, name="% acumulado", mode="lines+markers", marker_color=CORAL), secondary_y=True)
    fig_p.add_hline(y=80, line_dash="dash", line_color="gray", secondary_y=True)
    fig_p.update_yaxes(title_text="Toneladas", secondary_y=False)
    fig_p.update_yaxes(title_text="% acumulado", secondary_y=True, range=[0, 105])
    fig_p.update_layout(legend=dict(orientation="h", y=1.15))
    st.plotly_chart(fig_p, use_container_width=True)

with c2:
    st.subheader("Diversificación de socios por país")
    partner_counts = df_f.groupby("Country_clean")["Partner"].apply(lambda s: s.dropna().nunique())
    sin_dato = df_f.groupby("Country_clean")["Partner"].apply(lambda s: s.isna().all())
    dfp = pd.DataFrame({"n_socios": partner_counts, "sin_dato": sin_dato}).sort_values("n_socios")
    dfp["categoria"] = np.select(
        [dfp["sin_dato"], dfp["n_socios"] == 1],
        ["Sin socio registrado", "1 solo socio (riesgo)"],
        default="2+ socios"
    )
    dfp["valor_x"] = dfp["n_socios"].where(~dfp["sin_dato"], 0)
    fig_d = px.bar(dfp.reset_index(), x="valor_x", y="Country_clean", color="categoria", orientation="h",
                    color_discrete_map={"Sin socio registrado": GRAY, "1 solo socio (riesgo)": CORAL, "2+ socios": NAVY})
    fig_d.update_layout(xaxis_title="Número de socios distintos", yaxis_title="", legend_title="", height=430)
    st.plotly_chart(fig_d, use_container_width=True)

st.divider()

# ---------------- Modal + Costo por transporte ----------------
c3, c4 = st.columns(2)
with c3:
    st.subheader("Distribución modal de transporte")
    modal = df_f.groupby("Transport_clean")["Tons"].sum().sort_values(ascending=False).reset_index()
    fig_m = px.pie(modal, names="Transport_clean", values="Tons", color_discrete_sequence=[NAVY, CORAL, GREEN, GRAY])
    st.plotly_chart(fig_m, use_container_width=True)

with c4:
    st.subheader("Costo promedio por tonelada según transporte")
    cost_mode = df_f.groupby("Transport_clean").apply(
        lambda d: d["Stock Value USD"].sum() / d["Tons"].sum() if d["Tons"].sum() > 0 else 0, include_groups=False
    ).sort_values(ascending=False).reset_index()
    cost_mode.columns = ["Transport_clean", "USD_ton"]
    fig_c = px.bar(cost_mode, x="Transport_clean", y="USD_ton", color_discrete_sequence=[NAVY])
    fig_c.update_layout(xaxis_title="", yaxis_title="USD por tonelada", showlegend=False)
    st.plotly_chart(fig_c, use_container_width=True)

st.divider()

# ---------------- Top socios ----------------
st.subheader("Top 10 socios por número de despachos")
top_partners = df_f["Partner"].value_counts().head(10).sort_values(ascending=True).reset_index()
top_partners.columns = ["Partner", "Despachos"]
fig_s = px.bar(top_partners, x="Despachos", y="Partner", orientation="h", color_discrete_sequence=[NAVY])
fig_s.update_layout(xaxis_title="Número de despachos", yaxis_title="", showlegend=False)
st.plotly_chart(fig_s, use_container_width=True)

st.divider()

# ---------------- Relación ayuda-daño (no filtrado, es a nivel evento) ----------------
st.subheader("💰 Relación entre el valor de la ayuda y el costo del daño")
st.caption("Esta sección no responde a los filtros — compara eventos específicos, no el periodo filtrado arriba.")

ayuda_melissa = df[df["Mes"].isin([10, 11])]["Stock Value USD"].sum() / 1e6
eventos = [
    {"nombre": "Huracán Dorian", "sub": "Bahamas, 2020", "danio": 3400, "ayuda": 24.1},
    {"nombre": "Huracán Melissa", "sub": "Jamaica, oct-nov 2025", "danio": 10000, "ayuda": ayuda_melissa},
]

col_a, col_b = st.columns(2)
for col, ev in zip([col_a, col_b], eventos):
    cobertura = ev["ayuda"] / ev["danio"] * 100
    with col:
        st.markdown(f"**{ev['nombre']}** · {ev['sub']}")
        m1, m2, m3 = st.columns(3)
        m1.metric("Daño estimado", f"${ev['danio']:,.0f}M")
        m2.metric("Ayuda CLRAH", f"${ev['ayuda']:,.1f}M")
        m3.metric("Cobertura", f"{cobertura:.2f}%")

fig_dano = go.Figure()
fig_dano.add_trace(go.Bar(
    x=[f"{e['nombre']}\n({e['sub']})" for e in eventos],
    y=[e["ayuda"] / e["danio"] * 100 for e in eventos],
    marker_color=[NAVY, CORAL],
    text=[f"{e['ayuda']/e['danio']*100:.2f}%" for e in eventos],
    textposition="outside",
))
fig_dano.update_layout(yaxis_title="% de cobertura (ayuda / daño)", xaxis_title="", height=350)
st.plotly_chart(fig_dano, use_container_width=True)

st.caption("Fuentes: Banco Interamericano de Desarrollo (2019, Dorian); Infobae (2025, Melissa); registros CLRAH (ayuda).")

# ---------------- Tabla de datos ----------------
with st.expander("Ver datos filtrados (tabla completa, 2025)"):
    st.dataframe(df_f[["Fecha","User_clean","Country_clean","Transport_clean","Partner","Tons","Stock Value USD"]],
                 use_container_width=True)
