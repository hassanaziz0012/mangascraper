from typing import List
import requests
import time
import re
import json
import scrapy
from scrapy.http.response.html import HtmlResponse


class MangaReaderSpider(scrapy.Spider):
    name = "chapter"

    start_urls = [
        "https://mangapill.com/search?q=&type=&status=&genre=Action&genre=Adventure&genre=Cars&genre=Comedy&genre=Dementia&genre=Demons&genre=Doujinshi&genre=Drama&genre=Ecchi&genre=Fantasy&genre=Game&genre=Gender+Bender&genre=Harem&genre=Historical&genre=Horror&genre=Isekai&genre=Josei&genre=Kids&genre=Magic&genre=Martial+Arts&genre=Mecha&genre=Military&genre=Music&genre=Mystery&genre=Parody&genre=Police&genre=Psychological&genre=Romance&genre=Samurai&genre=School&genre=Sci-Fi&genre=Seinen&genre=Shoujo&genre=Shoujo+Ai&genre=Shounen&genre=Shounen+Ai&genre=Slice+of+Life&genre=Space&genre=Sports&genre=Super+Power&genre=Supernatural&genre=Thriller&genre=Tragedy&genre=Vampire&genre=Yaoi&genre=Yuri"
    ]
    manga_links = []
    mangas = []

    def parse(self, response: HtmlResponse):
        hrefs = response.css('div.my-3.grid div a::attr(href)').getall()

        for href in hrefs:
            self.manga_links.append("https://mangapill.com" + href)

        next_hrefs = response.css('a.btn.btn-sm')
        next_link = self.get_next_page(next_hrefs)

        if next_link is not None:
            print(f"{len(self.manga_links)} mangas scanned. Moving to next page...")
            yield scrapy.Request(next_link, self.parse)
        else:
            print(f"{len(self.manga_links)} mangas scanned. Scraping metadata.")
            for link in self.manga_links:
                yield scrapy.Request(link, self.parse_manga)

    def get_next_page(self, btns):
        selectors = btns
        for selector in selectors:
            if selector.css('::text').extract()[0] == "Next":
                relative_link = selector.css('::attr(href)').get()
                absolute_link = "https://mangapill.com" + relative_link
                return absolute_link
        return None

    def parse_manga(self, response: HtmlResponse):
        cover_img = response.css("div.text-transparent.bg-card.rounded img::attr(data-src)").get()

        metadata = response.css("div.flex.flex-col")
        title = metadata.css("div.mb-3 h1.font-bold::text").get()
        description = metadata.css("div.mb-3 p.text-sm::text").get()
        
        # Get Status
        pub_info_elem = metadata.css("div.grid div")
        pub_info = {
            'type': None,
            'status': None,
            'year': None,
        }
        for item in pub_info_elem:
            if item.css("label::text").get() == "Type":
                elems = item.css("div::text").extract()
                type = [elem for elem in elems if elem != "\n"][0]
                pub_info.update({'type': type})

            if item.css("label::text").get() == "Status":
                elems = item.css("div::text").extract()
                status = [elem for elem in elems if elem != "\n"][0]
                pub_info.update({'status': status})

            if item.css("label::text").get() == "Year":
                elems = item.css("div::text").extract()
                year = [elem for elem in elems if elem != "\n"][0]
                pub_info.update({'year': year})

        # Scraping chapters
        chapters = response.css('div#chapters div.grid a')
        chaps = []
        for chap in chapters.css("::attr(href)"):
            chaps.append("https://mangapill.com" + chap.extract())
        chaps.reverse()

        manga = {
            "title": title,
            "description": description,
            "cover_img": cover_img,
            "type": pub_info.get('type'),
            "status": pub_info.get('status'),
            "year": pub_info.get('year'),
            "chapters": [],
            "chapter_links": chaps,
        }
        print(f"Scraping and Saving {title}...")
        # self.save_manga(manga)

        for i, chap in enumerate(chaps):
            name = f"Chapter {i}"
            yield scrapy.Request(chap, self.parse_chapter, cb_kwargs={"manga": manga, "name": name, "order": i})

    def save_manga(self, manga):
        print(f"Saving manga {manga.get('title')}...")
        filename = "".join([c for c in manga.get('title') if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        with open(f'mangas/{filename}.json', 'w+') as file:
            file.write(json.dumps(manga))

    def parse_chapter(self, response: HtmlResponse, manga, name, order):
        images = response.css('div.lg\:container chapter-page div.border div.relative picture img::attr(data-src)').getall()

        print(f"Scraping {name} of {manga.get('title')}...")
        panels = []
        for i, img in enumerate(images):
            panels.append(img)
        
        chapter = {
            'name': name,
            'order': order,
            'panels': panels
        }

        chapters = manga['chapters']
        chapters.append(chapter)
        manga['chapters'] = chapters
        self.save_manga(manga)
