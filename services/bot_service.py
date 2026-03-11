from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random
import re
from webdriver_manager.chrome import ChromeDriverManager

def silent_lead_enricher(name, location):
    """
    ENRIQUECEDOR SILENCIOSO v7.0 (Scrapy-Style)
    Busca o telefone sem abrir navegador, usando DuckDuckGo + Scraping.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    search_query = f"{name} {location} telefone whatsapp"
    url = f"https://duckduckgo.com/html/?q={search_query.replace(' ', '+')}"
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            phone_pattern = r"\(?\d{2}\)?\s?9?\d{4}-?\d{4}"
            phones = re.findall(phone_pattern, text)
            if phones:
                for p in phones:
                    if "9" in p: return p
                return phones[0]
    except: pass
    return "Pendente"

def hunt_leads_master(query):
    """
    MASTER HUNTER ELITE v6.8 - Headless & Fast.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Desativa imagens
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    leads_found = []
    try:
        url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        driver.get(url)
        time.sleep(5)
        
        cards = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
        for i in range(min(len(cards), 10)):
            try:
                card = cards[i]
                name = card.get_attribute("aria-label") or "Empresa"
                driver.execute_script("arguments[0].click();", card)
                time.sleep(3)
                
                html = driver.page_source
                phones = re.findall(r"\(?\d{2}\)?\s?9?\d{4}-?\d{4}", html)
                phone = phones[0] if phones else "Não informado"
                
                address = "Brasil"
                details = driver.find_elements(By.CSS_SELECTOR, ".Io6YTe")
                for d in details:
                    if any(c.isdigit() for c in d.text) and len(d.text) > 10:
                        address = d.text
                        break

                leads_found.append({"name": name, "whatsapp": phone, "address": address})
            except: continue
        return leads_found
    finally:
        driver.quit()

def quick_phone_hunt(company_name):
    # Redireciona para o Silent Hunter para máxima velocidade
    return silent_lead_enricher(company_name, "Brasil")
