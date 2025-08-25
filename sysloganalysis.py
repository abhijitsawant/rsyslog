import os
import json
import time
import re
from datetime import datetime
from multiprocessing import Pool, cpu_count
from collections import defaultdict

def process_file(file_path):
    connections = 0
    sessionClose = 0
    parsedSessionClose = 0
    flow_dict = defaultdict(int)  # Use dictionary for O(1) lookups instead of O(n) list scanning
    totalSizeProcessed = os.path.getsize(file_path)
    
    # Pre-compile regex patterns for faster matching
    rt_flow_pattern = re.compile(r"RT_FLOW_SESSION_CLOSE")
    colon_split_pattern = re.compile(r":")
    space_split_pattern = re.compile(r"\s+")
    ip_port_pattern = re.compile(r"(.+?)/(\d+)->(.+?)/(\d+)")
    protocol_pattern = re.compile(r"protocol\s+(\S+)")

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            connections += 1
            if rt_flow_pattern.search(line):
                sessionClose += 1
                temp = colon_split_pattern.split(line, 5)  # Only split first 5 colons
                
                if len(temp) > 5 and temp[3].strip() == "RT_FLOW_SESSION_CLOSE":
                    parsedSessionClose += 1
                    try:
                        # Parse device ID more efficiently
                        device_parts = space_split_pattern.split(temp[2].strip())
                        deviceId = device_parts[1] if len(device_parts) > 1 else "unknown"
                        
                        # Parse timestamp more efficiently
                        timestamp_parts = space_split_pattern.split(temp[0].strip())
                        if len(timestamp_parts) >= 5:
                            timestamp = f"{timestamp_parts[1]}-{timestamp_parts[0]} {timestamp_parts[2]}:{timestamp_parts[3]}:{timestamp_parts[4]}"
                        else:
                            timestamp = "unknown"
                        
                        # Parse session closure reason
                        session_reason = temp[4].strip()
                        if "session closed" in session_reason:
                            sessionClosureReason = session_reason.split("session closed")[1].strip()
                        else:
                            sessionClosureReason = "unknown"
                        
                        # Parse IP/port information using regex
                        ip_port_match = ip_port_pattern.search(temp[5])
                        if ip_port_match:
                            sourceIP = ip_port_match.group(1)
                            destinationIP = ip_port_match.group(3)
                            destinationPort = ip_port_match.group(4)
                        else:
                            continue  # Skip if we can't parse IP/port
                        
                        # Parse protocol
                        protocol_match = protocol_pattern.search(temp[5])
                        protocol = protocol_match.group(1) if protocol_match else "unknown"
                        
                        # Create unique key and count in dictionary
                        key = f"{deviceId}_{sourceIP}_{destinationIP}_{destinationPort}_{protocol}"
                        flow_dict[key] += 1
                        
                    except Exception as e:
                        continue
    
    # Convert dictionary to flow list format
    flowList = []
    for key, count in flow_dict.items():
        key_parts = key.split('_')
        if len(key_parts) >= 5:
            flowList.append({
                "key": key,
                "timestamp": "aggregated",  # We lose individual timestamps with this approach
                "deviceId": key_parts[0],
                "sessionClosureReason": "aggregated",  # We lose individual reasons
                "sourceIP": key_parts[1],
                "destinationIP": key_parts[2],
                "destinationPort": key_parts[3],
                "protocol": key_parts[4],
                "count": count
            })

    return {
        "connections": connections,
        "sessionClose": sessionClose,
        "parsedSessionClose": parsedSessionClose,
        "flowList": flowList,
        "totalSizeProcessed": totalSizeProcessed
    }

def extract_fields_parallel(sourceDir):
    start_time = time.time()
    
    # Get all files with proper filtering
    file_paths = []
    for f in os.listdir(sourceDir):
        full_path = os.path.join(sourceDir, f)
        if os.path.isfile(full_path) and not f.startswith('.'):  # Skip hidden files
            file_paths.append(full_path)
    
    # Use imap_unordered for better memory efficiency with large files
    with Pool(min(cpu_count(), len(file_paths) or 1)) as pool:
        results = list(pool.imap_unordered(process_file, file_paths))

    # Aggregate results more efficiently
    connections = 0
    sessionClose = 0
    parsedSessionClose = 0
    totalSizeProcessed = 0
    combined_flows = defaultdict(int)
    
    for r in results:
        connections += r["connections"]
        sessionClose += r["sessionClose"]
        parsedSessionClose += r["parsedSessionClose"]
        totalSizeProcessed += r["totalSizeProcessed"]
        
        for flow in r["flowList"]:
            combined_flows[flow["key"]] += flow["count"]
    
    # Convert back to list format
    flowList = []
    for key, count in combined_flows.items():
        key_parts = key.split('_')
        if len(key_parts) >= 5:
            flowList.append({
                "key": key,
                "timestamp": "aggregated",
                "deviceId": key_parts[0],
                "sessionClosureReason": "aggregated",
                "sourceIP": key_parts[1],
                "destinationIP": key_parts[2],
                "destinationPort": key_parts[3],
                "protocol": key_parts[4],
                "count": count
            })

    elapsedTime = time.time() - start_time
    
    stats = {
        "totalConnections": connections,
        "totalSessionClosures": sessionClose,
        "sessionClosurePercent": f"{(sessionClose / connections) * 100:.2f}%" if connections else "0.00%",
        "parsedSessionClosure": parsedSessionClose,
        "parsedSuccessRate": f"{(parsedSessionClose / sessionClose) * 100:.2f}%" if sessionClose else "0.00%",
        "flows": len(flowList)
    }

    performance = {
        "startTime": start_time,
        "endTime": time.time(),
        "elapsedTime": elapsedTime,
        "totalConnections": connections,
        "totalSizeProcessed": f"{totalSizeProcessed/(1024*1024*1024):.2f}GB",
        "processingPerformance": {
            "connectionsPerSecond": f"{connections/elapsedTime:.2f} connections/second",
            "sizePerSecond": f"{totalSizeProcessed/(elapsedTime * 1024*1024*1024):.2f} GB/second" if elapsedTime > 0 else "0.00 GB/second"
        }
    }

    response = {
        "responseHeader": {
            "type": "parsingOnly",
            "performance": performance,
            "sessionStats": stats
        },
        "flows": flowList
    }

    return response

def write_output_file(response, output_path, encoding):
    try:
        # Write in chunks to handle large files
        with open(output_path, 'w', encoding=encoding) as output_file:
            json.dump(response, output_file, indent=4)
        return "Write op succeeded"
    except Exception as e:
        return f"Write op failed: {str(e)}"

def generate_output_filename(output_dir):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(output_dir, f"v9_output_{timestamp}.json")

if __name__ == "__main__":
    response = extract_fields_parallel("syslog")
    outputPath = generate_output_filename("output")
    print(json.dumps(response["responseHeader"], indent=4))
    write_output_file(response, outputPath, "utf-8")
