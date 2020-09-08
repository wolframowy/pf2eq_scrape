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


def search_for_subitem_rarity(title_tag) -> str:
    curr = title_tag.next_sibling
    while curr.name != 'br' and curr.name != 'b':
        if curr['class'][0] == 'traitrare':
            return 'Rare'
        if curr['class'][0] == 'traituncommon':
            return 'Uncommon'
        curr = curr.next_sibling
    return 'Common'


with open('items.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Title', 'Lvl', 'Rarity', 'Price', 'Traits', 'URL'])
    curr_id = 1
    url = BASE_URL + ITEM_ATTR + str(curr_id)
    page = requests.get(url)
    while page.status_code == 200:
        soup = BeautifulSoup(page.text, 'html5lib')
        item = soup.find(id='ctl00_MainContent_DetailedOutput')
        traits = [str(x.string) for x in item.find_all(class_='trait')]
        title_bar = item.find('h1', class_='title')
        lvl = str(title_bar.contents[-1].string).split()[-1]
        prices = [convert_to_gp(str(x.nextSibling)) for x in item.find_all_next('b', string='Price')]
        if lvl[-1] == '+':
            title_bars = item.find_all('h2', class_='title')
            for i in range(len(title_bars)):
                title = str(title_bars[i].contents[-2].string)
                lvl = str(title_bars[i].contents[-1].string).split()[-1]
                rarity = search_for_subitem_rarity(title_bars[i])
                writer.writerow([curr_id, title, lvl, rarity, prices[i], traits, url])
        else:
            title = str(title_bar.contents[-2].string)
            lvl = str(title_bar.contents[-1].string).split()[-1]
            rarity = 'Rare' if item.find(class_='traitrare') else ('Uncommon' if item.find(class_='traituncommon') else
                                                                   'Common')
            writer.writerow([curr_id, title, lvl, rarity, prices[0] if prices else 0, traits, url])
        if curr_id % 10 == 0:
            print(f'Scraped {curr_id} items')
        curr_id += 1
        url = BASE_URL + ITEM_ATTR + str(curr_id)
        page = requests.get(url)
        # time sleep to prevent spamming the site
        time.sleep(1)
    print(f'FINISHED! Scraped {curr_id - 1} items')
