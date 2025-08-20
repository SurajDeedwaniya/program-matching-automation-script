# send_email.py
import os
import base64
import mimetypes
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

WORKDIR = os.environ.get("WORKDIR", os.getcwd())

# Gmail OAuth2 credentials (Info only)
CLIENT_ID = os.environ["EMAIL_API_CLIENT_ID"]
CLIENT_SECRET = os.environ["EMAIL_API_CLIENT_SECRET"]
REDIRECT_URI = os.environ["EMAIL_API_REQUEST_URI"]
ACCESS_TOKEN = os.environ["EMAIL_API_ACCESS_TOKEN"]
REFRESH_TOKEN = os.environ["EMAIL_API_REFRESH_TOKEN"]

def build_gmail_service():
    creds = Credentials(
        token=ACCESS_TOKEN,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
    )
    return build("gmail", "v1", credentials=creds)


# --- Create Email Message ---
def create_message(to, subject, body, attachments=None, cc=None, bcc=None, reply_to=None):
    msg = MIMEMultipart()
    msg["From"] = "info@accredian.com"
    msg["To"] = ", ".join(to if isinstance(to, list) else [to])
    msg["Subject"] = subject

    if cc:
        msg["Cc"] = ", ".join(cc if isinstance(cc, list) else [cc])
    if bcc:
        msg["Bcc"] = ", ".join(bcc if isinstance(bcc, list) else [bcc])
    if reply_to:
        msg["Reply-To"] = reply_to

    msg.attach(MIMEText(body, "html"))

    if attachments:
        for path in attachments:
            if os.path.exists(path):
                ctype, _ = mimetypes.guess_type(path)
                if ctype is None:
                    ctype = "application/octet-stream"
                maintype, subtype = ctype.split("/", 1)
                with open(path, "rb") as f:
                    part = MIMEBase(maintype, subtype)
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", "attachment", filename=os.path.basename(path))
                    msg.attach(part)

    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw_message}


# --- Send Email ---
def send_custom_email(to, subject, body, attachments=None, cc=None, bcc=None, reply_to=None):
    try:
        service = build_gmail_service()
        message = create_message(to, subject, body, attachments, cc, bcc, reply_to)
        sent = service.users().messages().send(userId="me", body=message).execute()
        print(f"✅ Email sent to {to}, ID: {sent['id']}")
    except Exception as e:
        print("❌ Failed to send email:", e)
        raise


# --- Daily Report Email ---
# --- Daily Report Email ---
def send_report_email():
    import os
    from datetime import datetime

    # ✅ Static recipients
    to = ["hemanka@accredian.com","surbhi.bhatia@accredian.com"]   # <-- change as needed
    cc = ["suraj.deedwaniya@accredian.com,vinayak@accredian.com"]
    bcc = []
    reply_to = ""

    # ✅ Dynamic subject with date
    today = datetime.now().strftime("%d %B %Y")
    subject = f"📊 Daily Program & Brochure Validation Report – {today}"

    # ✅ Properly formatted plain-text body with newlines
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p>Hello Team,</p>

        <p>
            Please find attached the latest validation reports for 
            <b>Programs &amp; Brochures</b> as of {today}.
        </p>

        <p><b>Reports Included:</b></p>
        <ul>
            <li>📑 Mismatch Report (program vs. sheet data)</li>
            <li>📑 Brochure Report (extracted vs. sheet data)</li>
        </ul>

        <p>
            This is an automated email. If you have any questions or notice discrepancies,<br>
            please reply to this thread.
        </p>

        <p>
            Best regards,<br>
            <b>Accredian Automated Validation Bot 🤖</b>
        </p>
    </body>
    </html>
    """


    # ✅ Attachments
    attachments = [
        os.path.join(WORKDIR, "mismatch_report.xlsx"),
        os.path.join(WORKDIR, "brochure_report.xlsx"),
    ]

    # ✅ Send email
    send_custom_email(
        to,
        subject,
        body,
        attachments,
        cc=cc,
        bcc=bcc,
        reply_to=reply_to
    )


if __name__ == "__main__":
    send_report_email()
