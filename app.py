"""
ENA · Panel Ejecutivo de Monitoreo del Productor Agropecuario Nacional
INEI — Dirección Nacional de Censos y Encuestas
Versión 2.0 — Dashboard Ejecutivo Integral
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io

st.set_page_config(
    page_title="ENA · Panel Ejecutivo Nacional",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Autenticación ─────────────────────────────────────────────────────────────
def check_password():
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if not st.session_state.auth:
        st.markdown("""
        <div style="max-width:400px;margin:90px auto;padding:44px 40px;
                    background:#fff;border-radius:16px;text-align:center;
                    box-shadow:0 8px 32px rgba(30,58,138,0.13);
                    border-top:5px solid #1E3A8A;">
          <div style="font-size:44px;margin-bottom:10px;">🌾</div>
          <div style="font-size:19px;font-weight:700;color:#0F172A;margin-bottom:4px;">
            Panel Ejecutivo ENA</div>
          <div style="font-size:12px;color:#64748B;margin-bottom:26px;">
            INEI · Dirección Nacional de Censos y Encuestas<br>
            <b>Acceso restringido — solo personal autorizado</b></div>
        </div>""", unsafe_allow_html=True)
        col = st.columns([1,1.6,1])[1]
        with col:
            pw = st.text_input("Contraseña", type="password", placeholder="Ingrese la clave de acceso")
            if st.button("Ingresar", use_container_width=True):
                if pw == "ENA_INEI_2025":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta.")
        st.stop()

check_password()

# ── Paleta y constantes ───────────────────────────────────────────────────────
C = dict(
    azul="#1E3A8A", verde="#0F766E", lila="#7C3AED", naranja="#EA580C",
    teal="#0891B2", exito="#16A34A", rojo="#DC2626", gris="#64748B",
    azul_lt="#EFF6FF", verde_lt="#F0FDF4", naranja_lt="#FFF7ED"
)
PAL = ["#1E3A8A","#0F766E","#7C3AED","#EA580C","#0891B2","#16A34A","#DC2626","#64748B",
       "#0284C7","#15803D","#9333EA","#C2410C"]

YEARS = [2023, 2024, 2025, 2026]
YR19  = {2023:19, 2024:21, 2025:23, 2026:25}   # hojas con col estimación en posición par+1
YR20  = {2023:20, 2024:22, 2025:24, 2026:26}   # hojas de cruce sexo

# ── CSS ejecutivo ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
*, .stMarkdown { font-family:'Inter',sans-serif !important; }
[data-testid="stAppViewContainer"] { background:#F1F5F9; }
[data-testid="stSidebar"] { background:#0F172A !important; }
[data-testid="stSidebar"] * { color:#F8FAFC !important; }
.stTabs [data-baseweb="tab-list"] { gap:6px; background:#E2E8F0; padding:5px; border-radius:10px; }
.stTabs [data-baseweb="tab"] { padding:9px 18px; border-radius:7px; color:#475569; font-weight:600; border:none; }
.stTabs [aria-selected="true"] { background:#1E3A8A !important; color:#fff !important; box-shadow:0 2px 6px rgba(30,58,138,0.25); }
.kpi { background:#fff; border:1px solid #E2E8F0; border-radius:12px; padding:18px 20px;
       box-shadow:0 1px 3px rgba(0,0,0,0.06); }
.kpi-lbl { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.06em; color:#64748B; margin-bottom:6px; }
.kpi-val { font-size:26px; font-weight:700; color:#0F172A; line-height:1.1; }
.kpi-d   { font-size:11px; margin-top:5px; font-weight:500; }
.pos { color:#16A34A; } .neg { color:#DC2626; } .neu { color:#64748B; }
.insight { background:#EFF6FF; border-left:4px solid #1E3A8A; border-radius:8px;
           padding:14px 16px; margin:12px 0; font-size:12px; color:#1E3A8A; line-height:1.6; }
.sec { font-size:13px; font-weight:700; color:#0F172A; text-transform:uppercase;
       letter-spacing:.06em; border-bottom:2px solid #1E3A8A; padding-bottom:4px; margin:20px 0 14px; }
.badge-pos { background:#DCFCE7; color:#15803D; padding:2px 8px; border-radius:6px;
             font-size:11px; font-weight:600; }
.badge-neg { background:#FEE2E2; color:#B91C1C; padding:2px 8px; border-radius:6px;
             font-size:11px; font-weight:600; }
.badge-neu { background:#F1F5F9; color:#475569; padding:2px 8px; border-radius:6px;
             font-size:11px; font-weight:600; }
.fuente { font-size:10px; color:#94A3B8; margin-top:30px; padding-top:10px; border-top:1px solid #E2E8F0; }
</style>""", unsafe_allow_html=True)

# ── Funciones de lectura ──────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def leer(fb):
    xl = pd.ExcelFile(io.BytesIO(fb))

    def total(sh):
        df = xl.parse(sh, header=None)
        return {yr: float(df.iloc[11,col]) for yr,col in YR19.items()
                if col < df.shape[1] and pd.notna(df.iloc[11,col])}

    def categ(sh, n, cat_col=2, yc=None):
        yc = yc or YR19
        df = xl.parse(sh, header=None)
        out = {}
        for i in range(n):
            ri = 11 + i
            if ri >= len(df): break
            cat = str(df.iloc[ri, cat_col]).strip()
            if not cat or cat == 'nan': continue
            vals = {}
            for yr, col in yc.items():
                if col < df.shape[1]:
                    v = df.iloc[ri, col]
                    if pd.notna(v):
                        try: vals[yr] = round(float(v), 2)
                        except: pass
            if vals: out[cat] = vals
        return out

    def categ_cruce(sh, n_sex=2, n_cat=4, sex_col=2, cat_col=3, yc=None):
        """Hojas con cruce sexo × categoría (edad_sexo, educ_sexo, idioma_sexo)"""
        yc = yc or YR20
        df = xl.parse(sh, header=None)
        out = {}
        row = 11
        for s in range(n_sex):
            sexo = str(df.iloc[row, sex_col]).strip()
            row += 1
            for c in range(n_cat):
                if row >= len(df): break
                cat = str(df.iloc[row, cat_col]).strip()
                if not cat or cat == 'nan':
                    row += 1; continue
                key = f"{sexo} · {cat}"
                vals = {}
                for yr, col in yc.items():
                    if col < df.shape[1]:
                        v = df.iloc[row, col]
                        if pd.notna(v):
                            try: vals[yr] = round(float(v), 2)
                            except: pass
                if vals: out[key] = vals
                row += 1
        return out

    def especie(sh, label_col, yc=None):
        yc = yc or YR19
        df = xl.parse(sh, header=None)
        sp = ['Vacunos','Ovinos','Caprinos','Porcinos','Llamas','Alpacas','Cuyes',
              'Pollos','Gallinas']
        out = {}
        for i in range(10, 25):
            if i >= len(df): break
            lbl = str(df.iloc[i, label_col]).strip()
            m = next((s for s in sp if s.lower() in lbl.lower()), None)
            if not m: continue
            vals = {}
            for yr, col in yc.items():
                if col < df.shape[1]:
                    v = df.iloc[i, col]
                    if pd.notna(v):
                        try: vals[yr] = round(float(v), 0)
                        except: pass
            if vals: out[m] = vals
        return out

    def sup(sh):
        df = xl.parse(sh, header=None)
        rows = {'Sup. agrícola total':10,'Sup. sembrada':11,'Sup. en barbecho':12,
                'Tierras inactivas':13,'Sup. en descanso':14,'Sup. no agrícola':15,
                'Pastos nat. manejados':16,'Pastos no manejados':17,'Montes y bosques':18}
        out = {}
        for lbl, ri in rows.items():
            if ri >= len(df): continue
            vals = {}
            for yr, col in YR19.items():
                if col < df.shape[1]:
                    v = df.iloc[ri, col]
                    if pd.notna(v):
                        try: vals[yr] = round(float(v)/1e6, 3)
                        except: pass
            if vals: out[lbl] = vals
        return out

    D = {}
    D['total']         = total('total_productores')
    D['sexo']          = categ('1.2.1_sexo', 2)
    D['edad3']         = categ('1.1.1_edad_3', 4)       # grupos 3 (15-34, 35-49, 50-64, 65+)
    D['edad4']         = categ('1.1.1_edad', 4)          # grupos 4 (15-29, 30-44, 45-59, 60+)
    D['edad2']         = categ('1.1.1_edad_2', 3)        # grupos 2 (14-39, 40-59, 60+)
    D['edad_sexo3']    = categ_cruce('1.2.2_edad_sexo_3', n_sex=2, n_cat=4, sex_col=2, cat_col=3, yc=YR20)
    D['edad_sexo4']    = categ_cruce('1.2.2_edad_sexo',   n_sex=2, n_cat=4, sex_col=2, cat_col=3, yc=YR20)
    D['educ']          = categ('1.5.1_nivel_educ_a', 5)
    D['educ_sexo']     = categ_cruce('1.5.2_nivel_educ_a_sexo', n_sex=2, n_cat=5, sex_col=2, cat_col=3, yc=YR20)
    D['etnicidad']     = categ_cruce('1.3.2_etnicidad_sexo', n_sex=2, n_cat=6, sex_col=2, cat_col=3, yc=YR20)
    D['idioma']        = categ_cruce('1.3.4_idioma_sexo', n_sex=2, n_cat=4, sex_col=2, cat_col=3, yc=YR20)
    D['tam_ua1']       = categ('4.1.1_tam_ua_1', 6)      # 6 rangos finos
    D['tam_ua2']       = categ('4.1.1_tam_ua_2', 4)      # 4 rangos medios
    D['tam_ua3']       = categ('4.1.1_tam_ua_3', 4)      # micro UA (<2ha)
    D['num_parc']      = categ('4.1.2_num_parc', 5)
    D['sup_abs']       = sup('sup_usos_tierra_abs')
    D['esp_12m']       = especie('num_especi_ult12mes', 1)
    D['prod_12m']      = especie('num_prod_ult12mes',   2)
    D['esp_dia']       = especie('num_especi_diaentrev', 1)
    D['prod_dia']      = especie('num_prod_diaentrev',   2)
    return D

# ── Helpers ───────────────────────────────────────────────────────────────────
def df_long(d, val='valor'):
    return pd.DataFrame([{'categoria':k,'anio':yr, val:v}
                         for k,yv in d.items() for yr,v in yv.items()])

def LY(d):  # layout base plotly
    return dict(plot_bgcolor='white', paper_bgcolor='white',
                font_family="Inter,sans-serif", font_color="#334155",
                margin=dict(t=38,b=24,l=8,r=8),
                legend=dict(font_size=11, orientation='h', y=1.15, x=0))

def insight(txt):
    st.markdown(f'<div class="insight">💡 {txt}</div>', unsafe_allow_html=True)

def delta_badge(v):
    if v > 0:   return f'<span class="badge-pos">▲ +{v:.1f}</span>'
    elif v < 0: return f'<span class="badge-neg">▼ {v:.1f}</span>'
    else:       return f'<span class="badge-neu">= {v:.1f}</span>'

def trend_line(d, title, val_label='%', fmt='.1f', proj=True):
    yrs_ok = sorted([y for y in YEARS if y in d])
    yv = [d[y] for y in yrs_ok]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[str(y) for y in yrs_ok], y=yv, mode='lines+markers+text',
        line=dict(color=C['azul'], width=2.5),
        marker=dict(size=8, color=C['azul'], line=dict(color='white',width=2)),
        text=[f"{v:{fmt}}" for v in yv], textposition='top center',
        textfont=dict(size=10), name='Observado'))
    if proj and max(yrs_ok)+1 not in d:
        x_n = np.arange(len(yrs_ok))
        coef = np.polyfit(x_n, yv, 1)
        y_p = np.polyval(coef, len(yrs_ok))
        fig.add_trace(go.Scatter(
            x=[str(max(yrs_ok)), f"{max(yrs_ok)+1}*"],
            y=[yv[-1], y_p], mode='lines+markers',
            line=dict(color=C['naranja'],width=2,dash='dash'),
            marker=dict(size=7,symbol='diamond',color=C['naranja']),
            text=['', f"{y_p:{fmt}}*"], textposition='top center',
            textfont=dict(size=10,color=C['naranja']), name='Proyección'))
    fig.update_layout(title=title, yaxis_title=val_label, **LY())
    return fig

def bar_grupo(d, title, val_label='%', stack=False):
    df = df_long(d)
    cats = df['categoria'].unique().tolist()
    cmap = {c: PAL[i % len(PAL)] for i,c in enumerate(cats)}
    mode = 'stack' if stack else 'group'
    fig = px.bar(df, x='anio', y='valor', color='categoria', barmode=mode,
                 color_discrete_map=cmap, text_auto='.1f',
                 labels={'valor':val_label,'anio':'Año','categoria':''},
                 title=title)
    fig.update_traces(textfont_size=9, textposition='outside' if not stack else 'inside',
                      cliponaxis=False)
    fig.update_layout(**LY())
    if stack: fig.update_layout(yaxis_range=[0,107])
    return fig

def line_multi(d, title, val_label='%'):
    df = df_long(d)
    cats = df['categoria'].unique().tolist()
    cmap = {c: PAL[i % len(PAL)] for i,c in enumerate(cats)}
    fig = px.line(df, x='anio', y='valor', color='categoria',
                  color_discrete_map=cmap, markers=True,
                  labels={'valor':val_label,'anio':'Año','categoria':''},
                  title=title)
    fig.update_traces(line_width=2.2, marker_size=7)
    fig.update_layout(**LY())
    return fig

def bar_horiz_delta(d, title, yr_a=2023, yr_b=None):
    yr_b = yr_b or max(k for k in YEARS if any(yr_b_ := k, True) and
                       any(yr_b_ in v for v in d.values())) 
    # Simplified: use last available year
    avail = sorted(set(yr for v in d.values() for yr in v))
    yr_b = avail[-1]
    rows = []
    for cat, yv in d.items():
        if yr_a in yv and yr_b in yv:
            rows.append({'cat': cat, 'delta': round(yv[yr_b]-yv[yr_a],2),
                         f'{yr_a}': yv[yr_a], f'{yr_b}': yv[yr_b]})
    if not rows: return go.Figure()
    df = pd.DataFrame(rows).sort_values('delta')
    cols = [C['exito'] if v>=0 else C['rojo'] for v in df['delta']]
    fig = go.Figure(go.Bar(x=df['delta'], y=df['cat'], orientation='h',
                           marker_color=cols,
                           text=[f"{v:+.1f}pp" for v in df['delta']],
                           textposition='outside'))
    fig.update_layout(title=title, xaxis_title='Puntos porcentuales', **LY())
    return fig

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Fuente de datos")
    uploaded = st.file_uploader("Sube el Excel ENA", type=["xlsx"],
                                help="0_var_estruc_factor.xlsx — tal cual sale de Stata")
    st.markdown("---")
    st.markdown("**Módulos del dashboard:**")
    mods = ["Resumen ejecutivo","Demografía del productor","Educación e identidad",
            "Tenencia y estructura UA","Sector pecuario","Superficie agrícola","Tabla maestra"]
    for m in mods:
        st.markdown(f"<span style='font-size:11px;'>▸ {m}</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("ENA 2023–2025 · INEI–DNCE\nActualización: al subir nuevo Excel")

# ── Sin archivo ───────────────────────────────────────────────────────────────
if uploaded is None:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1E3A8A,#1d4ed8);color:#fff;
                padding:24px 28px;border-radius:12px;margin-bottom:20px;">
      <h1 style="font-size:20px;font-weight:700;margin:0;">
        🌾 Panel Ejecutivo ENA · Perfil del Productor Agropecuario Nacional</h1>
      <p style="font-size:12px;margin:6px 0 0;opacity:.75;">
        INEI — Dirección Nacional de Censos y Encuestas · 2023–2025</p>
    </div>""", unsafe_allow_html=True)
    st.info("👈 Sube el archivo Excel en el panel izquierdo para activar el dashboard.")
    st.stop()

with st.spinner("Procesando datos..."):
    D = leer(uploaded.read())

# ── Banner ────────────────────────────────────────────────────────────────────
tot = D['total']
yr_max  = max(y for y in YEARS if y in tot)
yr_prev = yr_max - 1 if (yr_max-1) in tot else sorted(tot.keys())[-2]

st.markdown(f"""
<div style="background:linear-gradient(135deg,#1E3A8A,#1d4ed8);color:#fff;
            padding:18px 24px;border-radius:12px;margin-bottom:18px;
            display:flex;justify-content:space-between;align-items:center;">
  <div>
    <div style="font-size:19px;font-weight:700;">
      🌾 Panel Ejecutivo ENA · Perfil del Productor Agropecuario Nacional</div>
    <div style="font-size:11px;opacity:.75;margin-top:3px;">
      INEI — Dirección Nacional de Censos y Encuestas · Nivel nacional · 2023–{yr_max}</div>
  </div>
  <div style="text-align:right;font-size:11px;opacity:.7;">
    Año más reciente: <b>{yr_max}</b><br>Serie: 2023–{yr_max}
  </div>
</div>""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
d_abs = tot[yr_max]-tot[yr_prev]
d_pct = (tot[yr_max]-tot[2023])/tot[2023]*100
promedio = np.mean([tot[y] for y in tot])

k1,k2,k3,k4 = st.columns(4)
kpis_data = [
    (f"{tot[yr_max]:,.0f}",
     f"{'▲' if d_abs>=0 else '▼'} {abs(d_abs):,.0f} vs {yr_prev}",
     d_abs>=0, C['azul'], f"Productores {yr_max}"),
    (f"{tot[yr_prev]:,.0f}",
     f"{'▲' if tot[yr_prev]>tot[2023] else '▼'} {abs(tot[yr_prev]-tot[2023]):,.0f} vs 2023",
     tot[yr_prev]>=tot[2023], C['verde'], f"Productores {yr_prev}"),
    (f"{tot[2023]:,.0f}", "Año base de la serie", None, C['gris'], "Productores 2023"),
    (f"{d_pct:+.1f}%", f"Acumulado 2023–{yr_max}", d_pct>=0, C['lila'],
     "Tendencia acumulada"),
]
for col, (val, delta, pos, color, lbl) in zip([k1,k2,k3,k4], kpis_data):
    dc = "pos" if pos else ("neg" if pos is False else "neu")
    with col:
        st.markdown(f"""
        <div class="kpi" style="border-left:4px solid {color}">
          <div class="kpi-lbl">{lbl}</div>
          <div class="kpi-val">{val}</div>
          <div class="kpi-d {dc}">{delta}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📊 Resumen ejecutivo",
    "👤 Demografía",
    "🎓 Educación e identidad",
    "🏡 Tenencia y UA",
    "🐄 Sector pecuario",
    "🌱 Superficie agrícola",
    "📋 Tabla maestra"
])

# ══════════════════════════════════════════════
# TAB 0 — RESUMEN EJECUTIVO
# ══════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="sec">Evolución del total de productores agropecuarios</div>',
                unsafe_allow_html=True)

    # Proyección
    yrs_ok = sorted([y for y in YEARS if y in tot])
    yv_ok  = [tot[y] for y in yrs_ok]
    coef   = np.polyfit(np.arange(len(yrs_ok)), yv_ok, 1)
    y_proj = np.polyval(coef, len(yrs_ok))

    insight(f"En {yr_max} se registran <b>{tot[yr_max]:,.0f}</b> productores a nivel nacional. "
            f"La variación acumulada respecto a 2023 es de <b>{d_pct:+.1f}%</b>. "
            f"De mantenerse la tendencia, la proyección lineal para {max(yrs_ok)+1} apunta a "
            f"<b>{y_proj:,.0f}</b> productores.")

    c1, c2 = st.columns([1.5, 1])
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[str(y) for y in yrs_ok], y=yv_ok,
            mode='lines+markers+text',
            line=dict(color=C['azul'], width=3),
            marker=dict(size=10, color=C['azul'], line=dict(color='white',width=2)),
            text=[f"{v/1e6:.3f}M" for v in yv_ok], textposition='top center',
            fill='tozeroy', fillcolor='rgba(30,58,138,0.07)', name='Observado'))
        if max(yrs_ok)+1 not in tot:
            fig.add_trace(go.Scatter(
                x=[str(max(yrs_ok)), f"{max(yrs_ok)+1}*"],
                y=[yv_ok[-1], y_proj], mode='lines+markers',
                line=dict(color=C['naranja'],width=2,dash='dash'),
                marker=dict(size=8,symbol='diamond',color=C['naranja']),
                text=['',f"{y_proj/1e6:.3f}M*"], textposition='top center',
                textfont=dict(size=10,color=C['naranja']), name=f"Proyección {max(yrs_ok)+1}"))
        fig.update_layout(
            title='Total de productores/as agropecuarios/as · Serie 2023–'+str(yr_max),
            yaxis=dict(title='Productores', tickformat=',.0f'), **LY())
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Cuadro de variaciones interanuales
        st.markdown('<div class="sec" style="margin-top:0">Variaciones interanuales</div>',
                    unsafe_allow_html=True)
        for i in range(1, len(yrs_ok)):
            ya, yb = yrs_ok[i-1], yrs_ok[i]
            diff = tot[yb]-tot[ya]
            pct  = diff/tot[ya]*100
            st.markdown(f"""
            <div style="background:#fff;border:1px solid #E2E8F0;border-radius:10px;
                        padding:12px 16px;margin-bottom:8px;display:flex;
                        justify-content:space-between;align-items:center;">
              <div>
                <div style="font-size:11px;color:#64748B;font-weight:600;">{ya} → {yb}</div>
                <div style="font-size:18px;font-weight:700;color:#0F172A;">
                  {diff:+,.0f}</div>
              </div>
              {delta_badge(pct)}
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">Indicadores estructurales clave</div>', unsafe_allow_html=True)
    c3,c4,c5,c6 = st.columns(4)

    def kpi_mini(col, lbl, val23, val_ult, unidad='%'):
        d = val_ult - val23
        dc = "pos" if d>=0 else "neg"
        sign = "▲" if d>=0 else "▼"
        with col:
            st.markdown(f"""
            <div class="kpi" style="border-left:3px solid #1E3A8A">
              <div class="kpi-lbl">{lbl}</div>
              <div style="font-size:20px;font-weight:700;color:#0F172A;">{val_ult:.1f}{unidad}</div>
              <div class="kpi-d {dc}">{sign} {abs(d):.1f}pp vs 2023</div>
            </div>""", unsafe_allow_html=True)

    # Extraer valores clave
    def get_val(dic, cat_key, yr):
        for k,v in dic.items():
            if cat_key.lower() in k.lower() and yr in v:
                return v[yr]
        return np.nan

    v_hombre23 = get_val(D['sexo'], 'Hombre', 2023)
    v_hombre_ult= get_val(D['sexo'], 'Hombre', yr_max)
    v_65_23 = get_val(D['edad3'], '65', 2023)
    v_65_ult= get_val(D['edad3'], '65', yr_max)
    v_prim23= get_val(D['educ'], 'Primaria', 2023)
    v_prim_ult=get_val(D['educ'], 'Primaria', yr_max)
    v_10ha23= get_val(D['tam_ua2'], '10', 2023)
    v_10ha_ult=get_val(D['tam_ua2'], '10', yr_max)

    if not np.isnan(v_hombre23): kpi_mini(c3, "% Productores hombre", v_hombre23, v_hombre_ult)
    if not np.isnan(v_65_23):    kpi_mini(c4, "% Productores 65+ años", v_65_23, v_65_ult)
    if not np.isnan(v_prim23):   kpi_mini(c5, "% Con ed. primaria", v_prim23, v_prim_ult)
    if not np.isnan(v_10ha23):   kpi_mini(c6, "% UA ≥10 ha", v_10ha23, v_10ha_ult)

# ══════════════════════════════════════════════
# TAB 1 — DEMOGRAFÍA
# ══════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="sec">Distribución por sexo del productor/a</div>',
                unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.plotly_chart(bar_grupo(D['sexo'],
            'Productores por sexo · % del total nacional',
            val_label='%'), use_container_width=True)
    with c2:
        st.plotly_chart(line_multi(D['sexo'],
            'Tendencia distribución por sexo (2023–'+str(yr_max)+')'),
            use_container_width=True)

    st.markdown('<div class="sec">Distribución por grupos de edad</div>', unsafe_allow_html=True)

    sub1, sub2 = st.tabs(["Grupos principales (15-34 / 35-49 / 50-64 / 65+)",
                           "Grupos alternativos (15-29 / 30-44 / 45-59 / 60+)"])
    with sub1:
        c3,c4 = st.columns(2)
        with c3:
            st.plotly_chart(line_multi(D['edad3'],
                '% por grupos de edad (clasificación ENA)'), use_container_width=True)
        with c4:
            st.plotly_chart(bar_horiz_delta(D['edad3'],
                f'Cambio en estructura etaria · {yr_max} vs 2023 (pp)'),
                use_container_width=True)
        insight("El grupo 65+ años muestra la tendencia más pronunciada, reflejando el "
                "envejecimiento sostenido del productor agropecuario peruano.")

    with sub2:
        c5,c6 = st.columns(2)
        with c5:
            st.plotly_chart(line_multi(D['edad4'],
                '% por grupos de edad (15-29 / 30-44 / 45-59 / 60+)'),
                use_container_width=True)
        with c6:
            st.plotly_chart(line_multi(D['edad2'],
                '% por grupos de edad (14-39 / 40-59 / 60+)'),
                use_container_width=True)

    st.markdown('<div class="sec">Edad del productor/a por sexo</div>', unsafe_allow_html=True)
    c7,c8 = st.columns(2)
    hombres = {k:v for k,v in D['edad_sexo3'].items() if 'Hombre' in k}
    mujeres  = {k:v for k,v in D['edad_sexo3'].items() if 'Mujer' in k}
    hombres_lbl = {k.replace('Hombre · ',''):v for k,v in hombres.items()}
    mujeres_lbl  = {k.replace('Mujer · ',''):v  for k,v in mujeres.items()}
    with c7:
        st.plotly_chart(line_multi(hombres_lbl, 'Grupos de edad · Hombres (%)'),
                        use_container_width=True)
    with c8:
        st.plotly_chart(line_multi(mujeres_lbl, 'Grupos de edad · Mujeres (%)'),
                        use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 — EDUCACIÓN E IDENTIDAD
# ══════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="sec">Nivel educativo del productor/a</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        df_ed = df_long(D['educ'])
        fig_ed = px.bar(df_ed, x='valor', y='categoria', color='anio', barmode='group',
                        orientation='h', text_auto='.1f',
                        color_discrete_map={2023:PAL[0],2024:PAL[1],2025:PAL[2],2026:PAL[3]},
                        labels={'valor':'%','categoria':'Nivel educativo','anio':'Año'},
                        title='% por nivel educativo alcanzado · Nacional')
        fig_ed.update_layout(yaxis=dict(autorange='reversed'), **LY())
        st.plotly_chart(fig_ed, use_container_width=True)
    with c2:
        st.plotly_chart(bar_horiz_delta(D['educ'],
            f'Cambio en nivel educativo · {yr_max} vs 2023 (pp)'),
            use_container_width=True)

    st.markdown('<div class="sec">Nivel educativo por sexo</div>', unsafe_allow_html=True)
    c3,c4 = st.columns(2)
    educ_h = {k.replace('Hombre · ',''):v for k,v in D['educ_sexo'].items() if 'Hombre' in k}
    educ_m = {k.replace('Mujer · ',''):v  for k,v in D['educ_sexo'].items() if 'Mujer' in k}
    with c3:
        st.plotly_chart(line_multi(educ_h, 'Nivel educativo · Hombres (%)'),
                        use_container_width=True)
    with c4:
        st.plotly_chart(line_multi(educ_m, 'Nivel educativo · Mujeres (%)'),
                        use_container_width=True)
    insight("La brecha educativa entre hombres y mujeres es significativa: "
            "las productoras tienen mayor proporción sin nivel o con primaria incompleta.")

    st.markdown('<div class="sec">Autoidentificación étnica del productor/a</div>',
                unsafe_allow_html=True)
    c5,c6 = st.columns(2)
    etn_h = {k.replace('Hombre · ',''):v for k,v in D['etnicidad'].items() if 'Hombre' in k}
    etn_m = {k.replace('Mujer · ',''):v  for k,v in D['etnicidad'].items() if 'Mujer' in k}
    with c5:
        st.plotly_chart(line_multi(etn_h, 'Etnicidad · Hombres (%)'), use_container_width=True)
    with c6:
        st.plotly_chart(line_multi(etn_m, 'Etnicidad · Mujeres (%)'), use_container_width=True)

    st.markdown('<div class="sec">Idioma materno del productor/a</div>', unsafe_allow_html=True)
    c7,c8 = st.columns(2)
    idi_h = {k.replace('Hombre · ',''):v for k,v in D['idioma'].items() if 'Hombre' in k}
    idi_m = {k.replace('Mujer · ',''):v  for k,v in D['idioma'].items() if 'Mujer' in k}
    with c7:
        st.plotly_chart(line_multi(idi_h, 'Idioma materno · Hombres (%)'),
                        use_container_width=True)
    with c8:
        st.plotly_chart(line_multi(idi_m, 'Idioma materno · Mujeres (%)'),
                        use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — TENENCIA Y UA
# ══════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="sec">Tamaño de la unidad agropecuaria (UA)</div>',
                unsafe_allow_html=True)

    sub1, sub2, sub3 = st.tabs(["Rangos medios (4 grupos)",
                                  "Rangos finos (6 grupos)",
                                  "Micro UA (< 2 ha)"])
    with sub1:
        c1,c2 = st.columns(2)
        with c1:
            st.plotly_chart(bar_grupo(D['tam_ua2'],
                '% por tamaño de UA · 4 rangos', stack=True),
                use_container_width=True)
        with c2:
            st.plotly_chart(line_multi(D['tam_ua2'],
                'Tendencia por tamaño de UA (4 rangos)'), use_container_width=True)
        insight("El segmento ≥10 ha muestra la tendencia de crecimiento más marcada, "
                "sugiriendo una concentración progresiva de la tierra.")

    with sub2:
        c3,c4 = st.columns(2)
        with c3:
            st.plotly_chart(bar_grupo(D['tam_ua1'],
                '% por tamaño de UA · 6 rangos finos', stack=True),
                use_container_width=True)
        with c4:
            st.plotly_chart(bar_horiz_delta(D['tam_ua1'],
                f'Cambio por tamaño de UA · {yr_max} vs 2023 (pp)'),
                use_container_width=True)

    with sub3:
        c5,c6 = st.columns(2)
        with c5:
            st.plotly_chart(line_multi(D['tam_ua3'],
                '% distribución de micro UA (< 2 ha)'), use_container_width=True)
        with c6:
            st.plotly_chart(bar_horiz_delta(D['tam_ua3'],
                f'Cambio en micro UA · {yr_max} vs 2023 (pp)'),
                use_container_width=True)

    st.markdown('<div class="sec">Número de parcelas por unidad agropecuaria</div>',
                unsafe_allow_html=True)
    c7,c8 = st.columns(2)
    with c7:
        st.plotly_chart(bar_grupo(D['num_parc'],
            '% por número de parcelas · Nacional', stack=True),
            use_container_width=True)
    with c8:
        st.plotly_chart(line_multi(D['num_parc'],
            'Tendencia de fragmentación parcelaria'), use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 — SECTOR PECUARIO
# ══════════════════════════════════════════════
with tabs[4]:
    sub1, sub2 = st.tabs(["Referencia: últimos 12 meses", "Referencia: día de entrevista"])

    for sub, esp_key, prod_key, label in [
        (sub1, 'esp_12m', 'prod_12m', 'últimos 12 meses'),
        (sub2, 'esp_dia', 'prod_dia', 'día de entrevista')
    ]:
        with sub:
            st.markdown(f'<div class="sec">Número de cabezas por especie · {label}</div>',
                        unsafe_allow_html=True)
            c1,c2 = st.columns(2)
            with c1:
                df_e = df_long(D[esp_key], 'cabezas')
                cats_e = df_e['categoria'].unique().tolist()
                cmap_e = {c: PAL[i%len(PAL)] for i,c in enumerate(cats_e)}
                fig_e = px.bar(df_e, x='anio', y='cabezas', color='categoria', barmode='group',
                               color_discrete_map=cmap_e, text_auto='.2s',
                               labels={'cabezas':'Cabezas','anio':'Año','categoria':'Especie'},
                               title=f'N° cabezas por especie · {label}')
                fig_e.update_layout(**LY())
                st.plotly_chart(fig_e, use_container_width=True)
            with c2:
                st.plotly_chart(line_multi(
                    {k:v for k,v in D[esp_key].items()},
                    f'Tendencia de cabezas por especie · {label}', val_label='Cabezas'),
                    use_container_width=True)

            st.markdown(f'<div class="sec">Productores pecuarios · {label}</div>',
                        unsafe_allow_html=True)
            c3,c4 = st.columns(2)
            with c3:
                df_p = df_long(D[prod_key], 'productores')
                cats_p = df_p['categoria'].unique().tolist()
                cmap_p = {c: PAL[i%len(PAL)] for i,c in enumerate(cats_p)}
                fig_p = px.bar(df_p, x='categoria', y='productores', color='anio',
                               barmode='group', color_discrete_map={
                                   2023:PAL[0],2024:PAL[1],2025:PAL[2],2026:PAL[3]},
                               text_auto='.2s',
                               labels={'productores':'Productores','categoria':'Especie','anio':'Año'},
                               title=f'Productores por especie · {label}')
                fig_p.update_layout(**LY())
                st.plotly_chart(fig_p, use_container_width=True)
            with c4:
                # Variación % por especie
                rows_v = []
                for esp, yv in D[prod_key].items():
                    avail = sorted(yv.keys())
                    if len(avail) >= 2:
                        ya, yb = avail[0], avail[-1]
                        d = (yv[yb]-yv[ya])/yv[ya]*100
                        rows_v.append({'Especie':esp, 'Δ%': round(d,1),
                                       str(ya): yv[ya], str(yb): yv[yb]})
                if rows_v:
                    dv = pd.DataFrame(rows_v).sort_values('Δ%')
                    cols_v = [C['exito'] if v>=0 else C['rojo'] for v in dv['Δ%']]
                    fv = go.Figure(go.Bar(x=dv['Δ%'], y=dv['Especie'], orientation='h',
                                          marker_color=cols_v,
                                          text=[f"{v:+.1f}%" for v in dv['Δ%']],
                                          textposition='outside'))
                    fv.update_layout(title='Variación % productores por especie', **LY())
                    st.plotly_chart(fv, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5 — SUPERFICIE AGRÍCOLA
# ══════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="sec">Superficie agropecuaria absoluta (millones de hectáreas)</div>',
                unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    agri  = {k:v for k,v in D['sup_abs'].items() if 'agrícola' in k.lower() or 'barbecho' in k.lower()
             or 'inactiv' in k.lower() or 'descanso' in k.lower() or 'sembrada' in k.lower()}
    noagri= {k:v for k,v in D['sup_abs'].items() if k not in agri}
    with c1:
        st.plotly_chart(line_multi(agri, 'Superficie agrícola y usos (M ha)', 'Millones ha'),
                        use_container_width=True)
    with c2:
        st.plotly_chart(line_multi(noagri, 'Superficie no agrícola (M ha)', 'Millones ha'),
                        use_container_width=True)

    st.markdown('<div class="sec">Variación absoluta de superficie</div>', unsafe_allow_html=True)
    c3,c4 = st.columns(2)
    with c3:
        avail_yr = sorted(set(yr for v in D['sup_abs'].values() for yr in v))
        yr_a, yr_b = avail_yr[0], avail_yr[-1]
        rows_s = [{'Uso':k, 'Δ M ha': round(v[yr_b]-v[yr_a],3)}
                  for k,v in D['sup_abs'].items() if yr_a in v and yr_b in v]
        ds = pd.DataFrame(rows_s).sort_values('Δ M ha')
        cs = [C['exito'] if v>=0 else C['rojo'] for v in ds['Δ M ha']]
        fs = go.Figure(go.Bar(x=ds['Δ M ha'], y=ds['Uso'], orientation='h',
                               marker_color=cs,
                               text=[f"{v:+.3f}" for v in ds['Δ M ha']],
                               textposition='outside'))
        fs.update_layout(title=f'Variación sup. {yr_b} vs {yr_a} (M ha)', **LY())
        st.plotly_chart(fs, use_container_width=True)
    with c4:
        # Tabla de valores absolutos
        rows_t = []
        for k, yv in D['sup_abs'].items():
            row = {'Uso de suelo': k}
            for yr in sorted(yv.keys()):
                row[str(yr)] = f"{yv[yr]:.3f}"
            rows_t.append(row)
        st.dataframe(pd.DataFrame(rows_t), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 6 — TABLA MAESTRA
# ══════════════════════════════════════════════
with tabs[6]:
    st.markdown('<div class="sec">Tabla maestra · todos los indicadores ENA</div>',
                unsafe_allow_html=True)
    rows_m = []

    # Total
    rows_m.append({'Módulo':'Productores','Indicador':'Total productores',
                   'Categoría':'Total',
                   **{str(yr): f"{tot[yr]:,.0f}" for yr in sorted(tot.keys())},
                   'Δ pp/% 2023→'+str(yr_max): f"{d_pct:+.1f}%"})

    grupos = [
        ('sexo','Demografía','% por sexo'),
        ('edad3','Demografía','% edad (15-34/35-49/50-64/65+)'),
        ('edad4','Demografía','% edad (15-29/30-44/45-59/60+)'),
        ('edad2','Demografía','% edad (14-39/40-59/60+)'),
        ('educ','Educación','% nivel educativo'),
        ('etnicidad','Identidad','% autoidentificación étnica'),
        ('idioma','Identidad','% idioma materno'),
        ('tam_ua1','Tenencia UA','% tamaño UA (6 rangos)'),
        ('tam_ua2','Tenencia UA','% tamaño UA (4 rangos)'),
        ('tam_ua3','Tenencia UA','% micro UA (<2ha)'),
        ('num_parc','Tenencia UA','% n° parcelas'),
    ]
    for key, mod, ind in grupos:
        for cat, yv in D[key].items():
            avail = sorted(yv.keys())
            v0 = yv.get(2023, np.nan); vf = yv.get(yr_max, np.nan)
            delta = f"{vf-v0:+.1f}pp" if not np.isnan(v0) and not np.isnan(vf) else "—"
            rows_m.append({'Módulo':mod,'Indicador':ind,'Categoría':cat,
                           **{str(yr): f"{yv[yr]:.1f}%" if yr in yv else "—" for yr in YEARS},
                           'Δ pp/% 2023→'+str(yr_max): delta})

    for key, mod, ind, lbl_val in [
        ('esp_12m','Pecuario','Cabezas (12m)','cabezas'),
        ('prod_12m','Pecuario','Productores pecuarios (12m)','prod'),
        ('esp_dia','Pecuario','Cabezas (día entrevista)','cabezas'),
        ('prod_dia','Pecuario','Productores (día entrevista)','prod'),
    ]:
        for cat, yv in D[key].items():
            avail = sorted(yv.keys())
            v0 = yv.get(avail[0], np.nan); vf = yv.get(avail[-1], np.nan)
            dpct = f"{(vf-v0)/v0*100:+.1f}%" if not np.isnan(v0) and v0!=0 else "—"
            rows_m.append({'Módulo':mod,'Indicador':ind,'Categoría':cat,
                           **{str(yr): f"{yv[yr]:,.0f}" if yr in yv else "—" for yr in YEARS},
                           'Δ pp/% 2023→'+str(yr_max): dpct})

    df_m = pd.DataFrame(rows_m)
    col_delta = 'Δ pp/% 2023→'+str(yr_max)

    def style_delta(val):
        if isinstance(val,str) and val.startswith('+'): return 'color:#16A34A;font-weight:600'
        if isinstance(val,str) and val.startswith('-'): return 'color:#DC2626;font-weight:600'
        return ''

    st.dataframe(df_m.style.applymap(style_delta, subset=[col_delta]),
                 use_container_width=True, hide_index=True, height=520)

    csv = df_m.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Descargar tabla maestra en CSV", csv,
                       f"ENA_tabla_maestra_2023_{yr_max}.csv", "text/csv")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="fuente">
  <b>Fuente:</b> INEI — Encuesta Nacional Agropecuaria (ENA) 2023, 2024 y 2025.
  Elaboración: Dirección Nacional de Censos y Encuestas — Área de procesamiento ENA.<br>
  Estimaciones a nivel nacional (estimaciones puntuales). 
  (*) Proyección lineal indicativa basada en tendencia 2023–{yr_max}. 
  Uso restringido — documento de trabajo interno.
</div>""", unsafe_allow_html=True)
