import nmap

class WorkerNMAP:
    def __int__(self, network="192.168.1.1/24"):
        self.networkRange = network
        self.devices = []


    # Additional network functions
    def scan_network(self):
        """Scan the network for active devices."""
        scanner = nmap.PortScanner()
        scanner.scan(hosts=self.network_range, arguments="-sn")
        self.devices = [host for host in scanner.all_hosts() if scanner[host].state() == "up"]
        return self.devices