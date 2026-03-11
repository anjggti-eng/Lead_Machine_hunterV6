import scrapy
from scrapy.selector import Selector
import requests
import random
import time
import re

# --- CONFIGURAÇÃO STEALTH PROFISSIONAL 2026 ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
]

class EmpresasSpider(scrapy.Spider):
    """
    Spider para diretórios empresariais estruturados.
    """
    name = "empresas"
    
    # settings.py integrado via custom_settings
    custom_settings = {
        'CONCURRENT_REQUESTS': 3,
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'COOKIES_ENABLED': True,
        'AUTOTHROTTLE_ENABLED': True,
        'ROBOTSTXT_OBEY': False
    }

    def parse(self, response):
        # Seleção Dinâmica (Baseado no seu exemplo real)
        cards = response.css(".company-card, .list-item, article")

        for card in cards:
            # TÉCNICA AVANÇADA 1: XPath para links 'tel:'
            telefone = card.xpath(".//a[contains(@href,'tel:')]/text()").get()
            
            # TÉCNICA AVANÇADA 2: Regex para telefones escondidos em Scripts/TEXTO
            if not telefone:
                # Procura padrão (XX) XXXXX-XXXX ou XX XXXXX-XXXX
                phones = re.findall(r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}", card.get())
                telefone = phones[0] if phones else "Não localizado"

            yield {
                "nome": card.css(".company-name::text, h2::text, .title::text").get(),
                "telefone": telefone,
                "endereco": card.css(".address::text, .location::text").get(),
            }

class extraction_engine:
    """Motor que orquestra Scrapy e Regex Fallback."""
    
    @staticmethod
    def smart_extract_phone(html_content):
        """Usa Regex para caçar telefones em qualquer HTML/Script."""
        # Padrão brasileiro: (11) 99999-9999 ou 11 9999-9999
        pattern = r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}"
        matches = re.findall(pattern, html_content)
        return matches[0] if matches else "Não encontrado"

    @staticmethod
    def quick_get(url):
        """Scraper ultra-leve com headers humanos e delay."""
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        time.sleep(random.uniform(2, 5))
        
        try:
            res = requests.get(url, headers=headers, timeout=10)
            sel = Selector(text=res.text)
            
            # Tenta extrair telefone via Regex no corpo todo do site
            phone = extraction_engine.smart_extract_phone(res.text)
            
            return {
                "title": sel.css('title::text').get(),
                "phone": phone,
                "status": "sucesso"
            }
        except Exception as e:
            return {"status": "erro", "msg": str(e)}

# Instância Global
scraper_engine = extraction_engine()
