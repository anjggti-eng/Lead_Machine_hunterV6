import scrapy
from scraper.items import LeadItem

class LeadSpider(scrapy.Spider):
    name = "lead_spider"
    
    def __init__(self, query=None, location=None, *args, **kwargs):
        super(LeadSpider, self).__init__(*args, **kwargs)
        self.query = query
        self.location = location
        self.limit = 10
        self.count = 0

    def start_requests(self):
        # Usando DuckDuckGo para encontrar sites de empresas ou diretórios
        search_query = f"{self.query} {self.location} telefone"
        url = f"https://duckduckgo.com/html/?q={search_query.replace(' ', '+')}"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Aqui extraímos informações básicas dos resultados de busca
        results = response.css('.result')
        for res in results:
            if self.count >= self.limit:
                break
            
            title = res.css('.result__title a::text').get()
            snippet = res.css('.result__snippet::text').get() or ""
            
            if title:
                item = LeadItem()
                item['empresa'] = title.strip()
                item['endereco'] = self.location
                
                # Regex para pegar telefone no snippet
                import re
                phone_pattern = r"\(?\d{2}\)?\s?9?\d{4}-?\d{4}"
                phones = re.findall(phone_pattern, snippet)
                item['telefone'] = phones[0] if phones else "Pendente"
                
                yield item
                self.count += 1
