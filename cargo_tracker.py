import asyncio
import json
import os
import re
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import folium
import googlemaps
from browser_use import Agent, BrowserSession
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from langchain_google_genai import ChatGoogleGenerativeAI

# Suppress warnings
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", message="unclosed.*")
warnings.filterwarnings("ignore", message="I/O operation on closed pipe")

# Load environment variables
load_dotenv()

class CargoTracker:
    """A class to track cargo shipments using HMM's tracking system."""
    
    def __init__(self, headless: bool = False):
        """Initialize the cargo tracker.
        
        Args:
            headless: Run browser in headless mode if True
        """
        self.headless = headless
        self.results_dir = Path("tracking_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize APIs
        self._init_apis()
    
    def _init_apis(self) -> None:
        """Initialize required APIs with API keys."""
        self.gmaps = googlemaps.Client(key=os.getenv("GOOGLE_API_KEY"))
        self.llm = ChatGoogleGenerativeAI(
            model='gemini-2.0-flash-exp',
            temperature=0.0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    
    async def track(self, reference_id: str) -> Dict[str, Any]:
        """Track a cargo shipment by its reference ID.
        
        Args:
            reference_id: The booking or tracking ID
            
        Returns:
            Dictionary containing tracking information
        """
        print(f"\n{'='*50}")
        print(f"Tracking cargo with ID: {reference_id}")
        print(f"{'='*50}")
        
        # Get tracking data
        tracking_data = await self._get_tracking_data(reference_id)
        
        # Generate route map if we have port information
        if all(k in tracking_data for k in ['origin_port', 'destination_port']):
            map_path = self._generate_route_map(
                tracking_data['origin_port'],
                tracking_data['destination_port']
            )
            tracking_data['map_path'] = map_path
        
        # Save results
        self._save_results(tracking_data)
        
        # Display results
        self._display_results(tracking_data)
        
        return tracking_data
    
    async def _get_tracking_data(self, ref_id: str) -> Dict[str, Any]:
        """Retrieve tracking data for the given reference ID."""
        task = self._create_tracking_task(ref_id)
        raw_data = await self._execute_tracking_task(task)
        return self._parse_tracking_data(raw_data, ref_id)
    
    def _create_tracking_task(self, ref_id: str) -> str:
        """Create a task description for the tracking agent."""
        return f"""
        Track cargo shipment with reference ID: {ref_id}
        
        1. Navigate to http://www.seacargotracking.net/
        2. Locate HMM (Hyundai Merchant Marine) option
        3. Access the tracking section and enter the reference ID
        4. Extract the following details:
           - Vessel name and number
           - Voyage details
           - Port of loading
           - Port of discharge
           - Estimated time of arrival
           - Current status
        
        Return the data in this JSON format:
        {{
            "vessel": {{
                "name": "vessel name",
                "number": "voyage number"
            }},
            "ports": {{
                "loading": "port of loading",
                "discharge": "port of discharge"
            }},
            "schedule": {{
                "eta": "estimated arrival time",
                "status": "current status"
            }}
        }}
        """
    
    async def _execute_tracking_task(self, task: str) -> Any:
        """Execute the tracking task using browser automation."""
        browser = None
        try:
            browser = BrowserSession(
                executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                headless=self.headless,
                viewport={"width": 1920, "height": 1080}
            )
            await browser.start()
            
            agent = Agent(
                task=task,
                llm=self.llm,
                browser_session=browser
            )
            
            return await agent.run()
            
        finally:
            if browser:
                await browser.close()
                await asyncio.sleep(0.5)
    
    def _parse_tracking_data(self, raw_data: Any, ref_id: str) -> Dict[str, Any]:
        """Parse raw tracking data into a structured format."""
        # Default response
        parsed = {
            'reference_id': ref_id,
            'vessel': {'name': 'N/A', 'number': 'N/A'},
            'ports': {'loading': 'N/A', 'discharge': 'N/A'},
            'schedule': {'eta': 'N/A', 'status': 'N/A'},
            'timestamp': datetime.now().isoformat()
        }
        
        if not raw_data:
            return parsed
            
        try:
            # Handle string input
            if isinstance(raw_data, str):
                # Try to find JSON in the string
                json_match = re.search(r'\{.*\}', raw_data, re.DOTALL)
                if json_match:
                    raw_data = json.loads(json_match.group())
                else:
                    return parsed
            
            # Handle dictionary input
            if isinstance(raw_data, dict):
                # Extract vessel info
                if 'vessel' in raw_data and isinstance(raw_data['vessel'], dict):
                    parsed['vessel'].update({
                        'name': raw_data['vessel'].get('name', 'N/A'),
                        'number': raw_data['vessel'].get('number', 'N/A')
                    })
                
                # Extract port info
                if 'ports' in raw_data and isinstance(raw_data['ports'], dict):
                    parsed['ports'].update({
                        'loading': raw_data['ports'].get('loading', 'N/A'),
                        'discharge': raw_data['ports'].get('discharge', 'N/A')
                    })
                
                # Extract schedule info
                if 'schedule' in raw_data and isinstance(raw_data['schedule'], dict):
                    parsed['schedule'].update({
                        'eta': raw_data['schedule'].get('eta', 'N/A'),
                        'status': raw_data['schedule'].get('status', 'N/A')
                    })
            
            return parsed
            
        except Exception as e:
            print(f"Error parsing tracking data: {e}")
            return parsed
    
    def _generate_route_map(self, origin: str, destination: str) -> Optional[str]:
        """Generate an interactive map showing the shipping route."""
        try:
            geolocator = Nominatim(user_agent="cargo_tracker")
            
            # Get coordinates for ports
            origin_loc = geolocator.geocode(f"{origin} port")
            dest_loc = geolocator.geocode(f"{destination} port")
            
            if not all([origin_loc, dest_loc]):
                return None
            
            # Create map centered between the two points
            map_center = [
                (origin_loc.latitude + dest_loc.latitude) / 2,
                (origin_loc.longitude + dest_loc.longitude) / 2
            ]
            
            route_map = folium.Map(location=map_center, zoom_start=3)
            
            # Add markers
            folium.Marker(
                [origin_loc.latitude, origin_loc.longitude],
                popup=f"Origin: {origin}",
                icon=folium.Icon(color="green", icon="anchor")
            ).add_to(route_map)
            
            folium.Marker(
                [dest_loc.latitude, dest_loc.longitude],
                popup=f"Destination: {destination}",
                icon=folium.Icon(color="red", icon="flag")
            ).add_to(route_map)
            
            # Add route line
            folium.PolyLine(
                locations=[[origin_loc.latitude, origin_loc.longitude], 
                         [dest_loc.latitude, dest_loc.longitude]],
                color="blue",
                weight=2,
                opacity=1
            ).add_to(route_map)
            
            # Save map
            map_path = self.results_dir / f"route_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            route_map.save(str(map_path))
            return str(map_path)
            
        except Exception as e:
            print(f"Error generating route map: {e}")
            return None
    
    def _save_results(self, data: Dict[str, Any]) -> Path:
        """Save tracking results to a JSON file."""
        result_file = self.results_dir / 'tracking_history.json'
        
        # Load existing data
        history = []
        if result_file.exists():
            try:
                with open(result_file, 'r') as f:
                    history = json.load(f)
                    if not isinstance(history, list):
                        history = []
            except json.JSONDecodeError:
                history = []
        
        # Add new entry
        history.append(data)
        
        # Save back to file
        with open(result_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        return result_file
    
    def _display_results(self, data: Dict[str, Any]) -> None:
        """Display tracking results in a user-friendly format."""
        print("\nTracking Results:")
        print("-" * 30)
        print(f"Reference ID: {data['reference_id']}")
        print(f"Vessel: {data['vessel']['name']} (Voyage: {data['vessel']['number']})")
        print(f"Route: {data['ports']['loading']} → {data['ports']['discharge']}")
        print(f"Status: {data['schedule']['status']}")
        print(f"ETA: {data['schedule']['eta']}")
        
        if 'map_path' in data and data['map_path']:
            print(f"\nRoute map generated: {data['map_path']}")


async def main():
    """Main function to run the cargo tracker."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Track cargo shipments')
    parser.add_argument('reference_id', help='The cargo reference or booking ID')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    args = parser.parse_args()
    
    try:
        tracker = CargoTracker(headless=args.headless)
        await tracker.track(args.reference_id)
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    asyncio.run(main())
