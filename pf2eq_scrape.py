import requests
import csv
import time

from bs4 import BeautifulSoup

URL_ALL = 'https://2e.aonprd.com/Equipment.aspx?All=true'
BASE_URL = 'https://2e.aonprd.com/'
ITEM_ATTR = '?ID='
GP_RATE = {
    'gp': 1.0,
    'sp': 0.1,
    'cp': 0.01,
}


def convert_to_gp(price: str) -> float:
    s = price.split()
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


def scrape_equipment(soup: BeautifulSoup, curr_id: int):
    item = soup.find(id='ctl00_MainContent_DetailedOutput')
    traits = [str(x.string) for x in item.find_all(class_='trait')]
    title_bar = item.find('h1', class_='title')
    lvl = str(title_bar.contents[-1].string).split()[-1]
    prices = [convert_to_gp(str(x.nextSibling)) for x in item.find_all_next('b', string='Price')]
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
    item = soup.find(id='ctl00_MainContent_DetailedOutput')
    traits = []
    trait_section = item.find('b', string='Traits')
    if trait_section:
        trait = trait_section.find_next_sibling('u')
        while trait:
            traits.append(str(trait.a.string))
            trait = trait.find_next_sibling('u')
    title_bar = item.find('h1', class_='title')
    lvl_tag = title_bar.find('span', style='float:right')
    lvl = '0'
    if lvl_tag:
        lvl = str(lvl_tag.string).split()[-1]
    prices = [convert_to_gp(str(x.nextSibling)) for x in item.find_all_next('b', string='Price')]
    title = str(title_bar.find_all('a')[-1].string)
    rarity = 'Rare' if item.find(class_='traitrare') else (
        'Uncommon' if item.find(class_='traituncommon') else
        'Common')
    writer.writerow([curr_id, title, lvl, rarity, prices[0] if prices else 0, traits, url])
    return curr_id + 1


with open('items.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['ID', 'Title', 'Lvl', 'Rarity', 'Price', 'Traits', 'URL'])
    checked_urls = set()
    curr_id = 1
    counter = 1
    url_all = URL_ALL
    page_all = requests.get(url_all)
    soup = BeautifulSoup(page_all.text, 'html5lib')
    item_list = soup.find(id='ctl00_MainContent_AllElement').tbody.find_all('tr')[1:]
    print(f'Found {item_list.__len__()} items')
    print(f'Starting scrapping')
    for item in item_list:
        link = item.td.a.attrs['href']
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
                    print(f'Scraped {counter} / {item_list.__len__()} items, items created: {curr_id}')
                counter += 1
                # time sleep to prevent spamming the site
                time.sleep(1)
            else:
                print(f'Item {url} is unavailable!')
    print(f'FINISHED! Scraped {curr_id - 1} items')
