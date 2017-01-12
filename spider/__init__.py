import warnings
from flask.exthook import ExtDeprecationWarning

warnings.simplefilter('ignore', ExtDeprecationWarning)


from flask import Flask, request, session, render_template, url_for, make_response
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf.csrf import CsrfProtect
import json
from datetime import datetime, timedelta


from .cache import cache
from .db import db
from .config import DEBUG, SECRET_KEY, DBURI, MAINTENANCE, PROJECT_NAME, MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USE_SSL, MAIL_USERNAME, MAIL_PASSWORD, ALLOW_ROBOTS
from .logger import Log

from .models import Bid, Ask, UserQuery, DestinationStats

#from .requester import random_request

from .toolbox import russian_plurals, get_hash


app = Flask(__name__)



app.debug = DEBUG

app.config['PROJECT_NAME']=PROJECT_NAME
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DBURI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_POOL_RECYCLE'] = 60
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
app.config['BOOTSTRAP_SERVE_LOCAL']=True
app.config['CACHE_TYPE']='simple'
app.config['EMAIL_HOST']= MAIL_SERVER
app.config['EMAIL_PORT']= MAIL_PORT
app.config['EMAIL_HOST_USER']= MAIL_USERNAME
app.config['EMAIL_HOST_PASSWORD']= MAIL_PASSWORD
app.config['EMAIL_USE_SSL']= MAIL_USE_SSL
app.config['EMAIL_USE_TLS']= MAIL_USE_TLS

app.config['WTF_CSRF_TIME_LIMIT'] = 36000

cache.init_app(app)

toolbar = DebugToolbarExtension(app)

csrf = CsrfProtect(app)

db.init_app(app)

bootstrap = Bootstrap(app)


lm = LoginManager(app)
lm.login_view = 'social.login'

@app.context_processor
def set_global_mode():
    return {'debug_mode': DEBUG}


@lm.user_loader
def load_user(id):
    if id:
        return User.query.get(id)
    else:
        return None

@app.before_request
def make_session_permanent():
    session.permanent = True


@app.before_request
def check_for_maintenance():
    if MAINTENANCE and request.path != url_for('maintenance') and not 'static' in request.path:
        return redirect(url_for('maintenance'))

@app.route('/maintenance')
def maintenance():
    if MAINTENANCE:
        return render_template('maintenance.html')
    else:
        return redirect(url_for('root'))

@app.route('/robots.txt')
def robots():
    if not ALLOW_ROBOTS:
        return ("User-agent: *\nDisallow: /")
    else:
        return ("User-agent: *\nDisallow:")



@app.route('/')
def root():
    Log.register(action='route:root')
    return render_template('main.html')

@app.route('/bid-feed', methods = ['POST'])
def bid_feed():
    res = {'success': True, 'bids': []}

    #move to toolbox
    fields = ['destination', 'departure_date', 'return_date', 'price', 'rating', 'dest_name', 'stops', 'found_at']
    bids = list(db.engine.execute(""" SELECT b.%s, s.avg_price FROM bid as b JOIN destination_stats as s ON b.destination=s.code WHERE to_expose=1 ORDER BY rating DESC LIMIT 50""" % ', b.'.join(fields)))
    for b in bids:
        nb = {}
        i=0
        for f in fields:

            if isinstance(b[i], datetime):
                bf = datetime.strftime(b[i], '%b %d')
                if f=='departure_date':
                    dd_url = datetime.strftime(b[i], '%Y-%m-%d')
                if f=='return_date':
                    rd_url = datetime.strftime(b[i], '%Y-%m-%d')
            else:
                bf = b[i]

            if f=='stops':
                if b[i]==0:
                    bf="ПРЯМОЙ"
                elif b[i]==1:
                    bf="1 СТОП"
                elif b[i]==2:
                    bf="2 СТОПА"

            nb[f]=bf
            i+=1

        nb['age']=(b['found_at']-datetime.utcnow()).seconds
        if nb['age']<3*3600:
            nb['age_color']='#00ff00'
        elif nb['age']>12*3600:
            nb['age_color']='#ddaa00'
        else:
            nb['age_color']='white'

        dayz = (b[2]-b[1]).days
        print('????????')
        print(b[1])
        print(b[2])
        nb['days']=str(dayz)+" "+russian_plurals('день', dayz)

        # MAX_AGE= 3600*24
        # age_prc = nb['age']/MAX_AGE
        # g=hex(int(255-120*age_prc))[2:]
        # r=hex(int(128*age_prc))[2:]
        # bc=hex(int(96*age_prc))[2:]
        # r = "0"+r if len(r)<2 else r
        # g = "0"+g if len(g)<2 else g
        # bc = "0"+bc if len(bc)<2 else bc
        # nb['age_color']="#"+r+g+bc

        tpurl="http://aviasales.ru/?marker=14721&origin_iata=MOW"
        nb['href']=tpurl+"&destination_iata=%s&depart_date=%s&return_date=%s" % (nb['destination'],dd_url, rd_url)
        #nb['special'] = True if nb['price']<10000 else False
        nb['special'] = True if nb['price']<0.66*b[8] else False
        res['bids'].append(nb)

    return json.dumps(res)


#@app.route('/pulse', methods = ['POST'])
#def pulse():
#    res={}
#    print ('ACCEPTED '+str(datetime.utcnow()))
#    if (datetime.utcnow()-DestinationStats.last_request_time()).seconds<7:
#        res['success']=False
#        print ("Too early for any request - skip")
#    else:
#        destinations = [p for p in db.engine.execute("""SELECT name, code, country, score FROM destination""")]
#        random_request(destinations)
#    return json.dumps({'success':True})


def check_subscriber(hsh):
    q = list(db.engine.execute("""SELECT id, email FROM subscribers WHERE hash="%s" """ % hsh ))
    res = {'exists': len(q) > 0}
    if res['exists']:
        res['email']=q[0][1]
    return res


@app.route('/save-email', methods=['POST'])
def save_email():

    success=False
    q = request.json

    if q['email']!='' and '@' in q['email'] and '.' in q['email']:
        hsh = get_hash(q['email'])
        if not check_subscriber(hsh)['exists']:
            db.engine.execute("""INSERT INTO subscribers (`email`, `marker`, `hash`) VALUES ("%s", "%s", "%s")""" % (q['email'], session['marker'], hsh) )
        success = True

    return json.dumps({"success": success})


@app.route('/unsubscribe', methods=['GET'])
def unsubscribe():

    success=False
    email=''
    hsh = request.args.get('ref')

    check_res = check_subscriber(hsh)
    if check_res['exists']:
        email = check_res['email']
        db.engine.execute(""" DELETE FROM subscribers WHERE hash="%s" """ % hsh)
        check_res = check_subscriber(hsh)
        if not check_res['exists']:
            success = True

    return render_template('unsubscribed.html', success=success, email = email)






@app.template_filter('nl2br')
def nl2br(value):
    text = ""
    if value:
        for line in value.split('\n'):
            text += Markup.escape(line) + Markup('<br />')
    return text

@app.errorhandler(404)
def page_not_found(e):
    Log.register(action='route:404', data=request.url)
    return render_template('404.html'), 404

@app.errorhandler(413)
def error413(e):
    return "Your error page for 413 status code", 413





