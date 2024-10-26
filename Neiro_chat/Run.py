from Bert import load_trained_model, classify_query, get_answer, find_similar_queries
from answers_for_none import get_default_response, find_response_by_keywords
import sys
import json

model, tokenizer = load_trained_model()

def process_query(query, alternative=False):
    if alternative:
        alternative_answer = find_response_by_keywords(query)
        return {"answer": alternative_answer}

    predicted_label, category_name = classify_query(model, query)
    answer = get_answer(query, predicted_label)
    similar_queries = find_similar_queries(query)

    with open('./Neiro_chat/exact_answer_map.json', 'r') as f:
        exact_answer_map = json.load(f)
    
    return {"answer": answer, "category": category_name, "similar_queries": similar_queries, "exact_answer_map": exact_answer_map}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = sys.argv[1]
        alternative = len(sys.argv) > 2 and sys.argv[2] == "alternative"
        result = process_query(query, alternative)
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps({"error": "Запрос не был предоставлен"}, ensure_ascii=False))