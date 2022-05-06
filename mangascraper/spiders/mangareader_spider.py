import scrapy
from scrapy.http.response.html import HtmlResponse


class MangaReaderSpider(scrapy.Spider):
    name = "mangareader"

    start_urls = [
        "https://mangareader.to/az-list"
    ]

    def parse(self, response: HtmlResponse):
        mangas = response.css('div.mls-wrap div.item a.manga-poster::attr(href)').getall()
        manga_links = []
        for manga in mangas:
            manga_link = "https://mangareader.to" + manga
            manga_links.append(manga_link)
            
            break

        
            

