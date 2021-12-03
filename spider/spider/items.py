# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RedfinItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    address = scrapy.Field()
    state_zipcode = scrapy.Field()
    price = scrapy.Field()
    bed = scrapy.Field()
    bath = scrapy.Field()
    square_footage = scrapy.Field()
    description = scrapy.Field()
    status = scrapy.Field()
    time_on_redfin = scrapy.Field()
    property_type = scrapy.Field()