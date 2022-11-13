# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class JSONWriterPipeline:
    def open_spider(self,spider):
        if spider.name == "zip_codes_and_yelp":
            self.f1 = open("zip_code_data.jsonl","w",encoding = "utf-8")
            self.f2 = open("yelp_data.jsonl","w",encoding = "utf-8")
        
        if spider.name == "tripadvisor_attractions":
            self.f3 = open("tripadvisor_data.jsonl","w",encoding = "utf-8")
    
    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"

        if spider.name == "zip_codes_and_yelp":
            if "nearby_zip_codes" in item:
                self.f1.write(line)
            if "restaurant_name" in item:
                self.f2.write(line)

        if spider.name == "tripadvisor_attractions":
            self.f3.write(line)
        return item

    def close_spider(self,spider):
        if spider.name == "zip_codes_and_yelp":
            self.f1.close()
            self.f2.close()
        
        if spider.name == "tripadvisor_attractions":
            self.f3.close()

class DuplicatesPipeline:

    def open_spider(self,spider):
        if spider.name == "zip_codes_and_yelp":
            self.s1 = set()
            self.s2 = set()
        
        if spider.name == "tripadvisor_attractions":
            self.s3 = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if spider.name == "zip_codes_and_yelp":
            if "nearby_zip_codes" in adapter:
                if adapter["zip_code"] not in self.s1:
                    self.s1.add(adapter["zip_code"])
                    return item
                else:
                    raise DropItem(f"Duplicate item found: {item!r}")

            if "restaurant_name" in adapter:
                if adapter["restaurant_name"] not in self.s2:
                    self.s2.add(adapter["restaurant_name"])
                    return item
                else:
                    raise DropItem(f"Duplicate item found: {item!r}")
        
        if spider.name == "tripadvisor_attractions":
            if adapter["attraction_name"] not in self.s3:
                self.s3.add(adapter["attraction_name"])
                return item
            else:
                raise DropItem(f"Duplicate item found: {item!r}")