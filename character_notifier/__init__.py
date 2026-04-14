#!/usr/bin/env python3
"""
Character Notifier Plugin for Simple
Prints the character name when a player switches characters.
Uses on_update for efficient batched processing.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils import get_character_name

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
        
        # Check if this is a character change
        if path.startswith("players[") and path.endswith("].character"):
            if old_val != new_val and new_val is not None:
                player_index = path.split("[")[1].split("]")[0]
                character_name = get_character_name(new_val)
                print(f"Player {player_index} is now playing as {character_name}!")

# Plugin metadata
PLUGIN_NAME = "Character Notifier"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Prints character names when players switch characters."
