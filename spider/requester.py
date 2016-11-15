import requests
import json
from datetime import datetime, timedelta
from random import randint

from .config import TRAVEL_PAYOUTS_TOKEN
from .models import Bid, DestinationStats
from .db import db

from .tpapi import get_month_bids
from .toolbox import get_hash, fib, chances

def bid_cleanup(d):
    last = datetime.today() - timedelta(d)
    db.engine.execute("""DELETE FROM bid WHERE found_at<'%s'""" % last)

#=======================
def random_request( destinations):
    bid_cleanup(2)
    destination = destinations[randint(0, len(destinations)-1)]
    print()
    print(datetime.utcnow())
    print ('REQUESTING %s' % destination[0])
    #-----------------------------------------

    allowed=False
    stat = DestinationStats.query.filter_by(code=destination[1]).first()
    if not stat:
        print("not exists")
        stat = DestinationStats()
        stat.code = destination[1]
        allowed = True
    else:
        print("exists")
        if stat.results_count==0:
            print("no results last time")
            allowed = chances(10)
            print("allowed ", allowed)

    stat.requested_at = datetime.utcnow()


    if allowed:

        print("proceed...")

        #====
        month_bids = get_month_bids({"beginning_of_period": "2016-12-01", "destination": destination[1], "origin":"MOW" })
        #====



        dest_name = destination[0]
        number = destination[3]
        i=0
        bids_count = len(month_bids['data'])

        stat.results_count = bids_count

        for b in month_bids['data']:
            destination = b['destination']
            found_at = datetime.strptime( ':'.join(b['found_at'].split(':')[:-1])+'00', '%Y-%m-%dT%H:%M:%S%z') 
            departure_date = datetime.strptime( b['depart_date'],'%Y-%m-%d')
            price = b['value']

            snapshot = get_hash(destination+str(price)+str(found_at)+str(departure_date))

            snap_count = len(list(db.engine.execute("""SELECT id FROM bid WHERE snapshot="%s" """ % snapshot)))
            print("snapcount "+str(snap_count))

            if snap_count ==0:

                #rint(b)
                print (destination, price)
                bid = Bid()
                bid.origin = b['origin']
                bid.destination = destination
                bid.dest_name = dest_name.upper()
                bid.one_way = month_bids['params']['one_way']
                bid.price = price
                bid.trip_class = b['trip_class']
                bid.stops = b['number_of_changes']
                bid.distance = b['distance']
                bid.departure_date = departure_date
                if 'return_date' in b.keys():
                    bid.return_date = datetime.strptime( b['return_date'], '%Y-%m-%d')

                bid.found_at = found_at 

                bid.snapshot = snapshot
                k = 2 if bid.one_way =="false" else 1
                now = datetime.now()
                td = bid.departure_date - now
                days_to = td.days
                rating = int(bid.distance/bid.price*1000*k/(bid.stops+1)+number/10)-days_to-2**i if i<=10 else 0
                lim_low = int(bid.distance/400)
                lim_high = int(bid.distance/200)
                dur = (bid.return_date - bid.departure_date).days
                pen_days=0
                if dur > lim_high:
                    pen_days = dur-lim_high
                elif dur<lim_low:
                    pen_days=lim_low-dur
                rating-=pen_days*5
                bid.rating = rating
                bid.to_expose = True if i<=5 else False
                print(bid.found_at)

                db.session.add(bid)
                db.session.commit()

                i+=1

    db.session.add(stat)
    db.session.commit()


