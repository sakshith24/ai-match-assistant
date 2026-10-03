import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('CRICKET_API_KEY')
BASE_URL = "https://api.cricapi.com/v1"

def get_player_id(player_name:str) -> str | None:
    """Find the unique id for a given player name """
    url = f"{BASE_URL}/players"
    params = {
        "apikey": API_KEY,
        "search" : player_name
    }
    response = requests.get(url,params=params)
    data = response.json()

    if data.get("status") == "success" and data.get("data"):
        return data["data"][0]["id"]
    return None

def get_players_recent_matches(player_name :str , limit:int = 5) -> list[dict]:
    """
    Fetches real recent match performance for a player.
    Returns: [{'match': '...', 'date': '...', 'runs': ...}, ...]
    """
    player_id = get_player_id(player_name)
    if not player_id:
        print(f"Player {player_name} not found")
        return []
    url = f"{BASE_URL}/players_info"
    params = {
        "apikey": API_KEY,
        "id": player_id 
    }
    response = requests.get(url,params=params)
    data = response.json()

    if data.get("status") != "success":
        return []
    recent_matches = []
    matches_data = data.get("data",{}).get("recentmatches", [])

    for match in matches_data[:limit]:
        recent_matches.append({
            "match":match.get("name","unknown match"),
            "date":match.get("date" , "N/A"),
            "runs":match.get("runs" , 0)
        })
        return recent_matches