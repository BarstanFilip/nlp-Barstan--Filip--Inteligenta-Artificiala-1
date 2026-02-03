
import torch
import torch.nn as nn
import joblib
import numpy as np
from transformers import RobertaTokenizer, RobertaModel
from sklearn.feature_extraction.text import TfidfVectorizer

#tf-idf
class CustomTfidfVectorizer(TfidfVectorizer):
    def __init__(
        self,
        penalize_words=None,
        boost_words=None,
        penalization=0.5,
        boost=1.5,
        max_features=5000,
        ngram_range=(1, 2)
    ):
        super().__init__(
            max_features=max_features,
            ngram_range=ngram_range
        )
        self.penalize_words = penalize_words or []
        self.boost_words = boost_words or []
        self.penalization = penalization
        self.boost = boost

    def fit(self, raw_documents, y=None):
        super().fit(raw_documents, y)
        vocab = self.get_feature_names_out()
        for i, word in enumerate(vocab):
            if word in self.penalize_words:
                self.idf_[i] *= (1 - self.penalization)
            elif word in self.boost_words:
                self.idf_[i] *= self.boost
        return self

#Roberta
class RobertaClickbaitClassifier(nn.Module):
    def __init__(self, dropout_rate=0.3, hidden_size=256, use_attention=True):
        super().__init__()
        self.roberta = RobertaModel.from_pretrained("roberta-base")
        self.use_attention = use_attention

        self.dropout = nn.Dropout(dropout_rate)
        self.fc1 = nn.Linear(self.roberta.config.hidden_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

        if use_attention:
            self.attention = nn.Linear(self.roberta.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask):
        outputs = self.roberta(input_ids=input_ids, attention_mask=attention_mask)
        hidden_state = outputs.last_hidden_state
        if self.use_attention:
            attn_weights = torch.softmax(self.attention(hidden_state), dim=1)
            pooled = torch.sum(attn_weights * hidden_state, dim=1)
        else:
            pooled = hidden_state[:, 0]

        x = self.dropout(pooled)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return self.sigmoid(x).squeeze()

#extract lexicon features
def extract_lexicon_features(texts):
    
    return np.zeros((len(texts), 5))





#SVM + Tf-idf
tfidf = joblib.load("tfidf_vectorizer.joblib")
svm_model = joblib.load("svm_clickbait_model.joblib")

#RoBERTa
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = RobertaTokenizer.from_pretrained("roberta_clickbait_tokenizer")
roberta_model = RobertaClickbaitClassifier().to(device)
roberta_model.load_state_dict(
    torch.load("roberta_clickbait.pth", map_location=device)
)
roberta_model.eval()


#SVM prediction
def predict_svm(text):
    X_tfidf = tfidf.transform([text]).toarray()
    X_lex = extract_lexicon_features([text])
    X_combined = np.hstack([X_tfidf, X_lex])
    label = svm_model.predict(X_combined)[0]
    prob = svm_model.predict_proba(X_combined)[0][1]
    return label, prob

#Roberta prediction
def predict_roberta(text):
    encoding = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=128,
        padding="max_length",
        truncation=True,
        return_attention_mask=True,
        return_tensors="pt"
    )
    input_ids = encoding["input_ids"].to(device)
    attention_mask = encoding["attention_mask"].to(device)

    with torch.no_grad():
        prob = roberta_model(input_ids, attention_mask).item()

    label = 1 if prob >= 0.5 else 0 #0.5
    return label, prob




texts = [
  "You Won’t Believe What Happened Next",
  "Company Reports Quarterly Earnings"
]

for word in texts:
    print(f'test sa vad daca merge cum trebe de fieccare data -- {predict_svm(word)}')


print(f'dev = {device}')
a=True
while a:
    text = input("Headline ")
    if text == "esc":
        a=False

    svm_label, svm_prob = predict_svm(text)
    rob_label, rob_prob = predict_roberta(text)
    ensemble = 0.5 * svm_prob + 0.5 * rob_prob
    print(device)
    print("------------")
    
    print(f"SVM + tf-idf + Lexicon  {'clickbait' if svm_label else 'non-clickbait'} --- scor={svm_prob:.3f}")
    print(f"RoBERTa                  {'clickbait' if rob_label else 'non-clickbait'} --- scor={rob_prob:.3f}")
    print(f"ENSEMBLE                 {'clickbait' if ensemble>=0.5 else 'non-clickbait'} --- scor={ensemble:.3f}")
