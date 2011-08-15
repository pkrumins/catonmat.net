import re

r = re.compile

spamlist_names = [
    r('classifieds', re.I),
    r('credit card', re.I),
    r('austin home', re.I),
    r('noah theme', re.I),
    r('cash loans', re.I),
    r('silver price', re.I),
    r('ed hardy', re.I),
    r('florida.*fishing', re.I),
    r('fishing.*florida', re.I),
    r('real estate', re.I),
    r('free dating', re.I),
    r('countertop', re.I),
    r('solar panel', re.I)
]

spamlist_urls = [
    r('cancer', re.I)
]

