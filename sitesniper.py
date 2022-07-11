# imports & dependencies
from platform import release
import pandas as pd
import requests
from wasabi import msg
import dateutil.parser as dparser
import datetime

# get list of current TLDs from IANA / ICANN
def fetch(list=True, df=False, csv=False, csv_path=None):
    get = requests.get('https://data.iana.org/TLD/tlds-alpha-by-domain.txt')
    tlds = get.text.split('\n')
    release = tlds[0].replace('# ', '')
    msg.info(f'IANA.org TLDs: {release}')
    tlds.pop(0)
    msg.loading()
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

