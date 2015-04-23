from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from urlparse import urlparse
# from scrapy.contrib.spiders import CrawlSpider, Rule
# from scrapy.spider import Spider
from scrapy.spider import BaseSpider
from crawler.items import LinkItem
from scrapy.http import Request
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import scrapy
from scrapy.http import FormRequest
from scrapy import log
from loginform import fill_login_form
import json
#import injection
import urllib, urllib2
from BeautifulSoup import BeautifulSoup,SoupStrainer

class NewSpider(BaseSpider):
    name =  'app7.com'
    allowed_domains=[]#["app5.com"]
    start_urls = []#['https://app5.com/www/index.php']
    item_urls = []
    handle_httpstatus_list = [500]
    all_urls = []
    login_user = 'admin'
    login_pass = 'admin'
    json_objects = []
    patterns_in_exploits = {}
    appendurl = []
#    callback_function  = "after_login"

    """Stage 1 """   
    # 'log' and 'pwd' are names of the username and password fields
    # depends on each website, you'll have to change those fields properly
    # one may use loginform lib https://github.com/scrapy/loginform to make it easier
    # when handling multiple credentials from multiple sites.
    def parse(self, response):
      # args, url, method = fill_login_form(response.url, response.body, self.login_user, self.login_pass)
       #return FormRequest(url, method=method, formdata=args, dont_filter=True,callback=self.after_login)
       args, url, method, name , number = fill_login_form(response.url, response.body, self.login_user, self.login_pass)
       if name:
                yield FormRequest.from_response(response, method=method, formdata=args, formname=name,  dont_filter=True,callback=self.after_login)        
       else:
                yield FormRequest.from_response(response, method=method, formdata=args, formnumber=number,  dont_filter=True,callback=self.after_login)
    #   return FormRequest.from_response(
     #        response,            
      #       formdata={'lang' : 'English' ,'username': 'admin', 'password': 'admin'},
        #       method="POST",
       #        dont_filter=True,
        #     callback=self.after_login
         #)
    #    return [scrapy.FormRequest(self.start_urls[0], 
     #       formdata={'adminname': 'admin', 'Password': 'admin'},
      #       callback=self.after_login)]
       #   yield Request(url=self.start_urls[0], callback=self.parse_page)

    def __init__(self,filename = None):
        temp = []
        if filename:
            with open(filename, 'r') as f:
                temp = f.readlines()
        self.start_urls.append(temp[0].strip())
        self.allowed_domains.append(temp[1].strip())
        self.appendurl.append(temp[2].strip())

        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def after_login(self, response):
        # check login succeed before going on
       # print response.url
        print "This is response url " +  response.url
        if "The username/password combination you have entered is invalid" in response.body:
            self.log("Login failed", level=log.ERROR)
            return        
        # continue scraping with authenticated session...
        elif "logout" in response.body:
            print "This is response url " +  response.url
            self.log("Login succeed!", level=log.DEBUG)
            return Request(url=response.url,
                           callback=self.parse_page)
        else:
            print "Error1111"
            return Request(url=response.url,
                           callback=self.parse_page)
    def isURLinPool(self, url):

        for t  in self.item_urls:
            if (t.find("?") != -1):
                t = t[:t.find("?")]
            if (url.find("?") != -1):
                url = url[:url.find("?")]    
            if url.lower() == t.lower():
                return False
        if "logout" in url:
          return False        
        return True  

    def parse_HTML(self, url, htmlContent, urlGlobalList):
      """
        Parse the HTML/XHTML code to get POST/GET requests parameters
      """
      urlDict = dict()
      forms = SoupStrainer('form')
      input = SoupStrainer('input')

      listForm = [tag for tag in BeautifulSoup(htmlContent, parseOnlyThese=forms)]

      for f in listForm:
        method = 'GET'
        if 'method' in f or 'METHOD' in f:
          method = f['method'].upper()

        listInput = [tag for tag in BeautifulSoup(str(f), parseOnlyThese=input)]
        tmpurlDict = dict()
        tmpList = list()

      for i in listInput:
        tmpDict = dict()
        tmpDict['type'] = method

        try:
           value = i['value']
        except KeyError:
          value = '-1'
        try:
          name = i['name']
        except KeyError:
          name = 'name'
          value= 'value'
          continue

      tmpDict['param'] = str(name)
      tmpDict['value'] = str(value)

      tmpList.append(tmpDict)

      tmpurlDict['url'] = url
      tmpurlDict['injection'] = tmpList
      urlGlobalList.append(tmpurlDict)

      return urlGlobalList              

    # example of crawling all other urls in the site with the same
    # authenticated session.


    def get_html_content(url, value):
      """
        Fetch HTML content
        url - Clean URL without any parameters
        value - parameters
      """
      data = urllib.urlencode(value)

      # Submit the form
      req = urllib2.Request(url, data)
      rsp = urllib2.urlopen(req)
  
      return rsp.read()

    def parse_page(self, response):
        """ Scrape useful stuff from page, and spawn new requests
        """
       # hxs = HtmlXPathSelector(response)
        d = {"url" : response.url}
  #      print response.body
        url = response.url
        if (url.find("?") > -1):
          url = url[:url.find("?")]        
        djs = {"url" :url, "method" : "GET"}
        hxs = HtmlXPathSelector(response)
        # i = CrawlerItem()
        # find all the link in the <a href> tag
        input_box =  hxs.select('//input/@name').extract()
        print "Scraping the URL " + response.url
   
        d1 = urlparse(response.url)
      
        query = d1.query
        a1 = query.split("&")
        params = {}
   
        j = 0
        params = {}
        for s in a1:
            stem = s
            stem1 = stem.split("=")
 #           params.append(stem1[0])
            #print "the list  " 
            #rint stem1
           # params["Param" + str(j)] =  stem1[0]
            if len(stem1) ==2: 
              params[stem1[0]] =  stem1[1]
            elif len(stem1) == 1 :#and len(stem1[0]):
                params[stem1[0]] =  ""
          #  params{stem1[0]: stem1[1]}
            j = j+1
        
        no_insert = 1 
        if len(params) > 0 and params.keys()[0] != "": 
          djs["params"] = params
          no_insert =0
        

         
        if no_insert:
          params = {}
          djs["params"] = params
        #print "Json Data"
      #  d111 = json.dumps(djs)
        #print d111  
        self.json_objects.append(djs)
      

      #  for inputs in input_box:
       #s     print "The input boxes with name " + inputs


        
        
#        htmlContent = self.get_html_content(response.url)
       # url = response.url
        #if (url.find("?")):
        #  url = url[:url.find("?")]
       # urlGlobalList = []
        #urlGlobalList = self.parse_HTML(url, response.body, urlGlobalList)

     #   print "The Link is " + response.url
   #     print htmlContent

        #print "A break"
        #print urlGlobalList
        links = hxs.select('//a/@href').extract()
        input_box =  hxs.select('//input/@src').extract()

        links1 = hxs.select('//script/@src').extract()
        input_box =  hxs.select('//script/@src').extract()

        for sc2 in input_box:
          base = response.url
          k = base.rfind("/")
          sc2l = base[:k] + "/" + sc2
          self.all_urls.append(sc2l)
        
       # print "Scraping the URL " + response.url
    #    for inputs in input_box:
  #          print "The input boxes with src " + inputs
   #     print "\n"
      
        links2 = hxs.select('//a/@href').extract()
        
        sites = hxs.select('//li//a/@href').extract()
      #  links3 = hxs.select('//li//a/@href').extract()
        links = links1 + links2 + sites
        self.all_urls = self.all_urls + links
       # links = links + sites

#        for inputs in links:
 #           print "The input boxes with links " + inputs
  #      print "\n"      
        # Yield a new request for each link we found
        # this may lead to infinite crawling...
        i = 0
        l ={}
        for link in self.all_urls:
         #   if(link.find(":") != -1):
          #     continue 
            if link.find("http") > -1:
                link = link
            else:
                link = self.appendurl[0]+link
            l["link" + str(i)] =  link
            i = i+1
            if(self.isURLinPool(link)):
               if link.find("http") > -1:
                    yield Request(url=link, callback=self.parse_page)
               else:
                    yield Request(url=self.appendurl[0]+link, callback=self.parse_page)
        d['URLS'] = l    
     #   print d        
        self.item_urls.append(response.url)        

        item = LinkItem()
       # item["title"] = hxs.select('//title/text()').extract()[0]
        #item["url"] = response.url
       # yield self.collect_item(item)

    def collect_item(self, item):
        return item      

    def spider_closed(self, spider):
       # for s in self.json_objects:
        #  print s
#       all_json_objects = {}
 #      all_json_objects["injections"] =  self.json_objects
       f = open("json_objects1.json", 'w')
 #      jsonString = json.dumps(jsonObj)
       f.write(json.dumps(self.json_objects,indent= 4, sort_keys = True))
       f.close()
  #     self.callback_function =  """payload_generation("Stage2.json")"""
    #   self.parse()
   #    self.parse1(url = self.start_urls[0])  
       self.payload_generation("Stage21.json")
#       self.Stage2Starts

    def load_potential_payloads(self):
      potential_payloads = []
      f = open('exploits.json').read()
      potential_payloads = json.loads(f)
 #     f.close()
      return potential_payloads  

    def load_injection_points(self):
      injection_points = []
      f = open('json_objects1.json').read()
      print f
      injection_points = json.loads(f)
      print injection_points
#      f.close()
      return injection_points  


    def payload_generation(self,file):
      potential_payloads = self.load_potential_payloads()
      injection_points = self.load_injection_points()

      pot_exploits = []

      for pot_pay in potential_payloads:

        for inject_point in injection_points :

          url = inject_point["url"]
          method = inject_point["method"]
          params = inject_point["params"]

          for param_key, param_value in params.iteritems():
            exploit = {}
            exploit.update({"url":url})
            exploit.update({"method":method})
            paramsData = []
            for p_k, p_v in params.iteritems():
              data = {}
              data.update({"key":p_k})
              if p_k==param_key:
                data.update({"value":pot_pay})
              else:
                data.update({"value":p_v})
              paramsData.insert(0, data)
            exploit.update({"params":paramsData})
            pot_exploits.insert(0, exploit)

      self.generate_payload_json(file, pot_exploits)

    def generate_payload_json(self,file, exploits):
      jsonObj = {}
      jsonObj["exploits"] = exploits
      f = open(file, 'w')
      jsonString = json.dumps(jsonObj,indent= 4, sort_keys = True)
      f.write(jsonString)  
      f.close()





