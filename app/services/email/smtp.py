from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings


async def send_email(
    email: str,
    subject: str,
    html: str,
):
    message = EmailMessage()

    message["From"] = (
        f"{settings.MAIL_FROM_NAME} "
        f"<{settings.MAIL_FROM}>"
    )

    message["To"] = email
    message["Subject"] = subject

    message.set_content(
        "This email requires an HTML-compatible email client."
    )

    message.add_alternative(
        html,
        subtype="html",
    )

    await aiosmtplib.send(
        message,
        hostname=settings.MAIL_HOST,
        port=settings.MAIL_PORT,
        username=settings.MAIL_USERNAME,
        password=settings.MAIL_PASSWORD,
        use_tls=settings.MAIL_SSL,
        start_tls=settings.MAIL_TLS,
        timeout=30,
    )