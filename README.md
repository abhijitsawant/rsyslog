<h1>Syslog Host</h1>

<p>
This repository contains a Docker-based setup for running an <strong>Rsyslog</strong> server with 
<em>log rotation</em> and <em>automatic cleanup</em> using <code>logrotate</code> and <code>cron</code>.
It listens on TCP port <code>514</code>, stores logs by hostname and timestamp, and rotates them hourly.
</p>

<h2>Project Structure</h2>

<pre>
.
├── rsyslog.conf                # Main Rsyslog configuration
├── Dockerfile                   # Docker build instructions
├── docker-compose.yml           # Docker Compose configuration
├── rsyslog.d/                   # Additional rsyslog configs (currently empty)
└── logrotate.d/
    └── collector-a              # Log rotation policy
</pre>

<h2>Configuration Files</h2>

<h3>1. rsyslog.conf</h3>
<p>Configures Rsyslog to:</p>
<ul>
  <li>Listen for syslog messages over TCP on port <code>514</code>.</li>
  <li>Save logs in <code>/var/log/db/syslog/collector-a/</code> with filenames based on hostname and timestamp.</li>
  <li>Store the <strong>raw</strong> message without modification.</li>
</ul>

<pre>
module(load="imtcp")
input(type="imtcp" port="514")

template(name="CustomLogFile" type="string"
  string="/var/log/db/syslog/collector-a/%hostname%_%timereported:1:10:date-rfc3339%%timereported:11:8:date-rfc3339%.log"
)

template(name="RawSRXLog" type="string" string="%rawmsg%\n")

*.* action(
  type="omfile"
  DynaFile="CustomLogFile"
  template="RawSRXLog"
  FileCreateMode="0644"
)
</pre>

<h3>2. Dockerfile</h3>
<p>Builds a container with:</p>
<ul>
  <li>Ubuntu 22.04 base image</li>
  <li>Rsyslog, Logrotate, Cron</li>
  <li>A cron job running logrotate every 10 minutes</li>
</ul>

<pre>
FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y rsyslog logrotate cron && \
    rm -rf /var/lib/apt/lists/*

RUN echo "*/10 * * * * root /usr/sbin/logrotate -f /etc/logrotate.d/collector-a" \
    > /etc/cron.d/logrotate-collector-a && \
    chmod 0644 /etc/cron.d/logrotate-collector-a

RUN touch /var/log/cron.log

CMD service cron start && rsyslogd -n
</pre>

<h3>3. docker-compose.yml</h3>
<p>Runs the Rsyslog container with:</p>
<ul>
  <li>Host network mode</li>
  <li>Automatic restart</li>
  <li>CPU and memory limits</li>
  <li>Mounted volumes for configs and logs</li>
</ul>

<pre>
version: '3.8'
services:
  rsyslog:
    build: .
    container_name: rsyslog
    restart: always
    network_mode: "host"
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1g
    volumes:
      - ./rsyslog.conf:/etc/rsyslog.conf:ro
      - /var/log/db/syslog/collector-a:/var/log/db/syslog/collector-a
      - ./logrotate.d/collector-a:/etc/logrotate.d/collector-a:ro
</pre>

<h3>4. logrotate.d/collector-a</h3>
<p>Defines rotation policy:</p>
<ul>
  <li>Rotate hourly</li>
  <li>Keep up to 9999 rotations</li>
  <li>Delete logs older than 2 days</li>
  <li>Use timestamp in rotated filenames</li>
</ul>

<pre>
/var/log/db/syslog/collector-a/*.log {
    rotate 9999
    missingok
    notifempty
    size 0
    minsize 1
    maxage 1
    su root root
    copytruncate
    dateext
    dateformat _%Y%m%d_%H%M%S
    hourly
    create 0644 root root
    postrotate
        /usr/bin/find /var/log/db/syslog/collector-a/ -type f -mmin +2880 -delete
    endscript
}
</pre>

<h2>Usage</h2>

<ol>
  <li>Clone this repository:
    <pre>git clone &lt;repo-url&gt; && cd test3</pre>
  </li>
  <li>Build and start the container:
    <pre>docker compose up --build -d</pre>
  </li>
  <li>Send syslog messages to TCP port <code>514</code> of the host.</li>
  <li>Logs will be stored in:
    <pre>/var/log/db/syslog/collector-a/</pre>
  </li>
</ol>

<h2>Notes</h2>
<ul>
  <li>Requires root privileges to bind to port 514.</li>
  <li>Ensure <code>/var/log/db/syslog/collector-a</code> exists on the host and has correct permissions.</li>
</ul>










<h1>Syslog Collector</h1>

<p>
This project sets up a <strong>Syslog Collector</strong> using <code>rsyslog</code> inside a Docker container.  
It listens for incoming syslog messages over <strong>UDP/514</strong> from a Juniper SRX firewall and forwards them to another server over <strong>TCP/514</strong>.
</p>

<h2>Overview</h2>
<ul>
  <li><strong>Collector Host IP:</strong> 192.168.210.171</li>
  <li><strong>Source Device (SRX) IP:</strong> 192.168.210.191 (sending logs over UDP/514)</li>
  <li><strong>Forwarding Target Host IP:</strong> 192.168.210.170 (receiving logs over TCP/514)</li>
</ul>

<h2>Configuration Files</h2>

<h3>1. rsyslog.conf</h3>
<pre>
module(load="imudp")
input(type="imudp" port="514")

# Include extra config files
include(file="/etc/rsyslog.d/*.conf" mode="optional")
</pre>

<h3>2. rsyslog.d/10-forward.conf</h3>
<pre>
# Define template to send the full raw syslog message
template(name="FullRawSyslog" type="string" string="%rawmsg%\n")

# Forward all syslogs to Host-B over TCP using raw format
*.* action(
  type="omfwd"
  target="192.168.29.170"
  port="514"
  protocol="tcp"
  template="FullRawSyslog"
  keepalive="on"
  action.resumeRetryCount="-1"
  queue.type="linkedlist"
  queue.size="10000"
)
</pre>

<h3>3. Dockerfile</h3>
<pre>
FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y rsyslog && \
    rm -rf /var/lib/apt/lists/*

CMD ["rsyslogd", "-n"]
</pre>

<h3>4. docker-compose.yml</h3>
<pre>
version: '3.8'

services:
  rsyslog:
    build: .
    container_name: rsyslog
    restart: always
    network_mode: "host"
    volumes:
      - ./rsyslog.conf:/etc/rsyslog.conf:ro
      - ./rsyslog.d:/etc/rsyslog.d:ro
    ports:
      - "514:514/udp"
</pre>

<h2>Usage</h2>
<ol>
  <li>Clone this repository:</li>
  <pre>git clone &lt;your-repo-url&gt; && cd &lt;repo-folder&gt;</pre>
  
  <li>Build and start the container:</li>
  <pre>docker compose up --build -d</pre>
  
  <li>Verify that rsyslog is running:</li>
  <pre>docker logs rsyslog</pre>
  
  <li>Configure your Juniper SRX to send syslogs to <code>192.168.210.171</code> over UDP/514.</li>
</ol>

<h2>Notes</h2>
<ul>
  <li>This container listens for syslog over UDP/514 and forwards them to another syslog server over TCP/514.</li>
  <li>The forwarding target IP and port can be changed in <code>rsyslog.d/10-forward.conf</code>.</li>
  <li>Ensure the target syslog server is configured to accept TCP connections on port 514.</li>
</ul>

