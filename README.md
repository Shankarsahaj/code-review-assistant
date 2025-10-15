# 🚀 AI Code Review Assistant

Professional code review assistant powered by Google Gemini AI.

## Features
- Multi-language support (Python, JavaScript, Java, C, C++, C#, Go, Ruby)
- AI-powered code analysis with severity ratings
- Perfect code generation
- Security vulnerability detection
- Downloadable reports
- Modern glass-morphism UI

## Quick Start

### Local Development
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with your Gemini API key
4. Run: `uvicorn main:app --reload`
5. Open: `http://localhost:8000`

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `GEMINI_MODEL`: Model name (default: models/gemini-2.5-flash)

## Deployment

### Render (Free)
1. Fork this repository
2. Connect to Render
3. Set environment variable: `GEMINI_API_KEY`
4. Deploy automatically

### Railway (Free)
1. Connect GitHub repository
2. Set `GEMINI_API_KEY` environment variable
3. Deploy with one click

## Tech Stack
- **Backend**: FastAPI + SQLAlchemy
- **AI**: Google Gemini
- **Frontend**: Vanilla JS + Modern CSS
- **Database**: SQLite

## API Endpoints
- `POST /review/` - Analyze code files
- `GET /reports/` - List saved reports
- `GET /reports/{id}/download` - Download report

Built with ❤️ for developers"# code-review-assistant" 
