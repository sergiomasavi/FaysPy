from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail
import sys

def send_async_email(app, msg):
    try:
        with app.app_context():
            mail.send(msg)
    except Exception as e:
        print('Email de confirmación no enviado!\n',e,sep='', file=sys.stderr)
    else:
        print('Email de confirmación enviado correctamente!')

def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()

    msg = Message(app.config['OFFBRAND_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['OFFBRAND_MAIL_SENDER'], recipients=to)
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    thr = Thread(target=send_async_email, args=[app,msg])
    thr.start()
    return thr

