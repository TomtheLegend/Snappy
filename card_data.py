import scrython
import requests
import csv

set_code = 'eld'

def get_all_cards():
    new_cards = scrython.cards.Search(q='set:{} is:booster'.format(set_code), order='color')
    all_cards = new_cards.data()
    # print(new_cards.next_page())
    if new_cards.has_more():
        next_set = requests.get(new_cards.next_page()).json()
        all_cards.extend(get_more_cards(next_set))
    return all_cards


def get_edited_cards(all_cards):
    edited_list = []

    for card in all_cards:
        '''
        'name': 'Interplanar Beacon'
        'mana_cost': '', 
        'cmc': 0.0, 
        'type_line': 'Land', 
        'oracle_text'
        '''
        short_dict = {'name': card['name'],
                      'cmc': card['cmc'],
                      'type': card['type_line'],
                      'rarity': card['rarity'],
                      'sub_types': get_card_sub_types(card['type_line']),
                      'oracle_text': card['oracle_text']
                      }
        edited_list.append(short_dict)
    return edited_list


def get_more_cards(all_card_data):
    card_data = all_card_data['data']
    # if has more
    if all_card_data['has_more']:
        # print(all_card_data['next_page'])
        # request new uri
        next_set = requests.get(all_card_data['next_page']).json()
        return card_data.extend(get_more_cards(next_set))
    else:
        return card_data


def get_card_sub_types(card_type_line):
    suptypes_return = []
    if '—' in card_type_line:
        suptypes = card_type_line.split('—')[1].split(' ')
        for sub in suptypes:
            # add to the db
            if sub != '':
                suptypes_return.append(sub.strip())
    return suptypes_return

def get_card_sub_types_as_string(card_type_line):
    suptypes_return = ''
    if '—' in card_type_line:
        suptypes = card_type_line.split('—')[1].split(' ')
        for sub in suptypes:
            # add to the db
            if sub != '':
                suptypes_return.join(sub.strip(), ',')
    return suptypes_return

def write_all_cards_to_csv():
    all_cards = get_edited_cards(get_all_cards())
    print(all_cards)
    with open('all_cards_sample.csv', 'w', encoding="utf-8", newline='') as outfile:
        w = csv.DictWriter(outfile, all_cards[0].keys())
        for card in all_cards:
            w.writerow(card)


# write_all_cards_to_csv()
