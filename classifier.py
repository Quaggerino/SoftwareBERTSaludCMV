import torch
from transformers import BertTokenizer, BertForSequenceClassification
from torch.nn.functional import softmax

# Load the model and tokenizer
model_directory = './model'
tokenizer = BertTokenizer.from_pretrained(model_directory)
model = BertForSequenceClassification.from_pretrained(model_directory)

def classify_text(text):
    inputs = tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**inputs)
    probabilities = softmax(outputs.logits, dim=1)
    top_prob, top_pred = torch.max(probabilities, dim=1)
    confidence = top_prob.item()
    prediction = top_pred.item()
    return prediction, confidence