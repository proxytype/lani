import subprocess
import re
import platform
import json

class NSLookup:
    def run_nslookup(self, domain):
        # Run nslookup command
        result = subprocess.run(["nslookup", domain], capture_output=True, text=True)
        return self.parse_nslookup_output(result.stdout)

    def parse_nslookup_output(self, output):
        # Extract DNS Server
        server_match = re.search(r"Server:\s+([\S]+)", output)
        server_info = f"The DNS query was resolved by {server_match.group(1)}." if server_match else ""

        # Extract IP Address
        ip_match = re.findall(r"Address:\s+([\d\.]+)", output)
        if ip_match:
            ip_addresses = ", ".join(ip_match[1:])  # Skipping the first address, as it's often the DNS resolver
            ip_info = f" The domain resolves to IP address(es): {ip_addresses}."
        else:
            ip_info = " No IP address found for the domain."

        # Compile the final human-readable output
        readable_output = f"{server_info}{ip_info}"

        return readable_output if readable_output else "NSLookup command failed or no data was received."
