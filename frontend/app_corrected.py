import streamlit as st
from agentforge.services.sql_service import ask_sql_question
from agentforge.tools.weather import get_weather

st.set_page_config(page_title="Agent Forge", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
.stApp{background:radial-gradient(ellipse at 4% 2%,rgba(210,184,255,.36),transparent 27%),radial-gradient(ellipse at 98% 4%,rgba(177,231,255,.38),transparent 25%),#fffdfd;color:#111b55;font-family:Inter,sans-serif}
#MainMenu,footer{visibility:hidden}.block-container{max-width:1240px;padding-top:1rem;padding-bottom:1rem}
.brand{display:flex;justify-content:center;align-items:center;gap:15px;margin:.4rem 0 1.2rem}
.brand-mark{width:68px;height:68px;border-radius:22px;display:flex;align-items:center;justify-content:center;font-size:38px;background:linear-gradient(140deg,#7c4dff,#31b9ff);box-shadow:0 12px 30px #744bff38}
.brand-name{font-size:3.3rem;font-weight:800;letter-spacing:-2px;color:#10194f}.brand-name span{background:linear-gradient(100deg,#7046ed,#9b28e8);-webkit-background-clip:text;color:transparent}
.home-intro{text-align:center;color:#69728f;margin:0 0 1rem}
.card{height:360px;border-radius:34px;padding:1.5rem;text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative;overflow:hidden;transition:transform .28s,box-shadow .28s,border-color .28s}
.sql{background:linear-gradient(145deg,#ffffffed,#f4ebffe8);border:2px solid #a47bff78;box-shadow:0 16px 42px #7e4fee20}
.weather{background:linear-gradient(145deg,#ffffffed,#e4fbf8e8);border:2px solid #58dacb70;box-shadow:0 16px 42px #29c1b71c}
.card-icon{width:130px;height:130px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:65px;margin-bottom:1rem;background:radial-gradient(circle,#fff,#eee6ff);box-shadow:0 12px 30px #7c4dff20}
.weather .card-icon{background:radial-gradient(circle,#fff,#e4fbfa);box-shadow:0 12px 30px #16c7c120}
.card-title{font-size:2.1rem;font-weight:800;color:#111b55}.card-desc{color:#65708f;margin-top:.4rem}
.card-arrow{position:absolute;right:1.6rem;bottom:1.3rem;width:52px;height:52px;border-radius:50%;display:grid;place-items:center;color:white;font-size:1.8rem;background:linear-gradient(135deg,#b25aff,#7046ed)}
.weather .card-arrow{background:linear-gradient(135deg,#25d7d0,#00aaa9)}
/* Invisible Streamlit button overlays the full visual card; card itself remains the visible design. */
.card-click div.stButton{margin-top:-360px;position:relative;z-index:5}
.card-click div.stButton>button{height:360px;width:100%;opacity:0;border:0;background:transparent;color:transparent;cursor:pointer}
.card-click div.stButton>button:hover{background:transparent;border:0}
.card:hover{transform:translateY(-9px) scale(1.012)}
.sql:hover{border-color:#9b70ff;box-shadow:0 24px 55px #7e4fee47,0 0 24px #9b70ff29}
.weather:hover{border-color:#4ed8d0;box-shadow:0 24px 55px #29c1b73d,0 0 24px #4ed8d029}
.workspace-title{font-size:1.85rem;font-weight:800;letter-spacing:-1px;color:#111b55;margin:0}
.workspace-subtitle{color:#65708f;font-size:.88rem;margin:.1rem 0 .75rem}
.panel{background:#ffffffd1;border:1px solid #e9e6f5;border-radius:18px;padding:.9rem 1rem;min-height:300px}
.panel-title{font-size:1rem;font-weight:750;color:#18245c;margin-bottom:.5rem}
div.stButton>button,div.stFormSubmitButton>button{border-radius:13px;min-height:2.55rem;font-weight:650}
.sql-submit div.stFormSubmitButton>button{background:linear-gradient(100deg,#7650f5,#a04df2);color:white;border:0}
.weather-submit div.stFormSubmitButton>button{background:linear-gradient(100deg,#18c9c2,#12aaa9);color:white;border:0}
@media(max-width:800px){.card{height:260px}.card-click div.stButton{margin-top:-260px}.card-click div.stButton>button{height:260px}.card-icon{width:100px;height:100px;font-size:52px}.card-title{font-size:1.6rem}.panel{min-height:auto}}
</style>
''', unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page = "home"
if "sql_result" not in st.session_state: st.session_state.sql_result = None
if "weather_result" not in st.session_state: st.session_state.weather_result = None
if "weather_city" not in st.session_state: st.session_state.weather_city = ""

def go_home():
    st.session_state.page = "home"

def brand():
    st.markdown('<div class="brand"><div class="brand-mark">🤖</div><div class="brand-name">Agent <span>Forge</span></div></div>', unsafe_allow_html=True)

def render_home():
    brand()
    st.markdown('<div class="home-intro">Choose an AI agent to get started</div>', unsafe_allow_html=True)
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown('<div class="card sql"><div class="card-icon">🗄️</div><div class="card-title">SQL Agent</div><div class="card-desc">Ask questions about your database</div><div class="card-arrow">→</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="card-click">', unsafe_allow_html=True)
        if st.button("Open SQL Agent", key="sql_card_click", use_container_width=True):
            st.session_state.page = "sql"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card weather"><div class="card-icon">🌤️</div><div class="card-title">Weather Agent</div><div class="card-desc">Get current weather for any city</div><div class="card-arrow">→</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="card-click">', unsafe_allow_html=True)
        if st.button("Open Weather Agent", key="weather_card_click", use_container_width=True):
            st.session_state.page = "weather"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def render_sql():
    h, b = st.columns([5, 1])
    with h: st.markdown('<div class="workspace-title">🗄️ SQL Agent</div><div class="workspace-subtitle">Ask your database in natural language.</div>', unsafe_allow_html=True)
    with b: st.button("← Home", key="sql_home", on_click=go_home, use_container_width=True)
    left, right = st.columns([.9, 1.35], gap="medium")
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Your question</div>', unsafe_allow_html=True)
        with st.form("sql_form", border=False):
            question = st.text_area("Question", placeholder="Example: Find employees working in the IT department", height=125, label_visibility="collapsed")
            st.markdown('<div class="sql-submit">', unsafe_allow_html=True)
            submitted = st.form_submit_button("Run SQL Agent", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Ask about employees, departments, courses, and more.")
        st.markdown('</div>', unsafe_allow_html=True)
        if submitted:
            if not question.strip(): st.warning("Please enter a question.")
            else:
                with st.spinner("Analyzing your question..."):
                    st.session_state.sql_result = ask_sql_question(question.strip())
    with right:
        st.markdown('<div class="panel"><div class="panel-title">Answer & results</div>', unsafe_allow_html=True)
        result = st.session_state.sql_result
        if not result: st.markdown('<div style="color:#7b84a0;padding:2rem;text-align:center">Your answer and query results will appear here.</div>', unsafe_allow_html=True)
        elif result.get("status") == "error": st.error(result.get("error", "Something went wrong."))
        else:
            st.caption("Status: " + str(result.get("status", "unknown")).upper())
            if result.get("final_answer"): st.markdown(result["final_answer"])
            if result.get("generated_sql"):
                with st.expander("Generated SQL"): st.code(result["generated_sql"], language="sql")
            df = result.get("dataframe")
            if df is not None and not df.empty:
                st.markdown("**Query results**")
                st.dataframe(df, use_container_width=True, height=165)
            elif result.get("status") == "success": st.caption("Query executed successfully; no matching rows.")
        st.markdown('</div>', unsafe_allow_html=True)

def render_weather():
    h, b = st.columns([5, 1])
    with h: st.markdown('<div class="workspace-title">🌤️ Weather Agent</div><div class="workspace-subtitle">Current weather conditions for cities worldwide.</div>', unsafe_allow_html=True)
    with b: st.button("← Home", key="weather_home", on_click=go_home, use_container_width=True)
    cities = ["Hyderabad","Bengaluru","Mumbai","Delhi","Chennai","Visakhapatnam","Pune","Kolkata","Warangal","Vijayawada","Ahmedabad","Jaipur","Kochi","London","New York","Tokyo","Singapore","Dubai","Paris","Sydney"]
    left, right = st.columns([.9, 1.35], gap="medium")
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Find a city</div>', unsafe_allow_html=True)
        choice = st.selectbox("City", ["Select a city..."] + cities + ["Enter another city"], label_visibility="collapsed")
        custom = st.text_input("City name", placeholder="Type any city") if choice == "Enter another city" else ""
        with st.form("weather_form", border=False):
            st.markdown('<div class="weather-submit">', unsafe_allow_html=True)
            submitted = st.form_submit_button("Get Weather", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Type in the selector to filter city suggestions.")
        st.markdown('</div>', unsafe_allow_html=True)
        if submitted:
            city = custom.strip() if choice == "Enter another city" else choice
            if not city or city == "Select a city...": st.warning("Please select or enter a city.")
            else:
                with st.spinner("Fetching current weather..."):
                    st.session_state.weather_result = get_weather.invoke({"city": city})
                    st.session_state.weather_city = city
    with right:
        st.markdown('<div class="panel"><div class="panel-title">Current conditions</div>', unsafe_allow_html=True)
        result = st.session_state.weather_result
        if not result: st.markdown('<div style="color:#7b84a0;padding:2rem;text-align:center">Weather details will appear here.</div>', unsafe_allow_html=True)
        elif result.startswith("Unable to") or "was not found" in result or "API returned an error" in result: st.error(result)
        else:
            st.markdown(f'<div style="font-size:1.5rem;font-weight:800;color:#111b55;margin-bottom:.4rem">{st.session_state.weather_city}</div>', unsafe_allow_html=True)
            st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.page == "home": render_home()
elif st.session_state.page == "sql": render_sql()
elif st.session_state.page == "weather": render_weather()
