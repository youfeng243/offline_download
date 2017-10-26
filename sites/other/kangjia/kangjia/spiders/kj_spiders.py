# -*- coding: utf-8 -*-
from kangjia.items import ShafaItem
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule, Request
from scrapy.linkextractors import LinkExtractor


class ShafaSpider(CrawlSpider):
    name = 'shafa'
    allowed_domains = ["app.shafa.com"]
    start_urls = ["http://app.shafa.com"]
    rules = (
        Rule(LinkExtractor(allow=("/archives/\d+\.html", )), callback='parse_item'),
    )

    def parse_item(self, response):
        self.log('当前正在抓取的列表页是：%s' % response.url)

        apps = Selector(response).xpath("//div[@class='container']/div[@class='row'][3]/div[@class='col-sm-6']/a/@href")
        # for a in apps:
        #     print a.extract()
        #     yield Request(url=a.extract(), callback=self.parse_ear_app)
        yield Request(url=apps[3].extract(), callback=self.parse_ear_app)

    def parse_ear_app(self, response):
        self.log('当前正在抓取的内容页是：%s' % response.url)

        sel = Selector(response)
        item = ShafaItem()
        item['app_name'] = sel.xpath("//div[@class='view-header-title']/h1/text()").extract()
        item['cat'] = sel.xpath("//ol[@class='breadcrumb']/li[4]/a/text()|//ol[@class='breadcrumb']/li[5]/a/text()|//ol[@class='breadcrumb']/li[6]/a/text()").extract()
        item['comments'] = sel.xpath("//section[@class='app-view-section app-view-comment']/h2/small/a/text()").extract()
        item['control_type'] = sel.xpath("//div[@class='view-header-middle']/div[@class='view-header-rating']/span[3]/text()").extract()
        item['download_link'] = sel.xpath('//*[@id="downloadModal"]/div/div/div[3]/div/a[2]/@data-url').extract()
        item['downloads'] = sel.xpath(u"//ul[@class='view-info-list list-unstyled']/li/div[contains(text(),'下载')]/../span/text()").extract()
        item['introduction'] = sel.xpath("//section[@class='app-view-desc app-view-section']/p[1]/text()").extract()
        item['language'] = sel.xpath(u"//ul[@class='view-info-list list-unstyled']/li/div[contains(text(),'语言')]/../span/text()").extract()
        item['package_name'] = sel.re("'send', 'event', 'Downloads', '\d+', '(.+)'\);\"")
        item['resolution'] = sel.xpath("//div[@class='view-header-middle']/div[@class='view-header-rating']/span[5]/text()").extract()
        item['score'] = sel.xpath('//meta[@itemprop="ratingValue"]/@content').extract()
        item['system'] = sel.xpath(u"//ul[@class='view-info-list list-unstyled']/li/div[contains(text(),'系统')]/../span/text()").extract()
        item['tag'] = sel.xpath("///div[@class='view-header-tags']/ul[@class='list-inline']/li/span[@class='btn btn-sm btn-default']/text()").extract()
        item['type'] = sel.xpath(u"//ul[@class='view-info-list list-unstyled']/li/div[contains(text(),'类型')]/../a/span/text()").extract()
        item['update'] = sel.xpath(u"//ul[@class='view-info-list list-unstyled']/li/div[contains(text(),'更新')]/../span/text()").extract()
        item['version'] = sel.xpath(u"//ul[@class='view-info-list list-unstyled']/li/div[contains(text(),'版本')]/../span/text()").extract()
        item['picture'] = sel.xpath("//div[@class='view-header-left']/img[@class='view-header-icon']/@src").extract()
        item['package_size'] = sel.xpath(u"//ul[@class='view-info-list list-unstyled']/li/div[contains(text(),'大小')]/../span/text()").extract()
        item['mark_distribution'] = sel.xpath("//div[@class='reviews-element']/div[@class='review-chart']//span[@class='review-chart-percentage']/text()").extract()
        item['mark_count'] = sel.re(u"（(\d+) 个评分）")
        yield item
        # return item
