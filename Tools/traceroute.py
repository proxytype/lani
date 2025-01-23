import subprocess
import re

class Traceroute:
    def run_traceroute(self, host):
        # Run traceroute command
        result = subprocess.run(["traceroute", host], capture_output=True, text=True)
        return self.parse_traceroute_output(result.stdout)

    def parse_traceroute_output(self, output):
        # Extract hops
        hop_matches = re.findall(r"(\d+)\s+([\d\w\.\-]+)\s+\(?([\d\.]+)?\)?\s+.*?(\d+\.\d+ ms)?", output)

        if not hop_matches:
            return "Traceroute command failed or no data was received."

        hops = []
        for hop in hop_matches:
            hop_number, host, ip, latency = hop
            hop_desc = f"Hop {hop_number}: {host} ({ip})" if ip else f"Hop {hop_number}: {host}"
            if latency:
                hop_desc += f" with a latency of {latency}"
            hops.append(hop_desc)

        # Format the extracted hops into a readable output
        readable_output = "Traceroute results:\n" + "\n".join(hops)

        return readable_output