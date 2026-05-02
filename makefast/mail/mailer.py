import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

from .mailable import Mailable

class MailSender:
    def __init__(self, to_email: str):
        self.to_email = to_email

    def send(self, mailable: Mailable):
        # Configure the mailable
        mailable.build()

        if not mailable._view:
            raise ValueError("Mailable must have a view template defined.")

        # Read SMTP config from environment variables
        host = os.getenv("MAIL_HOST", "localhost")
        port = int(os.getenv("MAIL_PORT", 1025))
        username = os.getenv("MAIL_USERNAME")
        password = os.getenv("MAIL_PASSWORD")
        from_address = os.getenv("MAIL_FROM_ADDRESS", "hello@example.com")
        from_name = os.getenv("MAIL_FROM_NAME", "Makefast App")

        # Set up Jinja2 environment
        # Assuming templates are in 'resources/views'
        template_dir = os.path.join(os.getcwd(), "resources", "views")
        if not os.path.exists(template_dir):
            os.makedirs(template_dir, exist_ok=True)
            
        env = Environment(loader=FileSystemLoader(template_dir))
        
        # Convert dot notation to path (e.g. emails.welcome -> emails/welcome.html)
        template_file = mailable._view.replace(".", "/") + ".html"
        
        try:
            template = env.get_template(template_file)
            html_content = template.render(**mailable._data)
        except Exception as e:
            raise Exception(f"Failed to render email template '{template_file}': {e}")

        # Construct email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = mailable._subject or "No Subject"
        msg["From"] = f"{from_name} <{from_address}>"
        msg["To"] = self.to_email

        # Attach HTML content
        part = MIMEText(html_content, "html")
        msg.attach(part)

        # Send email
        try:
            with smtplib.SMTP(host, port) as server:
                if username and password:
                    server.login(username, password)
                server.send_message(msg)
        except Exception as e:
            raise Exception(f"Failed to send email: {e}")

class Mail:
    @classmethod
    def to(cls, email_address: str) -> MailSender:
        return MailSender(email_address)
