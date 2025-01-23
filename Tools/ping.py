import subprocess
import re

class Ping:
    def run_ping(self, host):
        # Run ping command (sends 4 packets by default)
        result = subprocess.run(["ping", "-c", "4", host], capture_output=True, text=True)
        return self.parse_ping_output(result.stdout)

    def parse_ping_output(self, output):
        # Extract destination IP
        ip_match = re.search(r"PING\s+\S+\s+\(([\d\.]+)\)", output)
        ip_address = f"The request was sent to IP address {ip_match.group(1)}." if ip_match else ""

        # Extract packet loss
        packet_loss_match = re.search(r"(\d+)% packet loss", output)
        packet_loss = f" Packet loss was {packet_loss_match.group(1)}%." if packet_loss_match else ""

        # Extract round-trip time (RTT)
        rtt_match = re.search(r"rtt min/avg/max/mdev = ([\d\.]+)/([\d\.]+)/([\d\.]+)/([\d\.]+) ms", output)
        if rtt_match:
            rtt_info = f" The round-trip times were: minimum {rtt_match.group(1)} ms, average {rtt_match.group(2)} ms, maximum {rtt_match.group(3)} ms."
        else:
            rtt_info = ""

        # Compile the final human-readable output
        readable_output = f"{ip_address}{packet_loss}{rtt_info}"

        return readable_output if readable_output else "Ping command failed or no data was received."
