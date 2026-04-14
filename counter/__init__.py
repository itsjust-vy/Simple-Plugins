#!/usr/bin/env python3
"""
Counter Plugin for Simple
Tracks and prints how many times on_change and on_frame have been called.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils import get_plugin_setting

# Track call counts
_change_count = 0
_frame_count = 0

# Get interval
interval = get_plugin_setting('counter', 'print_interval', default=60)

def on_change(changes, full_data):
    """Called when values change - increments change counter."""
    global _change_count
    _change_count += 1

def on_frame(changes, full_data):
    """Called every frame - prints total call counts."""
    global _frame_count
    _frame_count += 1
        
    if _frame_count % interval == 0:
        print(f"[Counter] on_change calls: {_change_count} | on_frame calls: {_frame_count}")

# Plugin metadata
PLUGIN_NAME = "Hook Counter"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Tracks and displays call counts for on_change and on_frame hooks"
