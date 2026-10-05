import math
import statistics
from typing import List, Dict, Any, Union

def calculate_batting_summary(matches: List[Dict]) -> Dict:
    """
    Calculates a batting summary for a list of matches.
    """
    matches_analyzed = 0
    total_runs = 0
    total_balls = 0
    total_fours = 0
    total_sixes = 0
    fifties = 0
    hundreds = 0
    ducks = 0
    runs_list: List[int] = []
    strike_rates_list: List[float] = []

    for match in matches:
        batting_stats = match.get("batting")
        if batting_stats and isinstance(batting_stats, dict):
            runs = batting_stats.get("runs")
            balls = batting_stats.get("balls")
            fours = batting_stats.get("fours")
            sixes = batting_stats.get("sixes")
            strike_rate = batting_stats.get("strike_rate")

            # Only consider matches where the player actually batted
            if runs is not None:
                matches_analyzed += 1
                total_runs += runs
                runs_list.append(runs)

                if balls is not None:
                    total_balls += balls
                    if runs == 0 and balls > 0:  # Duck if faced at least one ball
                        ducks += 1

                if fours is not None:
                    total_fours += fours
                if sixes is not None:
                    total_sixes += sixes

                if 50 <= runs < 100:
                    fifties += 1
                elif runs >= 100:
                    hundreds += 1
                
                if strike_rate is not None :
                    strike_rates_list.append(strike_rate)
            
    average_runs = round(total_runs / matches_analyzed, 2) if matches_analyzed > 0 else 0.0
    highest_score = max(runs_list) if runs_list else 0
    lowest_score = min(runs_list) if runs_list else 0
    average_strike_rate = round(sum(strike_rates_list) / len(strike_rates_list), 2) if strike_rates_list else 0.0

    return {
        "matches_analyzed": matches_analyzed,
        "total_runs": total_runs,
        "average_runs": average_runs,
        "highest_score": highest_score,
        "lowest_score": lowest_score,
        "total_balls": total_balls,
        "total_fours": total_fours,
        "total_sixes": total_sixes,
        "fifties": fifties,
        "hundreds": hundreds,
        "ducks": ducks,
        "average_strike_rate": average_strike_rate
    }

def calculate_batting_consistency(matches: List[Dict]) -> Dict:
    """
    Calculates batting consistency metrics (mean, standard deviation, coefficient of variation).
    """
    runs_list: List[int] = []
    for match in matches:
        batting_stats = match.get("batting")
        if batting_stats and isinstance(batting_stats, dict) and batting_stats.get("runs") is not None:
            runs_list.append(batting_stats["runs"])

    matches_analyzed = len(runs_list)
    average_runs = round(statistics.mean(runs_list), 2) if runs_list else 0.0

    standard_deviation = 0.0
    if len(runs_list) >= 2:
        standard_deviation = round(statistics.stdev(runs_list), 2)
    elif len(runs_list) == 1:
        standard_deviation = 0.0

    coefficient_of_variation = 0.0
    if average_runs > 0:
        coefficient_of_variation = round(standard_deviation / average_runs, 2)
    
    return {
        "average_runs": average_runs,
        "standard_deviation": standard_deviation,
        "coefficient_of_variation": coefficient_of_variation,
        "matches_analyzed": matches_analyzed
    }

def calculate_format_summary(matches: List[Dict]) -> Dict:
    """
    Groups and summarizes batting statistics by match format.
    """
    format_stats: Dict[str, Dict[str, Any]] = {}

    for match in matches:
        match_info = match.get("match", "")
        format_name = match_info.split(' - ')[0].strip() if ' - ' in match_info else "Unknown"
        
        if format_name not in format_stats:
            format_stats[format_name] = {
                "matches": 0,
                "total_runs": 0,
                "runs_list": []
            }
        
        batting_stats = match.get("batting")
        if batting_stats and isinstance(batting_stats, dict) and batting_stats.get("runs") is not None:
            runs = batting_stats["runs"]
            format_stats[format_name]["matches"] += 1
            format_stats[format_name]["total_runs"] += runs
            format_stats[format_name]["runs_list"].append(runs)

    for format_name, stats in format_stats.items():
        runs_list = stats.pop("runs_list")
        total_runs = stats["total_runs"]
        num_matches = stats["matches"]
        
        stats["average_runs"] = round(total_runs / num_matches, 2) if num_matches > 0 else 0.0
    
    return format_stats

def calculate_bowling_summary(matches: List[Dict]) -> Dict:
    """
    Calculates a bowling summary for a list of matches.

    Handles cricket overs represented as:
    - int/float: 4, 4.0
    - string: "4", "4.0", "3.2"
    
    Note:
    Cricket "3.2 overs" means 3 overs and 2 balls,
    not 3.2 decimal overs.
    """

    matches_with_bowling = 0
    total_wickets = 0
    total_runs_conceded = 0
    total_overs = 0.0
    best_wickets = 0

    economy_values: List[float] = []

    def overs_to_decimal(overs) -> float:
        """
        Converts cricket overs notation to decimal overs.

        Examples:
            4       -> 4.0
            "4"     -> 4.0
            "3.2"   -> 3.6667
            "10.4"  -> 10.6667

        In cricket, .2 means 2 balls, not 0.2 overs.
        """

        if overs is None:
            return 0.0

        try:
            overs_str = str(overs).strip()

            if "." in overs_str:
                whole, balls = overs_str.split(".", 1)

                whole_overs = int(whole)
                balls = int(balls)

                # A valid over can only contain 0-5 balls
                if 0 <= balls <= 5:
                    return whole_overs + (balls / 6)

            return float(overs_str)

        except (ValueError, TypeError):
            return 0.0

    for match in matches:
        bowling_stats = match.get("bowling")

        if not bowling_stats or not isinstance(bowling_stats, dict):
            continue

        wickets = bowling_stats.get("wickets")
        runs_conceded = bowling_stats.get("runs_conceded")
        overs = bowling_stats.get("overs")
        economy = bowling_stats.get("economy")

        # Safely convert numeric values
        try:
            wickets = float(wickets) if wickets is not None else 0.0
        except (ValueError, TypeError):
            wickets = 0.0

        try:
            runs_conceded = (
                float(runs_conceded)
                if runs_conceded is not None
                else 0.0
            )
        except (ValueError, TypeError):
            runs_conceded = 0.0

        decimal_overs = overs_to_decimal(overs)

        try:
            economy = (
                float(economy)
                if economy is not None
                else None
            )
        except (ValueError, TypeError):
            economy = None

        # Player actually bowled in this match
        if decimal_overs > 0 or wickets > 0:

            matches_with_bowling += 1

            total_wickets += int(wickets)
            total_runs_conceded += runs_conceded
            total_overs += decimal_overs

            best_wickets = max(
                best_wickets,
                int(wickets)
            )

            # Use supplied economy if available
            if economy is not None and economy > 0:
                economy_values.append(economy)

            # Otherwise calculate economy ourselves
            elif decimal_overs > 0:
                calculated_economy = (
                    runs_conceded / decimal_overs
                )

                economy_values.append(
                    round(calculated_economy, 2)
                )

    average_wickets = (
        round(total_wickets / matches_with_bowling, 2)
        if matches_with_bowling > 0
        else 0.0
    )

    average_economy = (
        round(
            sum(economy_values) / len(economy_values),
            2
        )
        if economy_values
        else 0.0
    )

    return {
        "matches_with_bowling": matches_with_bowling,
        "total_wickets": total_wickets,
        "total_runs_conceded": round(total_runs_conceded, 2),
        "total_overs": round(total_overs, 2),
        "average_wickets": average_wickets,
        "average_economy": average_economy,
        "best_wickets": best_wickets
    }

def analyze_player_performance(matches: List[Dict], player_name: str) -> Dict:
    """
    Combines various player performance analysis summaries into one payload.
    """
    batting_summary = calculate_batting_summary(matches)
    consistency = calculate_batting_consistency(matches)
    format_summary = calculate_format_summary(matches)
    bowling_summary = calculate_bowling_summary(matches)

    return {
        "player": player_name,
        "matches_analyzed": batting_summary.get("matches_analyzed", 0),
        "batting_summary": batting_summary,
        "consistency": consistency,
        "format_summary": format_summary,
        "bowling_summary": bowling_summary
    }