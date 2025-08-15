# utils/emailer.py

from dotenv import load_dotenv
import os
import smtplib
from email.message import EmailMessage

load_dotenv()  # Load from .env file

# ---- Email Configuration ----
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_report_email(to_email, pdf_path, subject="Your NBA Brand Visibility Report"):
    """
    Send the final report PDF to the user's email.
    """
    if not os.path.isfile(pdf_path):
        print(f"❌ Report file not found: {pdf_path}")
        return

    msg = EmailMessage()
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content("Attached is your automatically generated NBA brand visibility report.")

    with open(pdf_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(pdf_path)
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Report sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
