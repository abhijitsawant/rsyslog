<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>rsyslog.conf Description</title>
</head>
<body>
    <header>
        <h1>Understanding <code>rsyslog.conf</code></h1>
        <p>The <code>rsyslog.conf</code> file is the main configuration file for the Rsyslog daemon, which is used for logging messages from the kernel, system services, and applications. It defines how log messages are received, processed, and stored.</p>
    </header>

    <main>
        <section>
            <h2>Key Sections of <code>rsyslog.conf</code></h2>
            <ol>
                <li>
                    <h3>Global Directives</h3>
                    <p>Control overall behavior of Rsyslog, such as queue sizes, default permissions, and module loading.</p>
                </li>
                <li>
                    <h3>Module Loading</h3>
                    <p>Modules extend Rsyslog functionality (e.g., <code>imudp</code> for UDP syslog input, <code>imtcp</code> for TCP syslog input).</p>
                </li>
                <li>
                    <h3>Rule Sets</h3>
                    <p>Define filters and actions for specific log types.</p>
                </li>
                <li>
                    <h3>Templates</h3>
                    <p>Specify the format and destination for log output.</p>
                </li>
                <li>
                    <h3>Selectors and Actions</h3>
                    <p>Define which log messages are processed and where they are sent or stored (e.g., files, databases, remote servers).</p>
                </li>
            </ol>
        </section>

        <section>
            <h2>Example Basic Configuration</h2>
            <pre>
# Load UDP and TCP input modules
module(load="imudp")
input(type="imudp" port="514")
module(load="imtcp")
input(type="imtcp" port="514")

# Store all logs in /var/log/messages
*.* /var/log/messages
            </pre>
        </section>

        <section>
            <h2>Common Use Cases</h2>
            <ul>
                <li>Centralized logging for multiple systems</li>
                <li>Filtering and routing logs to different destinations</li>
                <li>Integrating with log analysis tools</li>
                <li>Rotating and compressing log files</li>
            </ul>
        </section>
    </main>

    <footer>
        <p><strong>Note:</strong> Changes to <code>rsyslog.conf</code> require restarting the Rsyslog service for the configuration to take effect.</p>
    </footer>
</body>
</html>
