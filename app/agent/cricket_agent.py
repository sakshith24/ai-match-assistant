import os
import json
from typing import List, Dict, Any, Optional

from openai import OpenAI

# Import existing tools from Phase 2, 3, and 4
from app.tools.players_stat import get_player_recent_match_stats
from app.tools.performance_analysis import analyze_player_performance
from app.tools.players_comparison import compare_players

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the system prompt guiding agent behavior
SYSTEM_PROMPT = """You are a cricket performance analysis assistant.
Use the available tools to retrieve real cricket statistics.
Never invent or guess statistics.
Use tool results as the source of truth.
Do not perform statistical calculations yourself when the tool already provides the calculated metric.
If required data is unavailable, clearly tell the user.
When discussing consistency, remember that a lower coefficient of variation indicates more consistent scoring.
Do not interpret missing bowling data as zero bowling performance, instead state that no bowling data was available.
Keep responses concise, clear, and easy to understand."""

# Define the JSON schemas for tools exposed to OpenAI tool calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_player_recent_match_stats",
            "description": "Retrieves recent match statistics for a specified cricket player, including batting and bowling performance for each match. Default limit is 5 matches.",
            "parameters": {
                "type": "object",
                "properties": {
                    "player_name": {
                        "type": "string",
                        "description": "The full name of the cricket player."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "The maximum number of recent matches to retrieve (default: 5).",
                        "default": 5
                    }
                },
                "required": ["player_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_player_performance",
            "description": "Analyzes a single cricket player's performance based on their recent match statistics, providing summaries for batting, consistency, and bowling, and breaking down performance by format. Requires recent match data as input.",
            "parameters": {
                "type": "object",
                "properties": {
                    "player_name": {
                        "type": "string",
                        "description": "The full name of the cricket player to analyze."
                    },
                    "matches": {
                        "type": "array",
                        "description": "A list of match dictionaries containing player's recent performance.",
                        "items": {
                            "type": "object"
                        }
                    }
                },
                "required": ["player_name", "matches"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_players",
            "description": "Compares the recent performance of two cricket players across various batting, bowling, and consistency metrics. It provides a detailed breakdown of who is better for each metric and a format-aware comparison. Default limit is 5 matches.",
            "parameters": {
                "type": "object",
                "properties": {
                    "player_a_name": {
                        "type": "string",
                        "description": "The full name of the first cricket player for comparison."
                    },
                    "player_b_name": {
                        "type": "string",
                        "description": "The full name of the second cricket player for comparison."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "The maximum number of recent matches to consider for each player (default: 5).",
                        "default": 5
                    }
                },
                "required": ["player_a_name", "player_b_name"]
            }
        }
    }
]

# Map string tool names to Python callable functions
AVAILABLE_FUNCTIONS = {
    "get_player_recent_match_stats": get_player_recent_match_stats,
    "analyze_player_performance": analyze_player_performance,
    "compare_players": compare_players,
}


def run_cricket_agent(user_message: str, conversation_history: List[Dict[str, Any]]) -> str:
    """
    Runs the AI cricket agent to process a user message, invoking tools when needed.

    Args:
        user_message: The user's input string.
        conversation_history: List of prior user/assistant message dictionaries.

    Returns:
        Natural language answer generated by the LLM.
    """
    # Append the incoming message to conversation context
    messages = conversation_history + [{"role": "user", "content": user_message}]

    try:
        # First LLM Call: Determine tool usage
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.0
        )
        response_message = response.choices[0].message

        # Handle tool call requests
        if response_message.tool_calls:
            tool_calls = response_message.tool_calls
            tool_outputs = []

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = AVAILABLE_FUNCTIONS.get(function_name)
                function_args = json.loads(tool_call.function.arguments)

                print(f"DEBUG: Calling tool: {function_name} with args: {function_args}")

                if function_to_call:
                    # Resolve missing match data for performance analysis dynamically
                    if function_name == "analyze_player_performance" and "matches" not in function_args:
                        player_name = function_args.get("player_name")
                        
                        # Infer player name from context if omitted
                        if not player_name:
                            for msg in reversed(conversation_history):
                                if msg.get("role") == "user" and "player" in msg.get("content", "").lower():
                                    parts = msg["content"].split()
                                    if len(parts) > 2:
                                        player_name = f"{parts[-2]} {parts[-1]}"
                                        break
                        
                        if player_name:
                            print(f"DEBUG: Fetching match stats for {player_name} before analysis.")
                            recent_matches = get_player_recent_match_stats(player_name, limit=5)
                            function_args["matches"] = recent_matches
                        else:
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": "Error: Could not determine player name for analysis."
                            })
                            continue

                    try:
                        tool_result = function_to_call(**function_args)
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(tool_result, indent=2) if isinstance(tool_result, (dict, list)) else str(tool_result)
                        })
                    except Exception as e:
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": f"Error executing tool {function_name}: {e}"
                        })
                else:
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": f"Tool '{function_name}' not found."
                    })

            # Append assistant's tool call request and outputs back into context
            messages.append(response_message)
            messages.extend([
                {
                    "role": "tool",
                    "tool_call_id": tc_output["tool_call_id"],
                    "content": tc_output["output"]
                }
                for tc_output in tool_outputs
            ])

            # Second LLM Call: Generate final natural language summary
            print("DEBUG: Second LLM call with tool outputs for explanation.")
            second_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
                temperature=0.5
            )
            return second_response.choices[0].message.content

        else:
            # Direct text response without tool execution
            return response_message.content

    except Exception as e:
        print(f"ERROR: OpenAI API call failed: {e}")
        return "I apologize, but I encountered an error communicating with the AI. Please try again."