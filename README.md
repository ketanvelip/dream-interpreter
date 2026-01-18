# Dream Interpreter with Symbolic Analysis

An AI-powered dream interpretation application that analyzes dreams and provides symbolic meanings using OpenAI's API. Built with FastAPI, React, PostgreSQL, and Docker.

## Features

- 🌙 **Dream Journal**: Record and store your dreams with detailed descriptions
- ✨ **AI-Powered Analysis**: Get comprehensive interpretations using OpenAI GPT-4
- 🔮 **Symbol Extraction**: Identify key symbols and their meanings
- 😊 **Emotion Tracking**: Tag dreams with emotions you experienced
- 📊 **Pattern Recognition**: Analyze recurring themes across multiple dreams
- 💬 **Follow-up Chat**: Ask questions about your dream interpretations
- 💾 **Persistent Storage**: All dreams saved to PostgreSQL database
- 🎨 **Modern UI**: Beautiful, responsive interface with gradient design

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **OpenAI API**: GPT-4 for dream analysis
- **PostgreSQL**: Database for storing dreams
- **SQLAlchemy**: ORM for database operations

### Frontend
- **React**: UI framework
- **Lucide React**: Modern icon library
- **Axios**: HTTP client
- **date-fns**: Date formatting

### Infrastructure
- **Docker & Docker Compose**: Containerization
- **Nginx**: Frontend web server

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd dream-interpreter
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Run with Docker

```bash
docker-compose up --build
```

This will:
- Build and start the PostgreSQL database
- Build and start the FastAPI backend on port 8000
- Build and start the React frontend on port 3000

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Usage

### Recording a Dream

1. Click on "New Dream" tab
2. Enter a title for your dream
3. Describe your dream in detail
4. Select emotions you felt during the dream
5. Click "Analyze Dream"
6. View the AI-generated interpretation and symbolic analysis

### Viewing Dream Journal

1. Click on "Dream Journal" tab
2. Browse all your recorded dreams
3. Click on any dream to view its full interpretation
4. Delete dreams you no longer want to keep

### Analyzing Patterns

1. Record at least 2 dreams
2. Click on "Patterns" tab
3. View recurring themes, symbols, and emotional patterns
4. Get insights about your subconscious state

### Asking Follow-up Questions

1. After analyzing a dream, click "Ask Follow-up Questions"
2. Type your question about the dream interpretation
3. Get personalized insights from the AI
4. Continue the conversation to explore deeper meanings
5. All chat history is saved with your dream

## API Endpoints

### Dreams

- `POST /dreams` - Create and analyze a new dream
- `GET /dreams/{user_id}` - Get all dreams for a user
- `GET /dreams/{user_id}/{dream_id}` - Get a specific dream
- `DELETE /dreams/{dream_id}` - Delete a dream

### Patterns

- `GET /dreams/{user_id}/patterns` - Analyze patterns across user's dreams

### Chat

- `POST /dreams/{dream_id}/chat` - Send a follow-up question about a dream
- `GET /dreams/{dream_id}/chat` - Get chat history for a dream

### Health

- `GET /health` - Health check endpoint
- `GET /` - API information

## Development

### Running Backend Locally

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your OPENAI_API_KEY to .env
uvicorn api:app --reload
```

### Running Frontend Locally

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env if needed
npm start
```

### Database Access

Connect to PostgreSQL:

```bash
docker-compose exec db psql -U dreamuser -d dreamdb
```

## Project Structure

```
dream-interpreter/
├── backend/
│   ├── api.py              # FastAPI application
│   ├── database.py         # Database models (Dream, ChatMessage)
│   ├── dream_analyzer.py   # OpenAI integration
│   ├── init_db.py          # Database initialization script
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Styles
│   ├── public/
│   │   └── index.html      # HTML template
│   ├── package.json        # Node dependencies
│   ├── Dockerfile          # Frontend container
│   ├── nginx.conf          # Nginx configuration
│   └── .env.example        # Environment variables template
├── docker-compose.yml      # Docker orchestration
├── .env.example            # Root environment variables
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## How It Works

### Dream Analysis Flow

1. **User Input**: User submits dream description and emotions
2. **API Request**: Frontend sends POST request to `/dreams` endpoint
3. **OpenAI Processing**: 
   - Backend calls OpenAI GPT-4 with specialized prompts
   - Generates comprehensive interpretation
   - Extracts key symbols and their meanings
4. **Database Storage**: Dream and analysis saved to PostgreSQL
5. **Response**: Full interpretation returned to user

### Pattern Analysis

1. **Data Collection**: Retrieves user's recent dreams from database
2. **AI Analysis**: OpenAI analyzes dreams collectively for patterns
3. **Insights**: Identifies recurring themes, symbols, and emotional patterns

### Follow-up Chat

1. **Context Loading**: Retrieves dream details and interpretation
2. **Conversation History**: Loads previous chat messages for context
3. **AI Response**: GPT-4 generates personalized answers based on dream context
4. **Storage**: All messages saved to database for future reference

## OpenAI API Usage

This application uses the OpenAI Responses API. Key features:

- **Model**: GPT-5 Mini (`gpt-5-mini`)
- **Temperature**: 0.7 for creative yet coherent interpretations
- **Instructions-based**: Uses system instructions for consistent behavior
- **JSON Mode**: Used for structured symbol extraction
- **Context Management**: Maintains conversation history for follow-up questions
- **Response Storage**: Responses are stored for potential future analysis
- **Specialized Instructions**: Tailored for dream analysis and symbolic interpretation

## Troubleshooting

### Backend won't start
- Check if OpenAI API key is set correctly in `.env`
- Ensure PostgreSQL is running: `docker-compose ps`
- Check logs: `docker-compose logs backend`

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check REACT_APP_API_URL in frontend/.env
- Check browser console for CORS errors

### Database connection issues
- Wait for database health check to pass
- Check DATABASE_URL in backend environment
- Restart services: `docker-compose restart`

### Data not persisting after reload
- Data is stored in Docker volumes and persists between restarts
- User ID is stored in browser localStorage
- To completely reset: `docker-compose down -v` (WARNING: deletes all data)
- To backup data: `docker-compose exec db pg_dump -U dreamuser dreamdb > backup.sql`

## Security Notes

- Never commit `.env` files with real API keys
- Keep your OpenAI API key secure
- Use environment variables for sensitive data
- In production, use proper authentication and authorization

## Future Enhancements

- User authentication and multi-user support
- Dream sharing and community features
- Advanced visualization of dream patterns
- Export dreams to PDF
- Mobile app version
- Voice input for dream recording
- Dream reminders and notifications
- Image generation for dream scenes
- Integration with sleep tracking apps

## License

MIT License - Feel free to use and modify for your projects

## Support

For issues or questions, please check:
- OpenAI API documentation: https://platform.openai.com/docs
- FastAPI documentation: https://fastapi.tiangolo.com
- React documentation: https://react.dev

---

Built with ❤️ using OpenAI, FastAPI, and React
