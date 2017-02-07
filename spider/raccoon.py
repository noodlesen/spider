from .models import Bid
from .db import db

#dest, slud, flud, mindur, maxdur, minprice, maxprice, minstops, maxstops
def lookup(**kwargs):

    query="""SELECT * FROM bid """
    q = []

    if "destinations" in kwargs:
        q.append(" destination IN (%s)" % ", ".join(["'"+d+"'" for d in kwargs['destinations']]))

    if "maxprice" in kwargs:
        q.append(" price <= %d" % kwargs['maxprice'])

    if "maxstops" in kwargs:
        q.append(" stops <= %d" % kwargs['maxstops'])

    if "minstops" in kwargs:
        q.append(" stops >= %d" % kwargs['minstops'])

    if len(q)>0:
        query+="WHERE "+" AND ".join(q)

    print (query)

    res = list(db.engine.execute(query))
    for r in res:
        print(r)




