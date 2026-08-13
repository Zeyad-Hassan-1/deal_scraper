# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ProductItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    image = scrapy.Field()
    old_price = scrapy.Field()
    rating = scrapy.Field()
    sku = scrapy.Field()
    delivery_cairo = scrapy.Field()
    delivery_outside = scrapy.Field()
    specs = scrapy.Field()
    url = scrapy.Field()
    store = scrapy.Field()
    country = scrapy.Field()
