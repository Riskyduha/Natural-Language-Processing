#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import torch
from datasets import Dataset, DatasetDict
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    accuracy_score,
    precision_recall_fscore_support
)
import matplotlib.pyplot as plt


# In[74]:


df = pd.read_csv(
    "dataset/financial_news.csv",
    encoding="latin1",
    header=None,
    names=["label", "sentence"]
)

df["sentence"] = df["sentence"].fillna("").astype(str).str.strip()
df["sentence"] = df["sentence"].str.replace(r"\s+", " ", regex=True)
df["label"] = df["label"].astype(str).str.strip().str.lower()

valid_labels = ["negative", "neutral", "positive"]
df = df[df["label"].isin(valid_labels)].drop_duplicates().reset_index(drop=True)

label2id = {"negative": 0, "neutral": 1, "positive": 2}
id2label = {v: k for k, v in label2id.items()}

df["label_id"] = df["label"].map(label2id)


# In[76]:


df.head()


# In[77]:


df.label.value_counts()


# In[78]:


df.shape


# ## Split train, validation, test

# In[79]:


train_df, temp_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42,
    stratify=df["label_id"]
)

val_df, test_df = train_test_split(
    temp_df,
    test_size=0.5,
    random_state=42,
    stratify=temp_df["label_id"]
)

print("Train:", train_df.shape)
print("Validation:", val_df.shape)
print("Test:", test_df.shape)


# ## Hugging Face Dataset

# In[80]:


dataset = DatasetDict({
    "train": Dataset.from_pandas(train_df.reset_index(drop=True)),
    "validation": Dataset.from_pandas(val_df.reset_index(drop=True)),
    "test": Dataset.from_pandas(test_df.reset_index(drop=True)),
})

print(dataset)


# ## Tokenization

# In[81]:


model_name = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize_function(examples):
    return tokenizer(
        examples["sentence"],
        truncation=True,
        padding="max_length",
        max_length=128
    )

tokenized_dataset = dataset.map(tokenize_function, batched=True)
tokenized_dataset = tokenized_dataset.rename_column("label_id", "labels")

keep_cols = ["input_ids", "attention_mask", "labels"]
remove_cols = [c for c in tokenized_dataset["train"].column_names if c not in keep_cols]
tokenized_dataset = tokenized_dataset.remove_columns(remove_cols)

tokenized_dataset.set_format("torch")

print(tokenized_dataset)


# ## Load model

# In[82]:


device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print("Using device:", device)

model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=3,
    id2label=id2label,
    label2id=label2id
)

model = model.to(device)


# ## Metrik evaluasi

# In[83]:


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="weighted"
    )
    acc = accuracy_score(labels, preds)

    return {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


# ## Training arguments

# In[84]:


training_args = TrainingArguments(
    output_dir="./finbert_results",
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    save_total_limit=2,
    report_to="none"
)


# ## Buat Trainer dan training

# In[85]:


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],
    compute_metrics=compute_metrics
)

trainer.train()


# ## Evaluasi validation dan test

# In[88]:


def compute_metrics_manual(pred_output):
    y_true = pred_output.label_ids
    y_pred = np.argmax(pred_output.predictions, axis=1)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted"
    )
    acc = accuracy_score(y_true, y_pred)

    return {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

# validation
val_pred = trainer.predict(tokenized_dataset["validation"])
val_results = compute_metrics_manual(val_pred)

# test
test_pred = trainer.predict(tokenized_dataset["test"])
test_results = compute_metrics_manual(test_pred)

print("Validation Results:", val_results)
print("Test Results:", test_results)


# ## Classification report

# In[89]:


cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2])

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["negative", "neutral", "positive"]
)

disp.plot(cmap="Blues")
plt.title("Confusion Matrix - FinBERT")
plt.show()


# In[90]:


trainer.save_model("./best_finbert_model")
tokenizer.save_pretrained("./best_finbert_model")


# ## Simpan hasil prediksi test untuk error analysis

# In[91]:


test_result_df = test_df.reset_index(drop=True).copy()
test_result_df["y_true"] = y_true
test_result_df["y_pred"] = y_pred
test_result_df["true_label"] = test_result_df["y_true"].map(id2label)
test_result_df["pred_label"] = test_result_df["y_pred"].map(id2label)

test_result_df.to_csv("test_predictions.csv", index=False)
print(test_result_df.head())


# In[92]:


errors = test_result_df[test_result_df["y_true"] != test_result_df["y_pred"]]
print(errors[["sentence", "true_label", "pred_label"]].head(20))
print("Jumlah error:", len(errors))


# ## Prediksi sentence baru dengan model hasil fine-tuning

# In[93]:


import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

model_path = "./best_finbert_model"

inference_tokenizer = AutoTokenizer.from_pretrained(model_path)
inference_model = AutoModelForSequenceClassification.from_pretrained(model_path)

inference_model = inference_model.to(device)
inference_model.eval()

id2label = {
    0: "negative",
    1: "neutral",
    2: "positive"
}

def predict_sentiment(text):
    inputs = inference_tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = inference_model(**inputs)

    probs = torch.softmax(outputs.logits, dim=1)[0]
    pred_id = torch.argmax(probs).item()

    return {
        "sentence": text,
        "label": id2label[pred_id],
        "negative": float(probs[0].cpu()),
        "neutral": float(probs[1].cpu()),
        "positive": float(probs[2].cpu())
    }


# In[100]:


new_sentences = [
    # Positive
    "The company posted record earnings for the second consecutive quarter.",
    "Revenue grew significantly after strong demand in the European market.",
    "Operating profit improved due to lower production costs.",
    "The firm announced a successful expansion into new international markets.",
    "Net sales increased by 18 percent compared to last year.",

    # Neutral
    "The company released its quarterly financial statement on Monday.",
    "Sales remained unchanged compared to the previous quarter.",
    "The board announced the appointment of a new chief executive officer.",
    "The firm will publish its annual report next month.",
    "The company maintained its full-year guidance.",

    # Negative
    "The company reported a sharp decline in operating profit.",
    "Net losses widened because of rising raw material costs.",
    "Revenue fell significantly due to weak consumer demand.",
    "The firm announced layoffs after disappointing financial results.",
    "Production was suspended following a major supply chain disruption."
]

for text in new_sentences:
    result = predict_sentiment(text)
    print(result)


# In[101]:


def predict_sentiments(texts):
    inputs = inference_tokenizer(
        texts,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = inference_model(**inputs)

    probs = torch.softmax(outputs.logits, dim=1)
    pred_ids = torch.argmax(probs, dim=1)

    results = []
    for i, text in enumerate(texts):
        results.append({
            "sentence": text,
            "label": id2label[pred_ids[i].item()],
            "negative": float(probs[i][0].cpu()),
            "neutral": float(probs[i][1].cpu()),
            "positive": float(probs[i][2].cpu())
        })

    return pd.DataFrame(results)

# ── Re-export model tanpa training ulang ─────────────────────────
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = "ProsusAI/finbert"

# Load ulang dari checkpoint terbaik
print("Loading model dari checkpoint-726...")
tokenizer = AutoTokenizer.from_pretrained(model_name)  # tokenizer dari base model
model = AutoModelForSequenceClassification.from_pretrained(
    "./finbert_results/checkpoint-726",
    num_labels=3,
    id2label={0: "negative", 1: "neutral", 2: "positive"},
    label2id={"negative": 0, "neutral": 1, "positive": 2},
    ignore_mismatched_sizes=True
)
model.to(device)

# Simpan
print("Menyimpan ke ./best_finbert_model ...")
model.save_pretrained("./best_finbert_model")
tokenizer.save_pretrained("./best_finbert_model")
print("✅ Selesai! Sekarang jalankan: python app.py")