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
    name =  'nologin_stage12'
    allowed_domains=[]#["app5.com"]
    start_urls = []#['https://app5.com/www/index.php']
    item_urls = []
    all_urls = []
    login_user = 'admin'
    login_pass = 'admin'
    json_objects = []
    patterns_in_exploits = {}
    appendurl =[]
    excludelist = ['password', 'username', 'login', 'submit']
#    callback_function  = "after_login"

    """Stage 1 """   
    # 'log' and 'pwd' are names of the username and password fields
    # depends on each website, you'll have to change those fields properly
    # one may use loginform lib https://github.com/scrapy/loginform to make it easier
    # when handling multiple credentials from multiple sites.
    def parse(self, response):
          yield Request(url=self.start_urls[0], callback=self.parse_page)

    def __init__(self,filename = None):
        temp = []
        if filename:
            with open(filename, 'r') as f:
                temp = f.readlines()
        self.start_urls.append(temp[0].strip())
        self.allowed_domains.append(temp[1].strip())
        self.appendurl.append(temp[2].strip())
        credentials = list()
        tmpparam = dict()
        tmpparam["url"] =  self.start_urls[0]
        tmpparam["userid"] = ""
        tmpparam["passwordid"] = ""
        tmpparam["login"] = "False" 

        credentials.append(tmpparam)
        f = open("json/credentials.json", 'w')
        f.write(json.dumps(credentials,indent= 4, sort_keys = True))
        f.close()        

        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def isURLinPool(self, url):

        for t  in self.item_urls:
            if (t.find("?") != -1):
                t = t[:t.find("?")]
            if (url.find("?") != -1):
                url = url[:url.find("?")]    
            if url.lower() == t.lower():
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

    def dict_add(self,d1,d2):
      """
        Flatten 2 dictionaries
      """
      d={}
      if len(d1):
        for s in d1.keys():
          d[s] = d1[s]
      if len(d2):
        for s in d2.keys():
          d[s] = d2[s]
      return d


    def parse_HTML(self, url, htmlContent):
      """
        Parse the HTML/XHTML code to get POST/GET requests parameters
      """
      urlGlobalList = list()
      forms = SoupStrainer('form')
      input = SoupStrainer('input')
      input1 = SoupStrainer('select') 

      listForm = [tag for tag in BeautifulSoup(htmlContent, parseOnlyThese=forms)]

      for f in listForm:
        methodVal = 'GET'
        if (f.has_key('method') or f.has_key('method')):
          methodVal = f['method'].upper()

        if (methodVal == 'POST'):
          listInput = [tag for tag in BeautifulSoup(str(f), parseOnlyThese=input)]
          listInput1 = [tag for tag in BeautifulSoup(str(f), parseOnlyThese=input1)]
          listInput = listInput + listInput1
          tmpUrlDict = dict() 
          tmpDict = dict()    
          for i in listInput:
            try:
              value = i['value']
            except KeyError:
              value = ''
            try:
              name = i['name']
            except KeyError:
              name = '-1'
              value= ''
              continue

            name = str(name)
            value = str(value)
            excludeflag = False
            for keyword in self.excludelist:
              if (keyword in name.lower()):
                excludeflag = True
                break            
                
            if (not excludeflag):
              if (name != '-1'):
                tmpUrlDict['url'] = url
                tmpUrlDict['method'] = methodVal
                tmpDict = self.dict_add(tmpDict, {name : value})
                tmpUrlDict['params'] = tmpDict

          if (bool(tmpUrlDict)):
            urlGlobalList.append(tmpUrlDict)

      return urlGlobalList           



    def parse_page(self, response):
        """ Scrape useful stuff from page, and spawn new requests
        """
       # hxs = HtmlXPathSelector(response)
        d = {"url" : response.url}
 #       print response.body
        url = response.url
        if (url.find("?") > -1):
          url = url[:url.find("?")]        
        djs = {"url" :url, "method" : "GET"}
        hxs = HtmlXPathSelector(response)
        # i = CrawlerItem()
        # find all the link in the <a href> tag
        input_box_name =  hxs.select('//input/@name').extract()
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
            if len(stem1) ==2: 
              params[stem1[0]] =  stem1[1]
            elif len(stem1) == 1 :#and len(stem1[0]):
                params[stem1[0]] =  ""
          #  params{stem1[0]: stem1[1]}
            j = j+1
        
        for inp in input_box_name:
          excludeflag = False
          for keyword in self.excludelist:
            if (keyword in inp.lower()):
              excludeflag = True
              break
          if (not excludeflag):
             params[inp] = ""

        print params  
        no_insert = 1 
        if len(params) > 0 and params.keys()[0] != "": 
          print "Enterr"
          djs["params"] = params
          no_insert =0
        

         
        if no_insert:
         # params = {}
          params["file"] = ""
          djs["params"] = params
        #print "Json Data"
      #  d111 = json.dumps(djs)
        #print d111  
        self.json_objects.append(djs)

        urlGlobalList = []
        urlGlobalList = self.parse_HTML(url, response.body)
        if len(urlGlobalList) > 0:
           self.json_objects = self.json_objects + urlGlobalList        
      

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

      #  for inputs in links:
       #     print "The input boxes with links " + inputs
        #print "\n"      
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
      inj_points = []
      for inj in self.json_objects:
        params = inj["params"]
        p1 = {}
        for p_k, p_v in params.iteritems():
          if not (p_k == ""):
            p1[p_k] = p_v
        inj["params"] = p1
        inj_points.insert(0, inj)

      f = open("json/Stage1_json_objects.json", 'w')
#      jsonString = json.dumps(jsonObj)
      f.write(json.dumps(inj_points,indent= 4, sort_keys = True))
      f.close()
      self.stage2_exploit_generation("json/Stage1_json_objects.json","json/exploitsUdt.json","json/Stage2_json_objects.json")  
  

    def stage2_exploit_generation(self,stage1_injection_file, stage2_in_exploitsFile, stage2_Out_JsonFile):

      injection_points = []
      f1 = open(stage1_injection_file, 'r').read()
      injection_points = json.loads(f1)

      exploit_payloads = []
      f2 = open(stage2_in_exploitsFile, 'r').read()
      exploit_payloads = json.loads(f2)

      pot_exploits = []
      '''
      for pot_pay in exploit_payloads:

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
        '''
      for pot_pay in exploit_payloads:

        for inject_point in injection_points :

          url = inject_point["url"]
          method = inject_point["method"]
          params = inject_point["params"]

          params_novalue = []
          params_value_dict = {}

          for param_k, param_v in params.iteritems():
            if param_v == '':
              params_novalue.insert(0, param_k)
            else:
              params_value_dict[param_k]=param_v
              print param_k
              

          if len(params_value_dict.keys()) > 0:
            for p_k, p_v in params.iteritems():
              exploit = {}
              exploit.update({"url":url})
              exploit.update({"method":method})
              newparams = []
              for p in params_value_dict.keys():
                s_pm = {}
                s_pm["key"]=p
                if p==p_k:
                  s_pm["value"]=pot_pay
                else:
                  s_pm["value"]=params[p]
                newparams.insert(0, s_pm)
              for pp_k in params_novalue:
                s_pm = {}
                s_pm["key"]=pp_k
                s_pm["value"]=pot_pay
                newparams.insert(0, s_pm)
              exploit.update({"params":newparams})
              pot_exploits.insert(0, exploit)
          else:
            exploit = {}
            exploit.update({"url":url})
            exploit.update({"method":method})
            newparams = []
            for pp_k in params_novalue:
              s_pm = {}
              s_pm["key"]=pp_k
              s_pm["value"]=pot_pay
              newparams.insert(0, s_pm)
            exploit.update({"params":newparams})
            pot_exploits.insert(0, exploit)
      jsonObj = {}
      jsonObj["exploits"] = pot_exploits
      f = open(stage2_Out_JsonFile, 'w')
      jsonString = json.dumps(jsonObj, indent=4, sort_keys=True)
      f.write(jsonString)
      f.close()