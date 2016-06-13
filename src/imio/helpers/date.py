# -*- coding: utf-8 -*-
from DateTime import DateTime
from zope.i18n import translate


MONTHIDS = {1: 'month_jan', 2: 'month_feb', 3: 'month_mar', 4: 'month_apr',
            5: 'month_may', 6: 'month_jun', 7: 'month_jul', 8: 'month_aug',
            9: 'month_sep', 10: 'month_oct', 11: 'month_nov', 12: 'month_dec'}


def formatDate(date, month_name=True, context=None, long_format=False):
    """
      Format the given date.  This is usefull for formatting dates
      in the pod templates
      long_format:we want the hour with it
      mont_name:we want the name of the month instead of the number
      Note that we force european format...
    """
    if date == "now":
        # we want the current date, calculate it
        date = DateTime()

    day = date.dd()
    year = str(date.year())
    month = date.mm()

    if long_format:
        hour = date.strftime(' (%H:%M)')
    else:
        hour = ''
    # check if we need to return the month name
    if month_name:
        month = date.month()
        translated_month = translate(msgid=MONTHIDS[month],
                                     domain="plonelocales",
                                     context=context,
                                     default=MONTHIDS[month],
                                     target_language='fr')
        # replace '01 ' by '1er '
        if date.day() == 1:
            day = '1er'
        return u'{0} {1} {2}{3}'.format(day,
                                        translated_month.lower(),
                                        year,
                                        hour)
    else:
        return u'{0}/{1}/{2}{3}'.format(day, month, year, hour)


def wordizeDate(date, context=None, long_format=False):
    """
      Convert a date made of digits to a date made of words.
      If long_format is True, we convert the hour to words too
    """
    converted_month = formatDate(date,
                                 month_name=True,
                                 context=context,
                                 long_format=False).split(' ')[1]

    splitted_date = date.strftime("%Y/%m/%d").split('/')
    date_time = ""
    # check if we have a time
    if len(str(date).split(' ')) > 1:
        date_time = str(date).split(' ')[1]

    # work on the date
    day_to_convert = int(splitted_date[2])
    if day_to_convert == 1:
        converted_day = "premier"
    else:
        converted_day = int2word(day_to_convert)
    converted_year = int2word(splitted_date[0])
    converted_date = u"{} {} {}".format(converted_day,
                                        converted_month,
                                        converted_year)

    converted_time = ""
    if long_format and date_time:
        # work on the hour
        splitted_time = date_time.split(':')
        hour = splitted_time[0]
        minutes = splitted_time[1]
        converted_hour = int2word(int(hour))
        if converted_hour.endswith("un"):
            converted_hour += "e"
        converted_minutes = int2word(int(minutes))
        if hour in ['01', '1', '0', '00', ]:
            hour_word = "heure"
        else:
            hour_word = "heures"
        # do not display 'zero' in the date like : eleven hour zero...
        # see http://dev.communesplone.org/trac/ticket/1553
        if converted_minutes and minutes not in ['0', '00', ]:
            converted_time = u" {} {} {} {}".format(u"à",
                                                    converted_hour,
                                                    hour_word,
                                                    converted_minutes)
        else:
            # remove the minutes, especially useless spaces if there
            # are no minutes
            converted_time = u" {} {} {}".format(u"à",
                                                 converted_hour,
                                                 hour_word)
    return converted_date.encode('utf-8') + converted_time.encode('utf-8')


def int2word(n):
    """Convert an integer number into a string of french word
    based on the http://www.daniweb.com/code/snippet609.html
    code that convert into english words..."""

    ONES = ["", "un ", "deux ", "trois ", "quatre ", "cinq ",
            "six ", "sept ", "huit ", "neuf "]
    TENS = ["dix ", "onze ", "douze ", "treize ", "quatorze ",
            "quinze ", "seize ", "dix-sept ", "dix-huit ", "dix-neuf "]
    TWENTIES = ["", "", "vingt ", "trente ", "quarante ", "cinquante ",
                "soixante ", "septante ", "quatre-vingt ", "nonante "]
    THOUSANDS = ["", "mille ", "million ", "milliard ", "billiard ",
                 "trilliard ", "quadrilliard ", "quintillard ",
                 "sextilliard ", "septilliard ", "octilliard ", "nonilliard ",
                 u"décillion ", u"décilliard ", u"unodécillion ",
                 u"unodécilliard ", u"duodécillion ", u"duodécilliard "]

    # quickly manage if n is < 10
    if n < 10:
        ONES = [u"zéro ", "un ", "deux ", "trois ", "quatre ",
                "cinq ", "six ", "sept ", "huit ", "neuf "]
        return ONES[n].strip()

    # break the number into groups of 3 digits using slicing
    # each group representing hundred, thousand, million, billion, ...
    n3 = []
    # create numeric string
    ns = str(n)
    for k in range(3, 60, 3):
        r = ns[-k:]
        q = len(ns) - k
        # break if end of ns has been reached
        if q < -2:
            break
        else:
            if q >= 0:
                n3.append(int(r[:3]))
            elif q >= -1:
                n3.append(int(r[:2]))
            elif q >= -2:
                n3.append(int(r[:1]))

    # break each group of 3 digits into
    # ONES, TENS/TWENTIES, hundreds
    # and form a string
    nw = ""
    for i, x in enumerate(n3):
        b1 = x % 10
        b2 = (x % 100) // 10
        b3 = (x % 1000) // 100
        if x == 0:
            continue  # skip
        else:
            t = THOUSANDS[i]
        if b2 == 0:
            # cas du 'mille' qui n'est pas 'un mille'
            if b1 == 1 and i == 1:
                nw = t + nw
            else:
                nw = ONES[b1] + t + nw
        elif b2 == 1:
            nw = TENS[b1] + t + nw
        elif b2 > 1:
            extra = ""
            if b1 == 1:
                nw = TWENTIES[b2] + "et un " + t + nw
            elif b1 > 1:
                nw = TWENTIES[b2][:-1] + "-" + ONES[b1] + t + nw
            else:
                nw = TWENTIES[b2] + extra + ONES[b1] + t + nw
        if b3 > 0:
            if b3 > 1:
                nw = ONES[b3] + "cent " + nw
            else:
                nw = "cent " + nw
    return nw.strip()
