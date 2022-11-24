import json
import os

import pandas as pd

ip_file = os.path.join(os.path.dirname(__file__),"tripadvisor_data.jsonl")
op_file = os.path.join(os.path.dirname(__file__),"tripadvisor_attraction.csv")

with open(ip_file,"r") as f:
    data = f.read().split("\n")[:-1]

data = list(map(lambda a:json.loads(a),data))

cols = list(data[0].keys())

d = {}
for col in cols:
    d[col] = list(map(lambda a:a[col],data))

df = pd.DataFrame(d)
df.to_csv(op_file, index=False)