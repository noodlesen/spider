from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from spider import app, bid_feed
from spider.db import db
from spider.requester import request_destination, expose
from time import sleep
from random import randint
from datetime import datetime
from spider.logger import Log
from math import floor
from spider.toolbox import get_hash
from spider.raccoon import lookup

from spider.mandrill import send_prices_email, send_confirmation_email

manager = Manager(app)


def plus_month(dt, n):
    sm = dt.month+n
    if sm > 12:
        nm = sm % 12
        ny = dt.year+1+floor(n/12)
        return dt.replace(month = nm, year = ny)
    else:
        return dt.replace(month = sm)

today = datetime.utcnow()
this_month_start = today.replace(day=1).date()
this_month = this_month_start.month
next_month_start = plus_month(this_month_start,1)
after_next_month_start = plus_month(this_month_start,2)



@manager.command
def preload():
    destinations = [p for p in db.engine.execute("""SELECT name, code, country, score FROM destination""")]
    n=0
    while n<200:
        #random_request( destinations)
        destination = destinations[randint(0, len(destinations)-1)]

        print()
        print('THIS')
        request_destination(destination, this_month_start)
        print ('SLEEPING', 3)
        sleep(3)

        print()
        print('NEXT')
        request_destination(destination, next_month_start, False)
        print ('SLEEPING', 3)
        sleep(3)

        print()
        print('AFTER')
        request_destination(destination, after_next_month_start, False)
        print ('SLEEPING', 3)
        sleep(3)

        # stat.requested_at = datetime.utcnow()
        # db.session.add(stat)
        # db.session.commit()
        n+=1

    expose(50, 1)

@manager.command
def scheduled():
    msg = "scheduled. ran at "+datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S%z')
    print(msg)
    #Log.register(data=msg)


@manager.command
def test_mandrill():
    send_confirmation_email(bid_feed(), "fcb2ce1ebdccf90be8056a33101754c1")


@manager.command
def test_expose():
    expose(50, 1)

@manager.command
def make_hash():
    subs = list(db.engine.execute("""SELECT id, marker FROM subscribers"""))
    for s in subs:
        hsh = get_hash(s[1])
        db.engine.execute("""UPDATE subscribers SET hash="%s" WHERE id=%d """ % (hsh, s[0]))

@manager.command
def raccoon():
    lookup(destinations=['VRN'], maxprice=10000)


migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()