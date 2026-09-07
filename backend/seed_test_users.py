"""Create/update predictable development accounts for BuildTrack testing.

Run from backend/ with:
    python seed_test_users.py

These accounts are for local development/demo use only.
"""
from app.database.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

ACCOUNTS = [
    ("BuildTrack Admin", "admin@buildtrack.com", "Admin@123", "ADMIN"),
    ("Project Manager", "manager@buildtrack.com", "Manager@123", "PROJECT_MANAGER"),
    ("Site Engineer", "engineer@buildtrack.com", "Engineer@123", "SITE_ENGINEER"),
    ("Contractor", "contractor@buildtrack.com", "Contractor@123", "CONTRACTOR"),
    ("Worker", "worker@buildtrack.com", "Worker@123", "WORKER"),
    ("Client", "client@buildtrack.com", "Client@123", "CLIENT"),
]


def main():
    db = SessionLocal()
    try:
        for name, email, password, role in ACCOUNTS:
            user = db.query(User).filter(User.email == email).first()
            if user is None:
                user = User(
                    name=name,
                    email=email,
                    password=hash_password(password),
                    phone="0000000000",
                    role=role,
                    is_active=True,
                )
                db.add(user)
                action = "created"
            else:
                user.name = name
                user.password = hash_password(password)
                user.role = role
                user.is_active = True
                if not user.phone:
                    user.phone = "0000000000"
                action = "updated"
            print(f"{action:7} {email:30} role={role}")
        db.commit()
        print("\nDevelopment login accounts are ready.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
