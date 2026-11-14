# Financial Crime Agentic Investigator

Agentic AI financial crime investigation system using **LangGraph + Groq + FastAPI + Streamlit**.

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # Linux/macOS:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your Groq API key to `.env`:
   ```env
   GROQ_API_KEY=your_groq_api_key
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

## Running the Project

Terminal 1 – Backend:
```bash
uvicorn app.main:app --reload
```

Terminal 2 – Frontend:
```bash
streamlit run ui/streamlit_app.py
```

Run tests:
```bash
pytest -v
```
