#!/bin/bash

# Configuration
#!/bin/bash

# Configuration
LOG_FILE=#!/bin/bash
set -x  # Debugging output

# Configuration
LOG_FILE="/home/akaifyb/logs_code/app_log.txt" 

# Task 1: Filter entries for user "John"
 grep "User: John" app_log.txt

# Task 2: Correct typographical errors (replace 'Loogin' with 'Login')
sed -i 's/Loogin/Login/g' app_log.txt

# Task 3: Find failed actions and include context
# Define the output file where the results will be saved
OUTPUT_FILE="failed_actions_with_context.log"
# Find failed actions and extract two lines before and after each failure
grep -n "Status: Failed" app_log.txt | cut -d: -f1 | while read line_num; do
    # Show two lines before and after each failed action (adjust line numbers)
    sed -n "$((line_num-2)),$((line_num+2))p" app_log.txt
    # Add a gap (empty line) between each result
    echo ""
done | tee "$OUTPUT_FILE"

# Task 4: Summarize user activities (only user and action)
 awk -F"User: | Action: " '{if($2 != "") actions[$2] = actions[$2] $3 "\n"} END {for (user in actions) print "User: " user "\nActions:\n" actions[user] "\n"}' app_log.txt | tee user_activities_summary.log

# Task 5: Aggregate failed actions from all log files in the directory
grep -H "Status: Failed" app_log.txt > aggregated_failed_actions.log


