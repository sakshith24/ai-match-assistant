import os
from app.tools.players_comparison import compare_players

def print_comparison_metric(label, comp_dict, player_a_name, player_b_name, key_a='player_a', key_b='player_b', better_key='better'):
    val_a = comp_dict.get(key_a, 'N/A')
    val_b = comp_dict.get(key_b, 'N/A')
    better = comp_dict.get(better_key, 'Tie')
    print(f"{label}:")
    print(f"  {player_a_name}: {val_a}")
    print(f"  {player_b_name}: {val_b}")
    print(f"  Better: {better}\n")

def run_comparison_demo():
    # Set default environment variables if not present
    if os.getenv("RAPIDAPI_KEY") is None:
        os.environ["RAPIDAPI_KEY"] = "YOUR_RAPIDAPI_KEY_HERE"
    if os.getenv("RAPIDAPI_HOST") is None:
        os.environ["RAPIDAPI_HOST"] = "cricbuzz-live.p.rapidapi.com"

    player_a_name = "Virat Kohli"
    player_b_name = "Pat Cummins"
    limit = 3

    print("=" * 60)
    print(f"--- Player Comparison: {player_a_name} vs {player_b_name} ---")
    print(f"Analyzing last {limit} matches...\n")

    results = compare_players(player_a_name, player_b_name, limit=limit)

    if "error" in results:
        print(f"Error: {results['error']}")
        return

    player_a_data = results["player_a"]
    player_b_data = results["player_b"]
    comp_metrics = results["comparison"]
    format_comp = results["format_comparison"]
    bowl_comp = results["bowling_comparison"]

    print(f"Player A: {player_a_data['name']}")
    print(f"Player B: {player_b_data['name']}\n")

    # --- Batting ---
    print("--- Batting Comparison ---\n")
    print_comparison_metric("Matches Analyzed", comp_metrics["matches_analyzed"], player_a_name, player_b_name)
    print_comparison_metric("Total Runs", comp_metrics["total_runs"], player_a_name, player_b_name)
    print_comparison_metric("Average Runs", comp_metrics["average_runs"], player_a_name, player_b_name)
    print_comparison_metric("Highest Score", comp_metrics["highest_score"], player_a_name, player_b_name)
    print_comparison_metric("Lowest Score", comp_metrics["lowest_score"], player_a_name, player_b_name)
    print_comparison_metric("Fifties", comp_metrics["fifties"], player_a_name, player_b_name)
    print_comparison_metric("Hundreds", comp_metrics["hundreds"], player_a_name, player_b_name)
    print_comparison_metric("Ducks", comp_metrics["ducks"], player_a_name, player_b_name)
    print_comparison_metric("Average Strike Rate", comp_metrics["average_strike_rate"], player_a_name, player_b_name)

    print("Consistency:")
    print_comparison_metric("Standard Deviation", comp_metrics["consistency_std_dev"], player_a_name, player_b_name, better_key='better')
    print_comparison_metric("Coefficient of Variation", comp_metrics["consistency_coeff_variation"], player_a_name, player_b_name, key_a='player_a_cv', key_b='player_b_cv', better_key='more_consistent')

    # --- Formats ---
    print("--- Format-wise Comparison ---\n")
    for fmt, fmt_data in format_comp.items():
        print(f"Format: {fmt}")
        if isinstance(fmt_data, str):
            print(f"  {fmt_data}\n")
            continue

        print(f"  {player_a_name}: {fmt_data['player_a']}")
        print(f"  {player_b_name}: {fmt_data['player_b']}")

        if fmt_data.get("comparison_metrics"):
            print("  Comparison:")
            for metric, data in fmt_data["comparison_metrics"].items():
                print(f"    {metric.replace('_', ' ').title()}:")
                print(f"      {player_a_name}: {data.get('player_a', 'N/A')}")
                print(f"      {player_b_name}: {data.get('player_b', 'N/A')}")
                print(f"      Better: {data.get('better', 'Tie')}")
        print("-" * 30)

    # --- Bowling ---
    print("\n--- Bowling Comparison ---\n")
    if isinstance(bowl_comp, str):
        print(f"{bowl_comp}\n")
    elif bowl_comp:
        print_comparison_metric("Matches with Bowling", bowl_comp["matches_with_bowling"], player_a_name, player_b_name)
        print_comparison_metric("Total Wickets", bowl_comp["total_wickets"], player_a_name, player_b_name)
        print_comparison_metric("Average Wickets", bowl_comp["average_wickets"], player_a_name, player_b_name)
        print_comparison_metric("Total Runs Conceded", bowl_comp["total_runs_conceded"], player_a_name, player_b_name)
        print_comparison_metric("Average Economy", bowl_comp["average_economy"], player_a_name, player_b_name)
        print_comparison_metric("Best Wickets", bowl_comp["best_wickets"], player_a_name, player_b_name)

if __name__ == "__main__":
    run_comparison_demo()