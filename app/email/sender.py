import resend
from app.config import get_settings
from app.models import DigestPost
from app.email.templates import generate_digest_html
from typing import List
from datetime import datetime

settings = get_settings()
resend.api_key = settings.resend_api_key


class EmailSender:
    """Handles email delivery via Resend."""

    def __init__(self):
        self.from_email = "digest@yourdomain.com"  # Update with your verified domain
        self.from_name = "Reddit Digest"

    def send_digest(self, recipient: str, posts: List[DigestPost], is_preview: bool = False) -> bool:
        """Send daily digest email."""
        try:
            # Generate email HTML
            html_content = generate_digest_html(posts, is_preview)

            # Prepare subject line
            date_str = datetime.now().strftime("%B %d, %Y")
            subject = f"Your Reddit Digest - {date_str}"
            if is_preview:
                subject = f"[PREVIEW] {subject}"

            # Send email
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [recipient],
                "subject": subject,
                "html": html_content
            }

            response = resend.Emails.send(params)
            print(f"Email sent successfully: {response}")
            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_test_email(self, recipient: str) -> bool:
        """Send a test email to verify configuration."""
        try:
            html = """
            <html>
                <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px;">
                    <h2>Test Email</h2>
                    <p>If you're reading this, your Reddit Summarizer email configuration is working correctly!</p>
                    <p>You're all set to receive your daily digests.</p>
                </body>
            </html>
            """

            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [recipient],
                "subject": "Reddit Summarizer - Test Email",
                "html": html
            }

            response = resend.Emails.send(params)
            print(f"Test email sent: {response}")
            return True

        except Exception as e:
            print(f"Error sending test email: {e}")
            return False
