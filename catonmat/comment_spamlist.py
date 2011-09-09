import re

r = re.compile

spamlist_names = [
    r('classifieds', re.I),
    r('credit card', re.I),
    r('austin home', re.I),
    r('noah theme', re.I),
    r('cash loan', re.I),
    r('cash.*loan', re.I),
    r('advance loan', re.I),
    r('payday loan', re.I),
    r('silver price', re.I),
    r('ed hardy', re.I),
    r('florida.*fishing', re.I),
    r('fishing.*florida', re.I),
    r('real estate', re.I),
    r('free dating', re.I),
    r('dating site', re.I),
    r('dating website', re.I),
    r('countertop', re.I),
    r('solar panel', re.I),
    r('dentists', re.I),
    r('.+dentist', re.I),
    r('dental clinic', re.I),
    r('clinical ', re.I),
    r('locksmith in', re.I),
    r('buy.*online', re.I),
    r('coupons', re.I),
    r('discount.*coupon', re.I),
    r('self diagnosis', re.I),
    r('handicapped vans', re.I),
    r('hotel finder', re.I),
    r('cheap hotel', re.I),
    r('cheap business', re.I),
    r('lawsuit', re.I),
    r('horoscope', re.I),
    r('garmin.*forerunner', re.I),
    r('replica purses', re.I),
    r('cheap.*insurance', re.I),
    r('mobile.*review', re.I),
    r('.+app?artment', re.I),
    r('refurbished.+', re.I),
    r('water damage', re.I),
    r('fire damage', re.I),
    r('.+ seo', re.I),
    r('light bulb', re.I),
    r('.+ tour', re.I),
    r('surgery', re.I),
    r('.+ restoration', re.I),
    r('cleaning service', re.I),
    r('house clean', re.I),
    r('vibrator', re.I),
    r('male.+pills', re.I),
    r('seo .+', re.I),
    r('.+ lawyer', re.I),
    r('flat stomach', re.I),
    r('weight loss', re.I),
    r('angle grinder', re.I),
    r('janetcmr', re.I),
    r('steamfast sf-407', re.I),
    r('du ventre', re.I),
    r('iphone', re.I),
    r('antivirus', re.I),
    r('mortgage', re.I),
    r('windows.*key', re.I),
    r('office.*key', re.I),
    r('louis.*vuitton', re.I),
    r('land for sale', re.I),
    r('suspension training', re.I),
    r('artificial turf', re.I),
    r('make money', re.I),
    r('money online', re.I),
    r('beauty business', re.I),
    r('cheap.+ticket', re.I),
    r('hair loss', re.I),
    r('fasciitis', re.I),
    r('abuse', re.I),
    r('finance professional', re.I),
    r('slot machine', re.I),
    r('addiction', re.I),
    r('fall in love', re.I),
    r('classified ads', re.I),
    r('^seo$', re.I),
    r('rapidement', re.I),
    r('gratuitement', re.I),
    r('transpiration', re.I),
    r('maigrir', re.I),
    r('mobile.+app', re.I),
    r('^cash$', re.I),
    r('habitat restore', re.I),
    r('android developer', re.I),
    r('web.*software', re.I),
    r('laptops', re.I),
    r(' advertising', re.I),
    r('voisine', re.I),
    r('cartomancie', re.I),
    r(' amour', re.I),
    r('crash course', re.I),
    r('hospital', re.I),
    r('poop bag', re.I),
    r('internet marketing', re.I),
    r('project management', re.I),
    r(' services', re.I),
    r('nauka angielskiego', re.I),
    r('^loans?$', re.I),
    r('jobs? in ', re.I),
    r('bipolar test', re.I),
    r('mincir', re.I),
    r('adopting ', re.I),
    r('travail', re.I),
    r('custom.*builder', re.I),
    r('air condition', re.I),
    r('klima servisi', re.I),
    r('last minute', re.I),
    r('zeiterfassung', re.I),
    r('spraytan', re.I),
    r(' girls', re.I),
    r('mold ', re.I),
    r('remediation', re.I),
    r('barbecue', re.I),
    r('new jersey', re.I),
    r('minivan', re.I),
    r('handicap', re.I),
    r('used ', re.I),
    r('magic mesh', re.I),
    r('forex', re.I),
    r('iit exam', re.I),
    r('garagedoor', re.I),
    r('garage door', re.I),
    r('swing set', re.I),
    r('designer cloth', re.I),
    r('it health', re.I),
    r('healthcare', re.I),
    r('fiance visa', re.I),
    r('for sale', re.I),
    r('linoleum', re.I),
    r('essay editor', re.I),
    r('professional.*editor', re.I),
    r('tailor.*shirt', re.I),
    r('divorce attorney', re.I),
    r(' dating', re.I),
    r('dating ', re.I),
    r('^dating$', re.I),
    r('financing', re.I),
    r('restaurant ', re.I),
    r('adoption', re.I),
    r('adoptive', re.I),
    r('article submission', re.I),
    r('ultrasound ', re.I),
    r('hypnoteraphy', re.I),
    r('mobile signal', re.I),
    r('signal booster', re.I),
    r('party suppl', re.I),
    r('vergleich', re.I),
    r('buy ', re.I),
    r('twitter ', re.I),
    r('football pick', re.I),
    r('net branch', re.I),
    r('tax attorney', re.I),
    r('ugg boot', re.I),
    r('nurse qualification', re.I),
    r('car transport', re.I),
    r('prank call', re.I),
    r('web design', re.I),
    r('scuba diving', re.I),
    r('spas in', re.I),
    r('thailand ', re.I),
    r('retirement', re.I),
    r('scratchcard', re.I),
    r('scratch card', re.I),
    r('satchel handbag', re.I),
    r('leather ', re.I),
    r('for women', re.I),
    r('for woman', re.I),
    r(' vacation', re.I),
    r('vacation ', re.I),
    r('video poker', re.I),
    r('couch surf', re.I),
    r(' knives', re.I),
    r('family vacation', re.I),
    r('family issues', re.I),
    r('fake.*watch', re.I),
    r('flex duct', re.I),
    r('house paint', re.I),
    r('article directory', re.I),
    r('viagra', re.I),
    r(' attorney', re.I),
    r('attorney ', re.I),
    r('^attorney$', re.I),
    r('chinese herb', re.I),
    r('fertality', re.I),
    r(' earring', re.I),
    r('^earring$', re.I),
    r('law enforcement', re.I),
    r('training online', re.I),
    r(' online', re.I),
    r(' massage', re.I),
    r('massage ', re.I),
    r('^massage$', re.I),
    r('hair removal', re.I),
    r('chanel bag', re.I),
    r('chanel ', re.I),
    r('trench coat', re.I),
    r('credit report', re.I),
    r('stem cell', re.I),
    r('personal statement', re.I),
    r('ultra sound', re.I),
    r('resume writing', re.I),
    r('glass pool', re.I),
    r('moncler.*jacket', re.I),
    r('button triplet', re.I),
    r('love music', re.I),
    r('cheap jordans', re.I),
    r('astrologie', re.I),
    r('natural vitamin', re.I),
    r('vitamins? supplement', re.I),
    r('^cheap ', re.I),
    r('fabric blinds', re.I),
    r('wedding dress', re.I),
    r('bingoonline', re.I),
    r('spyware removal', re.I),
    r('income plan', re.I),
    r(' workout', re.I),
    r(' printing', re.I),
    r('bankruptcy', re.I),
    r('music video', re.I),
    r('wind shield', re.I),
    r('auto transport', re.I),
    r('sunglasses', re.I),
    r('business card', re.I),
    r('colon cleanse', re.I),
    r(' cleanse', re.I),
    r('herbal product', re.I),
    r('^webhosting$', re.I),
    r('hosting review', re.I),
    r('telefonsex', re.I),
    r('natural health', re.I),
    r('health product', re.I),
    r('couples counsel', re.I),
    r(' hotels? ', re.I),
    r('driving instructor', re.I),
    r('halloween ', re.I),
    r('justin bieber', re.I),
    r('car insurance', re.I),
    r(' insurance', re.I),
    r('ex boyfriend', re.I),
    r('hemorrhoid', re.I),
    r('penny auction', re.I),
    r('free sms', re.I),
    r('love sms', re.I),
    r('funny sms', re.I),
    r('birthday sms', re.I),
    r('floor sanding', re.I),
    r('tongue piercing', re.I),
    r('^psychologist$', re.I),
    r('bin cabinet', re.I),
    r('bin shelving', re.I),
    r('droid accesor', re.I),
    r('wholesale', re.I),
    r('lingerie', re.I),
    r('assignment help', re.I),
    r('wedding', re.I),
    r('domain price', re.I),
    r('belly fat', re.I),
    r(' symptoms', re.I),
    r('research paper', re.I),
    r(' betting', re.I),
    r(' facts', re.I),
    r('nike.*sale', re.I),
    r('cigarette ', re.I),
    r('cigars ', re.I),
    r('affiliate program', re.I),
    r('cosmetology', re.I),
    r('personal trainer', re.I),
    r('commercial cleaning', re.I),
    r('cholesterol', re.I),
    r('^funny ', re.I),
    r('coach bag', re.I),
    r('brand bag', re.I),
    r('^bags$', re.I),
    r('timberland', re.I),
    r(' boots', re.I),
    r('baby contest', re.I),
    r('flirten', re.I),
    r('fashion ', re.I),
    r(' glasses', re.I),
    r('eyeglass', re.I),
    r('grow taller', re.I),
    r('nursing shoe', re.I),
    r('hair extension', re.I),
    r('flatter stomach', re.I),
    r('love quote', re.I),
    r('menopause', re.I),
    r('driving lesson', re.I),
    r('article director', re.I),
    r('^oakley$', re.I),
    r('bag wholesale', re.I),
    r('wholesale', re.I),
    r('bottom shoes', re.I),
    r('sexy.*costume', re.I),
    r('dog obedience', re.I),
    r('gorilla safari', re.I),
    r('weightloss', re.I),
    r('internet wiki', re.I),
    r('du sommeil', re.I),
    r('barcode', re.I),
    r(' software', re.I),
]

spamlist_emails = [
    r('cancer', re.I),
    r('angelmike', re.I),
]

spamlist_urls = [
    r('cancer', re.I),
    r('du-?ventre', re.I),
    r('xrumer.+service', re.I),
    r('cheap-', re.I),
    r('discount.*coupon', re.I),
    r('wedding', re.I),
    r('abuse', re.I),
    r('addiction', re.I),
    r('android-developer.in', re.I),
    r('android-app', re.I),
    r('itunes.apple.com', re.I),
    r('telefon-sex', re.I),
    r('longchamp', re.I),
    r('slotmachine', re.I),
    r('gambling', re.I),
    r('deals.co', re.I),
    r('tripploans.com', re.I),
    r('kredit.com', re.I),
    r('phonecharger', re.I),
    r('footballpicks', re.I),
    r('divorceattorney', re.I),
    r('asiadate', re.I),
    r('freemoney', re.I),
    r('vacation-network', re.I),
    r('casino', re.I),
    r('moncler', re.I),
    r('astrologie', re.I),
]

spamlist_comments = [
    r('cash loan', re.I),
    r('payday loan', re.I),
    r('>loan<', re.I),
    r('tripploans.com', re.I),
    r('natural remed(y|ies)', re.I),
    r('acid reflux', re.I),
    r('unlock iphone', re.I),
    r('real estate', re.I),
    r('live sport', re.I),
    r('fasciitis exercise', re.I),
    r('foreclosure', re.I),
    r('house cleaning', re.I),
    r('quotes about life', re.I),
    r('creatine supplement', re.I),
    r('outlook time tracking', re.I),
    r('bukmacherskie', re.I),
    r('shoes outlet', re.I),
    r('cheap hotel', re.I),
    r('saint laurent', re.I),
    r('vacation network', re.I),
    r('cheap.*shoes', re.I),
    r('cheap.*air.*max', re.I),
    r('nike-outlet', re.I),
    r('discount.*shoes', re.I),
    r('nauka angiel', re.I),
    r('credit score', re.I),
    r('boat loan', re.I),
    r('car loan', re.I),
    r('house loan', re.I),
    r('apartment loan', re.I),
    r('dental insurance', re.I),
    r('cheap.*insurance', re.I),
    r('auto insurance', re.I),
    r('car insurance', re.I),
    r('rwanda safaris', re.I),
    r('free iphone', re.I),
    r('iphone deal', re.I),
    r('drudge report', re.I),
    r('hurricane.com', re.I),
    r('slot machine', re.I),
    r('printable coupon', re.I),
    r('tax attorney', re.I),
    r('>last minute', re.I),
    r('laptisor.*vanzare', re.I),
    r('>.*?dentist<', re.I),
    r('>.*?accomodation<', re.I),
    r('>debit card<', re.I),
    r('>credit card<', re.I),
    r('thyroid symptoms', re.I),
    r('angina symptoms', re.I),
    r('morning sickness', re.I),
    r('sickness remed(y|ies)', re.I),
    r('ex-?boyfriend', re.I),
    r('ex-?girlfriend', re.I),
    r('induce labor', re.I),
    r('knee pain', re.I),
    r('pain running', re.I),
    r('penisforstoring', re.I),
    r('>water colors', re.I),
    r('>mortgage ', re.I),
    r('>pandora ', re.I),
    r('term papers?<', re.I),
    r('finance<', re.I),
    r('buy.*toaster', re.I),
    r('football picks<', re.I),
    r('finance degrees?<', re.I),
    r('air.jordan', re.I),
    r('grout strain', re.I),
    r('acne treatment', re.I),
    r('zeanballonline.com', re.I),
    r('louis vuitton', re.I),
    r('home furniture', re.I),
    r('dog trainer', re.I),
    r('xanax abuse', re.I),
    r('toronto limo', re.I),
]

