from database.searchcards import current_card


def get_bg_colour_hex(colour):
    colours = {'W': '#eadede',
               'U': '#4b81d8',
               'B': '#1c1d1e',
               'R': '#af2626',
               'G': '#339b41',
               'multi-colour': '#bc3cba',
               'colourless': '#898189'}
    if colour in colours:
        return colour
    else:
        return '#FFFFFF'


def get_current_bg_colour_hex():
    return get_bg_colour_hex(current_card().card_colour)


def get_colour_dict_array(length):
    array = [0] * length
    colours = ['All', 'W', 'U', 'B', 'R', 'G', 'colourless', 'multi-colour']
    return_dict = {col: array for col in colours}
    return return_dict
