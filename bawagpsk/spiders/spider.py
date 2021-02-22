import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import BawagpskItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class BawagpskSpider(scrapy.Spider):
	name = 'bawagpsk'
	start_urls = ['https://www.bawagpsk.com/BAWAGPSK/Ueber_uns/Presse/300106/archiv.html?int=BAWAGPSK|Ueber_uns|Presse|AktuelleNews|AktuelleNews,2,1,#collapse4_517198']

	def parse(self, response):
		post_links = response.xpath('//a[@target="_self"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)


	def parse_post(self, response):
		title = response.xpath('//h2/text()').get()

		content = response.xpath('//div[@class="col--container"]//text()[not (ancestor::h2)]').getall()
		content = [x for x in content if "(PDF)" not in x]
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))
		date = response.xpath('//div[@class="col--container"]//p//text()').getall()[0:5]
		try:
			date = re.findall(r'\d+\.\s\w+\s\d+',''.join(date))
		except date is None:
			date = re.findall(r'\d+\.\s?\w+\s\d+',''.join(date).replace("\xa0", " "))

		item = ItemLoader(item=BawagpskItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
