from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from crawler.items import LinkItem
from scrapy.http import Request
import scrapy
from scrapy.http import FormRequest
from scrapy import log



class Spider(CrawlSpider):
    name = 'application5'
    start_urls = ['https://app5.com/']
    item_urls = []
    
   # urlpool = []

    # 'log' and 'pwd' are names of the username and password fields
    # depends on each website, you'll have to change those fields properly
    # one may use loginform lib https://github.com/scrapy/loginform to make it easier
    # when handling multiple credentials from multiple sites. 
    def parse(self, response):
        #return FormRequest.from_response(
         #   response,
          #  formdata={'username': 'scanner1', 'password': 'scanner1'},
           # callback=self.after_login
        #)
        return Request(url='https://app5.com',
                           callback=self.parse_page)

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
            return Request(url='https://app1.com/users/home.php',
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
        input_box =  hxs.select('//input').extract()
        print "Scraping the URL " + response.url
      #  for inputs in input_box:
       #     print "The input boxes with name " + inputs

        links = hxs.select('//a/@href').extract()
        input_box =  hxs.select('//input/@src').extract()
        
       # print "Scraping the URL " + response.url
        for inputs in input_box:
            print "The input boxes with src " + inputs
        print "\n"
   
        input_box =  hxs.select('//script/@src').extract()
        
       # print "Scraping the URL " + response.url
        for inputs in input_box:
            print "The script boxes with src " + inputs
        print "\n"
        # Yield a new request for each link we found
        # #this may lead to infinite crawling...
        ur1 = ""
        for link in links:
            if link.find("http") > -1:
                url = link 
            else:
                url  = "https://app5.com"+link 
                #else:
                 #   url  = "https://app3.com"+link  
            #if(link.find(":") != -1):
             #  continue 
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