#!/usr/bin/env python

from optparse import OptionParser

from lib import mark_up


MINIMUM_MARKED_DATA_PERCENT = 1
MINIMUM_NEW_CAT_PERCENT = 50


def make_decision(new_cat_percent: float, marked_up_percent: float) -> bool:
    mark_up_data = False

    # нам важны как однородность размеченных данных так и процент размеченных данных
    # грубо, можно было бы сделать if new_cat_percent + marked_up_percent > 100,
    # но на мой взгляд это смотрится черезчур дико
    if new_cat_percent == 100:
        mark_up_data = True
    elif new_cat_percent > 90:
        if marked_up_percent >= 3:
            mark_up_data = True
    elif new_cat_percent > 80:
        if marked_up_percent >= 5:
            mark_up_data = True
    elif new_cat_percent > 70:
        if marked_up_percent >= 7:
            mark_up_data = True

    return mark_up_data


if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option('-v', action='store_true', dest='verbose', help='verbose mode')
    parser.add_option('-a', '--all', action='store_true', dest='all', help='mark up all available data')

    (options, args) = parser.parse_args()

    mark_up(mark_up_all=options.all is True, verbose=options.verbose is True)
