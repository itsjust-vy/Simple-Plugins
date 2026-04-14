#!/usr/bin/env python3
"""
Stock Notifier Plugin for Simple
Prints to console when a player loses a stock.
Uses on_values_changed for efficient batched processing.
"""

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
        
        # Check if this is a stock change
        if path.startswith("players[") and path.endswith("].stocks"):
            if old_val is not None and new_val is not None and new_val < old_val:
                player_index = path.split("[")[1].split("]")[0]
                
                # Get player name if available
                player_data = full_data.get('players', [])[int(player_index)] if full_data.get('players') else None
                player_name = player_data.get('name', f"Player {player_index}") if player_data else f"Player {player_index}"
                
                stocks_lost = old_val - new_val
                print(f"Player {player_index} ({player_name}) lost {stocks_lost} stock{'s' if stocks_lost > 1 else ''}! Remaining: {new_val}")

# Plugin metadata
PLUGIN_NAME = "Stock Notifier"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Notifies when players lose stocks."
