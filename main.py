import warnings

from Nmap.WorkerNetwork import WorkerNMAP
from Agent.AgentNetwork import AgentNetworkAI
import time

VERSION = "0.2"


if __name__ == "__main__":
    worker = WorkerNMAP()
    agent = AgentNetworkAI()

    print(f"""
██          █████     ███    ██    ██          
██         ██   ██    ████   ██    ██ 
██         ███████    ██ ██  ██    ██ 
██         ██   ██    ██  ██ ██    ██ 
███████ ██ ██   ██ ██ ██   ████ ██ ██ 
Local Area Network Intelligence
Rudenetworks.com {VERSION} alpha                                                                        
""")

    print("Hello, I'm L.A.N.I, your network assistant! How can I help you today?")

    worker.start()

    while True:
        query = input("Ask Lani: ")
        time.sleep(1)
        response = agent.analyze_user_query(query, worker.devices)
        print("Lani's response:", response)
        time.sleep(1)

