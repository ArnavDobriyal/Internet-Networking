#!/bin/bash

# Configuration
LOG_DIR="$HOME/system_health_logs"  # Logs will be stored in your home directory
LOG_FILE="$LOG_DIR/health_report_$(date +%Y%m%d_%H%M%S).log"
MAX_LOG_FILES=5  # Keep only the last 5 logs

# Step 1: Create the log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Step 2: Start logging system health information
echo "===== System Health Report - $(date) =====" | tee "$LOG_FILE"

# Step 3: Log CPU Usage
echo -e "\nCPU Usage:" | tee -a "$LOG_FILE"
top -bn1 | grep "Cpu(s)" | tee -a "$LOG_FILE"

# Step 4: Log Memory Usage
echo -e "\nMemory Usage:" | tee -a "$LOG_FILE"
free -h | tee -a "$LOG_FILE"

# Step 5: Log Disk Usage
echo -e "\nDisk Usage:" | tee -a "$LOG_FILE"
df -h | tee -a "$LOG_FILE"

# Step 6: Log System Uptime
echo -e "\nSystem Uptime:" | tee -a "$LOG_FILE"
uptime | tee -a "$LOG_FILE"

# Step 7: Log Top 5 Processes by CPU Usage
echo -e "\nTop 5 Processes by CPU Usage:" | tee -a "$LOG_FILE"
ps -eo pid,ppid,cmd,%cpu,%mem --sort=-%cpu | head -n 6 | tee -a "$LOG_FILE"

# Step 8: Clean up old logs (keep only the last 5 logs)
echo "Cleaning up old logs..." | tee -a "$LOG_FILE"
find "$LOG_DIR" -name "health_report_*.log" -type f | sort -r | tail -n +$((MAX_LOG_FILES + 1)) | xargs rm -f

# Step 9: Notify the user
echo "System health report generated: $LOG_FILE" | tee -a "$LOG_FILE"
