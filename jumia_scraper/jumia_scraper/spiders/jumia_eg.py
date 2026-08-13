from scrapy.http import response
import scrapy
from jumia_scraper.items import ProductItem

class JumiaEgSpider(scrapy.Spider):
    name = "jumia_eg"
    allowed_domains = ["jumia.com.eg"]

    def __init__(self, query=None, category=None, max_price=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if query:
            self.start_url = f"https://www.jumia.com.eg/catalog/?q={query}"
        elif category:
            self.start_url = f"https://www.jumia.com.eg/{category}/"
        else:
            raise ValueError("Provide either -a query=... or -a category=...")
            
        if max_price and max_price.lower() != "skip" and max_price.isdigit():
            # Jumia uses &price=MIN-MAX or ?price=MIN-MAX
            separator = "&" if "?" in self.start_url else "?"
            self.start_url += f"{separator}price=0-{max_price}"
            
        self.start_urls = [self.start_url]

    # pyrefly: ignore [bad-override-mutable-attribute]
    def parse(self, response):
        yield from self.parse_products(response)

    def parse_products(self, response):
        products = response.css('article.prd')
        print(f"Found {len(products)} products")
        for p in products:
            title = p.css('h3.name::text').get()
            price = p.css('div.prc::text').get()
            image = p.css('img.img::attr(data-src)').get()
            relative_link = p.css('a.core::attr(href)').get()
            absolute_link = response.urljoin(relative_link)
            
            yield scrapy.Request(
                url = absolute_link,
                callback = self.parse_product,
                meta = {
                    'title' : title,
                    'price' : price,
                    'image' : image,
                }
            )

        # auto-follow next page
        next_page = response.css('a[aria-label="Next Page"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_products)

    def parse_product(self, response):
        title = response.meta['title']
        price = response.meta['price']
        image = response.meta['image']
        rating = response.css("div.stars::text").get()
        delivery_blocks = response.css("div.markup.-ptxs")
        delivery_time = delivery_blocks[1].css("::text").getall() if len(delivery_blocks) > 1 else None
        delivery_time = " ".join(delivery_time).strip() if delivery_time else None      
        sku_raw = response.xpath("//span[text()='SKU']/parent::li//text()").getall()
        sku = "".join(sku_raw).replace("SKU", "").replace(":", "").strip()
        specs = {}
        features = []
        feature_rows = response.xpath(
            "//h3[text()='Key Features']/following-sibling::div[contains(@class,'markup')]//li | "
            "//h3[text()='Key Features']/following-sibling::div[contains(@class,'markup')]//p"
        )
        for row in feature_rows:
            full_text = " ".join(row.css("::text").getall()).strip()
            if not full_text:
                continue
            if ":" in full_text:
                label, value = full_text.split(":", 1)
                if value.strip():
                    specs[label.strip()] = value.strip()
                else:
                    features.append(full_text)
            else:
                features.append(full_text)

        # Also try the Specifications table (some products have it)
        spec_rows = response.xpath(
            "//h3[text()='Specifications']/following-sibling::div//li"
        )
        for row in spec_rows:
            texts = row.css("::text").getall()
            texts = [t.strip() for t in texts if t.strip()]
            if len(texts) >= 2:
                specs[texts[0].rstrip(":")] = " ".join(texts[1:])

        if features:
            specs["features"] = features
                
        yield ProductItem(
            title=title,
            price=price,
            image=image,
            delivery_time=delivery_time,
            rating=rating,
            sku=sku,
            url=response.url,
            specs=specs,
            store="jumia_eg",
            country="EG",
        )