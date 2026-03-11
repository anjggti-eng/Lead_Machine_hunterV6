import scrapy

class LeadItem(scrapy.Item):
    empresa = scrapy.Field()
    telefone = scrapy.Field()
    endereco = scrapy.Field()
    cidade = scrapy.Field()
