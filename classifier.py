import torch
from transformers import BertTokenizer, BertForSequenceClassification

# Load the model and tokenizer
model_directory = './model'
tokenizer = BertTokenizer.from_pretrained(model_directory)
model = BertForSequenceClassification.from_pretrained(model_directory)

def classify_text(text):
    inputs = tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**inputs)
    _, prediction = torch.max(outputs.logits, dim=1)
    return prediction.item()