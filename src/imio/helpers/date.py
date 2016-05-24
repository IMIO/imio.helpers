# -*- coding: utf-8 -*-
from DateTime import DateTime
from imio.helpers.testing import IntegrationTestCase
from zope.i18n import translate


monthsIds = {1:  'month_jan', 2:  'month_feb', 3:  'month_mar', 4:  'month_apr',
             5:  'month_may', 6:  'month_jun', 7:  'month_jul', 8:  'month_aug',
             9:  'month_sep', 10: 'month_oct', 11: 'month_nov', 12: 'month_dec'}

def formatDate(date, month_name=True, context=None, long_format=False):
    """
      Format the given date.  This is usefull for formatting dates in the pod templates
      long_format : we want the hour with it
      mont_name : we want the name of the month instead of the number
      Note that we force european format...
    """
    if date == "now":
        #we want the current date, calculate it
        date = DateTime()

    if long_format:
        hour = ' (%H:%M)'
    else:
        hour = ''
    #check if we need to return the month name
    if month_name:
        month = date.month()
        translated_month = translate(msgid=monthsIds[month], domain="plonelocales", context=context, default=monthsIds[month], target_language='fr')
        #use mOntH here to avoid strftime translating the month...
        res = date.strftime('%e mOntH %Y' + hour)
        #replace '01 ' by '1er '
        res = res.replace('01 ', '1er ')
        #... now that we have mOntH in the string, we can easily replace it
        res = res.replace('mOntH', translated_month.lower())
        return res.strip()
    else:
        return date.strftime("%d/%m/%Y" + hour)

def wordizeDate(date, context=None, long_format=False):
    """
      Convert a date made of digits to a date made of words.
      If long_format is True, we convert the hour to words too
    """
    converted_month = formatDate(date, month_name=True, context=context, long_format=False).split(' ')[1]

    splitted_date = date.strftime("%Y/%m/%d").split('/')
    date_time = ""
    #check if we have a time
    if len(str(date).split(' ')) > 1:
        date_time = str(date).split(' ')[1]

    #work on the date
    day_to_convert = int(splitted_date[2])
    if day_to_convert == 1:
        converted_day = "premier"
    else:
        converted_day = int2word(day_to_convert)
    converted_year = int2word(splitted_date[0])
    converted_date = "%s %s %s" % (converted_day, converted_month, converted_year)

    converted_time = ""
    if long_format and date_time:
        #work on the hour
        splitted_time = date_time.split(':')
        hour = splitted_time[0]
        minutes = splitted_time[1]
        converted_hour = int2word(int(hour))
        if converted_hour.endswith("un "):
            converted_hour = converted_hour[:-1] + "e"
        converted_minutes = int2word(int(minutes))
        if hour in ['01', '1', '0', '00', ]:
            hour_word = "heure"
        else:
            hour_word = "heures"
        #do not display 'zero' in the date like : eleven hour zero...
        #see http://dev.communesplone.org/trac/ticket/1553
        if converted_minutes and not minutes in ['0', '00',]:
            converted_time = " %s %s %s %s" % (u"à", converted_hour, hour_word, converted_minutes)
        else:
            #remove the minutes, especially useless spaces if there are no minutes
            converted_time = " %s %s %s" % (u"à", converted_hour, hour_word)
    return converted_date.encode('utf-8') + converted_time.encode('utf-8')

def int2word(n):
    """
      Convert an integer number into a string of french word
      Based on the http://www.daniweb.com/code/snippet609.html
      code that convert into english words...
    """
    ############# globals ################
    ones = ["", "un ","deux ","trois ","quatre ", "cinq ",
    "six ","sept ","huit ","neuf "]
    tens = ["dix ","onze ","douze ","treize ", "quatorze ",
    "quinze ","seize ","dix-sept ","dix-huit ","dix-neuf "]
    twenties = ["","","vingt ","trente ","quarante ",
    "cinquante ","soixante ","septante ","quatre-vingt ","nonante "]
    thousands = ["","mille ","million ", "milliard ", "billiard ",
    "trilliard ", "quadrilliard ", "quintillard ", "sextilliard", "septilliard ",
    "octilliard ", "nonilliard ", u"dÃ©cillion ", u"dÃ©cilliard ", u"unodÃ©cillion ", u"unodÃ©cilliard ", u"duodÃ©cillion ", u"duodÃ©cilliard "]

    #quickly manage if n is < 10
    if n < 10:
        ones = [u'zéro', "un ","deux ","trois ","quatre ", "cinq ", "six ","sept ","huit ","neuf "]
        return ones[n]

    # break the number into groups of 3 digits using slicing
    # each group representing hundred, thousand, million, billion, ...
    n3 = []
    r1 = ""
    # create numeric string
    ns = str(n)
    for k in range(3, 33, 3):
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

    r1 = r

    #print n3 # test
    # break each group of 3 digits into
    # ones, tens/twenties, hundreds
    # and form a string
    nw = ""
    for i, x in enumerate(n3):
        b1 = x % 10
        b2 = (x % 100)//10
        b3 = (x % 1000)//100
        #print b1, b2, b3 # test
        if x == 0:
            continue # skip
        else:
            t = thousands[i]
        if b2 == 0:
            #cas du 'mille' qui n'est pas 'un mille'
            if b1 == 1 and i == 1:
                nw = t + nw
            else:
                nw = ones[b1] + t + nw
        elif b2 == 1:
            nw = tens[b1] + t + nw
        elif b2 > 1:
            extra = ""
            if b1==1:
                nw = twenties[b2] + "et un " + t + nw
            elif b1>1:
                nw = twenties[b2][:-1] + "-" + ones[b1] + t + nw
            else:
                nw = twenties[b2] + extra + ones[b1] + t + nw
        if b3 > 0:
            if b3>1:
                nw = ones[b3] + "cent " + nw
            else:
                nw = "cent " + nw
    return nw.strip()
