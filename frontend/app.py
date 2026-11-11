import streamlit as st
from agentforge.services.sql_service import ask_sql_question
from agentforge.tools.weather import get_weather

st.set_page_config(page_title="Agent Forge", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

st.markdown(r'''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{--ink:#111b55;--muted:#65708f;--purple:#7650f5;--teal:#16c7c1}
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{background:radial-gradient(ellipse at 4% 2%,rgba(210,184,255,.36),transparent 27%),radial-gradient(ellipse at 98% 4%,rgba(177,231,255,.38),transparent 25%),radial-gradient(ellipse at 0% 100%,rgba(229,211,255,.26),transparent 28%),#fffdfd;color:var(--ink)}
[data-testid="stHeader"]{background:transparent}#MainMenu,footer{visibility:hidden}.block-container{max-width:1180px;padding-top:2.2rem;padding-bottom:3rem}
.brand{display:flex;justify-content:center;align-items:center;gap:15px;margin:1.2rem 0 3.6rem}.brand-mark{width:76px;height:76px;border-radius:24px;display:flex;align-items:center;justify-content:center;font-size:42px;background:linear-gradient(140deg,#7c4dff,#31b9ff);box-shadow:0 12px 30px rgba(116,75,255,.25)}.brand-name{font-size:clamp(2.3rem,5vw,4rem);line-height:1;font-weight:800;letter-spacing:-2.5px;color:#10194f}.brand-name span{background:linear-gradient(100deg,#7046ed,#9b28e8);-webkit-background-clip:text;background-clip:text;color:transparent}
.home-intro{text-align:center;color:#69728f;font-size:1rem;margin:-2rem 0 2.1rem}.agent-card{min-height:365px;border-radius:34px;padding:2.5rem 1.5rem 1.6rem;text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;transition:transform .28s ease,box-shadow .28s ease,border-color .28s ease;position:relative;overflow:hidden;backdrop-filter:blur(18px)}.agent-card:before{content:"";position:absolute;inset:auto -10% -35px -10%;height:105px;border-radius:50% 50% 0 0;opacity:.72;pointer-events:none}
.sql-card{background:linear-gradient(145deg,rgba(255,255,255,.94),rgba(244,235,255,.88));border:2px solid rgba(164,123,255,.48);box-shadow:0 16px 42px rgba(126,79,238,.12),inset 0 0 30px rgba(255,255,255,.8)}.sql-card:before{background:linear-gradient(90deg,rgba(173,139,255,.18),rgba(126,73,255,.24))}
.weather-card{background:linear-gradient(145deg,rgba(255,255,255,.96),rgba(228,251,248,.9));border:2px solid rgba(88,218,207,.4);box-shadow:0 16px 42px rgba(41,193,183,.11),inset 0 0 30px rgba(255,255,255,.85)}.weather-card:before{background:linear-gradient(90deg,rgba(104,230,218,.18),rgba(30,196,190,.22))}
.agent-card:hover{transform:translateY(-10px) scale(1.015)}.sql-card:hover{border-color:#9b70ff;box-shadow:0 24px 55px rgba(126,79,238,.28),0 0 24px rgba(155,112,255,.16)}.weather-card:hover{border-color:#4ed8d0;box-shadow:0 24px 55px rgba(41,193,183,.24),0 0 24px rgba(78,216,208,.16)}
.agent-icon{width:132px;height:132px;border-radius:50%;display:flex;justify-content:center;align-items:center;font-size:66px;margin-bottom:1.1rem;transition:transform .3s ease;position:relative;z-index:1}.sql-icon{background:radial-gradient(circle,#fff 15%,#eee6ff 75%);box-shadow:0 12px 30px rgba(124,77,255,.12)}.weather-icon{background:radial-gradient(circle,#fff 10%,#e4fbfa 78%);box-shadow:0 12px 30px rgba(22,199,193,.12)}.agent-card:hover .agent-icon{transform:scale(1.08) rotate(-3deg)}.agent-title{font-size:2.1rem;font-weight:750;color:#111b55;letter-spacing:-1px;position:relative;z-index:1}.agent-description{color:#65708f;font-size:.96rem;margin-top:.45rem;position:relative;z-index:1}.card-arrow{position:absolute;right:2rem;bottom:1.6rem;width:54px;height:54px;border-radius:50%;display:grid;place-items:center;color:white;font-size:1.8rem;z-index:2}.sql-arrow{background:linear-gradient(135deg,#b25aff,#7046ed)}.weather-arrow{background:linear-gradient(135deg,#25d7d0,#00aaa9)}
div.stButton>button{border-radius:16px;min-height:3.1rem;font-weight:650;border:1px solid #e5e4f2;transition:transform .2s ease,box-shadow .2s ease,background .2s ease}div.stButton>button:hover{transform:translateY(-2px);box-shadow:0 9px 22px rgba(95,77,180,.14);border-color:#b9a5ff}.primary-sql div.stButton>button{background:linear-gradient(100deg,#7650f5,#a04df2);color:white;border:0}.primary-weather div.stButton>button{background:linear-gradient(100deg,#18c9c2,#12aaa9);color:white;border:0}
.workspace-heading{font-size:2rem;font-weight:800;letter-spacing:-1px;color:#111b55;margin-bottom:.2rem}.workspace-subtitle{color:#65708f;margin-bottom:1.5rem}.result-panel{border:1px solid #e9e6f5;border-radius:18px;padding:1rem 1.2rem;background:rgba(255,255,255,.78);margin:.8rem 0}
@media(max-width:700px){.brand{margin-bottom:2.4rem}.brand-mark{width:58px;height:58px;font-size:32px}.agent-card{min-height:280px;margin-bottom:1rem}.agent-title{font-size:1.65rem}.agent-icon{width:105px;height:105px;font-size:54px}}
</style>''', unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "home"

def go_home(): st.session_state.page = "home"
def open_sql(): st.session_state.page = "sql"
def open_weather(): st.session_state.page = "weather"

def render_brand():
    st.markdown('''<div class="brand"><div class="brand-mark">🤖</div><div class="brand-name">Agent <span>Forge</span></div></div>''', unsafe_allow_html=True)

def render_home():
    render_brand()
    st.markdown('<div class="home-intro">Choose an AI agent to get started</div>', unsafe_allow_html=True)
    left,right=st.columns(2,gap="large")
    with left:
        st.markdown('''<div class="agent-card sql-card"><div class="agent-icon sql-icon">🗄️</div><div class="agent-title">SQL Agent</div><div class="agent-description">Ask questions about your database</div><div class="card-arrow sql-arrow">→</div></div>''',unsafe_allow_html=True)
        st.markdown('<div class="primary-sql">',unsafe_allow_html=True)
        st.button("Open SQL Agent  →",key="open_sql",on_click=open_sql,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown('''<div class="agent-card weather-card"><div class="agent-icon weather-icon">🌤️</div><div class="agent-title">Weather Agent</div><div class="agent-description">Get current weather for any city</div><div class="card-arrow weather-arrow">→</div></div>''',unsafe_allow_html=True)
        st.markdown('<div class="primary-weather">',unsafe_allow_html=True)
        st.button("Open Weather Agent  →",key="open_weather",on_click=open_weather,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)

def render_sql():
    a,b=st.columns([5,1])
    with a:
        st.markdown('<div class="workspace-heading">🗄️ SQL Agent</div><div class="workspace-subtitle">Ask questions about your connected database in natural language.</div>',unsafe_allow_html=True)
    with b: st.button("← Home",key="sql_home",on_click=go_home,use_container_width=True)
    with st.form("sql_query_form"):
        question=st.text_area("Your question",placeholder="Example: Find all employees working in the IT department",height=120)
        submitted=st.form_submit_button("Run SQL Agent",use_container_width=True)
    if submitted:
        if not question.strip(): st.warning("Please enter a database question.")
        else:
            with st.spinner("Agent Forge is analyzing your question..."):
                result=ask_sql_question(question.strip())
            if result.get("status")=="error": st.error(result.get("error","Something went wrong."))
            else:
                st.success(f"Status: {result.get('status','unknown')}")
                if result.get("final_answer"):
                    st.markdown("### Answer")
                    st.markdown(result["final_answer"])
                if result.get("generated_sql"):
                    with st.expander("Generated SQL",expanded=True): st.code(result["generated_sql"],language="sql")
                if result.get("validation_output"):
                    with st.expander("SQL checker output"): st.code(str(result["validation_output"]),language="sql")
                dataframe=result.get("dataframe")
                if dataframe is not None:
                    st.markdown("### Query results")
                    st.dataframe(dataframe,use_container_width=True)
                if result.get("status")=="no_sql": st.info("This request was answered without executing a database query.")

def render_weather():
    a,b=st.columns([5,1])
    with a:
        st.markdown('<div class="workspace-heading">🌤️ Weather Agent</div><div class="workspace-subtitle">Search a city to get its current weather conditions.</div>',unsafe_allow_html=True)
    with b: st.button("← Home",key="weather_home",on_click=go_home,use_container_width=True)
    cities=["Hyderabad","Bengaluru","Mumbai","Delhi","Chennai","Visakhapatnam","Pune","Kolkata","Warangal","Vijayawada","Ahmedabad","Jaipur","Kochi","London","New York","Tokyo","Singapore","Dubai","Paris","Sydney"]
    selected=st.selectbox("Search or select a city",["Choose a city..."]+cities+["Enter another city..."])
    custom=""
    if selected=="Enter another city...": custom=st.text_input("City name",placeholder="Type any city in the world")
    city=custom.strip() if selected=="Enter another city..." else selected
    with st.form("weather_form"): submitted=st.form_submit_button("Get Weather",use_container_width=True)
    if submitted:
        if not city or city=="Choose a city...": st.warning("Please select or enter a city.")
        else:
            with st.spinner(f"Fetching current weather for {city}..."):
                result=get_weather.invoke({"city":city})
            if result.startswith("Unable to") or "was not found" in result or "API returned an error" in result: st.error(result)
            else:
                st.markdown(f'''<div class="result-panel"><div style="font-size:1.05rem;color:#65708f">CURRENT WEATHER</div><div style="font-size:2rem;font-weight:800;color:#111b55;margin:.2rem 0">{city}</div><div style="white-space:pre-line;font-size:1.08rem;line-height:1.9;color:#27345f">{result}</div></div>''',unsafe_allow_html=True)

if st.session_state.page=="home": render_home()
elif st.session_state.page=="sql": render_sql()
elif st.session_state.page=="weather": render_weather()
