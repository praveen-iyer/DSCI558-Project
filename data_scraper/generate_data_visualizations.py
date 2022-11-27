import matplotlib.pyplot as plt
import json
import os
from collections import defaultdict

yelp_file = os.path.join(os.path.dirname(__file__),"yelp_data_with_amenity_flags.jsonl")
attraction_file = os.path.join(os.path.dirname(__file__),"tripadvisor_linked_data.jsonl")

def read_jsonl(fpath):
    with open(fpath,"r") as f:
        fdata = f.read().split("\n")[:-1]
    fdata = list(map(lambda a:json.loads(a),fdata))
    return fdata

def get_zip_counts(data):
    zc = defaultdict(int)
    for d in data:
        zc[int(d["zip_code"])]+=1
    return zc

def generate_zc_plot(fpath, base_name, save_dir = os.path.join(os.path.dirname(__file__))):
    data = read_jsonl(fpath)
    zc = get_zip_counts(data)
    zc = sorted(zc.items(),key = lambda a:-a[1])[:10]
    z,c = zip(*zc)
    plt.plot(c)
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.xlabel("ZIP Codes")
    plt.ylabel(f"Number of {base_name}")
    plt.title(f"{base_name.title()} distribution across ZIP codes")
    fig_path = os.path.join(save_dir, f"zip_code_wise_{base_name}_distribution.png")
    plt.savefig(fig_path)
    plt.show()
    plt.clf()

yelp_data = generate_zc_plot(yelp_file,"restaurants")
attraction_file = generate_zc_plot(attraction_file,"attractions")