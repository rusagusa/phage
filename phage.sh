#!/bin/bash
# PHAGE MUSCLE V2.4: FIXED EXEC + VOICE RESPONSE + SWARM
# 🧬 "The Decentralized Swarm Muscle"

# 1. SETUP: Ask for Device ID if not set
if [ -z "$DEVICE_ID" ]; then
    echo "🧬 Phage Protocol: Enter your DEVICE_ID (e.g., node_02): "
    read -r DEVICE_ID
fi

# exec > >(tee -a /sdcard/Download/phage.log) 2>&1
# URL="https://phage-gatway-343327310617.europe-west1.run.app"
URL="YOUR_CLOUD_RUN_URL"
STATE="IDLE"

echo "🧬 Phage Muscle Swarm [v2.4 - THE FIX] Online ($DEVICE_ID)"

# 🛡️ Watchdog
cleanup_hangs() {
    pkill -f "uiautomator dump" 2>/dev/null
    pkill -f "adb shell" 2>/dev/null
    pkill -f "screencap" 2>/dev/null
}

# 🎙️ Ambient Awareness
ambient_poll() {
    if [ "$STATE" == "AWAKE" ]; then
        echo "🎙️ Sampling..."
        termux-microphone-record -d 2 -f /sdcard/Phage/ambient.mp3 >/dev/null 2>&1
        sleep 2
        termux-microphone-record -q
        curl -s -X POST -F "audio=@/sdcard/Phage/ambient.mp3" -F "device_id=$DEVICE_ID" -F "ambient=true" "$URL" > /dev/null
    fi
}

while true; do
    cleanup_hangs
    ITERATION=$((ITERATION + 1))
    if [ $((ITERATION % 20)) -eq 0 ]; then
        BATTERY=$(termux-battery-status 2>/dev/null | jq -r '.percentage' 2>/dev/null || echo 0)
        curl -s -X POST -H "Content-Type: application/json" \
             -d "{\"heartbeat\": true, \"battery\": $BATTERY, \"device_id\": \"$DEVICE_ID\"}" \
             "$URL"
    fi

    # 🎙️ Ambient Awareness (Sample occasionally)
    if [ $((ITERATION % 5)) -eq 0 ]; then
        ambient_poll
    fi

    # 2. Executive Poll (Polling with device_id)
    RESPONSE=$(timeout 10s curl -s -S "$URL?device_id=$DEVICE_ID" 2>/dev/null)
    
    if [[ "$RESPONSE" == {* ]]; then
        STATE="AWAKE"
        COMMAND=$(echo "$RESPONSE" | jq -r '.command // empty')
        REASON=$(echo "$RESPONSE" | jq -r '.reason // empty')
        CONTINUE=$(echo "$RESPONSE" | jq -r '.continue // empty')
        ORIGIN_CHAT_ID=$(echo "$RESPONSE" | jq -r '.chat_id // empty')

        if [ -n "$COMMAND" ] && [ "$COMMAND" != "null" ]; then
            echo "📥 BRAIN [v2.4]: $REASON"
            
            # --- VISION PROTOCOL EXECUTION ---
            if [ "$COMMAND" == "read_screen" ]; then
                echo "📸 Vision Protocol Initiated..."
                # Grab XML
                timeout 15s adb shell uiautomator dump /sdcard/uidump.xml > /dev/null 2>&1
                adb pull /sdcard/uidump.xml ./uidump.xml > /dev/null 2>&1
                # Grab Screenshot
                timeout 10s adb shell screencap -p /sdcard/screen.png > /dev/null 2>&1
                adb pull /sdcard/screen.png ./screen.png > /dev/null 2>&1
                # Upload both
                curl -s -X POST -F "xml_map=@./uidump.xml" -F "image=@./screen.png" -F "device_id=$DEVICE_ID" -F "chat_id=$ORIGIN_CHAT_ID" "$URL"
            else
                echo "🧬 Executing: $COMMAND"
                # THE FIX: Avoid 'eval' inside timeout directly. Use bash -c explicitly.
                EXEC_OUTPUT=$(timeout --foreground 30s bash -c "$COMMAND" 2>&1)
                EXIT_CODE=$?
                
                # Report back to the specific user chat
                curl -s -X POST -H "Content-Type: application/json" \
                     -d "{\"terminal_sync\": \"$EXEC_OUTPUT\", \"exit_code\": \"$EXIT_CODE\", \"command\": \"$COMMAND\", \"device_id\": \"$DEVICE_ID\", \"chat_id\": \"$ORIGIN_CHAT_ID\"}" \
                     "$URL"
            fi
            
            if [ "$CONTINUE" == "true" ]; then
                continue
            fi
        fi
    else
        STATE="IDLE"
    fi

    sleep 2
done