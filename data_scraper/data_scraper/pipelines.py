# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from itemadapter import ItemAdapter


class JSONWriterPipeline:
    def open_spider(self,spider):
        self.f1 = open("zip_code_data.jsonl","w",encoding = "utf-8")
        self.f2 = open("yelp_data.jsonl","w",encoding = "utf-8")
    
    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        if "nearby_zip_codes" in item:
            self.f1.write(line)
        if "restaurant_name" in item:
            self.f2.write(line)
        return item
