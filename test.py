import pandas as pd
from PIL import Image
import requests
from io import BytesIO
from datetime import timedelta
from datetime import datetime
from ebaysdk.finding import Connection
from app.models import User, Ebay
from app.email import send_ebay_results
import numpy as np
from misspellings import split_misspelled_keywords

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

def get_drive_time(apiKey, origin, destination):

    url = ('https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins={}&destinations={}&key={}'
           .format(origin.replace(' ','+'),
                   destination.replace(' ','+'),
                   apiKey
                  )
          )

    response = requests.get(url)
    resp_json_payload = response.json()
    drive_time = resp_json_payload['rows'][0]['elements'][0]['duration']['value']/60

    return drive_time

def driving_time(x):
    if x< 60:
        return str(int(round(x,0))) + " mins away."
    else:
        return str(int(x/60)) + " hr " + str(int(x%60)) + " mins away."

apiKey = 'AIzaSyBbxKRbmdMkeBh2FOkbH5QW3IFTTrmg3IY'

def ebay_results(misspelling, keyword):

    origin = keyword.location


    deadline = 48*60 # 2 days of results


    endDate = (datetime.utcnow() + timedelta(minutes=deadline)).isoformat()

    titles = []
    prices = []
    images = []
    links = []
    endings = []
    driveTime = []
    pickupOnly = []
    keywords = []

    for miss in misspelling:
        request = {
                    'keywords': miss,
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




        response = api.execute('findItemsByKeywords', request)

        if response.reply.searchResult._count != '0' and int(response.reply.searchResult._count) < 10:

            for i in response.reply.searchResult.item:
                keywords.append(request['keywords'])
                titles.append(i.title)
                prices.append(str(float(i.sellingStatus.currentPrice.value) + float(i.shippingInfo.shippingServiceCost.value)))

                if i.shippingInfo.shippingType == 'FreePickup':
                    try:
                        driveTime.append(get_drive_time(apiKey, origin, i.postalCode))
                        pickupOnly.append(1)
                    except:
                        try:
                            driveTime.append(get_drive_time(apiKey, origin, i.location))
                            pickupOnly.append(1)
                        except:
                            driveTime.append(0.0)
                            pickupOnly.append(2) # Couldn't calulcate pickup time
                else:
                    driveTime.append(0.0)
                    pickupOnly.append(0)

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
                            'DrivingTime':driveTime,
                            'PickupOnly':pickupOnly,
                            'Link':links,
                            'Ending':endings,
                            'test':test})

    if keyword.driveTime != None:
        listing = listing[listing.DrivingTime <= float(keyword.driveTime)*60]
    listing = listing[listing.Price.astype('float64') <= keyword.maxAmount].reset_index()
    listing['Title'] = ['<a href="{}">{}</a>'.format(j, i) for i, j in zip(listing.Title,listing.Link)]
    listing['Price'] = listing['Price'].map(lambda x: f'£{float(x):.2f}')
    listing = listing.sort_values(by=['Keywords','Ending']).reset_index()
    listing['Details'] = (listing.index + 1).astype(str) + ". " + listing['Title']  + "<br><br>" + listing['Ending'] + "<br><br>" + "<b>" + listing['Price'] + "</b>"
    listing['Details'] = np.where(listing.PickupOnly == 1, listing['Details'] + " (collection only)<br>" + listing['DrivingTime'].apply(driving_time), listing['Details'])
    listing['Details'] = np.where(listing.PickupOnly == 2, listing['Details'] + " (collection only)", listing['Details'])


    df_length = len(listing)
    if len(listing) == 0:
        listing == ""
    else:
        listing = listing[['Image','Details']].to_html(formatters={'Image': image_formatter,},
                                             index=False, header=False, border=0, escape=False)






    return listing, df_length



users = User.query.all()
for user in users:
    keywords = Ebay.query.filter_by(user_id = user.id).order_by(Ebay.id.desc()).all()
    noneFound = []
    html = ""
    total = 0
    no_items = 0
    for keyword in keywords:
        words = keyword.keyword.lower()
        if len(words) > 8:
            misspelling = split_misspelled_keywords(words)
            total += 1
            listings, df_length = ebay_results(misspelling, keyword)
            no_items += df_length
            if len(listings) < 1:
                noneFound.append(keyword.keyword + "<br>")
            else:
                html += "<h2>" + keyword.keyword + "</h2>" + listings + "<br><br>"
    #html += "<h2>No listings for the following items</h2><br>" + "".join(noneFound)
    subject = str(no_items) + " Possible Misspelled Items on Ebay!" if no_items >1 else str(no_items) + " Possible Misspelled Item on Ebay!"
    if len(noneFound) != total:
        send_ebay_results(user, html, subject)