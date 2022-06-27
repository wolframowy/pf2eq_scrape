import json
import requests
import csv
import time
import timeit
from datetime import timedelta
import re
import argparse


from bs4 import BeautifulSoup

BASE_URL = 'https://2e.aonprd.com/'
ITEM_ATTR = '?ID='
GP_RATE = {
    'gp': 1.0,
    'sp': 0.1,
    'cp': 0.01,
}


def convert_to_gp(price: str) -> float:
    s = re.sub(r'\(.*\)', '', price).split()
    value = 0
    if len(s) < 2 or s[0][0] == '—':
        return 0.0
    value += GP_RATE[''.join(e for e in s[1] if e.isalnum())] * int(''.join(e for e in s[0] if e.isalnum()))
    return value


def search_for_subitem_rarity(title_tag) -> str:
    curr = title_tag.next_sibling
    while curr.name != 'br' and curr.name != 'b':
        if curr['class'][0] == 'traitrare':
            return 'Rare'
        if curr['class'][0] == 'traituncommon':
            return 'Uncommon'
        curr = curr.next_sibling
    return 'Common'


def search_for_subitem_traits(title_tag, main_traits) -> str:
    curr = title_tag.find_next_sibling(class_='trait');
    sub_traits = [];
    while curr and curr.get('class') and 'trait' in curr['class']:
        sub_traits.append(curr.string)
        curr = curr.next_sibling
    
    return json.dumps(sub_traits) if len(sub_traits) > 0 else main_traits


def scrape_equipment(soup: BeautifulSoup, curr_id: int):
    item = soup.find(id='ctl00_RadDrawer1_Content_MainContent_DetailedOutput')
    traits = json.dumps([str(x.string) for x in item.find_all(class_='trait')])
    title_bar = item.find('h1', class_='title')
    lvl = str(title_bar.contents[-1].string).split()[-1]
    prices = [convert_to_gp(str(x.nextSibling)) for x in item.find_all('b', string='Price')]
    if lvl[-1] == '+':
        title_bars = [x for x in item.find_all('h2', class_='title') if x.previous_sibling.name != 'h1']
        if len(prices) < len(title_bars):
            prices.extend([0.0] * (len(title_bars) - len(prices)))
        sup_rarity = search_for_subitem_rarity(title_bar)
        for i in range(len(title_bars)):
            if title_bars[i].previous_sibling.name == 'h1':
                title_bars.pop(i)
                i -= 1
                continue
            title = str(title_bars[i].contents[-2].string)
            lvl = str(title_bars[i].contents[-1].string).split()[-1]
            rarity = search_for_subitem_rarity(title_bars[i]) if sup_rarity == 'Common' else sup_rarity
            traits = search_for_subitem_traits(title_bars[i], traits)
            writer.writerow([curr_id, title, lvl, rarity, prices[i], traits, url])
            curr_id += 1
    else:
        title = str(title_bar.contents[-2].string)
        lvl = str(title_bar.contents[-1].string).split()[-1]
        rarity = 'Rare' if item.find(class_='traitrare') else (
            'Uncommon' if item.find(class_='traituncommon') else
            'Common')
        writer.writerow([curr_id, title, lvl, rarity, prices[0] if prices else 0, traits, url])
        curr_id += 1
    return curr_id


def scrape_other(soup: BeautifulSoup, curr_id: int):
    item = soup.find(id='ctl00_RadDrawer1_Content_MainContent_DetailedOutput')
    traits = []
    trait_section = item.find('b', string='Traits')
    if trait_section:
        trait = trait_section.find_next_sibling('u')
        while trait:
            traits.append(str(trait.a.string))
            trait = trait.find_next_sibling('u')
    traits = json.dumps(traits)
    title_bar = item.find('h1', class_='title')
    lvl_tag = title_bar.find('span', style='float:right')
    lvl = '0'
    if lvl_tag:
        lvl = str(lvl_tag.string).split()[-1]
    prices = [convert_to_gp(str(x.nextSibling)) for x in item.find_all('b', string='Price')]
    title = str(title_bar.find_all('a')[-1].string)
    rarity = 'Rare' if item.find(class_='traitrare') else (
        'Uncommon' if item.find(class_='traituncommon') else
        'Common')
    writer.writerow([curr_id, title, lvl, rarity, prices[0] if prices else 0, traits, url])
    return curr_id + 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PF2E loot scrapper')
    parser.add_argument('fileName', metavar='fileName', type=str, help='File location of all exported items from https://2e.aonprd.com/Equipment.aspx?All=true')
    args = parser.parse_args()
    with open(args.fileName, newline='') as csvfile:
        item_count = sum(1 for line in csvfile) - 1
        print(f'Found {item_count} items')
        print(f'Starting scrapping')
    time_start = timeit.default_timer()
    with open(args.fileName, newline='', encoding='utf-8-sig') as csvfile:
        item_list = csv.DictReader(csvfile, quotechar='"');
        with open('items.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';', quotechar="'")
            writer.writerow(['ID', 'Title', 'Lvl', 'Rarity', 'Price', 'Traits', 'URL'])
            checked_urls = set()
            curr_id = 1
            counter = 1
            try:
                for row in item_list:
                    link = BeautifulSoup(row['Name'], 'html5lib').a.attrs['href']
                    if link not in checked_urls:
                        checked_urls.add(link)
                        url = BASE_URL + link
                        page = requests.get(url)
                        if page.status_code == 200:
                            soup = BeautifulSoup(page.text, 'html5lib')
                            if link.find('Equipment') >= 0:
                                curr_id = scrape_equipment(soup, curr_id)
                            else:
                                curr_id = scrape_other(soup, curr_id)
                            if counter % 10 == 0:
                                time_run = timeit.default_timer() - time_start
                                print(f'T:{timedelta(seconds=time_run)} Scraped {counter} / {item_count} items, items created: {curr_id}')
                            # time sleep to prevent spamming the site
                            time.sleep(1)
                        else:
                            print(f'Item {url} is unavailable!')
                    counter += 1
            except Exception as ex:
                print(row['Name'])
                print(url)
                print(f'ERROR {ex}')
                quit()
            print(f'FINISHED! Scraped {curr_id - 1} items')
