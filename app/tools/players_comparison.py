from typing import List, Dict, Any, Union
from app.tools.players_stat import get_player_recent_match_stats
from app.tools.performance_analysis import analyze_player_performance


def _compare_metric(
    metric_name: str,
    val_a: Union[int, float, None],
    val_b: Union[int, float, None],
    higher_is_better: bool
) -> Dict[str, Any]:
    """
    Compares two metric values and determines which player is better.
    Handles None values gracefully.
    """
    result: Dict[str, Any] = {
        "player_a": val_a,
        "player_b": val_b,
        "better": "Tie"
    }

    if val_a is None and val_b is None:
        result["better"] = "No data for either player"
    elif val_a is None:
        result["better"] = "Player B" if higher_is_better else "Player A"
    elif val_b is None:
        result["better"] = "Player A" if higher_is_better else "Player B"
    else:
        if (higher_is_better and val_a > val_b) or (not higher_is_better and val_a < val_b):
            result["better"] = "Player A"
        elif (higher_is_better and val_b > val_a) or (not higher_is_better and val_b < val_a):
            result["better"] = "Player B"
        else:
            result["better"] = "Tie"
            
    return result


def _compare_consistency(
    cv_a: Union[float, None],
    cv_b: Union[float, None]
) -> Dict[str, Any]:
    """
    Compares consistency based on Coefficient of Variation (CV). Lower CV is better.
    """
    result: Dict[str, Any] = {
        "player_a_cv": cv_a,
        "player_b_cv": cv_b,
        "more_consistent": "Tie"
    }

    if cv_a is None and cv_b is None:
        result["more_consistent"] = "No data for either player"
    elif cv_a is None:
        result["more_consistent"] = "Player B"
    elif cv_b is None:
        result["more_consistent"] = "Player A"
    else:
        if cv_a < cv_b:
            result["more_consistent"] = "Player A"
        elif cv_b < cv_a:
            result["more_consistent"] = "Player B"
        else:
            result["more_consistent"] = "Tie"
            
    return result


def compare_players(
    player_a_name: str,
    player_b_name: str,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Compares the performance of two cricket players based on their recent match statistics.

    Args:
        player_a_name (str): The name of the first player.
        player_b_name (str): The name of the second player.
        limit (int): The number of recent matches to consider for analysis.

    Returns:
        Dict[str, Any]: A structured dictionary containing the analysis and comparison
                        of both players.
    """
    comparison_result: Dict[str, Any] = {
        "player_a": {"name": player_a_name, "analysis": None},
        "player_b": {"name": player_b_name, "analysis": None},
        "comparison": {},
        "format_comparison": {},
        "bowling_comparison": None
    }

    # 1. Retrieve and Analyze Player A
    player_a_matches = get_player_recent_match_stats(player_a_name, limit)
    if player_a_matches:
        player_a_analysis = analyze_player_performance(player_a_matches, player_a_name)
        comparison_result["player_a"]["analysis"] = player_a_analysis
    else:
        return {"error": f"No data found for {player_a_name}"}

    # 2. Retrieve and Analyze Player B
    player_b_matches = get_player_recent_match_stats(player_b_name, limit)
    if player_b_matches:
        player_b_analysis = analyze_player_performance(player_b_matches, player_b_name)
        comparison_result["player_b"]["analysis"] = player_b_analysis
    else:
        return {"error": f"No data found for {player_b_name}"}

    if not player_a_analysis or not player_b_analysis:
        return {"error": "Could not analyze both players due to missing data."}

    # 3. Batting Comparison
    bat_a = player_a_analysis["batting_summary"]
    bat_b = player_b_analysis["batting_summary"]
    cons_a = player_a_analysis["consistency"]
    cons_b = player_b_analysis["consistency"]

    comparison_result["comparison"]["matches_analyzed"] = _compare_metric(
        "matches_analyzed", bat_a.get("matches_analyzed"), bat_b.get("matches_analyzed"), higher_is_better=True
    )
    comparison_result["comparison"]["total_runs"] = _compare_metric(
        "total_runs", bat_a.get("total_runs"), bat_b.get("total_runs"), higher_is_better=True
    )
    comparison_result["comparison"]["average_runs"] = _compare_metric(
        "average_runs", bat_a.get("average_runs"), bat_b.get("average_runs"), higher_is_better=True
    )
    comparison_result["comparison"]["highest_score"] = _compare_metric(
        "highest_score", bat_a.get("highest_score"), bat_b.get("highest_score"), higher_is_better=True
    )
    comparison_result["comparison"]["lowest_score"] = _compare_metric(
        "lowest_score", bat_a.get("lowest_score"), bat_b.get("lowest_score"), higher_is_better=True
    )
    comparison_result["comparison"]["fifties"] = _compare_metric(
        "fifties", bat_a.get("fifties"), bat_b.get("fifties"), higher_is_better=True
    )
    comparison_result["comparison"]["hundreds"] = _compare_metric(
        "hundreds", bat_a.get("hundreds"), bat_b.get("hundreds"), higher_is_better=True
    )
    comparison_result["comparison"]["ducks"] = _compare_metric(
        "ducks", bat_a.get("ducks"), bat_b.get("ducks"), higher_is_better=False
    )
    comparison_result["comparison"]["average_strike_rate"] = _compare_metric(
        "average_strike_rate", bat_a.get("average_strike_rate"), bat_b.get("average_strike_rate"), higher_is_better=True
    )

    # Consistency Comparison
    comparison_result["comparison"]["consistency_std_dev"] = _compare_metric(
        "standard_deviation", cons_a.get("standard_deviation"), cons_b.get("standard_deviation"), higher_is_better=False
    )
    comparison_result["comparison"]["consistency_coeff_variation"] = _compare_consistency(
        cons_a.get("coefficient_of_variation"), cons_b.get("coefficient_of_variation")
    )

    # 4. Format-aware Comparison
    format_a = player_a_analysis["format_summary"]
    format_b = player_b_analysis["format_summary"]
    all_formats = sorted(list(set(format_a.keys()) | set(format_b.keys())))

    for fmt in all_formats:
        fmt_data_a = format_a.get(fmt)
        fmt_data_b = format_b.get(fmt)

        if not fmt_data_a and not fmt_data_b:
            comparison_result["format_comparison"][fmt] = "No data for either player"
            continue

        format_comp_entry: Dict[str, Any] = {
            "player_a": fmt_data_a if fmt_data_a else "No data",
            "player_b": fmt_data_b if fmt_data_b else "No data",
            "comparison_metrics": {}
        }

        if fmt_data_a or fmt_data_b:
            format_comp_entry["comparison_metrics"]["matches"] = _compare_metric(
                "matches", fmt_data_a.get("matches") if fmt_data_a else None, fmt_data_b.get("matches") if fmt_data_b else None, higher_is_better=True
            )
            format_comp_entry["comparison_metrics"]["total_runs"] = _compare_metric(
                "total_runs", fmt_data_a.get("total_runs") if fmt_data_a else None, fmt_data_b.get("total_runs") if fmt_data_b else None, higher_is_better=True
            )
            format_comp_entry["comparison_metrics"]["average_runs"] = _compare_metric(
                "average_runs", fmt_data_a.get("average_runs") if fmt_data_a else None, fmt_data_b.get("average_runs") if fmt_data_b else None, higher_is_better=True
            )

        comparison_result["format_comparison"][fmt] = format_comp_entry

    # 5. Bowling Comparison
    bowl_a = player_a_analysis["bowling_summary"]
    bowl_b = player_b_analysis["bowling_summary"]

    if bowl_a and bowl_b and (bowl_a.get("matches_with_bowling", 0) > 0 or bowl_b.get("matches_with_bowling", 0) > 0):
        bowling_comp: Dict[str, Any] = {}
        bowling_comp["matches_with_bowling"] = _compare_metric(
            "matches_with_bowling", bowl_a.get("matches_with_bowling"), bowl_b.get("matches_with_bowling"), higher_is_better=True
        )
        bowling_comp["total_wickets"] = _compare_metric(
            "total_wickets", bowl_a.get("total_wickets"), bowl_b.get("total_wickets"), higher_is_better=True
        )
        bowling_comp["average_wickets"] = _compare_metric(
            "average_wickets", bowl_a.get("average_wickets"), bowl_b.get("average_wickets"), higher_is_better=True
        )
        bowling_comp["total_runs_conceded"] = _compare_metric(
            "total_runs_conceded", bowl_a.get("total_runs_conceded"), bowl_b.get("total_runs_conceded"), higher_is_better=False
        )
        bowling_comp["average_economy"] = _compare_metric(
            "average_economy", bowl_a.get("average_economy"), bowl_b.get("average_economy"), higher_is_better=False
        )
        bowling_comp["best_wickets"] = _compare_metric(
            "best_wickets", bowl_a.get("best_wickets"), bowl_b.get("best_wickets"), higher_is_better=True
        )
        comparison_result["bowling_comparison"] = bowling_comp
    else:
        comparison_result["bowling_comparison"] = "No significant bowling data for either player."

    return comparison_result