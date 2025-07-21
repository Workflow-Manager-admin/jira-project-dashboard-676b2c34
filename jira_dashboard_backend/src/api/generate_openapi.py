import json
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api.main import app

def generate_openapi_spec():
    """Generate OpenAPI specification for the Jira Dashboard API"""
    
    # Get the OpenAPI schema
    openapi_schema = app.openapi()
    
    # Ensure the interfaces directory exists
    output_dir = "interfaces"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "openapi.json")
    
    # Write the schema to file
    with open(output_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)
    
    print(f"OpenAPI specification generated successfully at: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_openapi_spec()
