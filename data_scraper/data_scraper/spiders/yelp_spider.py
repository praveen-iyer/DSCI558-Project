import scrapy
import os
import json

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class YelpSpder(scrapy.Spider):
    name = "yelp"
    zip_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"zip_code_data.jsonl")
    with open(zip_file_path,"r") as f:
        data = f.read().split("\n")[:-1]
    zip_data = map(lambda a:json.loads(a)["zip_code"],data)
    start_urls = [f"https://www.yelp.com/search?find_desc=Restaurants&find_loc={zip}" for zip in zip_data]

    def parse(self,response):
        # driver_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"chromedriver_linux64", "chromedriver")
        # self.driver = webdriver.Chrome(driver_path)
        restaurant_links = response.css('li.border-color--default__09f24__NPAKY span.css-1egxyvc a::attr(href)').getall()
        all_restaurant_links = [response.urljoin(url) for url in restaurant_links]
        yield from response.follow_all(all_restaurant_links, callback = self.parse_restaurant_info)

        page_data = response.css('li.border-color--default__09f24__NPAKY div.pagination__09f24__VRjN4.border--top__09f24__exYYb.border--bottom__09f24___mg5X.border-color--default__09f24__NPAKY  span.css-chan6m::text').get()
        
        if page_data is None:
            return
        
        page_data = page_data.split(" of ")
        
        if page_data[0]!=page_data[1]:
            start_from_val = page_data[0] + "0"
            next_page = f"https://www.yelp.com/search?find_desc=Restaurants&find_loc=94088&start={start_from_val}"
            yield response.follow(next_page, callback = self.parse)
        # self.driver.quit()

    def parse_restaurant_info(self,response):

        def give_empty_data():
            restaurant_data = {}
            restaurant_data["restaurant_name"] = None
            restaurant_data["n_reviews"] = None
            restaurant_data["average_rating"] = None
            restaurant_data["restaurant_address"] = None
            restaurant_data["zip_code"] = None
            restaurant_data["amenities"] = None
            return restaurant_data

        def get_zip_code_from_location_string(location):
            delimeter = "CA "
            zip_code_len = 5
            zip_code = []
            for i in range(location.find(delimeter)+len(delimeter),len(location)):
                if location[i].isdigit():
                    zip_code.append(location[i])
                    if len(zip_code)==zip_code_len:
                        break
            zip_code = "".join(zip_code)

        restaurant_name = response.css('h1.css-1se8maq::text').get()

        n_reviews = response.css('div.arrange__09f24__LDfbs.gutter-1-5__09f24__vMtpw.vertical-align-middle__09f24__zU9sE.margin-b2__09f24__CEMjT.border-color--default__09f24__NPAKY span.css-1fdy0l5::text').get()

        if n_reviews is None:
            n_reviews = response.css('div.arrange__09f24__LDfbs.gutter-1-5__09f24__vMtpw.vertical-align-middle__09f24__zU9sE.margin-b2__09f24__CEMjT.border-color--default__09f24__NPAKY span.css-1fdy0l5 a::text').get()

        if n_reviews is None:
            return give_empty_data()
        
        n_reviews = "".join((c for c in n_reviews if c.isdigit()))

        average_rating = response.css('div.five-stars__09f24__mBKym.five-stars--large__09f24__Waiqf.display--inline-block__09f24__fEDiJ.border-color--default__09f24__NPAKY::attr(aria-label)').get()

        if average_rating is None:
            return give_empty_data()
        
        average_rating = "".join((c for c in average_rating if (c.isdigit() or c==".")))

        if response.css('div address').get() is None:
            return give_empty_data()
        
        location = ", ".join(response.css('div address p span::text').getall())
        if location=="":
            return give_empty_data()
        
        zip_code = get_zip_code_from_location_string(location)

        amenities = self.get_amenities(response)
        if len(amenities)==0:
            return give_empty_data()
        
        processed_amenities = []
        for amenity in amenities:
            processed_amenities += amenity.split(", ")

        restaurant_data = {}
        restaurant_data["restaurant_name"] = restaurant_name
        restaurant_data["n_reviews"] = n_reviews
        restaurant_data["average_rating"] = average_rating
        restaurant_data["restaurant_address"] = location
        restaurant_data["zip_code"] = zip_code
        restaurant_data["amenities"] = amenities

        yield restaurant_data

    def get_amenities(self,response):
        url = response.url
        driver_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"chromedriver_linux64", "chromedriver")
        driver = webdriver.Chrome(driver_path)
        driver.get(url)
        try:
            button = WebDriverWait(driver, timeout=5).until(EC.element_to_be_clickable((By.XPATH, "/html/body/yelp-react-root/div[1]/div[4]/div/div/div[2]/div/div[1]/main/section[3]/div[2]/button")))
            button = button.click()
            amenities = driver.find_elements(By.CSS_SELECTOR,"""section[aria-label="Amenities and More"] span""")
            amenities = [amenity.text.strip() for amenity in amenities]
            amenities = [amenity for amenity in amenities if amenity!="" and amenity!="Show Less"]
        except TimeoutException:
            amenities = response.css('section[aria-label="Amenities and More"]')
            amenities = amenities.css('span::text').getall()
        driver.quit()
        return amenities