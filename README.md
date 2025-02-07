# Lean Six Sigma RAG Chatbot

A RAG-based AI chatbot system focused on Lean Six Sigma methodology, providing expert guidance, resources, and interactive support for LSS practitioners at all levels.

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs with Python 3.7+
- **SQLAlchemy**: SQL toolkit and ORM for database interactions
- **Alembic**: Database migration tool
- **Pydantic**: Data validation using Python type annotations
- **LangChain**: Framework for developing applications powered by language models
- **OpenAI**: For RAG implementation and text embeddings

### Frontend
- **React 18**: UI library for building user interfaces
- **TypeScript**: For type-safe code
- **Vite**: Next generation frontend tooling
- **Material-UI**: React UI framework for faster and easier web development
- **React Query**: For server state management
- **Zustand**: For client state management
- **React Router**: For application routing

### Databases
- **PostgreSQL**: Primary relational database
- **Weaviate**: Vector database for semantic search and RAG implementation

### Development & Testing
- **Docker**: For containerization and development environment
- **Pytest**: Backend testing framework
- **Vitest**: Frontend testing framework
- **ESLint & Black**: Code formatting and linting

## Project Structure

```
.
├── backend/
│   └── app/
│       ├── api/        # API routes
│       ├── core/       # Core functionality
│       ├── db/         # Database models and config
│       ├── models/     # Pydantic models
│       ├── schemas/    # Schema definitions
│       ├── services/   # Business logic
│       └── utils/      # Utility functions
├── frontend/
│   └── src/
│       ├── components/ # Reusable React components
│       ├── hooks/      # Custom React hooks
│       ├── pages/      # Page components
│       ├── services/   # API services
│       ├── store/      # State management
│       ├── types/      # TypeScript types
│       └── utils/      # Utility functions
└── knowledge_base/     # LSS content
    ├── methodologies/
    ├── tools/
    ├── case_studies/
    └── templates/
```

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Python 3.10+
- Node.js 18+
- PostgreSQL 15
- OpenAI API key

### Environment Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd lean6sigma
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

4. Install frontend dependencies:
```bash
cd frontend
npm install
```

5. Copy environment variables:
```bash
cp .env.example .env
```
Edit `.env` with your configuration values.

### Running the Application

1. Start the development environment:
```bash
docker-compose up -d
```

2. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

3. Start the frontend development server:
```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development Workflow

1. Backend Development:
   - Models are defined in `backend/app/models`
   - API routes are in `backend/app/api`
   - Business logic goes in `backend/app/services`

2. Frontend Development:
   - Components are in `frontend/src/components`
   - Pages are in `frontend/src/pages`
   - API calls are handled in `frontend/src/services`

3. Testing:
   - Backend: `pytest`
   - Frontend: `npm test`

## Environment Variables

Key environment variables required:

```env
# Backend
BACKEND_PORT=8000
DATABASE_URL=postgresql://user:password@localhost:5432/lean6sigma
WEAVIATE_URL=http://localhost:8080
OPENAI_API_KEY=your-openai-api-key

# Frontend
VITE_API_URL=http://localhost:8000
```

## Contributing

1. Create a new branch for your feature
2. Write tests for new functionality
3. Ensure all tests pass
4. Submit a pull request

## License

[License Type] - see LICENSE file for details

## Current Progress

- **Database Setup:**
  - PostgreSQL is configured and running using Docker Compose
  - Initial database migrations have been successfully created and applied using Alembic
  - Tables `users`, `chat_history`, and `alembic_version` are set up
  - Database connection pooling implemented for optimal performance

- **Authentication System:**
  - User registration and login endpoints fully implemented
  - JWT token generation and validation working
  - Token sharing across services implemented
  - Comprehensive error handling and logging added
  - Integration tests passing for auth endpoints

- **Frontend Development:**
  - Core layout with responsive design and navigation completed
  - Authentication pages (Login/Register) with form validation
  - Protected route handling and authentication state management
  - Documentation page with markdown rendering and search
  - Chat interface with real-time messaging and query limits
  - Profile page with user settings and password management
  - Material-UI components integrated for consistent design
  - React Query implemented for efficient data fetching
  - Cross-service token management working

- **Chat System:**
  - Basic RAG-based chatbot implementation with simulated responses
  - Chat endpoint (`/api/v1/chat/chat`) processes user queries
  - Chat history stored in database
  - Real-time query limit tracking and display
  - Integration tests passing for chat endpoints

- **Documentation System:**
  - Structured knowledge base organization completed
  - Comprehensive documentation templates created
  - Initial DMAIC methodology documentation added
  - Documentation API endpoints implemented:
    - List available documents (`/api/v1/docs/list`)
    - Retrieve document content (`/api/v1/docs/content/{path}`)
    - Support for both markdown and HTML rendered content
  - Integration tests passing for documentation endpoints

- **Testing Infrastructure:**
  - Integration tests implemented for all services
  - Test utilities and helpers created
  - Vitest configuration completed
  - GitHub Actions CI/CD setup pending

- **Free Tier Implementation:**
  - Query limiting functionality (10 queries per day)
  - Query count tracking with automatic daily reset
  - Endpoint to check remaining queries
  - Rate limiting with appropriate error messages

- **Next Steps:**
  - Implement RAG with actual OpenAI integration
  - Set up Weaviate for vector search
  - Add subscription management
  - Implement advanced analytics
  - Set up CI/CD pipeline
  - Add more LSS content to knowledge base 