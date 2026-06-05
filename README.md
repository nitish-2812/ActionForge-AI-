<div align="center">

# 🔥 ActionForge AI

### Turn Meeting Chaos Into Actionable Strategy

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-actionforge--ai.netlify.app-orange?style=for-the-badge&logoColor=white)](https://actionforge-ai.netlify.app)
[![Netlify Status](https://api.netlify.com/api/v1/badges/actionforge-ai/deploy-status)](https://app.netlify.com/projects/actionforge-ai/deploys)

[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-6366f1?style=flat-square)](https://groq.com)
[![Netlify Functions](https://img.shields.io/badge/Netlify-Serverless-00C7B7?style=flat-square&logo=netlify&logoColor=white)](https://www.netlify.com)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=flat-square&logo=chartdotjs&logoColor=white)](https://www.chartjs.org)

**Paste your meeting notes → Get tasks, deadlines, assignments, and a follow-up email — all powered by a multi-step AI analysis pipeline.**

[**🚀 Try the Live Demo →**](https://actionforge-ai.netlify.app)

---

</div>

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📋 **Executive Summary** | AI generates a concise 2-3 sentence meeting summary |
| ✅ **Action Item Extraction** | Automatically identifies tasks with priority levels (High / Medium / Low) |
| ⏰ **Deadline Detection** | Converts relative dates ("ASAP", "next Tuesday") into actual calendar dates |
| 👥 **Role Assignment** | Maps tasks to specific team members mentioned in the notes |
| ✉️ **Follow-up Email** | Drafts a professional email with all action items and deadlines |
| 🧠 **Session Memory** | Maintains context across multiple meetings for continuity |
| 🎙️ **Audio Upload** | Upload meeting recordings — transcribed via OpenAI Whisper |
| 📊 **Analytics Dashboard** | Visual charts for priority distribution, urgency, and top assignees |
| 📥 **PDF & CSV Export** | Download action plans in PDF or CSV format |
| 🔍 **Smart Filtering** | Search and filter tasks by priority, owner, or keyword |
| 🤝 **Collaboration** | Register, login, create shared sessions, and share with teammates |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (HTML/JS)                     │
│              Tailwind CSS + Chart.js                      │
│         actionforge-ai.netlify.app                        │
└──────────────────────┬──────────────────────────────────┘
                       │ API Calls
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Netlify Serverless Functions                 │
│                                                          │
│  ┌──────────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ process_notes│  │  memory  │  │   export_csv      │  │
│  │              │  │          │  │                    │  │
│  │  5-step AI   │  │  GET /   │  │  POST → CSV file  │  │
│  │  pipeline    │  │  DELETE  │  │                    │  │
│  └──────┬───────┘  └──────────┘  └───────────────────┘  │
│         │                                                │
└─────────┼────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│                  Groq Cloud API                          │
│            LLaMA 3.3 70B Versatile                       │
│         (fallback: LLaMA 3.1 8B Instant)                 │
└─────────────────────────────────────────────────────────┘
```

### 🔄 AI Tool Pipeline (MCP-Style)

Each request runs through **5 sequential AI tools**, similar to the Model Context Protocol (MCP) pattern:

```
Meeting Notes
     │
     ▼
┌─────────────┐    ┌──────────────┐    ┌───────────────┐
│ 1. Summary  │───▶│ 2. Tasks     │───▶│ 3. Deadlines  │
│   Writer    │    │  Extractor   │    │  Detector     │
└─────────────┘    └──────────────┘    └───────┬───────┘
                                               │
     ┌─────────────────────────────────────────┘
     ▼
┌─────────────┐    ┌──────────────┐
│ 4. Role     │───▶│ 5. Email     │───▶ Final Action Plan
│  Assigner   │    │  Generator   │
└─────────────┘    └──────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- [Node.js](https://nodejs.org/) v18+
- [Groq API Key](https://console.groq.com) (free, no credit card needed)
- [OpenAI API Key](https://platform.openai.com/api-keys) *(optional — only for audio transcription)*

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/nitish-2812/ActionForge-AI-.git
cd ActionForge-AI-

# 2. Install dependencies
npm install

# 3. Set up environment variable
#    Create a .env file in the project root (or set in Netlify dashboard)
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# 4. Run with Netlify Dev (recommended — runs functions locally)
npx netlify dev
```

The app will be available at `http://localhost:8888`

### Running the Python Backend (Alternative)

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your API keys

# Run the server
uvicorn main:app --reload --port 8000
```

---

## 📁 Project Structure

```
actionforge/
├── frontend/
│   └── index.html            # Single-page application (HTML + JS + Tailwind)
│
├── backend/                   # Python FastAPI backend (for local dev)
│   ├── main.py               # API endpoints
│   ├── tools.py              # AI tool functions (summary, tasks, etc.)
│   ├── prompts.py            # LLM system prompts
│   ├── memory.py             # Session memory management
│   ├── models.py             # Pydantic data models
│   ├── export.py             # PDF & CSV export logic
│   ├── collaboration.py      # User auth & shared sessions
│   ├── llm.py                # Groq LLM client wrapper
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment variable template
│
├── netlify/
│   └── functions/             # Netlify serverless functions (JS)
│       ├── process_notes.js   # Main AI pipeline (5 tools)
│       ├── health.js          # Health check endpoint
│       ├── memory.js          # Memory status endpoint
│       └── export_csv.js      # CSV export endpoint
│
├── netlify.toml               # Netlify deployment config
├── package.json               # Node.js dependencies (groq-sdk)
└── .gitignore
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ Yes | Free API key from [console.groq.com](https://console.groq.com) |
| `OPENAI_API_KEY` | ❌ Optional | For audio transcription via Whisper API |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, JavaScript, Tailwind CSS, Chart.js |
| **Backend (Serverless)** | Netlify Functions (Node.js) |
| **Backend (Local)** | Python, FastAPI, Uvicorn |
| **AI Model** | LLaMA 3.3 70B via Groq (with 8B fallback) |
| **Audio** | OpenAI Whisper API |
| **Deployment** | Netlify (auto-deploy from GitHub) |

---

## 📸 How It Works

1. **Paste your meeting notes** into the text area (or upload an audio recording)
2. **Set the meeting date** for accurate deadline conversion
3. **Click "Generate Action Plan"** — watch the 6-step AI pipeline animate in real-time
4. **Review your results** across 5 tabs: Summary, Tasks, Deadlines, Roles, Email
5. **Export** as PDF or CSV, or **copy the email** directly to your clipboard
6. **Session memory** carries context forward for your next meeting

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ by [Nitish](https://github.com/nitish-2812)**

[🚀 Try ActionForge AI Live →](https://actionforge-ai.netlify.app)

</div>
