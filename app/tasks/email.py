import asyncio

from app.services.email.service import email_service
from app.tasks.celery_app import celery


@celery.task(name="send_welcome_email")
def send_welcome_email(
    email: str,
    name: str,
):
    asyncio.run(
        email_service.welcome(
            email,
            name,
        )
    )
@celery.task(name="send_verify_email")
def send_verify_email(
    email: str,
    name: str,
    otp: str,
):
    asyncio.run(
        email_service.verify_email(
            email,
            name,
            otp,
        )
    )  
@celery.task(name="send_reset_password_email")
def send_reset_password_email(
    email: str,
    name: str,
    otp: str,
):
    asyncio.run(
        email_service.reset_password_otp(
            email,
            name,
            otp,
        )
    )      