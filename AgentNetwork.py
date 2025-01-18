import csv
import nmap
import psutil
import subprocess
import json
import time
import threading
import re
from datetime import datetime
import torch
from torch.nn.functional import cosine_similarity
from transformers import BertTokenizer, BertModel, BertForTokenClassification
from transformers import pipeline
from AgentPatterns import AgentPatternsAI


class AgentNetworkAI:
    def __init__(self, dataset = "network_queries.csv"):
        self.device_activity_log = "device_activity_log.json"
        self.query_response_dataset = self.load_dataset(dataset)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.bert_model = BertModel.from_pretrained("bert-base-uncased").to(self.device)
        self.model = BertForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
        self.nlp = pipeline("ner", model=self.model, tokenizer=self.tokenizer)
        #self.embeddings, self.responses, self.classes = self.prepare_embeddings()
        self.embeddings, self.responses, self.classes = self.load_trained_model("lani_model.pth")

    def load_trained_model(self, model_path):
        """Load trained model embeddings, responses, and classes."""
        checkpoint = torch.load(model_path, map_location=self.device)
        return checkpoint['embeddings'], checkpoint['responses'], checkpoint['classes']

    def load_dataset(self, filepath):
        """Load the CSV dataset containing queries and responses."""
        dataset = []
        with open(filepath, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            for row in reader:
                dataset.append((row[0].lower(), row[1], row[2]))
        return dataset

    def encode_query(self, query):
        """Generate BERT embeddings for a given query."""
        inputs = self.tokenizer(query, return_tensors="pt", padding=True, truncation=True, max_length=50).to(
            self.device)
        with torch.no_grad():
            outputs = self.bert_model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze()


    def prepare_embeddings(self):
        """Generate embeddings for all queries in the dataset using BERT."""
        embeddings = []
        responses = []
        classes = []
        for query, response, cls in self.query_response_dataset:
            embedding = self.encode_query(query).unsqueeze(0).to(self.device)
            embeddings.append(embedding)
            responses.append(response)
            classes.append(cls)
        return torch.cat(embeddings).to(self.device), responses, classes

    def analyze_user_query(self, query, devices):
        """Analyze the user's query and return an appropriate response."""
        return self.find_best_match(query, devices)

    def extract_dynamic_values(self, query):
        """Use BERT-based NER to extract dynamic values like IPs, dates, ports, device names, etc."""
        extracted_values = {}

        # Use BERT NER pipeline
        ner_results = self.nlp(query)

        # Extract entities from BERT NER results
        for result in ner_results:
            if result['entity'] == 'B-LOC' or result['entity'] == 'I-LOC':  # Location/Geographical Entity
                extracted_values["LOCATION"] = result['word']
            elif result['entity'] == 'B-MISC' or result['entity'] == 'I-MISC':  # Miscellaneous Entities
                extracted_values["MISC"] = result['word']
            elif result['entity'] == 'B-PER' or result['entity'] == 'I-PER':  # Person Entity (for example)
                extracted_values["PERSON"] = result['word']
            elif result['entity'] == 'B-ORG' or result['entity'] == 'I-ORG':  # Organization
                extracted_values["ORG"] = result['word']
            elif result['entity'] == 'B-DATE' or result['entity'] == 'I-DATE':  # Date
                extracted_values["DATE"] = result['word']
            elif result['entity'] == 'B-TIME' or result['entity'] == 'I-TIME':  # Time
                extracted_values["TIME"] = result['word']
            elif result['entity'] == 'B-TECH' or result[
                'entity'] == 'I-TECH':  # Technology-related terms (e.g., device names, protocols)
                extracted_values["DEVICE_NAME"] = result['word']

        # Use regex for extracting IP addresses and ports
        ip_addresses = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", query)
        if ip_addresses:
            extracted_values["IP_ADDRESS"] = ip_addresses[0]  # Take the first found IP address

        # Extract port numbers
        ports = re.findall(r"\b(?:\d{1,5})\b", query)
        if ports:
            extracted_values["PORTS"] = [port for port in ports if 0 < int(port) <= 65535]  # Filter valid ports

        # Extract numerical values (e.g., bandwidth, usage, amount)
        numbers = re.findall(r"\b\d+\b", query)
        if numbers:
            extracted_values["NUMBERS"] = [int(num) for num in numbers]

        return extracted_values

    def find_best_match(self, query, devices):
        with torch.no_grad():
            query_embedding = self.encode_query(query).unsqueeze(0).to(self.device)

            # Calculate cosine similarity, which should return a 2D array
            similarities = cosine_similarity(query_embedding.cpu(), self.embeddings.cpu())

            # Check if similarities is 2D and if it's flattened to 1D
            similarities_tensor = torch.tensor(similarities)

            if similarities_tensor.dim() == 1:
                # For 1D similarity tensor
                best_match_idx = torch.argmax(similarities_tensor).item()
                best_match_score = similarities_tensor[best_match_idx].item()
            else:
                # If it's 2D, we can use the previous approach
                best_match_idx = torch.argmax(similarities_tensor).item()
                best_match_score = similarities_tensor[0, best_match_idx].item()

            patterns = AgentPatternsAI()

            if best_match_score > 0.5:  # Set a threshold for a good match
                response_template = self.responses[best_match_idx]
                dynamic_values = self.extract_dynamic_values(query)
                response = patterns.inject_patterns(response_template, dynamic_values, devices)
                return response
            else:
                return "Sorry, I couldn't understand your query. Please try again."