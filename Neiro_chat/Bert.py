import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification, AdamW
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pandas as pd
from tqdm import tqdm
import difflib
import json
import random
from answers_for_none import get_default_response, find_response_by_keywords

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')

class CustomDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts.iloc[idx]
        label = self.labels.iloc[idx]
        
        encoding = self.tokenizer.encode_plus(
            text,
            max_length=self.max_len,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def accuracy(preds, labels):
    pred_flat = preds.argmax(axis=1).flatten()
    labels_flat = labels.flatten()
    return (pred_flat == labels_flat).cpu().numpy().mean()

def train_and_save_model(patience=3):
    print("Загрузка датасета...")
    df = pd.read_excel("./Neiro_chat/dataset.xlsx")
    print("Датасет успешно загружен.")

    label_encoder = LabelEncoder()
    df['label_encoded'] = label_encoder.fit_transform(df['label'])

    category_map = dict(zip(df['label_encoded'], df['label']))
    answer_map = (
        df.groupby('label_encoded')['Solution']
        .apply(lambda x: [ans for ans in x if isinstance(ans, str) and ans.strip() != ""])
        .to_dict()
    )

    exact_answer_map = {
        topic: solution for topic, solution in zip(df['Topic'], df['Solution']) if pd.notna(solution) and solution.strip() != ""
    }

    with open('./Neiro_chat/category_map.json', 'w') as f:
        json.dump(category_map, f)
    with open('./Neiro_chat/answer_map.json', 'w') as f:
        json.dump(answer_map, f)
    with open('./Neiro_chat/exact_answer_map.json', 'w') as f:
        json.dump(exact_answer_map, f)

    train_texts, val_texts, train_labels, val_labels = train_test_split(df['Topic'], df['label_encoded'], test_size=0.2, random_state=42)

    num_labels = len(df['label_encoded'].unique())
    model = RobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=num_labels).to(device)

    train_dataset = CustomDataset(train_texts, train_labels, tokenizer)
    val_dataset = CustomDataset(val_texts, val_labels, tokenizer)

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64)

    optimizer = AdamW(model.parameters(), lr=2e-5)

    best_val_accuracy = 0
    epochs_without_improvement = 0

    for epoch in range(250):
        print(f"Epoch {epoch + 1}/250")
        model.train()
        total_loss = 0
        for batch in tqdm(train_loader):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            optimizer.zero_grad()
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            total_loss += loss.item()
            loss.backward()
            optimizer.step()
        
        avg_train_loss = total_loss / len(train_loader)
        print(f"Средняя потеря на эпохе {epoch + 1}: {avg_train_loss}")
        
        model.eval()
        total_accuracy = 0
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                total_accuracy += accuracy(logits, labels)
        
        avg_val_accuracy = total_accuracy / len(val_loader)
        print(f"Точность на валидационном наборе: {avg_val_accuracy}")

        if avg_val_accuracy > best_val_accuracy:
            best_val_accuracy = avg_val_accuracy
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            print(f"Нет улучшений в течение {epochs_without_improvement} эпох.")
        
        if epochs_without_improvement >= patience:
            print("Ранняя остановка: обучение прекращено.")
            break

    model.save_pretrained('./Neiro_chat/fine_tuned_roberta')
    tokenizer.save_pretrained('./Neiro_chat/fine_tuned_roberta')
    print("Модель успешно обучена и сохранена.")


def load_trained_model():
    model = RobertaForSequenceClassification.from_pretrained('./Neiro_chat/fine_tuned_roberta').to(device)
    tokenizer = RobertaTokenizer.from_pretrained('./Neiro_chat/fine_tuned_roberta')
    return model, tokenizer

def classify_query(model, query):
    inputs = tokenizer.encode_plus(
        query,
        return_tensors="pt",
        max_length=128,
        truncation=True,
        padding="max_length"
    )
    inputs = {key: value.to(device) for key, value in inputs.items()}
    
    model.eval()
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_label = logits.argmax(dim=1).item()
    
    with open('./Neiro_chat/category_map.json', 'r') as f:
        category_map = json.load(f)

    category_name = category_map.get(str(predicted_label), "Категория не найдена")
    
    return predicted_label, category_name


def get_answer(query, predicted_label):
    with open('./Neiro_chat/exact_answer_map.json', 'r') as f:
        exact_answer_map = json.load(f)
    
    exact_answer = exact_answer_map.get(query)
    if exact_answer and exact_answer != "nan":
        return exact_answer
    
    response_by_keywords = find_response_by_keywords(query)
    if response_by_keywords != "Извините, подходящая инструкция не найдена.":
        return response_by_keywords

    return "Ответ для этой категории отсутствует"

def find_similar_queries(query, num_results=3):
    with open('./Neiro_chat/exact_answer_map.json', 'r') as f:
        exact_answer_map = json.load(f)
    
    all_questions = list(exact_answer_map.keys())
    
    similar_queries = difflib.get_close_matches(query, all_questions, n=num_results, cutoff=0.2)
    
    if len(similar_queries) < num_results:
        additional_count = num_results - len(similar_queries)
        additional_questions = [q for q in all_questions if q not in similar_queries][:additional_count]
        similar_queries.extend(additional_questions)
    
    return similar_queries