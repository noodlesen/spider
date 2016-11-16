from .db import db

class UserQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer)
    max_stops = db.Column(db.Integer)
    query_type = db.Column(db.String(1))
    search_date_in = db.Column(db.DateTime)
    search_date_out = db.Column(db.DateTime)
    departure_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)
    departure_pm = db.Column(db.Integer)
    return_pm = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    origin = db.Column(db.String(3))
    destination = db.Column(db.String(3))
    one_way = db.Column(db.Boolean)
    trip_class = db.Column(db.Integer)
    price_limit = db.Column(db.Integer)
    price_unit = db.Column(db.String(1))
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)

class Ask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(20))
    origin = db.Column(db.String(3))
    destination = db.Column(db.String(3))
    search_date_in = db.Column(db.DateTime)
    one_way = db.Column(db.Boolean)
    expires_at = db.Column(db.DateTime)

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(3))
    destination = db.Column(db.String(3))
    dest_name = db.Column(db.String(35))
    one_way = db.Column(db.String(5))
    departure_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)
    found_at = db.Column(db.DateTime)
    price = db.Column(db.Integer)
    trip_class = db.Column(db.Integer)
    stops = db.Column(db.Integer)
    distance = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    exposed = db.Column(db.Boolean)
    snapshot = db.Column(db.String(50))
    to_expose = db.Column(db.Boolean)

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35))
    code = db.Column(db.String(3))
    country = db.Column(db.String(35))
    score = db.Column(db.Integer) 

class DestinationStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3))
    avg_price = db.Column(db.Integer)
    total_bid_count = db.Column(db.Integer, default=0)
    results_count = db.Column(db.Integer)
    requested_at = db.Column(db.DateTime)

    @staticmethod
    def last_request_time():
        last = list(db.engine.execute("""SELECT requested_at FROM destination_stats ORDER BY requested_at DESC LIMIT 1"""))[0][0]
        return last

# TEMP

    class AddAirport(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        iata = db.Column(db.String(3))
        city_code = db.Column(db.String(3))
        city = db.Column(db.String(50))
        country_code = db.Column(db.String(3))
        country = db.Column(db.String(50))






