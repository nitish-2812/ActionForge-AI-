# ⚡ ActionForge AI

**Meeting Notes to Strategy Engine**

ActionForge AI is an intelligent meeting-to-strategy platform built to automate the conversion of unstructured sales meeting notes into structured, executable action plans. The application uses a multi-step AI pipeline to sequentially process meeting notes through five specialized stages: summarization, task extraction, deadline detection, role assignment, and email generation.

## 🚀 Key Features

- **Multi-Stage API Pipeline:** Automatically generates Executive Summaries, Task Lists, Deadlines, Roles, and Follow-Up Emails.
- **Smart Task Extraction:** Detects action items, priority levels, and ownership directly from unstructured context.
- **Session Memory:** Retains meeting context to allow cross-meeting continuity and smart tracking.
- **Dual-Model Processing:** Backed by Groq's APIs, utilizing Llama 3.3 70B for deep analysis with automatic fallback options.
- **Audio Transcription:** Seamless audio upload using the Whisper API for immediate speech-to-text processing.
- **Data Exporting:** Instantly export generated action plans into clean PDF and CSV formats.

## 💻 Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **AI & LLM:** Groq API (Llama 3.3 70B), Prompt Engineering
- **Frontend:** HTML, CSS, JavaScript (Custom Modern Glassmorphism UI)

## 🛠️ Installation & Setup

**1. Clone the repository:**
```bash
git clone https://github.com/nitish-2812/ActionForge-AI-.git
cd ActionForge-AI-
```

**2. Set up a virtual environment:**
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
```

**3. Install Dependencies:**
Navigate to the backend directory and install:
```bash
cd backend
pip install -r requirements.txt
cd ..
```

**4. Set up Environment Variables:**
Create a `.env` file in the `backend/` folder using `.env.example` as a template:
```env
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
```

**5. Start the Application:**

**Start the Backend Server:**
In a terminal at the `backend/` folder:
```bash
uvicorn main:app --reload --port 8000
```

**Start the Frontend Client:**
In a separate terminal at the `frontend/` folder:
```bash
python -m http.server 5500
```

Navigate to `http://localhost:5500` in your web browser to interact with the engine!

## 📄 License
This project is open-source and created for academic documentation.
