#!/usr/bin/env python3
"""
Toolchanger Beacon Contact Value Capture
Uses Moonraker API to parse BEACON_OFFSET_COMPARE outputs
"""

import requests
import re
import time
import sys
import json

# Moonraker Base URL (Standard Port 7125)
MOONRAKER_BASE = "http://localhost:7125"

def capture_beacon_contact(tool_number):
    """
    Read Contact value from gcode_store (TC_BEACON_MARKER must be set beforehand)
    
    Args:
        tool_number (int): Tool number (0 to max_tool_count-1, see toolchanger config)
        
    Returns:
        float: Contact value in mm, or None on error
    """
    try:
        # Fetch gcode store
        response = requests.get(
            f"{MOONRAKER_BASE}/server/gcode_store",
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"ERROR: Failed to get gcode_store: {response.status_code}", file=sys.stderr)
            return None
        
        store = response.json()["result"]["gcode_store"]
        
        # Search backwards: FIRST find marker, THEN read Contact line
        contact_value = None
        found_marker = False
        
        for item in reversed(store):
            msg = item.get("message", "")
            
            # 1. First find marker (comes FIRST in reversed iteration)
            if not found_marker and f"TC_BEACON_MARKER: tool={tool_number}" in msg:
                found_marker = True
                continue
            
            # 2. Then search for Contact line (comes AFTER marker in reversed iteration)
            if found_marker and contact_value is None and "Contact:" in msg:
                # Regex: "// Contact:   0.25433 mm" or "// Contact:   -0.21752 mm"
                match = re.search(r"//\s*Contact:\s+([-0-9.]+)\s*mm", msg)
                if match:
                    contact_value = float(match.group(1))
                    break
        
        if not found_marker:
            print(f"ERROR: Marker 'TC_BEACON_MARKER: tool={tool_number}' not found in gcode_store", file=sys.stderr)
            return None
        
        if contact_value is None:
            print(f"ERROR: Contact value not found before marker for tool {tool_number}", file=sys.stderr)
            return None
        
        return contact_value
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        return None


def main():
    """
    Main function - expects tool number as argument
    Reads Contact value and writes it to temporary file
    """
    if len(sys.argv) != 2:
        print("Usage: tc_beacon_capture.py <tool_number>", file=sys.stderr)
        sys.exit(1)
    
    try:
        tool_number = int(sys.argv[1])
        if not 0 <= tool_number <= 5:
            print(f"ERROR: Tool number must be between 0 and 5, got {tool_number}", file=sys.stderr)
            sys.exit(1)
    except ValueError:
        print(f"ERROR: Invalid tool number: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
    
    # Capture Beacon Contact value
    contact_value = capture_beacon_contact(tool_number)
    
    if contact_value is None:
        sys.exit(1)
    
    # Write value to temporary file (macro reads this later)
    temp_file = f"/tmp/beacon_contact_t{tool_number}.txt"
    try:
        with open(temp_file, 'w') as f:
            f.write(f"{contact_value:.6f}")
        print(f"Contact: {contact_value:.6f} mm → {temp_file}")
    except Exception as e:
        print(f"ERROR: Failed to write temp file: {e}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
