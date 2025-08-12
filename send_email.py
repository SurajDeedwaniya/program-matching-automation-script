# send_email.py
import os, mimetypes, smtplib
from email.message import EmailMessage

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ["SMTP_USERNAME"]
SMTP_PASS = os.environ["SMTP_PASSWORD"]
EMAIL_FROM = os.environ.get("EMAIL_FROM", SMTP_USER)
EMAIL_TO = os.environ["EMAIL_TO"].split(",")  # comma-separated recipients

msg = EmailMessage()
msg["Subject"] = os.environ.get("EMAIL_SUBJECT", "Daily Program & Brochure Reports")
msg["From"] = EMAIL_FROM
msg["To"] = ", ".join(EMAIL_TO)
msg.set_content(os.environ.get("EMAIL_BODY", "Attached: daily mismatch reports (if any)."))

# attachments we expect (the script writes to /content/)
candidate_paths = [
    "/content/mismatch_report.xlsx",
    "/content/brochure_report.xlsx",
]

attached = 0
for path in candidate_paths:
    if os.path.exists(path):
        ctype, _ = mimetypes.guess_type(path)
        if ctype is None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(path, "rb") as f:
            data = f.read()
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=os.path.basename(path))
            attached += 1

if attached == 0:
    print("No files found to attach. Still sending email with plain text.")
try:
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)
    print("✅ Email sent to:", EMAIL_TO)
except Exception as e:
    print("❌ Failed to send email:", e)
    raise
