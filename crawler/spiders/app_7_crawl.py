from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders.init import InitSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from crawler.items import LinkItem
from scrapy.http import Request
import scrapy
from scrapy.http import FormRequest
from scrapy import log
from scrapy.http.cookies import CookieJar


class LinkedPySpider(CrawlSpider):
    name = 'LinkedPy'
   # allowed_domains = ['linkedin.com']
   # login_page = 'https://www.linkedin.com/uas/login'
   # start_urls = ["http://www.linkedin.com/csearch/results"]
    #login_page = 'https://app1.com/users/login.php'
   # start_urls = ['https://app1.com/users/home.php']
    login_page = 'https://app7.com/oc-admin/index.php?page=login'
    start_urls = ['https://app7.com/oc-admin/']
    item_urls = []

    #def start_requests(self):
    #"""This function is called before crawling starts."""
        # return Request(url=self.login_page, callback=self.login)
     #    return [Request(url='https://app1.com/users/login.php', callback=self.login)]
    def start_requests(self):
        yield Request(
            url=self.login_page,
            callback=self.login
        )
       

    def login(self, response):
    #"""Generate a login request."""
         return FormRequest.from_response(response,
                formdata={'user': 'admin', 'password': 'admin'},
   #             meta={'cookiejar': 1},
                callback=self.check_login_response)

    def login1(self, response):
    #"""Generate a login request."""
         return FormRequest.from_response(response,
                formdata={'username': 'swapnil', 'password': '123'},
   #             meta={'cookiejar': 1},
                callback=self.parse_page)     

    def check_login_response(self, response):
        # check login succeed before going on
        if "ERROR: Invalid username" in response.body:
            self.log("Login failed", level=log.ERROR)
            return

        # continue scraping with authenticated session...
        else:
            self.log("Login succeed!", level=log.DEBUG)
            print "Logging in"
            print  "asdsdsd  " + response.url
            print response.request.headers.get('method')
            cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
            cookieJar.extract_cookies(response, response.request)
            return Request(url='https://app7.com/oc-admin/',
                           #meta={'cookiejar': response.meta['cookiejar']},
                       #    meta = {'dont_merge_cookies': False, 'cookie_jar': cookieJar},
                          # cookie= response.cookie,
                           callback=self.parse_page)

    def isURLinPool(self, url):

        for t  in self.item_urls:
            if (t.find("?") != -1):
                t = t[:t.find("?")]
            if (url.find("?") != -1):
                url = url[:url.find("?")]    
            if url.lower() == t.lower():
                return False
        return True

    def parse_page(self, response):
        """ Scrape useful stuff from page, and spawn new requests
        """
        hxs = HtmlXPathSelector(response)
        # i = CrawlerItem()
        # find all the link in the <a href> tag
        input_box =  hxs.select('//input/@name').extract()
        print "Scraping the URL " + response.url
        for inputs in input_box:
            print "The input boxes with name " + inputs

        links = hxs.select('//a/@href').extract()
        input_box =  hxs.select('//input/@src').extract()
        
       # print "Scraping the URL " + response.url
        for inputs in input_box:
            print "The input boxes with src " + inputs
        print "\n"

        # Yield a new request for each link we found
        # #this may lead to infinite crawling...
        ur1 = ""
        for link in links:
            url  = "https://app1.com"+link
            if(link.find(":") != -1):
               continue 
            if(self.isURLinPool(url)):
               print "THIS IS A LINK " + link
#              yield Request(url= "https://app1.com"+link, callback=self.parse_page)
               

            #only process external/full link
               link = url
               ur1 = link
               cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
               cookieJar.extract_cookies(response, response.request)
               if link.find("http") > -1:
                  print "Before Sending it for parse " + link
                 # yield Request(url=link, meta = {'dont_merge_cookies': True, 'cookie_jar': cookieJar}, callback=self.parse_page)
                  yield Request(
                       url=link,
                     #  headers={'Referer':link},
                       callback=self.parse_page
                  )  
        self.item_urls.append(response.url)        
        item = LinkItem()
        item["title"] = hxs.select('//title/text()').extract()[0]
        item["url"] = response.url
    #    self.item_urls["title"] = hxs.select('//title/text()').extract()[0]
     #   self.item_urls["url"] = response.url
        yield self.collect_item(item)

    def collect_item(self, item):
        return item
