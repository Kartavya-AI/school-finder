import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class LocationInput(BaseModel):
    """Input schema for LocationTool."""
    query: str = Field(..., description="Query to get location information (e.g., 'current location', 'my location')")

class LocationTool(BaseTool):
    name: str = "get_current_location"
    description: str = "Get current location information including city, region, and country based on IP address."
    args_schema: Type[BaseModel] = LocationInput

    def _run(self, query: str) -> str:
        """
        Get current location information using IP geolocation.
        
        Args:
            query: Query string (not used but required by schema)
            
        Returns:
            String containing location information
        """
        try:
            # Using ipapi.co for free IP geolocation
            response = requests.get('https://ipapi.co/json/', timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'error' in data:
                fallback_response = requests.get('http://ip-api.com/json/', timeout=10)
                fallback_response.raise_for_status()
                fallback_data = fallback_response.json()
                
                if fallback_data.get('status') == 'success':
                    return f"Current Location: {fallback_data.get('city', 'Unknown')}, {fallback_data.get('regionName', 'Unknown')}, {fallback_data.get('country', 'Unknown')}"
                else:
                    return "Unable to determine current location. Please specify your location manually."
            
            city = data.get('city', 'Unknown')
            region = data.get('region', 'Unknown')
            country = data.get('country_name', 'Unknown')
            
            return f"Current Location: {city}, {region}, {country}"
            
        except requests.RequestException as e:
            return f"Error getting location: {str(e)}. Please specify your location manually."
        except Exception as e:
            return f"Unexpected error: {str(e)}. Please specify your location manually."

# Create tool instance
tool = LocationTool()
