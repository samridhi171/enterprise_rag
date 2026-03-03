#!/bin/bash
# Enterprise RAG & SQL Copilot - Deployment Script

echo "🚀 Starting Enterprise AI Assistant Setup..."

# Check if the virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the environment (Linux/Mac style for servers)
source venv/bin/activate

echo "📥 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Launch the Streamlit application
echo "🟢 Launching application..."
streamlit run app.py