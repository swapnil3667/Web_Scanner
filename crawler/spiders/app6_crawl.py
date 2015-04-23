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

class NewSpider(BaseSpider):
    name =  'app6.com'
    allowed_domains=["app6.com"]
    start_urls = ['https://app6.com/zimplit.php?action=login']
    item_urls = []
    login_user = 'admin'
    login_pass = 'admin'

    # 'log' and 'pwd' are names of the username and password fields
    # depends on each website, you'll have to change those fields properly
    # one may use loginform lib https://github.com/scrapy/loginform to make it easier
    # when handling multiple credentials from multiple sites.
    def parse(self, response):
    #    args, url, method = fill_login_form(response.url, response.body, self.login_user, self.login_pass)
     #   return FormRequest(url, method="POST", formdata=args, callback=self.after_login)
        return FormRequest.from_response(
             response,            
             formdata={'lang' : 'English' ,'username': 'admin', 'password': 'admin'},
               method="POST",
             callback=self.after_login
         )
        #return [scrapy.FormRequest(self.start_urls[0], 
         #   formdata={'Username': 'admin', 'Password': 'admin'},
          #   callback=self.after_login)]

    def after_login(self, response):
        # check login succeed before going on
        #print response.body
        if "The username/password combination you have entered is invalid" in response.body:
            self.log("Login failed", level=log.ERROR)
            return        
        # continue scraping with authenticated session...
        elif "Logout" in response.body:
            self.log("Login succeed!", level=log.DEBUG)
            return Request(url="https://app6.com/zimplit.php",
                           callback=self.parse_page)
        else:
            print "Error1111"
            return Request(url="https://app6.com/zimplit.php",
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

    # example of crawling all other urls in the site with the same
    # authenticated session.
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

        links = hxs.select('//a/@href').extract()

        # Yield a new request for each link we found
        # this may lead to infinite crawling...

        for link in links:
            if(link.find(":") != -1):
               continue 
            if link.find("http") > -1:
                link = link
            else:
                link = "https://app6.com"+link

            if(self.isURLinPool(link)):
               print "THIS IS A LINK " + link
#              yield Request(url= "https://app1.com"+link, callback=self.parse_page)
               

            #only process external/full link
               if link.find("http") > -1:
                    yield Request(url=link, callback=self.parse_page)
               else:
                    yield Request(url="https://app6.com"+link, callback=self.parse_page)
        self.item_urls.append(response.url)        
   #     for link in links:
    #        print "THIS IS A LINK" + link
            #only process external/full link
     #       if link.find("http") > -1:
      #          yield Request(url=link, callback=self.parse_page)
       #     else:
        #        yield Request(url="https://app1.com"+link, callback=self.parse_page)
        item = LinkItem()
       # item["title"] = hxs.select('//title/text()').extract()[0]
        #item["url"] = response.url
       # yield self.collect_item(item)

    def collect_item(self, item):
        return item