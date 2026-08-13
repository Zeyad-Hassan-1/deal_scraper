import scrapy

class ProductItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    image = scrapy.Field()
    delivery_time = scrapy.Field()
    rating = scrapy.Field()
    sku = scrapy.Field()
    specs = scrapy.Field()
    url = scrapy.Field()
    store = scrapy.Field()
    country = scrapy.Field()