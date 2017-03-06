#import os
import smtplib
import json
from premailer import transform
from flask import render_template
from datetime import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import MANDRILL_USERNAME, MANDRILL_PASSWORD

from .db import db


def send_prices_email(email, prices):

    qhsh = list(db.engine.execute("""SELECT hash, last_mail_sent_at FROM subscribers WHERE email="%s" """ % email))

    if len(qhsh)>0 and qhsh[0][1] and (datetime.now().replace(microsecond=0) - qhsh[0][1]).seconds>7200:

        print ("SECONDS: ", (datetime.now().replace(microsecond=0) - qhsh[0][1]).seconds)

        hsh=qhsh[0][0]

        msg = MIMEMultipart('alternative')

        msg['Subject'] = "Fly From Moscow — ежедневный обзор лучших цен на авиабилеты"
        msg['From']    = "Fly From Moscow <price@flyfrom.moscow>" # Your from name and email address
        msg['To']      = email

        text = "К сожалению, рассылка лучших цен на авиабилеты FLYFROM.MOSCOW поддерживает только HTML формат письма"
        part1 = MIMEText(text, 'plain')

        html = transform(render_template('letter.html', prices=json.loads(prices)['bids'], hsh=hsh)) # "<em>Mandrill speaks <strong>HTML</strong></em>"
        part2 = MIMEText(html, 'html')


        username = MANDRILL_USERNAME # os.environ['MANDRILL_USERNAME']
        password = MANDRILL_PASSWORD # os.environ['MANDRILL_PASSWORD']

        msg.attach(part1)
        msg.attach(part2)

        s = smtplib.SMTP('smtp.mandrillapp.com', 587)

        s.login(username, password)
        s.sendmail(msg['From'], msg['To'], msg.as_string())

        s.quit()

        db.engine.execute("""UPDATE subscribers SET last_mail_sent_at="%s" WHERE hash="%s" """ 
                          % (datetime.now().strftime('%Y-%m-%d %H:%M:%S%z'), hsh)
        )




def send_confirmation_email(email, prices):

    qhsh = list(db.engine.execute("""SELECT hash FROM subscribers WHERE email="%s" """ % email))

    if len(qhsh)>0:

        hsh=qhsh[0][0]

        msg = MIMEMultipart('alternative')

        msg['Subject'] = "Подтверждение адреса — рассылка лучших цен на авиабилеты Fly From Moscow"
        msg['From']    = "Fly From Moscow <price@flyfrom.moscow>" # Your from name and email address
        msg['To']      = email

        text = "К сожалению, рассылка лучших цен на авиабилеты FLYFROM.MOSCOW поддерживает только HTML формат письма"
        part1 = MIMEText(text, 'plain')

        html = transform(render_template('confirmation_letter.html', prices=json.loads(prices)['bids'], hsh=hsh)) # "<em>Mandrill speaks <strong>HTML</strong></em>"
        part2 = MIMEText(html, 'html')


        username = MANDRILL_USERNAME # os.environ['MANDRILL_USERNAME']
        password = MANDRILL_PASSWORD # os.environ['MANDRILL_PASSWORD']

        msg.attach(part1)
        msg.attach(part2)

        s = smtplib.SMTP('smtp.mandrillapp.com', 587)

        s.login(username, password)
        s.sendmail(msg['From'], msg['To'], msg.as_string())

        s.quit()

        db.engine.execute("""UPDATE subscribers SET confirm_requested = 1 WHERE email = "%s" """ % email)

