from datetime import datetime

import nmap
import time
import threading

import psutil


class WorkerNMAP:

    PARAM_BYTES_SENT = "bytes_sent"
    PARAM_BYTES_RECEIVED = "bytes_received"

    PORTS = [
        {"port": 21, "service": "ftp"},
        {"port": 22, "service": "ssh"},
        {"port": 23, "service": "telnet"},
        {"port": 25, "service": "smtp"},
        {"port": 53, "service": "dns"},
        {"port": 80, "service": "http"},
        {"port": 123, "service": "ntp"},
        {"port": 443, "service": "https"},
        {"port": 1433, "service": "mssql"},
        {"port": 3306, "service": "mysql"},
        {"port": 5432, "service": "postgres"},
        {"port": 27017, "service": "monogodb"}
    ]

    LOCALNETWORK = {}

    def get_network_traffic(self):
        """Get real-time network traffic statistics."""
        net_io = psutil.net_io_counters()

        WorkerNMAP.LOCALNETWORK[WorkerNMAP.PARAM_BYTES_SENT] = net_io.bytes_sent
        WorkerNMAP.LOCALNETWORK[WorkerNMAP.PARAM_BYTES_RECEIVED] = net_io.bytes_recv

        return WorkerNMAP.LOCALNETWORK

    def __init__(self, network_range="192.168.1.0/24"):
        self.network_range = network_range
        self.devices = []

    def start(self):
        threading.Thread(target=self.background_scan_network, daemon=True).start()

    def scan_network(self):

        self.get_network_traffic()
        """Scan the network for active devices."""
        scanner = nmap.PortScanner()
        scanner.scan(hosts=self.network_range, arguments="-sn")

        temp_devices = []
        for host in scanner.all_hosts():
            device = {"ip": host, "up": scanner[host].state(), "ports": [], "collected": datetime.now()}
            # device["ports"] = self.check_open_ports(device["ip"])
            temp_devices.append(device)

        self.devices = temp_devices

    def background_scan_network(self):
        while True:
            self.scan_network()
            time.sleep(300)  # Scan every 5 minutes

    def check_open_ports(self, ip):
        """Check open ports on a specific IP address."""
        scanner = nmap.PortScanner()
        service_ports = ", ".join(ports["port"] for ports in WorkerNMAP.PORTS) if WorkerNMAP.PORTS else "1-65535"
        scanner.scan(ip, arguments="-p", ports=service_ports)
        open_ports = [port for port in scanner[ip]['tcp'] if scanner[ip]['tcp'][port]['state'] == 'open']

        temp_ports = []

        if len(open_ports) != 0:
            for p in open_ports:
                for p2 in WorkerNMAP.PORTS:
                    if p == str(p2["port"]):
                        temp_ports.append(p2)

        return temp_ports