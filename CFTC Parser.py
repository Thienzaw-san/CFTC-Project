import urllib.request
import urllib.parse
import json
import pandas as pd
import re
import os
from utils import func_name, timeit


class HtmlCleaner:  # removes tags from the URL content

    def __init__(self, raw_html):
        self.raw_html = raw_html

    def clean_html(self):
        remove_tag = re.compile('<.*?>')
        clear_data = re.sub(remove_tag, '', self.raw_html)
        return clear_data


class Parser:   # parses the data

    search_pattern = r'[-].*\(.*\)|CFTC Code #\S+\s*\b|Total Traders:\s*\S+|Open Interest is\s*\S+|["].*["]' \
                     r'|Futures Only Positions as of.*?\d{4}|pageTracker\._trackPageview\(\)' \
                     r'|.*\(Futures Only\)|_gat\._|Total Change is:\s*\S+|Changes from:.*?\d{4}\b' \
                     r'|((?<=Updated ).*?\d{4}|.*(?=\s[-] .*\()|[-+]?\d+(?:[,.]\d+)?(?:[,.]\d+)?|[.])'

    def __init__(self, html_data):
        self.html_data = html_data
        self.data = self.main_parser()
        self.date = self.date_parser()

    def main_parser(self):  # retrieves all the necessary data
        main_data = [x for x in re.findall(self.search_pattern, self.html_data) if x]
        return main_data

    def long_short_spreading_parser(self, reference):  # retrieves long, short & spreading values from the main parser
        lookup = reference
        long_short_spreading_data = []
        for index, value in enumerate(self.data):
            if index == lookup:
                long_short_spreading_data.append(value)
                lookup += 55
        return long_short_spreading_data

    def currency_parser(self):  # retrieves currency from the main parser
        currencies = self.data[:-1][0::55]
        return currencies

    def date_parser(self):  # retrieves date from the main parser
        date = self.data[len(self.data) - 1]
        match = re.match(r'([a-zA-Z]+) (\d+), (\d{4})', date)
        month = match.group(1)
        day = match.group(2)
        year = match.group(3)
        month_list = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']

        for index, value in enumerate(month_list):
            if value in month:
                return str(index + 1) + '-' + day + '-' + year


class DictionaryWriter:

    def __init__(self, data):
        self.parser = Parser(data)

    def dictionary_converter(self):  # converts data into dictionary

        outer_key_list = ['Long', 'Short', 'Spreading']
        inner_key_list = ['Position', 'Changes', 'Percent', 'Number of Traders']
        currency_key_list = self.parser.currency_parser()

        dct = {x: [{'Dealer Intermediary': {y: {z: None for z in inner_key_list}
                                           for y in outer_key_list}}] for x in currency_key_list}

        # insert LONG position, changes, percent, number of trader
        for currency_key, long_data in zip(currency_key_list, self.parser.long_short_spreading_parser(1)):
            dct[currency_key][0]['Dealer Intermediary']['Long']['Position'] = long_data
        for currency_key, long_data in zip(currency_key_list, self.parser.long_short_spreading_parser(15)):
            dct[currency_key][0]['Dealer Intermediary']['Long']['Changes'] = long_data
        for currency_key, long_data in zip(currency_key_list, self.parser.long_short_spreading_parser(29)):
            dct[currency_key][0]['Dealer Intermediary']['Long']['Percent'] = long_data
        for currency_key, long_data in zip(currency_key_list, self.parser.long_short_spreading_parser(43)):
            dct[currency_key][0]['Dealer Intermediary']['Long']['Number of Traders'] = long_data

        # insert Short position, changes, percent, number of trader
        for currency_key, short_data in zip(currency_key_list, self.parser.long_short_spreading_parser(2)):
            dct[currency_key][0]['Dealer Intermediary']['Short']['Position'] = short_data
        for currency_key, short_data in zip(currency_key_list, self.parser.long_short_spreading_parser(16)):
            dct[currency_key][0]['Dealer Intermediary']['Short']['Changes'] = short_data
        for currency_key, short_data in zip(currency_key_list, self.parser.long_short_spreading_parser(30)):
            dct[currency_key][0]['Dealer Intermediary']['Short']['Percent'] = short_data
        for currency_key, short_data in zip(currency_key_list, self.parser.long_short_spreading_parser(44)):
            dct[currency_key][0]['Dealer Intermediary']['Short']['Number of Traders'] = short_data

        # insert Spreading position, changes, percent, number of trader
        for currency_key, spreading_data in zip(currency_key_list, self.parser.long_short_spreading_parser(3)):
            dct[currency_key][0]['Dealer Intermediary']['Spreading']['Position'] = spreading_data
        for currency_key, spreading_data in zip(currency_key_list, self.parser.long_short_spreading_parser(17)):
            dct[currency_key][0]['Dealer Intermediary']['Spreading']['Changes'] = spreading_data
        for currency_key, spreading_data in zip(currency_key_list, self.parser.long_short_spreading_parser(31)):
            dct[currency_key][0]['Dealer Intermediary']['Spreading']['Percent'] = spreading_data
        for currency_key, spreading_data in zip(currency_key_list, self.parser.long_short_spreading_parser(45)):
            dct[currency_key][0]['Dealer Intermediary']['Spreading']['Number of Traders'] = spreading_data

        return {'report date': self.parser.date_parser(), 'financial report': dct}


class Writer:

    def __init__(self, html_data, dictionary_data, date):
        self.html_data = html_data
        self.dictionary_data = dictionary_data
        self.date = date

    def text_writer(self):  # saves the raw file
        file_date = self.date
        raw_html_data = self.html_data
        f = open(file_date + ".cot.futures.txt", "w")
        f.write(raw_html_data)
        f.close()

    def json_writer(self):  # converts dictionary to JSON and save as JSON
        file_date = self.date
        with open(file_date + '.cot.futures.json', 'w') as dictionary_data:
            json.dump(self.dictionary_data, dictionary_data, indent = 4)


class JsonToCsvConverter:

    def __init__(self, json_data, date):
        self.json_data = json_data
        self.date = date

    def csv_converter(self):  # converts JSON to CSV
        currency_list = self.json_data['financial report'].keys()
        with open(self.date + '.cot.futures.json', encoding='utf-8-sig') as json_file:
            data = json.load(json_file)
            main_frame = pd.DataFrame()
            for currency in currency_list:
                json_data = pd.json_normalize(data, meta=['report date'], record_path=['financial report', currency])
                main_frame = main_frame.append(json_data)
            main_frame.insert(0, 'Currency', currency_list)
            main_frame.to_csv(self.date + '.cot.futures.csv', encoding='utf-8', index=False)


def html_content_retriever():  # retrieves html data
    request = urllib.request.Request("https://www.cftc.gov/dea/futures/financial_lf.htm")
    url_data = urllib.request.urlopen(request)
    cftc_data = url_data.read().decode('utf-8')
    cleaner = HtmlCleaner(cftc_data)
    return cleaner.clean_html()


@timeit
def main():

    output_dir = "output"

    os.makedirs(output_dir, exist_ok = True)
    os.chdir(output_dir)

    html_data = html_content_retriever()
    parser = Parser(html_data)
    dct_writer = DictionaryWriter(html_data)
    dct_data = dct_writer.dictionary_converter()

    file_writer = Writer(html_data, dct_data, parser.date)
    file_writer.text_writer()
    file_writer.json_writer()

    csv_writer = JsonToCsvConverter(dct_data, parser.date)
    csv_writer.csv_converter()


if __name__ == "__main__":
    main()
