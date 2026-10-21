
from __future__ import annotations

import asyncio

from sqlalchemy import insert, select

from app.database.session import AsyncSessionLocal
from app.modules.roles.models import Role
from app.modules.roles.association import role_permissions
from app.modules.permissions.models import Permission
from scripts.seed_rbac import load_all_models


PERMISSION_NAME = "admin.promotions"
PERMISSION_DESCRIPTION = (
    "Create, manage, schedule, and report on marketplace promotions."
)


async def main() -> None:
    load_all_models()

    async with AsyncSessionLocal() as db:
        try:
            # Create the permission only if it does not exist.
            permission = await db.scalar(
                select(Permission).where(
                    Permission.name == PERMISSION_NAME
                )
            )

            if permission is None:
                permission = Permission(
                    name=PERMISSION_NAME,
                    description=PERMISSION_DESCRIPTION,
                )
                db.add(permission)
                await db.flush()
                print(f"Created permission: {PERMISSION_NAME}")
            else:
                print(f"Permission already exists: {PERMISSION_NAME}")

            # Assign the permission to the existing admin role.
            admin_role = await db.scalar(
                select(Role).where(Role.slug == "admin")
            )

            if admin_role is None:
                raise RuntimeError(
                    "The 'admin' role does not exist. "
                    "No changes will be committed."
                )

            assignment = await db.execute(
                select(role_permissions.c.role_id).where(
                    role_permissions.c.role_id == admin_role.id,
                    role_permissions.c.permission_id == permission.id,
                )
            )

            if assignment.first() is None:
                await db.execute(
                    insert(role_permissions).values(
                        role_id=admin_role.id,
                        permission_id=permission.id,
                    )
                )
                print("Assigned admin.promotions to the admin role.")
            else:
                print("The admin role already has this permission.")

            await db.commit()
            print("Promotions permission setup completed successfully.")

        except Exception:
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
