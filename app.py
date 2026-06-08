import streamlit as st
from supabase import create_client, Client
from datetime import date

# ============================================
# CONFIG
# ============================================
SUPABASE_URL = "https://gojnzhpapqzodzadetek.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdvam56aHBhcHF6b2R6YWRldGVrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA5MzU4MTcsImV4cCI6MjA5NjUxMTgxN30.5Y2-MXRBmPt-ps1JZ-52qYi2g9lQOED_Lb69uVAwzxk"  # paste your eyJ... key here

# ============================================
# SUPABASE CLIENT
# ============================================
@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Life Archive",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# GLOBAL STYLES
# ============================================
st.markdown("""
<style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

    /* Base */
    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
        background-color: #0e0e0e;
        color: #e8e8e8;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #141414;
        border-right: 1px solid #2a2a2a;
    }

    /* Main area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Section header */
    .section-header {
        font-family: 'Syne', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.2rem;
        color: #ffffff;
    }

    .section-sub {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 1.5rem;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Color level badges */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.5px;
    }
    .badge-green  { background: #1a3a2a; color: #4ade80; border: 1px solid #4ade80; }
    .badge-yellow { background: #3a2e0a; color: #facc15; border: 1px solid #facc15; }
    .badge-red    { background: #3a1212; color: #f87171; border: 1px solid #f87171; }
    .badge-blue   { background: #0f2640; color: #60a5fa; border: 1px solid #60a5fa; }
    .badge-orange { background: #3a1f0a; color: #fb923c; border: 1px solid #fb923c; }
    .badge-grey   { background: #1e1e1e; color: #9ca3af; border: 1px solid #444; }
    .badge-gold   { background: #3a2e00; color: #fbbf24; border: 1px solid #fbbf24; }

    /* Cards */
    .card {
        background: #161616;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
    }

    /* Divider */
    .divider {
        border: none;
        border-top: 1px solid #2a2a2a;
        margin: 1.5rem 0;
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background-color: #1a1a1a !important;
        border: 1px solid #2e2e2e !important;
        color: #e8e8e8 !important;
        border-radius: 8px !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #1a1a1a;
        color: #e8e8e8;
        border: 1px solid #3a3a3a;
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        padding: 0.4rem 1.2rem;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        border-color: #4ade80;
        color: #4ade80;
        background-color: #1a3a2a;
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        background-color: #1a3a2a;
        border-color: #4ade80;
        color: #4ade80;
    }

    /* Sidebar nav item style */
    .nav-item {
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        margin-bottom: 4px;
        cursor: pointer;
        font-size: 0.9rem;
        color: #aaa;
        transition: all 0.15s;
    }
    .nav-item:hover { background: #1e1e1e; color: #fff; }
    .nav-item.active { background: #1a3a2a; color: #4ade80; font-weight: 700; }

    /* Metric cards */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        flex: 1;
        background: #141414;
        border: 1px solid #2a2a2a;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================
# COLOR LEVEL HELPERS
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
    c = colors.get(clarity, "badge-grey")
    i = icons.get(clarity, "●")
    return f'<span class="badge {c}">{i} {clarity}</span>'

def physical_badge(state: str) -> str:
    colors = {"energized": "badge-green", "neutral": "badge-blue", "tired": "badge-red"}
    icons  = {"energized": "⚡", "neutral": "🔵", "tired": "🔴"}
    c = colors.get(state, "badge-grey")
    i = icons.get(state, "●")
    return f'<span class="badge {c}">{i} {state}</span>'

def mental_badge(state: str) -> str:
    colors = {"calm": "badge-green", "stable": "badge-blue", "stressed": "badge-orange", "heavy": "badge-red"}
    icons  = {"calm": "🟢", "stable": "🔵", "stressed": "🟠", "heavy": "🔴"}
    c = colors.get(state, "badge-grey")
    i = icons.get(state, "●")
    return f'<span class="badge {c}">{i} {state}</span>'

def result_badge(result: str) -> str:
    colors = {"win": "badge-green", "pass": "badge-blue", "fail": "badge-red", "complete": "badge-gold"}
    icons  = {"win": "🏆", "pass": "✅", "fail": "❌", "complete": "⭐"}
    c = colors.get(result, "badge-grey")
    i = icons.get(result, "●")
    return f'<span class="badge {c}">{i} {result.upper()}</span>'

def goal_status_badge(status: str) -> str:
    colors = {"active": "badge-green", "paused": "badge-grey", "completed": "badge-gold"}
    icons  = {"active": "🟢", "paused": "⏸️", "completed": "⭐"}
    c = colors.get(status, "badge-grey")
    i = icons.get(status, "●")
    return f'<span class="badge {c}">{i} {status.upper()}</span>'

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
# SIDEBAR NAVIGATION
# ============================================
with st.sidebar:
    st.markdown("""
        <div style="padding: 1rem 0 1.5rem 0;">
            <div style="font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 800; color: #fff;">
                🗂️ Life Archive
            </div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #444; margin-top: 4px;">
                personal memory system
            </div>
        </div>
        <hr style="border-color: #2a2a2a; margin-bottom: 1rem;">
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        options=[
            "🏠  Home",
            "📝  Daily Log",
            "📖  Reading Log",
            "🚨  Life Event",
            "🛍️  Purchase Tracker",
            "💫  Wish List",
            "🎯  Goals",
            "🏆  Outcomes",
            "📜  Archive",
        ],
        label_visibility="collapsed"
    )

    st.markdown("""
        <hr style="border-color: #2a2a2a; margin-top: 1rem;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #333; padding: 0.5rem 0;">
            v1.0 · built for long-term self-awareness
        </div>
    """, unsafe_allow_html=True)

# ============================================
# HOME PAGE
# ============================================
if page == "🏠  Home":
    st.markdown('<div class="section-header">Good to see you.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Today is {date.today().strftime("%A, %B %d %Y")} · Your archive is running.</div>', unsafe_allow_html=True)

    # Quick stats
    try:
        total_logs     = supabase.table("daily_logs").select("id", count="exact").execute().count or 0
        total_goals    = supabase.table("goals").select("id", count="exact").execute().count or 0
        total_wishes   = supabase.table("wishes").select("id", count="exact").execute().count or 0
        total_outcomes = supabase.table("outcomes").select("id", count="exact").execute().count or 0
    except:
        total_logs = total_goals = total_wishes = total_outcomes = 0

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-value" style="color:#4ade80">{total_logs}</div>
            <div class="metric-label">Days Logged</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color:#60a5fa">{total_goals}</div>
            <div class="metric-label">Active Goals</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color:#facc15">{total_wishes}</div>
            <div class="metric-label">Wishes</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color:#fb923c">{total_outcomes}</div>
            <div class="metric-label">Outcomes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div style="font-size:0.8rem; color:#666; font-family:'JetBrains Mono',monospace; margin-bottom:0.5rem;">WHAT THIS IS</div>
        <div style="color:#ccc; line-height:1.7;">
            This is your private life archive. Not a productivity tool. Not a habit tracker.<br>
            A structured memory of who you are, what you tried, and what actually happened.<br><br>
            Every entry you make becomes a permanent, queryable record of your life.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div style="font-size:0.8rem; color:#666; font-family:'JetBrains Mono',monospace; margin-bottom:0.8rem;">QUICK START</div>
        <div style="color:#ccc; font-size:0.9rem; line-height:2;">
            📝 &nbsp;<b>Daily Log</b> — start here every day<br>
            💫 &nbsp;<b>Wish List</b> — add anything you want to pursue<br>
            🎯 &nbsp;<b>Goals</b> — activate a wish and start tracking<br>
            🏆 &nbsp;<b>Outcomes</b> — record what happened when it ended<br>
            📜 &nbsp;<b>Archive</b> — browse your full history
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# PLACEHOLDER PAGES (to be built in next parts)
# ============================================
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

        if st.button("✏️ Edit Today's Entry"):
            st.session_state.edit_mode = True
            st.session_state.accomplishments = e.get('accomplishments') or []
            st.session_state.media_list = e.get('media_consumed') or []
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
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error saving: {ex}")

        if already_logged and st.button("Cancel"):
            st.session_state.edit_mode = False
            st.rerun()

elif page == "📖  Reading Log":
    st.markdown('<div class="section-header">📖 Reading Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">coming in part 3</div>', unsafe_allow_html=True)
    st.info("This section is being built. Check back after Part 3.")

elif page == "🚨  Life Event":
    st.markdown('<div class="section-header">🚨 Life Event Diary</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">coming in part 3</div>', unsafe_allow_html=True)
    st.info("This section is being built. Check back after Part 3.")

elif page == "🛍️  Purchase Tracker":
    st.markdown('<div class="section-header">🛍️ Purchase Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">coming in part 3</div>', unsafe_allow_html=True)
    st.info("This section is being built. Check back after Part 3.")

elif page == "💫  Wish List":
    st.markdown('<div class="section-header">💫 Wish List</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">coming in part 4</div>', unsafe_allow_html=True)
    st.info("This section is being built. Check back after Part 4.")

elif page == "🎯  Goals":
    st.markdown('<div class="section-header">🎯 Goals</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">coming in part 4</div>', unsafe_allow_html=True)
    st.info("This section is being built. Check back after Part 4.")

elif page == "🏆  Outcomes":
    st.markdown('<div class="section-header">🏆 Outcomes</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">coming in part 5</div>', unsafe_allow_html=True)
    st.info("This section is being built. Check back after Part 5.")

elif page == "📜  Archive":
    st.markdown('<div class="section-header">📜 Archive</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">coming in part 6</div>', unsafe_allow_html=True)
    st.info("This section is being built. Check back after Part 6.")
