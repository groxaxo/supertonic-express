#!/bin/bash

CONTAINER_NAME="supertonic-app"
OUTPUT_FILE="resource_usage.log"

echo "Timestamp, CPU %, Mem Usage, Mem %, Net I/O, Block I/O, PIDs" > "$OUTPUT_FILE"

echo "Monitoring container: $CONTAINER_NAME"
echo "Logging to: $OUTPUT_FILE"

while true; do
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    STATS=$(docker stats --no-stream --format "{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}},{{.PIDs}}" "$CONTAINER_NAME" 2>/dev/null)
    
    if [ -n "$STATS" ]; then
        echo "$TIMESTAMP, $STATS" >> "$OUTPUT_FILE"
        echo "$TIMESTAMP: $STATS"
    else
        echo "$TIMESTAMP: Container not running or stats unavailable"
    fi
    sleep 1
done
