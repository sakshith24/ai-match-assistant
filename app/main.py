import json
from app.tools.players_stat import get_players_recent_matches

if __name__ == "__main__":
    player_name = "Virat Kohli"
    print(f"Fetching recent matches for {player_name}...\n")

    match_data = get_players_recent_matches(player_name)
    print(json.dumps(match_data,indent=4))