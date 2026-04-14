#!/usr/bin/env python3
"""
Change Notifier Plugin for Simple
Prints formatted change notifications to console.
"""

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'

def on_change(changes, full_data):
    """Print formatted changes to console."""
    for change in changes:
        if change['type'] == 'new':
            print(f"  {Colors.BOLD}{Colors.MAGENTA}{change['path']}:{Colors.RESET} {Colors.GREEN}NEW:{Colors.RESET} {Colors.CYAN}{change['new']}{Colors.RESET}")
        elif change['type'] == 'removed':
            print(f"  {Colors.BOLD}{Colors.MAGENTA}{change['path']}:{Colors.RESET} {Colors.RED}REMOVED:{Colors.RESET} {Colors.RED}{change['old']}{Colors.RESET}")
        else:
            print(f"  {Colors.BOLD}{Colors.MAGENTA}{change['path']}:{Colors.RESET} {Colors.YELLOW}CHANGED:{Colors.RESET} {Colors.RED}{change['old']}{Colors.RESET} → {Colors.GREEN}{change['new']}{Colors.RESET}")

# Plugin metadata
PLUGIN_NAME = "Change Notifier"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Prints formatted change notifications to console"
