import re

r = re.compile

spamlist_names = [
    r('classifieds', re.I),
    r('credit card', re.I),
    r('austin home', re.I),
    r('noah theme', re.I),
    r('cash loan', re.I),
    r('payday loan', re.I),
    r('silver price', re.I),
    r('ed hardy', re.I),
    r('florida.*fishing', re.I),
    r('fishing.*florida', re.I),
    r('real estate', re.I),
    r('free dating', re.I),
    r('countertop', re.I),
    r('solar panel', re.I),
    r('dentists', re.I),
    r('.+dentist', re.I),
    r('dental clinic', re.I),
    r('locksmith in', re.I),
    r('buy.*online', re.I),
    r('coupons', re.I),
    r('self diagnosis', re.I),
    r('handicapped vans', re.I),
    r('hotel finder', re.I),
    r('horoscope', re.I),
    r('garmin.*forerunner', re.I),
    r('replica purses', re.I),
    r('replica purses', re.I),
    r('cheap.*insurance', re.I),
    r('mobile.*review', re.I),
    r('.+app?artment', re.I),
    r('refurbished.+', re.I),
    r('water damage', re.I),
    r('fire damage', re.I),
    r('fire damage', re.I),
    r('.+ seo', re.I),
    r('light bulb', re.I),
    r('.+ tour', re.I),
    r('surgery', re.I),
    r('.+ restoration', re.I),
    r('cleaning service', re.I),
    r('vibrator', re.I),
    r('male.+pills', re.I),
    r('seo .+', re.I),
    r('.+ lawyer', re.I),
    r('flat stomach', re.I),
    r('weight loss', re.I),
    r('angle grinder', re.I),
    r('janetcmr', re.I),
    r('steamfast sf-407', re.I),
    r('du ventre', re.I)
]

spamlist_urls = [
    r('cancer', re.I),
    r('du-?ventre', re.I),
]

spamlist_comments = [
    r('cash loan', re.I)
]

