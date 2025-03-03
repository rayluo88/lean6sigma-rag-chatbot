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

- **RAG Implementation:**
  - Core RAG service implemented with OpenAI integration
  - Weaviate vector store setup and configured
  - Document chunking and embedding pipeline
  - Context retrieval and response generation
  - Comprehensive error handling and logging
  - Token limit handling with fallbacks
  - Integration tests passing
  - Troubleshooting tools and diagnostics added

- **Database Setup:**
  - PostgreSQL is configured and running using Docker Compose
  - Initial database migrations have been successfully created and applied using Alembic
  - Tables `users`, `chat_history`, `subscription_plans`, and `user_subscriptions` are set up
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
  - Integration tests passing for all services

- **Chat System:**
  - RAG-based chatbot implementation completed
  - Chat endpoint (`/api/v1/chat/chat`) processes user queries
  - Chat history stored in database
  - Real-time query limit tracking and display
  - Integration tests passing for chat endpoints
  - Error handling and logging throughout
  - Token limit handling implemented
  - Diagnostic endpoints for troubleshooting

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
  - Test coverage for:
    - Authentication flows
    - Chat functionality
    - Documentation retrieval
    - RAG service operations
  - GitHub Actions CI/CD setup pending
  - Diagnostic tools for troubleshooting added

- **Free Tier Implementation:**
  - Query limiting functionality (10 queries per day)
  - Query count tracking with automatic daily reset
  - Endpoint to check remaining queries
  - Rate limiting with appropriate error messages

- **Subscription Management:**
  - Subscription plans model and database tables
  - User subscription tracking and management
  - Tiered access with different query limits
  - Subscription API endpoints:
    - List available plans (`/api/v1/subscription/plans`)
    - View current subscription (`/api/v1/subscription/my`)
    - Subscribe to a plan (`/api/v1/subscription/subscribe`)
    - Cancel subscription (`/api/v1/subscription/my/cancel`)
  - Admin endpoints for plan management
  - Payment processing integration (placeholder)
  - Free plan auto-assignment for new users

## Known Issues

- **RAG Service Connectivity:**
  - Intermittent issues with the RAG service response generation
  - Weaviate vector database is running correctly but may require additional configuration
  - OpenAI API integration may need troubleshooting in certain environments
  - Error handling in the RAG service may need enhancement for better diagnostics

- **Testing and Debugging:**
  - Added diagnostic endpoints and tools for troubleshooting
  - Enhanced logging for better error identification
  - Documented common issues and their solutions
  - Created step-by-step testing guide for all features

## Next Steps

- Add more LSS content to knowledge base
- Resolve RAG service connectivity issues
- Add advanced analytics
- Set up CI/CD pipeline
- Enhance error monitoring and logging
- Add user feedback collection
- Implement advanced visualization tools 