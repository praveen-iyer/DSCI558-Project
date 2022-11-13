import scrapy

class AttractionSpider(scrapy.Spider):
    name = "tripadvisor_attractions"

    start_urls = ["https://www.tripadvisor.com/Attractions-g28926-Activities-a_allAttractions.true-California.html"]

    def parse(self,response):
        all_page_urls = response.css('div.DDJze section.jemSU div.BqDzz.z div.hZuqH div.alPVI.eNNhq.PgLKC.tnGGX a:not([class="BMQDV _F G- wSSLS SwZTJ FGwzt ukgoS"])').css('a::attr(href)').getall()
        all_page_urls = [response.urljoin(url) for url in all_page_urls]
        yield from response.follow_all(all_page_urls, callback=self.parse_attraction_info)

        next_page_details = response.css('div.DDJze section.jemSU div.uYzlj.c div.biGQs._P.pZUbB.hmDzD div.Ci::text').getall()
        # Looks like ['Showing results ', '28,381', '-', '28,397', ' of ', '28,397']
        next_page_possibility = not (next_page_details[-3].strip() == next_page_details[-1].strip())
        if next_page_possibility:
            number = next_page_details[-3].strip().replace(",","")
            next_page_url = f"https://www.tripadvisor.com/Attractions-g28926-Activities-oa{number}-California.html"
            yield response.follow(next_page_url,callback = self.parse)

    def parse_attraction_info(self,response):
        attraction_data = {}

        def give_empty_data():
            data =  {}
            data["attraction_name"] = None
            data["attraction_address"] = None
            data["zip_code"] = None
            data["attraction_rating"] = None
            data["attraction_n_reviews"] = None
            return data


        if response.css('div.vAiJm h1.biGQs._P.fiohW.eIegw::text').get() is not None:
            attraction_name = response.css('div.vAiJm h1.biGQs._P.fiohW.eIegw::text').get().strip()

            if not response.css('div.ZhNYD div.MJ').getall():
                attraction_data = give_empty_data()

            else:

                location = response.css('div.ZhNYD div.MJ button.UikNM.G.B-._S._T.c.G.P0.wSSLS.wnNQG.raEkE span.biGQs._P.XWJSj.Wb::text').get()
                if not location:
                    location = response.css('div.ZhNYD div.MJ span.biGQs._P.XWJSj.Wb::text').getall()
                    if location:
                        location = location[-1]
                    else:
                        location = ""
                # location = "2800 E. Observatory Rd., Los Angeles, CA 90027-1299"

                if location:
                    delimeter = "CA "
                    zip_code_len = 5
                    zip_code = []
                    for i in range(location.find(delimeter)+len(delimeter),len(location)):
                        if location[i].isdigit():
                            zip_code.append(location[i])
                            if len(zip_code)==zip_code_len:
                                break
                    zip_code = "".join(zip_code)

                    rev_rat = response.css('div.eSDnY div.bdeBj.e div.yFKLG div.f.u.j')
                    if rev_rat.getall():
                        rating = float(rev_rat.css('div.biGQs._P.fiohW.hzzSG.uuBRH::text').get().strip())
                        n_reviews = rev_rat.css('span.biGQs._P.pZUbB.biKBZ.KxBGd::text').get()
                        n_reviews = int("".join((c for c in n_reviews if c.isdigit())))
                    else:
                        rating = None
                        n_reviews = None

                    attraction_data["attraction_name"] = attraction_name
                    attraction_data["attraction_address"] = location
                    attraction_data["zip_code"] = zip_code
                    attraction_data["attraction_rating"] = rating
                    attraction_data["attraction_n_reviews"] = n_reviews
                else:
                    attraction_data = give_empty_data()

            yield attraction_data
        
        else:
            attraction_data = give_empty_data()
            yield attraction_data