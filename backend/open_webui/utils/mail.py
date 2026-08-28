import logging
import smtplib
from email.message import EmailMessage

from fastapi.concurrency import run_in_threadpool
from open_webui.env import (
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_SSL,
    SMTP_USE_TLS,
    SMTP_USERNAME,
)

log = logging.getLogger(__name__)


def is_mail_configured() -> bool:
    return bool(SMTP_HOST and SMTP_FROM_EMAIL)


def _send_email_sync(to_email: str, subject: str, body: str) -> bool:
    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = SMTP_FROM_EMAIL
    message['To'] = to_email
    message.set_content(body)

    try:
        smtp_cls = smtplib.SMTP_SSL if SMTP_USE_SSL else smtplib.SMTP
        with smtp_cls(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            if SMTP_USE_TLS and not SMTP_USE_SSL:
                server.starttls()
            if SMTP_USERNAME and SMTP_PASSWORD:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
        return True
    except Exception as e:
        log.error(f'Failed to send email to {to_email}: {e}')
        return False


async def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send an email via SMTP. Returns False (without raising) on failure or missing config."""
    if not is_mail_configured():
        log.warning('Email not sent: SMTP is not configured (SMTP_HOST/SMTP_FROM_EMAIL missing)')
        return False
    if not to_email:
        return False

    return await run_in_threadpool(_send_email_sync, to_email, subject, body)
