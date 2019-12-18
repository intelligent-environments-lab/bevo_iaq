import datetime
import smtplib, ssl

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "IEL.Beacon.Manager@gmail.com"  # Enter your address
receiver_email = "IEL.Beacon.Manager@gmail.com"  # Enter receiver address
password = "ZoltanIEL2019"
message = """\
Subject: SPS30 is down

SPS30 is down at {time}"""

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.format(time=str(datetime.datetime.now())))