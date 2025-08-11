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
  <li>Save logs in <code>/var/log/flowdb/syslog/collector-a/</code> with filenames based on hostname and timestamp.</li>
  <li>Store the <strong>raw</strong> message without modification.</li>
</ul>

<pre>
module(load="imtcp")
input(type="imtcp" port="514")

template(name="CustomLogFile" type="string"
  string="/var/log/flowdb/syslog/collector-a/%hostname%_%timereported:1:10:date-rfc3339%%timereported:11:8:date-rfc3339%.log"
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
      - /var/log/flowdb/syslog/collector-a:/var/log/flowdb/syslog/collector-a
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
/var/log/flowdb/syslog/collector-a/*.log {
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
        /usr/bin/find /var/log/flowdb/syslog/collector-a/ -type f -mmin +2880 -delete
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
    <pre>/var/log/flowdb/syslog/collector-a/</pre>
  </li>
</ol>

<h2>Notes</h2>
<ul>
  <li>Requires root privileges to bind to port 514.</li>
  <li>Ensure <code>/var/log/flowdb/syslog/collector-a</code> exists on the host and has correct permissions.</li>
</ul>
