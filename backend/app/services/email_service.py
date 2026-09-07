import html
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

from app.core.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_FROM_EMAIL,
    SMTP_FROM_NAME,
    SMTP_USE_TLS,
    SMTP_USE_SSL,
    SMTP_TIMEOUT_SECONDS,
    SMTP_DEBUG,
)


def is_smtp_configured() -> bool:
    """Return True when the minimum SMTP settings needed to send mail exist."""
    return bool(SMTP_HOST and SMTP_FROM_EMAIL)


def _sender() -> str:
    if SMTP_FROM_NAME:
        return formataddr((SMTP_FROM_NAME, SMTP_FROM_EMAIL))
    return SMTP_FROM_EMAIL


def send_email(recipient: str, subject: str, text_body: str, html_body: str | None = None) -> bool:
    """
    Send an email using SMTP settings from .env.

    The function returns False when SMTP is not configured. If SMTP is configured
    but the provider rejects the connection/login/message, the original exception
    is raised so the backend can log a clear error.
    """
    if not is_smtp_configured():
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = _sender()
    msg["To"] = recipient
    msg.set_content(text_body)
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()

    if SMTP_USE_SSL:
        smtp_client = smtplib.SMTP_SSL(
            SMTP_HOST,
            SMTP_PORT,
            timeout=SMTP_TIMEOUT_SECONDS,
            context=context,
        )
    else:
        smtp_client = smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
            timeout=SMTP_TIMEOUT_SECONDS,
        )

    with smtp_client as smtp:
        if SMTP_DEBUG:
            smtp.set_debuglevel(1)
        smtp.ehlo()
        if SMTP_USE_TLS and not SMTP_USE_SSL:
            smtp.starttls(context=context)
            smtp.ehlo()
        if SMTP_USERNAME:
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.send_message(msg)

    return True


def send_password_reset_email(recipient: str, reset_url: str) -> bool:
    """Send a BuildTrack password-reset email."""
    safe_url = html.escape(reset_url, quote=True)
    text_body = (
        "Hello,\n\n"
        "We received a request to reset your BuildTrack password.\n\n"
        f"Open this link to reset your password:\n{reset_url}\n\n"
        "This link expires soon. If you did not request this, you can ignore this email.\n\n"
        "- BuildTrack"
    )
    html_body = f"""
    <div style="font-family:Arial,sans-serif;line-height:1.6;color:#111827">
      <h2 style="color:#2563eb;margin-bottom:8px">BuildTrack Password Reset</h2>
      <p>We received a request to reset your BuildTrack password.</p>
      <p>
        <a href="{safe_url}" style="background:#2563eb;color:#ffffff;padding:12px 18px;border-radius:8px;text-decoration:none;display:inline-block">
          Reset Password
        </a>
      </p>
      <p style="font-size:13px;color:#64748b">If the button does not work, copy and paste this link into your browser:</p>
      <p style="word-break:break-all;font-size:13px;color:#334155">{safe_url}</p>
      <p style="font-size:13px;color:#64748b">If you did not request this, you can ignore this email.</p>
    </div>
    """
    return send_email(
        recipient=recipient,
        subject="BuildTrack Password Reset",
        text_body=text_body,
        html_body=html_body,
    )


def send_test_email(recipient: str) -> bool:
    """Send a simple SMTP test email."""
    return send_email(
        recipient=recipient,
        subject="BuildTrack SMTP Test",
        text_body="SMTP is configured correctly. BuildTrack can send emails now.",
        html_body="<p>SMTP is configured correctly. <strong>BuildTrack can send emails now.</strong></p>",
    )
