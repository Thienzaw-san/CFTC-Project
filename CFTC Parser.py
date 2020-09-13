import urllib.request
import urllib.parse
import csv
import re

# function to remove all html tags
def clean_html(raw_html):
    remove_tag = re.compile('<.*?>')
    clear_data = re.sub(remove_tag, '', raw_html)
    return clear_data

url = "https://www.cftc.gov/dea/futures/financial_" \
      "lf.htm?fbclid=IwAR1z7hGNDOegCiOEhbBDo97lrK" \
      "tM9gsqRB3loRBa3lmM-q_ELpzYbJGM-00"

request = urllib.request.Request(url)
data = urllib.request.urlopen(request)
cftc_data = data.read().decode('utf-8')
clean_cftc_data = clean_html(cftc_data)

search_data = [x for x in re.findall(r'[-].*\(.*\)|'  # regex pattern to search and retrieve data
                                     r'CFTC Code #\S+\s*\b'
                                     r'|Total Traders:\s*\S+'
                                     r'|Open Interest is\s*\S+'
                                     r'|["].*["]'
                                     r'|Futures Only Positions as of.*?\d{4}'
                                     r'|Updated.*?\d{4}|pageTracker\._trackPageview\(\)'
                                     r'|.*\(Futures Only\)'
                                     r'|_gat\._|Total Change is:\s*\S+'
                                     r'|Changes from:.*?\d{4}\b'
                                     r'|(.*(?=[-] .*\()|[-+]?\d+(?:[,.]\d+)?(?:[,.]\d+)?|[.])', clean_cftc_data) if x]

list_index = [0,1,2,3,15,16,17,29,30,31,43,44,45] # index reference to get needed data on search data list
parsed_data = [] # empty list to hold data to be parsed in search_data list

for idx, val in enumerate(search_data):  # loop to retrieve needed data in search_data list
    if idx in list_index:
        parsed_data.insert(idx,val)
        if idx == list_index[12]:
            list_index = [x + 55 for x in list_index]

print(clean_data)


