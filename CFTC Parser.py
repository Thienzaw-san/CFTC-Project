import urllib.request
import urllib.parse
import re


def clean_html(raw_html):  # function to remove all html tags
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

parsed_data = [x for x in re.findall(r'_gat\._'     # capture needed data
                                     r'|\(Futures Only\)'
                                     r'|\("UA-21047137-1"\)'
                                     r'|pageTracker\._trackPageview\(\)'
                                     r'|\(MINI\)'
                                     r'|pageTracker\.'
                                     r'|Updated.*?\d{4}|'
                                     r'Futures Only Positions as of.*?\d{4}'
                                     r'|Open Interest is\s*\S+|["].*["]'
                                     r'|Total Change is:\s*\S+|Total Traders:\s*\S+'
                                     r'|CFTC.*?\d+\b'
                                     r'|Changes from:.*?\d{4}\b'
                                     r'|(\(.*\)|[-+]?\d+(?:[,]\d+)?|[.])', clean_cftc_data) if x]

print(parsed_data)
