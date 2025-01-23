import subprocess
import re

class Dig:
    def run_dig(self, domain):
         # Run dig command
        result = subprocess.run(["dig", domain], capture_output=True, text=True)
        return result.stdout

    def parse_dig_output(self, output):
        # Extract Question Section
        question_match = re.search(r";;\s*QUESTION SECTION:\n;(\S+)\s+\S+\s+(\S+)", output)
        question = f"The query was made for the domain '{question_match.group(1)}', requesting a {question_match.group(2)} record." if question_match else ""

        # Extract Answer Section
        answer_match = re.findall(r"(\S+)\s+\d+\s+IN\s+(\S+)\s+(\S+)", output)
        if answer_match:
            answers = [f"{record[1]} record for {record[0]} resolves to {record[2]}." for record in answer_match]
            answer_section = " ".join(answers)
        else:
            answer_section = "No answer section found."

        # Extract Query Time
        query_time_match = re.search(r";; Query time: (\d+) msec", output)
        query_time = f" The query took {query_time_match.group(1)} milliseconds." if query_time_match else ""

        # Extract Server Info
        server_match = re.search(r";; SERVER: (\S+)", output)
        server_info = f" The query was resolved by the DNS server at {server_match.group(1)}." if server_match else ""

        # Compile the final human-readable output
        readable_output = f"{question} {answer_section}{query_time}{server_info}"

        return readable_output