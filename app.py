"""
ENA 2023–2025 · Perfil del Productor Agropecuario Nacional
Dashboard Streamlit ampliado — sube el Excel tal cual
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io

st.set_page_config(
    page_title="ENA · Perfil Productivo Nacional",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Acceso restringido ───────────────────────────────────────────────────────
def check_password():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.markdown("""
        <div style="max-width:380px;margin:80px auto;padding:32px;
                    background:#fff;border-radius:12px;
                    box-shadow:0 4px 20px rgba(0,0,0,0.10);text-align:center;">
          <div style="font-size:38px;margin-bottom:8px;">🌾</div>
          <div style="font-size:17px;font-weight:600;color:#1a4731;margin-bottom:4px;">
            ENA · Perfil Productivo Nacional</div>
          <div style="font-size:12px;color:#888;margin-bottom:24px;">
            INEI — Uso restringido</div>
        </div>
        """, unsafe_allow_html=True)

        col = st.columns([1, 2, 1])[1]
        with col:
            clave = st.text_input("Contraseña", type="password",
                                  placeholder="Ingresa la clave de acceso")
            if st.button("Ingresar", use_container_width=True):
                if clave == "ENA_INEI_2025":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta.")
        st.stop()

check_password()

# ── Paleta ──────────────────────────────────────────────────────────────────
C = {
    "verde": "#0F766E",
    "azul": "#1E3A8A",
    "rosa": "#EC4899",
    "naranja": "#EA580C",
    "rojo": "#DC2626",
    "morado": "#7C3AED",
    "cyan": "#0891B2",
    "gris": "#64748B",

    "primary": "#1E3A8A",
    "secondary": "#0F766E",
    "success": "#16A34A",
    "warning": "#EA580C",
    "danger": "#DC2626",
    "purple": "#7C3AED",
    "dark": "#0F172A",
    "light": "#F8FAFC"
}

PAL8 = [
    "#1E3A8A",
    "#0F766E",
    "#7C3AED",
    "#EA580C",
    "#0891B2",
    "#16A34A",
    "#DC2626",
    "#64748B"
]

YEARS = [2023, 2024, 2025, 2026]

# Columnas de estimación en el Excel (fijas para la estructura ENA)
# 2026 agrega 2 columnas después de 2025 manteniendo el mismo patrón
YR19 = {2023: 19, 2024: 21, 2025: 23, 2026: 25}   # mayoría de hojas
YR20 = {2023: 20, 2024: 22, 2025: 24, 2026: 26}   # hojas de cruce sexo (etnicidad, idioma)

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"]{
    font-family:'Inter',sans-serif;
}

[data-testid="stAppViewContainer"]{
    background:#F8FAFC;
}

[data-testid="stSidebar"]{
    background:#0F172A;
}

[data-testid="stSidebar"] *{
    color:white;
}

.main-banner{
    background:linear-gradient(
    135deg,
    #0F172A,
    #1E3A8A);
    
    padding:30px;
    border-radius:18px;
    color:white;
    
    margin-bottom:25px;
}

.main-title{
    font-size:34px;
    font-weight:700;
}

.main-sub{
    font-size:14px;
    opacity:.85;
}

.kpi-card{
    background:white;
    border-radius:18px;
    padding:22px;
    box-shadow:0 5px 18px rgba(0,0,0,.08);
}

.kpi-icon{
    font-size:32px;
}

.kpi-label{
    color:#64748B;
    font-size:12px;
    text-transform:uppercase;
}

.kpi-value{
    font-size:32px;
    font-weight:700;
}

.kpi-delta{
    font-size:13px;
    font-weight:600;
}

.insight{
    background:#ECFEFF;
    border-left:5px solid #0891B2;
    border-radius:12px;
    padding:15px;
    margin-top:10px;
}

.stTabs [data-baseweb="tab"]{
    font-size:15px;
    font-weight:600;
}

.stTabs [aria-selected="true"]{
    background:#1E3A8A;
    color:white;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)


# ── Lectura del Excel ────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def leer(file_bytes):
    xl = pd.ExcelFile(io.BytesIO(file_bytes))

    def total(sheet):
        df = xl.parse(sheet, header=None)
        return {yr: float(df.iloc[11, col]) for yr, col in YR19.items()
                if pd.notna(df.iloc[11, col])}

    def categ(sheet, n, cat_col=2, yr_cols=None):
        yc = yr_cols or YR19
        df = xl.parse(sheet, header=None)
        out = {}
        for i in range(n):
            cat = str(df.iloc[11+i, cat_col]).strip()
            if not cat or cat == 'nan': continue
            out[cat] = {yr: round(float(df.iloc[11+i, col]), 2)
                        for yr, col in yc.items()
                        if pd.notna(df.iloc[11+i, col])}
        return out

    def especies(sheet, label_col):
        """Hojas de especies: yr_row=8, datos desde fila 10, sin fila Nacional"""
        df = xl.parse(sheet, header=None)
        out = {}
        species_list = ['Vacunos','Ovinos','Caprinos','Porcinos',
                        'Llamas','Alpacas','Cuyes','Pollos']
        for i in range(10, 25):
            lbl = str(df.iloc[i, label_col]).strip()
            if not lbl or lbl == 'nan': continue
            match = next((s for s in species_list if s.lower() in lbl.lower()), None)
            if not match: continue
            vals = {}
            for yr, col in YR19.items():
                v = df.iloc[i, col]
                if pd.notna(v):
                    try: vals[yr] = round(float(v), 0)
                    except: pass
            if vals: out[match] = vals
        return out

    def sup_abs(sheet):
        df = xl.parse(sheet, header=None)
        labels = {
            'Sup. agrícola total':   10,
            'Sup. sembrada':         11,
            'Sup. en barbecho':      12,
            'Tierras inactivas':     13,
            'Sup. en descanso':      14,
            'Sup. no agrícola':      15,
            'Pastos nat. manejados': 16,
            'Pastos no manejados':   17,
            'Montes y bosques':      18,
        }
        out = {}
        for lbl, row in labels.items():
            vals = {}
            for yr, col in YR19.items():
                v = df.iloc[row, col]
                if pd.notna(v):
                    try: vals[yr] = round(float(v)/1e6, 3)  # en millones ha
                    except: pass
            if vals: out[lbl] = vals
        return out

    d = {}
    d['total']        = total('total_productores')
    d['sexo']         = categ('1.2.1_sexo',          2)
    d['edad']         = categ('1.1.1_edad_3',         4)
    d['educ']         = categ('1.5.1_nivel_educ_a',   5)
    d['tam_ua']       = categ('4.1.1_tam_ua_2',       4)
    d['usos_pct']     = {  # sup_usos_tierra_AG_NAG
        'Sup. sembrada':      {2023:43.7, 2024:43.1, 2025:44.9},
        'Sup. en barbecho':   {2023:12.7, 2024:12.5, 2025: 6.1},
        'Tierras inactivas':  {2023:33.8, 2024:33.5, 2025:41.5},
        'Sup. en descanso':   {2023: 9.8, 2024:11.0, 2025: 7.6},
    }
    d['num_parc']     = categ('4.1.2_num_parc', 5)
    d['esp_12m']      = especies('num_especi_ult12mes', label_col=1)
    d['prod_12m']     = especies('num_prod_ult12mes',   label_col=2)
    d['sup_abs']      = sup_abs('sup_usos_tierra_abs')

    # Etnicidad: yr_cols offset = YR20, cat anidada (Hombre col2, etnia col3)
    df_et = xl.parse('1.3.2_etnicidad_sexo', header=None)
    etnias = ['Quechua','Aymara','Nativo o indígena de la Amazonía',
              'Negro/Mulato/Zambo/Afro peruano','Blanco','Mestizo']
    et_out = {}
    for i in range(11, 25):
        cat = str(df_et.iloc[i, 3]).strip()
        match = next((e for e in etnias if e[:8] in cat), None)
        if not match: continue
        vals = {}
        for yr, col in YR20.items():
            v = df_et.iloc[i, col]
            if pd.notna(v):
                try: vals[yr] = round(float(v), 2)
                except: pass
        if vals: et_out[match[:20]] = vals
    d['etnicidad'] = et_out

    return d


def to_df(d, val='valor'):
    rows = [{'categoria': cat, 'anio': yr, val: v}
            for cat, yv in d.items() for yr, v in yv.items()]
    return pd.DataFrame(rows)


def layout():
    return dict(plot_bgcolor='white', paper_bgcolor='white',
                font_family="Inter,sans-serif", font_color="#333",
                margin=dict(t=36, b=28, l=8, r=8))


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown("## 🌾 ENA Dashboard")

    uploaded = st.file_uploader(
        "Seleccionar archivo ENA",
        type=["xlsx"]
    )

    st.markdown("---")

    st.markdown("### 📊 Variables")

    variables = [
        "Productores",
        "Sexo",
        "Edad",
        "Educación",
        "Etnicidad",
        "UA",
        "Parcelas",
        "Ganadería",
        "Superficie"
    ]

    for x in variables:
        st.markdown(f"✅ {x}")

    st.markdown("---")

    st.caption("INEI · DNCE")

if uploaded is None:
    st.markdown("""
    <div class="banner">
      <h1>🌾 Perfil del Productor Agropecuario Nacional · ENA</h1>
      <p>Encuesta Nacional Agropecuaria · INEI · Nivel nacional · 2023–2025</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("👈 Sube el archivo Excel en el panel izquierdo para cargar el dashboard.")
    st.stop()

with st.spinner("Procesando Excel..."):
    D = leer(uploaded.read())

# ── Banner ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-banner">

<div class="main-title">
🌾 ENA Dashboard Ejecutivo Nacional
</div>

<div class="main-sub">
Perfil del Productor Agropecuario Peruano
</div>

</div>
""", unsafe_allow_html=True)

# ── KPIs ─────────────────────────────────────────────────────────────────────
tot = D['total']
# Año más reciente disponible en los datos
yr_max  = max(yr for yr in YEARS if yr in tot)
yr_prev = yr_max - 1 if (yr_max - 1) in tot else sorted(tot.keys())[-2]

d_abs  = tot[yr_max] - tot[yr_prev]
d_pct  = (tot[yr_max] - tot[2023]) / tot[2023] * 100
rango  = f"2023→{yr_max}"

k1,k2,k3,k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">👨‍🌾</div>
        <div class="kpi-label">Productores</div>
        <div class="kpi-value">
            {tot[yr_max]/1000000:.2f} M
        </div>
        <div class="kpi-delta">
            {d_pct:+.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📈</div>
        <div class="kpi-label">Variación anual</div>
        <div class="kpi-value">
            {d_abs:,.0f}
        </div>
        <div class="kpi-delta">
            respecto a {yr_prev}
        </div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📅</div>
        <div class="kpi-label">Último año</div>
        <div class="kpi-value">
            {yr_max}
        </div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📊</div>
        <div class="kpi-label">Tendencia</div>
        <div class="kpi-value">
            {"↑" if d_pct>0 else "↓"}
        </div>
        <div class="kpi-delta">
            2023 → {yr_max}
        </div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("## 📌 Resumen Ejecutivo")

c1,c2 = st.columns([2,1])

with c1:

    st.markdown(f"""
    <div class="insight">
    <b>Hallazgo principal:</b><br>
    El número de productores agropecuarios alcanzó
    <b>{tot[yr_max]:,.0f}</b> en {yr_max},
    representando una variación de
    <b>{d_pct:+.1f}%</b> respecto a 2023.
    </div>
    """, unsafe_allow_html=True)

with c2:

    st.metric(
        "Crecimiento acumulado",
        f"{d_pct:+.1f}%"
    )

# ── TAB NAVIGATION ───────────────────────────────────────────────────────────
tabs = st.tabs([
"📈 Resumen",
"👤 Productores",
"🐄 Ganadería",
"🌱 Agricultura",
"🏡 Unidad Agropecuaria",
"📋 Reportes"
])

# ════════════════════════════════════════════════════════
# TAB 1 — PERFIL DEMOGRÁFICO
# ════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="sec">Evolución total de productores</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1.5, 1])
    with c1:
        yv = [tot[y] for y in YEARS if y in tot]
        yrs_disp = [y for y in YEARS if y in tot]
        x_num = np.arange(len(yrs_disp))
        coef = np.polyfit(x_num, yv, 1)
        yr_proj = max(yrs_disp) + 1
        y_proj = np.polyval(coef, len(yrs_disp))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[str(y) for y in yrs_disp], y=yv, mode='lines+markers+text',
            line=dict(color=C['verde'], width=3),
            marker=dict(size=9, color=C['verde'], line=dict(color='white',width=2)),
            text=[f"{v/1e6:.3f}M" for v in yv], textposition='top center',
            fill='tozeroy', fillcolor='rgba(29,158,117,0.08)', name='Observado'))

        # Solo mostrar proyección si 2026 aún no está en los datos
        if yr_proj not in tot:
            fig.add_trace(go.Scatter(
                x=[str(max(yrs_disp)), f"{yr_proj}*"],
                y=[yv[-1], y_proj],
                mode='lines+markers', line=dict(color=C['naranja'],width=2,dash='dash'),
                marker=dict(size=7,symbol='diamond',color=C['naranja']),
                text=['', f"{y_proj/1e6:.3f}M*"], textposition='top center',
                textfont=dict(size=10,color=C['naranja']), name=f'Proyección {yr_proj}'))
        fig.update_layout(title='Total productores/as agropecuarios/as',
                          yaxis=dict(tickformat=',.0f'), legend=dict(x=0,y=1.12,orientation='h'),
                          **layout())
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        df_s = to_df(D['sexo'])
        fig2 = px.bar(df_s, x='anio', y='valor', color='categoria', barmode='group',
                      color_discrete_map={'Hombre':C['azul'],'Mujer':C['rosa']},
                      text_auto='.1f', title='Distribución por sexo (%)',
                      labels={'valor':'%','anio':'Año','categoria':'Sexo'})
        fig2.update_traces(textfont_size=10, textposition='outside', cliponaxis=False)
        fig2.update_layout(yaxis_range=[0,88], **layout())
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="sec">Estructura por edad y educación</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        df_e = to_df(D['edad'])
        cmap = {c: PAL8[i] for i,c in enumerate(df_e['categoria'].unique())}
        fig3 = px.line(df_e, x='anio', y='valor', color='categoria',
                       color_discrete_map=cmap, markers=True,
                       title='% por grupos de edad',
                       labels={'valor':'%','anio':'Año','categoria':'Grupo'})
        fig3.update_traces(line_width=2.5, marker_size=8)
        fig3.update_layout(**layout())
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        df_ed = to_df(D['educ'])
        fig4 = px.bar(df_ed, x='valor', y='categoria', color='anio', barmode='group',
                      orientation='h', text_auto='.1f',
                      color_discrete_map={2023:C['verde'],2024:C['azul'],2025:C['naranja']},
                      title='% por nivel educativo',
                      labels={'valor':'%','categoria':'Nivel','anio':'Año'})
        fig4.update_traces(textfont_size=9)
        fig4.update_layout(yaxis=dict(autorange='reversed'), **layout())
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="sec">Etnicidad del productor (%)</div>', unsafe_allow_html=True)
    df_et = to_df(D['etnicidad'])
    if not df_et.empty:
        cmap_et = {c: PAL8[i] for i,c in enumerate(df_et['categoria'].unique())}
        fig_et = px.line(df_et, x='anio', y='valor', color='categoria',
                         color_discrete_map=cmap_et, markers=True,
                         title='Autoidentificación étnica del productor (% Hombre, Nacional)',
                         labels={'valor':'%','anio':'Año','categoria':'Etnia'})
        fig_et.update_traces(line_width=2.5, marker_size=8)
        fig_et.update_layout(**layout())
        st.plotly_chart(fig_et, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 2 — SECTOR PECUARIO
# ════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="sec">Número de cabezas por especie (últimos 12 meses)</div>',
                unsafe_allow_html=True)

    df_esp = to_df(D['esp_12m'], val='cabezas')
    c1, c2 = st.columns(2)

    with c1:
        # Barras agrupadas para especies principales
        esp_princ = ['Cuyes','Ovinos','Vacunos','Gallinas'] if 'Gallinas' in D['esp_12m'] else \
                    ['Cuyes','Ovinos','Vacunos','Porcinos']
        df_p = df_esp[df_esp['categoria'].isin(esp_princ)]
        fig_p = px.bar(df_p, x='anio', y='cabezas', color='categoria', barmode='group',
                       color_discrete_map={c: PAL8[i] for i,c in enumerate(esp_princ)},
                       text_auto='.2s',
                       title='Principales especies (cabezas)',
                       labels={'cabezas':'Cabezas','anio':'Año','categoria':'Especie'})
        fig_p.update_layout(**layout())
        st.plotly_chart(fig_p, use_container_width=True)

    with c2:
        # Líneas de tendencia para todas las especies
        cmap_e = {c: PAL8[i] for i,c in enumerate(df_esp['categoria'].unique())}
        fig_e2 = px.line(df_esp, x='anio', y='cabezas', color='categoria',
                         color_discrete_map=cmap_e, markers=True,
                         title='Tendencia por especie (cabezas)',
                         labels={'cabezas':'Cabezas','anio':'Año','categoria':'Especie'})
        fig_e2.update_traces(line_width=2.5, marker_size=7)
        fig_e2.update_layout(**layout())
        st.plotly_chart(fig_e2, use_container_width=True)

    st.markdown('<div class="sec">Número de productores pecuarios (últimos 12 meses)</div>',
                unsafe_allow_html=True)

    df_prod = to_df(D['prod_12m'], val='productores')
    c3, c4 = st.columns(2)

    with c3:
        cmap_pr = {c: PAL8[i] for i,c in enumerate(df_prod['categoria'].unique())}
        fig_pr = px.bar(df_prod, x='categoria', y='productores', color='anio', barmode='group',
                        color_discrete_map={2023:C['verde'],2024:C['azul'],2025:C['naranja']},
                        text_auto='.2s',
                        title='Productores por especie y año',
                        labels={'productores':'Productores','categoria':'Especie','anio':'Año'})
        fig_pr.update_layout(**layout())
        st.plotly_chart(fig_pr, use_container_width=True)

    with c4:
        # Variación % 2023→2025 por especie
        rows_var = []
        for esp, yvals in D['prod_12m'].items():
            if 2023 in yvals and 2025 in yvals:
                delta = (yvals[2025] - yvals[2023]) / yvals[2023] * 100
                rows_var.append({'Especie': esp, 'Δ% 2023→2025': round(delta,1)})
        df_var = pd.DataFrame(rows_var).sort_values('Δ% 2023→2025')
        colors_bar = [C['verde'] if v >= 0 else C['rojo'] for v in df_var['Δ% 2023→2025']]
        fig_var = go.Figure(go.Bar(
            x=df_var['Δ% 2023→2025'], y=df_var['Especie'],
            orientation='h', marker_color=colors_bar,
            text=[f"{v:+.1f}%" for v in df_var['Δ% 2023→2025']],
            textposition='outside'))
        fig_var.update_layout(title='Variación % productores 2023→2025',
                              xaxis=dict(title='%'), **layout())
        st.plotly_chart(fig_var, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 3 — SUPERFICIE AGRÍCOLA
# ════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="sec">Superficie agrícola absoluta (millones de hectáreas)</div>',
                unsafe_allow_html=True)

    df_sa = to_df(D['sup_abs'], val='millones_ha')
    c1, c2 = st.columns(2)

    with c1:
        cats_area = ['Sup. agrícola total','Sup. sembrada','Sup. en barbecho',
                     'Tierras inactivas','Sup. en descanso']
        df_main = df_sa[df_sa['categoria'].isin(cats_area)]
        cmap_a = {c: PAL8[i] for i,c in enumerate(cats_area)}
        fig_a = px.line(df_main, x='anio', y='millones_ha', color='categoria',
                        color_discrete_map=cmap_a, markers=True,
                        title='Componentes de superficie agrícola (M ha)',
                        labels={'millones_ha':'Millones ha','anio':'Año','categoria':'Uso'})
        fig_a.update_traces(line_width=2.5, marker_size=8)
        fig_a.update_layout(**layout())
        st.plotly_chart(fig_a, use_container_width=True)

    with c2:
        cats_noagri = ['Sup. no agrícola','Pastos nat. manejados',
                       'Pastos no manejados','Montes y bosques']
        df_na = df_sa[df_sa['categoria'].isin(cats_noagri)]
        cmap_na = {c: PAL8[i+4] for i,c in enumerate(cats_noagri)}
        fig_na = px.line(df_na, x='anio', y='millones_ha', color='categoria',
                         color_discrete_map=cmap_na, markers=True,
                         title='Superficie no agrícola (M ha)',
                         labels={'millones_ha':'Millones ha','anio':'Año','categoria':'Uso'})
        fig_na.update_traces(line_width=2.5, marker_size=8)
        fig_na.update_layout(**layout())
        st.plotly_chart(fig_na, use_container_width=True)

    st.markdown('<div class="sec">Usos de la superficie agrícola (%)</div>',
                unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        df_up = to_df(D['usos_pct'])
        cmap_up = {c: PAL8[i] for i,c in enumerate(df_up['categoria'].unique())}
        fig_up = px.line(df_up, x='anio', y='valor', color='categoria',
                         color_discrete_map=cmap_up, markers=True,
                         title='% usos de la superficie agrícola',
                         labels={'valor':'%','anio':'Año','categoria':'Uso'})
        fig_up.update_traces(line_width=2.5, marker_size=8)
        fig_up.update_layout(**layout())
        st.plotly_chart(fig_up, use_container_width=True)

    with c4:
        # Waterfall de variación absoluta 2023→2025 en superficie
        rows_w = []
        for cat, yvals in D['sup_abs'].items():
            if 2023 in yvals and 2025 in yvals:
                rows_w.append({'Uso': cat, 'Δ M ha': round(yvals[2025]-yvals[2023],3)})
        df_w = pd.DataFrame(rows_w).sort_values('Δ M ha')
        cols_w = [C['verde'] if v>=0 else C['rojo'] for v in df_w['Δ M ha']]
        fig_w = go.Figure(go.Bar(
            x=df_w['Δ M ha'], y=df_w['Uso'], orientation='h',
            marker_color=cols_w,
            text=[f"{v:+.3f}" for v in df_w['Δ M ha']], textposition='outside'))
        fig_w.update_layout(title='Variación absoluta sup. 2023→2025 (M ha)',
                             xaxis=dict(title='Millones ha'), **layout())
        st.plotly_chart(fig_w, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 4 — ESTRUCTURA UA
# ════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="sec">Tamaño de la unidad agropecuaria y número de parcelas</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        df_tam = to_df(D['tam_ua'])
        cmap_t = {c: PAL8[i] for i,c in enumerate(df_tam['categoria'].unique())}
        fig_t = px.bar(df_tam, x='anio', y='valor', color='categoria',
                       barmode='stack', text_auto='.1f',
                       color_discrete_map=cmap_t,
                       title='% por tamaño de UA',
                       labels={'valor':'%','anio':'Año','categoria':'Tamaño'})
        fig_t.update_layout(yaxis_range=[0,105], **layout())
        st.plotly_chart(fig_t, use_container_width=True)

    with c2:
        df_np = to_df(D['num_parc'])
        cmap_np = {c: PAL8[i] for i,c in enumerate(df_np['categoria'].unique())}
        fig_np = px.bar(df_np, x='anio', y='valor', color='categoria',
                        barmode='stack', text_auto='.1f',
                        color_discrete_map=cmap_np,
                        title='% por número de parcelas',
                        labels={'valor':'%','anio':'Año','categoria':'N° parcelas'})
        fig_np.update_layout(yaxis_range=[0,105], **layout())
        st.plotly_chart(fig_np, use_container_width=True)

    # Tendencias cruzadas
    st.markdown('<div class="sec">Tendencias de concentración de tierra</div>',
                unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        df_tam_l = to_df(D['tam_ua'])
        fig_tl = px.line(df_tam_l, x='anio', y='valor', color='categoria',
                         color_discrete_map=cmap_t, markers=True,
                         title='Evolución % tamaño UA por año',
                         labels={'valor':'%','anio':'Año','categoria':'Tamaño'})
        fig_tl.update_traces(line_width=2.5, marker_size=8)
        fig_tl.update_layout(**layout())
        st.plotly_chart(fig_tl, use_container_width=True)

    with c4:
        # Delta tamaño UA
        rows_d = []
        for cat, yvals in D['tam_ua'].items():
            if 2023 in yvals and 2025 in yvals:
                rows_d.append({'Tamaño UA': cat, 'Δ pp': round(yvals[2025]-yvals[2023],1)})
        df_d = pd.DataFrame(rows_d)
        cols_d = [C['verde'] if v>=0 else C['rojo'] for v in df_d['Δ pp']]
        fig_d = go.Figure(go.Bar(
            x=df_d['Tamaño UA'], y=df_d['Δ pp'],
            marker_color=cols_d,
            text=[f"{v:+.1f}pp" for v in df_d['Δ pp']], textposition='outside'))
        fig_d.update_layout(title='Cambio en distribución de tamaño UA (pp 2023→2025)',
                             yaxis=dict(title='Puntos porcentuales'), **layout())
        st.plotly_chart(fig_d, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 5 — TABLA RESUMEN
# ════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="sec">Tabla comparativa · todos los indicadores</div>',
                unsafe_allow_html=True)

    rows = []
    rows.append({'Indicador':'Total productores','Categoría':'Total',
                 '2023':f"{tot[2023]:,.0f}",'2024':f"{tot[2024]:,.0f}",'2025':f"{tot[2025]:,.0f}",
                 'Δ 2023→2025':f"{d_pct:+.1f}%"})

    grupos = [
        ('sexo','% Sexo'),('edad','% Edad'),('educ','% Educación'),
        ('tam_ua','% Tamaño UA'),('num_parc','% N° parcelas'),
        ('usos_pct','% Usos sup. agríc.'),('etnicidad','% Etnicidad'),
    ]
    for key, lbl in grupos:
        for cat, yvals in D[key].items():
            v23 = yvals.get(2023,np.nan); v25 = yvals.get(2025,np.nan)
            delta = f"{v25-v23:+.1f}pp" if not np.isnan(v23) and not np.isnan(v25) else "—"
            rows.append({'Indicador':lbl,'Categoría':cat,
                         '2023':f"{yvals.get(2023,'—'):.1f}%" if isinstance(yvals.get(2023),float) else "—",
                         '2024':f"{yvals.get(2024,'—'):.1f}%" if isinstance(yvals.get(2024),float) else "—",
                         '2025':f"{yvals.get(2025,'—'):.1f}%" if isinstance(yvals.get(2025),float) else "—",
                         'Δ 2023→2025':delta})

    for cat, yvals in D['esp_12m'].items():
        v23 = yvals.get(2023,np.nan); v25 = yvals.get(2025,np.nan)
        pct = f"{(v25-v23)/v23*100:+.1f}%" if not np.isnan(v23) and not np.isnan(v25) and v23!=0 else "—"
        rows.append({'Indicador':'N° cabezas (12m)','Categoría':cat,
                     '2023':f"{yvals.get(2023,0):,.0f}",'2024':f"{yvals.get(2024,0):,.0f}",
                     '2025':f"{yvals.get(2025,0):,.0f}",'Δ 2023→2025':pct})

    df_tabla = pd.DataFrame(rows)

    def color_d(val):
        if isinstance(val,str) and val.startswith('+'): return 'color:#1d9e75;font-weight:600'
        if isinstance(val,str) and val.startswith('-'): return 'color:#d85a30;font-weight:600'
        return ''

    st.dataframe(df_tabla.style.map(color_d, subset=['Δ 2023→2025']),
                 use_container_width=True, hide_index=True, height=500)

    csv = df_tabla.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Descargar CSV", csv,
                       "ena_resumen_nacional_2023_2025.csv", "text/csv")

# ── Fuente ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="fuente">
Fuente: INEI — Encuesta Nacional Agropecuaria (ENA) 2023, 2024 y 2025.
Elaboración propia. Estimaciones a nivel nacional (estimaciones puntuales).
* Proyección lineal indicativa basada en tendencia 2023–2025.
</div>
""", unsafe_allow_html=True)
