from scrapy import Spider, Request
from spider.items import RedfinItem

list_of_zipcode = [20001]


class RedfinSpider(Spider):
    name = "redfin_spider"
    allowed_urls = ['https://www.redfin.com/zipcode']
    start_urls = ['https://www.redfin.com/zipcode/{i}' for i in list_of_zipcode]

    #get all urls to parse through 
    def parse(self, response):

        #loop through all zipcodes 
        for zipcode in list_of_zipcode:
            
            #for each zipcode get number of pages 
            num_of_pages = int(response.xpath("//div[@class = 'viewingPage']//span[@class='pageText']/text()").extract()[0].split(" ")[-1])
            
            page_urls = [f"https://www.redfin.com/zipcode/{zipcode}/page-{i}" for i in range(num_of_pages)]

            for url in page_urls: 
                yield Request(url=url, callback=self.get_listing_urls)

    #parse through all the listing urls
    def get_listing_urls(self, response):
        domain_url = "www.redfin.com"
        sub_listing_urls = response.xpath("//div[@class='PhotoSlider photoContainer']//a/@href").extract()
        listing_urls = [domain_url+i for i in sub_listing_urls]

        print("="*55)
        print(listing_urls)
        print("="*55)
        # for listing_url in listing_urls:
        #     yield Request(url=listing_url, callback=self.get_listing_features)


    def get_listing_features(self, response):
        #zipcode
        #city
        #state
        #etc
        pass