from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any

class JiraCredentials(BaseModel):
    """Model for Jira authentication credentials"""
    email: EmailStr = Field(..., description="User's Jira email address")
    api_token: str = Field(..., min_length=1, description="User's Jira API token")
    domain: str = Field(..., min_length=1, description="Jira domain (e.g., 'mycompany' or 'https://mycompany.atlassian.net')")

class UserInfo(BaseModel):
    """Model for authenticated user information"""
    email: str = Field(..., description="User's email address")
    display_name: str = Field(..., description="User's display name")
    account_id: str = Field(..., description="User's Jira account ID")
    domain: str = Field(..., description="Jira domain")

class AuthResponse(BaseModel):
    """Model for authentication response"""
    success: bool = Field(..., description="Whether authentication was successful")
    message: str = Field(..., description="Authentication result message")
    user: Optional[UserInfo] = Field(None, description="User information if authentication successful")
    error_code: Optional[str] = Field(None, description="Error code if authentication failed")

class ProjectLead(BaseModel):
    """Model for project lead information"""
    display_name: str = Field(..., description="Lead's display name")
    email: str = Field(..., description="Lead's email address")

class IssueType(BaseModel):
    """Model for issue type information"""
    id: str = Field(..., description="Issue type ID")
    name: str = Field(..., description="Issue type name")
    description: str = Field(..., description="Issue type description")
    icon_url: Optional[str] = Field(None, description="Issue type icon URL")

class ProjectComponent(BaseModel):
    """Model for project component information"""
    id: str = Field(..., description="Component ID")
    name: str = Field(..., description="Component name")
    description: str = Field(..., description="Component description")
    lead: str = Field(..., description="Component lead name")

class ProjectVersion(BaseModel):
    """Model for project version information"""
    id: str = Field(..., description="Version ID")
    name: str = Field(..., description="Version name")
    description: str = Field(..., description="Version description")
    released: bool = Field(..., description="Whether version is released")
    release_date: Optional[str] = Field(None, description="Release date")

class Project(BaseModel):
    """Model for project information"""
    id: str = Field(..., description="Project ID")
    key: str = Field(..., description="Project key")
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    lead: Optional[ProjectLead] = Field(None, description="Project lead information")
    project_type: str = Field(..., description="Project type")
    url: str = Field(..., description="Project API URL")
    avatar_urls: Dict[str, str] = Field(default_factory=dict, description="Project avatar URLs")
    category: str = Field(..., description="Project category")
    created_date: Optional[str] = Field(None, description="Project creation date")
    issue_types: List[IssueType] = Field(default_factory=list, description="Project issue types")

class ProjectDetails(Project):
    """Extended model for detailed project information"""
    components: List[ProjectComponent] = Field(default_factory=list, description="Project components")
    versions: List[ProjectVersion] = Field(default_factory=list, description="Project versions")

class ProjectsResponse(BaseModel):
    """Model for projects list response"""
    success: bool = Field(..., description="Whether request was successful")
    projects: List[Project] = Field(default_factory=list, description="List of projects")
    total: int = Field(..., description="Total number of projects")
    message: str = Field(..., description="Response message")
    error_code: Optional[str] = Field(None, description="Error code if request failed")

class ProjectDetailsResponse(BaseModel):
    """Model for project details response"""
    success: bool = Field(..., description="Whether request was successful")
    project: Optional[ProjectDetails] = Field(None, description="Detailed project information")
    message: str = Field(..., description="Response message")
    error_code: Optional[str] = Field(None, description="Error code if request failed")

class ErrorResponse(BaseModel):
    """Model for error responses"""
    success: bool = Field(False, description="Always false for error responses")
    message: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
