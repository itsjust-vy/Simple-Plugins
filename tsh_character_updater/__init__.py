#!/usr/bin/env python3
"""
TSH Character Updater Plugin for Simple
Automatically pushes character and skin/costume changes to TournamentStreamHelper.

Watches for player character and skin changes, then POSTs the updated data to
TSH's built-in web server so the scoreboard overlay stays in sync.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils import get_plugin_setting, get_character_name

import json
from urllib.request import Request, urlopen
from urllib.error import URLError

# Load settings once at module load
_tsh_host = get_plugin_setting('tsh_character_updater', 'tsh_host', 'localhost')
_tsh_port = get_plugin_setting('tsh_character_updater', 'tsh_port', 5000)
_scoreboard_number = get_plugin_setting('tsh_character_updater', 'scoreboard_number', 1)
_player_team_map = get_plugin_setting('tsh_character_updater', 'player_team_map', {
    "0": {"team": 1, "player": 1},
    "1": {"team": 2, "player": 1}
})
_skin_offset = get_plugin_setting('tsh_character_updater', 'skin_offset', 0)

print(f"[TSH Character Updater] Plugin loaded. Host={_tsh_host}:{_tsh_port} Scoreboard={_scoreboard_number} Map={_player_team_map} SkinOffset={_skin_offset}")


def _send_update(player_index, character_name, skin):
    """POST character/skin data to TSH for the mapped team/player."""
    print(f"[TSH Character Updater] _send_update called for player {player_index} with char='{character_name}' skin={skin}")

    mapping = _player_team_map.get(str(player_index))
    if not mapping:
        print(f"[TSH Character Updater] No team mapping for player {player_index}, skipping.")
        return

    team = mapping.get("team")
    player = mapping.get("player")
    if team is None or player is None:
        print(f"[TSH Character Updater] Invalid mapping for player {player_index}: {mapping}")
        return

    payload = {
        "mains": {
            "ssbu": [
                [character_name, skin + _skin_offset]
            ]
        }
    }

    url = f"http://{_tsh_host}:{_tsh_port}/scoreboard{_scoreboard_number}-update-team-{team}-{player}"
    body = json.dumps(payload).encode('utf-8')
    req = Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')

    print(f"[TSH Character Updater] POST {url} payload={payload}")

    try:
        with urlopen(req, timeout=2) as response:
            result = response.read().decode()
            print(f"[TSH Character Updater] SUCCESS: player {player_index} -> team {team}, player {player}: TSH responded '{result}'")
    except URLError as e:
        print(f"[TSH Character Updater] URLError for player {player_index}: {e}")
    except Exception as e:
        print(f"[TSH Character Updater] Unexpected error for player {player_index}: {e}")


def on_change(changes, full_data):
    """
    Called once per change with all value changes.
    Sends updated character and skin data to TSH whenever they change in-game.
    """
    players = full_data.get('players', [])
    print(f"[TSH Character Updater] on_change fired. {len(changes)} change(s), {len(players)} player(s)")

    dirty_players = set()

    for i, change in enumerate(changes):
        path = change['path']
        old_val = change.get('old')
        new_val = change.get('new')
        print(f"[TSH Character Updater] Change {i}: path='{path}' old={old_val} new={new_val}")

        if not path.startswith("players["):
            print(f"[TSH Character Updater]   -> skipped: not a player path")
            continue

        if not (path.endswith("].character") or path.endswith("].skin")):
            print(f"[TSH Character Updater]   -> skipped: not character/skin")
            continue

        try:
            player_index = int(path.split("[")[1].split("]")[0])
        except (IndexError, ValueError) as e:
            print(f"[TSH Character Updater]   -> skipped: cannot parse index from '{path}' ({e})")
            continue

        if player_index >= len(players):
            print(f"[TSH Character Updater]   -> skipped: index {player_index} out of range (len={len(players)})")
            continue

        player = players[player_index]
        if not isinstance(player, dict):
            print(f"[TSH Character Updater]   -> skipped: players[{player_index}] is not a dict ({type(player)})")
            continue

        # is_in_game = player.get('is_in_game', False)
        # if not is_in_game:
        #     print(f"[TSH Character Updater]   -> skipped: players[{player_index}] is_in_game={is_in_game}")
        #     continue

        character_id = player.get('character')
        if character_id == 0 or character_id is None:
            print(f"[TSH Character Updater]   -> skipped: players[{player_index}] character={character_id}")
            continue

        print(f"[TSH Character Updater]   -> ACCEPTED: players[{player_index}] will be updated")
        dirty_players.add(player_index)

    print(f"[TSH Character Updater] Dirty players: {dirty_players if dirty_players else 'none'}")

    for player_index in dirty_players:
        player = players[player_index]
        character_name = get_character_name(player['character'])
        skin = player.get('skin', 0)
        print(f"[TSH Character Updater] Preparing update for player {player_index}: character_id={player['character']} resolved='{character_name}' skin={skin}")
        _send_update(player_index, character_name, skin)


# def on_frame(changes, full_data):
#     """
#     Called every frame. Syncs all in-game players on initial load/reconnect.
#     """
#     if '_initial_sync_done' in globals():
#         return

#     players = full_data.get('players', [])
#     for i, player in enumerate(players):
#         if not isinstance(player, dict):
#             continue
#         if not player.get('is_in_game', False):
#             continue

#         character_id = player.get('character')
#         if character_id == 0 or character_id is None:
#             continue

#         character_name = get_character_name(character_id)
#         skin = player.get('skin', 0)
#         _send_update(i, character_name, skin)

#     globals()['_initial_sync_done'] = True


# Plugin metadata
PLUGIN_NAME = "TSH Character Updater"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Pushes character and skin/costume changes to TSH in real-time."
