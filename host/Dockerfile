FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y rsyslog logrotate cron && \
    rm -rf /var/lib/apt/lists/*

# Add cron job to run logrotate every 10 minutes
RUN echo "*/10 * * * * root /usr/sbin/logrotate -f /etc/logrotate.d/collector-a" \
    > /etc/cron.d/logrotate-collector-a && \
    chmod 0644 /etc/cron.d/logrotate-collector-a

# Touch cron log (optional)
RUN touch /var/log/cron.log

# Start cron and rsyslog together
CMD service cron start && rsyslogd -n
