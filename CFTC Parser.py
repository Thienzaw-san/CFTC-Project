import urllib.request
import urllib.parse
import pandas as pd
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

# regex pattern to search and retrieve data from url
search_data = [x for x in re.findall(r'[-].*\(.*\)|'  
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

# index reference to get needed data on search_data list
index_reference = [0, 1, 2, 3, 15, 16, 17, 29, 30, 31, 43, 44, 45]

# list to hold needed data from search_data list
parsed_data = []
sub_list = []

# loop to retrieve needed data in search_data list
for idx, val in enumerate(search_data):
    if idx in index_reference:
        sub_list.append(val)
        if idx == index_reference[12]:
            index_reference = [x + 55 for x in index_reference]
            parsed_data.append(sub_list)
            sub_list = []

# convert list to DataFrame
cftc_df = pd.DataFrame(parsed_data, columns=['Currency', 'Position Long', 'Position Short', 'Position Spreading',
                                             'Change Long', 'Change Short', 'Change Spreading',
                                             '% Long', '% Short', '%Spreading',
                                             'No. of Trader Long', 'No. of Trader Short', 'No. of Trader Spreading'])

# save to csv
cftc_df.to_csv('CFTC Data.csv', mode='a', index=None)
