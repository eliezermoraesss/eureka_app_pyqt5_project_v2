import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from app.config.email_config import read_email_params

logging.basicConfig(level=logging.DEBUG)


def send_email(subject, body, recipient):
    email_params = read_email_params()
    sender_email = email_params['sender_email']
    password = email_params['password']  # Use the app password generated for Gmail e-mail provider

    # Configure the email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    # Connect to the Gmail SMTP server and send the email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)

        server.sendmail(sender_email, recipient, msg.as_string())
        logging.info(f"Email sent successfully to {recipient}")

        server.quit()
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

