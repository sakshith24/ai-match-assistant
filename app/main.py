import json
from app.tools.players_stat import get_player_recent_match_stats
from app.tools.performance_analysis import analyze_player_performance

def main():
    player_name = "Virat Kohli"
    print(f"Fetching recent match stats for {player_name}...\n")

    results = get_player_recent_match_stats(player_name, limit=3)
    
    if results:
        # Pass the raw match statistics to your performance analysis tool
        player_analysis = analyze_player_performance(results, player_name)

        print("Performance Analysis\n")
        print(f"Player: {player_analysis['player']}")
        print(f"Matches analyzed: {player_analysis['matches_analyzed']}\n")

        # Batting Summary
        batting_summary = player_analysis['batting_summary']
        print("Batting:")
        print(f"  Total runs: {batting_summary['total_runs']}")
        print(f"  Average runs: {batting_summary['average_runs']}")
        print(f"  Highest score: {batting_summary['highest_score']}")
        print(f"  Lowest score: {batting_summary['lowest_score']}")
        print(f"  Fifties: {batting_summary['fifties']}")
        print(f"  Hundreds: {batting_summary['hundreds']}")
        print(f"  Ducks: {batting_summary['ducks']}")
        print(f"  Average strike rate: {batting_summary['average_strike_rate']}\n")

        # Consistency
        consistency = player_analysis['consistency']
        print("Consistency:")
        print(f"  Average runs: {consistency['average_runs']}")
        print(f"  Standard deviation: {consistency['standard_deviation']}")
        print(f"  Coefficient of variation: {consistency['coefficient_of_variation']}\n")

        # Format Summary
        format_summary = player_analysis['format_summary']
        print("Format Summary:\n")
        for format_name, stats in format_summary.items():
            print(f"  {format_name}:")
            print(f"    Matches: {stats['matches']}")
            print(f"    Total runs: {stats['total_runs']}")
            print(f"    Average runs: {stats['average_runs']}\n")
        
        # Bowling Summary
        bowling_summary = player_analysis['bowling_summary']
        print("Bowling:")
        print(f"  Matches with bowling: {bowling_summary['matches_with_bowling']}")
        print(f"  Total wickets: {bowling_summary['total_wickets']}")
        print(f"  Total runs conceded: {bowling_summary['total_runs_conceded']}")
        print(f"  Total overs: {bowling_summary['total_overs']}")
        print(f"  Average wickets: {bowling_summary['average_wickets']}")
        print(f"  Average economy: {bowling_summary['average_economy']}")
        print(f"  Best wickets: {bowling_summary['best_wickets']}\n")

    else:
        print(f"No match statistics found for {player_name}.")

if __name__ == "__main__":
    main()