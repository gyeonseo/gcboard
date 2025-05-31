from flask import current_app, render_template
from flask_mail import Message
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        app.extensions['mail'].send(msg)

def send_email(subject, recipients, text_body, html_body):
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    # 비동기로 이메일 발송
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def send_verification_email(user_email, token):
    """이메일 인증 메일 발송"""
    verification_url = current_app.config['EMAIL_VERIFICATION_URL'].format(token)
    
    # 템플릿 렌더링
    text_body = render_template('email/verify_email.txt',
                              verification_url=verification_url)
    html_body = render_template('email/verify_email.html',
                              verification_url=verification_url)
    
    # 이메일 발송
    send_email(
        subject='이메일 인증',
        recipients=[user_email],
        text_body=text_body,
        html_body=html_body
    ) 