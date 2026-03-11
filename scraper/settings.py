BOT_NAME = "engine"

ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
COOKIES_ENABLED = True

DEFAULT_REQUEST_HEADERS = {
    "Accept-Language": "pt-BR,pt;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

AUTOTHROTTLE_ENABLED = True
ITEM_PIPELINES = {
   'scraper.pipelines.LeadPipeline': 300,
}
