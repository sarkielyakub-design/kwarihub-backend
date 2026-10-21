
import asyncio

from sqlalchemy import inspect
from app.database.session import engine


async def main():
    async with engine.connect() as connection:
        def inspect_schema(sync_connection):
            inspector = inspect(sync_connection)

            order_columns = {
                column["name"]
                for column in inspector.get_columns("orders")
            }

            redemption_exists = inspector.has_table(
                "promotion_redemptions"
            )

            print("Order discount columns:")
            for column in (
                "discount_amount",
                "coupon_code",
                "promotion_id",
            ):
                print(f"  {column}: {column in order_columns}")

            print(
                "Promotion redemption table:",
                redemption_exists,
            )

            if redemption_exists:
                print(
                    "Redemption columns:",
                    [
                        column["name"]
                        for column in inspector.get_columns(
                            "promotion_redemptions"
                        )
                    ],
                )

        await connection.run_sync(inspect_schema)


if __name__ == "__main__":
    asyncio.run(main())
