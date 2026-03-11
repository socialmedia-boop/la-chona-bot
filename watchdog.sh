#!/bin/bash
# La Chona Watchdog — Auto-restart if the bot crashes
# Uses PID file to avoid conflicts with other bots

BOT_DIR="/home/ubuntu/team-culture-bot"
LOG_FILE="/home/ubuntu/la-chona.log"
PID_FILE="/tmp/la-chona.pid"

echo "🐕 La Chona Watchdog started at $(date)" >> "$LOG_FILE"

while true; do
    # Check if La Chona is running via PID file
    RUNNING=0
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            RUNNING=1
        fi
    fi

    if [ "$RUNNING" -eq 0 ]; then
        echo "⚠️  La Chona is not running. Restarting at $(date)..." >> "$LOG_FILE"
        cd "$BOT_DIR"
        python3 -u app.py >> "$LOG_FILE" 2>&1 &
        NEW_PID=$!
        echo $NEW_PID > "$PID_FILE"
        echo "✅ La Chona restarted (PID: $NEW_PID)" >> "$LOG_FILE"
    fi
    sleep 30
done
