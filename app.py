import streamlit as st
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent

st.set_page_config(page_title="Enterprise Data Assistant", layout="wide")
st.title("🧠 Enterprise Data Assistant (Agent Mode)")

api_key = st.text_input("Paste your Google API Key here:", type="password")

if "messages" not in st.session_state:
    st.session_state.messages = []

try:
    df = pd.read_csv("data.csv")
    
    with st.expander("📊 Click here to view raw data preview"):
        st.dataframe(df.head()) 

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if question := st.chat_input("Ask a question about your data..."):
        if not api_key:
            st.error("⚠️ Please enter your API key at the top first!")
        else:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            # --- NEW: Initialize the AI Agent ---
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0)
            
            # The agent is given permission to write and run pandas code to find the answer
            agent = create_pandas_dataframe_agent(llm, df, verbose=True, allow_dangerous_code=True, handle_parsing_errors=True)

            with st.chat_message("assistant"):
                with st.spinner("Writing code to analyze your data..."):
                    with st.spinner("Analyzing your data..."):
                      try:
                        # The agent runs the code and returns the exact answer
                        response = agent.invoke(question)
                        answer = response["output"]
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                      except Exception as e:
                        error_str = str(e)
                        # If LangChain panics over casual conversation, we catch it here:
                        if "Could not parse LLM output:" in error_str:
                            # We slice the text to extract Gemini's hidden friendly message
                            hidden_message = error_str.split("Could not parse LLM output:")[1].split("For troubleshooting")[0].strip()
                            hidden_message = hidden_message.strip("`").strip() # Clean up any weird formatting
                            
                            st.markdown(hidden_message)
                            st.session_state.messages.append({"role": "assistant", "content": hidden_message})
                        else:
                            # If it's a real error, we show it normally
                            st.error(f"Oops! The agent encountered an error: {e}")

except FileNotFoundError:
    st.error("⚠️ Oops! Make sure your CSV file is named exactly 'data.csv' and is in the same folder.")