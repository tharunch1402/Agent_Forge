import re
from io import StringIO

import pandas as pd
import sqlglot
import streamlit as st

from agentforge.agents import build_agent
from traffic_map import render_traffic_map


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="MultiTool AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==================================================
# 2. WORKSPACE SETTINGS (one place for all agents)
# ==================================================

WORKSPACES = {
    "sql": {
        "icon": "🗄️",
        "title": "SQL Agent",
        "card_text": "Ask your database questions in plain English.",
        "description": "Ask questions about your database.",
        "placeholder": "Example: Find the top 5 highest-paid employees.",
        "instruction": (
            "The user is in the SQL Agent workspace. "
            "Use the SQL/database tools to answer the question. "
            "Do not use unrelated tools. "
        ),
    },
    "weather": {
        "icon": "🌤️",
        "title": "Weather Agent",
        "card_text": "Current weather and conditions for any city.",
        "description": "Ask questions about weather conditions.",
        "placeholder": "Example: What is the current weather in Bengaluru?",
        "instruction": (
            "The user is in the Weather Agent workspace. "
            "Use the weather tool to answer the question. "
            "Do not use unrelated tools. "
        ),
    },
    "traffic": {
        "icon": "🗺️",
        "title": "Traffic Agent",
        "card_text": "Live routes, travel times and traffic on a map.",
        "description": "Ask for a route — the fastest one is shown on the map.",
        "placeholder": (
            "Example: Find the fastest route from "
            "HSR Layout, Bengaluru to Electronic City, Bengaluru."
        ),
        "instruction": (
            "The user is in the Traffic Agent workspace. "
            "Extract the starting location and destination "
            "from the user's natural-language question. "
            "Use the TomTom traffic tool to calculate the route. "
            "Do not ask the user for separate location fields. "
        ),
    },
}


# ==================================================
# 3. CUSTOM CSS
# ==================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #F7F8FB; }

#MainMenu, footer, header { visibility: hidden; }

.block-container { max-width: 1100px; padding-top: 2.5rem; padding-bottom: 3rem; }

/* Homepage */
.main-title {
    font-size: 40px; font-weight: 800; color: #1E2235;
    text-align: center; letter-spacing: -1px; margin-bottom: 6px;
}
.main-subtitle {
    text-align: center; color: #6B7085; font-size: 15px; margin-bottom: 40px;
}

/* Agent cards (Streamlit adds the class st-key-<key> to keyed containers) */
div[class*="st-key-card_"] {
    background: #FFFFFF;
    border: 1px solid #E6E8EF !important; border-radius: 20px;
    padding: 26px 24px 22px;
    box-shadow: 0 2px 10px rgba(30, 34, 53, 0.04);
    transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}
div[class*="st-key-card_"]:hover {
    transform: translateY(-4px);
    border-color: #2563EB !important;
    box-shadow: 0 12px 28px rgba(37, 99, 235, 0.12);
}
.card-icon {
    width: 48px; height: 48px; border-radius: 14px; background: #EEF3FF;
    display: flex; align-items: center; justify-content: center; font-size: 24px;
    margin-bottom: 14px;
}
.card-title { font-size: 18px; font-weight: 700; color: #1E2235; margin-bottom: 4px; }
.card-text  { font-size: 14px; color: #6B7085; line-height: 1.55; min-height: 44px; margin-bottom: 8px; }

/* Blue accent for primary buttons (matches the route colour on the map) */
button[kind^="primary"] { background: #2563EB !important; border-color: #2563EB !important; color: #fff !important; }
button[kind^="primary"]:hover { background: #1D4ED8 !important; border-color: #1D4ED8 !important; }

/* Workspace */
.workspace-title { font-size: 28px; font-weight: 800; color: #1E2235; letter-spacing: -0.5px; }
.workspace-description { color: #6B7085; font-size: 14px; margin-bottom: 18px; }

div.stButton > button { border-radius: 10px; font-weight: 600; }

div[data-testid="stForm"] {
    background: #FFFFFF; padding: 20px;
    border: 1px solid #E6E8EF; border-radius: 16px;
}

div[data-testid="stMetric"] { background: #FFFFFF; }
</style>
""", unsafe_allow_html=True)


# ==================================================
# 4. AGENT
# ==================================================

@st.cache_resource
def load_agent():
    return build_agent()


def extract_answer(response):
    """Return the text of the last AI message."""
    for message in reversed(response.get("messages", [])):
        if getattr(message, "type", None) == "ai":
            content = message.content

            if isinstance(content, str) and content.strip():
                return content

            if isinstance(content, list):
                return "\n".join(
                    str(item.get("text", "")) if isinstance(item, dict) else str(item)
                    for item in content
                )

    return "The agent did not return a response."


def ask_agent(question, workspace):
    response = load_agent().invoke({
        "messages": [
            {"role": "user", "content": WORKSPACES[workspace]["instruction"] + question}
        ]
    })
    return extract_answer(response)


# ==================================================
# 4b. SQL AGENT: answer + generated SQL + retrieved data
# ==================================================

def format_sql(query):
    """Remove ```sql fences and lay the query out on separate lines."""
    if not query:
        return ""
    query = re.sub(r"^```(?:sql)?\s*|\s*```$", "", str(query).strip(), flags=re.IGNORECASE)
    try:
        return sqlglot.transpile(query, read="mysql", write="mysql", pretty=True)[0]
    except Exception:
        return query


def ask_sql_agent(question):
    """Run the agent and pull out the SQL it ran, the rows it got back and its answer."""
    response = load_agent().invoke({
        "messages": [
            {"role": "user", "content": WORKSPACES["sql"]["instruction"] + question}
        ]
    })

    sql_query = None      # query sent to execute_sql (the one that actually ran)
    checked_query = None  # query sent to the SQL checker (used if nothing was executed)
    raw_result = None     # JSON returned by execute_sql

    for message in response["messages"]:
        for tool_call in getattr(message, "tool_calls", None) or []:
            if tool_call["name"] == "execute_sql":
                sql_query = tool_call["args"].get("query")
            elif tool_call["name"] == "sql_db_query_checker":
                checked_query = tool_call["args"].get("query")

        if getattr(message, "name", None) == "execute_sql":
            raw_result = message.content

    data = None
    if raw_result and not str(raw_result).startswith("Error"):
        try:
            data = pd.read_json(StringIO(raw_result), orient="split")
        except ValueError:
            data = None

    return {
        "question": question,
        "answer": extract_answer(response),
        "sql": format_sql(sql_query or checked_query),
        "data": data,
        "sql_error": raw_result if raw_result and str(raw_result).startswith("Error") else None,
    }


# ==================================================
# 5. ORIGIN / DESTINATION FROM THE QUESTION
# ==================================================

# Stop only at ? ! ; or end of line, so "Electronic City, Bengaluru" keeps its city
_END = r"\s*(?:[?!;\n]|$)"

ROUTE_PATTERNS = [
    rf"\bfrom\s+(?P<origin>.+?)\s+to\s+(?P<destination>.+?){_END}",
    rf"\bbetween\s+(?P<origin>.+?)\s+and\s+(?P<destination>.+?){_END}",
    rf"\bto\s+(?P<destination>.+?)\s+from\s+(?P<origin>.+?){_END}",
]


def extract_route_locations(question):
    """
    Supports questions like:
      - Find the fastest route from HSR Layout, Bengaluru to Electronic City, Bengaluru.
      - Route between Koramangala and Whitefield
      - How long to Airport from MG Road?
    """
    for pattern in ROUTE_PATTERNS:
        match = re.search(pattern, question, flags=re.IGNORECASE)

        if match:
            origin = match.group("origin").strip(" .,")
            destination = match.group("destination").strip(" .,")

            if origin and destination:
                return origin, destination

    return None, None


# ==================================================
# 6. SESSION STATE
# ==================================================

if "answers" not in st.session_state:
    st.session_state.answers = {name: None for name in WORKSPACES}


# ==================================================
# 7. HOMEPAGE
# ==================================================

def open_workspace(name):
    st.query_params["workspace"] = name


def show_homepage():
    st.markdown('<div class="main-title">MultiTool AI Agent</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">One platform. Multiple specialised AI agents.</div>',
        unsafe_allow_html=True,
    )

    columns = st.columns(len(WORKSPACES), gap="medium")

    for column, (name, ws) in zip(columns, WORKSPACES.items()):
        with column, st.container(key=f"card_{name}"):
            st.markdown(
                f'<div class="card-icon">{ws["icon"]}</div>'
                f'<div class="card-title">{ws["title"]}</div>'
                f'<div class="card-text">{ws["card_text"]}</div>',
                unsafe_allow_html=True,
            )
            st.button(
                "Open →",
                key=f"open_{name}",
                on_click=open_workspace,
                args=(name,),
                type="primary",
                width="stretch",
            )


# ==================================================
# 8. WORKSPACE
# ==================================================

def go_home():
    st.query_params.clear()


def show_workspace(workspace):
    ws = WORKSPACES[workspace]

    st.button("← Back", key="back_home", on_click=go_home)

    st.markdown(
        f'<div class="workspace-title">{ws["icon"]} {ws["title"]}</div>'
        f'<div class="workspace-description">{ws["description"]}</div>',
        unsafe_allow_html=True,
    )

    # Question form
    with st.form(key=f"{workspace}_form", border=False):
        question = st.text_area(
            "Ask your question",
            placeholder=ws["placeholder"],
            height=100,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Ask Agent", type="primary", width="stretch")

    if submitted:
        handle_question(question.strip(), workspace)

    show_answer(workspace)


def handle_question(question, workspace):
    if not question:
        st.warning("Please enter your question.")
        return

    origin = destination = None

    if workspace == "traffic":
        origin, destination = extract_route_locations(question)

        if not origin or not destination:
            st.warning(
                "Please mention both places, e.g. "
                "“from HSR Layout, Bengaluru to Electronic City, Bengaluru”."
            )
            return

    if workspace == "sql":
        try:
            with st.spinner("Writing and running the SQL query..."):
                st.session_state.answers["sql"] = ask_sql_agent(question)
        except Exception as error:
            st.error(f"Something went wrong: {error}")
        return

    try:
        with st.spinner("Your AI agent is working..."):
            answer = ask_agent(question, workspace)
    except Exception as error:
        st.error(f"Something went wrong: {error}")
        return

    st.session_state.answers[workspace] = {
        "question": question,
        "answer": answer,
        "origin": origin,
        "destination": destination,
    }


def show_answer(workspace):
    result = st.session_state.answers[workspace]

    if not result:
        return

    st.write("")

    if workspace == "sql":
        show_sql_answer(result)
    elif workspace == "traffic":
        st.markdown(f"**{result['origin']}**  →  **{result['destination']}**")
        render_traffic_map(result["origin"], result["destination"])

        with st.container(border=True):
            st.markdown("##### 🤖 Agent summary")
            st.markdown(result["answer"])
    else:
        with st.container(border=True):
            st.caption(result["question"])
            st.markdown(result["answer"])


def show_sql_answer(result):
    # 1. Answer
    with st.container(border=True):
        st.markdown("##### 🤖 Answer")
        st.caption(result["question"])
        st.markdown(result["answer"])

    # 2. Generated SQL (copy button appears at the top-right of the box)
    st.markdown("##### 🧾 Generated SQL query")
    if result["sql"]:
        st.code(result["sql"], language="sql")
    else:
        st.info("No SQL query was needed for this question.")

    if result["sql_error"]:
        st.error(result["sql_error"])

    # 3. Retrieved data
    data = result["data"]
    if data is not None:
        rows = len(data)
        st.markdown(f"##### 📊 Retrieved data · {rows} row{'s' if rows != 1 else ''}")
        if rows:
            st.dataframe(data, hide_index=True)
        else:
            st.info("The query ran successfully but returned no rows.")


# ==================================================
# 9. ROUTING
# ==================================================

workspace = st.query_params.get("workspace")

if workspace in WORKSPACES:
    show_workspace(workspace)
else:
    show_homepage()