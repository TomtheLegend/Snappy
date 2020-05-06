from database import searchcards
from cardinformation.statics import get_colour_dict_array
from flask_socketio import emit


def get_averge_by_cmc(cmc, table):

    card_averages = searchcards.get_all_card_metrics_by_cmc(table, cmc)
    return_dict = get_colour_dict_array(10)
    rarity_pos = {'all': 1, 'common': 3, 'uncommon': 5, 'rare': 7, 'mythic': 9}

    for card_colour, card_rarity, _, card_average, card_count in card_averages:
        num_position = rarity_pos[card_rarity]
        # average
        return_dict[card_colour][(num_position - 1)] = card_average
        # count
        return_dict[card_colour][num_position] = card_count
        # print(return_dict[card_av[0]])
    return return_dict


def get_averages(table):
    """
    Used to get the averages by cmc and rarity for a table.
    Mainly used for power and toughness
    """
    card_cmcs = searchcards.get_all_distinct_by_cmc(table)
    return_averages = {}
    for cmc, *_ in card_cmcs:
        return_averages[cmc[0]] = get_averge_by_cmc(cmc[0], table)
        print(return_averages[cmc[0]])
    return return_averages


def get_supertypes():
    return_averages = {}
    card_supertypes = searchcards.get_distinct_supertypes()
    for supertype in card_supertypes:
        return_averages[supertype[0]] = get_supertypes_by_type(supertype[0])
        # print(return_averages[cmc[0]])
    return return_averages


def get_supertypes_by_type(supertype):
    card_averages = searchcards.get_supertypes_by_type(supertype)
    return_dict = get_colour_dict_array(5)
    rarity_pos = {'all': 0, 'common': 1, 'uncommon': 2, 'rare': 3, 'mythic': 4}
    for card_av in card_averages:
        num_position = rarity_pos[card_av[0]]
        return_dict[card_av[1]][num_position] = card_av[2]
    return return_dict


def send_previous_voted():
    previous_card_data = {'prev_card_info': searchcards.previous_card(),
                          'prev_card_Ratings':  searchcards.get_previous_card_all_user_ratings()}
    emit('previous_card', previous_card_data, namespace='/info', broadcast=True)
