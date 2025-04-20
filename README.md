# Hack4Bengal (JogaKhichuri)

This project consists of a React frontend and a FastAPI backend. Follow the instructions below to set up the project locally.

## Prerequisites

- Node.js (v16 or higher)
- Python 3.11 or higher
- PostgreSQL
- Redis
- pnpm (recommended) or npm

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
CREATE DATABASE h4b
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

