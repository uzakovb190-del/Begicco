import streamlit as st
from supabase import create_client, Client
from datetime import date, datetime, timedelta
import base64
import io
import csv
import json
import zipfile
import urllib.parse
from collections import Counter

# ============================================
# CONFIG
# ============================================
# Credentials are read from st.secrets (Streamlit Community Cloud → App settings → Secrets).
# The hardcoded values below are only a local fallback — move them fully to secrets ASAP.
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    SUPABASE_URL = "https://gojnzhpapqzodzadetek.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdvam56aHBhcHF6b2R6YWRldGVrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA5MzU4MTcsImV4cCI6MjA5NjUxMTgxN30.5Y2-MXRBmPt-ps1JZ-52qYi2g9lQOED_Lb69uVAwzxk"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(
    page_title="Life Archive",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================
# LOAD WALLPAPER FROM SUPABASE
# ============================================
def get_wallpaper():
    try:
        r = supabase.table("settings").select("value").eq("key", "wallpaper_b64").execute()
        if r.data:
            return r.data[0]["value"]
    except:
        pass
    return None

def get_overlay_opacity():
    try:
        r = supabase.table("settings").select("value").eq("key", "overlay_opacity").execute()
        if r.data:
            return float(r.data[0]["value"])
    except:
        pass
    return 0.6

wallpaper_b64 = get_wallpaper()
overlay_opacity = get_overlay_opacity()

# ============================================
# GLOBAL STYLES — SOFT NOIR THEME
# ============================================
wallpaper_css = ""
if wallpaper_b64:
    wallpaper_css = f"""
    .stApp {{
        background-image: url("data:image/jpeg;base64,{wallpaper_b64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(10, 10, 26, {overlay_opacity});
        z-index: 0;
        pointer-events: none;
    }}
    """

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&family=Playfair+Display:ital,wght@0,400;0,700;1,400;1,700&display=swap');

    {wallpaper_css}

    html, body, [class*="css"] {{
        font-family: 'Syne', sans-serif;
        background-color: #0a0a1a;
        color: #e8e0ff;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #0d0d22 !important;
        border-right: 1px solid #2a2a4a !important;
    }}

    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    .section-header {{
        font-family: 'Syne', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.2rem;
        color: #e8e0ff;
    }}

    .section-sub {{
        font-size: 0.85rem;
        color: #3a3a6a;
        margin-bottom: 1.5rem;
        font-family: 'JetBrains Mono', monospace;
    }}

    .badge {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.5px;
    }}
    .badge-green  {{ background: #1a3a2a; color: #4ade80; border: 1px solid #4ade80; }}
    .badge-yellow {{ background: #3a2e0a; color: #facc15; border: 1px solid #facc15; }}
    .badge-red    {{ background: #3a1212; color: #f87171; border: 1px solid #f87171; }}
    .badge-blue   {{ background: #1a1a3a; color: #818cf8; border: 1px solid #818cf8; }}
    .badge-orange {{ background: #3a1f0a; color: #fb923c; border: 1px solid #fb923c; }}
    .badge-grey   {{ background: #1e1e2e; color: #9ca3af; border: 1px solid #444; }}
    .badge-gold   {{ background: #3a2e00; color: #fbbf24; border: 1px solid #fbbf24; }}
    .badge-purple {{ background: #1a1a3a; color: #a78bfa; border: 1px solid #a78bfa; }}

    .card {{
        background: #0d0d22;
        border: 1px solid #2a2a4a;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
    }}

    .divider {{
        border: none;
        border-top: 1px solid #2a2a4a;
        margin: 1.5rem 0;
    }}

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {{
        background-color: #0d0d22 !important;
        border: 1px solid #2a2a4a !important;
        color: #e8e0ff !important;
        border-radius: 8px !important;
    }}

    .stButton > button {{
        background-color: #0d0d22;
        color: #e8e0ff;
        border: 1px solid #2a2a4a;
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        padding: 0.4rem 1.2rem;
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        border-color: #a78bfa;
        color: #a78bfa;
        background-color: #1a1a3a;
    }}

    .stButton > button[kind="primary"] {{
        background-color: #1a1a3a;
        border-color: #a78bfa;
        color: #a78bfa;
    }}

    .metric-row {{
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }}
    .metric-card {{
        flex: 1;
        background: #0d0d22;
        border: 1px solid #2a2a4a;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        transition: all 0.2s ease;
    }}
    .metric-card:hover {{
        border-color: #a78bfa;
        background: #1a1a3a;
    }}
    .metric-value {{
        font-size: 2rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
    }}
    .metric-label {{
        font-size: 0.75rem;
        color: #3a3a6a;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }}

    .chivalry {{
        font-family: 'Playfair Display', serif;
        font-style: italic;
        color: #9a90cc;
    }}

    /* Page transition */
    @keyframes fadeInPage {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .main .block-container {{
        animation: fadeInPage 0.4s ease forwards;
    }}

    /* Progress bar */
    .progress-bar-bg {{
        background: #1a1a3a;
        border-radius: 10px;
        height: 8px;
        width: 100%;
        margin: 6px 0;
    }}
    .progress-bar-fill {{
        background: linear-gradient(90deg, #a78bfa, #818cf8);
        border-radius: 10px;
        height: 8px;
        transition: width 0.3s ease;
    }}
    /* Force sidebar toggle visible */
    [data-testid="stSidebarCollapseButton"] {{
        background-color: #1a1a3a !important;
        border: 1px solid #a78bfa !important;
        border-radius: 8px !important;
        opacity: 1 !important;
        visibility: visible !important;
    }}
    [data-testid="stSidebarCollapseButton"] svg {{
        fill: #a78bfa !important;
    }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ============================================
# LOGIN GATE (passcode from st.secrets["APP_PASSCODE"])
# ============================================
def _get_passcode():
    try:
        return st.secrets["APP_PASSCODE"]
    except Exception:
        return None

_passcode = _get_passcode()
if _passcode and not st.session_state.get("authed", False):
    st.markdown("""
        <div style="text-align:center;padding-top:4rem;">
            <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:#e8e0ff;">🗂️ Life Archive</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#3a3a6a;margin-top:6px;">private · enter passcode to continue</div>
        </div>
    """, unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        with st.form("login_form"):
            attempt = st.text_input("Passcode", type="password", label_visibility="collapsed", placeholder="Passcode...")
            if st.form_submit_button("Unlock", type="primary", use_container_width=True):
                if attempt == _passcode:
                    st.session_state["authed"] = True
                    st.rerun()
                else:
                    st.error("Wrong passcode.")
    st.stop()

# ============================================
# BADGE HELPERS
# ============================================
def mood_badge(score: int) -> str:
    if score >= 8:
        return f'<span class="badge badge-green">😊 {score}/10</span>'
    elif score >= 5:
        return f'<span class="badge badge-yellow">😐 {score}/10</span>'
    else:
        return f'<span class="badge badge-red">😔 {score}/10</span>'

def clarity_badge(clarity: str) -> str:
    colors = {"sharp": "badge-green", "normal": "badge-blue", "foggy": "badge-orange"}
    icons  = {"sharp": "⚡", "normal": "🔵", "foggy": "🌫️"}
    return f'<span class="badge {colors.get(clarity,"badge-grey")}">{icons.get(clarity,"●")} {clarity}</span>'

def physical_badge(state: str) -> str:
    colors = {"energized": "badge-green", "neutral": "badge-blue", "tired": "badge-red"}
    icons  = {"energized": "⚡", "neutral": "🔵", "tired": "🔴"}
    return f'<span class="badge {colors.get(state,"badge-grey")}">{icons.get(state,"●")} {state}</span>'

def mental_badge(state: str) -> str:
    colors = {"calm": "badge-green", "stable": "badge-blue", "stressed": "badge-orange", "heavy": "badge-red"}
    icons  = {"calm": "🟢", "stable": "🔵", "stressed": "🟠", "heavy": "🔴"}
    return f'<span class="badge {colors.get(state,"badge-grey")}">{icons.get(state,"●")} {state}</span>'

def result_badge(result: str) -> str:
    colors = {"win": "badge-green", "pass": "badge-blue", "fail": "badge-red", "complete": "badge-gold"}
    icons  = {"win": "🏆", "pass": "✅", "fail": "❌", "complete": "⭐"}
    return f'<span class="badge {colors.get(result,"badge-grey")}">{icons.get(result,"●")} {result.upper()}</span>'

def goal_status_badge(status: str) -> str:
    colors = {"active": "badge-green", "paused": "badge-grey", "completed": "badge-gold"}
    icons  = {"active": "🟢", "paused": "⏸️", "completed": "⭐"}
    return f'<span class="badge {colors.get(status,"badge-grey")}">{icons.get(status,"●")} {status.upper()}</span>'

def significance_badge(score: int) -> str:
    if score >= 5:
        return f'<span class="badge badge-gold">★★★★★ {score}/5</span>'
    elif score >= 4:
        return f'<span class="badge badge-orange">★★★★☆ {score}/5</span>'
    elif score >= 3:
        return f'<span class="badge badge-yellow">★★★☆☆ {score}/5</span>'
    else:
        return f'<span class="badge badge-grey">★★☆☆☆ {score}/5</span>'

# ============================================
# EXPORT ENGINE — Excel / CSV(zip) / PDF / Word
# ============================================
EXPORT_FORMATS = ["Excel (.xlsx)", "CSV (.zip)", "PDF", "Word (.docx)"]

def get_export_format() -> str:
    return st.session_state.get("export_format", EXPORT_FORMATS[0])

def _fmt_cell(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, (list, dict)):
        try:
            if isinstance(v, list) and all(isinstance(i, str) for i in v):
                return "; ".join(v)
            return json.dumps(v, ensure_ascii=False)
        except Exception:
            return str(v)
    return str(v)

def _table_columns(rows):
    cols = []
    for r in rows:
        for k in r.keys():
            if k not in cols:
                cols.append(k)
    return cols

def build_export_bytes(tables: dict, fmt: str, doc_title: str = "Life Archive Export"):
    """tables: {section_name: [row_dict, ...]} → (bytes, extension, mime)"""
    if fmt.startswith("Excel"):
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        wb = Workbook()
        wb.remove(wb.active)
        header_font = Font(bold=True, color="FFE8E0FF")
        header_fill = PatternFill("solid", fgColor="FF1A1A3A")
        for name, rows in tables.items():
            ws = wb.create_sheet(title=(name[:31] or "Sheet"))
            cols = _table_columns(rows)
            if not cols:
                ws.append(["(empty)"])
                continue
            ws.append(cols)
            for c in range(1, len(cols) + 1):
                cell = ws.cell(row=1, column=c)
                cell.font = header_font
                cell.fill = header_fill
            for r in rows:
                ws.append([_fmt_cell(r.get(c)) for c in cols])
            for i, c in enumerate(cols, start=1):
                width = max([len(str(c))] + [min(len(_fmt_cell(r.get(c))), 60) for r in rows])
                ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = min(max(width + 2, 10), 62)
        buf = io.BytesIO()
        wb.save(buf)
        return buf.getvalue(), "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    if fmt.startswith("CSV"):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, rows in tables.items():
                s = io.StringIO()
                cols = _table_columns(rows)
                writer = csv.writer(s)
                writer.writerow(cols if cols else ["(empty)"])
                for r in rows:
                    writer.writerow([_fmt_cell(r.get(c)) for c in cols])
                safe = "".join(ch if ch.isalnum() or ch in "-_ " else "_" for ch in name).strip() or "table"
                zf.writestr(f"{safe}.csv", s.getvalue())
        return buf.getvalue(), "zip", "application/zip"

    if fmt == "PDF":
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from xml.sax.saxutils import escape as xesc
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=16*mm, rightMargin=16*mm, topMargin=16*mm, bottomMargin=16*mm)
        styles = getSampleStyleSheet()
        h1 = ParagraphStyle("h1x", parent=styles["Heading1"], textColor=colors.HexColor("#4C1D95"))
        h2 = ParagraphStyle("h2x", parent=styles["Heading2"], textColor=colors.HexColor("#6D28D9"))
        body = ParagraphStyle("bodyx", parent=styles["BodyText"], fontSize=9, leading=12)
        story = [Paragraph(xesc(doc_title), h1), Spacer(1, 6)]
        for name, rows in tables.items():
            story.append(Paragraph(xesc(name), h2))
            if not rows:
                story.append(Paragraph("(empty)", body))
                story.append(Spacer(1, 8))
                continue
            cols = _table_columns(rows)
            for r in rows:
                data = [[Paragraph(f"<b>{xesc(str(c))}</b>", body), Paragraph(xesc(_fmt_cell(r.get(c)))[:2000], body)] for c in cols]
                t = Table(data, colWidths=[45*mm, 125*mm])
                t.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C4B5FD")),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EDE9FE")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                story.append(t)
                story.append(Spacer(1, 8))
        doc.build(story)
        return buf.getvalue(), "pdf", "application/pdf"

    # Word (.docx)
    from docx import Document
    from docx.shared import Pt, RGBColor
    d = Document()
    d.add_heading(doc_title, level=0)
    for name, rows in tables.items():
        d.add_heading(name, level=1)
        if not rows:
            d.add_paragraph("(empty)")
            continue
        cols = _table_columns(rows)
        for r in rows:
            t = d.add_table(rows=0, cols=2)
            try:
                t.style = "Light Grid Accent 4"
            except Exception:
                pass
            for c in cols:
                cells = t.add_row().cells
                run = cells[0].paragraphs[0].add_run(str(c))
                run.bold = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0x6D, 0x28, 0xD9)
                r2 = cells[1].paragraphs[0].add_run(_fmt_cell(r.get(c)))
                r2.font.size = Pt(9)
            d.add_paragraph("")
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue(), "docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

def export_download_button(label: str, tables: dict, filename_base: str, key: str, doc_title: str = "Life Archive Export"):
    """A download button that respects the session-wide export format picker (Settings)."""
    fmt = get_export_format()
    try:
        data, ext, mime = build_export_bytes(tables, fmt, doc_title)
    except Exception as ex:
        st.error(f"Export failed: {ex}")
        return
    st.download_button(f"{label} · {fmt}", data=data, file_name=f"{filename_base}.{ext}", mime=mime, key=key)

def telegram_share_link(text: str) -> str:
    return "https://t.me/share/url?url=%20&text=" + urllib.parse.quote(text)

def share_block(text: str, state_key: str, button_label: str = "📤 Share"):
    """Toggleable share text area + Telegram link (Daily Log / Outcomes pattern)."""
    if st.button(button_label, key=f"btn_{state_key}"):
        st.session_state[state_key] = not st.session_state.get(state_key, False)
        st.rerun()
    if st.session_state.get(state_key, False):
        st.text_area("Copy & share", value=text, height=220, key=f"txt_{state_key}")
        st.markdown(
            f'<a href="{telegram_share_link(text)}" target="_blank" style="font-family:\'JetBrains Mono\',monospace;'
            f'font-size:0.8rem;color:#818CF8;text-decoration:none;">✈️ Send via Telegram →</a>',
            unsafe_allow_html=True,
        )

def card_html(inner: str, style: str = "") -> str:
    """Builds card HTML on a single line so Streamlit's markdown never treats
    indented HTML lines as code blocks (the root cause of the raw-HTML Goals bug)."""
    inner = " ".join(line.strip() for line in inner.splitlines())
    return f'<div class="card" style="{style}">{inner}</div>'

def hbar_block(title: str, items: list, colors_cycle=None) -> str:
    """Minimal horizontal bar chart in the app palette. items: [(label, value, value_label)]"""
    if colors_cycle is None:
        colors_cycle = ["#A78BFA", "#4ADE80", "#FACC15", "#818CF8", "#C084FC", "#F87171"]
    max_v = max([v for _, v, _ in items] or [1]) or 1
    rows = ""
    for i, (label, v, vlabel) in enumerate(items):
        pct = max(int((v / max_v) * 100), 2)
        color = colors_cycle[i % len(colors_cycle)]
        rows += (
            f'<div style="margin-bottom:0.55rem;">'
            f'<div style="display:flex;justify-content:space-between;font-family:\'JetBrains Mono\',monospace;font-size:0.75rem;color:#9a90cc;margin-bottom:3px;">'
            f'<span>{label}</span><span>{vlabel}</span></div>'
            f'<div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%;background:{color};"></div></div>'
            f'</div>'
        )
    head = f'<div style="font-size:0.75rem;color:#3a3a6a;font-family:\'JetBrains Mono\',monospace;margin-bottom:0.8rem;letter-spacing:1px;">{title}</div>'
    return card_html(head + rows)


def skill_level_badge(level: str) -> str:
    colors = {"beginner": "badge-blue", "intermediate": "badge-yellow", "advanced": "badge-orange", "master": "badge-gold"}
    return f'<span class="badge {colors.get(level,"badge-grey")}">⚡ {level.upper()}</span>'

# ============================================
# NAVIGATION
# ============================================
nav_options = [
    "🏠  Home",
    "📝  Daily Log",
    "📖  Reading Log",
    "🚨  Life Event",
    "🛍️  Purchase Tracker",
    "💫  Wish List",
    "🎯  Goals",
    "🏆  Outcomes",
    "🧠  Skills",
    "📜  Archive",
    "⚙️  Settings",
]

if "nav_override_counter" not in st.session_state:
    st.session_state["nav_override_counter"] = 0
if "current_page_override" not in st.session_state:
    st.session_state["current_page_override"] = None

with st.sidebar:
    st.markdown("""
        <div style="padding: 1rem 0 1.5rem 0;">
            <div style="font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 800; color: #e8e0ff;">
                🗂️ Life Archive
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #3a3a6a; margin-top: 4px;">
                personal memory system
            </div>
        </div>
        <hr style="border-color: #2a2a4a; margin-bottom: 1rem;">
    """, unsafe_allow_html=True)

    if st.session_state.get("current_page_override"):
        default_index = nav_options.index(st.session_state["current_page_override"])
        st.session_state["current_page_override"] = None
        st.session_state["nav_override_counter"] += 1
    else:
        default_index = 0

    page = st.radio(
        "Navigation",
        options=nav_options,
        index=default_index,
        label_visibility="collapsed",
        key=f"sidebar_nav_{st.session_state['nav_override_counter']}"
    )

    st.markdown("""
        <hr style="border-color: #2a2a4a; margin-top: 1rem;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #2a2a4a; padding: 0.5rem 0;">
            v2.0 · soft noir · built for self-awareness
        </div>
    """, unsafe_allow_html=True)


# ============================================
# HOME PAGE
# ============================================
if page == "🏠  Home":
    st.markdown("<h1 style='font-family:Syne,sans-serif;font-size:2.2rem;font-weight:800;color:#e8e0ff;'>Welcome back, Captain 🫡</h1>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Today is {date.today().strftime("%A, %B %d %Y")} · Your archive is running.</div>', unsafe_allow_html=True)

    try:
        total_logs     = supabase.table("daily_logs").select("id", count="exact").execute().count or 0
        total_goals    = supabase.table("goals").select("id", count="exact").execute().count or 0
        total_wishes   = supabase.table("wishes").select("id", count="exact").execute().count or 0
        total_outcomes = supabase.table("outcomes").select("id", count="exact").execute().count or 0
    except:
        total_logs = total_goals = total_wishes = total_outcomes = 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'''<div class="metric-card"><div class="metric-value" style="color:#4ade80">{total_logs}</div><div class="metric-label">Days Logged</div></div>''', unsafe_allow_html=True)
        if st.button("→ Daily Log History", key="home_dailylog", use_container_width=True):
            st.session_state["current_page_override"] = "📜  Archive"
            st.session_state["archive_view_override"] = "📅 Daily Log History"
            st.session_state["nav_override_counter"] = st.session_state.get("nav_override_counter", 0) + 1
            st.rerun()
    with col2:
        st.markdown(f'''<div class="metric-card"><div class="metric-value" style="color:#a78bfa">{total_goals}</div><div class="metric-label">Active Goals</div></div>''', unsafe_allow_html=True)
        if st.button("→ Goals", key="home_goals", use_container_width=True):
            st.session_state["current_page_override"] = "🎯  Goals"
            st.session_state["nav_override_counter"] = st.session_state.get("nav_override_counter", 0) + 1
            st.rerun()
    with col3:
        st.markdown(f'''<div class="metric-card"><div class="metric-value" style="color:#c084fc">{total_wishes}</div><div class="metric-label">Wishes</div></div>''', unsafe_allow_html=True)
        if st.button("→ Wish List", key="home_wishes", use_container_width=True):
            st.session_state["current_page_override"] = "💫  Wish List"
            st.session_state["nav_override_counter"] = st.session_state.get("nav_override_counter", 0) + 1
            st.rerun()
    with col4:
        st.markdown(f'''<div class="metric-card"><div class="metric-value" style="color:#818cf8">{total_outcomes}</div><div class="metric-label">Outcomes</div></div>''', unsafe_allow_html=True)
        if st.button("→ Outcomes", key="home_outcomes", use_container_width=True):
            st.session_state["current_page_override"] = "🏆  Outcomes"
            st.session_state["nav_override_counter"] = st.session_state.get("nav_override_counter", 0) + 1
            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div style="font-size:0.75rem; color:#3a3a6a; font-family:'JetBrains Mono',monospace; margin-bottom:0.6rem; letter-spacing:1px;">WHAT THIS IS</div>
        <div class="chivalry" style="font-size:1.05rem; line-height:1.9;">
            This is your private life archive. Not a productivity tool. Not a habit tracker.<br>
            <em>A structured memory of who you are, what you tried, and what actually happened.</em><br><br>
            Every entry you make becomes a permanent, queryable record of your life.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- Stats snapshot: share / export ----
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    try:
        _snap_logs = supabase.table("daily_logs").select("mood_score,date").execute().data or []
        _snap_books = supabase.table("books").select("status", count="exact").eq("status", "finished").execute().count or 0
        _snap_skills = supabase.table("skills").select("id", count="exact").execute().count or 0
    except:
        _snap_logs, _snap_books, _snap_skills = [], 0, 0
    _avg_mood = (sum(l.get("mood_score", 0) or 0 for l in _snap_logs) / len(_snap_logs)) if _snap_logs else 0
    snapshot_rows = {
        "Days Logged": total_logs,
        "Average Mood": f"{_avg_mood:.1f}/10",
        "Active Goals": total_goals,
        "Wishes": total_wishes,
        "Outcomes": total_outcomes,
        "Books Finished": _snap_books,
        "Skills Tracked": _snap_skills,
    }
    snapshot_text = (
        "🗂️ Life Archive — Stats Snapshot\n"
        f"📅 {date.today().strftime('%B %d, %Y')}\n"
        + "\n".join(f"{k}: {v}" for k, v in snapshot_rows.items())
        + "\n— sent from Life Archive"
    )
    st.markdown(card_html(f"""
        <div style="font-size:0.75rem;color:#3a3a6a;font-family:'JetBrains Mono',monospace;margin-bottom:0.6rem;letter-spacing:1px;">STATS SNAPSHOT</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.85rem;color:#9a90cc;line-height:2;">
        {' · '.join(f'<b style=color:#e8e0ff>{v}</b> {k.lower()}' for k, v in snapshot_rows.items())}
        </div>
    """), unsafe_allow_html=True)
    col_share, col_dl = st.columns([1, 1])
    with col_share:
        share_block(snapshot_text, "home_snapshot_share", "📤 Share Snapshot")
    with col_dl:
        export_download_button("⬇️ Download Snapshot",
                               {"Stats Snapshot": [dict(snapshot_rows)]},
                               f"life-archive-snapshot-{date.today()}",
                               key="dl_home_snapshot",
                               doc_title="Life Archive — Stats Snapshot")

    st.markdown("""
    <div class="card">
        <div style="font-size:0.75rem; color:#3a3a6a; font-family:'JetBrains Mono',monospace; margin-bottom:0.8rem; letter-spacing:1px;">QUICK START</div>
        <div class="chivalry" style="font-size:1rem; line-height:2.2;">
            📝 &nbsp;<b>Daily Log</b> — start here every day<br>
            💫 &nbsp;<b>Wish List</b> — add anything you want to pursue<br>
            🎯 &nbsp;<b>Goals</b> — activate a wish and start tracking<br>
            🏆 &nbsp;<b>Outcomes</b> — record what happened when it ended<br>
            🧠 &nbsp;<b>Skills</b> — track mastery hour by hour<br>
            📜 &nbsp;<b>Archive</b> — browse your full history
        </div>
    </div>
    """, unsafe_allow_html=True)

elif page == "📝  Daily Log":
    st.markdown('<div class="section-header">📝 Daily Log</div>', unsafe_allow_html=True)
    today = date.today()
    st.markdown(f'<div class="section-sub">{today.strftime("%A, %B %d %Y")}</div>', unsafe_allow_html=True)

    # ---- Init session state lists ----
    if "accomplishments" not in st.session_state:
        st.session_state.accomplishments = []
    if "media_list" not in st.session_state:
        st.session_state.media_list = []
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
    if "workout_list" not in st.session_state:
        st.session_state.workout_list = []

    # ---- Check if today already logged ----
    try:
        existing = supabase.table("daily_logs").select("*").eq("date", str(today)).execute()
        already_logged = len(existing.data) > 0
        existing_entry = existing.data[0] if already_logged else None
    except:
        already_logged = False
        existing_entry = None

    # ---- VIEW MODE (already logged, not editing) ----
    if already_logged and not st.session_state.edit_mode:
        e = existing_entry
        st.markdown(f'<div class="section-sub">✅ Today\'s entry is saved.</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Mood** &nbsp; {mood_badge(e['mood_score'])}", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**Clarity** &nbsp; {clarity_badge(e['mental_clarity'])}", unsafe_allow_html=True)
        with col3:
            st.markdown(f"**Emotion** &nbsp; `{e['dominant_emotion']}`", unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card">
            <div style="font-size:0.75rem;color:#555;font-family:'JetBrains Mono',monospace;margin-bottom:0.5rem;">SELF ASSESSMENT</div>
            <div style="color:#ccc;">{e.get('self_assessment','—')}</div>
        </div>
        <div class="card">
            <div style="font-size:0.75rem;color:#555;font-family:'JetBrains Mono',monospace;margin-bottom:0.5rem;">DAILY SUMMARY</div>
            <div style="color:#ccc;">{e.get('daily_summary','—')}</div>
        </div>
        """, unsafe_allow_html=True)

        accs = e.get('accomplishments') or []
        media = e.get('media_consumed') or []

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card"><div style="font-size:0.75rem;color:#555;font-family:\'JetBrains Mono\',monospace;margin-bottom:0.5rem;">ACCOMPLISHMENTS</div>', unsafe_allow_html=True)
            for a in accs:
                st.markdown(f"&nbsp; ✦ {a}")
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="card"><div style="font-size:0.75rem;color:#555;font-family:\'JetBrains Mono\',monospace;margin-bottom:0.5rem;">MEDIA CONSUMED</div>', unsafe_allow_html=True)
            for m in media:
                st.markdown(f"&nbsp; 🎬 {m}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"**Sleep** &nbsp; `{e.get('sleep_duration','—')} hrs`")
        with col2:
            st.markdown(f"**Physical** &nbsp; {physical_badge(e.get('physical_state','neutral'))}", unsafe_allow_html=True)
        with col3:
            st.markdown(f"**Mental** &nbsp; {mental_badge(e.get('mental_state','stable'))}", unsafe_allow_html=True)
        with col4:
            st.markdown(f"**Spent** &nbsp; `{e.get('daily_spending',0)} UZS`")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown(f"**Good deed:** {e.get('good_deed','—')}")

        # ---- Exercise & Training (view) ----
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.75rem;color:#555;font-family:\'JetBrains Mono\',monospace;margin-bottom:0.8rem;letter-spacing:1px;">F · EXERCISE & TRAINING</div>', unsafe_allow_html=True)
        if e.get("rest_day"):
            st.markdown('<span class="badge badge-grey">😴 Rest day</span>', unsafe_allow_html=True)
        else:
            workouts = e.get("workouts") or []
            if isinstance(workouts, str):
                try:
                    workouts = json.loads(workouts)
                except:
                    workouts = []
            w_lines = "".join(
                f'<div style="margin-bottom:4px;">🥊 <b>{w.get("type","")}</b>'
                f'{" — " + w.get("label","") if w.get("label") else ""}</div>'
                for w in workouts
            ) or '<div style="color:#555;">no workouts logged</div>'
            intensity_cls = {"light": "badge-blue", "moderate": "badge-yellow", "hard": "badge-red", "max": "badge-red"}.get(e.get("training_intensity",""), "badge-grey")
            st.markdown(card_html(f"""
                {w_lines}
                <div style="margin-top:0.6rem;font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#888;">
                    ⏱ {e.get('training_duration',0) or 0} min ·
                    <span class="badge {intensity_cls}">{e.get('training_intensity') or '—'}</span> ·
                    body felt: {e.get('body_feel') or '—'}
                </div>
                {f'<div style="margin-top:0.5rem;color:#aaa;font-size:0.85rem;">📝 ' + e['training_notes'] + '</div>' if e.get('training_notes') else ''}
            """), unsafe_allow_html=True)

        # ---- Training streak (last 60 logs) ----
        try:
            _streak_logs = supabase.table("daily_logs").select("date,rest_day,training_duration").order("date", desc=True).limit(60).execute().data or []
        except:
            _streak_logs = []
        _by_date = {l["date"]: l for l in _streak_logs}
        streak = 0
        _cursor = date.today()
        while True:
            l = _by_date.get(str(_cursor))
            if l and not l.get("rest_day") and (l.get("training_duration") or 0) > 0:
                streak += 1
                _cursor -= timedelta(days=1)
            else:
                break
        streak_label = f"🔥 {streak} day streak" if streak == 1 else f"🔥 {streak} days in a row"
        if streak > 0:
            st.markdown(card_html(f"""
                <div style="text-align:center;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:800;color:#FACC15;">{streak_label}</div>
                    <div style="font-size:0.7rem;color:#3a3a6a;font-family:'JetBrains Mono',monospace;margin-top:4px;">CONSECUTIVE TRAINING DAYS</div>
                </div>
            """), unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.75rem;color:#3a3a6a;">🔥 no active training streak</div>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # ---- Share + download today's entry ----
        _workouts_txt = ""
        if not e.get("rest_day"):
            _w = e.get("workouts") or []
            if isinstance(_w, str):
                try:
                    _w = json.loads(_w)
                except:
                    _w = []
            _workouts_txt = ", ".join(f"{x.get('type','')}{' (' + x.get('label','') + ')' if x.get('label') else ''}" for x in _w)
        day_share_text = (
            "📝 Life Archive — Daily Log\n"
            f"📅 {today.strftime('%B %d, %Y')}\n"
            f"Mood: {e.get('mood_score','—')}/10 · Clarity: {e.get('mental_clarity','—')} · Emotion: {e.get('dominant_emotion','—')}\n"
            f"Summary: {e.get('daily_summary','—')}\n"
            f"Accomplishments: {'; '.join(e.get('accomplishments') or []) or '—'}\n"
            f"Sleep: {e.get('sleep_duration','—')} hrs · Spent: {e.get('daily_spending',0)}\n"
            + ("Training: rest day" if e.get("rest_day") else f"Training: {_workouts_txt or '—'} · {e.get('training_duration',0) or 0} min · {e.get('training_intensity') or '—'}")
            + (f"\n{streak_label}" if streak > 0 else "")
            + "\n— sent from Life Archive"
        )
        col_share, col_dl, col_edit = st.columns([1, 1, 1])
        with col_share:
            share_block(day_share_text, "daily_share_toggle", "📤 Share Today")
        with col_dl:
            export_download_button("⬇️ Download Entry", {f"Daily Log {today}": [e]},
                                   f"daily-log-{today}", key="dl_daily_entry",
                                   doc_title=f"Life Archive — Daily Log {today}")
        with col_edit:
            if st.button("✏️ Edit Today's Entry"):
                st.session_state.edit_mode = True
                st.session_state.accomplishments = e.get('accomplishments') or []
                st.session_state.media_list = e.get('media_consumed') or []
                _w = e.get('workouts') or []
                if isinstance(_w, str):
                    try:
                        _w = json.loads(_w)
                    except:
                        _w = []
                st.session_state.workout_list = _w
                st.rerun()

    # ---- FORM MODE (new entry or editing) ----
    else:
        if already_logged:
            st.info("Editing today's entry. Changes will overwrite the saved record.")
            e = existing_entry
        else:
            e = {}

        # --- Section A: Emotional & Cognitive ---
        st.markdown('<div style="font-size:0.75rem;color:#555;font-family:\'JetBrains Mono\',monospace;margin-bottom:0.8rem;letter-spacing:1px;">A · EMOTIONAL & COGNITIVE STATE</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            mood_score = st.slider("Mood Score", 1, 10, e.get('mood_score', 5))
        with col2:
            st.markdown(f"<br>{mood_badge(mood_score)}", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            clarity_options = ["foggy", "normal", "sharp"]
            clarity_default = clarity_options.index(e.get('mental_clarity', 'normal'))
            mental_clarity = st.selectbox("Mental Clarity", clarity_options, index=clarity_default)
        with col2:
            st.markdown(f"<br>{clarity_badge(mental_clarity)}", unsafe_allow_html=True)

        dominant_emotion = st.text_input("Dominant Emotion", value=e.get('dominant_emotion', ''), placeholder="e.g. anxious, hopeful, calm...")
        self_assessment = st.text_area("Self Assessment of the Day", value=e.get('self_assessment', ''), height=100, placeholder="How do you feel about today overall?")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # --- Section B: Activity ---
        st.markdown('<div style="font-size:0.75rem;color:#555;font-family:\'JetBrains Mono\',monospace;margin-bottom:0.8rem;letter-spacing:1px;">B · ACTIVITY SUMMARY</div>', unsafe_allow_html=True)

        daily_summary = st.text_area("Daily Summary", value=e.get('daily_summary', ''), height=100, placeholder="What happened today?")
        good_deed = st.text_input("Good Deed of the Day", value=e.get('good_deed', ''), placeholder="One good thing you did for someone...")

        # Accomplishments list
        st.markdown("**Accomplishments**")
        acc_col1, acc_col2 = st.columns([4, 1])
        with acc_col1:
            new_acc = st.text_input("Add accomplishment", key="new_acc_input", label_visibility="collapsed", placeholder="What did you accomplish today?")
        with acc_col2:
            if st.button("＋ Add", key="add_acc"):
                if new_acc.strip():
                    st.session_state.accomplishments.append(new_acc.strip())
                    st.rerun()

        for i, acc in enumerate(st.session_state.accomplishments):
            c1, c2 = st.columns([6, 1])
            with c1:
                st.markdown(f"&nbsp; ✦ {acc}")
            with c2:
                if st.button("✕", key=f"del_acc_{i}"):
                    st.session_state.accomplishments.pop(i)
                    st.rerun()

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # --- Section C: Health ---
        st.markdown('<div style="font-size:0.75rem;color:#555;font-family:\'JetBrains Mono\',monospace;margin-bottom:0.8rem;letter-spacing:1px;">C · HEALTH</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            sleep_duration = st.number_input("Sleep Duration (hours)", min_value=0.0, max_value=24.0, step=0.5, value=float(e.get('sleep_duration') or 7.0))
            phone_off = st.time_input("Phone Off Time", value=None)
        with col2:
            phone_on = st.time_input("Phone On Time", value=None)
            dream_log = st.text_input("Dream Log (optional)", value=e.get('dream_log', ''), placeholder="Any dreams worth noting?")

        col1, col2 = st.columns(2)
        with col1:
            phys_options = ["tired", "neutral", "energized"]
            phys_default = phys_options.index(e.get('physical_state', 'neutral'))
            physical_state = st.selectbox("Physical State", phys_options, index=phys_default)
            st.markdown(physical_badge(physical_state), unsafe_allow_html=True)
        with col2:
            ment_options = ["calm", "stable", "stressed", "heavy"]
            ment_default = ment_options.index(e.get('mental_state', 'stable'))
            mental_state = st.selectbox("Mental State", ment_options, index=ment_default)
            st.markdown(mental_badge(mental_state), unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # --- Section D: Spending ---
        st.markdown('<div style="font-size:0.75rem;color:#555;font-family:\'JetBrains Mono\',monospace;margin-bottom:0.8rem;letter-spacing:1px;">D · SPENDING</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            daily_spending = st.number_input("Daily Spending Total (UZS)", min_value=0.0, step=1000.0, value=float(e.get('daily_spending') or 0.0))
        with col2:
            spending_notes = st.text_input("Spending Notes", value=e.get('spending_notes', ''), placeholder="What did you spend on?")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # --- Section E: Media ---
        st.markdown('<div style="font-size:0.75rem;color:#555;font-family:\'JetBrains Mono\',monospace;margin-bottom:0.8rem;letter-spacing:1px;">E · MEDIA CONSUMED</div>', unsafe_allow_html=True)

        med_col1, med_col2 = st.columns([4, 1])
        with med_col1:
            new_media = st.text_input("Add media", key="new_media_input", label_visibility="collapsed", placeholder="Anime / movie / series title...")
        with med_col2:
            if st.button("＋ Add", key="add_media"):
                if new_media.strip():
                    st.session_state.media_list.append(new_media.strip())
                    st.rerun()

        for i, m in enumerate(st.session_state.media_list):
            c1, c2 = st.columns([6, 1])
            with c1:
                st.markdown(f"&nbsp; 🎬 {m}")
            with c2:
                if st.button("✕", key=f"del_media_{i}"):
                    st.session_state.media_list.pop(i)
                    st.rerun()

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # --- Section F: Exercise & Training ---
        st.markdown('<div style="font-size:0.75rem;color:#555;font-family:\'JetBrains Mono\',monospace;margin-bottom:0.8rem;letter-spacing:1px;">F · EXERCISE & TRAINING</div>', unsafe_allow_html=True)

        rest_day = st.toggle("😴 Rest day (no training today)", value=bool(e.get("rest_day", False)))

        if not rest_day:
            st.markdown("**Workout sessions**")
            workout_types = ["Gym", "Boxing", "Running", "Football", "Swimming", "Home workout", "Stretching", "Other"]
            wcol1, wcol2, wcol3 = st.columns([2, 3, 1])
            with wcol1:
                new_w_type = st.selectbox("Type", workout_types, key="new_workout_type", label_visibility="collapsed")
            with wcol2:
                new_w_label = st.text_input("Label", key="new_workout_label", label_visibility="collapsed", placeholder="e.g. push day, 5km, sparring...")
            with wcol3:
                if st.button("＋ Add", key="add_workout"):
                    st.session_state.workout_list.append({"type": new_w_type, "label": new_w_label.strip()})
                    st.rerun()

            for i, w in enumerate(st.session_state.workout_list):
                c1, c2 = st.columns([6, 1])
                with c1:
                    st.markdown(f"&nbsp; 🥊 **{w.get('type','')}**{' — ' + w.get('label','') if w.get('label') else ''}")
                with c2:
                    if st.button("✕", key=f"del_workout_{i}"):
                        st.session_state.workout_list.pop(i)
                        st.rerun()

            col1, col2 = st.columns(2)
            with col1:
                training_duration = st.number_input("Total training duration (minutes)", min_value=0, step=5, value=int(e.get("training_duration") or 0))
                intensity_opts = ["light", "moderate", "hard", "max"]
                training_intensity = st.selectbox("Intensity", intensity_opts,
                                                  index=intensity_opts.index(e.get("training_intensity")) if e.get("training_intensity") in intensity_opts else 1)
            with col2:
                feel_opts = ["great", "good", "normal", "sore", "exhausted", "injured"]
                body_feel = st.selectbox("How did your body feel?", feel_opts,
                                         index=feel_opts.index(e.get("body_feel")) if e.get("body_feel") in feel_opts else 2)
                training_notes = st.text_area("Training notes", value=e.get("training_notes") or "", height=68, placeholder="PRs, technique notes, how it went...")
        else:
            training_duration = 0
            training_intensity = None
            body_feel = None
            training_notes = ""

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # --- Save Button ---
        if st.button("💾 Save Day", type="primary"):
            if not dominant_emotion.strip():
                st.error("Please enter your dominant emotion.")
            else:
                record = {
                    "date": str(today),
                    "mood_score": mood_score,
                    "mental_clarity": mental_clarity,
                    "dominant_emotion": dominant_emotion.strip(),
                    "self_assessment": self_assessment.strip(),
                    "daily_summary": daily_summary.strip(),
                    "accomplishments": st.session_state.accomplishments,
                    "good_deed": good_deed.strip(),
                    "sleep_duration": sleep_duration,
                    "phone_off_time": str(phone_off) if phone_off else None,
                    "phone_on_time": str(phone_on) if phone_on else None,
                    "dream_log": dream_log.strip(),
                    "physical_state": physical_state,
                    "mental_state": mental_state,
                    "daily_spending": daily_spending,
                    "spending_notes": spending_notes.strip(),
                    "media_consumed": st.session_state.media_list,
                    "rest_day": rest_day,
                    "workouts": st.session_state.workout_list if not rest_day else [],
                    "training_duration": training_duration,
                    "training_intensity": training_intensity,
                    "body_feel": body_feel,
                    "training_notes": training_notes.strip() if training_notes else "",
                }
                try:
                    if already_logged:
                        supabase.table("daily_logs").update(record).eq("date", str(today)).execute()
                        st.success("✅ Entry updated.")
                    else:
                        supabase.table("daily_logs").insert(record).execute()
                        st.success("✅ Day saved to your archive.")
                    st.session_state.edit_mode = False
                    st.session_state.accomplishments = []
                    st.session_state.media_list = []
                    st.session_state.workout_list = []
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error saving: {ex}")

        if already_logged and st.button("Cancel"):
            st.session_state.edit_mode = False
            st.rerun()

elif page == "📖  Reading Log":
    st.markdown('<div class="section-header">📖 Reading Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">track every book · session by session</div>', unsafe_allow_html=True)

    # ---- Fetch all books ----
    try:
        all_books = supabase.table("books").select("*").order("created_at", desc=False).execute().data or []
        reading_books   = [b for b in all_books if b["status"] == "reading"]
        finished_books  = [b for b in all_books if b["status"] == "finished"]
    except:
        all_books = reading_books = finished_books = []

    # ---- Tabs ----
    tab1, tab2, tab3 = st.tabs(["📚 Currently Reading", "✅ Finished Shelf", "➕ Add New Book"])

    # ============================================================
    # TAB 1 — CURRENTLY READING
    # ============================================================
    with tab1:
        if not reading_books:
            st.info("No books in progress. Add one in the 'Add New Book' tab.")
        else:
            for book in reading_books:
                # Fetch sessions for this book
                try:
                    sessions = supabase.table("reading_sessions").select("*").eq("book_id", book["id"]).order("session_date", desc=False).execute().data or []
                except:
                    sessions = []

                total_read = sum(s["pages_read"] for s in sessions)
                total_pages = book["total_pages"]
                progress = min(int((total_read / total_pages) * 100), 100) if total_pages > 0 else 0

                # Inactivity check
                inactive_warning = ""
                if sessions:
                    from datetime import datetime, timedelta
                    last_session_date = datetime.strptime(sessions[-1]["session_date"], "%Y-%m-%d").date()
                    days_since = (date.today() - last_session_date).days
                    if days_since >= 7:
                        inactive_warning = f'<span class="badge badge-red">🔴 {days_since} days inactive</span>'

                # Progress circle via SVG
                radius = 36
                circumference = 2 * 3.14159 * radius
                stroke_offset = circumference * (1 - progress / 100)
                circle_color = "#4ade80" if progress >= 75 else "#facc15" if progress >= 40 else "#60a5fa"

                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown(f"""
                    <div style="display:flex;justify-content:center;align-items:center;padding:1rem 0;">
                        <svg width="100" height="100" viewBox="0 0 100 100">
                            <circle cx="50" cy="50" r="{radius}" fill="none" stroke="#2a2a2a" stroke-width="8"/>
                            <circle cx="50" cy="50" r="{radius}" fill="none" stroke="{circle_color}" stroke-width="8"
                                stroke-dasharray="{circumference:.1f}"
                                stroke-dashoffset="{stroke_offset:.1f}"
                                stroke-linecap="round"
                                transform="rotate(-90 50 50)"/>
                            <text x="50" y="54" text-anchor="middle" fill="#fff"
                                font-family="JetBrains Mono" font-size="14" font-weight="700">{progress}%</text>
                        </svg>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"### {book['title']}")
                    genre_badge = f'<span class="badge badge-purple">{book["genre"]}</span> ' if book.get("genre") else ""
                    if inactive_warning or genre_badge:
                        st.markdown(genre_badge + inactive_warning, unsafe_allow_html=True)
                    est_finish_txt = ""
                    if sessions and total_pages > total_read:
                        first_session_date = datetime.strptime(sessions[0]["session_date"], "%Y-%m-%d").date()
                        days_elapsed = max((date.today() - first_session_date).days, 1)
                        pace = total_read / days_elapsed  # pages per day
                        if pace > 0:
                            est_days = int((total_pages - total_read) / pace) + 1
                            est_finish_txt = f" · 📅 est. finish {(date.today() + timedelta(days=est_days)).strftime('%b %d')}"
                    st.caption(f"{book.get('author','Unknown')} · {total_read} / {total_pages} pages · {len(sessions)} sessions{est_finish_txt}")

                    if sessions:
                        with st.expander(f"🗂 {len(sessions)} past sessions", expanded=st.session_state.get(f"show_past_{book['id']}", False)):
                            for s in reversed(sessions):
                                stars = '★' * s['session_rating'] + '☆' * (5 - s['session_rating'])
                                st.markdown(f"""
                                <div class="card" style="margin-bottom:0.4rem;">
                                    <div style="display:flex;justify-content:space-between;">
                                        <span style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#888;">{s['session_date']}</span>
                                        <span class="badge badge-blue">+{s['pages_read']} pages</span>
                                        <span class="badge badge-yellow">{stars}</span>
                                    </div>
                                    <div style="margin-top:0.4rem;color:#ccc;font-size:0.85rem;">{s.get('learned','—')}</div>
                                    {f'<div style="margin-top:0.5rem;padding:0.5rem 0.8rem;border-left:3px solid #A78BFA;background:#1A1A3A;border-radius:0 8px 8px 0;font-style:italic;color:#C4B5FD;font-size:0.85rem;">❝ ' + s["highlight"] + ' ❞</div>' if s.get("highlight") else ''}
                                </div>
                                """, unsafe_allow_html=True)

                    with st.expander(f"➕ Log new session — '{book['title']}'", expanded=not st.session_state.get(f"show_past_{book['id']}", False)):
                        s_pages = st.number_input("Pages read today", min_value=1, step=1, key=f"pages_{book['id']}")
                        s_learned = st.text_area("What did you learn?", key=f"learned_{book['id']}", height=80)
                        s_highlight = st.text_area("Quote or passage worth saving (optional)", key=f"highlight_{book['id']}", height=70, placeholder="A line that stuck with you...")
                        s_rating = st.slider("How was the session?", 1, 5, 3, key=f"srating_{book['id']}")

                        if st.button("Save Session", key=f"save_session_{book['id']}"):
                            try:
                                supabase.table("reading_sessions").insert({
                                    "book_id": book["id"],
                                    "session_date": str(date.today()),
                                    "pages_read": s_pages,
                                    "learned": s_learned.strip(),
                                    "highlight": s_highlight.strip(),
                                    "session_rating": s_rating
                                }).execute()
                                new_total = total_read + s_pages
                                if new_total >= total_pages:
                                    st.session_state[f"complete_{book['id']}"] = True
                                    st.success("🎉 You finished the book!")
                                else:
                                    st.success(f"✅ Session saved! {total_pages - new_total} pages left.")
                                st.session_state[f"show_past_{book['id']}"] = True
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Error: {ex}")

                    # Completion form (auto-triggered)
                    if st.session_state.get(f"complete_{book['id']}", False):
                        st.markdown("---")
                        st.markdown("### 🏁 Book Complete — Final Review")
                        f_rating  = st.slider("Overall rating (1–10)", 1, 10, 8, key=f"frating_{book['id']}")
                        f_review  = st.text_area("How was the book overall?", key=f"freview_{book['id']}", height=80)
                        f_rec     = st.radio("Would you recommend it?", ["Yes", "No"], key=f"frec_{book['id']}")
                        f_takeaway = st.text_input("Key takeaway", key=f"ftakeaway_{book['id']}")

                        if st.button("✅ Mark as Finished", key=f"finish_{book['id']}"):
                            try:
                                supabase.table("books").update({
                                    "status": "finished",
                                    "overall_rating": f_rating,
                                    "review": f_review.strip(),
                                    "recommend": f_rec == "Yes",
                                    "key_takeaway": f_takeaway.strip(),
                                    "date_finished": str(date.today())
                                }).eq("id", book["id"]).execute()
                                st.session_state[f"complete_{book['id']}"] = False
                                st.success("Book moved to finished shelf!")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Error: {ex}")

                st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ============================================================
    # TAB 2 — FINISHED SHELF
    # ============================================================
    with tab2:
        if not finished_books:
            st.info("No finished books yet. Keep reading!")
        else:
            rating_filter = st.selectbox("Filter by rating", ["All", "⭐ 8–10", "👍 5–7", "👎 below 5"], label_visibility="collapsed")
            def _keep(b):
                r = b.get("overall_rating")
                if rating_filter == "All" or r is None:
                    return rating_filter == "All"
                if rating_filter.startswith("⭐"):
                    return r >= 8
                if rating_filter.startswith("👍"):
                    return 5 <= r <= 7
                return r < 5
            shelf = [b for b in finished_books if _keep(b)]
            if not shelf:
                st.info("No books match this rating filter.")
            for book in shelf:
                rec_badge = '<span class="badge badge-green">👍 Recommended</span>' if book.get("recommend") else '<span class="badge badge-grey">👎 Not Recommended</span>'
                genre_badge = f'<span class="badge badge-purple">{book["genre"]}</span>' if book.get("genre") else ""
                rating = book.get("overall_rating", "—")
                rating_color = "#4ade80" if (rating != "—" and rating >= 8) else "#facc15" if (rating != "—" and rating >= 5) else "#f87171"

                st.markdown(f"""
                <div class="card">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <span style="font-size:1rem;font-weight:800;color:#fff;">{book['title']}</span>
                            <span style="font-size:0.8rem;color:#666;margin-left:0.8rem;font-family:'JetBrains Mono',monospace;">{book.get('author','')}</span>
                        </div>
                        <div style="display:flex;gap:0.5rem;align-items:center;">
                            <span style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;font-weight:800;color:{rating_color};">{rating}/10</span>
                            {genre_badge}
                            {rec_badge}
                        </div>
                    </div>
                    <div style="margin-top:0.6rem;color:#aaa;font-size:0.85rem;">{book.get('review','')}</div>
                    <div style="margin-top:0.4rem;font-size:0.8rem;color:#555;font-family:'JetBrains Mono',monospace;">
                        💡 {book.get('key_takeaway','—')} &nbsp;·&nbsp; finished {book.get('date_finished','—')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ============================================================
    # TAB 3 — ADD NEW BOOK
    # ============================================================
    with tab3:
        st.markdown("#### Add a New Book")
        b_title  = st.text_input("Book Title", placeholder="e.g. Limitless")
        b_author = st.text_input("Author", placeholder="e.g. Jim Kwik")
        genres = ["Fiction", "Non-fiction", "Fantasy", "Sci-Fi", "Mystery", "Classic", "Biography",
                  "Self-Development", "History", "Philosophy", "Psychology", "Business", "Poetry", "Manga", "Other"]
        b_genre  = st.selectbox("Genre", genres)
        b_pages  = st.number_input("Total Pages", min_value=1, step=1, value=300)

        if st.button("➕ Add Book", type="primary"):
            if not b_title.strip():
                st.error("Please enter a title.")
            else:
                try:
                    supabase.table("books").insert({
                        "title": b_title.strip(),
                        "author": b_author.strip(),
                        "total_pages": b_pages,
                        "genre": b_genre,
                        "status": "reading",
                        "date_started": str(date.today())
                    }).execute()
                    st.success(f"'{b_title}' added to your reading list!")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")

elif page == "🚨  Life Event":
    st.markdown('<div class="section-header">🚨 Life Event Diary</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">record moments that actually mattered</div>', unsafe_allow_html=True)

    if "life_event_view" not in st.session_state:
        st.session_state["life_event_view"] = "➕ Log New Event"

    view = st.radio("Life Event View", ["📋 Past Events", "➕ Log New Event"],
                    index=0 if st.session_state["life_event_view"] == "📋 Past Events" else 1,
                    horizontal=True, label_visibility="collapsed")
    st.session_state["life_event_view"] = view
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ============================================================
    # PAST EVENTS
    # ============================================================
    if view == "📋 Past Events":
        event_types = ["All", "personal event", "milestone", "realization", "decision", "conversation", "travel", "accident", "movie", "other"]
        filter_type = st.selectbox("Filter by type", event_types, label_visibility="collapsed")

        try:
            query = supabase.table("life_events").select("*").order("event_date", desc=True)
            if filter_type != "All":
                query = query.eq("event_type", filter_type)
            events = query.execute().data or []
        except:
            events = []

        if not events:
            st.info("No life events logged yet.")
        else:
            for e in events:
                sig = e.get("significance_score", 1)
                if sig >= 5:
                    border_color = "#fbbf24"
                elif sig >= 4:
                    border_color = "#fb923c"
                elif sig >= 3:
                    border_color = "#facc15"
                else:
                    border_color = "#444"

                type_colors = {
                    "realization": "badge-green",
                    "personal event": "badge-blue",
                    "milestone": "badge-gold",
                    "decision": "badge-purple",
                    "conversation": "badge-blue",
                    "travel": "badge-yellow",
                    "accident": "badge-red",
                    "movie": "badge-grey",
                    "other": "badge-grey"
                }
                type_badge = f'<span class="badge {type_colors.get(e["event_type"], "badge-grey")}">{e["event_type"]}</span>'

                st.markdown(f"""
                <div class="card" style="border-left: 3px solid {border_color}; margin-bottom:1rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                        <span style="font-size:1rem;font-weight:800;color:#fff;">{e['event_title']}</span>
                        <div style="display:flex;gap:0.5rem;align-items:center;">
                            {type_badge}
                            {significance_badge(sig)}
                        </div>
                    </div>
                    <div style="color:#ccc;font-size:0.9rem;margin-bottom:0.5rem;">{e.get('event_description','')}</div>
                    <div style="color:#888;font-size:0.85rem;font-style:italic;">💭 {e.get('emotional_impact','')}</div>
                    {f'<div style="color:#888;font-size:0.85rem;margin-top:0.3rem;">👥 <b>People:</b> ' + e["people_involved"] + '</div>' if e.get("people_involved") else ''}
                    {f'<div style="color:#888;font-size:0.85rem;margin-top:0.3rem;">🔁 <b>Would change:</b> ' + e["would_change"] + '</div>' if e.get("would_change") else ''}
                    <div style="margin-top:0.5rem;font-size:0.75rem;color:#555;font-family:'JetBrains Mono',monospace;">{e.get('event_date','')}</div>
                </div>
                """, unsafe_allow_html=True)
                col_edit, col_del = st.columns([1, 1])
                with col_edit:
                    if st.button("✏️ Edit", key=f"edit_event_{e['id']}"):
                        st.session_state["editing_event"] = e
                        st.session_state["life_event_view"] = "➕ Log New Event"
                        st.rerun()
                with col_del:
                    if st.button("🗑️ Delete", key=f"del_event_{e['id']}"):
                        st.session_state[f"confirm_del_{e['id']}"] = True
                        st.rerun()
                if st.session_state.get(f"confirm_del_{e['id']}", False):
                    st.warning(f"Delete **{e['event_title']}**? This cannot be undone.")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes, delete", key=f"yes_del_{e['id']}"):
                            supabase.table("life_events").delete().eq("id", e["id"]).execute()
                            st.session_state[f"confirm_del_{e['id']}"] = False
                            st.rerun()
                    with c2:
                        if st.button("Cancel", key=f"cancel_del_{e['id']}"):
                            st.session_state[f"confirm_del_{e['id']}"] = False
                            st.rerun()

    # ============================================================
    # LOG NEW EVENT
    # ============================================================
    else:
        editing = st.session_state.get("editing_event", None)
        st.markdown(f"#### {'✏️ Editing Event' if editing else 'What happened?'}")

        e_types_list = ["personal event", "milestone", "realization", "decision", "conversation", "travel", "accident", "other"]
        e_title  = st.text_input("Event Title", value=editing["event_title"] if editing else "", placeholder="e.g. Got accepted...")
        e_type   = st.selectbox("Event Type", e_types_list, index=e_types_list.index(editing["event_type"]) if editing and editing.get("event_type") in e_types_list else 0)
        e_desc   = st.text_area("Description", value=editing.get("event_description","") if editing else "", height=100)
        e_impact = st.text_area("Emotional Impact", value=editing.get("emotional_impact","") if editing else "", height=80)
        e_people = st.text_input("People involved (optional)", value=editing.get("people_involved","") or "" if editing else "", placeholder="Who was part of this moment?")
        e_change = st.text_area("Would you change anything? (optional)", value=editing.get("would_change","") or "" if editing else "", height=70, placeholder="If you could redo it — what, if anything, would you do differently?")

        col1, col2 = st.columns(2)
        with col1:
            e_sig = st.slider("Significance (1–5)", 1, 5, editing["significance_score"] if editing else 3)
            st.markdown(significance_badge(e_sig), unsafe_allow_html=True)
        with col2:
            from datetime import datetime
            default_date = datetime.strptime(editing["event_date"], "%Y-%m-%d").date() if editing else date.today()
            e_date = st.date_input("Date", value=default_date)

        if st.button("💾 Update Event" if editing else "💾 Save Event", type="primary"):
            if not e_title.strip():
                st.error("Please enter an event title.")
            else:
                try:
                    record = {
                        "event_title": e_title.strip(),
                        "event_type": e_type,
                        "event_description": e_desc.strip(),
                        "emotional_impact": e_impact.strip(),
                        "people_involved": e_people.strip(),
                        "would_change": e_change.strip(),
                        "significance_score": e_sig,
                        "event_date": str(e_date)
                    }
                    if editing:
                        supabase.table("life_events").update(record).eq("id", editing["id"]).execute()
                        st.success("✅ Event updated.")
                        st.session_state["editing_event"] = None
                    else:
                        supabase.table("life_events").insert(record).execute()
                        st.success("✅ Event saved.")
                    st.session_state["life_event_view"] = "📋 Past Events"
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")

        if editing and st.button("Cancel"):
            st.session_state["editing_event"] = None
            st.rerun()
                
elif page == "🛍️  Purchase Tracker":
    st.markdown('<div class="section-header">🛍️ Purchase Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">track what you buy · review what it was worth</div>', unsafe_allow_html=True)

    if "purchase_view" not in st.session_state:
        st.session_state["purchase_view"] = "➕ Add Purchase"
    if "editing_purchase" not in st.session_state:
        st.session_state["editing_purchase"] = None

    view = st.radio("Purchase View", ["🔴 Pending Review", "📋 All Purchases", "➕ Add Purchase"],
                    index=["🔴 Pending Review", "📋 All Purchases", "➕ Add Purchase"].index(st.session_state["purchase_view"]),
                    horizontal=True, label_visibility="collapsed")
    st.session_state["purchase_view"] = view
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ============================================================
    # PENDING REVIEW
    # ============================================================
    if view == "🔴 Pending Review":
        try:
            all_purchases = supabase.table("purchases").select("*").eq("phase2_completed", False).order("purchase_date", desc=True).execute().data or []
            pending = [p for p in all_purchases if p.get("review_due_date") and p["review_due_date"] <= str(date.today())]
        except:
            pending = []

        if not pending:
            st.success("✅ No purchases pending review.")
        else:
            st.markdown(f'<div class="section-sub">🔴 {len(pending)} purchase(s) waiting for your honest review</div>', unsafe_allow_html=True)
            for p in pending:
                days_overdue = (date.today() - date.fromisoformat(p["review_due_date"])).days
                currency = p.get("currency", "UZS")
                st.markdown(f"""
                <div class="card" style="border-left: 3px solid #f87171;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                        <span style="font-weight:800;color:#fff;font-size:1rem;">{p['item_name']}</span>
                        <div style="display:flex;gap:0.5rem;">
                            <span class="badge badge-red">🔴 {days_overdue}d overdue</span>
                            <span class="badge badge-grey">{p.get('category','')}</span>
                        </div>
                    </div>
                    <div style="font-size:0.85rem;color:#888;font-family:'JetBrains Mono',monospace;">
                        {p.get('amount',0):,.0f} {currency} · bought {p.get('purchase_date','')} · expected: {p.get('expected_value','')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"📝 Review '{p['item_name']}'"):
                    r_usage      = st.selectbox("How often did you use it?", ["never", "once", "few times", "regularly", "daily"], key=f"usage_{p['id']}")
                    r_actual     = st.text_input("Actual use case", key=f"actual_{p['id']}", placeholder="What did you actually use it for?")
                    r_sat        = st.slider("Satisfaction (1–5)", 1, 5, 3, key=f"sat_{p['id']}")
                    r_regret     = st.slider("Regret level (1–5)", 1, 5, 2, key=f"regret_{p['id']}")
                    r_worth      = st.radio("Worth it?", ["Yes", "No"], key=f"worth_{p['id']}", horizontal=True)
                    r_reflection = st.text_area("Reflection", key=f"reflection_{p['id']}", height=80, placeholder="What did you learn from this purchase?")

                    if st.button("✅ Submit Review", key=f"review_{p['id']}", type="primary"):
                        try:
                            supabase.table("purchases").update({
                                "usage_frequency": r_usage,
                                "actual_use_case": r_actual.strip(),
                                "satisfaction_level": r_sat,
                                "regret_level": r_regret,
                                "worth_it": r_worth == "Yes",
                                "review_reflection": r_reflection.strip(),
                                "phase2_completed": True
                            }).eq("id", p["id"]).execute()
                            st.success("✅ Review saved.")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error: {ex}")

    # ============================================================
    # ALL PURCHASES
    # ============================================================
    elif view == "📋 All Purchases":
        try:
            all_purchases = supabase.table("purchases").select("*").order("purchase_date", desc=True).execute().data or []
        except:
            all_purchases = []

        if not all_purchases:
            st.info("No purchases logged yet.")
        else:
            # ---- Monthly spending summary — one block PER CURRENCY ----
            today_d = date.today()
            this_month = today_d.strftime("%Y-%m")
            last_month_d = (today_d.replace(day=1) - timedelta(days=1))
            last_month = last_month_d.strftime("%Y-%m")

            def _month_of(p):
                return (p.get("purchase_date") or "")[:7]

            totals_this, totals_last = {}, {}
            for p in all_purchases:
                cur = p.get("currency", "UZS") or "UZS"
                amt = p.get("amount", 0) or 0
                if _month_of(p) == this_month:
                    totals_this[cur] = totals_this.get(cur, 0) + amt
                elif _month_of(p) == last_month:
                    totals_last[cur] = totals_last.get(cur, 0) + amt

            summary_currencies = sorted(set(totals_this) | set(totals_last))
            if summary_currencies:
                st.markdown('<div style="font-size:0.75rem;color:#555;font-family:\'JetBrains Mono\',monospace;margin-bottom:0.6rem;letter-spacing:1px;">MONTHLY SPENDING — ' + today_d.strftime("%B %Y").upper() + '</div>', unsafe_allow_html=True)
                cur_cols = st.columns(len(summary_currencies))
                for i, cur in enumerate(summary_currencies):
                    t_now = totals_this.get(cur, 0)
                    t_prev = totals_last.get(cur, 0)
                    diff = t_now - t_prev
                    if diff > 0:
                        arrow = f'<span style="color:#F87171;font-weight:800;">▲ +{diff:,.0f}</span>'
                    elif diff < 0:
                        arrow = f'<span style="color:#4ADE80;font-weight:800;">▼ {diff:,.0f}</span>'
                    else:
                        arrow = '<span style="color:#9ca3af;">— 0</span>'
                    with cur_cols[i]:
                        st.markdown(card_html(f"""
                            <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#3a3a6a;letter-spacing:1px;">{cur}</div>
                            <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:800;color:#e8e0ff;margin:0.3rem 0;">{t_now:,.0f}</div>
                            <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#888;">last month: {t_prev:,.0f}</div>
                            <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;margin-top:0.3rem;">{arrow} vs last month</div>
                        """), unsafe_allow_html=True)

            # ---- Category breakdown — current month, per currency ----
            cat_totals = {}
            for p in all_purchases:
                if _month_of(p) == this_month:
                    cur = p.get("currency", "UZS") or "UZS"
                    cat = p.get("category", "other") or "other"
                    cat_totals.setdefault(cur, {})
                    cat_totals[cur][cat] = cat_totals[cur].get(cat, 0) + (p.get("amount", 0) or 0)
            for cur in sorted(cat_totals):
                items = sorted(cat_totals[cur].items(), key=lambda kv: kv[1], reverse=True)
                bars = [(cat, val, f"{val:,.0f} {cur}") for cat, val in items if val > 0]
                if bars:
                    st.markdown(hbar_block(f"SPEND BY CATEGORY · {this_month} · {cur}", bars), unsafe_allow_html=True)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            for p in all_purchases:
                currency = p.get("currency", "UZS")
                if not p.get("phase2_completed"):
                    border = "#444"
                    status_badge = '<span class="badge badge-grey">⏳ Pending Review</span>'
                elif p.get("worth_it"):
                    border = "#4ade80"
                    status_badge = '<span class="badge badge-green">✅ Worth It</span>'
                else:
                    border = "#f87171"
                    status_badge = '<span class="badge badge-red">❌ Not Worth It</span>'

                st.markdown(f"""
                <div class="card" style="border-left: 3px solid {border};">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                        <span style="font-weight:800;color:#fff;">{p['item_name']}</span>
                        <div style="display:flex;gap:0.5rem;">
                            {status_badge}
                            <span class="badge badge-grey">{p.get('category','')}</span>
                        </div>
                    </div>
                    <div style="font-size:0.85rem;color:#888;font-family:'JetBrains Mono',monospace;">
                        {p.get('amount',0):,.0f} {currency} · {p.get('purchase_date','')} · {p.get('emotional_state_post_purchase','')}
                    </div>
                    {f'<div style="margin-top:0.4rem;font-size:0.8rem;color:#666;">💭 {p["review_reflection"]}</div>' if p.get("review_reflection") else ''}
                </div>
                """, unsafe_allow_html=True)

                col_edit, col_del = st.columns([1, 1])
                with col_edit:
                    if st.button("✏️ Edit", key=f"edit_purchase_{p['id']}"):
                        st.session_state["editing_purchase"] = dict(p)
                        st.session_state["purchase_view"] = "➕ Add Purchase"
                        st.rerun()
                with col_del:
                    if st.button("🗑️ Delete", key=f"del_purchase_{p['id']}"):
                        st.session_state[f"confirm_del_p_{p['id']}"] = True
                        st.rerun()
                if st.session_state.get(f"confirm_del_p_{p['id']}", False):
                    st.warning(f"Delete **{p['item_name']}**? This cannot be undone.")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes, delete", key=f"yes_del_p_{p['id']}"):
                            supabase.table("purchases").delete().eq("id", p["id"]).execute()
                            st.session_state[f"confirm_del_p_{p['id']}"] = False
                            st.rerun()
                    with c2:
                        if st.button("Cancel", key=f"cancel_del_p_{p['id']}"):
                            st.session_state[f"confirm_del_p_{p['id']}"] = False
                            st.rerun()

    # ============================================================
    # ADD / EDIT PURCHASE
    # ============================================================
    else:
        editing_p = st.session_state.get("editing_purchase", None)
        editing_p_id = editing_p["id"] if editing_p else None
        st.markdown(f"#### {'✏️ Editing Purchase' if editing_p else 'What did you buy?'}")

        with st.form("purchase_form"):
            p_name     = st.text_input("Item Name", value=editing_p["item_name"] if editing_p else "", placeholder="e.g. AirPods, lunch, new jacket...")
            categories = ["food", "clothing", "tech", "entertainment", "transport", "other"]
            p_category = st.selectbox("Category", categories, index=categories.index(editing_p["category"]) if editing_p and editing_p.get("category") in categories else 0)
            currencies = ["UZS", "USD", "EUR", "RUB", "GBP", "JPY"]
            col_amt, col_cur = st.columns([3, 1])
            with col_amt:
                p_amount = st.number_input("Amount", min_value=0.0, step=1000.0, value=float(editing_p["amount"]) if editing_p and editing_p.get("amount") else 0.0)
            with col_cur:
                cur_index = currencies.index(editing_p.get("currency", "UZS")) if editing_p and editing_p.get("currency") in currencies else 0
                p_currency = st.selectbox("Currency", currencies, index=cur_index)
            p_reason   = st.text_input("Reason for buying", value=editing_p.get("reason_for_purchase", "") if editing_p else "", placeholder="Why did you buy this?")
            emotions   = ["planned", "impulse", "influenced", "necessity"]
            p_emotion  = st.selectbox("Emotional state at purchase", emotions, index=emotions.index(editing_p["emotional_state_post_purchase"]) if editing_p and editing_p.get("emotional_state_post_purchase") in emotions else 0)
            p_expected = st.text_input("Expected value", value=editing_p.get("expected_value", "") if editing_p else "", placeholder="What do you expect to get from this?")
            from datetime import datetime, timedelta
            default_date = datetime.strptime(editing_p["purchase_date"], "%Y-%m-%d").date() if editing_p and editing_p.get("purchase_date") else date.today()
            p_date     = st.date_input("Purchase Date", value=default_date)
            submitted  = st.form_submit_button("💾 Update Purchase" if editing_p else "💾 Log Purchase")

        if submitted:
            if not p_name.strip():
                st.error("Please enter an item name.")
            else:
                try:
                    from datetime import timedelta
                    record = {
                        "item_name": p_name.strip(),
                        "category": p_category,
                        "amount": p_amount,
                        "currency": p_currency,
                        "reason_for_purchase": p_reason.strip(),
                        "emotional_state_post_purchase": p_emotion,
                        "expected_value": p_expected.strip(),
                        "purchase_date": str(p_date),
                        "review_due_date": str(p_date + timedelta(days=14)),
                    }
                    if editing_p_id:
                        supabase.table("purchases").update(record).eq("id", editing_p_id).execute()
                        st.success("✅ Purchase updated.")
                        st.session_state["editing_purchase"] = None
                    else:
                        record["phase2_completed"] = False
                        supabase.table("purchases").insert(record).execute()
                        st.success(f"✅ Purchase logged. Review set for {p_date + timedelta(days=14)}.")
                    st.session_state["purchase_view"] = "📋 All Purchases"
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")

        if editing_p_id and st.button("Cancel", key="cancel_purchase_form"):
            st.session_state["editing_purchase"] = None
            st.session_state["purchase_view"] = "📋 All Purchases"
            st.rerun()
elif page == "🎯  Goals":
    st.markdown('<div class="section-header">🎯 Goals</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">A goal is a dream with a deadline</div>', unsafe_allow_html=True)

    if "goal_view" not in st.session_state:
        st.session_state["goal_view"] = "📋 Goals"
    if "goal_radio_counter" not in st.session_state:
        st.session_state["goal_radio_counter"] = 0

    goal_options = ["📋 Goals", "➕ Add Goal"]
    view = st.radio("Goal View", goal_options,
                    index=goal_options.index(st.session_state["goal_view"]),
                    horizontal=True, label_visibility="collapsed",
                    key=f"goal_radio_{st.session_state['goal_radio_counter']}")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    GOAL_CATEGORIES = ["Personal Growth", "Career", "Academic", "Health & Fitness", "Skills",
                       "Creative", "Financial", "Relationships", "Other"]

    # ============================================================
    # GOALS LIST
    # ============================================================
    if view == "📋 Goals":
        try:
            goals = supabase.table("goals").select("*").order("created_at", desc=False).execute().data or []
        except:
            goals = []

        active_goals    = [g for g in goals if g["status"] == "active"]
        paused_goals    = [g for g in goals if g["status"] == "paused"]
        completed_goals = [g for g in goals if g["status"] == "completed"]

        if not goals:
            st.info("No goals yet. Add one here, or activate a wish from the Wish List.")
        else:
            for g in active_goals + paused_goals + completed_goals:
                try:
                    sessions = supabase.table("goal_sessions").select("*").eq("goal_id", g["id"]).order("session_date", desc=False).execute().data or []
                except:
                    sessions = []

                total_hours = sum(s.get("duration_hours", 0) or 0 for s in sessions)
                avg_enjoyment = (sum(s.get("enjoyment_score", 0) or 0 for s in sessions) / len(sessions)) if sessions else 0

                # deadline badge
                deadline_badge = ""
                if g.get("target_date"):
                    try:
                        target_d = datetime.strptime(g["target_date"], "%Y-%m-%d").date()
                        days_left = (target_d - date.today()).days
                        if g["status"] == "completed":
                            deadline_badge = f'<span class="badge badge-grey">🏁 {g["target_date"]}</span>'
                        elif days_left < 0:
                            deadline_badge = f'<span class="badge badge-red">⏰ {abs(days_left)}d overdue</span>'
                        elif days_left <= 7:
                            deadline_badge = f'<span class="badge badge-yellow">⏳ {days_left}d left</span>'
                        else:
                            deadline_badge = f'<span class="badge badge-blue">📅 {days_left}d left</span>'
                    except:
                        pass

                cat_badge = f'<span class="badge badge-purple">{g["category"]}</span>' if g.get("category") else ""
                prio_map = {"high": "badge-red", "medium": "badge-yellow", "low": "badge-blue"}
                prio_badge = f'<span class="badge {prio_map.get(g.get("priority",""), "badge-grey")}">{g["priority"]} priority</span>' if g.get("priority") else ""

                why_html = f'<div style="margin-top:0.5rem;color:#9a90cc;font-size:0.85rem;font-style:italic;">💜 Why: {g["why"]}</div>' if g.get("why") else ""
                notes_html = f'<div style="margin-top:0.4rem;color:#888;font-size:0.85rem;">🗒 {g["progress_notes"]}</div>' if g.get("progress_notes") else ""

                st.markdown(card_html(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;flex-wrap:wrap;gap:0.4rem;">
                        <span style="font-size:1.1rem;font-weight:800;color:#fff;">{g['goal_title']}</span>
                        <div style="display:flex;gap:0.5rem;align-items:center;flex-wrap:wrap;">
                            {cat_badge}
                            {prio_badge}
                            {deadline_badge}
                            {goal_status_badge(g['status'])}
                        </div>
                    </div>
                    <div style="font-size:0.85rem;color:#888;font-family:'JetBrains Mono',monospace;">
                        {len(sessions)} sessions · {total_hours:.1f} hrs total · avg enjoyment {avg_enjoyment:.1f}/5
                    </div>
                    {why_html}
                    {notes_html}
                """), unsafe_allow_html=True)

                # Past sessions
                if sessions:
                    with st.expander(f"🗂 {len(sessions)} past sessions"):
                        for s in reversed(sessions):
                            stars = '★' * (s.get('enjoyment_score') or 0) + '☆' * (5 - (s.get('enjoyment_score') or 0))
                            st.markdown(card_html(f"""
                                <div style="display:flex;justify-content:space-between;">
                                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#888;">{s['session_date']}</span>
                                    <span class="badge badge-blue">{s.get('duration_hours',0)} hrs</span>
                                    <span class="badge badge-yellow">{stars}</span>
                                </div>
                                <div style="margin-top:0.4rem;color:#ccc;font-size:0.85rem;"><b>{s.get('activity_description','')}</b></div>
                                <div style="margin-top:0.2rem;color:#888;font-size:0.85rem;">{s.get('learning_summary','')}</div>
                            """, style="margin-bottom:0.4rem;"), unsafe_allow_html=True)

                # Log new session (only if active)
                if g["status"] == "active":
                    with st.expander(f"➕ Log a session for '{g['goal_title']}'"):
                        s_date     = st.date_input("Session Date", value=date.today(), key=f"sdate_{g['id']}")
                        s_duration = st.number_input("Duration (hours)", min_value=0.0, step=0.5, value=1.0, key=f"sdur_{g['id']}")
                        s_activity = st.text_input("What did you do?", key=f"sact_{g['id']}", placeholder="Describe the activity...")
                        s_learning = st.text_area("What did you learn?", key=f"slearn_{g['id']}", height=80)
                        s_enjoy    = st.slider("Enjoyment (1–5)", 1, 5, 3, key=f"senjoy_{g['id']}")

                        if st.button("💾 Save Session", key=f"save_goal_session_{g['id']}", type="primary"):
                            try:
                                supabase.table("goal_sessions").insert({
                                    "goal_id": g["id"],
                                    "session_date": str(s_date),
                                    "duration_hours": s_duration,
                                    "activity_description": s_activity.strip(),
                                    "learning_summary": s_learning.strip(),
                                    "enjoyment_score": s_enjoy
                                }).execute()
                                st.success("✅ Session logged.")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Error: {ex}")

                # Status controls
                if g["status"] == "active":
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("⏸️ Pause", key=f"pause_{g['id']}"):
                            supabase.table("goals").update({"status": "paused"}).eq("id", g["id"]).execute()
                            st.rerun()
                    with col2:
                        if st.button("🏁 End → Outcome", key=f"end_{g['id']}", type="primary"):
                            st.session_state["outcome_goal"] = dict(g)
                            st.session_state["current_page_override"] = "🏆  Outcomes"
                            st.session_state["nav_override_counter"] = st.session_state.get("nav_override_counter", 0) + 1
                            st.rerun()
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_goal_{g['id']}"):
                            st.session_state[f"confirm_del_g_{g['id']}"] = True
                            st.rerun()
                elif g["status"] == "paused":
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("▶️ Resume Goal", key=f"resume_{g['id']}"):
                            supabase.table("goals").update({"status": "active"}).eq("id", g["id"]).execute()
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_goal_{g['id']}"):
                            st.session_state[f"confirm_del_g_{g['id']}"] = True
                            st.rerun()
                else:
                    if st.button("🗑️ Delete", key=f"del_goal_{g['id']}"):
                        st.session_state[f"confirm_del_g_{g['id']}"] = True
                        st.rerun()

                if st.session_state.get(f"confirm_del_g_{g['id']}", False):
                    st.warning(f"Delete **{g['goal_title']}** and all its sessions? This cannot be undone.")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes, delete", key=f"yes_del_g_{g['id']}"):
                            try:
                                supabase.table("goal_sessions").delete().eq("goal_id", g["id"]).execute()
                                supabase.table("goals").delete().eq("id", g["id"]).execute()
                            except Exception as ex:
                                st.error(f"Error: {ex}")
                            st.session_state[f"confirm_del_g_{g['id']}"] = False
                            st.rerun()
                    with c2:
                        if st.button("Cancel", key=f"cancel_del_g_{g['id']}"):
                            st.session_state[f"confirm_del_g_{g['id']}"] = False
                            st.rerun()

                st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ============================================================
    # ADD GOAL
    # ============================================================
    else:
        st.markdown("#### What are you committing to?")
        with st.form("add_goal_form"):
            g_title = st.text_input("Goal Title", placeholder="e.g. Pass JLPT N2, Ship the workout app...")
            g_cat   = st.selectbox("Category", GOAL_CATEGORIES)
            g_date  = st.date_input("Target Date", value=date.today() + timedelta(days=30))
            g_why   = st.text_area("Why (motivation)", height=80, placeholder="Why does this matter to you?")
            g_notes = st.text_area("Progress Notes (optional)", height=70, placeholder="Where are you starting from?")
            submitted_goal = st.form_submit_button("💾 Add Goal", type="primary")

        if submitted_goal:
            if not g_title.strip():
                st.error("Please enter a goal title.")
            else:
                try:
                    supabase.table("goals").insert({
                        "goal_title": g_title.strip(),
                        "category": g_cat,
                        "target_date": str(g_date),
                        "why": g_why.strip(),
                        "progress_notes": g_notes.strip(),
                        "status": "active"
                    }).execute()
                    st.success(f"🎯 '{g_title}' is now an active goal!")
                    st.session_state["goal_view"] = "📋 Goals"
                    st.session_state["goal_radio_counter"] += 1
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")

elif page == "💫  Wish List":
    st.markdown('<div class="section-header">💫 Wish List</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">no deadlines · no pressure · just things you want</div>', unsafe_allow_html=True)

    if "wish_view" not in st.session_state:
        st.session_state["wish_view"] = "💫 Passive Wishes"
    if "editing_wish" not in st.session_state:
        st.session_state["editing_wish"] = None
    if "wish_radio_counter" not in st.session_state:
        st.session_state["wish_radio_counter"] = 0

    WISH_CATEGORIES = ["Personal Growth", "Travel", "Career", "Skills", "Health & Fitness",
                       "Relationships", "Creative", "Financial", "Education", "Long-term Dream", "Other"]

    options = ["💫 Passive Wishes", "➕ Add Wish"]
    current_index = options.index(st.session_state["wish_view"])
    view = st.radio("Wish View", options, index=current_index,
                    horizontal=True, label_visibility="collapsed",
                    key=f"wish_radio_{st.session_state['wish_radio_counter']}")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ============================================================
    # PASSIVE WISHES
    # ============================================================
    if view == "💫 Passive Wishes":
        try:
            wishes = supabase.table("wishes").select("*").eq("status", "passive").order("created_at", desc=True).execute().data or []
        except:
            wishes = []

        if not wishes:
            st.info("No wishes yet. Add anything you want to pursue someday.")
        else:
            prio_filter = st.selectbox("Filter by priority", ["All", "high", "medium", "low"], label_visibility="collapsed")
            shown = [w for w in wishes if prio_filter == "All" or (w.get("priority") or "medium") == prio_filter]
            if not shown:
                st.info("No wishes match this priority.")
            prio_map = {"high": "badge-red", "medium": "badge-yellow", "low": "badge-blue"}
            for w in shown:
                prio = w.get("priority") or "medium"
                prio_badge = f'<span class="badge {prio_map.get(prio, "badge-grey")}">{prio}</span>'
                cat_badge = f'<span class="badge badge-purple">{w["category"]}</span>' if w.get("category") else ""
                days_ago_txt = w.get("date_added", "")
                try:
                    d_added = datetime.strptime(w["date_added"], "%Y-%m-%d").date()
                    n = (date.today() - d_added).days
                    days_ago_txt = "added today" if n == 0 else f"added {n} day{'s' if n != 1 else ''} ago"
                except:
                    days_ago_txt = f"added {days_ago_txt}"
                st.markdown(card_html(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem;flex-wrap:wrap;gap:0.4rem;">
                        <span style="font-size:1rem;font-weight:800;color:#fff;">✦ {w['wish_title']}</span>
                        <div style="display:flex;gap:0.5rem;align-items:center;">{cat_badge}{prio_badge}</div>
                    </div>
                    <div style="color:#aaa;font-size:0.9rem;">{w.get('description','')}</div>
                    <div style="margin-top:0.4rem;font-size:0.75rem;color:#555;font-family:'JetBrains Mono',monospace;">{days_ago_txt}</div>
                """), unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("🎯 Activate as Goal", key=f"activate_{w['id']}", type="primary"):
                        try:
                            supabase.table("wishes").update({"status": "activated"}).eq("id", w["id"]).execute()
                            goal_record = {
                                "goal_title": w["wish_title"],
                                "linked_wish_id": w["id"],
                                "status": "active",
                                "category": w.get("category"),
                                "priority": w.get("priority") or "medium",
                                "why": w.get("description") or None,
                            }
                            try:
                                supabase.table("goals").insert(goal_record).execute()
                            except:
                                # fallback if optional columns (e.g. priority) don't exist yet
                                supabase.table("goals").insert({
                                    "goal_title": w["wish_title"],
                                    "linked_wish_id": w["id"],
                                    "status": "active",
                                    "category": w.get("category"),
                                }).execute()
                            st.success(f"'{w['wish_title']}' is now an active goal!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error: {ex}")
                with col2:
                    if st.button("✏️ Edit", key=f"edit_wish_{w['id']}"):
                        st.session_state["editing_wish"] = dict(w)
                        st.session_state["wish_view"] = "➕ Add Wish"
                        st.session_state["wish_radio_counter"] += 1
                        st.rerun()
                with col3:
                    if st.button("🗑️ Delete", key=f"del_wish_{w['id']}"):
                        st.session_state[f"confirm_del_w_{w['id']}"] = True
                        st.rerun()

                if st.session_state.get(f"confirm_del_w_{w['id']}", False):
                    st.warning(f"Delete **{w['wish_title']}**? This cannot be undone.")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes, delete", key=f"yes_del_w_{w['id']}"):
                            supabase.table("wishes").delete().eq("id", w["id"]).execute()
                            st.session_state[f"confirm_del_w_{w['id']}"] = False
                            st.rerun()
                    with c2:
                        if st.button("Cancel", key=f"cancel_del_w_{w['id']}"):
                            st.session_state[f"confirm_del_w_{w['id']}"] = False
                            st.rerun()

                st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ============================================================
    # ADD / EDIT WISH
    # ============================================================
    else:
        editing_w = st.session_state.get("editing_wish", None)
        editing_w_id = editing_w["id"] if editing_w else None
        st.markdown(f"#### {'✏️ Editing Wish' if editing_w else 'What do you want?'}")

        with st.form("wish_form"):
            w_title = st.text_input("Wish Title", value=editing_w["wish_title"] if editing_w else "", placeholder="e.g. Learn Japanese, Visit Japan, Build a startup...")
            w_desc  = st.text_area("Description (optional)", value=editing_w.get("description","") if editing_w else "", height=100, placeholder="Any details, context, or why this matters to you...")
            col_cat, col_prio = st.columns(2)
            with col_cat:
                w_cat = st.selectbox("Category", WISH_CATEGORIES,
                                     index=WISH_CATEGORIES.index(editing_w["category"]) if editing_w and editing_w.get("category") in WISH_CATEGORIES else 0)
            with col_prio:
                prios = ["high", "medium", "low"]
                w_prio = st.selectbox("Priority", prios,
                                      index=prios.index(editing_w["priority"]) if editing_w and editing_w.get("priority") in prios else 1)
            submitted = st.form_submit_button("💾 Update Wish" if editing_w else "💾 Add Wish")

        if submitted:
            if not w_title.strip():
                st.error("Please enter a wish title.")
            else:
                try:
                    record = {
                        "wish_title": w_title.strip(),
                        "description": w_desc.strip(),
                        "category": w_cat,
                        "priority": w_prio,
                    }
                    if editing_w_id:
                        supabase.table("wishes").update(record).eq("id", editing_w_id).execute()
                        st.success("✅ Wish updated.")
                        st.session_state["editing_wish"] = None
                    else:
                        record["status"] = "passive"
                        record["date_added"] = str(date.today())
                        supabase.table("wishes").insert(record).execute()
                        st.success("✅ Wish added to your list.")
                    st.session_state["wish_view"] = "💫 Passive Wishes"
                    st.session_state["wish_radio_counter"] += 1
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")

        if editing_w_id and st.button("Cancel", key="cancel_wish_form"):
            st.session_state["editing_wish"] = None
            st.session_state["wish_view"] = "💫 Passive Wishes"
            st.session_state["wish_radio_counter"] += 1
            st.rerun()

elif page == "🏆  Outcomes":
    st.markdown('<div class="section-header">🏆 Outcomes</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">where goals end and become permanent record</div>', unsafe_allow_html=True)

    if "outcome_view" not in st.session_state:
        st.session_state["outcome_view"] = "📋 All Outcomes"
    if "editing_outcome" not in st.session_state:
        st.session_state["editing_outcome"] = None
    if "outcome_goal" not in st.session_state:
        st.session_state["outcome_goal"] = None

    # If a goal was passed in to end (from Goals page), force Log view
    if st.session_state.get("outcome_goal"):
        st.session_state["outcome_view"] = "➕ Log Outcome"

    options = ["📋 All Outcomes", "➕ Log Outcome"]
    current_index = options.index(st.session_state["outcome_view"])
    view = st.radio("Outcome View", options, index=current_index,
                    horizontal=True, label_visibility="collapsed", key=f"outcome_radio_{current_index}")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ============================================================
    # ALL OUTCOMES
    # ============================================================
    if view == "📋 All Outcomes":
        filter_labels = {"All": "All", "✅ Win": "win", "❌ Fail": "fail", "🔵 Pass": "pass", "🏁 Complete": "complete"}
        filter_choice = st.selectbox("Filter by result", list(filter_labels.keys()), label_visibility="collapsed")
        filter_type = filter_labels[filter_choice]

        try:
            query = supabase.table("outcomes").select("*").order("outcome_date", desc=True)
            if filter_type != "All":
                query = query.eq("result_type", filter_type)
            outcomes = query.execute().data or []
        except:
            outcomes = []

        if not outcomes:
            st.info("No outcomes logged yet. End a goal from the Goals page to record one.")
        else:
            border_colors = {"win": "#4ade80", "pass": "#60a5fa", "fail": "#f87171", "complete": "#fbbf24"}
            for o in outcomes:
                border = border_colors.get(o.get("result_type"), "#444")
                st.markdown(f"""
                <div class="card" style="border-left: 3px solid {border};">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                        <span style="font-size:1rem;font-weight:800;color:#fff;">{o['outcome_title']}</span>
                        {result_badge(o.get('result_type','pass'))}
                    </div>
                    <div style="color:#ccc;font-size:0.9rem;margin-bottom:0.4rem;"><b>Result:</b> {o.get('score_or_result','')}</div>
                    <div style="color:#888;font-size:0.85rem;font-style:italic;margin-bottom:0.4rem;">💭 {o.get('emotional_reaction','')}</div>
                    <div style="color:#888;font-size:0.85rem;margin-bottom:0.4rem;"><b>Why:</b> {o.get('causal_analysis','')}</div>
                    <div style="color:#aaa;font-size:0.85rem;"><b>💡 Lesson:</b> {o.get('lessons_learned','')}</div>
                    <div style="margin-top:0.5rem;font-size:0.75rem;color:#555;font-family:'JetBrains Mono',monospace;">{o.get('outcome_date','')}</div>
                </div>
                """, unsafe_allow_html=True)

                outcome_share_text = (
                    "🏆 Life Archive — Outcome\n"
                    f"📅 {o.get('outcome_date','')}\n"
                    f"{o.get('outcome_title','')}\n"
                    f"Result: {(o.get('result_type') or '').upper()}\n"
                    f"Summary: {o.get('score_or_result','') or '—'}\n"
                    f"Reflection: {o.get('lessons_learned','') or '—'}\n"
                    "— sent from Life Archive"
                )
                share_block(outcome_share_text, f"outcome_share_{o['id']}", "📤 Share")

                col_edit, col_del = st.columns([1, 1])
                with col_edit:
                    if st.button("✏️ Edit", key=f"edit_outcome_{o['id']}"):
                        st.session_state["editing_outcome"] = dict(o)
                        st.session_state["outcome_view"] = "➕ Log Outcome"
                        st.rerun()
                with col_del:
                    if st.button("🗑️ Delete", key=f"del_outcome_{o['id']}"):
                        st.session_state[f"confirm_del_o_{o['id']}"] = True
                        st.rerun()
                if st.session_state.get(f"confirm_del_o_{o['id']}", False):
                    st.warning(f"Delete **{o['outcome_title']}**? This cannot be undone.")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes, delete", key=f"yes_del_o_{o['id']}"):
                            supabase.table("outcomes").delete().eq("id", o["id"]).execute()
                            supabase.table("win_failure_archive").delete().eq("outcome_id", o["id"]).execute()
                            st.session_state[f"confirm_del_o_{o['id']}"] = False
                            st.rerun()
                    with c2:
                        if st.button("Cancel", key=f"cancel_del_o_{o['id']}"):
                            st.session_state[f"confirm_del_o_{o['id']}"] = False
                            st.rerun()

    # ============================================================
    # LOG / EDIT OUTCOME
    # ============================================================
    else:
        editing_o = st.session_state.get("editing_outcome", None)
        editing_o_id = editing_o["id"] if editing_o else None
        goal_ctx = st.session_state.get("outcome_goal", None)

        if editing_o:
            st.markdown("#### ✏️ Editing Outcome")
        elif goal_ctx:
            st.markdown(f"#### 🏁 Ending Goal: *{goal_ctx['goal_title']}*")
        else:
            st.markdown("#### Log a New Outcome")

        with st.form("outcome_form"):
            default_title = editing_o["outcome_title"] if editing_o else (goal_ctx["goal_title"] if goal_ctx else "")
            o_title = st.text_input("Outcome Title", value=default_title, placeholder="e.g. IELTS attempt, Startup pitch...")

            result_types = ["win", "fail", "pass", "complete"]
            default_result = editing_o["result_type"] if editing_o and editing_o.get("result_type") in result_types else "complete"
            o_result_type = st.selectbox("Result Type", result_types, index=result_types.index(default_result))

            o_score = st.text_input("Score / Result", value=editing_o.get("score_or_result","") if editing_o else "", placeholder="e.g. Scored 8.5, Got the job, Didn't finish...")
            o_emotion = st.text_area("Emotional Reaction", value=editing_o.get("emotional_reaction","") if editing_o else "", height=80, placeholder="How did you feel about it?")
            o_env = st.text_area("Environment Context", value=editing_o.get("environment_context","") if editing_o else "", height=80, placeholder="What was going on around you at the time?")
            o_causal = st.text_area("Causal Analysis", value=editing_o.get("causal_analysis","") if editing_o else "", height=80, placeholder="Why did it go this way?")
            o_lessons = st.text_area("Lessons Learned", value=editing_o.get("lessons_learned","") if editing_o else "", height=80, placeholder="What will you take from this?")

            from datetime import datetime
            default_date = datetime.strptime(editing_o["outcome_date"], "%Y-%m-%d").date() if editing_o and editing_o.get("outcome_date") else date.today()
            o_date = st.date_input("Outcome Date", value=default_date)

            submitted = st.form_submit_button("💾 Update Outcome" if editing_o else "💾 Save Outcome")

        if submitted:
            if not o_title.strip():
                st.error("Please enter an outcome title.")
            else:
                try:
                    record = {
                        "outcome_title": o_title.strip(),
                        "result_type": o_result_type,
                        "score_or_result": o_score.strip(),
                        "emotional_reaction": o_emotion.strip(),
                        "environment_context": o_env.strip(),
                        "causal_analysis": o_causal.strip(),
                        "lessons_learned": o_lessons.strip(),
                        "outcome_date": str(o_date),
                    }

                    if editing_o_id:
                        supabase.table("outcomes").update(record).eq("id", editing_o_id).execute()
                        # Update archive copy too
                        supabase.table("win_failure_archive").update({
                            "title": o_title.strip(),
                            "result_type": o_result_type,
                            "summary": o_score.strip(),
                            "reflection": o_lessons.strip(),
                            "archive_date": str(o_date)
                        }).eq("outcome_id", editing_o_id).execute()
                        st.success("✅ Outcome updated.")
                        st.session_state["editing_outcome"] = None
                    else:
                        if goal_ctx:
                            record["linked_goal_id"] = goal_ctx["id"]

                        result = supabase.table("outcomes").insert(record).execute()
                        new_outcome_id = result.data[0]["id"]

                        # Push to win/failure archive
                        supabase.table("win_failure_archive").insert({
                            "outcome_id": new_outcome_id,
                            "archive_date": str(o_date),
                            "title": o_title.strip(),
                            "result_type": o_result_type,
                            "summary": o_score.strip(),
                            "reflection": o_lessons.strip()
                        }).execute()

                        # Mark linked goal as completed
                        if goal_ctx:
                            supabase.table("goals").update({"status": "completed"}).eq("id", goal_ctx["id"]).execute()
                            st.session_state["outcome_goal"] = None

                        st.success("✅ Outcome saved and archived.")

                    st.session_state["outcome_view"] = "📋 All Outcomes"
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")

        if (editing_o_id or goal_ctx) and st.button("Cancel", key="cancel_outcome_form"):
            st.session_state["editing_outcome"] = None
            st.session_state["outcome_goal"] = None
            st.session_state["outcome_view"] = "📋 All Outcomes"
            st.rerun()

elif page == "📜  Archive":
    st.markdown('<div class="section-header">📜 Archive</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">your life, browsable</div>', unsafe_allow_html=True)

    archive_opts = ["🏆 Win/Failure Archive", "📅 Daily Log History", "📊 Quick Stats"]
    _arch_override = st.session_state.pop("archive_view_override", None)
    archive_view = st.radio("Archive View", archive_opts,
                            index=archive_opts.index(_arch_override) if _arch_override in archive_opts else 0,
                            horizontal=True, label_visibility="collapsed")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ============================================================
    # WIN/FAILURE ARCHIVE
    # ============================================================
    if archive_view == "🏆 Win/Failure Archive":
        filter_type = st.selectbox("Filter", ["All", "win", "fail", "pass", "complete"], label_visibility="collapsed")

        try:
            query = supabase.table("win_failure_archive").select("*").order("archive_date", desc=True)
            if filter_type != "All":
                query = query.eq("result_type", filter_type)
            entries = query.execute().data or []
        except:
            entries = []

        if not entries:
            st.info("Your win/failure archive is empty. Outcomes you log will appear here permanently.")
        else:
            border_colors = {"win": "#4ade80", "pass": "#60a5fa", "fail": "#f87171", "complete": "#fbbf24"}
            for e in entries:
                border = border_colors.get(e.get("result_type"), "#444")
                st.markdown(f"""
                <div class="card" style="border-left: 3px solid {border};">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                        <span style="font-size:1rem;font-weight:800;color:#fff;">{e['title']}</span>
                        {result_badge(e.get('result_type','pass'))}
                    </div>
                    <div style="color:#ccc;font-size:0.9rem;margin-bottom:0.4rem;">{e.get('summary','')}</div>
                    <div style="color:#888;font-size:0.85rem;font-style:italic;">💡 {e.get('reflection','')}</div>
                    <div style="margin-top:0.5rem;font-size:0.75rem;color:#555;font-family:'JetBrains Mono',monospace;">{e.get('archive_date','')}</div>
                </div>
                """, unsafe_allow_html=True)

    # ============================================================
    # DAILY LOG HISTORY
    # ============================================================
    elif archive_view == "📅 Daily Log History":
        try:
            logs = supabase.table("daily_logs").select("*").order("date", desc=True).execute().data or []
        except:
            logs = []

        if not logs:
            st.info("No daily logs yet. Start with today's entry.")
        else:
            # Mood trend chart
            chart_logs = list(reversed(logs))
            dates = [l["date"] for l in chart_logs]
            moods = [l.get("mood_score", 5) for l in chart_logs]

            svg_width = 800
            svg_height = 150
            padding = 20
            n = len(moods)
            if n > 1:
                x_step = (svg_width - 2 * padding) / (n - 1)
                points = []
                for i, m in enumerate(moods):
                    x = padding + i * x_step
                    y = svg_height - padding - ((m - 1) / 9) * (svg_height - 2 * padding)
                    points.append(f"{x:.1f},{y:.1f}")
                points_str = " ".join(points)

                circles = ""
                for i, m in enumerate(moods):
                    x = padding + i * x_step
                    y = svg_height - padding - ((m - 1) / 9) * (svg_height - 2 * padding)
                    color = "#4ade80" if m >= 8 else "#facc15" if m >= 5 else "#f87171"
                    circles += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color}"/>'

                st.markdown(f"""
                <div class="card">
                    <div style="font-size:0.75rem;color:#555;font-family:'JetBrains Mono',monospace;margin-bottom:0.5rem;">MOOD TREND</div>
                    <svg width="100%" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" preserveAspectRatio="none">
                        <polyline points="{points_str}" fill="none" stroke="#60a5fa" stroke-width="2"/>
                        {circles}
                    </svg>
                    <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#555;font-family:'JetBrains Mono',monospace;margin-top:0.3rem;">
                        <span>{dates[0]}</span><span>{dates[-1]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            # Browse by date
            for log in logs:
                with st.expander(f"{log['date']} — Mood {log.get('mood_score','—')}/10"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Mood** &nbsp; {mood_badge(log.get('mood_score',5))}", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"**Clarity** &nbsp; {clarity_badge(log.get('mental_clarity','normal'))}", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"**Emotion** &nbsp; `{log.get('dominant_emotion','—')}`")

                    st.markdown(f"**Self Assessment:** {log.get('self_assessment','—')}")
                    st.markdown(f"**Daily Summary:** {log.get('daily_summary','—')}")

                    accs = log.get('accomplishments') or []
                    if accs:
                        st.markdown("**Accomplishments:**")
                        for a in accs:
                            st.markdown(f"&nbsp; ✦ {a}")

                    media = log.get('media_consumed') or []
                    if media:
                        st.markdown("**Media:**")
                        for m in media:
                            st.markdown(f"&nbsp; 🎬 {m}")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"**Sleep** `{log.get('sleep_duration','—')} hrs`")
                    with col2:
                        st.markdown(f"**Physical** {physical_badge(log.get('physical_state','neutral'))}", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"**Mental** {mental_badge(log.get('mental_state','stable'))}", unsafe_allow_html=True)
                    with col4:
                        st.markdown(f"**Spent** `{log.get('daily_spending',0):,.0f}`")

                    st.markdown(f"**Good deed:** {log.get('good_deed','—')}")

    # ============================================================
    # QUICK STATS
    # ============================================================
    else:
        try:
            logs = supabase.table("daily_logs").select("*").execute().data or []
            books = supabase.table("books").select("*").execute().data or []
            events = supabase.table("life_events").select("*").execute().data or []
            outcomes = supabase.table("outcomes").select("*").execute().data or []
        except:
            logs = books = events = outcomes = []

        total_days = len(logs)
        avg_mood = (sum(l.get("mood_score", 0) for l in logs) / total_days) if total_days else 0

        from collections import Counter
        emotions = [l.get("dominant_emotion","").strip().lower() for l in logs if l.get("dominant_emotion")]
        most_common_emotion = Counter(emotions).most_common(1)[0][0] if emotions else "—"

        finished_books = [b for b in books if b["status"] == "finished"]

        wins = len([o for o in outcomes if o.get("result_type") == "win"])
        fails = len([o for o in outcomes if o.get("result_type") == "fail"])

        sig_breakdown = Counter(e.get("significance_score", 0) for e in events)

        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-value" style="color:#4ade80">{total_days}</div>
                <div class="metric-label">Days Logged</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#60a5fa">{avg_mood:.1f}</div>
                <div class="metric-label">Avg Mood</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#facc15;font-size:1.2rem;">{most_common_emotion}</div>
                <div class="metric-label">Top Emotion</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#fb923c">{len(finished_books)}</div>
                <div class="metric-label">Books Finished</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-value" style="color:#4ade80">{wins}</div>
                <div class="metric-label">Wins</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#f87171">{fails}</div>
                <div class="metric-label">Fails</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#a78bfa">{len(events)}</div>
                <div class="metric-label">Life Events</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color:#fbbf24">{sig_breakdown.get(5,0)}</div>
                <div class="metric-label">5★ Moments</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <div style="font-size:0.75rem;color:#555;font-family:'JetBrains Mono',monospace;margin-bottom:0.5rem;">REFLECTION</div>
            <div style="color:#ccc;">
                Every number here represents something real you lived through. This archive doesn't judge — it just remembers, so you don't have to carry it all in your head.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# SKILLS PAGE
# ============================================
elif page == "🧠  Skills":
    st.markdown('<div class="section-header">🧠 Skills</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">track mastery · hour by hour</div>', unsafe_allow_html=True)

    if "skill_view" not in st.session_state:
        st.session_state["skill_view"] = "📊 Active Skills"
    if "editing_skill" not in st.session_state:
        st.session_state["editing_skill"] = None
    if "skill_radio_counter" not in st.session_state:
        st.session_state["skill_radio_counter"] = 0

    options = ["📊 Active Skills", "➕ Add Skill"]
    current_index = options.index(st.session_state["skill_view"])
    view = st.radio("Skill View", options, index=current_index,
                    horizontal=True, label_visibility="collapsed",
                    key=f"skill_radio_{st.session_state['skill_radio_counter']}")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── ACTIVE SKILLS ──
    if view == "📊 Active Skills":
        try:
            skills = supabase.table("skills").select("*").order("created_at", desc=False).execute().data or []
        except:
            skills = []

        if not skills:
            st.info("No skills yet. Add your first skill to start tracking mastery.")
        else:
            # one fetch for all sessions → summary chart + per-skill views
            try:
                all_sk_sessions = supabase.table("skill_sessions").select("*").order("session_date", desc=False).execute().data or []
            except:
                all_sk_sessions = []
            sessions_by_skill = {}
            for s in all_sk_sessions:
                sessions_by_skill.setdefault(s.get("skill_id"), []).append(s)

            # ---- Total hours per skill (visualization) ----
            hour_bars = []
            for sk in skills:
                hrs = sum(s.get("duration_hours", 0) or 0 for s in sessions_by_skill.get(sk["id"], []))
                if hrs > 0:
                    hour_bars.append((sk["skill_name"], hrs, f"{hrs:.1f} h"))
            if hour_bars:
                hour_bars.sort(key=lambda x: x[1], reverse=True)
                st.markdown(hbar_block("TOTAL HOURS PER SKILL", hour_bars), unsafe_allow_html=True)
                st.markdown('<hr class="divider">', unsafe_allow_html=True)

            for sk in skills:
                sessions = sessions_by_skill.get(sk["id"], [])

                total_hours = sum(s.get("duration_hours", 0) or 0 for s in sessions)
                target_hours = sk.get("target_hours", 100) or 100
                progress_pct = min(int((total_hours / target_hours) * 100), 100)
                last_date = sessions[-1]["session_date"] if sessions else None

                from datetime import datetime, timedelta
                inactive_badge = ""
                if last_date:
                    days_since = (date.today() - datetime.strptime(last_date, "%Y-%m-%d").date()).days
                    if days_since >= 5:
                        inactive_badge = f'<span class="badge badge-red">🔴 {days_since}d inactive</span>'

                progress_color = "#a78bfa" if progress_pct < 50 else "#818cf8" if progress_pct < 80 else "#4ade80"

                st.markdown(f"""
                <div class="card">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                        <span style="font-size:1.1rem;font-weight:800;color:#e8e0ff;">{sk['skill_name']}</span>
                        <div style="display:flex;gap:0.5rem;align-items:center;">
                            {skill_level_badge(sk.get('target_level','beginner'))}
                            {inactive_badge}
                        </div>
                    </div>
                    <div style="font-size:0.8rem;color:#3a3a6a;font-family:'JetBrains Mono',monospace;margin-bottom:0.6rem;">
                        <span class="badge badge-grey">{sk.get('category','') or 'uncategorized'}</span> · {total_hours:.1f} / {target_hours} hrs · {len(sessions)} sessions · last session: {last_date or '—'}
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width:{progress_pct}%;background:{progress_color};"></div>
                    </div>
                    <div style="font-size:0.75rem;color:#3a3a6a;font-family:'JetBrains Mono',monospace;margin-top:3px;">{progress_pct}% to {sk.get('target_level','goal')}</div>
                </div>
                """, unsafe_allow_html=True)

                if len(sessions) >= 2:
                    with st.expander("📈 Progress over time"):
                        cum, running = [], 0.0
                        for s in sessions:
                            running += s.get("duration_hours", 0) or 0
                            cum.append((s["session_date"], running))
                        sw, sh, pad = 700, 130, 18
                        n = len(cum)
                        max_h = cum[-1][1] or 1
                        pts = []
                        for i, (_, h) in enumerate(cum):
                            x = pad + i * (sw - 2 * pad) / (n - 1)
                            y = sh - pad - (h / max_h) * (sh - 2 * pad)
                            pts.append(f"{x:.1f},{y:.1f}")
                        dots = "".join(f'<circle cx="{p.split(",")[0]}" cy="{p.split(",")[1]}" r="3" fill="#A78BFA"/>' for p in pts)
                        st.markdown(card_html(f"""
                            <div style="font-size:0.7rem;color:#3a3a6a;font-family:'JetBrains Mono',monospace;margin-bottom:0.4rem;">CUMULATIVE HOURS — {sk['skill_name'].upper()}</div>
                            <svg width="100%" height="{sh}" viewBox="0 0 {sw} {sh}" preserveAspectRatio="none">
                                <polyline points="{' '.join(pts)}" fill="none" stroke="#818CF8" stroke-width="2"/>
                                {dots}
                            </svg>
                            <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#555;font-family:'JetBrains Mono',monospace;">
                                <span>{cum[0][0]}</span><span>{cum[-1][0]} · {cum[-1][1]:.1f} h</span>
                            </div>
                        """), unsafe_allow_html=True)

                if sessions:
                    with st.expander(f"🗂 {len(sessions)} past sessions"):
                        for s in reversed(sessions):
                            stars = '★' * (s.get('difficulty',0) or 0) + '☆' * (5 - (s.get('difficulty',0) or 0))
                            st.markdown(f"""
                            <div class="card" style="margin-bottom:0.4rem;">
                                <div style="display:flex;justify-content:space-between;">
                                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#3a3a6a;">{s['session_date']}</span>
                                    <span class="badge badge-purple">{s.get('duration_hours',0)}h</span>
                                    <span class="badge badge-yellow">{stars}</span>
                                </div>
                                <div style="margin-top:0.4rem;color:#e8e0ff;font-size:0.85rem;"><b>{s.get('what_practiced','')}</b></div>
                                <div style="margin-top:0.2rem;color:#6a6a9a;font-size:0.85rem;">💡 {s.get('learning_note','')}</div>
                            </div>
                            """, unsafe_allow_html=True)

                with st.expander(f"➕ Log a session for '{sk['skill_name']}'"):
                    s_date     = st.date_input("Date", value=date.today(), key=f"sk_date_{sk['id']}")
                    s_dur      = st.number_input("Duration (hours)", min_value=0.0, step=0.25, value=1.0, key=f"sk_dur_{sk['id']}")
                    s_what     = st.text_input("What did you practice?", key=f"sk_what_{sk['id']}", placeholder="e.g. Hiragana drills, jab-cross combos, recursion problems...")
                    s_note     = st.text_area("What clicked / what you learned", key=f"sk_note_{sk['id']}", height=70)
                    s_diff     = st.slider("Difficulty (1–5)", 1, 5, 3, key=f"sk_diff_{sk['id']}")
                    s_enjoy    = st.slider("Enjoyment (1–5)", 1, 5, 3, key=f"sk_enjoy_{sk['id']}")

                    if st.button("💾 Save Session", key=f"sk_save_{sk['id']}", type="primary"):
                        try:
                            supabase.table("skill_sessions").insert({
                                "skill_id": sk["id"],
                                "session_date": str(s_date),
                                "duration_hours": s_dur,
                                "what_practiced": s_what.strip(),
                                "learning_note": s_note.strip(),
                                "difficulty": s_diff,
                                "enjoyment": s_enjoy
                            }).execute()
                            st.success("✅ Session logged.")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error: {ex}")

                col_edit, col_del = st.columns([1, 1])
                with col_edit:
                    if st.button("✏️ Edit", key=f"edit_skill_{sk['id']}"):
                        st.session_state["editing_skill"] = dict(sk)
                        st.session_state["skill_view"] = "➕ Add Skill"
                        st.session_state["skill_radio_counter"] += 1
                        st.rerun()
                with col_del:
                    if st.button("🗑️ Delete", key=f"del_skill_{sk['id']}"):
                        st.session_state[f"confirm_del_sk_{sk['id']}"] = True
                        st.rerun()
                if st.session_state.get(f"confirm_del_sk_{sk['id']}", False):
                    st.warning(f"Delete **{sk['skill_name']}**? All sessions will be lost.")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes, delete", key=f"yes_del_sk_{sk['id']}"):
                            supabase.table("skill_sessions").delete().eq("skill_id", sk["id"]).execute()
                            supabase.table("skills").delete().eq("id", sk["id"]).execute()
                            st.session_state[f"confirm_del_sk_{sk['id']}"] = False
                            st.rerun()
                    with c2:
                        if st.button("Cancel", key=f"cancel_del_sk_{sk['id']}"):
                            st.session_state[f"confirm_del_sk_{sk['id']}"] = False
                            st.rerun()

                st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── ADD / EDIT SKILL ──
    else:
        editing_sk = st.session_state.get("editing_skill", None)
        editing_sk_id = editing_sk["id"] if editing_sk else None
        st.markdown(f"#### {'✏️ Editing Skill' if editing_sk else 'What do you want to master?'}")

        with st.form("skill_form"):
            sk_name  = st.text_input("Skill Name", value=editing_sk["skill_name"] if editing_sk else "", placeholder="e.g. Japanese, Boxing, Python, Guitar...")
            cats     = ["Programming", "Language", "Sport", "Music", "Art", "Academic", "Other"]
            _legacy  = {"tech": "Programming", "language": "Language", "sport": "Sport",
                        "music": "Music", "art": "Art", "other": "Other"}
            _current = _legacy.get((editing_sk or {}).get("category", ""), (editing_sk or {}).get("category", ""))
            sk_cat   = st.selectbox("Category", cats, index=cats.index(_current) if _current in cats else 0)
            levels   = ["beginner", "intermediate", "advanced", "master"]
            sk_level = st.selectbox("Target Level", levels, index=levels.index(editing_sk["target_level"]) if editing_sk and editing_sk.get("target_level") in levels else 0)
            sk_hours = st.number_input("Target Hours to reach that level", min_value=1, step=10, value=int(editing_sk.get("target_hours", 100)) if editing_sk else 100)
            sk_why   = st.text_area("Why do you want this skill?", value=editing_sk.get("motivation","") if editing_sk else "", height=80, placeholder="What drives you to learn this?")
            submitted = st.form_submit_button("💾 Update Skill" if editing_sk else "💾 Add Skill")

        if submitted:
            if not sk_name.strip():
                st.error("Please enter a skill name.")
            else:
                try:
                    record = {
                        "skill_name": sk_name.strip(),
                        "category": sk_cat,
                        "target_level": sk_level,
                        "target_hours": sk_hours,
                        "motivation": sk_why.strip(),
                    }
                    if editing_sk_id:
                        supabase.table("skills").update(record).eq("id", editing_sk_id).execute()
                        st.success("✅ Skill updated.")
                        st.session_state["editing_skill"] = None
                    else:
                        record["date_started"] = str(date.today())
                        supabase.table("skills").insert(record).execute()
                        st.success(f"✅ '{sk_name}' added. Start logging sessions!")
                    st.session_state["skill_view"] = "📊 Active Skills"
                    st.session_state["skill_radio_counter"] += 1
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")

        if editing_sk_id and st.button("Cancel", key="cancel_skill_form"):
            st.session_state["editing_skill"] = None
            st.session_state["skill_view"] = "📊 Active Skills"
            st.session_state["skill_radio_counter"] += 1
            st.rerun()

# ============================================
# SETTINGS PAGE
# ============================================
elif page == "⚙️  Settings":
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">wallpaper · display · preferences</div>', unsafe_allow_html=True)

    st.markdown("#### 🖼 Wallpaper")

    current_wp = get_wallpaper()
    if current_wp:
        st.markdown('<span class="badge badge-green">✅ Wallpaper active</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload a wallpaper image", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed")

    current_opacity = get_overlay_opacity()
    opacity = st.slider("Overlay darkness (how much to dim the wallpaper)", 0.2, 0.9, current_opacity, step=0.05)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Wallpaper", type="primary"):
            try:
                if uploaded:
                    img_bytes = uploaded.read()
                    b64 = base64.b64encode(img_bytes).decode("utf-8")
                    supabase.table("settings").upsert({"key": "wallpaper_b64", "value": b64}).execute()
                supabase.table("settings").upsert({"key": "overlay_opacity", "value": str(opacity)}).execute()
                st.success("✅ Settings saved. Refresh the page to see your wallpaper.")
                st.rerun()
            except Exception as ex:
                st.error(f"Error: {ex}")
    with col2:
        if current_wp and st.button("🗑️ Remove Wallpaper"):
            try:
                supabase.table("settings").delete().eq("key", "wallpaper_b64").execute()
                st.success("✅ Wallpaper removed.")
                st.rerun()
            except Exception as ex:
                st.error(f"Error: {ex}")

    if current_wp:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("**Current wallpaper preview:**")
        import base64 as b64mod
        st.markdown(f'<img src="data:image/jpeg;base64,{current_wp[:100]}..." style="display:none">', unsafe_allow_html=True)
        st.markdown(f'<div style="width:100%;height:120px;background-image:url(\'data:image/jpeg;base64,{current_wp}\');background-size:cover;background-position:center;border-radius:8px;border:1px solid #2a2a4a;"></div>', unsafe_allow_html=True)

    # ============================================
    # EXPORT — full archive in your chosen format
    # ============================================
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("#### 📦 Export")
    st.markdown('<div class="section-sub">choose a format once — every download button in the app will use it</div>', unsafe_allow_html=True)

    fmt_choice = st.radio("Download format", EXPORT_FORMATS,
                          index=EXPORT_FORMATS.index(get_export_format()),
                          horizontal=True)
    st.session_state["export_format"] = fmt_choice

    ARCHIVE_TABLES = {
        "Daily Logs": ("daily_logs", "date"),
        "Books": ("books", "created_at"),
        "Reading Sessions": ("reading_sessions", "session_date"),
        "Life Events": ("life_events", "event_date"),
        "Purchases": ("purchases", "purchase_date"),
        "Wishes": ("wishes", "created_at"),
        "Goals": ("goals", "created_at"),
        "Goal Sessions": ("goal_sessions", "session_date"),
        "Outcomes": ("outcomes", "outcome_date"),
        "Win Failure Archive": ("win_failure_archive", "archive_date"),
        "Skills": ("skills", "created_at"),
        "Skill Sessions": ("skill_sessions", "session_date"),
    }

    if st.button("🗂 Generate Full Archive Export", type="primary"):
        tables = {}
        with st.spinner("Collecting your archive..."):
            for label, (tbl, order_col) in ARCHIVE_TABLES.items():
                try:
                    tables[label] = supabase.table(tbl).select("*").order(order_col, desc=True).execute().data or []
                except:
                    try:
                        tables[label] = supabase.table(tbl).select("*").execute().data or []
                    except:
                        tables[label] = []
        st.session_state["full_archive_tables"] = tables
        st.rerun()

    if st.session_state.get("full_archive_tables"):
        _tables = st.session_state["full_archive_tables"]
        _count = sum(len(v) for v in _tables.values())
        st.markdown(f'<div class="section-sub">✅ archive ready · {_count} records across {len(_tables)} tables</div>', unsafe_allow_html=True)
        export_download_button("⬇️ Download Full Archive", _tables,
                               f"life-archive-full-{date.today()}",
                               key="dl_full_archive",
                               doc_title="Life Archive — Full Export")

    # ============================================
    # DANGER ZONE
    # ============================================
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.1rem;font-weight:800;color:#F87171;font-family:\'Syne\',sans-serif;">☠️ Danger Zone</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">permanently delete every record in your archive · there is no undo</div>', unsafe_allow_html=True)

    with st.expander("🗑️ Delete ALL data"):
        st.error("This wipes every table: daily logs, books, sessions, events, purchases, wishes, goals, outcomes, skills — everything.")
        confirm_phrase = st.text_input('Type **DELETE EVERYTHING** to confirm', placeholder="DELETE EVERYTHING")
        if st.button("☠️ Permanently delete all data"):
            if confirm_phrase.strip() == "DELETE EVERYTHING":
                _wipe_order = ["reading_sessions", "goal_sessions", "skill_sessions",
                               "win_failure_archive", "outcomes", "goals", "wishes",
                               "purchases", "life_events", "books", "daily_logs"]
                errors = []
                with st.spinner("Deleting..."):
                    for tbl in _wipe_order:
                        try:
                            supabase.table(tbl).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                        except Exception as ex:
                            errors.append(f"{tbl}: {ex}")
                if errors:
                    st.error("Some tables could not be wiped:\n" + "\n".join(errors))
                else:
                    st.success("💀 All data deleted. Your archive is empty.")
                    st.session_state.pop("full_archive_tables", None)
            else:
                st.error("Confirmation phrase does not match. Nothing was deleted.")
