import json
import os
import pandas as pd
import rltk
import csv
import re
from rltk.similarity.tf_idf import TF_IDF

tokenizer = rltk.tokenizer.crf_tokenizer.crf_tokenizer.CrfTokenizer()

class expert_records(rltk.Record):
    def __init__(self, raw_object):
        super().__init__(raw_object)
        self.name = ''

    @rltk.cached_property
    def id(self):
        return self.raw_object['ID']

    @rltk.cached_property
    def attraction_name(self):
        return self.raw_object['attraction_name']
    
    @rltk.cached_property
    def about(self):
        return self.raw_object['about']

    
class tripadvisor_records(rltk.Record):
    def __init__(self, raw_object):
        super().__init__(raw_object)
        self.name = ''

    @rltk.cached_property
    def id(self):
        return self.raw_object['ID']

    @rltk.cached_property
    def attraction_name(self):
        return self.raw_object['attraction_name']
    
    @rltk.cached_property
    def attraction_address(self):
        return self.raw_object['attraction_address']
    
    @rltk.cached_property
    def zipcode(self):
        return self.raw_object['zip_code']
    
    @rltk.cached_property
    def rating(self):
        return self.raw_object['attraction_rating']
    
    @rltk.cached_property
    def reviews(self):
        return self.raw_object['attraction_n_reviews']
    
    @rltk.cached_property
    def url(self):
        return self.raw_object['attraction_url']
    
    @rltk.cached_property
    def popular_mentions(self):
        return self.raw_object['popular_mentions']

expert_attraction_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),"data_scraper","expert_attraction.csv")
tripadvisor_attraction_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),"data_scraper","tripadvisor_attraction.csv")

dataset_expert = rltk.Dataset(rltk.CSVReader(expert_attraction_file),record_class=expert_records)
dataset_tripadvisor = rltk.Dataset(rltk.CSVReader(tripadvisor_attraction_file),record_class=tripadvisor_records)

bg = rltk.HashBlockGenerator()
block = bg.generate(bg.block(dataset_expert, function_=lambda r: r.attraction_name[:2]),bg.block(dataset_tripadvisor, function_=lambda r: r.attraction_name[:2]))

def name_similarity_1(r1, r2):
    s1 = r1.attraction_name
    s2 = r2.attraction_name
    
    return rltk.jaro_winkler_similarity(s1, s2)
    
def name_similarity_2(r1, r2):
    l1 = tokenizer.tokenize(r1.attraction_name)
    l2 = tokenizer.tokenize(r2.attraction_name)
    
    tfidf = TF_IDF()

    tfidf.add_document('id1', l1)
    tfidf.add_document('id2', l2)

    tfidf.pre_compute()
    
    return tfidf.similarity('id1', 'id2')

def name_similarity_3(r1,r2):
    l1 = tokenizer.tokenize(r1.attraction_name)
    
    flag=0
    for word in l1:
        if word.lower() in r2.attraction_address.lower():
            flag=1
    if flag==1:
        return 1
    else:
        return 0

def rule_based_method(r1, r2):
    score_1 = name_similarity_1(r1, r2)
    score_2 = name_similarity_2(r1, r2)
    score_3 = name_similarity_3(r1,r2)

    MY_TRESH = 0.75
    total = 0.8*score_2 + 0.2*score_3 
    
    return total > MY_TRESH, total

candidate_pairs = rltk.get_record_pairs(dataset_expert, dataset_tripadvisor)

manual_file = os.path.join(os.path.dirname(__file__),"manually_annotated.json")

with open(manual_file,"r") as f:
    gt = json.load(f)

tp,fp,n = 0,0,0

linked_tripadvisor_names_with_about = {}
for r1, r2 in candidate_pairs:
    result, confidence = rule_based_method(r1, r2)
    if result == True:
        if r1.attraction_name in gt:
            gt.remove(r1.attraction_name)
            tp+=1
        else:
            fp+=1
        linked_tripadvisor_names_with_about[r2.attraction_name] = r1.about
    else:
        n +=1
fn = len(gt)
tn = n - fn
precision = (tp)/(tp+fp)
recall = (tp)/(tp+fn)
f1 = (2*precision*recall)/(precision+recall)

print("The metrics based on our manual evaluation are as follows:")
print(f"Precision = {precision} ; Recall = {recall} ; F-1 score = {f1}")

old_jsonl = os.path.join(os.path.dirname(os.path.dirname(__file__)),"data_scraper","tripadvisor_data.jsonl")
new_jsonl = os.path.join(os.path.dirname(os.path.dirname(__file__)),"data_scraper","tripadvisor_linked_data.jsonl")

with open(old_jsonl,"r") as f:
    fdata = f.read().split("\n")[:-1]

fdata = list(map(lambda a:json.loads(a),fdata))
for d in fdata:
    if d["attraction_name"] in linked_tripadvisor_names_with_about:
        d["expert_review"] = linked_tripadvisor_names_with_about[d["attraction_name"]]
        d["expert_recommended"] = "Yes"
    else:
        d["expert_review"] = ""
        d["expert_recommended"] = "No"
    d["attraction_name"] = d["attraction_name"].replace("'","")

fdata = list(map(lambda a:json.dumps(a),fdata))
out_str = "\n".join(fdata) + "\n"
with open(new_jsonl,"w") as f:
    f.write(out_str)

