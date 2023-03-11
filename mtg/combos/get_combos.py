#!/usr/bin/env python3
# Combo parser
#
# python -m virutalenv .venv
# source .venv/bin/activate
# pip install click requests beautifulsoup4 html5lib

from bs4 import BeautifulSoup
import click
import re
import requests
import urllib.parse

COMBO_TYPES = [
    'combo_win',
    'combo_mill'
    'combo_draw',
    'combo_life',
    'combo_life',
    'combo_attack',
    'combo_lock',
    'combo_soft_lock',
    'combo_mana',
    'combo_token',
    'combo_turn',
    'combo_storm',
    'combo_tie',
    'combo_etb',
    'combo_review',
    'combo_power',
]
COLORS = {
    'colorless': 'C',
    'green': 'G',
    'red': 'R',
    'black': 'B',
    'white': 'W',
    'blue': 'U',
}
count_rex = re.compile(r'.* Showing[\s]+(?P<num_combos>[0-9]+)[\s]+combos from[\s]+(?P<total_combos>[0-9]+)[\s]+results', re.DOTALL)
next_page_rex = re.compile(r'.*&page=(?P<page_num>[0-9]+)')
base_url = "https://mtg.cardsrealm.com"
combo_url = f"{base_url}/en-us/combo-infinite/"

def get_page(
    page=1,
    types="",
    path="",
    colors="",
    card_format=6, # commander
    color_operator="or",
    order_by="combo_datetime DESC"
):
    q = {
        "page": page,
        "types": types, 
        "card_path": path, # name of a card to combo
        "order_by": order_by,
        "colors": colors,
        "color_operator": color_operator,
        "card_format": card_format,
    }
    r = requests.get(combo_url, params=q)
    return BeautifulSoup(r.content, 'html5lib')

def parse_combos(page):
    arrow = page.find('a', attrs={'class': 'arrow_right'})
    next = 0
    if arrow:
        if m := next_page_rex.match(arrow.get('href')):
            next = int(m.group('page_num'))

    combos = page.findAll('a', attrs={'class':'combo_search_combo_div'}) 
    stripe = page.findAll('h1', attrs={'class': 'website_stripe_top'})
    num = 0
    total = 0
    if m := count_rex.match(str(stripe)):
        num = m.group('num_combos')
        total = m.group('total_combos')
    return next, num, total, combos

def report(combos):
    report_string = ""
    for c in combos:
        combo_url = base_url + c.get('href')
        report_string += f"<a href='{combo_url}' target='_blank'>{c.get('title')}</a><br>"
        cards = c.find(
            'div',
            attrs={'class': 'combo_search_combo_div_div'}
        ).findAll(
            'div',
            attrs={'class': 'combo_hover'}
        )
        types = c.find(
            'div',
            attrs={'class': 'combo_search_types_div'}
        ).findAll(
            'div',
            attrs={'class': 'combo_search_type_type'}
        )
        report_string += "<table border=0><tr>"
        for card_obj in cards:
            card = card_obj.find('img')
            report_string += f"<td><a href='https://www.lecoindujeu.ca/search?page=1&q={urllib.parse.quote(card.get('alt'))}' target='_blank'>{card.get('alt')}<br><img alt='{card.get('alt')}' src='{card.get('src')}' /></a></td>"
        report_string += "</tr></table>"
        for type_obj in types:
            report_string += type_obj.get('title') + "<br/"
        report_string += "<p>"
    return report_string

def get_combos(card, combo_choice, colors, card_format):
    next = 1
    card_report = f"<h1>{card}</h1>"
    parsed_cards = 0
    while next > 0:
        page = get_page(page=next, path=card,
                        types=combo_choice, colors=colors,
                        card_format=card_format)
        (next, num, total, combos) = parse_combos(page)
        parsed_cards += int(num)
        print(f"[{card}] Next page: {next} {parsed_cards} / {total}")
        card_report += report(combos)
    if parsed_cards == 0:
        return ""
    return card_report

@click.command()
@click.option('--type', 'combo_types_choice', multiple=True, type=click.Choice(COMBO_TYPES))
@click.option('--color', 'color_choice', multiple=True, type=click.Choice(COLORS.keys()))
@click.option('--format', 'card_format', default=6)
@click.option('--card-file', type=click.File('r'))
@click.option('--output', default='mtg-report.html', type=click.Path(exists=False))
def main(card_file, combo_types_choice, color_choice, card_format, output):
    combo_choice = ",".join(combo_types_choice)
    colors = "".join([COLORS[c] for c in color_choice])
    full_report = ""
    for card in card_file.readlines():
        full_report += get_combos(card.rstrip(), combo_choice, colors, card_format)
    with open(output, 'w') as f:
        f.write(full_report)

if __name__ == "__main__":
    main()
