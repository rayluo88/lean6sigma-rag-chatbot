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
- **Gradio**: For building interactive UI components for the chatbot

### Frontend
- **React 18**: UI library for building user interfaces
- **TypeScript**: For type-safe code
- **Vite**: Next generation frontend tooling
- **Material-UI**: React UI framework for faster and easier web development
- **React Query**: For server state management
- **Zustand**: For client state management
- **React Router**: For application routing
- **Gradio**: Alternative web interface for the chatbot

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
│       └── gradio_ui.py # Gradio UI implementation
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

## Available Interfaces

The project provides two user interfaces:

1. **React Frontend (Production UI)**
   - URL: http://localhost:3000
   - Features:
     - Full authentication support
     - Integration with all app features
     - Material-UI based design
     - Query limit tracking
     - Chat history
     - User profile management
     - Subscription handling

2. **Gradio UI (Development/Testing Interface)**
   - URL: http://localhost:8000/chatbot
   - Features:
     - Direct RAG service integration
     - Quick testing interface
     - No authentication required
     - Simplified chat experience
     - Useful for development and debugging

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
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. Start the frontend development server:
```bash
cd frontend
npm run dev
```

The application will be available at:
- React Frontend: http://localhost:3000
- Gradio UI: http://localhost:8000/chatbot
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Current Status

### RAG Implementation
✅ Core RAG service with LangChain integration
✅ Weaviate vector store setup
✅ Document chunking and embedding pipeline
✅ Robust error handling with fallback mechanisms
✅ Automatic retries for API operations
✅ Fallback to direct LLM when Weaviate is unavailable
✅ Configurable timeouts and connection settings
✅ Comprehensive logging system

### User Interface
✅ Dual UI approach with React and Gradio
✅ React frontend with Material-UI components
✅ Gradio UI for development and testing
✅ Responsive design for both interfaces
✅ Cross-origin request handling
✅ Real-time chat interaction
✅ Source document display

### Authentication & Security
✅ JWT-based authentication
✅ User registration and login
✅ Query limit tracking
✅ Subscription management
✅ API key security
✅ Error handling and validation

### Database & Storage
✅ PostgreSQL integration
✅ Weaviate vector store
✅ Migration system
✅ Connection pooling
✅ Error recovery

### Development Tools
✅ Comprehensive logging
✅ Testing infrastructure
✅ Development server configuration
✅ Code formatting and linting
✅ API documentation

## Known Issues

- **Weaviate Connection**: 
  ✅ Fixed: Added robust error handling and retries
  ✅ Fixed: Implemented fallback to direct LLM
  ✅ Fixed: Configurable timeouts
  - Note: May need proper configuration in production

- **Frontend Integration**:
  ✅ Fixed: CORS configuration
  ✅ Fixed: Authentication flow
  ✅ Fixed: Real-time updates
  - Note: Consider WebSocket for streaming responses

## Next Steps

1. **RAG Improvements**
   - Implement streaming responses
   - Add more LSS content
   - Enhance context retrieval
   - Optimize embedding process

2. **UI Enhancements**
   - Add chat message streaming
   - Improve source document display
   - Add visualization tools
   - Enhance mobile responsiveness

3. **Infrastructure**
   - Set up CI/CD pipeline
   - Add monitoring and analytics
   - Implement caching
   - Optimize performance

4. **Documentation**
   - Add API usage examples
   - Improve setup guides
   - Add troubleshooting section
   - Document best practices

## Contributing

1. Create a new branch for your feature
2. Write tests for new functionality
3. Ensure all tests pass
4. Submit a pull request

## License

[License Type] - see LICENSE file for details 