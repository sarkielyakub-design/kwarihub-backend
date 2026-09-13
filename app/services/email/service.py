from datetime import datetime

from app.services.email.smtp import send_email
from app.services.email.utils import render


class EmailService:

    async def welcome(
        self,
        email: str,
        name: str,
    ):
        html = render(
            "welcome.html",
            title="Welcome to KWARIHUB",
            year=datetime.now().year,
            name=name,
        )

        await send_email(
            email=email,
            subject="Welcome to KWARIHUB",
            html=html,
        )

    async def verify_email(
        self,
        email: str,
        name: str,
        otp: str,
    ):
        html = render(
            "verify_email.html",
            title="Verify Your Email",
            year=datetime.now().year,
            name=name,
            otp=otp,
        )

        await send_email(
            email=email,
            subject="Verify Your Email",
            html=html,
        )

    async def reset_password(
        self,
        email: str,
        name: str,
        url: str,
    ):
        html = render(
            "reset_password.html",
            title="Reset Password",
            year=datetime.now().year,
            name=name,
            url=url,
        )

        await send_email(
            email=email,
            subject="Reset Your Password",
            html=html,
        )

    async def order_confirmation(
        self,
        email: str,
        name: str,
        order_no: str,
        amount,
    ):
        html = render(
            "order_confirmation.html",
            title="Order Confirmation",
            year=datetime.now().year,
            name=name,
            order_no=order_no,
            amount=amount,
        )

        await send_email(
            email=email,
            subject="Order Confirmation",
            html=html,
        )

    async def withdrawal(
        self,
        email: str,
        name: str,
        status: str,
        amount,
        message: str,
    ):
        html = render(
            "withdrawal.html",
            title="Withdrawal Update",
            year=datetime.now().year,
            name=name,
            status=status,
            amount=amount,
            message=message,
        )

        await send_email(
            email=email,
            subject="Withdrawal Update",
            html=html,
        )

    async def product_approved(
        self,
        email: str,
        seller: str,
        product: str,
    ):
        html = render(
            "product_approved.html",
            title="Product Approved",
            year=datetime.now().year,
            seller=seller,
            product=product,
        )

        await send_email(
            email=email,
            subject="Your Product Has Been Approved",
            html=html,
        )
    async def reset_password_otp(
    self,
    email: str,
    name: str,
    otp: str,
):
     html = render(
        "reset_password_otp.html",
        title="Reset Password",
        year=datetime.now().year,
        name=name,
        otp=otp,
    )

     await send_email(
        email=email,
        subject="Reset Your Password",
        html=html,
    )

email_service = EmailService()