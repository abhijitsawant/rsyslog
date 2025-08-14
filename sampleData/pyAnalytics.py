import os
import re

# Directory containing syslog files
log_dir = "./syslogs"

# Regex to capture source-address value inside quotes
pattern_source_address = re.compile(r'source-address="([^"]+)"')
pattern_destination_address = re.compile(r'destination-address="([^"]+)"')

# Loop through all files in the directory
local_counter = 0
for filename in os.listdir(log_dir):
    file_path = os.path.join(log_dir, filename)
    print(file_path)
    # Skip directories
    if not os.path.isfile(file_path):
        continue

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            local_counter += 1
            if "RT_FLOW_SESSION_CLOSE" in line:
                match_source_address = pattern_source_address.search(line)
                match_destination_address = pattern_destination_address.search(line)
                #if match_source_address and match_destination_address:
                #    print(f"[{local_counter}] {filename}: {match_source_address.group(1)} -> {match_destination_address.group(1)}")

