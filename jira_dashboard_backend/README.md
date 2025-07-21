# Jira Dashboard Backend

FastAPI backend service for the Jira Dashboard application, providing secure authentication with Jira and project data fetching capabilities.

## Features

- **Jira Authentication**: Secure authentication using email, API token, and domain
- **Project Management**: Fetch and display user's accessible Jira projects
- **Error Handling**: Comprehensive error handling with informative feedback
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **CORS Support**: Configured for cross-origin requests from frontend

## API Endpoints

### Authentication
- `POST /api/auth/login` - Authenticate with Jira credentials

### Projects  
- `POST /api/projects` - Fetch all user projects
- `POST /api/projects/{project_key}` - Get detailed project information

### Health
- `GET /` - Health check endpoint

## Environment Variables

The following environment variables can be configured in the `.env` file:

```env
# Optional: Custom logging level (default: INFO)
LOG_LEVEL=INFO

# Optional: Custom API configuration
API_TIMEOUT=30
```

## Jira API Token Setup

To use this application, users need to generate a Jira API token:

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label (e.g., "Jira Dashboard")
4. Copy the generated token
5. Use this token along with your email and Jira domain in the login form

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Interactive API docs: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json

## Security Notes

- API tokens are not stored permanently
- All communication with Jira uses HTTPS
- Credentials are only held in memory during request processing
- CORS is configured - adjust origins for production use

## Error Handling

The API provides detailed error responses with:
- `success`: Boolean indicating request success
- `message`: Human-readable error description  
- `error_code`: Machine-readable error identifier
- Additional context when applicable

Common error codes:
- `INVALID_CREDENTIALS`: Invalid email/token combination
- `ACCESS_DENIED`: Insufficient permissions
- `TIMEOUT`: Request timeout
- `CONNECTION_ERROR`: Network connectivity issues
- `PROJECT_NOT_FOUND`: Project doesn't exist or no access
