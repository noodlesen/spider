from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from spider import app
from spider.db import db
from spider.requester import request_destination
from time import sleep
from random import randint
from datetime import datetime
from spider.logger import Log
from math import floor

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
        request_destination(destination, next_month_start)
        print ('SLEEPING', 3)
        sleep(3)

        print()
        print('AFTER')
        stat = request_destination(destination, after_next_month_start)
        print ('SLEEPING', 3)
        sleep(3)
        
        stat.requested_at = datetime.utcnow()
        db.session.add(stat)
        db.session.commit()
        n+=1

@manager.command
def scheduled():
    msg = "scheduled. ran at "+datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S%z')
    print(msg)
    #Log.register(data=msg)


migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()