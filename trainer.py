import torch
from transformers import BertTokenizer, BertModel
import csv

class LaniTrainer:
    def __init__(self, dataset_path="DataSet/network_queries.csv", model_path="Model/lani_model.pth"):
        self.dataset_path = dataset_path
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.bert_model = BertModel.from_pretrained("bert-base-uncased").to(self.device)

    def load_dataset(self):
        dataset = []
        with open(self.dataset_path, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                dataset.append((row[0].lower(), row[1], row[2]))
        return dataset

    def encode_query(self, query):
        inputs = self.tokenizer(query, return_tensors="pt", padding=True, truncation=True, max_length=50).to(self.device)
        with torch.no_grad():
            outputs = self.bert_model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().cpu()

    def train_and_save_model(self):
        dataset = self.load_dataset()
        embeddings = []
        responses = []
        classes = []

        for query, response, cls in dataset:
            embedding = self.encode_query(query).unsqueeze(0).to(self.device)
            embeddings.append(embedding)
            responses.append(response)
            classes.append(cls)

        embeddings_tensor = torch.cat(embeddings).to(self.device)
        model_data = {"embeddings": embeddings_tensor, "responses": responses, "classes": classes}
        torch.save(model_data, self.model_path)
        print(f"Model saved to {self.model_path}")

if __name__ == "__main__":
    trainer = LaniTrainer()
    trainer.train_and_save_model()