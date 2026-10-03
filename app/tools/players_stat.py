import os
import requests
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST
}

BASE_URL = f"https://{RAPIDAPI_HOST}"


def search_player_id(player_name: str) -> str | None:
    """Searches Cricbuzz for a player by name and returns their player ID."""
    url = f"{BASE_URL}/stats/v1/player/search"
    params = {"plrN": player_name}

    try:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        
        player_list = data.get("player", [])
        if player_list:
            return str(player_list[0].get("id"))
            
    except Exception as e:
        print(f"[Search Error]: {e}")
        
    return None


def get_player_recent_matches(player_name: str, limit: int = 5) -> list[dict]:
    """Fetches recent match appearances for a player across formats."""
    player_id = search_player_id(player_name)
    if not player_id:
        print(f"Player '{player_name}' not found.")
        return []

    url = f"{BASE_URL}/stats/v1/player/{player_id}/career"
    
    try:
        response = requests.get(url, headers=HEADERS)
        data = response.json()

        recent_matches = []
        format_list = data.get("values", [])

        for item in format_list[:limit]:
            last_played_str = item.get("lastPlayed", "")
            
            # Parse string: "vs West Indies,  2026-10-03, PCA International..."
            parts = [p.strip() for p in last_played_str.split(",")] if last_played_str else []
            
            opponent = parts[0] if len(parts) > 0 else "Unknown Match"
            match_date = parts[1] if len(parts) > 1 else "N/A"
            
            recent_matches.append({
                "match": f"{item.get('name', '').upper()} - {opponent}",
                "date": match_date,
                "match_id": item.get("lastPlayedMatchId", "N/A")
            })

        return recent_matches

    except Exception as e:
        print(f"[API Error]: {e}")
        return []