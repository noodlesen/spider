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
    today = datetime.today()
    last = today - timedelta(d)
    db.engine.execute(""" DELETE FROM bid WHERE found_at<'%s' """ % last)
    db.engine.execute(""" DELETE FROM bid WHERE departure_date<='%s' """ % today)
    db.engine.execute(""" DELETE FROM bid WHERE departure_date=return_date """)

#=======================
def request_destination(destination, start_dt, check_time=True):
    bid_cleanup(2)
    #destination = destinations[randint(0, len(destinations)-1)]
    print()
    print(datetime.utcnow())
    print ('REQUESTING %s' % destination[0])
    #-----------------------------------------

    allowed=False
    stat = DestinationStats.query.filter_by(code=destination[1]).first()
    if not stat:
        print("stat not exists")
        stat = DestinationStats()
        stat.code = destination[1]
        stat.total_bid_count = 0
        stat.avg_price = 0
        stat.results_count = 0
        allowed = True

    else:
        print("stat exists")
        days_to_last_request = (datetime.utcnow()-stat.requested_at).days
        if stat.results_count==0:
            print("no results last time")
            allowed = chances(10)
            print("allowed ", allowed)
        elif days_to_last_request >= 1:
            print ('Last request is older than 24h - %d OK' % days_to_last_request)
            allowed=True

        else:
            if check_time:
                print ('Too early for this request - next time', days_to_last_request)
            else:
                allowed = True



    sum_price = 0
    sum_bids = 0


    if allowed:

        print("proceed...")

        stat.requested_at = datetime.utcnow()

        #====
        month_bids = get_month_bids({"beginning_of_period": start_dt.strftime('%Y-%m-%d'), "destination": destination[1], "origin":"MOW" })
        #====



        dest_name = destination[0]
        score = destination[3]
        i=0
        bids_count = len(month_bids['data'])

        stat.results_count = bids_count


        for b in month_bids['data']:
            destination = b['destination']
            found_at = datetime.strptime( ':'.join(b['found_at'].split(':')[:-1])+'00', '%Y-%m-%dT%H:%M:%S%z')
            departure_date = datetime.strptime( b['depart_date'],'%Y-%m-%d')
            price = b['value']

            # check if the bid is unique
            snapshot = get_hash(destination+str(price)+str(departure_date))
            snap_count = len(list(db.engine.execute("""SELECT id FROM bid WHERE snapshot="%s" """ % snapshot)))
            print("snapcount "+str(snap_count))

            if snap_count ==0:

                print (destination, price)
                bid = Bid()
                bid.origin = b['origin']
                bid.destination = destination
                bid.dest_name = dest_name.upper()
                bid.one_way = month_bids['params']['one_way']
                bid.price = price
                sum_price += price
                sum_bids += 1
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
                rating = int(bid.distance/bid.price*1000*k/(bid.stops+1)+score/10)-days_to-2**i if i<=10 else 0
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
                bid.to_expose = True if i==0 else False
                print(bid.found_at)

                db.session.add(bid)
                db.session.commit()

            i+=1

    new_bid_count = stat.total_bid_count+sum_bids
    if new_bid_count >0:
        stat.avg_price= int((stat.avg_price*stat.total_bid_count+sum_price)/new_bid_count)
        stat.total_bid_count=new_bid_count

    db.session.add(stat)
    db.session.commit()

    return (stat)


