#!/bin/bash
# Liest Beacon Contact aus temporärer Datei und speichert via TOOL_SAVE_Z_OFFSET

TOOL=$1

if [ -z "$TOOL" ]; then
    echo "ERROR: Tool number required" >&2
    exit 1
fi

TEMP_FILE="/tmp/beacon_contact_t${TOOL}.txt"

if [ ! -f "$TEMP_FILE" ]; then
    echo "ERROR: Temp file not found: $TEMP_FILE" >&2
    exit 1
fi

CONTACT=$(cat "$TEMP_FILE")

if [ -z "$CONTACT" ] || [ "$CONTACT" = "ERROR" ]; then
    echo "ERROR: Invalid contact value in $TEMP_FILE" >&2
    exit 1
fi

# Kurze Wartezeit, damit Klipper/Moonraker die vorherige Operation abschließen kann
sleep 0.5

# Hole das Initial Tool aus globals.current_tool
INITIAL_TOOL_JSON=$(curl -s "http://localhost:7125/printer/objects/query?gcode_macro%20globals" 2>/dev/null)
INITIAL_TOOL=$(echo "$INITIAL_TOOL_JSON" | grep -o '"current_tool": *[0-9]*' | grep -o '[0-9]*' | head -1)

# Fallback auf 0 wenn nicht gefunden
if [ -z "$INITIAL_TOOL" ]; then
    INITIAL_TOOL=0
fi

# Verwende TC_SAVE_CONFIG_VALUE Befehl aus tc_config_helper Modul
# Dieser ruft configfile.set() auf, sodass SAVE_CONFIG den Wert in printer.cfg schreibt

# Construct G-code command
GCODE="TC_SAVE_CONFIG_VALUE SECTION=\"tool T${INITIAL_TOOL}\" OPTION=\"t${TOOL}_z_offset\" VALUE=\"${CONTACT}\""

# Escape quotes for JSON (replace " with \")
GCODE_ESCAPED=$(echo "$GCODE" | sed 's/"/\\"/g')

# Build JSON payload
JSON_PAYLOAD="{\"script\":\"${GCODE_ESCAPED}\"}"

MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    RESPONSE=$(curl -s --max-time 10 -X POST "http://localhost:7125/printer/gcode/script" \
        -H "Content-Type: application/json" \
        -d "$JSON_PAYLOAD" 2>&1)
    
    CURL_EXIT=$?
    
    if [ $CURL_EXIT -eq 0 ]; then
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
        sleep 1
    fi
done

if [ $CURL_EXIT -ne 0 ]; then
    echo "ERROR: curl failed after $MAX_RETRIES attempts (exit code $CURL_EXIT)" >&2
    echo "Response: $RESPONSE" >&2
    exit 1
fi

# Note: TC_SAVE_CONFIG_VALUE already outputs a "Saved..." message, so we don't need to echo here
exit 0
