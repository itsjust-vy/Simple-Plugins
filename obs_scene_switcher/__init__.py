#!/usr/bin/env python3
"""
OBS Scene Switcher Plugin for Simple
Changes scenes based on the state of the game.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils import get_plugin_setting

import obsws_python as obs

# Load settings once at module load
_obs_host = get_plugin_setting('obs_scene_switcher', 'obs_host', 'localhost')
_obs_port = get_plugin_setting('obs_scene_switcher', 'obs_port', 4455)
_obs_password = get_plugin_setting('obs_scene_switcher', 'obs_password', '')

def _switch_scene(scene_name):
    """Switch to specified OBS scene."""
    try:
        client = obs.ReqClient(host=_obs_host, port=_obs_port, password=_obs_password)
        client.set_current_program_scene(scene_name)
        client.disconnect()
        print(f"[OBS Scene Switcher] Switched to scene: {scene_name}")
    except Exception as e:
        print(f"[OBS Scene Switcher] Failed to switch scene: {e}")

def on_change(changes, full_data):
    """
    Called once per frame with all value changes.
    
    Args:
        changes: List of change dicts with 'path', 'old', 'new', 'type'
        full_data: Complete current game data
    """
    for change in changes:
        path = change['path']
        old_val = change['old']
        new_val = change['new']
        
        # Check if the game has started
        if path.startswith("players[") and path.endswith("].is_in_game") and new_val == True and full_data.get('is_match') == True:
            print("[OBS] Match started! Switching to gameplay scene.")
            _switch_scene(get_plugin_setting('obs_scene_switcher', 'scenes', {}).get('in_game'))

        # Check if the game has finished
        if path == "is_match":
            if new_val == False:
                print("[OBS] Match ended! Switching to after-game scene.")
                _switch_scene(get_plugin_setting('obs_scene_switcher', 'scenes', {}).get('after_game'))

# Plugin metadata
PLUGIN_NAME = "OBS Scene Switcher"
PLUGIN_VERSION = "0.1.0"
PLUGIN_DESCRIPTION = "Automatically switches OBS scenes based on game state."
