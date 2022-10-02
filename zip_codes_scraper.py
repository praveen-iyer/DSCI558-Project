import time
import requests
from bs4 import BeautifulSoup


def get_nearby_zip_codes(zip_code):
    url = f"https://www.unitedstateszipcodes.org/{zip_code}/"
    headers = {"User-Agent": "Praveen Ubuntu"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    try:
        results = soup.find("ul",{"class":"list-unstyled nearby-zips-links clearfix"}).findAll("li")
    except AttributeError:
        return []
    results = list(map(lambda a:a.find("a").get_text().strip(),results))
    def get_digits(s):
        return int(''.join(c for c in s if c.isdigit()))
    results = list(map(get_digits,results))
    return results

def get_zip_codes_ca(zip_codes_url_ca):
    headers = {"User-Agent": "Praveen Ubuntu"}
    page = requests.get(zip_codes_url_ca, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.findAll("div", {"class" : "list-group-item"})
    results = list(filter(lambda a:a.find("div",{"class":"col-xs-12 prefix-col2"}).get_text().strip()!="PO Box",results))
    results = list(map(lambda a:a.find("div",{"class":"col-xs-12 prefix-col1"}).get_text().strip(),results))
    results = list(filter(lambda a:len(a)>0,results))
    results = list(map(int,results))
    return results

def main():
    zip_codes_url_ca = "https://www.unitedstateszipcodes.org/ca/"
    zip_codes_ca = get_zip_codes_ca(zip_codes_url_ca)
    zip_vs_nearby = {}
    for zip_code in zip_codes_ca:
        zip_vs_nearby[zip_code] = get_nearby_zip_codes(zip_code)
    print(zip_vs_nearby)

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(f"Time taken for execution is = {end-start}")
