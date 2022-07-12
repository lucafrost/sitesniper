# imports & dependencies
from platform import release
import pandas as pd
import requests
from wasabi import msg
import regex as re
from urllib.parse import urlparse
import tldextract
import spacy

# get list of current TLDs from IANA / ICANN
def fetch(list=True, df=False, csv=False, csv_path=None):
    """
    Fetch TLDs from IANA / ICANN
    :param list: (default: True) return list of TLDs
    :param df: (default: False) return dataframe of TLDs
    :param csv: (default: False) return CSV of TLDs
    :param csv_path: (default: None) path to save CSV
    """
    get = requests.get('https://data.iana.org/TLD/tlds-alpha-by-domain.txt')
    tlds = get.text.split('\n')
    release = tlds[0].replace('# ', '')
    msg.info(f'IANA.org TLDs: {release}')
    tlds.pop(0)
    msg.loading()
    tlds = [x.lower() for x in tlds if x]
    msg.good(f'{len(tlds)} TLDs found')
    if list:
        msg.good('Returned list of TLDs')
        return tlds
    if df:
        df = pd.DataFrame(tlds, columns=['tld'])
        msg.good(f'TLD DataFrame created')
        return df
    if csv:
        if csv_path:
            df = pd.DataFrame(tlds, columns=['tld'])
            df.to_csv(csv_path, index=False)
            msg.good(f'CSV saved to {csv_path}')
        else:
            msg.error('No CSV path provided')
            return False

tlds = fetch(list=True)
print(tlds)

def parse(string, tlds, detect=False, extract=True, domain=True, url=True, subdomain=True):
    """
    Parse a string for domains or URLs
    :param string: string to parse
    :param tlds: list of TLDs to search for
    :param detect: detect domains or URLs in string ~ will only return True/False if found
    :param extract: (default: True) extract all domains or URLs from string ~ returns list of domains or URLs
    :param domain: (default: False) returns domains (i.e 'example.com')
    :param url: (default: True) return URLs (i.e. 'https://example.com')
    :param subdomain: (default: True) return subdomains (i.e. 'news.example.com')
    """
    # validation
    if not tlds:
        msg.fail('No TLDs provided')
        raise ValueError('No TLDs provided! Please provide a list of TLDs to search for.')
    if not string:
        msg.fail('No string provided')
        raise ValueError('No string provided! Please provide a string to parse.')
    
    if detect: # detect domains or URLs in string ~ will only return True/False if found
        extract = False
        if domain:
            if any(f'.{x.lower()}' in string for x in tlds):
                msg.good('Url(s) / Domain(s) found in string')
                return True
            else:
                msg.fail('No Url(s) / Domain(s) found in string')
                return False
        if url:
            regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
            if re.search(regex, string):
                msg.good('Url(s) / Domain(s) found in string')
                return True
            else:
                msg.fail('No Url(s) / Domain(s) found in string')
                return False

    if extract: # extract all domains or URLs from string ~ returns list of domains or URLs
        urls = []
        domains = []
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        for x in re.findall(regex, string):
            urls.append(x[0])
        if domain:
            nlp = spacy.load('en_core_web_sm')
            doc = nlp(string)
            for tld in tlds:
                for token in doc:
                    if token.text.lower().endswith(f'.{tld}'):
                        domains.append(token.text)
            for i in range(len(domains)):
                if subdomain:
                    domains[i] = urlparse(domains[i]).netloc
                else: # return only domain + tld
                    domains[i] = tldextract.extract(domains[i]).registered_domain
        if url and not domain:
            msg.good(f'Found {len(urls)} in string')
            return url
        if url and domain:
            msg.good(f'Found {len(urls)} URL9(s) in string and {len(domains)} domain(s)')
            return urls + domains
        if domain and not url:
            msg.good(f'Found {len(domains)} domain(s) in string')
            return domains
            

test_text = "Hello, this is a test. https://example.com/test.html?test=1&test2=2, I also enjoy the website github.com, but wish they'd merge it with gists.github.com"
print("\nTesting parse() function:")
# test 1: detect domains or URLs in string ~ will only return True/False if found
msg.info('Test 1')
res = parse(test_text, tlds, detect=True)
expected_result = True
print (f"Expected result: {expected_result}")
print (f"Actual result: {res}")
# test 2: extract all domains or URLs from string ~ returns list of domains or URLs
res = parse(test_text, tlds, extract=True)
expected_result = ['https://example.com/test.html?test=1&test2=2', 'github.com', 'gists.github.com']
msg.info('Test 2')
print(f'Expected result: {expected_result}')
print(f'Actual result: {res}')
# test 3: extract domains from string ~ returns list of domains
res = parse(test_text, tlds, extract=True, domain=True, url=False)
msg.info('Test 3')
expected_result = ['example.com', 'github.com', 'gists.github.com']
print(f'Expected result: {expected_result}')
print(f'Actual result: {res}')
