import scrapy

class AttractionSpider(scrapy.Spider):
    name = "tripadvisor_attractions"

    start_urls = ["https://www.imdb.com/chart/top"]