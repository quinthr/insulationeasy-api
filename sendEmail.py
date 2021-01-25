import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg['Subject'] = 'Check out Bronx as a puppy!'
msg['From'] = 'support@insulationeasy.com.au'
msg['To'] = 'quinth.anthony@gmail.com'

msg.set_content('This is a plain text email')

msg.add_alternative("""\
<!DOCTYPE html>
<html>
    <body>
        <h1 style="color:SlateGray;">This is an HTML Email!</h1>
    </body>
</html>
""", subtype='html')


with smtplib.SMTP_SSL('mail.insulationeasy.com.au', 465) as smtp:
    smtp.login('support@insulationeasy.com.au', '@#IEA12Xx')
    smtp.send_message(msg)