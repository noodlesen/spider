#import os
import smtplib
import json
from premailer import transform
from flask import render_template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import MANDRILL_USERNAME, MANDRILL_PASSWORD

def send_prices_email(prices):

    msg = MIMEMultipart('alternative')

    msg['Subject'] = "Fly From Moscow — ежедневный обзор лучших цен на авиабилеты"
    msg['From']    = "Fly From Moscow <price@flyfrom.moscow>" # Your from name and email address
    msg['To']      = "k.lapshov@gmail.com"

    text = "Mandrill speaks plaintext"
    part1 = MIMEText(text, 'plain')

    html = transform(render_template('letter.html', prices=json.loads(prices)['bids'])) # "<em>Mandrill speaks <strong>HTML</strong></em>"
    part2 = MIMEText(html, 'html')


    username = MANDRILL_USERNAME # os.environ['MANDRILL_USERNAME']
    password = MANDRILL_PASSWORD # os.environ['MANDRILL_PASSWORD']

    msg.attach(part1)
    msg.attach(part2)

    s = smtplib.SMTP('smtp.mandrillapp.com', 587)

    s.login(username, password)
    s.sendmail(msg['From'], msg['To'], msg.as_string())

    s.quit()