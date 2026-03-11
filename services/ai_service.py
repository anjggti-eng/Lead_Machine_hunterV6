import requests
import json
import re

# IA para Score de Lead
def score_lead(empresa):
    """
    Pontua a empresa de 0 a 100 via Llama 3 / Mistral.
    Tenta Ollama (11434) e Fallback para LM Studio (1234).
    """
    prompt = f"O quão provável é a empresa {empresa} ser um cliente em potencial de serviços de tecnologia? Responda APENAS o número entre 0 e 100, nada mais."
    
    # 1. Tenta Ollama
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral", "prompt": prompt, "stream": False
        }, timeout=4)
        result = response.json()["response"]
        score_match = re.search(r'\d+', result)
        return int(score_match.group()) if score_match else 50
    except:
        # 2. Fallback para LM Studio (1234)
        try:
            url = "http://127.0.0.1:1234/v1/chat/completions"
            payload = {
                "model": "meta-llama-3-8b-instruct",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 15
            }
            response = requests.post(url, json=payload, timeout=4)
            result = response.json()['choices'][0]['message']['content']
            score_match = re.search(r'\d+', result)
            return int(score_match.group()) if score_match else 50
        except:
            return 50 # Default final

# Mantendo nossa IA robusta (LM Studio 1234) para Scripts de Venda
def generate_text(prompt, model="meta-llama-3-8b-instruct"):
    try:
        url = "http://127.0.0.1:1234/v1/chat/completions"
        payload = {
            "model": model, 
            "messages": [{"role": "system", "content": "Você é um Copywriter Sênior especializado em vendas internas e prospecção direta B2B."},{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 300
        }
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Olá, detectamos sua empresa e achamos que nossos serviços podem ajudar! Contato: {str(e)[:50]}"

def generate_sales_script(empresa, cidade, telefone):
    prompt = f"Gere uma mensagem persuasiva de WhatsApp para a empresa {empresa} localizada em {cidade}. O telefone é {telefone}."
    return generate_text(prompt)
