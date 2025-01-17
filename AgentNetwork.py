import spacy
import csv
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from AgentPatterns import AgentPatternsAI


class AgentNetworkAI:
    def __init__(self, dataset = "network_queries.csv"):
        self.nlp = spacy.load("en_core_web_sm")
        self.query_response_dataset = self.load_dataset(dataset)
        self.vectorizer = CountVectorizer().fit([q for q, _, _ in self.query_response_dataset])

    def load_dataset(self, filepath):
        """Load the CSV dataset containing queries and responses."""
        dataset = []
        with open(filepath, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            for row in reader:
                dataset.append((row[0].lower(), row[1], row[2]))
        return dataset

    def analyze_user_query(self, query, devices):
        """Analyze the user's query and return an appropriate response."""
        return self.find_best_match(query, devices)

    def extract_dynamic_values(self, query):
        """Extract dynamic values (e.g., IP addresses) from the query using NER."""
        doc = self.nlp(query)
        ip_addresses = [ent.text for ent in doc.ents if
                        ent.label_ == "GPE" and re.match(r"\d+\.\d+\.\d+\.\d+", ent.text)]
        return {"<IP_ADDRESS>": ip_addresses[0]} if ip_addresses else {}

    def find_best_match(self, query, devices):
        """Find the best matching response for the given query using cosine similarity."""
        query_vector = self.vectorizer.transform([query.lower()])
        dataset_vectors = self.vectorizer.transform([q for q, _, _ in self.query_response_dataset])
        similarities = cosine_similarity(query_vector, dataset_vectors)
        best_match_idx = similarities.argmax()
        best_match_score = similarities[0, best_match_idx]

        patterns = AgentPatternsAI()

        if best_match_score > 0.5:  # Set a threshold for a good match
            matched_query, response_template, mclass = self.query_response_dataset[best_match_idx]
            dynamic_values = self.extract_dynamic_values(query)
            response = patterns.inject_patterns(response_template, dynamic_values, devices)
            return response
        else:
            return "Sorry, I couldn't understand your query. Please try again."