import logging

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from src.services.jira_service import JiraService
from src.models.jira_models import (
    JiraCredentials,
    AuthResponse,
    ProjectsResponse,
    ProjectDetailsResponse
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI app with metadata
app = FastAPI(
    title="Jira Dashboard Backend API",
    description="Backend API for Jira Dashboard application providing authentication and project management features",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check endpoints"
        },
        {
            "name": "authentication",
            "description": "Jira authentication operations"
        },
        {
            "name": "projects",
            "description": "Jira project management operations"
        }
    ]
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get Jira service
def get_jira_service() -> JiraService:
    """Dependency to provide JiraService instance"""
    return JiraService()

@app.get(
    "/",
    tags=["health"],
    summary="Health Check",
    description="Check if the API is running and healthy"
)
def health_check():
    """
    Health check endpoint to verify API availability.
    
    Returns:
        dict: Health status message
    """
    return {"message": "Jira Dashboard Backend API is healthy", "status": "ok"}

# PUBLIC_INTERFACE
@app.post(
    "/api/auth/login",
    response_model=AuthResponse,
    tags=["authentication"],
    summary="Authenticate with Jira",
    description="Authenticate user with Jira using email, API token, and domain"
)
def authenticate_jira_user(
    credentials: JiraCredentials,
    jira_service: JiraService = Depends(get_jira_service)
) -> AuthResponse:
    """
    Authenticate user with Jira credentials.
    
    This endpoint verifies the user's Jira credentials by making a test API call
    to Jira's REST API. If successful, returns user information.
    
    Args:
        credentials: Jira authentication credentials (email, API token, domain)
        jira_service: Injected Jira service dependency
        
    Returns:
        AuthResponse: Authentication result with user information or error details
        
    Raises:
        HTTPException: For server errors during authentication
    """
    try:
        logger.info(f"Authentication attempt for user: {credentials.email} on domain: {credentials.domain}")
        
        result = jira_service.authenticate_user(
            email=credentials.email,
            api_token=credentials.api_token,
            domain=credentials.domain
        )
        
        if result['success']:
            logger.info(f"Authentication successful for user: {credentials.email}")
            return AuthResponse(**result)
        else:
            logger.warning(f"Authentication failed for user: {credentials.email} - {result['message']}")
            return AuthResponse(**result)
            
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Internal server error during authentication",
                "error_code": "INTERNAL_ERROR"
            }
        )

# PUBLIC_INTERFACE
@app.post(
    "/api/projects",
    response_model=ProjectsResponse,
    tags=["projects"],
    summary="Fetch User Projects",
    description="Fetch all Jira projects accessible to the authenticated user"
)
def get_user_projects(
    credentials: JiraCredentials,
    jira_service: JiraService = Depends(get_jira_service)
) -> ProjectsResponse:
    """
    Fetch all projects accessible to the authenticated user.
    
    This endpoint retrieves all Jira projects that the authenticated user has
    access to, including project details like name, key, description, and lead.
    
    Args:
        credentials: Jira authentication credentials
        jira_service: Injected Jira service dependency
        
    Returns:
        ProjectsResponse: List of projects with metadata or error details
        
    Raises:
        HTTPException: For server errors during project fetching
    """
    try:
        logger.info(f"Fetching projects for user: {credentials.email} on domain: {credentials.domain}")
        
        result = jira_service.fetch_user_projects(
            email=credentials.email,
            api_token=credentials.api_token,
            domain=credentials.domain
        )
        
        if result['success']:
            logger.info(f"Successfully fetched {result['total']} projects for user: {credentials.email}")
            return ProjectsResponse(**result)
        else:
            logger.warning(f"Failed to fetch projects for user: {credentials.email} - {result['message']}")
            return ProjectsResponse(**result)
            
    except Exception as e:
        logger.error(f"Unexpected error during project fetching: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Internal server error during project fetching",
                "error_code": "INTERNAL_ERROR"
            }
        )

# PUBLIC_INTERFACE
@app.post(
    "/api/projects/{project_key}",
    response_model=ProjectDetailsResponse,
    tags=["projects"],
    summary="Get Project Details",
    description="Get detailed information about a specific Jira project"
)
def get_project_details(
    project_key: str,
    credentials: JiraCredentials,
    jira_service: JiraService = Depends(get_jira_service)
) -> ProjectDetailsResponse:
    """
    Get detailed information about a specific project.
    
    This endpoint retrieves comprehensive details about a specific Jira project,
    including components, versions, issue types, and other metadata.
    
    Args:
        project_key: The key of the project to fetch details for
        credentials: Jira authentication credentials
        jira_service: Injected Jira service dependency
        
    Returns:
        ProjectDetailsResponse: Detailed project information or error details
        
    Raises:
        HTTPException: For server errors during project detail fetching
    """
    try:
        logger.info(f"Fetching details for project: {project_key} by user: {credentials.email}")
        
        result = jira_service.get_project_details(
            email=credentials.email,
            api_token=credentials.api_token,
            domain=credentials.domain,
            project_key=project_key
        )
        
        if result['success']:
            logger.info(f"Successfully fetched details for project: {project_key}")
            return ProjectDetailsResponse(**result)
        else:
            logger.warning(f"Failed to fetch details for project: {project_key} - {result['message']}")
            return ProjectDetailsResponse(**result)
            
    except Exception as e:
        logger.error(f"Unexpected error during project detail fetching: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Internal server error during project detail fetching",
                "error_code": "INTERNAL_ERROR"
            }
        )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "error_code": "INTERNAL_ERROR"
        }
    )

# Environment variable validation on startup
@app.on_event("startup")
async def startup_event():
    """Startup event to validate environment and log configuration"""
    logger.info("Starting Jira Dashboard Backend API")
    logger.info("Environment variables loaded successfully")
    
    # Log important configuration (without sensitive data)
    logger.info("API ready to accept requests")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event for cleanup"""
    logger.info("Shutting down Jira Dashboard Backend API")
