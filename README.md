# NeuroNotes: AI-Powered Study Companion 🧠✨
## 48-Hour Hackathon Project

## The Problem We Solved

As students, we've all struggled with inefficient note-taking and study methods. In just 48 hours, we built NeuroNotes to tackle this universal challenge!

## What We Built

**Smart Note-Taking:** Our AI generates well-structured notes from any topic or uploaded material - cutting hours of manual work down to seconds.

**Personalized Quiz Creation:** Transform study material into interactive quizzes with a single click to test your understanding.

**Web-Enhanced Learning:** Our AI searches the web for the most current information on your study topics, ensuring you're learning accurate content.

**Document-Based Learning:** Upload your lecture materials and our AI extracts the important information to create perfect study materials.

## Features Coming Soon

**Collections Organization:** We're building a system to organize notes by subject, course, or any category you choose.

**Collection-Based Quizzes:** Generate comprehensive quizzes that pull from multiple notes within a collection.

**Context-Aware Document Processing:** Upload multiple files to a collection and use that combined knowledge base to generate more comprehensive notes and quizzes.

**Smart Flashcards:** An adaptive flashcard system with SRS that evolves with your learning progress.

**Background Processing:** Large document handling with notifications when your study materials are ready.

**Create and Share:** Create and share your notes, quizzes and collections with your friends or peers (as PDFs, Zips, Texts or custom export format).

**Knowledgebase From Cloud:** Fetch knowledgebase from your Google Drive or Onedrive.


## Challenges We Faced

Given our 48-hour time constraint, we had to make tough choices:
- The automated categorization system still needs refinement.
- Some UI elements need polishing.
- Prioritization of core features and leaving application performance for later (like background processing).
- Prioritising automated quiz content generation over quiz name generation.


Despite these challenges, we're proud of what we accomplished in such a short time and committed to continuing development beyond this hackathon!

## Why NeuroNotes Matters

- **Time-Saving:** Reduces hours of note-taking to minutes.
- **Improved Learning:** Structures information for better retention.
- **Latest Information:** Integrates current web content with your personal materials.
- **Smarter Studying:** Personalized quiz creation targets knowledge gaps.

NeuroNotes represents what we believe education tools should be - intelligent, adaptive, and designed with real student needs in mind.


# Setup 
## Prerequisites

- Node.js (v16 or higher)
- Python 3.11 or higher
- PostgreSQL
- Redis
- pnpm (recommended) or npm
- ollama

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. Install dependencies using uv:
   ```bash
   uv pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your configuration:
   - Update database credentials
   - Set up email configuration
   - Add your Groq API key
   - Configure other environment variables as needed

5. Initialize the database:
   ```bash
   # Run database migrations
   alembic upgrade head
   ```

6. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   # Using pnpm (recommended)
   pnpm install
   
   # Or using npm
   npm install
   ```

3. Start the development server:
   ```bash
   # Using pnpm
   pnpm start
   
   # Or using npm
   npm start
   ```

## Additional Services

### PostgreSQL
Ensure PostgreSQL is running and create the database:
```bash
sudo -i -u postgres psql
CREATE DATABASE h4b;
```

## Project Structure

- `frontend/`: React application
  - `src/`: Source code
  - `public/`: Static files
- `backend/`: FastAPI application
  - `app/`: Main application code
  - `migrations/`: Database migrations
  - `alembic/`: Alembic configuration

## Environment Variables

Key environment variables to configure:

- `SQLALCHEMY_DATABASE_URI`: PostgreSQL connection string
- `GROQ_API_KEY`: For LLM
- `TAVILY_API_KEY`: For accessing web search

## Development

- Frontend runs on `http://localhost:3000`
- Backend API runs on `http://localhost:8000`

