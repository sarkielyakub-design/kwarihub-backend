from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal
from app.modules.roles.models import Role


async def seed_roles():
    async with AsyncSessionLocal() as db:
        roles = [
            {
                "name": "Super Admin",
                "slug": "super-admin",
                "description": "System Super Administrator",
            },
            {
                "name": "Admin",
                "slug": "admin",
                "description": "Platform Administrator",
            },
            {
                "name": "Buyer",
                "slug": "buyer",
                "description": "Marketplace Buyer",
            },
            {
                "name": "Vendor",
                "slug": "vendor",
                "description": "Marketplace Vendor",
            },
        ]

        for item in roles:
            existing = await db.scalar(
                select(Role).where(Role.slug == item["slug"])
            )

            if not existing:
                db.add(Role(**item, is_system=True))

        await db.commit()
        print("✅ Default roles seeded successfully.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(seed_roles())