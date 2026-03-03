import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from pypdf import PdfReader  # NEW: Library to read PDFs

st.set_page_config(page_title="Enterprise Data Assistant", layout="wide")
st.title("🧠 Enterprise AI Assistant (SQL + RAG)")

# --- NEW: Sidebar for Configurations & Uploads ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Paste your Google API Key here:", type="password")
    
    st.divider() # Draws a neat line
    
    st.header("📄 Knowledge Base Upload")
    st.write("Upload PDF documents to give the AI more context.")
    
    # The drag-and-drop file uploader
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    
    if uploaded_file is not None:
        # We process the PDF locally (No API quota used!)
        pdf_reader = PdfReader(uploaded_file)
        num_pages = len(pdf_reader.pages)
        st.success(f"✅ Successfully loaded: {uploaded_file.name} ({num_pages} pages)")
        
        # Show a tiny preview of the extracted text to prove it works
        with st.expander("👀 Preview Extracted Text"):
            first_page_text = pdf_reader.pages[0].extract_text()
            st.write(first_page_text[:500] + "...")

# --- Existing Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

try:
    db = SQLDatabase.from_uri("sqlite:///enterprise.db")
    with st.expander("🗄️ Click here to view Database connection status"):
        st.write(f"**Connected Tables:** {db.get_usable_table_names()}")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # We update the placeholder text
    if question := st.chat_input("Ask a question about your database or documents..."):
        if not api_key:
            st.error("⚠️ Please enter your API key in the sidebar first!")
        else:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            # (The AI logic remains here, but we won't trigger it today to save quota!)
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0)
            agent = create_sql_agent(llm, db=db, verbose=True, handle_parsing_errors=True)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    try:
                        response = agent.invoke(question)
                        answer = response["output"]
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        error_str = str(e)
                        if "Could not parse LLM output:" in error_str:
                            hidden_message = error_str.split("Could not parse LLM output:")[1].split("For troubleshooting")[0].strip()
                            hidden_message = hidden_message.strip("`").strip() 
                            st.markdown(hidden_message)
                            st.session_state.messages.append({"role": "assistant", "content": hidden_message})
                        else:
                            st.error(f"Oops! The agent encountered an error: {e}")

except Exception as e:
    st.error(f"⚠️ Database Error: {e}")