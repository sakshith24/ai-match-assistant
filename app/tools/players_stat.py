import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "cricbuzz-cricket.p.rapidapi.com")

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
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
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


def get_match_player_stats(player_name: str, match_id: str) -> dict | None:
    """
    Retrieves a player's actual batting and bowling performance from a match scorecard.
    """
    if not match_id or match_id == "N/A":
        return None

    # Endpoint candidates on cricbuzz-cricket.p.rapidapi.com
    endpoint_urls = [
        (f"{BASE_URL}/mcenter/v1/{match_id}/scard", {}),
        (f"{BASE_URL}/mcenter/v1/{match_id}/hscard", {}),
        (f"{BASE_URL}/mcenter/v1/{match_id}", {}),
        (f"{BASE_URL}/matches/get-scorecard-v2", {"matchId": match_id})
    ]
    
    scorecard_data = None
    for url, params in endpoint_urls:
        try:
            res = requests.get(url, headers=HEADERS, params=params, timeout=10)
            if res.status_code == 200:
                scorecard_data = res.json()
                break
        except requests.RequestException:
            continue

    if not scorecard_data:
        print(f"[Scorecard API Error] All endpoints returned 404/Error for match ID {match_id}")
        return None

    player_stats = {
        "player": player_name,
        "match_id": match_id,
        "batting": None,
        "bowling": None
    }

    # Extract scoreCard / scorecard / innings structure
    innings_list = (
        scorecard_data.get("scoreCard") 
        or scorecard_data.get("scorecard") 
        or scorecard_data.get("innings") 
        or scorecard_data.get("scoreCardList") 
        or []
    )

    surname = player_name.split()[-1].lower()

    for inning in innings_list:
        # Extract Batting Stats
        batsmen = (
            inning.get("batsman") 
            or inning.get("batsmen") 
            or (inning.get("batTeamDetails", {}).get("batsmenData", {}).values() if isinstance(inning.get("batTeamDetails"), dict) else []) 
            or []
        )
        
        for b in batsmen:
            if isinstance(b, dict):
                b_name = b.get("name") or b.get("fullName") or b.get("batName") or ""
                if surname in b_name.lower():
                    runs = b.get("runs") or b.get("R") or 0
                    balls = b.get("balls") or b.get("B") or 0
                    fours = b.get("fours") or b.get("4s") or 0
                    sixes = b.get("sixes") or b.get("6s") or 0
                    api_strike_rate = b.get("strikeRate") or b.get("strkRate")

                    final_strike_rate = None

                    if api_strike_rate is not None and api_strike_rate != 0.0:
                        final_strike_rate = float(api_strike_rate)
                    elif runs is not None and balls is not None:
                        if balls > 0:
                            final_strike_rate = round((runs / balls) * 100, 2)
                        else:
                            final_strike_rate = 0.0

                    player_stats["batting"] = {
                        "runs": runs,
                        "balls": balls,
                        "fours": fours,
                        "sixes": sixes,
                        "strike_rate": final_strike_rate
                    }
                    break  # Match found for batting

        # Extract Bowling Stats
        bowlers = (
            inning.get("bowler") 
            or inning.get("bowlers") 
            or (inning.get("bowlTeamDetails", {}).get("bowlersData", {}).values() if isinstance(inning.get("bowlTeamDetails"), dict) else []) 
            or []
        )

        for bw in bowlers:
            if isinstance(bw, dict):
                bw_name = bw.get("name") or bw.get("fullName") or bw.get("bowlName") or ""
                if surname in bw_name.lower():
                    overs = bw.get("overs") or bw.get("O") or 0.0
                    maidens = bw.get("maidens") or bw.get("M") or 0
                    runs_conceded = bw.get("runsConceded") or bw.get("runs") or bw.get("R") or 0
                    wickets = bw.get("wickets") or bw.get("W") or 0
                    api_economy = bw.get("economy") or bw.get("E")

                    final_economy = None

                    if api_economy is not None and api_economy != 0.0:
                        final_economy = float(api_economy)
                    elif overs is not None and runs_conceded is not None:
                        if overs > 0:
                            final_economy = round(runs_conceded / overs, 2)
                        else:
                            final_economy = 0.0

                    player_stats["bowling"] = {
                        "overs": overs,
                        "maidens": maidens,
                        "runs_conceded": runs_conceded,
                        "wickets": wickets,
                        "economy": final_economy
                    }
                    break  # Match found for bowling

    return player_stats


def get_player_recent_match_stats(player_name: str, limit: int = 5) -> list[dict]:
    """Combines player recent match metadata with scorecard details."""
    recent_matches = get_player_recent_matches(player_name, limit=limit)
    if not recent_matches:
        return []

    combined_results = []
    for m in recent_matches:
        match_id = m.get("match_id")
        stats = get_match_player_stats(player_name, match_id) if match_id else None

        combined_results.append({
            "match": m.get("match"),
            "date": m.get("date"),
            "match_id": match_id,
            "batting": stats.get("batting") if stats else None,
            "bowling": stats.get("bowling") if stats else None
        })

    return combined_results