import asyncio

from sqlalchemy import text

from app.core.security import hash_password
from app.database.session import AsyncSessionLocal


USER_EMAIL = "admin@kwarihub.com"
ADMIN_PASSWORD = "Admin123@kwarihub"


async def main():

    async with AsyncSessionLocal() as db:

        try:
            # ====================================================
            # FIND USER
            # ====================================================

            result = await db.execute(
                text("""
                    SELECT id, email
                    FROM users
                    WHERE email = :email
                    LIMIT 1
                """),
                {
                    "email": USER_EMAIL
                },
            )

            user = result.first()

            if not user:
                print()
                print("========================================")
                print("USER NOT FOUND")
                print("========================================")
                print(f"Email: {USER_EMAIL}")
                print("========================================")
                return

            user_id = user.id

            print(f"Found user: {user.email}")
            print(f"User ID: {user_id}")

            # ====================================================
            # FIND ADMIN ROLE
            # ====================================================

            result = await db.execute(
                text("""
                    SELECT id, name, slug
                    FROM roles
                    WHERE slug = :slug
                    LIMIT 1
                """),
                {
                    "slug": "admin"
                },
            )

            admin_role = result.first()

            if not admin_role:
                print()
                print("========================================")
                print("ADMIN ROLE NOT FOUND")
                print("========================================")
                return

            admin_role_id = admin_role.id

            print(f"Admin role found: {admin_role.name}")
            print(f"Admin role ID: {admin_role_id}")

            # ====================================================
            # UPDATE PRIMARY ROLE
            # ====================================================

            await db.execute(
                text("""
                    UPDATE users
                    SET role_id = :role_id
                    WHERE id = :user_id
                """),
                {
                    "role_id": admin_role_id,
                    "user_id": user_id,
                },
            )

            print("Primary role updated.")

            # ====================================================
            # CHECK user_roles
            # ====================================================

            result = await db.execute(
                text("""
                    SELECT user_id
                    FROM user_roles
                    WHERE user_id = :user_id
                      AND role_id = :role_id
                    LIMIT 1
                """),
                {
                    "user_id": user_id,
                    "role_id": admin_role_id,
                },
            )

            existing_role = result.first()

            if not existing_role:

                await db.execute(
                    text("""
                        INSERT INTO user_roles (
                            user_id,
                            role_id
                        )
                        VALUES (
                            :user_id,
                            :role_id
                        )
                    """),
                    {
                        "user_id": user_id,
                        "role_id": admin_role_id,
                    },
                )

                print("Admin role added to user_roles.")

            else:

                print(
                    "Admin role already exists in user_roles."
                )

            # ====================================================
            # HASH PASSWORD
            # ====================================================

            password_hash = hash_password(
                ADMIN_PASSWORD
            )

            # ====================================================
            # UPDATE PASSWORD + ACCOUNT STATUS
            # ====================================================

            await db.execute(
                text("""
                    UPDATE users
                    SET
                        password_hash = :password_hash,
                        is_active = TRUE,
                        is_deleted = FALSE
                    WHERE id = :user_id
                """),
                {
                    "password_hash": password_hash,
                    "user_id": user_id,
                },
            )

            print("Password updated.")
            print("Account activated.")

            # ====================================================
            # COMMIT
            # ====================================================

            await db.commit()

            print()
            print("========================================")
            print("       ADMIN ACCOUNT UPDATED")
            print("========================================")
            print(f"User ID : {user_id}")
            print(f"Email   : {USER_EMAIL}")
            print(f"Role    : {admin_role.name}")
            print(f"Slug    : {admin_role.slug}")
            print(f"Role ID : {admin_role_id}")
            print(f"Password: {ADMIN_PASSWORD}")
            print("Status  : ACTIVE")
            print("========================================")

        except Exception:
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())                                                                                                                                                                                        