from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from crawler.items import LinkItem
from scrapy.http import Request
import scrapy
from scrapy.http import FormRequest
from scrapy import log
from loginform import fill_login_form
from scrapy.http.cookies import CookieJar


class ExampleSpider(CrawlSpider):
    name = 'example2.com'
    start_urls = ['https://app1.com/users/login.php','https://app1.com/users/home.php']
    item_urls = []
    login_user = "scanner1"
    login_pass = "scanner1"
   # urlpool = []

    # 'log' and 'pwd' are names of the username and password fields
    # depends on each website, you'll have to change those fields properly
    # one may use loginform lib https://github.com/scrapy/loginform to make it easier
    # when handling multiple credentials from multiple sites. 
    rules = (
      Rule(SgmlLinkExtractor(allow=r'-\w+.html$'),
             callback='parse_page', follow=True),
    )
    def parse(self, response):
        args, url, method = fill_login_form(response.url, response.body, self.login_user, self.login_pass)
        return FormRequest(url, method=method, formdata=args, callback=self.after_login)

    #def start_requests(self):
     #   return [scrapy.FormRequest(self.start_urls[0], 
      #      formdata={'username': 'swapnil', 'password': '123'},
       #      callback=self.after_login)]

    def after_login(self, response):
        # check login succeed before going on
        if "The username/password combination you have entered is invalid" in response.body:
            self.log("Login failed", level=log.ERROR)
            return

        # continue scraping with authenticated session...
        else:
            self.log("Login succeed!", level=log.DEBUG)
            print "Logging in"
            print  "asdsdsd  " + response.url
      #      cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
       #     cookieJar.extract_cookies(response, response.request)
            yield Request(url="https://app1.com",
                          # meta={'cookiejar': response.meta['cookiejar']},
        #                  meta = {'dont_merge_cookies': False, 'cookie_jar': cookieJar},
                          callback=self.parse_page)


    # example of crawling all other urls in the site with the same
    # authenticated session.
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
               if link.find("http") > -1:
                  print "Before Sending it for parse " + link
                  yield Request(url=link, callback=self.parse_page)
        self.item_urls.append(response.url)        
        item = LinkItem()
        item["title"] = hxs.select('//title/text()').extract()[0]
        item["url"] = response.url
    #    self.item_urls["title"] = hxs.select('//title/text()').extract()[0]
     #   self.item_urls["url"] = response.url
        yield self.collect_item(item)

    def collect_item(self, item):
        return item