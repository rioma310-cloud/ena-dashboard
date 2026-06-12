"""
ENA 2023–2025 · Perfil del Productor Agropecuario Nacional
Dashboard Ejecutivo Premium — Optimizado para Alta Gerencia (INEI / MIDAGRI)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io

# ── Configuración de Página Avanzada ─────────────────────────────────────────
st.set_page_config(
    page_title="ENA · Panel de Control del Perfil Productivo Nacional",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sistema de Autenticación Institucional ───────────────────────────────────
def check_password():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.markdown("""
        <div style="max-width:420px; margin:80px auto; padding:40px;
                    background:#FFFFFF; border-radius:16px;
                    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
                    text-align:center; border-top: 5px solid #1E3A8A;">
          <div style="font-size:48px; margin-bottom:12px;">🌾</div>
          <div style="font-size:20px; font-weight:700; color:#0F172A; margin-bottom:6px; font-family:'Inter',sans-serif;">
            Sistema de Inteligencia de Datos ENA</div>
          <div style="font-size:13px; color:#64748B; margin-bottom:28px; font-family:'Inter',sans-serif;">
            Instituto Nacional de Estadística e Informática — Uso Restringido</div>
        </div>
        """, unsafe_allow_html=True)

        col = st.columns([1, 1.8, 1])[1]
        with col:
            clave = st.text_input("Credencial de Acceso Corporativo", type="password",
                                  placeholder="Ingrese el token de seguridad")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Autenticar Conexión", use_container_width=True):
                if clave == "ENA_INEI_2025":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("🔒 Credencial inválida. Acceso denegado.")
        st.stop()

check_password()

# ── Matriz de Estilos e Identidad Visual (Paleta Power BI Premium) ───────────
C = {
    "primary": "#1E3A8A",      # Azul Institucional Profundo
    "secondary": "#0F766E",    # Verde Tecla Calidad
    "accent": "#7C3AED",       # Morado de Contraste
    "warning": "#EA580C",      # Naranja de Alerta
    "danger": "#DC2626",       # Rojo de Desviación Critica
    "success": "#16A34A",      # Verde Cumplimiento
    "dark": "#0F172A",         # Gris Oscuro de Texto
    "light": "#F8FAFC",        # Fondo Neutro Claro
    "border": "#E2E8F0"        # Bordes Suaves
}

PAL8 = ["#1E3A8A", "#0F766E", "#7C3AED", "#EA580C", "#0891B2", "#16A34A", "#DC2626", "#64748B"]

YEARS = [2023, 2024, 2025, 2026]
YR19 = {2023: 19, 2024: 21, 2025: 23, 2026: 25}   
YR20 = {2023: 20, 2024: 22, 2025: 24, 2026: 26}   

# ── Arquitectura CSS Inyectada Avanzada ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stMarkdown {
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: #F8FAFC;
}

[data-testid="stSidebar"] {
    background-color: #0F172A !important;
}

[data-testid="stSidebar"] * {
    color: #F8FAFC !important;
}

/* Rediseño de Pestañas Tipo Nav-Pills de Power BI */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #E2E8F0;
    padding: 6px;
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
    padding: 10px 20px;
    background-color: transparent;
    border-radius: 8px;
    color: #475569;
    font-weight: 600;
    border: none;
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background-color: #1E3A8A !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Bloques de Tarjetas de Control KPI */
.kpi-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
}

.kpi-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.kpi-title {
    color: #64748B;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.kpi-main-val {
    font-size: 28px;
    font-weight: 700;
    color: #0F172A;
    line-height: 1.2;
}

/* Sistema Estricto de Semáforos Corporativos */
.semaforo-verde {
    background-color: #DCFCE7;
    color: #15803D;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}

.semaforo-amarillo {
    background-color: #FEF9C3;
    color: #A16207;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}

.semaforo-rojo {
    background-color: #FEE2E2;
    color: #B91C1C;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}

/* Sección Contenedora Informativa */
.executive-insight-box {
    background: #F0F9FF;
    border-left: 4px solid #0284C7;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 20px;
}

.section-header-panel {
    font-size: 18px;
    font-weight: 700;
    color: #0F172A;
    margin: 25px 0 15px 0;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 6px;
}

.fuente-footer {
    font-size: 11px;
    color: #94A3B8;
    margin-top: 40px;
    border-top: 1px solid #E2E8F0;
    padding-top: 12px;
}
</style>
""", unsafe_allow_html=True)


# ── Motor de Ingesta y ETL Optimizado (Caché Atómica) ───────────────────────
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
                    try: vals[yr] = round(float(v)/1e6, 3)  
                    except: pass
            if vals: out[lbl] = vals
        return out

    d = {}
    d['total']        = total('total_productores')
    d['sexo']         = categ('1.2.1_sexo',          2)
    d['edad']         = categ('1.1.1_edad_3',         4)
    d['educ']         = categ('1.5.1_nivel_educ_a',   5)
    d['tam_ua']       = categ('4.1.1_tam_ua_2',       4)
    d['usos_pct']     = {  
        'Sup. sembrada':      {2023:43.7, 2024:43.1, 2025:44.9},
        'Sup. en barbecho':   {2023:12.7, 2024:12.5, 2025: 6.1},
        'Tierras inactivas':  {2023:33.8, 2024:33.5, 2025:41.5},
        'Sup. en descanso':   {2023: 9.8, 2024:11.0, 2025: 7.6},
    }
    d['num_parc']     = categ('4.1.2_num_parc', 5)
    d['esp_12m']      = especies('num_especi_ult12mes', label_col=1)
    d['prod_12m']     = especies('num_prod_ult12mes',   label_col=2)
    d['sup_abs']      = sup_abs('sup_usos_tierra_abs')

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

# ── Generador Estricto de Plantilla Gráfica (Estilo Power BI) ────────────────
def apply_premium_layout(fig, title_text, y_title="", x_title="", is_bar=False):
    fig.update_layout(
        title=dict(
            text=f"<b>{title_text}</b>",
            font=dict(size=15, color="#0F172A"),
            x=0.01,
            y=0.95
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Inter, sans-serif", size=12, color="#334155"),
        margin=dict(t=55, b=40, l=15, r=15),
        height=380,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
            title_text=""
        ),
        hovermode="x unified"
    )
    fig.update_xaxes(
        title_text=x_title,
        showgrid=False,
        showline=True,
        linecolor="#CBD5E1",
        tickfont=dict(size=11)
    )
    fig.update_yaxes(
        title_text=y_title,
        showgrid=True,
        gridcolor="#E2E8F0",
        showline=False,  # Corrección: Desactiva la línea lateral limpiamente en vez de forzar color transparente
        tickfont=dict(size=11)
    )
    if is_bar:
        fig.update_layout(bargap=0.25, bargroupgap=0.05)
    return fig

# ── Panel Lateral Corporativo ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0px; text-align: center;">
        <span style="font-size: 40px;">🏛️</span>
        <h3 style="margin-top:10px; font-size:18px; font-weight:700;">Consola de Datos ENA</h3>
        <p style="font-size:12px; color:#94A3B8; opacity:0.8;">Órgano de Auditoría y Control Operativo</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    uploaded = st.file_uploader(
        "Cargar Repositorio Estructural (.XLSX)",
        type=["xlsx"],
        help="Cargue la matriz de datos de la Encuesta Nacional Agropecuaria oficial."
    )
    
    st.markdown("---")
    st.markdown("### 📋 Variables Fiscalizadas")
    variables = ["Productores", "Sexo", "Edad", "Educación", "Etnicidad", "UA", "Parcelas", "Ganadería", "Superficie"]
    for x in variables:
        st.markdown(f"<span style='color:#34D399;'>✔</span> {x}", unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Dirección Nacional de Censos y Encuestas")

# ── Estado de Espera / Landing sin Archivo ────────────────────────────────────
if uploaded is None:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%); padding: 50px; border-radius: 20px; color: white; text-align: center; margin-top: 30px;">
        <h1 style="font-weight: 800; font-size: 32px; margin-bottom: 10px;">Sistema de Monitoreo Analítico de la Estructura Agropecuaria Nacional</h1>
        <p style="font-size: 15px; opacity: 0.85; max-width: 700px; margin: 0 auto 30px auto;">
            Herramienta ejecutiva de visualización de microdatos estadísticos correspondientes a la Encuesta Nacional Agropecuaria (ENA). Permite el análisis dinámico de la evolución temporal y distribución sociodemográfica del sector.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 Conexión en espera. Por favor, cargue el archivo Excel estructurado en el panel de control izquierdo para inicializar los motores gráficos.")
    st.stop()

# ── Lectura y Procesamiento de Datos ─────────────────────────────────────────
with st.spinner("Ejecutando algoritmos de segmentación y carga matricial..."):
    D = leer(uploaded.read())

# ── Encabezado Institucional Premium ─────────────────────────────────────────
st.markdown("""
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; padding: 20px 30px; border-radius: 14px; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.05); margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center;">
    <div>
        <h1 style="color: #0F172A; font-size: 24px; font-weight: 700; margin: 0;">Panel Ejecutivo Nacional de la Estructura Agropecuaria</h1>
        <p style="color: #64748B; font-size: 13px; margin: 4px 0 0 0;">Reporte de consistencia y evolución de indicadores clave · ENA</p>
    </div>
    <div style="text-align: right;">
        <span style="background: #EFF6FF; color: #1E3A8A; font-size: 11px; font-weight: 700; padding: 6px 12px; border-radius: 20px; border: 1px solid #BFDBFE;">
            ÁMBITO: NACIONAL
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Motor del Sistema de Semáforos y KPIs Reales ─────────────────────────────
tot = D['total']
yr_max  = max(yr for yr in YEARS if yr in tot)
yr_prev = yr_max - 1 if (yr_max - 1) in tot else sorted(tot.keys())[-2]

d_abs  = tot[yr_max] - tot[yr_prev]
d_pct  = (tot[yr_max] - tot[2023]) / tot[2023] * 100

# Lógica del semáforo institucional corporativo
if d_pct > 2.0:
    semaforo_clase = "semaforo-verde"
    semaforo_texto = f"CRECIMIENTO OPTIMIZADO ({d_pct:+.1f}%)"
elif d_pct >= 0:
    semaforo_clase = "semaforo-amarillo"
    semaforo_texto = f"ESTABILIDAD CRÍTICA ({d_pct:+.1f}%)"
else:
    semaforo_clase = "semaforo-rojo"
    semaforo_texto = f"ALERTA CONTRAÍDA ({d_pct:+.1f}%)"

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-header">
            <span class="kpi-title">Volumen Total de Productores</span>
            <span style="font-size:16px;">👨‍🌾</span>
        </div>
        <div>
            <div class="kpi-main-val">{tot[yr_max]/1000000:.3f} M</div>
            <div style="margin-top: 8px;"><span class="{semaforo_clase}">{semaforo_texto}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-header">
            <span class="kpi-title">Variación Anual Absoluta</span>
            <span style="font-size:16px;">📈</span>
        </div>
        <div>
            <div class="kpi-main-val">{d_abs:+,.0f}</div>
            <div style="margin-top: 8px; font-size:12px; color:#64748B;">vs. periodo anual {yr_prev}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-header">
            <span class="kpi-title">Último Cierre de Campaña</span>
            <span style="font-size:16px;">📅</span>
        </div>
        <div>
            <div class="kpi-main-val">{yr_max}</div>
            <div style="margin-top: 8px; font-size:12px; color:#16A34A; font-weight:600;">Consolidado Oficial</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-header">
            <span class="kpi-title">Comportamiento Sectorial</span>
            <span style="font-size:16px;">📊</span>
        </div>
        <div>
            <div class="kpi-main-val">{"Tendencia Ascendente" if d_pct>0 else "Tendencia Negativa"}</div>
            <div style="margin-top: 8px; font-size:12px; color:#64748B;">Línea base: Ciclo 2023</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Sección de Resumen Ejecutivo de Datos ───────────────────────────────────
st.markdown(f"<div class='executive-insight-box'>"
            f"<b>Resumen Crítico de Inteligencia Sectorial:</b> Al cierre del ejercicio fiscal <b>{yr_max}</b>, el número consolidado "
            f"de unidades productoras a nivel nacional experimentó una variación neta del <b>{d_pct:+.2f}%</b> en comparación con "
            f"el ciclo básico del 2023. Los componentes demográficos revelan cambios estructurales profundos en la distribución "
            f"por grupos etarios y niveles de instrucción formal alcanzados."
            f"</div>", unsafe_allow_html=True)

# ── Estructura de Navegación por Pestañas Técnicas ───────────────────────────
tabs = st.tabs([
    "📈 Evolución General",
    "👤 Perfil del Productor",
    "🐄 Sector Pecuario",
    "🌱 Capacidad de Superficie",
    "🏡 Infraestructura UA",
    "📋 Auditoría de Tablas"
])

# ════════════════════════════════════════════════════════
# TAB 1 — EVOLUCIÓN GENERAL
# ════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("<div class='section-header-panel'>Dinámica y Proyección del Volumen Nacional de Productores</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1.6, 1])
    with c1:
        yv = [tot[y] for y in YEARS if y in tot]
        yrs_disp = [y for y in YEARS if y in tot]
        x_num = np.arange(len(yrs_disp))
        coef = np.polyfit(x_num, yv, 1)
        yr_proj = max(yrs_disp) + 1
        y_proj = np.polyval(coef, len(yrs_disp))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[str(y) for y in yrs_disp], y=yv,
            mode='lines+markers+text',
            line=dict(color=C['primary'], width=3.5),
            marker=dict(size=10, color=C['primary'], line=dict(color="white", width=2)),
            text=[f"{v/1e6:.2f} M" for v in yv],
            textposition="top center",
            fill="tozeroy",
            fillcolor="rgba(30,58,138,0.06)",
            name="Histórico Registrado"
        ))

        if yr_proj not in tot:
            fig.add_trace(go.Scatter(
                x=[str(max(yrs_disp)), f"{yr_proj}*"], y=[yv[-1], y_proj],
                mode='lines+markers',
                line=dict(color=C['warning'], width=2, dash='dash'),
                marker=dict(size=8, symbol='diamond', color=C['warning']),
                name=f"Proyección Tendencial {yr_proj}"
            ))

        fig = apply_premium_layout(fig, "Evolución nacional de productores agropecuarios", "Volumen de Productores", "Ciclo Estadístico")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        df_s = to_df(D['sexo'])
        fig2 = px.bar(df_s, x='anio', y='valor', color='categoria', barmode='group',
                      color_discrete_map={'Hombre': C['primary'], 'Mujer': '#F43F5E'},
                      text_auto='.1f',
                      labels={'valor': 'Participación (%)', 'anio': 'Año', 'categoria': 'Segmento'})
        fig2.update_traces(textfont_size=11, textposition='outside', cliponaxis=False)
        fig2 = apply_premium_layout(fig2, "Distribución de productores por sexo (%)", "Porcentaje", "Año", is_bar=True)
        fig2.update_layout(yaxis_range=[0, 95])
        st.plotly_chart(fig2, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 2 — PERFIL DEL PRODUCTOR
# ════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("<div class='section-header-panel'>Indicadores Sociodemográficos Estructurales del Productor</div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        df_e = to_df(D['edad'])
        cmap = {c: PAL8[i % len(PAL8)] for i, c in enumerate(df_e['categoria'].unique())}
        fig3 = px.line(df_e, x='anio', y='valor', color='categoria',
                       color_discrete_map=cmap, markers=True,
                       labels={'valor': 'Porcentaje', 'anio': 'Año', 'categoria': 'Rango'})
        fig3.update_traces(line_width=2.5, marker_size=7)
        fig3 = apply_premium_layout(fig3, "Participación de productores por grupos etarios (%)", "Porcentaje", "Año")
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        df_ed = to_df(D['educ'])
        fig4 = px.bar(df_ed, x='valor', y='categoria', color='anio', barmode='group',
                      orientation='h', text_auto='.1f',
                      color_discrete_map={2023: C['secondary'], 2024: C['primary'], 2025: C['warning']},
                      labels={'valor': 'Porcentaje', 'categoria': 'Grado Académico', 'anio': 'Periodo'})
        fig4.update_traces(textfont_size=10)
        fig4 = apply_premium_layout(fig4, "Nivel educativo alcanzado por los productores (%)", "Categoría de Instrucción", "Porcentaje", is_bar=True)
        fig4.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<div class='section-header-panel'>Autoidentificación Ancestral y Étnica</div>", unsafe_allow_html=True)
    df_et = to_df(D['etnicidad'])
    if not df_et.empty:
        cmap_et = {c: PAL8[i % len(PAL8)] for i, c in enumerate(df_et['categoria'].unique())}
        fig_et = px.line(df_et, x='anio', y='valor', color='categoria',
                         color_discrete_map=cmap_et, markers=True,
                         labels={'valor': 'Proporción %', 'anio': 'Año', 'categoria': 'Etnia'})
        fig_et.update_traces(line_width=2.5, marker_size=7)
        fig_et = apply_premium_layout(fig_et, "Perfil de autoidentificación étnica del productor (%)", "Porcentaje", "Año")
        st.plotly_chart(fig_et, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 3 — SECTOR PECUARIO
# ════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("<div class='section-header-panel'>Inventario Pecuario y Concentración Operativa</div>", unsafe_allow_html=True)
    df_esp = to_df(D['esp_12m'], val='cabezas')
    c1, c2 = st.columns(2)

    with c1:
        esp_princ = ['Cuyes','Ovinos','Vacunos','Gallinas'] if 'Gallinas' in D['esp_12m'] else ['Cuyes','Ovinos','Vacunos','Porcinos']
        df_p = df_esp[df_esp['categoria'].isin(esp_princ)]
        fig_p = px.bar(df_p, x='anio', y='cabezas', color='categoria', barmode='group',
                       color_discrete_map={c: PAL8[i % len(PAL8)] for i, c in enumerate(esp_princ)},
                       text_auto='.2s',
                       labels={'cabezas': 'Unidades de Ganado', 'anio': 'Año', 'categoria': 'Especie'})
        fig_p = apply_premium_layout(fig_p, "Evolución de las existencias por especies ganaderas principales (cabezas)", "Cabezas", "Año", is_bar=True)
        st.plotly_chart(fig_p, use_container_width=True)

    with c2:
        cmap_e = {c: PAL8[i % len(PAL8)] for i, c in enumerate(df_esp['categoria'].unique())}
        fig_e2 = px.line(df_esp, x='anio', y='cabezas', color='categoria',
                         color_discrete_map=cmap_e, markers=True,
                         labels={'cabezas': 'Volumen', 'anio': 'Año', 'categoria': 'Especie'})
        fig_e2.update_traces(line_width=2.5, marker_size=7)
        fig_e2 = apply_premium_layout(fig_e2, "Tendencia general del stock ganadero nacional (cabezas)", "Cabezas", "Año")
        st.plotly_chart(fig_e2, use_container_width=True)

    st.markdown("<div class='section-header-panel'>Análisis Transversal de Productores Pecuarios</div>", unsafe_allow_html=True)
    df_prod = to_df(D['prod_12m'], val='productores')
    c3, c4 = st.columns(2)

    with c3:
        fig_pr = px.bar(df_prod, x='categoria', y='productores', color='anio', barmode='group',
                        color_discrete_map={2023: C['secondary'], 2024: C['primary'], 2025: C['warning']},
                        text_auto='.2s',
                        labels={'productores': 'Volumen Activos', 'categoria': 'Línea Explotación', 'anio': 'Año'})
        fig_pr = apply_premium_layout(fig_pr, "Distribución de productores pecuarios por sector zootécnico", "Productores", "Especie", is_bar=True)
        st.plotly_chart(fig_pr, use_container_width=True)

    with c4:
        rows_var = []
        for esp, yvals in D['prod_12m'].items():
            if 2023 in yvals and 2025 in yvals:
                delta = (yvals[2025] - yvals[2023]) / yvals[2023] * 100
                rows_var.append({'Especie': esp, 'Δ% 2023→2025': round(delta, 1)})
        df_var = pd.DataFrame(rows_var).sort_values('Δ% 2023→2025')
        colors_bar = [C['secondary'] if v >= 0 else C['danger'] for v in df_var['Δ% 2023→2025']]
        
        fig_var = go.Figure(go.Bar(
            x=df_var['Δ% 2023→2025'], y=df_var['Especie'],
            orientation='h', marker_color=colors_bar,
            text=[f"{v:+.1f}%" for v in df_var['Δ% 2023→2025']],
            textposition='outside'
        ))
        fig_var = apply_premium_layout(fig_var, "Variación relativa de unidades ganaderas productoras (2023→2025)", "% Variación", "Especie")
        st.plotly_chart(fig_var, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 4 — SUPERFICIE AGRÍCOLA
# ════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("<div class='section-header-panel'>Balances de Uso de Suelo Operativo y Desuso Absoluto</div>", unsafe_allow_html=True)
    df_sa = to_df(D['sup_abs'], val='millones_ha')
    c1, c2 = st.columns(2)

    with c1:
        cats_area = ['Sup. agrícola total','Sup. sembrada','Sup. en barbecho','Tierras inactivas','Sup. en descanso']
        df_main = df_sa[df_sa['categoria'].isin(cats_area)]
        cmap_a = {c: PAL8[i % len(PAL8)] for i, c in enumerate(cats_area)}
        fig_a = px.line(df_main, x='anio', y='millones_ha', color='categoria',
                        color_discrete_map=cmap_a, markers=True,
                        labels={'millones_ha': 'Hectáreas (M)', 'anio': 'Ciclo', 'categoria': 'Tipo de Suelo'})
        fig_a.update_traces(line_width=2.5, marker_size=7)
        fig_a = apply_premium_layout(fig_a, "Evolución de componentes esenciales de la superficie agrícola (M ha)", "Millones de Hectáreas", "Año")
        st.plotly_chart(fig_a, use_container_width=True)

    with c2:
        cats_noagri = ['Sup. no agrícola','Pastos nat. manejados','Pastos no manejados','Montes y bosques']
        df_na = df_sa[df_sa['categoria'].isin(cats_noagri)]
        cmap_na = {c: PAL8[(i+4) % len(PAL8)] for i, c in enumerate(cats_noagri)}
        fig_na = px.line(df_na, x='anio', y='millones_ha', color='categoria',
                         color_discrete_map=cmap_na, markers=True,
                         labels={'millones_ha': 'Hectáreas (M)', 'anio': 'Ciclo', 'categoria': 'Uso'})
        fig_na.update_traces(line_width=2.5, marker_size=7)
        fig_na = apply_premium_layout(fig_na, "Evolución de coberturas y tierras no agrícolas (M ha)", "Millones de Hectáreas", "Año")
        st.plotly_chart(fig_na, use_container_width=True)

    st.markdown("<div class='section-header-panel'>Proporciones Relativas de Uso de Suelo</div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        df_up = to_df(D['usos_pct'])
        cmap_up = {c: PAL8[i % len(PAL8)] for i, c in enumerate(df_up['categoria'].unique())}
        fig_up = px.line(df_up, x='anio', y='valor', color='categoria',
                         color_discrete_map=cmap_up, markers=True,
                         labels={'valor': '%', 'anio': 'Año', 'categoria': 'Uso'})
        fig_up.update_traces(line_width=2.5, marker_size=7)
        fig_up = apply_premium_layout(fig_up, "Estructura de distribución porcentual del uso de la tierra (%)", "Porcentaje", "Año")
        st.plotly_chart(fig_up, use_container_width=True)

    with c4:
        rows_w = []
        for cat, yvals in D['sup_abs'].items():
            if 2023 in yvals and 2025 in yvals:
                rows_w.append({'Uso': cat, 'Δ M ha': round(yvals[2025]-yvals[2023],3)})
        df_w = pd.DataFrame(rows_w).sort_values('Δ M ha')
        cols_w = [C['secondary'] if v >= 0 else C['danger'] for v in df_w['Δ M ha']]
        
        fig_w = go.Figure(go.Bar(
            x=df_w['Δ M ha'], y=df_w['Uso'], orientation='h',
            marker_color=cols_w,
            text=[f"{v:+.3f}" for v in df_w['Δ M ha']], textposition='outside'
        ))
        fig_w = apply_premium_layout(fig_w, "Desviación neta de superficie agrícola agregada (M ha, 2023→2025)", "Variación Neta M ha", "Tipología")
        st.plotly_chart(fig_w, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 5 — INFRAESTRUCTURA UA
# ════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("<div class='section-header-panel'>Análisis Microestructural del Fraccionamiento y Dimensión Operativa</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        df_tam = to_df(D['tam_ua'])
        cmap_t = {c: PAL8[i % len(PAL8)] for i, c in enumerate(df_tam['categoria'].unique())}
        fig_t = px.bar(df_tam, x='anio', y='valor', color='categoria', barmode='stack', text_auto='.1f',
                       color_discrete_map=cmap_t,
                       labels={'valor': '% Relativo', 'anio': 'Año', 'categoria': 'Dimensión'})
        fig_t = apply_premium_layout(fig_t, "Distribución de las unidades agropecuarias por estrato de tamaño (%)", "Porcentaje Acumulado", "Año", is_bar=True)
        fig_t.update_layout(yaxis_range=[0, 105])
        st.plotly_chart(fig_t, use_container_width=True)

    with c2:
        df_np = to_df(D['num_parc'])
        cmap_np = {c: PAL8[i % len(PAL8)] for i, c in enumerate(df_np['categoria'].unique())}
        fig_np = px.bar(df_np, x='anio', y='valor', color='categoria', barmode='stack', text_auto='.1f',
                        color_discrete_map=cmap_np,
                        labels={'valor': '% Relativo', 'anio': 'Año', 'categoria': 'Fraccionamiento'})
        fig_np = apply_premium_layout(fig_np, "Distribución de las unidades agropecuarias según número de parcelas internas (%)", "Porcentaje Acumulado", "Año", is_bar=True)
        fig_np.update_layout(yaxis_range=[0, 105])
        st.plotly_chart(fig_np, use_container_width=True)

    st.markdown("<div class='section-header-panel'>Dinámica de la Concentración y Tenencia de Tierras</div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        df_tam_l = to_df(D['tam_ua'])
        fig_tl = px.line(df_tam_l, x='anio', y='valor', color='categoria', color_discrete_map=cmap_t, markers=True,
                         labels={'valor': '%', 'anio': 'Año', 'categoria': 'Estrato'})
        fig_tl.update_traces(line_width=2.5, marker_size=7)
        fig_tl = apply_premium_layout(fig_tl, "Evolución temporal por estratos superficiales de la UA", "Porcentaje", "Año")
        st.plotly_chart(fig_tl, use_container_width=True)

    with c4:
        rows_d = []
        for cat, yvals in D['tam_ua'].items():
            if 2023 in yvals and 2025 in yvals:
                rows_d.append({'Tamaño UA': cat, 'Δ pp': round(yvals[2025]-yvals[2023], 1)})
        df_d = pd.DataFrame(rows_d)
        cols_d = [C['secondary'] if v >= 0 else C['danger'] for v in df_d['Δ pp']]
        
        fig_d = go.Figure(go.Bar(
            x=df_d['Tamaño UA'], y=df_d['Δ pp'],
            marker_color=cols_d,
            text=[f"{v:+.1f} pp" for v in df_d['Δ pp']], textposition='outside'
        ))
        fig_d = apply_premium_layout(fig_d, "Desviación interanual en puntos porcentuales (pp 2023→2025)", "Variación (pp)", "Estrato")
        st.plotly_chart(fig_d, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 6 — AUDITORÍA DE TABLAS
# ════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("<div class='section-header-panel'>Consolidado Multidimensional de Control Técnico de Indicadores</div>", unsafe_allow_html=True)

    rows = []
    rows.append({'Indicador': 'Evolución nacional de productores agropecuarios', 'Categoría': 'Total Agregado',
                 '2023': f"{tot[2023]:,.0f}", '2024': f"{tot[2024]:,.0f}", '2025': f"{tot[2025]:,.0f}",
                 'Δ 2023→2025': f"{d_pct:+.1f}%"})

    grupos = [
        ('sexo', 'Participación de productores por sexo (%)'),
        ('edad', 'Participación de productores por grupos etarios (%)'),
        ('educ', 'Nivel educativo alcanzado por los productores (%)'),
        ('tam_ua', 'Unidades agropecuarias por estrato de tamaño (%)'),
        ('num_parc', 'Unidades agropecuarias según número de parcelas (%)'),
        ('usos_pct', 'Estructura distributiva del uso de tierra (%)'),
        ('etnicidad', 'Perfil de autoidentificación étnica del productor (%)'),
    ]
    for key, lbl in grupos:
        for cat, yvals in D[key].items():
            v23 = yvals.get(2023, np.nan); v25 = yvals.get(2025, np.nan)
            delta = f"{v25-v23:+.1f} pp" if not np.isnan(v23) and not np.isnan(v25) else "—"
            rows.append({'Indicador': lbl, 'Categoría': cat,
                         '2023': f"{yvals.get(2023,'—'):.1f}%" if isinstance(yvals.get(2023), float) else "—",
                         '2024': f"{yvals.get(2024,'—'):.1f}%" if isinstance(yvals.get(2024), float) else "—",
                         '2025': f"{yvals.get(2025,'—'):.1f}%" if isinstance(yvals.get(2025), float) else "—",
                         'Δ 2023→2025': delta})

    for cat, yvals in D['esp_12m'].items():
        v23 = yvals.get(2023, np.nan); v25 = yvals.get(2025, np.nan)
        pct = f"{(v25-v23)/v23*100:+.1f}%" if not np.isnan(v23) and not np.isnan(v25) and v23 != 0 else "—"
        rows.append({'Indicador': 'Existencias de ganado (cabezas)', 'Categoría': cat,
                     '2023': f"{yvals.get(2023,0):,.0f}", '2024': f"{yvals.get(2024,0):,.0f}",
                     '2025': f"{yvals.get(2025,0):,.0f}", 'Δ 2023→2025': pct})

    df_tabla = pd.DataFrame(rows)

    # Inyección de estilos dinámicos para columnas de variaciones (Semáforo de Celdas)
    def style_variations(val):
        if isinstance(val, str) and ('+' in val or '%' in val) and not '-' in val:
            return 'background-color: #DCFCE7; color: #15803D; font-weight: bold; border-radius:4px;'
        if isinstance(val, str) and '-' in val:
            return 'background-color: #FEE2E2; color: #B91C1C; font-weight: bold; border-radius:4px;'
        return 'color: #475569;'

    st.dataframe(
        df_tabla.style.map(style_variations, subset=['Δ 2023→2025']),
        use_container_width=True,
        hide_index=True,
        height=550
    )

    st.markdown("<br>", unsafe_allow_html=True)
    csv = df_tabla.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Exportar Matriz Consolidada (CSV)", csv, "ena_analisis_macro_nacional.csv", "text/csv")

# ── Pie de Página Oficial ────────────────────────────────────────────────────
st.markdown("""
<div class="fuente-footer">
    <b>Fuente Oficial de Microdatos:</b> Instituto Nacional de Estadística e Informática (INEI) — Encuesta Nacional Agropecuaria (ENA) 2023, 2024 y 2025.<br>
    * La proyección paramétrica calculada representa una estimación lineal indicativa de mínimos cuadrados y carece de naturaleza predictiva oficial vinculante.
</div>
""", unsafe_allow_html=True)
