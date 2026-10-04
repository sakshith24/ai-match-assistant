import json
from app.tools.players_stat import get_player_recent_match_stats

def main():
    player_name = "Virat Kohli"
    print(f"Fetching recent match stats for {player_name}...\n")

    results = get_player_recent_match_stats(player_name, limit=3)
    
    if results:
        print(json.dumps(results, indent=4))
    else:
        print(f"No match statistics found for {player_name}.")

if __name__ == "__main__":
    main()