import requests
import csv
import time

from bs4 import BeautifulSoup

BASE_URL = 'https://2e.aonprd.com/Equipment.aspx'
ITEM_ATTR = '?ID='
GP_RATE = {
    'gp': 1.0,
    'sp': 0.1,
    'cp': 0.01,
}


def convert_to_gp(price: str) -> float:
    s = price.split()
    return GP_RATE[s[1]] * int(s[0].replace(',', ''))


with open('items.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Title', 'Lvl', 'Price', 'Traits', 'URL'])
    curr_id = 26
    url = BASE_URL + ITEM_ATTR + str(curr_id)
    page = requests.get(url)
    while page.status_code == 200:
        soup = BeautifulSoup(page.text, 'html5lib')
        item = soup.find(id='ctl00_MainContent_DetailedOutput')
        traits = [str(x.string) for x in item.find_all(class_='trait')]
        title_bars = item.find_all(class_='title')
        prices = [convert_to_gp(str(x.nextSibling)) for x in item.find_all_next('b', string='Price')]
        if len(title_bars) > 1:
            for i in range(1, len(title_bars)):
                title = str(title_bars[i].contents[-2].string)
                lvl = str(title_bars[i].contents[-1].string).split()[-1]
                writer.writerow([curr_id, title, lvl, prices[i - 1], traits, url])
        else:
            title = str(title_bars[0].contents[-2].string)
            lvl = str(title_bars[0].contents[-1].string).split()[-1]
            writer.writerow([curr_id, title, lvl, prices[0] if prices else 0, traits, url])
        if curr_id % 10 == 0:
            print(f'Scraped {curr_id} items')
        curr_id += 1
        url = BASE_URL + ITEM_ATTR + str(curr_id)
        page = requests.get(url)
        # time sleep to prevent spamming the site
        time.sleep(1)
    print(f'FINISHED! Scraped {curr_id - 1} items')
