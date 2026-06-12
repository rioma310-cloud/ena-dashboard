"""
ENA · Consola de Datos — Panel Ejecutivo Nacional
INEI — Dirección Nacional de Censos y Encuestas
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io

st.set_page_config(
    page_title="ENA · Consola de Datos Nacional",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Autenticación ─────────────────────────────────────────────────────────────
def check_password():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if not st.session_state.autenticado:
        st.markdown("""
        <div style="max-width:420px;margin:80px auto;padding:40px;background:#FFFFFF;
                    border-radius:16px;box-shadow:0 10px 25px -5px rgba(0,0,0,0.1);
                    text-align:center;border-top:5px solid #1E3A8A;">
          <div style="font-size:48px;margin-bottom:12px;">🏛️</div>
          <div style="font-size:20px;font-weight:700;color:#0F172A;margin-bottom:6px;">
            Consola de Datos ENA</div>
          <div style="font-size:13px;color:#64748B;margin-bottom:28px;">
            Instituto Nacional de Estadística e Informática — Uso Restringido</div>
        </div>""", unsafe_allow_html=True)
        col = st.columns([1,1.8,1])[1]
        with col:
            clave = st.text_input("Credencial de Acceso", type="password",
                                  placeholder="Ingrese el token de seguridad")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Autenticar Conexión", use_container_width=True):
                if clave == "MARIO":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("🔒 Credencial inválida. Acceso denegado.")
        st.stop()

check_password()

# ── Paleta ────────────────────────────────────────────────────────────────────
C = {
    "primary":   "#1E3A8A",
    "secondary": "#0F766E",
    "accent":    "#7C3AED",
    "warning":   "#EA580C",
    "danger":    "#DC2626",
    "success":   "#16A34A",
    "dark":      "#0F172A",
    "light":     "#F8FAFC",
    "border":    "#E2E8F0"
}
PAL8 = ["#1E3A8A","#0F766E","#7C3AED","#EA580C","#0891B2","#16A34A","#DC2626","#64748B",
        "#0284C7","#15803D","#9333EA","#C2410C"]

YEARS = [2023, 2024, 2025, 2026]
YR19  = {2023:19, 2024:21, 2025:23, 2026:25}
YR20  = {2023:20, 2024:22, 2025:24, 2026:26}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"],.stMarkdown { font-family:'Inter',sans-serif !important; }
[data-testid="stAppViewContainer"] { background:#F8FAFC; }
[data-testid="stSidebar"] { background-color:#0F172A !important; }
[data-testid="stSidebar"] * { color:#F8FAFC !important; }
.stTabs [data-baseweb="tab-list"] { gap:8px; background-color:#E2E8F0; padding:6px; border-radius:12px; }
.stTabs [data-baseweb="tab"] { padding:10px 20px; background-color:transparent; border-radius:8px;
    color:#475569; font-weight:600; border:none; transition:all 0.2s ease; }
.stTabs [aria-selected="true"] { background-color:#1E3A8A !important; color:#FFFFFF !important;
    box-shadow:0 4px 6px -1px rgba(0,0,0,0.1); }
.kpi-box { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:20px;
    box-shadow:0 1px 3px 0 rgba(0,0,0,0.05); display:flex; flex-direction:column;
    justify-content:space-between; height:100%; }
.kpi-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }
.kpi-title { color:#64748B; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; }
.kpi-main-val { font-size:28px; font-weight:700; color:#0F172A; line-height:1.2; }
.semaforo-verde   { background:#DCFCE7; color:#15803D; padding:2px 8px; border-radius:6px; font-size:12px; font-weight:600; }
.semaforo-amarillo{ background:#FEF9C3; color:#A16207; padding:2px 8px; border-radius:6px; font-size:12px; font-weight:600; }
.semaforo-rojo    { background:#FEE2E2; color:#B91C1C; padding:2px 8px; border-radius:6px; font-size:12px; font-weight:600; }
.executive-insight-box { background:#F0F9FF; border-left:4px solid #0284C7; border-radius:8px;
    padding:16px; margin-bottom:20px; }
.section-header-panel { font-size:18px; font-weight:700; color:#0F172A; margin:25px 0 15px 0;
    border-bottom:2px solid #E2E8F0; padding-bottom:6px; }
.fuente-footer { font-size:11px; color:#94A3B8; margin-top:40px; border-top:1px solid #E2E8F0; padding-top:12px; }
</style>""", unsafe_allow_html=True)

# ── Lectura de datos ──────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def leer(file_bytes):
    xl = pd.ExcelFile(io.BytesIO(file_bytes))

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
        yc = yc or YR20
        df = xl.parse(sh, header=None)
        out = {}
        sexo_actual = None
        # Recorre filas desde 11 hasta encontrar 'Región' o agotar bloques
        count = 0
        for row in range(11, min(11 + n_sex * (n_cat + 2), len(df))):
            sx = str(df.iloc[row, sex_col]).strip()
            cat = str(df.iloc[row, cat_col]).strip()
            # Actualiza sexo cuando aparece (Hombre/Mujer); si nan, mantiene el anterior
            if sx and sx != 'nan':
                if 'Región' in sx or 'Costa' in sx or 'Sierra' in sx:
                    break
                sexo_actual = sx
            if not cat or cat == 'nan':
                continue
            if 'Región' in cat:
                break
            key = f"{sexo_actual} · {cat}"
            vals = {}
            for yr, col in yc.items():
                if col < df.shape[1]:
                    v = df.iloc[row, col]
                    if pd.notna(v):
                        try: vals[yr] = round(float(v), 2)
                        except: pass
            if vals:
                out[key] = vals
                count += 1
            if count >= n_sex * n_cat:
                break
        return out

    def especie(sh, label_col, yc=None):
        yc = yc or YR19
        df = xl.parse(sh, header=None)
        sp = ['Vacunos','Ovinos','Caprinos','Porcinos','Llamas','Alpacas','Cuyes','Pollos','Gallinas']
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

    def sup_abs(sh):
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
    D['total']      = total('total_productores')
    D['sexo']       = categ('1.2.1_sexo', 2)
    D['edad3']      = categ('1.1.1_edad_3', 4)
    D['edad4']      = categ('1.1.1_edad', 4)
    D['edad2']      = categ('1.1.1_edad_2', 3)
    D['edad_sexo3'] = categ_cruce('1.2.2_edad_sexo_3', n_sex=2, n_cat=4, sex_col=2, cat_col=3, yc=YR20)
    D['edad_sexo4'] = categ_cruce('1.2.2_edad_sexo',   n_sex=2, n_cat=4, sex_col=2, cat_col=3, yc=YR20)
    D['educ']       = categ('1.5.1_nivel_educ_a', 5)
    D['educ_sexo']  = categ_cruce('1.5.2_nivel_educ_a_sexo', n_sex=2, n_cat=5, sex_col=2, cat_col=3, yc=YR20)
    D['etnicidad']  = categ_cruce('1.3.2_etnicidad_sexo', n_sex=2, n_cat=8, sex_col=2, cat_col=3, yc=YR20)
    D['idioma']     = categ_cruce('1.3.4_idioma_sexo', n_sex=2, n_cat=7, sex_col=2, cat_col=3, yc=YR20)
    D['tam_ua1']    = categ('4.1.1_tam_ua_1', 6)
    D['tam_ua2']    = categ('4.1.1_tam_ua_2', 4)
    D['tam_ua3']    = categ('4.1.1_tam_ua_3', 4)
    D['num_parc']   = categ('4.1.2_num_parc', 5)
    D['sup_abs']    = sup_abs('sup_usos_tierra_abs')
    D['esp_12m']    = especie('num_especi_ult12mes', 1)
    D['prod_12m']   = especie('num_prod_ult12mes',   2)
    D['esp_dia']    = especie('num_especi_diaentrev', 1)
    D['prod_dia']   = especie('num_prod_diaentrev',   2)
    D['usos_pct']   = {
        'Sup. sembrada':    {2023:43.7,2024:43.1,2025:44.9},
        'Sup. en barbecho': {2023:12.7,2024:12.5,2025: 6.1},
        'Tierras inactivas':{2023:33.8,2024:33.5,2025:41.5},
        'Sup. en descanso': {2023: 9.8,2024:11.0,2025: 7.6},
    }
    return D

# ── Helpers ───────────────────────────────────────────────────────────────────
def to_df(d, val='valor'):
    rows = [{'categoria':k,'anio':yr,val:v}
            for k,yv in d.items() for yr,v in yv.items()]
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=['categoria','anio',val])

def apply_premium_layout(fig, title_text, y_title="", x_title="", is_bar=False):
    # Si la figura está vacía, mostrar fondo blanco con mensaje
    if not fig.data:
        fig.add_annotation(text="Sin datos disponibles para este indicador",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           showarrow=False, font=dict(size=13, color="#94A3B8"))
    fig.update_layout(
        title=dict(text=f"<b>{title_text}</b>",
                   font=dict(size=15,color="#0F172A"), x=0.01, y=0.94, yanchor="top"),
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family="Inter,sans-serif", size=11, color="#475569"),
        margin=dict(t=95,b=50,l=45,r=20), height=420, showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right",
                    x=0.99, title_text="", font=dict(size=10,color="#475569"), itemwidth=40),
        hovermode="x unified"
    )
    fig.update_xaxes(title_text=f"<b>{x_title}</b>" if x_title else "",
                     title_font=dict(size=11,color="#1E3A8A"),
                     showgrid=False, showline=True, linecolor="#CBD5E1",
                     tickfont=dict(size=11,color="#475569"), linewidth=1)
    # Forzar años como categorías discretas (evita 2023.5, 2024.5)
    if x_title and ("o" in x_title.lower() or "ciclo" in x_title.lower()):
        fig.update_xaxes(type='category')
    fig.update_yaxes(title_text=f"<b>{y_title}</b>" if y_title else "",
                     title_font=dict(size=11,color="#1E3A8A"),
                     showgrid=True, gridcolor="#F1F5F9",
                     showline=False, tickfont=dict(size=11,color="#475569"))
    if is_bar:
        fig.update_layout(bargap=0.22, bargroupgap=0.04)
        fig.update_traces(textposition='outside', cliponaxis=False)
    return fig

def safe_line(d, title, y_label="Porcentaje", x_label="Año"):
    if not d:
        return apply_premium_layout(go.Figure(), title, y_label, x_label)
    df = to_df(d)
    if df.empty or 'categoria' not in df.columns:
        return apply_premium_layout(go.Figure(), title, y_label, x_label)
    df['anio'] = df['anio'].astype(str)
    cats = df['categoria'].unique().tolist()
    cmap = {c: PAL8[i%len(PAL8)] for i,c in enumerate(cats)}
    fig = px.line(df, x='anio', y='valor', color='categoria',
                  color_discrete_map=cmap, markers=True,
                  labels={'valor':y_label,'anio':x_label,'categoria':''})
    fig.update_traces(line_width=2.5, marker_size=7)
    return apply_premium_layout(fig, title, y_label, x_label)

def safe_bar(d, title, y_label="%", stack=False):
    if not d:
        return apply_premium_layout(go.Figure(), title, y_label)
    df = to_df(d)
    if df.empty:
        return apply_premium_layout(go.Figure(), title, y_label)
    df['anio'] = df['anio'].astype(str)
    cats = df['categoria'].unique().tolist()
    cmap = {c: PAL8[i%len(PAL8)] for i,c in enumerate(cats)}
    mode = 'stack' if stack else 'group'
    fig = px.bar(df, x='anio', y='valor', color='categoria', barmode=mode,
                 color_discrete_map=cmap, text_auto='.1f',
                 labels={'valor':y_label,'anio':'Año','categoria':''})
    fig = apply_premium_layout(fig, title, y_label, "Año", is_bar=True)
    if stack: fig.update_layout(yaxis_range=[0,105])
    return fig

def delta_bar(d, title, yr_a=2023):
    if not d: return go.Figure()
    avail = sorted(set(yr for v in d.values() for yr in v))
    yr_b = avail[-1]
    rows = [{'cat':k,'delta':round(v[yr_b]-v[yr_a],2),
             'v_inicio':v[yr_a],'v_fin':v[yr_b]}
            for k,v in d.items() if yr_a in v and yr_b in v]
    if not rows: return go.Figure()
    df = pd.DataFrame(rows).sort_values('delta')
    
    # Colores con gradiente de intensidad según magnitud
    max_abs = max(abs(df['delta'].max()), abs(df['delta'].min()), 0.01)
    colors = []
    for v in df['delta']:
        intensity = min(abs(v)/max_abs, 1.0)
        if v >= 0:
            r = int(22 + (34-22)*(1-intensity))
            g = int(163 + (163)*intensity)
            b = int(74 + (74)*(1-intensity))
            colors.append(f'rgb({r},{g},{b})')
        else:
            r = int(220 - (220-180)*intensity)
            g = int(38 * (1-intensity*0.7))
            b = int(38 * (1-intensity*0.7))
            colors.append(f'rgb({r},{g},{b})')
    
    fig = go.Figure()
    
    # Barras con ancho proporcional a cambio
    fig.add_trace(go.Bar(
        x=df['delta'], y=df['cat'], orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='white', width=1.5),
            cornerradius=4
        ),
        text=[f"<b>{v:+.1f}pp</b><br><span style='font-size:9px'>{r:.1f}%→{f:.1f}%</span>"
              for v,r,f in zip(df['delta'],df['v_inicio'],df['v_fin'])],
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>Variación: %{x:+.2f} pp<extra></extra>",
        cliponaxis=False
    ))
    
    # Línea vertical en cero destacada
    fig.add_vline(x=0, line_width=2, line_color="#0F172A", opacity=0.4)
    
    # Anotación de alerta si hay cambio brusco
    max_delta = df['delta'].abs().max()
    if max_delta > 3:
        fig.add_annotation(
            x=0.99, y=0.02, xref="paper", yref="paper",
            text=f"⚠️ Cambio máximo: {max_delta:.1f}pp",
            showarrow=False, font=dict(size=10, color=C['warning']),
            bgcolor="#FFF7ED", bordercolor=C['warning'],
            borderwidth=1, borderpad=4
        )
    
    fig = apply_premium_layout(fig, title, "Puntos porcentuales", "")
    fig.update_xaxes(zeroline=False)
    return fig

def semaforo_tendencias(d, title, unidad="%", umbral_alto=2.0, umbral_medio=0.5):
    """Tabla visual tipo semáforo: muestra cada categoría con su tendencia.
    Verde=sube fuerte, amarillo=estable, rojo=baja fuerte."""
    if not d: return None
    avail = sorted(set(yr for v in d.values() for yr in v))
    if len(avail) < 2: return None
    yr_a, yr_b = avail[0], avail[-1]
    
    items = []
    for cat, yv in d.items():
        if yr_a in yv and yr_b in yv:
            delta = yv[yr_b] - yv[yr_a]
            if unidad == "%cab":  # variación porcentual para cabezas
                delta_pct = (yv[yr_b]-yv[yr_a])/yv[yr_a]*100 if yv[yr_a] else 0
                items.append((cat, yv[yr_a], yv[yr_b], delta_pct, delta_pct))
            else:
                items.append((cat, yv[yr_a], yv[yr_b], delta, delta))
    
    items.sort(key=lambda x: x[4], reverse=True)
    return items, yr_a, yr_b

def render_semaforo(items, yr_a, yr_b, unidad="%", umbral_alto=2.0, umbral_medio=0.5):
    """Renderiza HTML de semáforo de tendencias."""
    html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px;margin:10px 0;">'
    for cat, v0, vf, delta, sortkey in items:
        if sortkey > umbral_alto:
            color, bg, icon, txt = "#15803D", "#DCFCE7", "▲▲", "AL ALZA"
        elif sortkey > umbral_medio:
            color, bg, icon, txt = "#65A30D", "#ECFCCB", "▲", "LEVE ALZA"
        elif sortkey >= -umbral_medio:
            color, bg, icon, txt = "#A16207", "#FEF9C3", "▬", "ESTABLE"
        elif sortkey >= -umbral_alto:
            color, bg, icon, txt = "#EA580C", "#FFEDD5", "▼", "LEVE BAJA"
        else:
            color, bg, icon, txt = "#B91C1C", "#FEE2E2", "▼▼", "A LA BAJA"
        
        if unidad == "%cab":
            val_disp = f"{delta:+.1f}%"
            sub = f"{v0:,.0f} → {vf:,.0f}"
        else:
            val_disp = f"{delta:+.1f}pp"
            sub = f"{v0:.1f}% → {vf:.1f}%"
        
        html += f"""
        <div style="background:{bg};border-radius:10px;padding:12px 14px;border-left:4px solid {color};">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:11px;font-weight:700;color:#0F172A;">{cat[:24]}</span>
            <span style="font-size:9px;font-weight:700;color:{color};background:white;padding:2px 6px;border-radius:10px;">{icon} {txt}</span>
          </div>
          <div style="font-size:20px;font-weight:700;color:{color};margin-top:4px;">{val_disp}</div>
          <div style="font-size:10px;color:#64748B;margin-top:2px;">{sub}</div>
        </div>"""
    html += '</div>'
    return html




# ─── GRÁFICOS AVANZADOS DE DETECCIÓN DE CAMBIOS ──────────────────────────────

def slope_chart(d, title, unidad="%"):
    """Slope chart: 2 puntos (año inicio/fin) conectados por líneas.
    Las pendientes pronunciadas revelan cambios bruscos al instante."""
    if not d: return go.Figure()
    avail = sorted(set(yr for v in d.values() for yr in v))
    if len(avail) < 2: return go.Figure()
    ya, yb = avail[0], avail[-1]

    fig = go.Figure()
    items = [(cat, yv[ya], yv[yb]) for cat, yv in d.items() if ya in yv and yb in yv]
    items.sort(key=lambda x: x[2]-x[1], reverse=True)

    for i, (cat, v0, vf) in enumerate(items):
        delta = vf - v0
        if delta > 1.0:    color, w = "#16A34A", 3.5
        elif delta < -1.0: color, w = "#DC2626", 3.5
        else:              color, w = "#94A3B8", 2

        fig.add_trace(go.Scatter(
            x=[str(ya), str(yb)], y=[v0, vf],
            mode='lines+markers+text',
            line=dict(color=color, width=w),
            marker=dict(size=9, color=color, line=dict(color='white', width=1.5)),
            text=[f"{v0:.1f}", f"{vf:.1f}  <b>{cat[:20]}</b> ({delta:+.1f})"],
            textposition=["middle left", "middle right"],
            textfont=dict(size=10, color=color),
            showlegend=False,
            hovertemplate=f"<b>{cat}</b><br>{ya}: {v0:.1f}{unidad}<br>{yb}: {vf:.1f}{unidad}<br>Δ: {delta:+.1f}<extra></extra>"
        ))

    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", font=dict(size=15, color="#0F172A"),
                   x=0.01, y=0.96, yanchor="top"),
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family="Inter,sans-serif", size=11, color="#475569"),
        margin=dict(t=60, b=30, l=60, r=180), height=420,
        xaxis=dict(showgrid=False, showline=True, linecolor="#CBD5E1",
                   tickfont=dict(size=13, color="#0F172A"), type='category',
                   range=[-0.25, 1.6]),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", showline=False,
                   tickfont=dict(size=10, color="#94A3B8")),
        hovermode="closest"
    )
    return fig


def heatmap_variaciones(D_dict, yr_max):
    """Heatmap panorámico: filas=indicadores, columnas=años, color=valor relativo.
    Detecta de un vistazo dónde están los cambios en TODO el dashboard."""
    rows = []

    bloques = [
        ('sexo', 'Sexo'), ('edad3', 'Edad'), ('educ', 'Educación'),
        ('tam_ua2', 'Tamaño UA'), ('num_parc', 'Parcelas'), ('usos_pct', 'Uso tierra'),
    ]
    # Detectar qué años tienen datos en al menos un indicador
    years_with_data = set()
    for key, _ in bloques:
        for yv in D_dict[key].values():
            years_with_data.update(yv.keys())
    cols_years = sorted(years_with_data)

    for key, grupo in bloques:
        for cat, yv in D_dict[key].items():
            avail = sorted(yv.keys())
            if len(avail) < 2: continue
            ya, yb = avail[0], avail[-1]
            delta = yv[yb] - yv[ya]
            vals_by_year = [yv.get(y, None) for y in cols_years]
            label = f"{grupo} | {cat[:26]}"
            rows.append((label, vals_by_year, delta))

    rows.sort(key=lambda x: x[2], reverse=True)

    z, y_labels, text_vals = [], [], []
    for label, vals, delta in rows:
        base = next((v for v in vals if v is not None), 0)
        normalized = [(v - base) if v is not None else None for v in vals]
        z.append(normalized)
        y_labels.append(label)
        text_vals.append([f"{v:.1f}" if v is not None else "·" for v in vals])

    fig = go.Figure(go.Heatmap(
        z=z,
        x=[str(y) for y in cols_years],
        y=y_labels,
        text=text_vals, texttemplate="%{text}",
        textfont=dict(size=10, color="#0F172A"),
        colorscale=[[0,'#DC2626'],[0.35,'#FCA5A5'],[0.48,'#FEF9C3'],
                    [0.52,'#FEF9C3'],[0.65,'#86EFAC'],[1,'#16A34A']],
        zmid=0, showscale=True,
        hoverongaps=False,
        colorbar=dict(title=dict(text="Δ vs<br>2023", font=dict(size=10)),
                      tickfont=dict(size=9), thickness=12, len=0.6),
        hovertemplate="<b>%{y}</b><br>%{x}: %{text}<extra></extra>",
        xgap=4, ygap=4
    ))

    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family="Inter,sans-serif", size=10, color="#475569"),
        margin=dict(t=40, b=20, l=10, r=10),
        height=max(450, len(y_labels) * 27 + 90),
        xaxis=dict(side='top', type='category',
                   tickfont=dict(size=13, color="#0F172A"),
                   fixedrange=True),
        yaxis=dict(tickfont=dict(size=10, color="#334155"),
                   autorange='reversed', automargin=True,
                   fixedrange=True)
    )
    return fig


def render_semaforo_spark(items_with_series, yr_a, yr_b, unidad="%",
                          umbral_alto=2.0, umbral_medio=0.5):
    """Semáforo con sparklines: tarjetas que incluyen mini-gráfico de tendencia SVG."""
    html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px;margin:10px 0;">'

    for cat, serie, delta, sortkey in items_with_series:
        if sortkey > umbral_alto:
            color, bg, icon, txt = "#15803D", "#DCFCE7", "▲▲", "AL ALZA"
        elif sortkey > umbral_medio:
            color, bg, icon, txt = "#65A30D", "#ECFCCB", "▲", "LEVE ALZA"
        elif sortkey >= -umbral_medio:
            color, bg, icon, txt = "#A16207", "#FEF9C3", "▬", "ESTABLE"
        elif sortkey >= -umbral_alto:
            color, bg, icon, txt = "#EA580C", "#FFEDD5", "▼", "LEVE BAJA"
        else:
            color, bg, icon, txt = "#B91C1C", "#FEE2E2", "▼▼", "A LA BAJA"

        # Generar sparkline SVG con la serie completa
        vals = [v for _, v in serie]
        if len(vals) >= 2:
            vmin, vmax = min(vals), max(vals)
            rng = (vmax - vmin) or 1
            W, H = 90, 28
            pts = []
            for i, v in enumerate(vals):
                px = 4 + i * (W-8) / (len(vals)-1)
                py = H - 4 - (v - vmin) / rng * (H-8)
                pts.append(f"{px:.1f},{py:.1f}")
            polyline = " ".join(pts)
            last_x, last_y = pts[-1].split(",")
            spark = f"""<svg width="{W}" height="{H}" style="display:block;">
              <polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="{last_x}" cy="{last_y}" r="3" fill="{color}"/>
            </svg>"""
        else:
            spark = ""

        if unidad == "%cab":
            val_disp = f"{delta:+.1f}%"
            sub = f"{serie[0][1]:,.0f} → {serie[-1][1]:,.0f}"
        else:
            val_disp = f"{delta:+.1f}pp"
            sub = f"{serie[0][1]:.1f}% → {serie[-1][1]:.1f}%"

        html += f"""
        <div style="background:{bg};border-radius:10px;padding:12px 14px;border-left:4px solid {color};">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:11px;font-weight:700;color:#0F172A;">{cat[:26]}</span>
            <span style="font-size:9px;font-weight:700;color:{color};background:white;padding:2px 6px;border-radius:10px;white-space:nowrap;">{icon} {txt}</span>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-top:6px;">
            <div>
              <div style="font-size:20px;font-weight:700;color:{color};">{val_disp}</div>
              <div style="font-size:10px;color:#64748B;margin-top:2px;">{sub}</div>
            </div>
            {spark}
          </div>
        </div>"""
    html += '</div>'
    return html


def build_spark_items(d, unidad="%"):
    """Prepara items con serie completa para el semáforo con sparklines."""
    if not d: return None
    out = []
    for cat, yv in d.items():
        serie = sorted(yv.items())
        if len(serie) < 2: continue
        v0, vf = serie[0][1], serie[-1][1]
        if unidad == "%cab":
            delta = (vf - v0) / v0 * 100 if v0 else 0
        else:
            delta = vf - v0
        out.append((cat, serie, delta, delta))
    out.sort(key=lambda x: x[3], reverse=True)
    if not out: return None
    yrs = sorted(set(yr for v in d.values() for yr in v))
    return out, yrs[0], yrs[-1]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:10px 0;text-align:center;">
        <span style="font-size:40px;">🏛️</span>
        <h3 style="margin-top:10px;font-size:18px;font-weight:700;">Consola de Datos ENA</h3>
        <p style="font-size:12px;color:#94A3B8;opacity:.8;">Órgano de Auditoría y Control Operativo</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    uploaded = st.file_uploader("Cargar Repositorio Estructural (.XLSX)", type=["xlsx"],
                                help="Cargue la matriz de datos ENA oficial.")
    st.markdown("---")
    st.markdown("### 📋 Variables Fiscalizadas")
    for x in ["Productores","Sexo","Edad","Educación","Etnicidad","Idioma",
               "UA (3 estratos)","Parcelas","Ganadería (12m + día)","Superficie"]:
        st.markdown(f"<span style='color:#34D399;'>✔</span> {x}", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("INEI — Dirección Nacional de Censos y Encuestas\nENA 2023–2026")

# ── Sin archivo ───────────────────────────────────────────────────────────────
if uploaded is None:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0F172A,#1E3A8A);padding:50px;
                border-radius:20px;color:white;text-align:center;margin-top:30px;">
      <h1 style="font-weight:800;font-size:32px;margin-bottom:10px;">
        Sistema de Monitoreo Analítico de la Estructura Agropecuaria Nacional</h1>
      <p style="font-size:15px;opacity:.85;max-width:700px;margin:0 auto 30px;">
        Herramienta ejecutiva de visualización de microdatos estadísticos — ENA · INEI</p>
    </div>""", unsafe_allow_html=True)
    st.info("💡 Cargue el archivo Excel en el panel izquierdo para inicializar los motores gráficos.")
    st.stop()

with st.spinner("Ejecutando algoritmos de segmentación y carga matricial..."):
    D = leer(uploaded.read())

# ── Header institucional ──────────────────────────────────────────────────────
tot = D['total']
yr_max  = max(y for y in YEARS if y in tot)
yr_prev = yr_max-1 if (yr_max-1) in tot else sorted(tot.keys())[-2]
d_abs = tot[yr_max]-tot[yr_prev]
d_pct = (tot[yr_max]-tot[2023])/tot[2023]*100

st.markdown("""
<div style="background:#FFFFFF;border:1px solid #E2E8F0;padding:20px 30px;border-radius:14px;
            box-shadow:0 1px 3px rgba(0,0,0,0.05);margin-bottom:25px;
            display:flex;justify-content:space-between;align-items:center;">
  <div>
    <h1 style="color:#0F172A;font-size:24px;font-weight:700;margin:0;">
      Panel Ejecutivo Nacional de la Estructura Agropecuaria</h1>
    <p style="color:#64748B;font-size:13px;margin:4px 0 0;">
      Reporte de consistencia y evolución de indicadores clave · ENA</p>
  </div>
  <div style="text-align:right;">
    <span style="background:#EFF6FF;color:#1E3A8A;font-size:11px;font-weight:700;
                 padding:6px 12px;border-radius:20px;border:1px solid #BFDBFE;">
      ÁMBITO: NACIONAL</span>
  </div>
</div>""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
if d_pct > 2.0:   sem_cls, sem_txt = "semaforo-verde",   f"CRECIMIENTO OPTIMIZADO ({d_pct:+.1f}%)"
elif d_pct >= 0:  sem_cls, sem_txt = "semaforo-amarillo", f"ESTABILIDAD CRÍTICA ({d_pct:+.1f}%)"
else:             sem_cls, sem_txt = "semaforo-rojo",    f"ALERTA CONTRAÍDA ({d_pct:+.1f}%)"

k1,k2,k3,k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="kpi-box">
        <div class="kpi-header"><span class="kpi-title">Volumen Total de Productores</span>
        <span style="font-size:16px;">👨‍🌾</span></div>
        <div><div class="kpi-main-val">{tot[yr_max]/1e6:.3f} M</div>
        <div style="margin-top:8px;"><span class="{sem_cls}">{sem_txt}</span></div></div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-box">
        <div class="kpi-header"><span class="kpi-title">Variación Anual Absoluta</span>
        <span style="font-size:16px;">📈</span></div>
        <div><div class="kpi-main-val">{d_abs:+,.0f}</div>
        <div style="margin-top:8px;font-size:12px;color:#64748B;">vs. periodo anual {yr_prev}</div></div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-box">
        <div class="kpi-header"><span class="kpi-title">Último Cierre de Campaña</span>
        <span style="font-size:16px;">📅</span></div>
        <div><div class="kpi-main-val">{yr_max}</div>
        <div style="margin-top:8px;font-size:12px;color:#16A34A;font-weight:600;">Consolidado Oficial</div></div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-box">
        <div class="kpi-header"><span class="kpi-title">Comportamiento Sectorial</span>
        <span style="font-size:16px;">📊</span></div>
        <div><div class="kpi-main-val">{"Tendencia Ascendente" if d_pct>0 else "Tendencia Negativa"}</div>
        <div style="margin-top:8px;font-size:12px;color:#64748B;">Línea base: Ciclo 2023</div></div>
    </div>""", unsafe_allow_html=True)

st.markdown(f"""<div class="executive-insight-box">
<b>Resumen Crítico de Inteligencia Sectorial:</b> Al cierre del ejercicio fiscal <b>{yr_max}</b>,
el número consolidado de unidades productoras a nivel nacional experimentó una variación neta del
<b>{d_pct:+.2f}%</b> respecto al ciclo base 2023. Los componentes demográficos revelan cambios
estructurales en la distribución por grupos etarios, niveles de instrucción y tenencia de tierras.
</div>""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs(["📈 Evolución General","👤 Perfil del Productor","🎓 Educación e Identidad",
                "🐄 Sector Pecuario","🌱 Capacidad de Superficie","🏡 Infraestructura UA",
                "📋 Auditoría de Tablas"])

# ══════════════════════════════════════════════
# TAB 0 — EVOLUCIÓN GENERAL
# ══════════════════════════════════════════════
with tabs[0]:
    # ── PANEL SEMÁFORO DE TENDENCIAS CLAVE ──
    st.markdown("<div class='section-header-panel'>🚦 Semáforo de Tendencias Estructurales Clave</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px;color:#64748B;margin:-8px 0 12px;'>Variación acumulada de los indicadores demográficos y estructurales más relevantes. Verde = al alza · Amarillo = estable · Rojo = a la baja.</p>", unsafe_allow_html=True)

    # Construir indicadores clave para el semáforo
    semaforo_data = {}
    # Sexo
    for cat, yv in D['sexo'].items():
        semaforo_data[f"Productores {cat}"] = yv
    # Edad 65+
    for cat, yv in D['edad3'].items():
        if '65' in cat: semaforo_data["Edad 65+ años"] = yv
        if '15 a 34' in cat: semaforo_data["Edad 15-34 años"] = yv
    # Educacion
    for cat, yv in D['educ'].items():
        if 'Sin nivel' in cat: semaforo_data["Sin nivel educativo"] = yv
        if 'universitaria' in cat and 'no' not in cat.lower(): semaforo_data["Ed. universitaria"] = yv
    # Tamaño UA grande
    for cat, yv in D['tam_ua2'].items():
        if '10' in cat: semaforo_data["UA grandes (≥10 ha)"] = yv

    res = build_spark_items(semaforo_data)
    if res:
        items_s, ya, yb = res
        st.markdown(render_semaforo_spark(items_s, ya, yb), unsafe_allow_html=True)

    # ── MAPA DE CALOR PANORÁMICO ──
    st.markdown("<div class='section-header-panel'>🔥 Mapa de Calor · Detección Panorámica de Cambios</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px;color:#64748B;margin:-8px 0 12px;'>Cada fila es un indicador, cada columna un año. El color muestra cuánto se desvía del valor inicial: <span style='color:#16A34A;font-weight:600;'>verde = subió</span> · <span style='color:#DC2626;font-weight:600;'>rojo = bajó</span>. Los focos de color intenso son los cambios más fuertes.</p>", unsafe_allow_html=True)
    st.plotly_chart(heatmap_variaciones(D, yr_max), use_container_width=True, key="heatmap_main")

    st.markdown("<div class='section-header-panel'>Dinámica y Proyección del Volumen Nacional de Productores</div>", unsafe_allow_html=True)
    c1,c2 = st.columns([1.6,1])
    with c1:
        yv = [tot[y] for y in YEARS if y in tot]
        yrs_d = [y for y in YEARS if y in tot]
        coef = np.polyfit(np.arange(len(yrs_d)), yv, 1)
        y_proj = np.polyval(coef, len(yrs_d))
        yr_proj = max(yrs_d)+1

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[str(y) for y in yrs_d], y=yv, mode='lines+markers+text',
            line=dict(color=C['primary'],width=3.5),
            marker=dict(size=10,color=C['primary'],line=dict(color="white",width=2)),
            text=[f"{v/1e6:.2f} M" for v in yv], textposition="top center",
            fill="tozeroy", fillcolor="rgba(30,58,138,0.07)", name="Histórico Registrado"))
        if yr_proj not in tot:
            fig.add_trace(go.Scatter(
                x=[str(max(yrs_d)), str(yr_proj)],
                y=[yv[-1], y_proj], mode='lines+markers+text',
                line=dict(color=C['warning'],width=2.5,dash='dot'),
                marker=dict(size=9,color=C['warning'],symbol='diamond',
                           line=dict(color="white",width=2)),
                text=["", f"{y_proj/1e6:.2f} M*"], textposition="top center",
                name=f"Proyección Tendencial {yr_proj}"))
        fig = apply_premium_layout(fig, "Evolución nacional de productores agropecuarios",
                                   "Volumen de Productores", "Ciclo Estadístico")
        fig.update_yaxes(tickformat=',.2s')
        st.plotly_chart(fig, use_container_width=True, key="f4e3dc33")

    with c2:
        df_s = to_df(D['sexo'])
        df_s['anio'] = df_s['anio'].astype(str)
        cmap_s = {'Hombre':C['primary'],'Mujer':C['danger']}
        fig2 = px.bar(df_s, x='anio', y='valor', color='categoria', barmode='group',
                      color_discrete_map=cmap_s, text_auto='.1f',
                      labels={'valor':'Porcentaje','anio':'Año','categoria':''})
        fig2 = apply_premium_layout(fig2, "Distribución de productores por sexo (%)",
                                    "Porcentaje", "Año", is_bar=True)
        fig2.update_layout(yaxis_range=[0,85])
        st.plotly_chart(fig2, use_container_width=True, key="f3224c09")

    st.markdown("<div class='section-header-panel'>Estructura Etaria Nacional</div>", unsafe_allow_html=True)
    c3,c4 = st.columns(2)
    with c3:
        st.plotly_chart(safe_line(D['edad3'],
            "Evolución de grupos etarios del productor (15-34/35-49/50-64/65+)",
            "Porcentaje","Año"), use_container_width=True, key="9fb6077e")
    with c4:
        st.plotly_chart(slope_chart(D['edad3'],
            f"Pendiente de cambio etario · 2023 → {yr_max}"),
            use_container_width=True, key="slope_edad3")

# ══════════════════════════════════════════════
# TAB 1 — PERFIL DEL PRODUCTOR
# ══════════════════════════════════════════════
with tabs[1]:
    st.markdown("<div class='section-header-panel'>Distribución Etaria por Sexo</div>", unsafe_allow_html=True)

    sub1, sub2, sub3 = st.tabs(["Grupos (15-34/35-49/50-64/65+)",
                                  "Grupos (15-29/30-44/45-59/60+)",
                                  "Grupos (14-39/40-59/60+)"])
    with sub1:
        c1,c2 = st.columns(2)
        hom3 = {k.replace('Hombre · ',''):v for k,v in D['edad_sexo3'].items() if 'Hombre' in k}
        muj3 = {k.replace('Mujer · ',''):v  for k,v in D['edad_sexo3'].items() if 'Mujer' in k}
        with c1:
            st.plotly_chart(safe_line(hom3,"Grupos de edad · Hombres (%)","Porcentaje","Año"),
                            use_container_width=True, key="b301d57d")
        with c2:
            st.plotly_chart(safe_line(muj3,"Grupos de edad · Mujeres (%)","Porcentaje","Año"),
                            use_container_width=True, key="c92c8d4f")
    with sub2:
        c3,c4 = st.columns(2)
        hom4 = {k.replace('Hombre · ',''):v for k,v in D['edad_sexo4'].items() if 'Hombre' in k}
        muj4 = {k.replace('Mujer · ',''):v  for k,v in D['edad_sexo4'].items() if 'Mujer' in k}
        with c3:
            st.plotly_chart(safe_line(hom4,"Grupos de edad · Hombres (15-29/30-44/45-59/60+)","Porcentaje","Año"),
                            use_container_width=True, key="7a3d2a54")
        with c4:
            st.plotly_chart(safe_line(muj4,"Grupos de edad · Mujeres (15-29/30-44/45-59/60+)","Porcentaje","Año"),
                            use_container_width=True, key="3135ac11")
    with sub3:
        c5,c6 = st.columns(2)
        with c5:
            st.plotly_chart(safe_line(D['edad2'],"Grupos etarios alternativos (14-39/40-59/60+)","Porcentaje","Año"),
                            use_container_width=True, key="d6fa425f")
        with c6:
            st.plotly_chart(delta_bar(D['edad2'],f"Desviación etaria alternativa (pp 2023→{yr_max})"),
                            use_container_width=True, key="f6116b67")

# ══════════════════════════════════════════════
# TAB 2 — EDUCACIÓN E IDENTIDAD
# ══════════════════════════════════════════════
with tabs[2]:
    st.markdown("<div class='section-header-panel'>Nivel Educativo del Productor/a</div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        df_ed = to_df(D['educ'])
        df_ed['anio'] = df_ed['anio'].astype(str)
        cmap_ed = {c:PAL8[i%len(PAL8)] for i,c in enumerate(df_ed['categoria'].unique())}
        fig_ed = px.bar(df_ed, x='valor', y='categoria', color='anio', barmode='group',
                        orientation='h', text_auto='.1f',
                        color_discrete_map={'2023':PAL8[0],'2024':PAL8[1],'2025':PAL8[2],'2026':PAL8[3]},
                        labels={'valor':'%','categoria':'Nivel educativo','anio':'Año'})
        fig_ed = apply_premium_layout(fig_ed, "Nivel educativo alcanzado por el productor/a (%)",
                                      "Nivel educativo","",is_bar=True)
        fig_ed.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig_ed, use_container_width=True, key="211afe56")
    with c2:
        st.plotly_chart(slope_chart(D['educ'], f"Pendiente de cambio educativo · 2023 → {yr_max}"), use_container_width=True, key="slope_educ")

    st.markdown("<div class='section-header-panel'>Nivel Educativo por Sexo</div>", unsafe_allow_html=True)
    c3,c4 = st.columns(2)
    educ_h = {k.replace('Hombre · ',''):v for k,v in D['educ_sexo'].items() if 'Hombre' in k}
    educ_m = {k.replace('Mujer · ',''):v  for k,v in D['educ_sexo'].items() if 'Mujer' in k}
    with c3:
        st.plotly_chart(safe_line(educ_h,"Nivel educativo · Hombres (%)","Porcentaje","Año"),
                        use_container_width=True, key="bcf2c3e7")
    with c4:
        st.plotly_chart(safe_line(educ_m,"Nivel educativo · Mujeres (%)","Porcentaje","Año"),
                        use_container_width=True, key="720e0768")

    st.markdown("<div class='section-header-panel'>Autoidentificación Étnica e Idioma Materno</div>", unsafe_allow_html=True)
    c5,c6 = st.columns(2)
    etn_h = {k.replace('Hombre · ',''):v for k,v in D['etnicidad'].items() if 'Hombre' in k}
    etn_m = {k.replace('Mujer · ',''):v  for k,v in D['etnicidad'].items() if 'Mujer' in k}
    with c5:
        st.plotly_chart(safe_line(etn_h,"Autoidentificación étnica · Hombres (%)","Porcentaje","Año"),
                        use_container_width=True, key="4b29d6d9")
    with c6:
        st.plotly_chart(safe_line(etn_m,"Autoidentificación étnica · Mujeres (%)","Porcentaje","Año"),
                        use_container_width=True, key="efdca321")

    c7,c8 = st.columns(2)
    idi_h = {k.replace('Hombre · ',''):v for k,v in D['idioma'].items() if 'Hombre' in k}
    idi_m = {k.replace('Mujer · ',''):v  for k,v in D['idioma'].items() if 'Mujer' in k}
    with c7:
        st.plotly_chart(safe_line(idi_h,"Idioma materno · Hombres (%)","Porcentaje","Año"),
                        use_container_width=True, key="0f0a763c")
    with c8:
        st.plotly_chart(safe_line(idi_m,"Idioma materno · Mujeres (%)","Porcentaje","Año"),
                        use_container_width=True, key="eb9ffd34")

# ══════════════════════════════════════════════
# TAB 3 — SECTOR PECUARIO
# ══════════════════════════════════════════════
with tabs[3]:
    sub_p1, sub_p2 = st.tabs(["Últimos 12 meses","Día de entrevista"])

    for sub, esp_k, prod_k, lbl in [
        (sub_p1,'esp_12m','prod_12m','Últimos 12 meses'),
        (sub_p2,'esp_dia','prod_dia','Día de entrevista')
    ]:
        with sub:
            # Semáforo de tendencias pecuarias
            st.markdown(f"<div class='section-header-panel'>🚦 Semáforo de Variación de Existencias · {lbl}</div>", unsafe_allow_html=True)
            res_p = build_spark_items(D[esp_k], unidad="%cab")
            if res_p:
                items_p, ya_p, yb_p = res_p
                st.markdown(render_semaforo_spark(items_p, ya_p, yb_p, unidad="%cab", umbral_alto=10, umbral_medio=3), unsafe_allow_html=True)

            st.markdown(f"<div class='section-header-panel'>Existencias por Especie · {lbl}</div>", unsafe_allow_html=True)
            c1,c2 = st.columns(2)
            with c1:
                df_e = to_df(D[esp_k],'cabezas')
                if not df_e.empty:
                    df_e['anio'] = df_e['anio'].astype(str)
                    fig_e = px.bar(df_e,x='categoria',y='cabezas',color='anio',barmode='group',
                                   color_discrete_map={'2023':PAL8[0],'2024':PAL8[1],'2025':PAL8[2],'2026':PAL8[3]},
                                   text_auto='.2s',
                                   labels={'cabezas':'Cabezas','categoria':'Especie','anio':'Año'})
                    fig_e = apply_premium_layout(fig_e,f"N° de cabezas por especie · {lbl}",
                                                 "Cabezas","Especie",is_bar=True)
                    st.plotly_chart(fig_e,use_container_width=True, key=f"esp_bar_{esp_k}")
            with c2:
                st.plotly_chart(safe_line(D[esp_k],f"Tendencia de cabezas por especie · {lbl}",
                                          "Cabezas","Año"),use_container_width=True, key=f"esp_line_{esp_k}")

            st.markdown(f"<div class='section-header-panel'>Productores Pecuarios · {lbl}</div>", unsafe_allow_html=True)
            c3,c4 = st.columns(2)
            with c3:
                df_p = to_df(D[prod_k],'productores')
                if not df_p.empty:
                    df_p['anio'] = df_p['anio'].astype(str)
                    cmap_p={c:PAL8[i%len(PAL8)] for i,c in enumerate(df_p['categoria'].unique())}
                    fig_p = px.bar(df_p,x='categoria',y='productores',color='anio',barmode='group',
                                   color_discrete_map={'2023':PAL8[0],'2024':PAL8[1],'2025':PAL8[2],'2026':PAL8[3]},
                                   text_auto='.2s',
                                   labels={'productores':'Productores','categoria':'Especie','anio':'Año'})
                    fig_p = apply_premium_layout(fig_p,f"Productores pecuarios por especie · {lbl}",
                                                 "Productores","Especie",is_bar=True)
                    st.plotly_chart(fig_p,use_container_width=True, key=f"prod_bar_{prod_k}")
            with c4:
                rows_v = []
                for esp,yv in D[prod_k].items():
                    av = sorted(yv.keys())
                    if len(av)>=2:
                        ya,yb = av[0],av[-1]
                        rows_v.append({'Especie':esp,'Δ%':round((yv[yb]-yv[ya])/yv[ya]*100,1)})
                if rows_v:
                    dv = pd.DataFrame(rows_v).sort_values('Δ%')
                    cv = [C['success'] if v>=0 else C['danger'] for v in dv['Δ%']]
                    fv = go.Figure(go.Bar(x=dv['Δ%'],y=dv['Especie'],orientation='h',
                                          marker_color=cv,
                                          text=[f"{v:+.1f}%" for v in dv['Δ%']],
                                          textposition='outside'))
                    fv = apply_premium_layout(fv,f"Variación % productores por especie · {lbl}",
                                              "Variación %","")
                    st.plotly_chart(fv,use_container_width=True, key=f"prod_var_{prod_k}")

# ══════════════════════════════════════════════
# TAB 4 — CAPACIDAD DE SUPERFICIE
# ══════════════════════════════════════════════
with tabs[4]:
    st.markdown("<div class='section-header-panel'>Superficie Agropecuaria Absoluta (Millones de Hectáreas)</div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    agri   = {k:v for k,v in D['sup_abs'].items() if any(x in k.lower() for x in ['agríc','barbecho','inact','descanso','sembrada'])}
    noagri = {k:v for k,v in D['sup_abs'].items() if k not in agri}
    with c1:
        st.plotly_chart(safe_line(agri,"Evolución de superficies agrícolas y sus usos (M ha)",
                                  "Millones de Hectáreas","Año"),use_container_width=True, key="1a1635bf")
    with c2:
        st.plotly_chart(safe_line(noagri,"Evolución de coberturas y tierras no agrícolas (M ha)",
                                  "Millones de Hectáreas","Año"),use_container_width=True, key="226965b6")

    st.markdown("<div class='section-header-panel'>Proporciones Relativas de Uso de Suelo</div>", unsafe_allow_html=True)
    c3,c4 = st.columns(2)
    with c3:
        st.plotly_chart(safe_line(D['usos_pct'],"Estructura porcentual del uso de la tierra (%)",
                                  "Porcentaje","Año"),use_container_width=True, key="9e0e899d")
    with c4:
        avail_s = sorted(set(yr for v in D['sup_abs'].values() for yr in v))
        if len(avail_s)>=2:
            ya_s,yb_s = avail_s[0],avail_s[-1]
            rows_w=[{'Uso':k,'Δ M ha':round(v[yb_s]-v[ya_s],3)}
                    for k,v in D['sup_abs'].items() if ya_s in v and yb_s in v]
            df_w=pd.DataFrame(rows_w).sort_values('Δ M ha')
            cols_w=[C['secondary'] if v>=0 else C['danger'] for v in df_w['Δ M ha']]
            fig_w=go.Figure(go.Bar(x=df_w['Δ M ha'],y=df_w['Uso'],orientation='h',
                                   marker_color=cols_w,
                                   text=[f"{v:+.3f}" for v in df_w['Δ M ha']],
                                   textposition='outside'))
            fig_w=apply_premium_layout(fig_w,f"Desviación neta superficie (M ha, {ya_s}→{yb_s})",
                                       "Variación Neta M ha","Tipología")
            st.plotly_chart(fig_w,use_container_width=True, key="0db38493")

# ══════════════════════════════════════════════
# TAB 5 — INFRAESTRUCTURA UA
# ══════════════════════════════════════════════
with tabs[5]:
    st.markdown("<div class='section-header-panel'>Análisis Microestructural del Fraccionamiento y Dimensión Operativa</div>", unsafe_allow_html=True)

    sub_ua1, sub_ua2, sub_ua3 = st.tabs(["Rangos medios (4 grupos)","Rangos finos (6 grupos)","Micro UA (<2 ha)"])

    with sub_ua1:
        c1,c2 = st.columns(2)
        with c1: st.plotly_chart(safe_bar(D['tam_ua2'],"Distribución de UA por estrato de tamaño · 4 rangos (%)",stack=True),use_container_width=True, key="8f246fa3")
        with c2: st.plotly_chart(slope_chart(D['tam_ua2'], f"Pendiente de concentración de tierra · 2023 → {yr_max}"),use_container_width=True, key="slope_ua2")
    with sub_ua2:
        c3,c4 = st.columns(2)
        with c3: st.plotly_chart(safe_bar(D['tam_ua1'],"Distribución de UA por estrato de tamaño · 6 rangos finos (%)",stack=True),use_container_width=True, key="994ec2ef")
        with c4: st.plotly_chart(delta_bar(D['tam_ua1'],f"Desviación interanual · 6 rangos (pp 2023→{yr_max})"),use_container_width=True, key="294bb8df")
    with sub_ua3:
        c5,c6 = st.columns(2)
        with c5: st.plotly_chart(safe_line(D['tam_ua3'],"Distribución de micro UA (<2 ha)","Porcentaje","Año"),use_container_width=True, key="69a738e8")
        with c6: st.plotly_chart(delta_bar(D['tam_ua3'],f"Desviación micro UA (pp 2023→{yr_max})"),use_container_width=True, key="d122ba26")

    st.markdown("<div class='section-header-panel'>Dinámica de la Concentración y Tenencia de Tierras</div>", unsafe_allow_html=True)
    c7,c8 = st.columns(2)
    with c7: st.plotly_chart(safe_bar(D['num_parc'],"Distribución de UA según número de parcelas internas (%)",stack=True),use_container_width=True, key="17ccb40c")
    with c8: st.plotly_chart(safe_line(D['num_parc'],"Evolución de la fragmentación parcelaria","Porcentaje","Año"),use_container_width=True, key="c125a68d")

# ══════════════════════════════════════════════
# TAB 6 — AUDITORÍA DE TABLAS
# ══════════════════════════════════════════════
with tabs[6]:
    st.markdown("<div class='section-header-panel'>Consolidado Multidimensional de Control Técnico de Indicadores</div>", unsafe_allow_html=True)

    rows = []
    rows.append({'Indicador':'Evolución nacional de productores','Categoría':'Total Agregado',
                 **{str(yr):f"{tot[yr]:,.0f}" for yr in sorted(tot.keys())},
                 'Δ 2023→'+str(yr_max): f"{d_pct:+.1f}%"})

    grupos = [
        ('sexo','Distribución por sexo (%)'),
        ('edad3','Grupos etarios ENA (15-34/35-49/50-64/65+) (%)'),
        ('edad4','Grupos etarios (15-29/30-44/45-59/60+) (%)'),
        ('edad2','Grupos etarios (14-39/40-59/60+) (%)'),
        ('educ','Nivel educativo alcanzado (%)'),
        ('tam_ua1','Tamaño UA · 6 rangos finos (%)'),
        ('tam_ua2','Tamaño UA · 4 rangos medios (%)'),
        ('tam_ua3','Micro UA (<2 ha) (%)'),
        ('num_parc','N° de parcelas por UA (%)'),
        ('usos_pct','Uso de la tierra agrícola (%)'),
    ]
    for key, lbl in grupos:
        for cat, yv in D[key].items():
            v0=yv.get(2023,np.nan); vf=yv.get(yr_max,np.nan)
            delta=f"{vf-v0:+.1f}pp" if not np.isnan(v0) and not np.isnan(vf) else "—"
            rows.append({'Indicador':lbl,'Categoría':cat,
                         **{str(yr):f"{yv[yr]:.1f}%" if yr in yv else "—" for yr in YEARS},
                         'Δ 2023→'+str(yr_max):delta})

    for key,lbl in [('esp_12m','Cabezas (12m)'),('prod_12m','Productores pecuarios (12m)'),
                    ('esp_dia','Cabezas (día)'),('prod_dia','Productores pecuarios (día)')]:
        for cat,yv in D[key].items():
            av=sorted(yv.keys())
            v0=yv.get(av[0],np.nan); vf=yv.get(av[-1],np.nan)
            dp=f"{(vf-v0)/v0*100:+.1f}%" if not np.isnan(v0) and v0!=0 else "—"
            rows.append({'Indicador':lbl,'Categoría':cat,
                         **{str(yr):f"{yv[yr]:,.0f}" if yr in yv else "—" for yr in YEARS},
                         'Δ 2023→'+str(yr_max):dp})

    df_tabla = pd.DataFrame(rows)
    col_d = 'Δ 2023→'+str(yr_max)
    # Ordenar columnas: Indicador, Categoría, años en orden, delta al final
    year_cols = sorted([c for c in df_tabla.columns if c.isdigit()])
    col_order = ['Indicador','Categoría'] + year_cols + [col_d]
    df_tabla = df_tabla[[c for c in col_order if c in df_tabla.columns]]
    df_tabla = df_tabla.fillna("—")

    def style_v(val):
        if isinstance(val,str) and ('+' in val) and '-' not in val:
            return 'background-color:#DCFCE7;color:#15803D;font-weight:bold;'
        if isinstance(val,str) and '-' in val:
            return 'background-color:#FEE2E2;color:#B91C1C;font-weight:bold;'
        return 'color:#475569;'

    st.dataframe(df_tabla.style.map(style_v, subset=[col_d]),
                 use_container_width=True, hide_index=True, height=550)
    csv = df_tabla.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Exportar Matriz Consolidada (CSV)", csv,
                       f"ENA_auditoria_{yr_max}.csv","text/csv")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="fuente-footer">
  <b>Fuente Oficial de Microdatos:</b> Instituto Nacional de Estadística e Informática (INEI) —
  Encuesta Nacional Agropecuaria (ENA) 2023, 2024 y 2025. Dirección Nacional de Censos y Encuestas.<br>
  * La proyección paramétrica calculada representa una estimación lineal de mínimos cuadrados
  y carece de naturaleza predictiva oficial vinculante. Uso restringido — documento de trabajo interno.
</div>""", unsafe_allow_html=True)
