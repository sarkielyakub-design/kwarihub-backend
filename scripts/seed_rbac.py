from __future__ import annotations

import asyncio
import importlib
import pkgutil

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal

from app.modules.roles.association import (
    role_permissions,
    user_roles,
)

from app.modules.roles.models import Role
from app.modules.permissions.models import Permission
from app.modules.users.models import User


# ============================================================
# LOAD ALL APPLICATION ORM MODELS
# ============================================================

def load_all_models() -> None:
    """
    Import every models.py module under app.modules.

    This is important because SQLAlchemy relationships use
    string class names such as:

        "Product"
        "Order"
        "RefreshToken"
        "Wallet"
        "Payment"

    Those classes must be registered before SQLAlchemy
    configures its mappers.
    """

    import app.modules

    print("Loading application ORM models...")

    loaded = 0

    for module_info in pkgutil.iter_modules(app.modules.__path__):

        module_name = f"app.modules.{module_info.name}.models"

        try:
            importlib.import_module(module_name)

            print(
                f"  Loaded: {module_name}"
            )

            loaded += 1

        except ModuleNotFoundError as exc:

            # Some module folders may not contain models.py.
            # Ignore only the case where that models.py itself
            # does not exist.
            if exc.name == module_name:
                continue

            raise

    print(
        f"Loaded {loaded} ORM model modules."
    )
    print()


# ============================================================
# SYSTEM ROLES
# ============================================================

ROLES = [
    {
        "name": "Buyer",
        "slug": "buyer",
        "description": "Customer who purchases products on KwariHub.",
        "is_system": True,
    },
    {
        "name": "Vendor",
        "slug": "vendor",
        "description": "Approved seller who manages products and marketplace orders.",
        "is_system": True,
    },
    {
        "name": "Admin",
        "slug": "admin",
        "description": "KwariHub administrator who manages marketplace operations.",
        "is_system": True,
    },
    {
        "name": "Super Admin",
        "slug": "super-admin",
        "description": "Full system administrator with unrestricted access.",
        "is_system": True,
    },
]


# ============================================================
# PERMISSIONS
# ============================================================

PERMISSIONS = [
    # Products
    (
        "products.view",
        "View marketplace products.",
    ),
    (
        "products.create",
        "Create products.",
    ),
    (
        "products.update",
        "Update owned products.",
    ),
    (
        "products.delete",
        "Delete owned products.",
    ),

    # Orders
    (
        "orders.view",
        "View orders.",
    ),
    (
        "orders.manage",
        "Manage order fulfillment.",
    ),

    # Inventory
    (
        "inventory.view",
        "View inventory.",
    ),
    (
        "inventory.manage",
        "Manage product inventory.",
    ),

    # Wallet
    (
        "wallet.view",
        "View wallet balance and transactions.",
    ),

    # Withdrawals
    (
        "withdrawals.view",
        "View withdrawal requests.",
    ),
    (
        "withdrawals.create",
        "Create withdrawal requests.",
    ),

    # Vendor
    (
        "vendor.view",
        "View vendor profile.",
    ),
    (
        "vendor.apply",
        "Submit a vendor application.",
    ),
    (
        "vendor.update",
        "Update vendor profile.",
    ),

    # Administration
    (
        "admin.users",
        "Manage marketplace users.",
    ),
    (
        "admin.vendors",
        "Manage vendor applications.",
    ),
    (
        "admin.products",
        "Manage marketplace products.",
    ),
    (
        "admin.orders",
        "Manage marketplace orders.",
    ),
    (
        "admin.settings",
        "Manage marketplace settings.",
    ),
]


# ============================================================
# ROLE -> PERMISSIONS
# ============================================================

ROLE_PERMISSIONS = {
    "buyer": [
        "products.view",
        "orders.view",
        "wallet.view",
    ],

    "vendor": [
        # Products
        "products.view",
        "products.create",
        "products.update",
        "products.delete",

        # Orders
        "orders.view",
        "orders.manage",

        # Inventory
        "inventory.view",
        "inventory.manage",

        # Wallet
        "wallet.view",

        # Withdrawals
        "withdrawals.view",
        "withdrawals.create",

        # Vendor
        "vendor.view",
        "vendor.apply",
        "vendor.update",
    ],

    "admin": [
        # Products
        "products.view",
        "products.create",
        "products.update",
        "products.delete",

        # Orders
        "orders.view",
        "orders.manage",

        # Inventory
        "inventory.view",
        "inventory.manage",

        # Wallet
        "wallet.view",

        # Withdrawals
        "withdrawals.view",
        "withdrawals.create",

        # Vendor
        "vendor.view",

        # Administration
        "admin.users",
        "admin.vendors",
        "admin.products",
        "admin.orders",
        "admin.settings",
    ],

    "super-admin": [
        permission_name
        for permission_name, _ in PERMISSIONS
    ],
}


# ============================================================
# SEED ROLES
# ============================================================

async def seed_roles(
    db: AsyncSession,
) -> dict[str, Role]:

    roles: dict[str, Role] = {}

    for data in ROLES:

        result = await db.execute(
            select(Role).where(
                Role.slug == data["slug"]
            )
        )

        role = result.scalar_one_or_none()

        if role is None:

            role = Role(**data)

            db.add(role)

            await db.flush()

            print(
                f"Created role: {role.name}"
            )

        else:

            role.name = data["name"]
            role.description = data["description"]
            role.is_system = data["is_system"]

            print(
                f"Role already exists: {role.name}"
            )

        roles[role.slug] = role

    return roles


# ============================================================
# SEED PERMISSIONS
# ============================================================

async def seed_permissions(
    db: AsyncSession,
) -> dict[str, Permission]:

    permissions: dict[str, Permission] = {}

    for name, description in PERMISSIONS:

        result = await db.execute(
            select(Permission).where(
                Permission.name == name
            )
        )

        permission = result.scalar_one_or_none()

        if permission is None:

            permission = Permission(
                name=name,
                description=description,
            )

            db.add(permission)

            await db.flush()

            print(
                f"Created permission: {name}"
            )

        else:

            permission.description = description

            print(
                f"Permission already exists: {name}"
            )

        permissions[name] = permission

    return permissions


# ============================================================
# ASSIGN ROLE PERMISSIONS
# ============================================================

async def assign_permissions(
    db: AsyncSession,
    roles: dict[str, Role],
    permissions: dict[str, Permission],
) -> None:

    for role_slug, permission_names in ROLE_PERMISSIONS.items():

        role = roles[role_slug]

        # Remove existing assignments.
        await db.execute(
            delete(role_permissions).where(
                role_permissions.c.role_id == role.id
            )
        )

        # Insert the correct assignments.
        for permission_name in permission_names:

            permission = permissions[permission_name]

            await db.execute(
                insert(role_permissions).values(
                    role_id=role.id,
                    permission_id=permission.id,
                )
            )

        print(
            f"Assigned {len(permission_names)} permissions "
            f"to {role.name}"
        )


# ============================================================
# BACKFILL EXISTING USERS
# ============================================================

async def backfill_user_roles(
    db: AsyncSession,
) -> None:

    """
    Existing users already have the legacy users.role_id.

    Copy their primary role into user_roles so the new RBAC
    authorization system continues to recognize them.
    """

    result = await db.execute(
        select(
            User.id,
            User.role_id,
        ).where(
            User.role_id.is_not(None)
        )
    )

    users = result.all()

    if not users:

        print(
            "No existing users require role backfill."
        )

        return

    inserted = 0
    skipped = 0

    for user_id, role_id in users:

        existing = await db.execute(
            select(user_roles.c.user_id).where(
                user_roles.c.user_id == user_id,
                user_roles.c.role_id == role_id,
            )
        )

        if existing.first() is not None:

            skipped += 1

            continue

        await db.execute(
            insert(user_roles).values(
                user_id=user_id,
                role_id=role_id,
            )
        )

        inserted += 1

    print(
        f"User role backfill completed: "
        f"{inserted} inserted, "
        f"{skipped} already existed."
    )


# ============================================================
# MAIN
# ============================================================

async def main() -> None:

    print()
    print("========================================")
    print("KwariHub RBAC Seed")
    print("========================================")
    print()

    # --------------------------------------------------------
    # IMPORTANT:
    # Load ALL model modules before touching any ORM query.
    # --------------------------------------------------------

    load_all_models()

    async with AsyncSessionLocal() as db:

        try:

            # ------------------------------------------------
            # 1. Roles
            # ------------------------------------------------

            print("Seeding roles...")

            roles = await seed_roles(db)

            print()

            # ------------------------------------------------
            # 2. Permissions
            # ------------------------------------------------

            print("Seeding permissions...")

            permissions = await seed_permissions(db)

            print()

            # ------------------------------------------------
            # 3. Role permissions
            # ------------------------------------------------

            print("Assigning role permissions...")

            await assign_permissions(
                db,
                roles,
                permissions,
            )

            print()

            # ------------------------------------------------
            # 4. Existing user roles
            # ------------------------------------------------

            print("Backfilling existing user roles...")

            await backfill_user_roles(db)

            print()

            # ------------------------------------------------
            # 5. Commit
            # ------------------------------------------------

            await db.commit()

            print("========================================")
            print("RBAC seed completed successfully.")
            print("========================================")
            print()

        except Exception:

            await db.rollback()

            print()
            print("========================================")
            print("RBAC seed FAILED.")
            print("All changes have been rolled back.")
            print("========================================")
            print()

            raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())