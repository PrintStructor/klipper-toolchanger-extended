#!/usr/bin/env python3
"""
Save a value to Klipper config via Moonraker API
Uses RUN_SHELL_COMMAND with a special Python extension script
"""
import requests
import sys
import json

MOONRAKER_BASE = "http://localhost:7125"

def save_config_value(section, option, value):
    """Save a config value using Moonraker's configfile API"""
    try:
        # Use a gcode macro that calls a Python extension
        # This uses the extended_macro approach to access configfile
        gcode = f"_TC_SAVE_CONFIG SECTION=\"{section}\" OPTION=\"{option}\" VALUE=\"{value}\""
        
        response = requests.post(
            f"{MOONRAKER_BASE}/printer/gcode/script",
            json={"script": gcode},
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"Successfully saved [{section}] {option} = {value}")
            return 0
        else:
            print(f"ERROR: Failed to save config: {response.status_code}", file=sys.stderr)
            return 1
            
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

def main():
    if len(sys.argv) != 4:
        print("Usage: tc_save_config_value.py <section> <option> <value>", file=sys.stderr)
        sys.exit(1)
    
    section = sys.argv[1]
    option = sys.argv[2]
    value = sys.argv[3]
    
    sys.exit(save_config_value(section, option, value))

if __name__ == "__main__":
    main()
