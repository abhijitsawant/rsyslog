___Syslog Host___
This setup runs a lightweight rsyslog container with automated log rotation for collecting and storing syslog messages from network devices (e.g., Juniper SRX).
Logs are stored in a timestamped format, rotated every 10 minutes, and cleaned up automatically after 48 hours.

Folder Structure
.
├── Dockerfile                 # Builds rsyslog + logrotate + cron image
├── docker-compose.yml         # Runs the rsyslog container in host network mode
├── rsyslog.conf               # Main rsyslog configuration
├── rsyslog.d/                 # (Optional) Extra rsyslog configs
└── logrotate.d/
    └── collector-a            # Log rotation rules for collector-a

<h2>How It Works</h2>
Syslog Listener

Listens on TCP port 514 for incoming logs.

Each device's logs are stored in:

swift
Copy
Edit
/var/log/db/syslog/collector-a/<hostname>_YYYYMMDD_HHMMSS.log
Log Rotation

Runs every 10 minutes using a cron job inside the container.

Keeps up to 9999 rotated files.

Deletes logs older than 48 hours automatically.

Dynamic File Naming

Uses %hostname% and %timereported% in filenames for easy traceability.

Container Resource Limits

Limited to 1 CPU core and 1 GB RAM.
