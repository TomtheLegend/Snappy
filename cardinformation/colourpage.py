from cardinformation.statics import get_bg_colour_hex
from database.searchcards import get_top_cards_by_colour, get_top_common_cards_by_colour


def get_card_colour_page_info(colour):

    all_card_ratings = {'CardColour_ratings': get_top_cards_by_colour(colour),
                        'common_ratings': get_top_common_cards_by_colour(colour),
                        'bg_colour': get_bg_colour_hex(colour), }
    return all_card_ratings
