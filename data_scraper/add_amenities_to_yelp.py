import json
import os

ip_path = os.path.join(os.path.dirname(__file__),"yelp_data.jsonl")
op_path = os.path.join(os.path.dirname(__file__),"yelp_data_with_amenity_flags.jsonl")

def search_substr(s,ap,aa):
    for a in aa:
        if s in a:
            return -1
    for a in ap:
        if s in a:
            return 1
    return 0


def process_d(d):
    ap = set(d["amenities_present"])
    aa = set(d["amenities_absent"])
    veg_flag = search_substr("Vegetarian", ap, aa)
    park_flag = search_substr("Parking", ap, aa)
    takeout_flag = search_substr("Takeout", ap, aa)
    drivethru_flag = search_substr("Drive-Thru", ap, aa)
    reservation_flag = search_substr("Reservations", ap, aa)
    kids_flag = search_substr("Good For Kids", ap, aa)
    dog_flag = search_substr("Dogs", ap, aa)
    smoking_flag = search_substr("Smoking", ap, aa)

    d["has_vegetarian"] = veg_flag
    d["has_parking"] = park_flag
    d["has_takeout"] = takeout_flag
    d["has_drivethru"] = drivethru_flag
    d["has_reservation"] = reservation_flag
    d["is_good_for_kids"] = kids_flag
    d["dogs_allowed"] = dog_flag
    d["smoking_allowed"] = smoking_flag
    d["restaurant_name"] = d["restaurant_name"].replace("'","")
    d["restaurant_address"] = d["restaurant_address"].replace("'","")

    # print(veg_flag+park_flag+takeout_flag+drivethru_flag+reservation_flag+kids_flag+dog_flag+smoking_flag)
    return d

with open(ip_path,"r") as f:
    fdata = f.read().split("\n")

fdata = list(filter(lambda a:a.strip()!="", fdata))
fdata = list(map(lambda a:json.loads(a),fdata))
fdata = list(map(lambda d:process_d(d),fdata))
fdata = list(map(lambda a:json.dumps(a),fdata))
out_str = "\n".join(fdata) + "\n"

with open(op_path,"w") as f:
    f.write(out_str)