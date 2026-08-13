import os
from scrapy.http import response
import scrapy
# pyrefly: ignore [missing-import]
from scrapers.items import ProductItem


def get_meta(extra_meta=None):
    meta = {"impersonate": "chrome120"}
    proxy = os.environ.get("PROXY_URL")
    if proxy:
        meta["proxy"] = proxy
        # pyrefly: ignore [bad-assignment]
        meta["impersonate_args"] = {"verify": False}
    if extra_meta:
        meta.update(extra_meta)
    return meta

class TwoBEgSpider(scrapy.Spider):
    name = "twoB_eg"
    allowed_domains = ["2b.com.eg"]

    def __init__(self, query=None, category=None, max_price=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_url = "https://2b.com.eg/en/computers/laptops.html"
            
        if max_price and max_price.lower() != "skip" and max_price.isdigit():
            # As the user noted, price filter only works for categories on 2B
            separator = "&" if "?" in self.start_url else "?"
            self.start_url += f"{separator}price=0-{max_price}"
        
    async def start(self):
        yield scrapy.Request(url=self.start_url, callback=self.parse, meta=get_meta())

    # pyrefly: ignore [bad-override-mutable-attribute]
    def parse(self, response):
        yield from self.parse_products(response)

    def parse_products(self, response):
        products = response.css('div.product-item-info')
        print(f"Found {len(products)} products")
        for p in products:
            title = p.css('a.product-item-link::text').get()
            link = p.css('a.product-item-link::attr(href)').get()
            rating = p.css('span.rating-value::text').get()
            old_price = p.css('span.old-price .price::text').get()
            price = p.css('span[id^="product-price-"] .price::text').get()
            image = p.css('img.product-image-photo::attr(src)').get()

            yield scrapy.Request(
                url = link,
                callback = self.parse_product,
                meta = get_meta({
                    'title' : title,
                    'price' : price,
                    'old_price': old_price,
                    'rating': rating,
                    'image' : image
                })
            )

        # auto-follow next page
        next_page = response.css('li.pages-item-next a.action.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse_products, meta=get_meta())

    def parse_product(self, response):
        title = response.meta['title']
        price = response.meta['price']
        old_price = response.meta['old_price']
        rating = response.meta['rating']

        delivery_items = response.css('div.delivery-info-grid div.info-item')
        delivery_cairo = delivery_items[0].css('div.info-content > p::text').get()
        delivery_outside = delivery_items[1].css('div.info-content > p::text').get()

        sku = response.css('div.product-sku span.spec-value::text').get()

        specs = {}
        spec_rows = response.css('table#product-attribute-specs-table tbody tr')
        for row in spec_rows:
            label = row.css('th.col.label::text').get()
            value = row.css('td.col.data::text').get()
            if label and value:
                specs[label.strip()] = value.strip()

        yield ProductItem(
            title=title,
            price=price,
            old_price=old_price,
            rating=rating,
            sku=sku,
            delivery_cairo=delivery_cairo,
            delivery_outside=delivery_outside,
            specs=specs,
            url=response.url,
            store="2b_eg",
            country="EG",
        )