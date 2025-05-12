# backend/app/resend_client.py

import os
import logging
import resend

# configure logging
logger = logging.getLogger("resend_client")
logger.setLevel(logging.DEBUG)  # adjust as needed

# Pull in your API key from env
resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(to, subject, html):
    """
    Sends an email via Resend.

    Args:
        to (str | list[str]): Recipient email or list of emails.
        subject (str): Email subject line.
        html (str): HTML body of the email.

    Returns:
        resend.Email: The Resend Email object on success.

    Raises:
        Exception: Propagates any errors from the Resend SDK.
    """
    # Normalize recipients to a list
    recipients = to if isinstance(to, (list, tuple)) else [to]

    params: resend.Emails.SendParams = {
        "from": os.getenv("EMAIL_FROM"),
        "to": recipients,
        "subject": subject,
        "html": html,
    }

    logger.debug(f"Resend parameters: {params!r}")

    try:
        email_obj = resend.Emails.send(params)
        logger.info(f"Email sent successfully: id={getattr(email_obj, 'id', None)}")
        return email_obj
    except Exception as e:
        logger.exception("Failed to send email via Resend")
        raise
