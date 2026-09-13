# 🚀 LeadFlow AI

LeadFlow AI is an AI-powered lead generation and CRM platform designed to collect business opportunities from multiple live sources, qualify them using AI, rank them based on commercial potential, and manage them through a CRM dashboard.

## ✨ Features

- 🔎 Multi-source lead collection
- 🤖 AI-powered lead qualification
- 📊 Commercial lead scoring and ranking
- 🔄 Lead deduplication
- 🧠 AI-generated lead insights
- 📋 Lead management
- 👥 CRM pipeline management
- 📈 Analytics dashboard
- 🌐 Production scraper framework
- ❤️ Scraper health monitoring
- 🔄 Opportunity status revalidation
- 🛡️ Contact protection for closed opportunities
- ⚙️ Source and scraper management
- 📝 Notes and follow-up management
- 💰 Deal value tracking
- 📧 AI-assisted outreach generation

## 🏗️ Architecture

```text
Live Sources
     ↓
Production Scrapers
     ↓
Aggregator
     ↓
Deduplication
     ↓
AI Qualification
     ↓
Commercial Ranking
     ↓
Database
     ↓
FastAPI
     ↓
React CRM Dashboard
📂 Project Structure
LeadFlow-AI/
│
├── backend/
│
├── database/
│   └── leadflow.db
│
├── pipeline/
│
├── scraper/
│   ├── base/
│   │   ├── base_scraper.py
│   │   └── lead_model.py
│   ├── manager.py
│   ├── registry.py
│   └── aggregator.py
│
├── tests/
│
├── frontend/
│
├── requirements.txt
├── package.json
├── .env
├── .gitignore
└── README.md
🌐 Production Sources

LeadFlow AI supports production scraping/integration for sources including:

RSS feeds
GitHub
Hacker News
Dev.to
RemoteOK
Product Hunt
Freelancer

The scraper framework is designed so additional sources can be added through the scraper registry and manager.

📊 Lead Qualification

LeadFlow AI classifies opportunities according to commercial score:

Score	Classification
72+	HOT
60–71	WARM
45–59	MEDIUM
Below 45	LOW
🔄 Opportunity Status

LeadFlow AI tracks the lifecycle status of opportunities:

Status	Meaning
OPEN	Source confirms the opportunity is active
CLOSED	Source confirms the opportunity is closed
EXPIRED	Source confirms the opportunity has expired
REMOVED	Source confirms the opportunity has been removed
UNKNOWN	Source does not provide enough reliable lifecycle information

CRM status is maintained separately from opportunity status.

CRM Statuses
New
Contacted
Meeting Scheduled
Proposal Sent
Won
Lost
🛠️ Technology Stack
Backend
Python
FastAPI
SQLAlchemy
SQLite
AI/LLM integration
Production scraper framework
Frontend
React.js
JavaScript
Tailwind CSS
Vite
Development Tools
Git
GitHub
Python Virtual Environment
npm
👥 How to Get and Run LeadFlow AI

This section explains how another developer can download, configure, and run the LeadFlow AI project locally.

1. Install Prerequisites

Before running the project, install the following software.

Git

Install Git and verify:

git --version
Python

Install Python and verify:

python --version
Node.js and npm

Install Node.js and verify:

node --version
npm --version
2. Clone the Repository

Open PowerShell or Command Prompt and run:

git clone https://github.com/Shoaib3496/LeadFlow-AI.git

Then move into the project:

cd LeadFlow-AI
3. Open the Project

If you use Visual Studio Code:

code .

Or open the LeadFlow-AI folder manually in your preferred code editor.

4. Create a Python Virtual Environment

From the project root, create a virtual environment:

python -m venv venv

Activate it on Windows:

.\venv\Scripts\Activate.ps1

If PowerShell blocks script execution, you can use Command Prompt instead:

venv\Scripts\activate

After activation, your terminal should show something similar to:

(venv) PS C:\...\LeadFlow-AI>
5. Install Backend Dependencies

With the virtual environment activated:

pip install -r requirements.txt

Verify the FastAPI installation:

python -c "import fastapi; print('FastAPI installed successfully')"
6. Configure Environment Variables

Create a .env file in the project root if it does not already exist.

Configure the environment variables required by the project and the AI/provider integrations used by your local setup.

Do not commit private API keys, passwords, tokens, or other secrets to GitHub.

A typical .env file should contain the credentials/configuration required by the project's backend services.

7. Start the FastAPI Backend

From the project root, start the backend using the project's FastAPI entry point.

For example, if the application entry point is main.py:

uvicorn main:app --reload

The backend should start on:

http://127.0.0.1:8000

FastAPI documentation is available at:

http://127.0.0.1:8000/docs

Keep this terminal running.

8. Install Frontend Dependencies

Open a new terminal.

Navigate to the frontend directory:

cd LeadFlow-AI\frontend

Install the frontend dependencies:

npm install
9. Start the React Dashboard

From the frontend directory:

npm run dev

Vite will display the local development URL in the terminal.

It will normally look similar to:

http://localhost:5173

Keep this terminal running.

10. Open the Dashboard

Open the URL displayed by Vite in your browser.

Typically:

http://localhost:5173

The LeadFlow AI CRM dashboard should now be available.

🔌 Backend API

When the FastAPI backend is running, the API documentation can be accessed at:

http://127.0.0.1:8000/docs

This provides an interactive interface for testing the available API endpoints.

🗄️ Database

LeadFlow AI uses SQLite for local database storage.

The local database is stored under:

database/leadflow.db

The database contains application data such as leads and CRM-related information.

When cloning the repository on a new machine, the local database may need to be initialized by the application or populated through the project's pipeline.

🔄 Running the Lead Pipeline

LeadFlow AI includes a production pipeline that can:

Collect opportunities from configured sources.
Aggregate the collected leads.
Remove duplicates.
Evaluate buyer intent.
Evaluate lead fit.
Calculate commercial scoring.
Store qualified leads.
Revalidate existing opportunity statuses.

The exact pipeline behavior depends on the configured production sources and environment variables.

🧪 Running Tests

From the project root, activate the virtual environment and run:

pytest

To run a specific test:

pytest tests/test_opportunity_contact_protection.py
🔐 Security

Never commit the following to GitHub:

API keys
Passwords
Authentication tokens
Secret keys
Private credentials
Personal access tokens

Make sure sensitive configuration is stored in .env and that .env is included in .gitignore.

📝 Development Workflow

Recommended workflow:

Clone Repository
       ↓
Create Virtual Environment
       ↓
Install Backend Dependencies
       ↓
Configure Environment Variables
       ↓
Start FastAPI
       ↓
Install Frontend Dependencies
       ↓
Start React
       ↓
Open CRM Dashboard
👨‍💻 Author

Shoaib

GitHub:

https://github.com/Shoaib3496

Repository:

https://github.com/Shoaib3496/LeadFlow-AI