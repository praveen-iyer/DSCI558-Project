import scrapy

class AttractionSpider(scrapy.Spider):
    name = "zip_codes_and_yelp"

    start_urls = ["https://www.unitedstateszipcodes.org/ca/"]

    def parse(self,response):
        zip_code_items = response.css('div.panel.panel-default.panel-prefixes div.list-group-item')
        zip_codes = []
        for zip_code_item in zip_code_items:
            type_of_zip_code = zip_code_item.css('div.col-xs-12.prefix-col2::text').get().strip().lower()
            if type_of_zip_code != "standard":
                continue
            zip_code = zip_code_item.css('div.col-xs-12.prefix-col1 a::text').get().strip()
            print(zip_code)
            zip_codes.append(zip_code)
            zip_code_url = f"https://www.unitedstateszipcodes.org/{zip_code}/"
            yield response.follow(zip_code_url,callback = self.parse_zip_info)
            ## 95836 was getting 404
        print("Number of zip codes",len(zip_codes))

    def parse_zip_info(self,response):
        zip_code_data = {}
        zip_code = response.url.rstrip("/").split("/")[-1]
        neighborhood = response.css('table.table.table-condensed.table-striped tbody tr')[1]
        neighborhood_list = neighborhood.css('tr td::text').get().strip().split("|")
        city = response.css('dl.dl-horizontal dd::text').get().strip()
        nearby_zip_codes = []
        def get_digits(s):
            return ''.join(c for c in s if c.isdigit())
        if response.css('ul.list-unstyled.nearby-zips-links.clearfix'):
            nearby_zip_codes = response.css('ul.list-unstyled.nearby-zips-links.clearfix li a::text').getall()
            nearby_zip_codes = list(map(get_digits,nearby_zip_codes))

        zip_code_data["zip_code"] = zip_code
        zip_code_data["neighborhood_list"] = neighborhood_list
        zip_code_data["city"] = city
        zip_code_data["nearby_zip_codes"] = nearby_zip_codes

        yield zip_code_data