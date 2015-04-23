from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
# from scrapy.contrib.spiders import CrawlSpider, Rule
# from scrapy.spider import Spider
from scrapy.spider import BaseSpider
from crawler.items import LinkItem
from scrapy.http import Request
import scrapy
from scrapy.http import FormRequest
from scrapy import log
from loginform import fill_login_form

class ExampleSpider(BaseSpider):
    name =  'app1.com'
    allowed_domains=["app1.com"]
    start_urls = ['https://app1.com/users/login.php']
    login_user = 'scanner1'
    login_pass = 'scanner1'

    # 'log' and 'pwd' are names of the username and password fields
    # depends on each website, you'll have to change those fields properly
    # one may use loginform lib https://github.com/scrapy/loginform to make it easier
    # when handling multiple credentials from multiple sites.
    def parse(self, response):
        args, url, method = fill_login_form(response.url, response.body, self.login_user, self.login_pass)
        return FormRequest(url, method=method, formdata=args, callback=self.after_login)
        # return FormRequest.from_response(
        #     response,            
        #     formdata={'username': 'scanner1', 'password': 'scanner1'},
        #     callback=self.after_login
        # )

    def after_login(self, response):
        # check login succeed before going on
        print response.body
        if "The username/password combination you have entered is invalid" in response.body:
            self.log("Login failed", level=log.ERROR)
            return        
        # continue scraping with authenticated session...
        elif "Logout" in response.body:
            self.log("Login succeed!", level=log.DEBUG)
            return Request(url="https://app1.com/pictures/recent.php",
                           callback=self.parse_page)
        else:
            print "Error1111"


    # example of crawling all other urls in the site with the same
    # authenticated session.
    def parse_page(self, response):
        """ Scrape useful stuff from page, and spawn new requests
        """
        hxs = HtmlXPathSelector(response)
        # i = CrawlerItem()
        # find all the link in the <a href> tag
        links = hxs.select('//a/@href').extract()

        # Yield a new request for each link we found
        # this may lead to infinite crawling...
        for link in links:
            print "THIS IS A LINK" + link
            #only process external/full link
            if link.find("http") > -1:
                yield Request(url=link, callback=self.parse_page)
            else:
                yield Request(url="https://app1.com"+link, callback=self.parse_page)
        item = LinkItem()
        item["title"] = hxs.select('//title/text()').extract()[0]
        item["url"] = response.url
        yield self.collect_item(item)

    def collect_item(self, item):
        return item