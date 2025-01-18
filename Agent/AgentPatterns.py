from Nmap.WorkerNetwork import WorkerNMAP

class AgentPatternsAI:

    PATTERN_IP = "<IP_ADDRESS>"
    PATTERN_PORTS = "<PORTS>"
    PATTERN_STATUS = "<STATUS>"
    PATTERN_DEVICES = "<DEVICES_LIST>"
    PATTERN_BYTES_SENT = "<BYTES_SENT>"
    PATTERN_BYTES_RECEIVED = "<BYTES_RECEIVED>"
    PATTERN_SCAN_DATE = "<SCAN_DATE>"
    PATTERN_SUPPORTED_PORTS = "<SUPPORTED_PORTS>"

    def __init__(self):
        pass

    def inject_patterns(self, response, dynamic_values, devices):

        if AgentPatternsAI.PATTERN_BYTES_SENT in response and AgentPatternsAI.PATTERN_BYTES_RECEIVED in response:
            sent = WorkerNMAP.LOCALNETWORK["bytes_sent"]
            received = WorkerNMAP.LOCALNETWORK["bytes_received"]
            traffic_data =  {AgentPatternsAI.PATTERN_BYTES_SENT: f"{sent} bytes", AgentPatternsAI.PATTERN_BYTES_RECEIVED: f"{received} bytes"}
            dynamic_values.update(traffic_data)

        if AgentPatternsAI.PATTERN_DEVICES in response:
            devices_list = ", ".join(device["ip"] for device in devices) if devices else "No devices found"
            dynamic_values[AgentPatternsAI.PATTERN_DEVICES] = devices_list

        if AgentPatternsAI.PATTERN_SUPPORTED_PORTS in response:
            supported_ports = ", ".join(pp["service"] for pp in WorkerNMAP.PORTS) if WorkerNMAP.PORTS else "No global ports found"
            dynamic_values[AgentPatternsAI.PATTERN_SUPPORTED_PORTS] = supported_ports

        for placeholder, value in dynamic_values.items():
            response = response.replace(placeholder, value)

        return response
