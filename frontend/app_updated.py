import streamlit as st
from agentforge.services.sql_service import ask_sql_question
from agentforge.tools.weather import get_weather

st.set_page_config(
    page_title="Agent Forge",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    r"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root { --ink:#111b55; --muted:#65708f; --purple:#7650f5; --teal:#16c7c1; }
    html, body, [class*="css"] { font-family:Inter,sans-serif; }
    .stApp {
        background:
          radial-gradient(ellipse at 4% 2%,rgba(210,184,255,.36),transparent 27%),
          radial-gradient(ellipse at 98% 4%,rgba(177,231,255,.38),transparent 25%),
          radial-gradient(ellipse at 0% 100%,rgba(229,211,255,.26),transparent 28%),
          #fffdfd;
        color:var(--ink);
    }
    [data-testid="stHeader"] { background:transparent; }
    #MainMenu, footer { visibility:hidden; }
    .block-container { max-width:1180px; padding-top:1.1rem; padding-bottom:1.2rem; }
    .brand { display:flex; justify-content:center; align-items:center; gap:14px; margin:.45rem 0 1.4rem; }
    .brand-mark { width:62px;height:62px;border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:35px;background:linear-gradient(140deg,#7c4dff,#31b9ff);box-shadow:0 12px 30px rgba(116,75,255,.22); }
    .brand-name { font-size:clamp(2.2rem,4vw,3.35rem);line-height:1;font-weight:800;letter-spacing:-2px;color:#10194f; }
    .brand-name span { background:linear-gradient(100deg,#7046ed,#9b28e8);-webkit-background-clip:text;background-clip:text;color:transparent; }
    .home-intro { text-align:center;color:#69728f;font-size:.98rem;margin:0 0 1.1rem; }
    .agent-select div.stButton > button {
        height:330px; width:100%; white-space:pre-wrap; text-align:center;
        border-radius:32px; border:2px solid rgba(164,123,255,.48);
        background:linear-gradient(145deg,rgba(255,255,255,.96),rgba(244,235,255,.9));
        color:#111b55; font-size:1.65rem; font-weight:750;
        box-shadow:0 16px 42px rgba(126,79,238,.13),inset 0 0 30px rgba(255,255,255,.8);
        transition:transform .28s ease,box-shadow .28s ease,border-color .28s ease;
    }
    .agent-select div.stButton > button:hover {
        transform:translateY(-9px) scale(1.012);border-color:#9b70ff;
        box-shadow:0 24px 55px rgba(126,79,238,.27),0 0 24px rgba(155,112,255,.16);
        color:#111b55;
    }
    .agent-select.weather div.stButton > button {
        border-color:rgba(88,218,207,.42);
        background:linear-gradient(145deg,rgba(255,255,255,.97),rgba(228,251,248,.92));
        box-shadow:0 16px 42px rgba(41,193,183,.12),inset 0 0 30px rgba(255,255,255,.85);
    }
    .agent-select.weather div.stButton > button:hover {
        border-color:#4ed8d0;box-shadow:0 24px 55px rgba(41,193,183,.24),0 0 24px rgba(78,216,208,.16);
    }
    .workspace-title { font-size:1.9rem;font-weight:800;letter-spacing:-1px;color:#111b55;margin:0; }
    .workspace-subtitle { color:#65708f;font-size:.9rem;margin:.15rem 0 .85rem; }
    .panel { background:rgba(255,255,255,.78);border:1px solid #e9e6f5;border-radius:18px;padding:1rem 1.05rem;min-height:310px; }
    .panel-title { font-size:1rem;font-weight:750;color:#18245c;margin-bottom:.65rem; }
    .status-pill { display:inline-block;padding:4px 10px;border-radius:999px;background:#eee9ff;color:#6744d8;font-size:.76rem;font-weight:700; }
    div.stButton > button, div.stFormSubmitButton > button { border-radius:13px;min-height:2.65rem;font-weight:650; }
    .sql-submit div.stFormSubmitButton > button { background:linear-gradient(100deg,#7650f5,#a04df2);color:white;border:0; }
    .weather-submit div.stFormSubmitButton > button { background:linear-gradient(100deg,#18c9c2,#12aaa9);color:white;border:0; }
    [data-testid="stDataFrame"] { border-radius:12px;overflow:hidden; }
    @media(max-width:700px) {
        .brand { margin:.2rem 0 1rem; }
        .brand-mark { width:50px;height:50px;font-size:29px; }
        .agent-select div.stButton > button { height:220px;font-size:1.3rem; }
        .panel { min-height:auto; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "page" not in st.session_state:
    st.session_state.page = "home"
if "sql_result" not in st.session_state:
    st.session_state.sql_result = None
if "weather_result" not in st.session_state:
    st.session_state.weather_result = None
if "weather_city" not in st.session_state:
    st.session_state.weather_city = ""

def go_home():
    st.session_state.page = "home"

def render_brand():
    st.markdown(
        '<div class="brand"><div class="brand-mark">🤖</div><div class="brand-name">Agent <span>Forge</span></div></div>',
        unsafe_allow_html=True,
    )

def render_home():
    render_brand()
    st.markdown('<div class="home-intro">Choose an AI agent to get started</div>', unsafe_allow_html=True)
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown('<div class="agent-select sql">', unsafe_allow_html=True)
        if st.button("🗄️\n\nSQL Agent\n\nAsk questions about your database\n\n↗", key="select_sql", use_container_width=True):
            st.session_state.page = "sql"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="agent-select weather">', unsafe_allow_html=True)
        if st.button("🌤️\n\nWeather Agent\n\nGet current weather for any city\n\n↗", key="select_weather", use_container_width=True):
            st.session_state.page = "weather"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def render_sql():
    head, back = st.columns([5, 1])
    with head:
        st.markdown('<div class="workspace-title">🗄️ SQL Agent</div><div class="workspace-subtitle">Ask your database in natural language.</div>', unsafe_allow_html=True)
    with back:
        st.button("← Home", key="sql_back", on_click=go_home, use_container_width=True)

    left, right = st.columns([1, 1.25], gap="medium")
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Your question</div>', unsafe_allow_html=True)
        with st.form("sql_form", border=False):
            question = st.text_area(
                "Question",
                placeholder="Example: Find employees working in the IT department",
                height=145,
                label_visibility="collapsed",
            )
            st.markdown('<div class="sql-submit">', unsafe_allow_html=True)
            submitted = st.form_submit_button("Run SQL Agent", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div style="color:#65708f;font-size:.8rem;margin-top:.25rem">Ask a question about the connected MySQL database.</div></div>', unsafe_allow_html=True)

        if submitted:
            if not question.strip():
                st.warning("Please enter a database question.")
            else:
                with st.spinner("Analyzing your question..."):
                    st.session_state.sql_result = ask_sql_question(question.strip())

    with right:
        st.markdown('<div class="panel"><div class="panel-title">Agent response</div>', unsafe_allow_html=True)
        result = st.session_state.sql_result
        if not result:
            st.markdown('<div style="color:#7b84a0;padding:2.5rem .2rem;text-align:center">Your answer and query results will appear here.</div>', unsafe_allow_html=True)
        elif result.get("status") == "error":
            st.error(result.get("error", "Something went wrong."))
        else:
            st.markdown(f'<span class="status-pill">{result.get("status","unknown").upper()}</span>', unsafe_allow_html=True)
            if result.get("final_answer"):
                st.markdown(result["final_answer"])
            if result.get("generated_sql"):
                with st.expander("Generated SQL"):
                    st.code(result["generated_sql"], language="sql")
            if result.get("validation_output"):
                with st.expander("SQL checker output"):
                    st.code(str(result["validation_output"]), language="sql")
            df = result.get("dataframe")
            if df is not None and not df.empty:
                st.markdown("**Query results**")
                st.dataframe(df, use_container_width=True, height=190)
            elif result.get("status") == "success":
                st.caption("The query executed successfully and returned no rows.")
        st.markdown("</div>", unsafe_allow_html=True)

def render_weather():
    head, back = st.columns([5, 1])
    with head:
        st.markdown('<div class="workspace-title">🌤️ Weather Agent</div><div class="workspace-subtitle">Find current weather conditions for a city.</div>', unsafe_allow_html=True)
    with back:
        st.button("← Home", key="weather_back", on_click=go_home, use_container_width=True)

    cities = [
        "Hyderabad", "Bengaluru", "Mumbai", "Delhi", "Chennai",
        "Visakhapatnam", "Pune", "Kolkata", "Warangal", "Vijayawada",
        "Ahmedabad", "Jaipur", "Kochi", "London", "New York",
        "Tokyo", "Singapore", "Dubai", "Paris", "Sydney",
    ]
    left, right = st.columns([1, 1.25], gap="medium")
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Choose a city</div>', unsafe_allow_html=True)
        city_choice = st.selectbox("Popular cities", ["Select a city..."] + cities + ["Enter another city"], label_visibility="collapsed")
        custom_city = ""
        if city_choice == "Enter another city":
            custom_city = st.text_input("City name", placeholder="Type any city in the world")
        st.markdown('<div class="weather-submit">', unsafe_allow_html=True)
        with st.form("weather_form", border=False):
            submitted = st.form_submit_button("Get Weather", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div style="color:#65708f;font-size:.8rem;margin-top:.4rem">Start typing in the city selector to filter suggestions.</div></div>', unsafe_allow_html=True)

        if submitted:
            city = custom_city.strip() if city_choice == "Enter another city" else city_choice
            if not city or city == "Select a city...":
                st.warning("Please select or enter a city.")
            else:
                with st.spinner(f"Fetching weather for {city}..."):
                    st.session_state.weather_result = get_weather.invoke({"city": city})
                    st.session_state.weather_city = city

    with right:
        st.markdown('<div class="panel"><div class="panel-title">Current conditions</div>', unsafe_allow_html=True)
        result = st.session_state.weather_result
        if not result:
            st.markdown('<div style="color:#7b84a0;padding:2.5rem .2rem;text-align:center">Choose a city to see its weather here.</div>', unsafe_allow_html=True)
        elif result.startswith("Unable to") or "was not found" in result or "API returned an error" in result:
            st.error(result)
        else:
            st.markdown(f'<div style="font-size:1.45rem;font-weight:800;color:#111b55;margin-bottom:.5rem">{st.session_state.weather_city}</div>', unsafe_allow_html=True)
            st.markdown(result)
        st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.page == "home":
    render_home()
elif st.session_state.page == "sql":
    render_sql()
elif st.session_state.page == "weather":
    render_weather()
