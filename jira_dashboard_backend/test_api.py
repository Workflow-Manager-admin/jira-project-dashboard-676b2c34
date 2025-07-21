#!/usr/bin/env python3
"""
Simple test script to validate Jira Dashboard API endpoints.
This script demonstrates how to use the API and can be used for basic testing.
"""

import requests
from typing import Dict, Any

class JiraAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def test_health_check(self) -> Dict[str, Any]:
        """Test the health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            return {
                'endpoint': 'GET /',
                'status_code': response.status_code,
                'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'success': response.status_code == 200
            }
        except Exception as e:
            return {
                'endpoint': 'GET /',
                'error': str(e),
                'success': False
            }
    
    def test_authentication(self, email: str, api_token: str, domain: str) -> Dict[str, Any]:
        """Test Jira authentication endpoint"""
        try:
            payload = {
                "email": email,
                "api_token": api_token,
                "domain": domain
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            return {
                'endpoint': 'POST /api/auth/login',
                'status_code': response.status_code,
                'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'success': response.status_code == 200
            }
        except Exception as e:
            return {
                'endpoint': 'POST /api/auth/login',
                'error': str(e),
                'success': False
            }
    
    def test_fetch_projects(self, email: str, api_token: str, domain: str) -> Dict[str, Any]:
        """Test fetch projects endpoint"""
        try:
            payload = {
                "email": email,
                "api_token": api_token,
                "domain": domain
            }
            
            response = self.session.post(
                f"{self.base_url}/api/projects",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            return {
                'endpoint': 'POST /api/projects',
                'status_code': response.status_code,
                'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'success': response.status_code == 200
            }
        except Exception as e:
            return {
                'endpoint': 'POST /api/projects',
                'error': str(e),
                'success': False
            }
    
    def test_project_details(self, project_key: str, email: str, api_token: str, domain: str) -> Dict[str, Any]:
        """Test fetch project details endpoint"""
        try:
            payload = {
                "email": email,
                "api_token": api_token,
                "domain": domain
            }
            
            response = self.session.post(
                f"{self.base_url}/api/projects/{project_key}",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            return {
                'endpoint': f'POST /api/projects/{project_key}',
                'status_code': response.status_code,
                'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'success': response.status_code == 200
            }
        except Exception as e:
            return {
                'endpoint': f'POST /api/projects/{project_key}',
                'error': str(e),
                'success': False
            }
    
    def run_basic_tests(self) -> Dict[str, Any]:
        """Run basic tests that don't require credentials"""
        print("Running basic API tests...")
        results = []
        
        # Test health check
        health_result = self.test_health_check()
        results.append(health_result)
        print(f"✓ Health Check: {'PASS' if health_result['success'] else 'FAIL'}")
        
        return {
            'total_tests': len(results),
            'passed': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }
    
    def run_full_tests(self, email: str, api_token: str, domain: str, project_key: str = None) -> Dict[str, Any]:
        """Run full API tests with credentials"""
        print("Running full API tests...")
        results = []
        
        # Test health check
        health_result = self.test_health_check()
        results.append(health_result)
        print(f"✓ Health Check: {'PASS' if health_result['success'] else 'FAIL'}")
        
        # Test authentication
        auth_result = self.test_authentication(email, api_token, domain)
        results.append(auth_result)
        print(f"✓ Authentication: {'PASS' if auth_result['success'] else 'FAIL'}")
        
        # Test fetch projects
        projects_result = self.test_fetch_projects(email, api_token, domain)
        results.append(projects_result)
        print(f"✓ Fetch Projects: {'PASS' if projects_result['success'] else 'FAIL'}")
        
        # Test project details if project_key provided
        if project_key:
            details_result = self.test_project_details(project_key, email, api_token, domain)
            results.append(details_result)
            print(f"✓ Project Details: {'PASS' if details_result['success'] else 'FAIL'}")
        
        return {
            'total_tests': len(results),
            'passed': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }

def main():
    """Main function for running tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Jira Dashboard API')
    parser.add_argument('--base-url', default='http://localhost:8000', help='Base URL of the API')
    parser.add_argument('--email', help='Jira email for authentication tests')
    parser.add_argument('--api-token', help='Jira API token for authentication tests')
    parser.add_argument('--domain', help='Jira domain for authentication tests')
    parser.add_argument('--project-key', help='Project key for project details test')
    parser.add_argument('--basic-only', action='store_true', help='Run only basic tests without credentials')
    
    args = parser.parse_args()
    
    tester = JiraAPITester(args.base_url)
    
    if args.basic_only:
        results = tester.run_basic_tests()
    elif args.email and args.api_token and args.domain:
        results = tester.run_full_tests(args.email, args.api_token, args.domain, args.project_key)
    else:
        print("Running basic tests only (no credentials provided)")
        results = tester.run_basic_tests()
    
    print("\n=== Test Results ===")
    print(f"Total: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    if results['failed'] > 0:
        print("\n=== Failed Tests ===")
        for result in results['results']:
            if not result['success']:
                print(f"❌ {result['endpoint']}: {result.get('error', 'Unknown error')}")
    
    return results['failed'] == 0

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
