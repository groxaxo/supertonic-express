#!/bin/bash

OUTPUT_FILE="production_resources.log"
echo "Timestamp, CPU %, Mem %, GPU Util %, VRAM Used (MiB), Power (W)" > "$OUTPUT_FILE"

# Find PID more robustly
# Look for the python process running uvicorn
PID=$(pgrep -f "uvicorn api.src.main:app" | head -n 1)

if [ -z "$PID" ]; then
    echo "Server process not found! Waiting for it to start..."
    sleep 5
    PID=$(pgrep -f "uvicorn api.src.main:app" | head -n 1)
fi

if [ -z "$PID" ]; then
    echo "Server process still not found. Exiting."
    exit 1
fi

echo "Monitoring PID: $PID"
echo "Logging to: $OUTPUT_FILE"

while true; do
    if ! kill -0 "$PID" 2>/dev/null; then
        echo "Process $PID exited."
        break
    fi

    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    
    # CPU and Mem from ps
    SYS_STATS=$(ps -p "$PID" -o %cpu,%mem --no-headers | awk '{print $1 "," $2}')
    
    # GPU Stats from nvidia-smi
    GPU_STATS=$(nvidia-smi --query-gpu=utilization.gpu,memory.used,power.draw --format=csv,noheader,nounits | head -n 1 | awk -F', ' '{print $1 "," $2 "," $3}')
    
    echo "$TIMESTAMP, $SYS_STATS, $GPU_STATS" >> "$OUTPUT_FILE"
    
    sleep 1
done
