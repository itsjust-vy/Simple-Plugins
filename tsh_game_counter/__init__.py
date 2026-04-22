#!/usr/bin/env python3
"""
TSH Game Counter Plugin for Simple
Automatically updates TournamentStreamHelper scoreboard when a game concludes.

When a match ends (is_match transitions from True to False), the plugin
compares remaining player stocks to determine the winner and increments
their score on the TSH scoreboard via its built-in web server.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils import get_plugin_setting

import json
from urllib.request import Request, urlopen
from urllib.error import URLError

# Load settings once at module load
_tsh_host = get_plugin_setting('tsh_game_counter', 'tsh_host', 'localhost')
_tsh_port = get_plugin_setting('tsh_game_counter', 'tsh_port', 5000)
_scoreboard_number = get_plugin_setting('tsh_game_counter', 'scoreboard_number', 1)
_player_team_map = get_plugin_setting('tsh_game_counter', 'player_team_map', {"0": 1, "1": 2})

# Track remaining_frames at the moment a player's last stock is lost
_last_remaining_frames = None


def _update_score(team):
    """Increment score for the specified team in TSH."""
    url = f"http://{_tsh_host}:{_tsh_port}/scoreboard{_scoreboard_number}-team{team}-scoreup"
    try:
        with urlopen(url, timeout=2) as response:
            body = response.read().decode()
            print(f"[TSH Game Counter] Score updated for team {team}: {body}")
    except URLError as e:
        print(f"[TSH Game Counter] Failed to update score for team {team}: {e}")

def _reset_scores():
    """Reset both team scores to 0 in TSH via the /score endpoint."""
    url = f"http://{_tsh_host}:{_tsh_port}/score"
    payload = {
        "team1score": 0,
        "team2score": 0,
        "scoreboard": str(_scoreboard_number)
    }
    body = json.dumps(payload).encode('utf-8')
    req = Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urlopen(req, timeout=2) as response:
            result = response.read().decode()
            print(f"[TSH Game Counter] Scores reset to 0: {result}")
    except URLError as e:
        print(f"[TSH Game Counter] Failed to reset scores: {e}")


def _get_winner_team(full_data):
    """
    Determine the winning team based on remaining stocks.

    Returns the mapped TSH team number for the player with the highest
    remaining stocks, or None if the result is ambiguous (tie / no data).
    """
    players = full_data.get('players', [])
    if len(players) < 2:
        return None

    best_index = None
    best_stocks = -1

    for i, player in enumerate(players):
        if not isinstance(player, dict):
            continue
        stocks = player.get('stocks')
        if stocks is None:
            continue
        if stocks > best_stocks:
            best_stocks = stocks
            best_index = i
        elif stocks == best_stocks:
            # Tie – ambiguous winner
            return None

    if best_index is None or best_stocks <= 0:
        return None

    return _player_team_map.get(str(best_index))


def _is_handwarmer(full_data):
    """
    Check if the game was a handwarmer (warm-up).

    A handwarmer is detected when any player has 2 or more self_destructs
    AND the game ended with at least 21600 frames remaining on the timer.
    The remaining_frames value is captured from the moment the first player's
    stocks hit 0, before the timer is reset.
    """
    players = full_data.get('players', [])
    high_self_destructs = any(
        isinstance(p, dict) and p.get('self_destructs', 0) >= 2
        for p in players
    )
    if not high_self_destructs:
        return False

    # Use the stored value captured when stocks hit 0; fall back to current data if unavailable
    remaining_frames = _last_remaining_frames if _last_remaining_frames is not None else full_data.get('remaining_frames', 0)
    return remaining_frames >= 21600


def on_change(changes, full_data):
    """
    Called once per frame with all value changes.

    Args:
        changes: List of change dicts with 'path', 'old', 'new', 'type'
        full_data: Complete current game data
    """
    global _last_remaining_frames

    for change in changes:
        path = change['path']
        old_val = change['old']
        new_val = change['new']

        # Capture timer the moment a player's stocks hit 0
        if path.startswith("players[") and path.endswith("].stocks"):
            if new_val == 0 and old_val != 0:
                _last_remaining_frames = full_data.get('remaining_frames')
                print(f"[TSH Game Counter] Player stocks hit 0. Captured remaining_frames: {_last_remaining_frames}")

        # New game or new set – clear the stored timer value
        if path == "is_match" and old_val == False and new_val == True:
            _last_remaining_frames = None

        # Detect game conclusion
        if path == "is_match" and old_val == True and new_val == False:
            if _is_handwarmer(full_data):
                print("[TSH Game Counter] Game concluded. Handwarmer detected, score will not be updated.")
                _last_remaining_frames = None
                continue

            winner_team = _get_winner_team(full_data)
            if winner_team:
                print(f"[TSH Game Counter] Game concluded. Winner is team {winner_team}.")
                _update_score(winner_team)
            else:
                print("[TSH Game Counter] Game concluded. No clear winner detected (tie or insufficient data).")
            _last_remaining_frames = None

        # Detect set conclusion
        if path.startswith("players[") and path.endswith("].name"):
            # Player names have been changed, this is likely the start of a new set.
            _last_remaining_frames = None
            _reset_scores()


# Plugin metadata
PLUGIN_NAME = "TSH Game Counter"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Automatically updates TSH scoreboard when a game concludes."
