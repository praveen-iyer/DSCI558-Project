import scrapy
import os
import json

class YelpSpder(scrapy.Spider):
    name = "yelp"
    zip_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"zip_code_data.jsonl")
    with open(zip_file_path,"r") as f:
        data = f.read().split("\n")[:-1]
    zip_data = map(lambda a:json.loads(a)["zip_code"],data)
    start_urls = [f"https://www.yelp.com/search?find_desc=Restaurants&find_loc={zip}" for zip in zip_data]

    def parse(self,response):
        restaurant_links = response.css('li.border-color--default__09f24__NPAKY span.css-1egxyvc a::attr(href)').getall()
        all_restaurant_links = [response.urljoin(url) for url in restaurant_links]
        yield from response.follow_all(all_restaurant_links, callback = self.parse_restaurant_info)

        page_data = response.css('li.border-color--default__09f24__NPAKY div.pagination__09f24__VRjN4.border--top__09f24__exYYb.border--bottom__09f24___mg5X.border-color--default__09f24__NPAKY  span.css-chan6m::text').getall().split(" of ")
        
        if page_data[0]!=page_data[1]:
            start_from_val = page_data[0] + "0"
            next_page = f"https://www.yelp.com/search?find_desc=Restaurants&find_loc=94088&start={start_from_val}"
        yield response.follow(next_page, callback = self.parse)

    def parse_restaurant_info(self,response):
        restaurant_name = response.css('h1.css-1se8maq::text').get()