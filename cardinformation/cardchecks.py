from database import searchcards


def get_card_info():
    """
    collect info related to the current card
    dict is split into sections
    returns: dict of all data
    """
    card_dict = {'card_image': '', 'rulings': [], 'info': {}}
    current_card = searchcards.current_card()

    # card_image
    card_dict['card_image'] = current_card.card_image

    # rulings
    card_dict['rulings'] = searchcards.get_current_card_rulings()

    # card info ###
    # card price
    card_dict['info']['card price $'] = current_card.card_price

    # card colour breakdown
    cardcolours = searchcards.get_current_card_colours()
    for colour in cardcolours:
        # card count in the colour
        card_dict['info'][str(colour.colour)] = ':all - ' +\
                                                str(searchcards.get_cards_colour_count(colour))
        # rarity count in the colour
        col_string = str(colour) + ':' + str(current_card.card_rarity)
        card_dict['info'][col_string] = ' ' + str(searchcards.get_cards_colour_count_current_card_rarity(colour))

    # card sub types total
    all_card_subtypes = searchcards.get_current_card_suptypes()
    for subtype in all_card_subtypes:
        # print (solo_type)
        card_dict['info'][str(subtype)] = ' ' + str(searchcards.get_card_subtype_count(subtype))

    return card_dict

