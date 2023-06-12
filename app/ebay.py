import pandas as pd
from PIL import Image
import requests
from io import BytesIO
from datetime import timedelta
from datetime import datetime
from ebaysdk.finding import Connection

api = Connection(config_file='/home/willacya/microblog-0.13/app/ebay.yaml', siteid="EBAY-GB", proxy_port=3128, proxy_host='proxy.server')

def add_zero(n):
    if len(str(n)) == 1:
        return '0' + str(n)
    return str(n)

def get_thumbnail(url):
    req = requests.get(url)
    img = Image.open(BytesIO(req.content))
    img.thumbnail((150, 150), Image.LANCZOS)
    return img

def image_formatter(im):
    return f'<img src="{im}">'

def make_clickable(val):
    return '<a href="{}">{}</a>'.format(val.Link,val.Title)

def subject_line(r):
    r

    if len(r) == 1:
        return r[0]['keywords']
    elif len(r) == 2:
        return r[0]['keywords'] + " and " + r[1]['keywords']
    else:
        return "".join([i['keywords'] + ", " for i in r[:-1]]) + "and " + r[-1]['keywords']

def format_time(time):
    time -= timedelta(hours=-1)
    suffix = 'th' if 11<=time.day<=13 else {1:'st',2:'nd',3:'rd'}.get(time.day%10, 'th')
    return time.strftime('%a {S} at %X').replace('{S}', str(time.day) + suffix)

def ebay_results(keyword):

    num_days = 2
    x = datetime.now() + timedelta(days=num_days)
    endDate = x.strftime('%Y-%m-%d') + 'T00:00:00.000Z'

    request = {
                'keywords': keyword.keyword,
                'itemFilter': [
                    {'name':'LocatedIn','value': 'GB'},
                    {'name':'EndTimeTo','value': endDate},
                    {'name':'ListingType','value':['Auction','AuctionWithBIN']},
                    {'name': 'HideDuplicateItems', 'value':'true'},
                    {'name': 'MinPrice', 'value':keyword.minAmount},
                    {'name': 'MaxPrice', 'value':keyword.maxAmount},
                ],

                'sortOrder': 'PricePlusShippingLowest'

                }

    titles = []
    prices = []
    images = []
    links = []
    endings = []

    keywords = []


    response = api.execute('findItemsByKeywords', request)
    try:
        if response.reply.searchResult._count != '0':

            for i in response.reply.searchResult.item:
                keywords.append(request['keywords'])
                titles.append(i.title)
                prices.append(str(float(i.sellingStatus.currentPrice.value) + float(i.shippingInfo.shippingServiceCost.value)))

                try:
                    images.append(i.galleryURL)
                except:
                    images.append("https://secureir.ebaystatic.com/pictures/aw/pics/stockimage1.jpg")

                links.append(i.viewItemURL)
                endings.append(format_time(i.listingInfo.endTime))

        listing = pd.DataFrame({'Keywords':keywords,
                                'Title':titles,
                                'Price':prices,
                                'Image':images,
                                'Link':links,
                                'Ending':endings})

        listing['Title'] = ['<a href="{}">{}</a>'.format(j, i) for i, j in zip(listing.Title,listing.Link)]
        listing['Price'] = listing['Price'].map(lambda x: f'£{float(x):.2f}')
        listing = listing.sort_values(by=['Keywords','Ending']).reset_index()
        listing['Details'] = (listing.index + 1).astype(str) + ". " + listing['Title']  + "<br><br>" + listing['Ending'] + "<br><br>" + "<b>" + listing['Price'] + "</b>"

        if len(listing) == 0:
            listing == ""
        else:
            listing = listing[['Image','Details']].to_html(formatters={'Image': image_formatter,},
                                                 index=False, header=False, border=0, escape=False)
        return listing
    except AttributeError:
        return ""




