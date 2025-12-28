# MailAgent

<div align="center">

![MailAgent Logo](https://img.shields.io/badge/MailAgent-AI%20Powered-blue?style=for-the-badge)

**An intelligent local email assistant powered by Large Language Models**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-cyan.svg)](https://reactjs.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg)](https://tailwindcss.com/)

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Tech Stack](#-tech-stack)

</div>

---

## Overview

**MailAgent** is a local AI-powered email assistant that automatically classifies, summarizes, and generates responses for your Gmail emails. Unlike cloud-based solutions, MailAgent runs entirely on your machine, ensuring complete privacy and control over your data.

### Key Capabilities

- **Smart Email Classification**: Automatically categorize emails by importance (high/medium/low) and type (professional, personal, newsletter, etc.)
- **AI-Powered Summaries**: Get instant summaries of long email threads
- **Response Generation**: Generate 3 response variants (formal, casual, neutral) with a single click
- **Improved Sender Detection**: Smart detection of newsletter senders (Medium, GitHub, etc.)
- **100% Local**: Your emails never leave your machine
- **Dark Theme UI**: Modern, professional interface optimized for productivity

---

## Screenshot

<!-- DASHBOARD_SCREENSHOT_PLACEHOLDER: Add your dashboard screenshot here -->
<!--
<p align="center">
  <img src="docs/screenshots/dashboard.png" alt="MailAgent Dashboard" width="1200">
</p>
-->

---

## Features

### Email Management
- **Automatic Synchronization**: Fetch and sync recent and historical emails from Gmail
- **Smart Filtering**: Filter emails by status, importance, and category
- **Batch Processing**: Process multiple emails in parallel for efficiency

### AI-Powered Insights
- **Importance Detection**: Identify urgent emails automatically
- **Category Classification**: Organize emails into meaningful categories
- **Intelligent Summaries**: Get concise summaries of long email threads

### Response Generation
- **3-Option Variants**: Generate formal, casual, or neutral responses
- **Custom Signatures**: Automatically uses your Gmail name in responses
- **Editable Drafts**: Fine-tune AI-generated responses before sending
- **One-Click Sending**: Send responses directly through Gmail API

### User Interface
- **Modern Dark Theme**: Eye-friendly interface for extended use
- **3-Column Layout**: Email list | Email content | Response editor
- **Independent Scrolling**: Navigate emails and responses simultaneously
- **Real-time Status**: Monitor Gmail and LLM connection status

---

## Architecture

MailAgent follows a clean 3-tier architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌──────────────┬──────────────────┬──────────────────────┐ │
│  │  Email List  │   Email Detail    │  Response Editor    │ │
│  │  (w-96)      │   (flex-1)       │   (flex-1)          │ │
│  └──────────────┴──────────────────┴──────────────────────┘ │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP/REST API
┌──────────────────────────────┴──────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌─────────────────┬────────────────┬─────────────────────┐ │
│  │  Gmail Service │   LLM Service  │  Response Generator│ │
│  │  (OAuth2)       │   (LM Studio)  │  (Qwen2.5-7B)       │ │
│  └─────────────────┴────────────────┴─────────────────────┘ │
│  ┌─────────────────┬────────────────┬─────────────────────┐ │
│  │   Classifier   │    Database    │    Config           │ │
│  │  (AI-powered)  │   (SQLite)     │  (Pydantic)         │ │
│  └─────────────────┴────────────────┴─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Email Sync**: Gmail Service fetches emails via OAuth2
2. **Processing**: Classifier analyzes and categorizes each email
3. **Storage**: Email metadata stored in SQLite database
4. **User Action**: User selects an email and requests responses
5. **Generation**: LLM generates 3 response variants
6. **Review**: User edits and sends the chosen response

---

## Tech Stack

### Backend
- **FastAPI** (0.109.0): Modern, fast Python web framework
- **SQLAlchemy** (2.0.25): SQL toolkit and ORM
- **Google API Client** (2.116.0): Gmail API integration with OAuth2
- **httpx** (0.26.0): Async HTTP client for LLM communication
- **Pydantic** (2.5.3): Data validation using Python type annotations

### Frontend
- **React** (18.2.0): UI library
- **Vite** (5.0.11): Next-generation frontend tooling
- **TailwindCSS** (3.4.1): Utility-first CSS framework
- **Lucide React** (0.309.0): Beautiful & consistent icons
- **Axios** (1.6.5): Promise-based HTTP client

### AI/ML
- **LM Studio**: Local LLM inference server
- **Qwen2.5-7B-Instruct-1M**: 7B parameter model with 128k context
- **Quantization**: Q4_K_M (~4-5GB VRAM) for RTX 4070 Super compatibility

### Database
- **SQLite**: Lightweight, serverless database
- **Tables**: emails, responses, user_preferences, sync_history

---

## Installation

### Prerequisites

- **Python** 3.10 or higher
- **Node.js** 18 or higher
- **LM Studio** with Qwen2.5-7B-Instruct-1M loaded
- **Gmail API Credentials** (OAuth 2.0)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd mailagent
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt
```

### Step 3: Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the credentials JSON file
6. Save it as `credentials/gmail_credentials.json`

### Step 4: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### Step 5: Environment Configuration

Create a `.env` file in the root directory:

```env
# LM Studio Configuration
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
LM_STUDIO_MODEL=qwen2.5-7b-instruct-1m
LM_STUDIO_TIMEOUT=60

# Gmail API Configuration
GMAIL_CREDENTIALS_PATH=credentials/gmail_credentials.json
GMAIL_TOKEN_PATH=credentials/token.pickle

# Database
DATABASE_URL=sqlite:///data/emails.db

# Application Settings
SYNC_INTERVAL_MINUTES=15
MAX_EMAILS_PER_SYNC=50
RESPONSE_VARIANTS=3

# Allowed Origins (CORS)
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

---

## Usage

### Start LM Studio

1. Open LM Studio
2. Load **Qwen2.5-7B-Instruct-1M** model
3. Click **"Start Server"** (ensure it runs on port 1234)

### Start the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

### Start the Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at `http://localhost:5173`

### First Run

1. Open `http://localhost:5173` in your browser
2. Click **"Sync Emails"** to fetch your recent emails
3. Grant Gmail access permissions when prompted
4. Emails will be automatically classified and categorized
5. Select an email and click **"Generate AI Responses"**
6. Review, edit, and send responses

---

## Project Structure

```
mailagent/
├── backend/
│   ├── main.py                 # FastAPI application & routes
│   ├── gmail_service.py        # Gmail API integration
│   ├── llm_service.py          # LM Studio client
│   ├── classifier.py           # AI email classification
│   ├── response_generator.py   # Response generation
│   ├── database.py             # SQLAlchemy models & DB ops
│   └── config.py               # Configuration management
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── StatusBar.jsx   # Status bar with system info
│   │   │   ├── EmailList.jsx   # Email list with filters
│   │   │   ├── EmailDetail.jsx # Email content viewer
│   │   │   └── ResponseEditor.jsx  # Response editor
│   │   ├── services/api.js     # API service layer
│   │   ├── App.jsx             # Main application
│   │   └── main.jsx            # Entry point
│   ├── package.json
│   └── vite.config.js
├── data/
│   └── emails.db               # SQLite database
├── credentials/
│   ├── gmail_credentials.json  # Gmail OAuth credentials
│   └── token.pickle            # OAuth token storage
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | System status (Gmail/LLM connection) |
| `/api/sync` | POST | Sync recent emails |
| `/api/sync/historical` | POST | Sync historical emails |
| `/api/emails` | GET | List emails with filters |
| `/api/emails/{id}` | GET | Get email by ID |
| `/api/emails/{id}/responses` | GET | Get generated responses |
| `/api/emails/{id}/send` | POST | Send email response |
| `/api/stats` | GET | Email statistics |

---

## Configuration

### LLM Settings

Adjust LLM parameters in `backend/config.py`:

```python
LM_STUDIO_MAX_TOKENS_CLASSIFY = 500  # Tokens for classification
LM_STUDIO_MAX_TOKENS_RESPONSE = 2000  # Tokens for response generation
LM_STUDIO_TEMPERATURE = 0.7            # Creativity (0.0-1.0)
```

### Classification Rules

Modify classification behavior in `backend/classifier.py`:

- **Importance levels**: high, medium, low
- **Categories**: professionnel, personnel, newsletter, notification, urgent, commercial, administratif

### Response Tones

Customize response styles in `backend/response_generator.py`:

1. **Formal**: Professional and business-appropriate
2. **Casual**: Friendly and informal
3. **Neutral**: Balanced and approachable

---

## Development

### Adding New Features

1. **Backend**: Add routes in `main.py`, services in appropriate modules
2. **Frontend**: Add components in `src/components/`, connect via `api.js`
3. **Database**: Modify models in `database.py`

### Testing

```bash
# Backend tests (when implemented)
cd backend
pytest tests/

# Frontend tests (when implemented)
cd frontend
npm test
```

### Logging

Logs are stored in `logs/app.log` with levels:
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Failures requiring attention

---

## Troubleshooting

### LM Studio Connection Issues

```bash
# Check if LM Studio is running
curl http://localhost:1234/v1/models

# Expected output: Model information JSON
```

### Gmail Authentication Errors

- Verify `credentials/gmail_credentials.json` exists
- Check OAuth consent screen is configured
- Delete `credentials/token.pickle` and re-authenticate

### Database Errors

```bash
# Recreate database
rm data/emails.db
python -c "from backend.database import init_db; init_db()"
```

### Port Already in Use

```bash
# Kill process on port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 5173 (Windows)
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

---

## Roadmap

### Version 1.1 (Planned)
- [ ] Multi-language support (French, English, etc.)
- [ ] Email templates and custom signatures
- [ ] Attachment download and preview
- [ ] Full-text search across emails

### Version 2.0 (Future)
- [ ] Multi-account Gmail support
- [ ] Calendar integration for meeting scheduling
- [ ] Advanced analytics and reporting
- [ ] Plugin system for custom extensions

---

## Privacy & Security

- **Local-Only**: Your emails are processed locally and never sent to external APIs (except Gmail)
- **OAuth 2.0**: Secure Gmail authentication with token refresh
- **No Telemetry**: No usage data or analytics are collected
- **Open Source**: Full transparency and control over your data

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- **Qwen2.5** by Alibaba Cloud for the excellent LLM
- **LM Studio** for the local inference platform
- **Gmail API** by Google
- **FastAPI** and **React** communities

---

<div align="center">

**Built with ❤️ for privacy and productivity**

[⬆ Back to Top](#mailagent)

</div>
