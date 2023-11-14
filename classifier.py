import torch
from transformers import BertTokenizer, BertForSequenceClassification
from torch.nn.functional import softmax
import os
import sys

# Determine if we're running in a bundle
if getattr(sys, 'frozen', False):
    # If the 'frozen' attribute is True, we are running in a bundle (created by PyInstaller)
    bundle_dir = sys._MEIPASS
else:
    # Else, we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))


# Set the model directory path
model_directory = os.path.join(bundle_dir, 'model')

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