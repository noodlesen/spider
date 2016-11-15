from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from spider import app
from spider.db import db
from spider.requester import random_request
from time import sleep
from random import randint

manager = Manager(app)




@manager.command
def preload():
    #origins = [p[1] for p in db.engine.execute("""SELECT name, code, country FROM prefered_airports WHERE origin=1""")]
    destinations = [p for p in db.engine.execute("""SELECT name, code, country, number FROM destination""")]
    #destinations = ['SIN']
    while True:
        random_request( destinations)
        t = randint(2,10)
        print ('SLEEPING', t)
        sleep(t)


migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()