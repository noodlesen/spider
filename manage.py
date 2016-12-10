from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from spider import app
from spider.db import db
from spider.requester import random_request
from time import sleep
from random import randint
from datetime import datetime
from spider.logger import Log

manager = Manager(app)




@manager.command
def preload():
    destinations = [p for p in db.engine.execute("""SELECT name, code, country, score FROM destination""")]
    n=0
    while n<10:
        random_request( destinations)
        print ('SLEEPING', 3)
        sleep(3)
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