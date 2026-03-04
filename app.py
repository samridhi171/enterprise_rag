import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from pypdf import PdfReader 
import sqlite3
import pandas as pd

st.set_page_config(page_title="Enterprise Data Assistant", layout="wide")

# --- CSS Injection ---
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass 

st.title("🧠 Box Office Analytics Platform")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Paste your Google API Key here (For AI Tab):", type="password")
    st.divider()
    st.header("📄 Document Viewer")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file is not None:
        pdf_reader = PdfReader(uploaded_file)
        st.success(f"✅ Successfully loaded: {uploaded_file.name}")
        with st.expander("👀 Preview Extracted Text"):
            st.write(pdf_reader.pages[0].extract_text()[:500] + "...")

# --- NEW: App Routing (Tabs) ---
tab1, tab2 = st.tabs(["💬 AI Copilot", "📊 Raw Data Dashboard"])

# ==========================================
# TAB 1: THE AI COPILOT (Needs API Key)
# ==========================================
with tab1:
    st.subheader("Chat with your Database")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    try:
        db = SQLDatabase.from_uri("sqlite:///enterprise.db")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if question := st.chat_input("Ask a question about the box office database..."):
            if not api_key:
                st.error("⚠️ Please enter your API key in the sidebar first!")
            else:
                st.session_state.messages.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.markdown(question)

                llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0)
                agent = create_sql_agent(llm, db=db, verbose=True, handle_parsing_errors=True)

                with st.chat_message("assistant"):
                    with st.spinner("Analyzing database..."):
                        try:
                            response = agent.invoke(question)
                            answer = response["output"]
                            st.markdown(answer)
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                        except Exception as e:
                            st.error(f"API Error or Quota Exceeded: {e}")

    except Exception as e:
        st.error(f"⚠️ Database Error: {e}")

# ==========================================
# TAB 2: THE OFFLINE DASHBOARD (No API Needed!)
# ==========================================
with tab2:
    st.subheader("Live Database Metrics")
    st.info("This dashboard runs locally on raw SQL. No API key required.")
    
    try:
        # Connect directly to the SQLite database
        conn = sqlite3.connect("enterprise.db")
        
        # Query 1: Get the top 10 highest grossing movies Worldwide
        df_top10 = pd.read_sql_query("SELECT Movie, Worldwide FROM company_data ORDER BY Worldwide DESC LIMIT 10", conn)
        
        # Query 2: Get a count of the Verdicts (Blockbuster, Flop, etc.)
        df_verdicts = pd.read_sql_query("SELECT Verdict, COUNT(*) as Count FROM company_data GROUP BY Verdict", conn)
        
        conn.close()

        # Display the data using Streamlit columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top 10 Movies Worldwide**")
            # Streamlit's built-in bar chart
            st.bar_chart(data=df_top10.set_index("Movie"))
            
        with col2:
            st.markdown("**Movie Verdict Breakdown**")
            # Displaying the raw data table
            st.dataframe(df_verdicts, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Could not load dashboard data: {e}")