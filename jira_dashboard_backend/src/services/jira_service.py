import requests
from typing import Dict, Any
import base64
import logging

logger = logging.getLogger(__name__)

class JiraService:
    """Service class for interacting with Jira REST API"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def _get_auth_header(self, email: str, api_token: str) -> str:
        """Create base64 encoded authorization header for Jira API"""
        auth_string = f"{email}:{api_token}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return f"Basic {encoded_auth}"
    
    def _get_base_url(self, domain: str) -> str:
        """Construct base URL for Jira instance"""
        if not domain.startswith('http'):
            return f"https://{domain}.atlassian.net"
        return domain
    
    # PUBLIC_INTERFACE
    def authenticate_user(self, email: str, api_token: str, domain: str) -> Dict[str, Any]:
        """
        Authenticate user with Jira using email, API token, and domain.
        
        Args:
            email: User's Jira email
            api_token: User's Jira API token
            domain: Jira domain (e.g., 'mycompany' or 'https://mycompany.atlassian.net')
            
        Returns:
            Dict with authentication result and user info
        """
        try:
            base_url = self._get_base_url(domain)
            auth_header = self._get_auth_header(email, api_token)
            
            # Test authentication by fetching user profile
            headers = {
                'Authorization': auth_header,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(
                f"{base_url}/rest/api/3/myself",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'success': True,
                    'message': 'Authentication successful',
                    'user': {
                        'email': user_data.get('emailAddress'),
                        'display_name': user_data.get('displayName'),
                        'account_id': user_data.get('accountId'),
                        'domain': domain
                    },
                    'credentials': {
                        'email': email,
                        'api_token': api_token,
                        'domain': domain,
                        'base_url': base_url
                    }
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'message': 'Invalid credentials. Please check your email and API token.',
                    'error_code': 'INVALID_CREDENTIALS'
                }
            elif response.status_code == 403:
                return {
                    'success': False,
                    'message': 'Access denied. Please check your API token permissions.',
                    'error_code': 'ACCESS_DENIED'
                }
            else:
                logger.error(f"Authentication failed with status {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'message': f'Authentication failed: {response.status_code}',
                    'error_code': 'AUTH_FAILED'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': 'Request timeout. Please check your domain and try again.',
                'error_code': 'TIMEOUT'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'message': 'Connection error. Please check your domain and internet connection.',
                'error_code': 'CONNECTION_ERROR'
            }
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            return {
                'success': False,
                'message': 'An unexpected error occurred during authentication.',
                'error_code': 'UNKNOWN_ERROR'
            }
    
    # PUBLIC_INTERFACE
    def fetch_user_projects(self, email: str, api_token: str, domain: str) -> Dict[str, Any]:
        """
        Fetch all projects accessible to the authenticated user.
        
        Args:
            email: User's Jira email
            api_token: User's Jira API token
            domain: Jira domain
            
        Returns:
            Dict with projects data and metadata
        """
        try:
            base_url = self._get_base_url(domain)
            auth_header = self._get_auth_header(email, api_token)
            
            headers = {
                'Authorization': auth_header,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Fetch projects with expanded details
            response = self.session.get(
                f"{base_url}/rest/api/3/project/search",
                headers=headers,
                params={
                    'expand': 'description,lead,url,projectKeys,issueTypes',
                    'maxResults': 100  # Adjust as needed
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                projects = []
                
                for project in data.get('values', []):
                    project_info = {
                        'id': project.get('id'),
                        'key': project.get('key'),
                        'name': project.get('name'),
                        'description': project.get('description', ''),
                        'lead': {
                            'display_name': project.get('lead', {}).get('displayName', 'Unknown'),
                            'email': project.get('lead', {}).get('emailAddress', '')
                        } if project.get('lead') else None,
                        'project_type': project.get('projectTypeKey', 'Unknown'),
                        'url': project.get('self'),
                        'avatar_urls': project.get('avatarUrls', {}),
                        'category': project.get('projectCategory', {}).get('name', 'Uncategorized') if project.get('projectCategory') else 'Uncategorized',
                        'created_date': project.get('created'),
                        'issue_types': [
                            {
                                'id': it.get('id'),
                                'name': it.get('name'),
                                'description': it.get('description', ''),
                                'icon_url': it.get('iconUrl')
                            }
                            for it in project.get('issueTypes', [])
                        ]
                    }
                    projects.append(project_info)
                
                return {
                    'success': True,
                    'projects': projects,
                    'total': len(projects),
                    'message': f'Successfully fetched {len(projects)} projects'
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'message': 'Authentication failed. Please re-authenticate.',
                    'error_code': 'AUTH_EXPIRED'
                }
            elif response.status_code == 403:
                return {
                    'success': False,
                    'message': 'Access denied. You may not have permission to view projects.',
                    'error_code': 'ACCESS_DENIED'
                }
            else:
                logger.error(f"Failed to fetch projects with status {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'message': f'Failed to fetch projects: {response.status_code}',
                    'error_code': 'FETCH_FAILED'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': 'Request timeout while fetching projects.',
                'error_code': 'TIMEOUT'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'message': 'Connection error while fetching projects.',
                'error_code': 'CONNECTION_ERROR'
            }
        except Exception as e:
            logger.error(f"Unexpected error while fetching projects: {str(e)}")
            return {
                'success': False,
                'message': 'An unexpected error occurred while fetching projects.',
                'error_code': 'UNKNOWN_ERROR'
            }
    
    # PUBLIC_INTERFACE
    def get_project_details(self, email: str, api_token: str, domain: str, project_key: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific project.
        
        Args:
            email: User's Jira email
            api_token: User's Jira API token
            domain: Jira domain
            project_key: Project key to fetch details for
            
        Returns:
            Dict with detailed project information
        """
        try:
            base_url = self._get_base_url(domain)
            auth_header = self._get_auth_header(email, api_token)
            
            headers = {
                'Authorization': auth_header,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Fetch detailed project information
            response = self.session.get(
                f"{base_url}/rest/api/3/project/{project_key}",
                headers=headers,
                params={
                    'expand': 'description,lead,url,projectKeys,issueTypes,versions,components'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                project = response.json()
                
                project_details = {
                    'id': project.get('id'),
                    'key': project.get('key'),
                    'name': project.get('name'),
                    'description': project.get('description', ''),
                    'lead': {
                        'display_name': project.get('lead', {}).get('displayName', 'Unknown'),
                        'email': project.get('lead', {}).get('emailAddress', '')
                    } if project.get('lead') else None,
                    'project_type': project.get('projectTypeKey', 'Unknown'),
                    'url': project.get('self'),
                    'avatar_urls': project.get('avatarUrls', {}),
                    'category': project.get('projectCategory', {}).get('name', 'Uncategorized') if project.get('projectCategory') else 'Uncategorized',
                    'created_date': project.get('created'),
                    'components': [
                        {
                            'id': comp.get('id'),
                            'name': comp.get('name'),
                            'description': comp.get('description', ''),
                            'lead': comp.get('lead', {}).get('displayName', '') if comp.get('lead') else ''
                        }
                        for comp in project.get('components', [])
                    ],
                    'versions': [
                        {
                            'id': ver.get('id'),
                            'name': ver.get('name'),
                            'description': ver.get('description', ''),
                            'released': ver.get('released', False),
                            'release_date': ver.get('releaseDate')
                        }
                        for ver in project.get('versions', [])
                    ],
                    'issue_types': [
                        {
                            'id': it.get('id'),
                            'name': it.get('name'),
                            'description': it.get('description', ''),
                            'icon_url': it.get('iconUrl')
                        }
                        for it in project.get('issueTypes', [])
                    ]
                }
                
                return {
                    'success': True,
                    'project': project_details,
                    'message': f'Successfully fetched details for project {project_key}'
                }
            elif response.status_code == 404:
                return {
                    'success': False,
                    'message': f'Project {project_key} not found or you do not have permission to view it.',
                    'error_code': 'PROJECT_NOT_FOUND'
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'message': 'Authentication failed. Please re-authenticate.',
                    'error_code': 'AUTH_EXPIRED'
                }
            else:
                logger.error(f"Failed to fetch project details with status {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'message': f'Failed to fetch project details: {response.status_code}',
                    'error_code': 'FETCH_FAILED'
                }
                
        except Exception as e:
            logger.error(f"Unexpected error while fetching project details: {str(e)}")
            return {
                'success': False,
                'message': 'An unexpected error occurred while fetching project details.',
                'error_code': 'UNKNOWN_ERROR'
            }
